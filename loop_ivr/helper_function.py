# -*- coding: utf-8 -*-
__author__ = 'Vikas Saini'

import requests
import time
import itertools
import MySQLdb
from datetime import datetime, timedelta
import xml.etree.ElementTree as xml_parse

from django.db.models import get_model

from dg.settings import EXOTEL_ID, EXOTEL_TOKEN, DATABASES, EXOTEL_HELPLINE_NUMBER

from loop.models import Crop, Mandi, CropLanguage
from loop.utils.ivr_helpline.helpline_data import SMS_REQUEST_URL, CALL_REQUEST_URL, APP_REQUEST_URL, \
    APP_URL
from loop.helpline_view import write_log

from loop_ivr.utils.marketinfo import raw_sql
from loop_ivr.utils.config import LOG_FILE, AGGREGATOR_SMS_NO, mandi_hi, indian_rupee, \
    agg_sms_initial_line, agg_sms_no_price_for_combination, agg_sms_no_price_available, \
    agg_sms_crop_line, helpline_hi, MARKET_INFO_CALL_RESPONSE_URL, MARKET_INFO_APP, MONTH_NAMES, \
    agg_sms_no_price_all_mandi, agg_sms_no_price_crop_mandi, crop_and_code
from loop_ivr.models import PriceInfoLog, PriceInfoIncoming


def make_market_info_call(caller_number, dg_number, incoming_time, incoming_call_id):
    app_request_url = APP_REQUEST_URL%(EXOTEL_ID,EXOTEL_TOKEN,EXOTEL_ID)
    app_id = MARKET_INFO_APP
    app_url = APP_URL%(app_id,)
    #call_response_url = MARKET_INFO_CALL_RESPONSE_URL
    #parameters = {'From':caller_number,'CallerId':dg_number,'CallType':'trans','Url':app_url,'StatusCallback':call_response_url}
    parameters = {'From':caller_number,'CallerId':dg_number,'CallType':'trans','Url':app_url}
    response = requests.post(app_request_url,data=parameters)
    module = 'make_market_info_call'
    if response.status_code == 200:
        response_tree = xml_parse.fromstring((response.text).encode('utf-8'))
        call_detail = response_tree.findall('Call')[0]
        outgoing_call_id = str(call_detail.find('Sid').text)
        outgoing_call_time = str(call_detail.find('StartTime').text)
        price_info_incoming_obj = PriceInfoIncoming(call_id=outgoing_call_id, from_number=caller_number,
                                        to_number=dg_number, incoming_time=outgoing_call_time)
    else:
        # Enter in Log
        price_info_incoming_obj = PriceInfoIncoming(call_id=incoming_call_id, from_number=caller_number,
                                        to_number=dg_number, incoming_time=incoming_time, info_status=5)
        log = 'Status Code: %s (Parameters: %s)'%(str(response.status_code),parameters)
        write_log(LOG_FILE,module,log)
    try:
        price_info_incoming_obj.save()    
    except Exception as e:
        # Save Errors in Logs
        write_log(LOG_FILE,module,str(e))

def send_sms(from_number,to_number,sms_body):
    sms_request_url = SMS_REQUEST_URL%(EXOTEL_ID,EXOTEL_TOKEN,EXOTEL_ID)
    parameters = {'From':from_number,'To':to_number,'Body':sms_body,'Priority':'high'}
    response = requests.post(sms_request_url,data=parameters)
    if response.status_code == 200:
        pass
    else:
        module = 'send_sms'
        log = "Status Code: %s (Parameters: %s)"%(str(response.status_code),parameters)
        write_log(LOG_FILE,module,log)

def get_valid_list(app_name, model_name, requested_item, farmer_number):
    model = get_model(app_name, model_name)
    if model_name == 'mandi':
        # If call from Bangladesh then return Mandi of Bangladesh
        if farmer_number.startswith('01'):
            id_list = set(model.objects.filter(district__state__country_id=2).values_list('id', flat=True))
        else:
            id_list = set(model.objects.filter(district__state__country_id=1).values_list('id', flat=True))
    else:
        id_list = set(model.objects.values_list('id', flat=True))
    requested_list = set(int(item) for item in requested_item.split('*') if item)
    if (0 in requested_list) or (len(requested_list)==0 and model_name == 'mandi'):
        return tuple(map(int,id_list)),1
    return tuple(map(int,requested_list.intersection(id_list))),0

def run_query(query):
    mysql_cn = MySQLdb.connect(host=DATABASES['default']['HOST'], port=DATABASES['default']['PORT'], 
        user=DATABASES['default']['USER'] ,
        passwd=DATABASES['default']['PASSWORD'],
        db=DATABASES['default']['NAME'],
        charset = 'utf8',
        use_unicode = True)
    cursor = mysql_cn.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def send_info(to_number, content):
    index = 0
    from_number = AGGREGATOR_SMS_NO
    while index < len(content):
        send_sms(from_number, to_number, content[index:index+1998])
        index += 1998
        time.sleep(1)

def get_price_info(from_number, crop_list, mandi_list, price_info_incoming_obj, all_crop_flag, all_mandi_flag):
    price_info_list = []
    price_info_log_list = []
    crop_mandi_comb = []
    crop_map = dict()
    mandi_map = dict()
    crop_in_hindi_map = dict()
    all_crop = Crop.objects.filter(id__in=crop_list).values('id', 'crop_name')
    all_mandi = Mandi.objects.filter(id__in=mandi_list).values('id', 'mandi_name')
    crop_in_hindi = CropLanguage.objects.filter(language_id=1, crop_id__in=crop_list).values('crop_id', 'crop_name')
    for crop in all_crop:
       crop_map[crop['id']] = crop['crop_name']
    for mandi in all_mandi:
       mandi_map[mandi['id']] = mandi['mandi_name']
    for crop in crop_in_hindi:
        crop_in_hindi_map[crop['crop_id']] = crop['crop_name']
    # Fetching price from DB
    price_info_list.append(agg_sms_initial_line)
    today_date = datetime.now()
    raw_query = raw_sql.last_three_trans.format('(%s)'%(crop_list[0],) if len(crop_list) == 1 else crop_list, '(%s)'%(mandi_list[0],) if len(mandi_list) == 1 else mandi_list, tuple((today_date-timedelta(days=day)).strftime('%Y-%m-%d') for day in range(0,3)))
    query_result = run_query(raw_query)
    if not query_result:
        if not all_crop_flag and not all_mandi_flag:
            crop_name_list = ','.join(map(lambda crop_id: crop_in_hindi_map.get(crop_id).encode("utf-8") if crop_in_hindi_map.get(crop_id) else crop_map[crop_id].encode("utf-8"), crop_list))
            mandi_name_list = ','.join(map(lambda mandi_id: mandi_map[mandi_id].encode("utf-8").rstrip(mandi_hi).rstrip(), mandi_list))
            no_price_message = (agg_sms_no_price_crop_mandi)%(crop_name_list, mandi_name_list)
        # If query for all Mandi
        elif all_mandi_flag:
            crop_name_list = ','.join(map(lambda crop_id: crop_in_hindi_map.get(crop_id).encode("utf-8") if crop_in_hindi_map.get(crop_id) else crop_map[crop_id].encode("utf-8"), crop_list))
            no_price_message = (agg_sms_no_price_all_mandi)%(crop_name_list,)
        # If query for all crops
        else:
            no_price_message = agg_sms_no_price_available
        price_info_list.append(no_price_message)
        price_info_list.append(('\n\n%s')%(crop_and_code,))
    else:
        prev_crop, prev_mandi, crop_name, mandi_name = -1, -1, '', ''
        for row in query_result:
            crop, mandi, date, min_price, max_price, mean = row['crop'], row['mandi'], row['date'], int(row['minp']), int(row['maxp']), int(row['mean'])
            if crop != prev_crop or mandi != prev_mandi:
                if not all_crop_flag and not all_mandi_flag:
                    crop_mandi_comb.append((crop,mandi))
                price_info_log_obj = PriceInfoLog(price_info_incoming=price_info_incoming_obj,
                                    crop_id=crop, mandi_id=mandi)
                price_info_log_list.append(price_info_log_obj)
                crop_name = crop_in_hindi_map.get(crop).encode("utf-8") if crop_in_hindi_map.get(crop) else crop_map[crop].encode("utf-8")
                mandi_name = mandi_map[mandi].encode("utf-8")
                if crop != prev_crop:
                    temp_str = ('\n%s: %s\n%s %s\n')%(agg_sms_crop_line,crop_name,mandi_name.rstrip(mandi_hi).rstrip(),mandi_hi)
                else:
                    temp_str = ('\n%s %s\n')%(mandi_name.rstrip(mandi_hi).rstrip(),mandi_hi)
                price_info_list.append(temp_str)
                prev_crop, prev_mandi = crop, mandi
            if max_price-min_price >= 2:
                min_price = mean-1
                max_price = mean+1
            if min_price != max_price:
                temp_str = ('%s %s: %s %s-%s\n')%(date.strftime('%d'),MONTH_NAMES[int(date.strftime('%m'))],indian_rupee,str(min_price),str(max_price))
            else:
                temp_str = ('%s %s: %s %s\n')%(date.strftime('%d'),MONTH_NAMES[int(date.strftime('%m'))],indian_rupee,str(max_price))
            price_info_list.append(temp_str)
    # Save combination of crop and mandi for which data is not present in query on if query not for all mandi and crops.
    if not all_crop_flag and not all_mandi_flag:
        prev_crop, prev_mandi, crop_name, mandi_name = -1, -1, '', ''
        for crop, mandi in itertools.product(crop_list, mandi_list):
            if (crop,mandi) not in crop_mandi_comb:
                price_info_log_obj = PriceInfoLog(price_info_incoming=price_info_incoming_obj,
                            crop_id=crop, mandi_id=mandi)
                price_info_log_list.append(price_info_log_obj)
                if query_result:
                    crop_name = crop_in_hindi_map.get(crop).encode("utf-8") if crop_in_hindi_map.get(crop) else crop_map[crop].encode("utf-8")
                    mandi_name = mandi_map[mandi].encode("utf-8")
                    if crop != prev_crop:
                        prev_crop = crop
                        temp_str = ('\n%s: %s\n%s %s\n')%(agg_sms_crop_line,crop_name,mandi_name.rstrip(mandi_hi).rstrip(),mandi_hi)
                    else:
                        prev_mandi = mandi
                        temp_str = ('\n%s %s\n')%(mandi_name.rstrip(mandi_hi).rstrip(),mandi_hi)
                    price_info_list.append(temp_str)
                    price_info_list.append(agg_sms_no_price_for_combination)
    price_info_list.append(('\n%s: %s')%(helpline_hi, EXOTEL_HELPLINE_NUMBER))
    final_result = ''.join(price_info_list)
    price_info_incoming_obj.price_result = final_result
    if len(final_result) >= 2000:
        price_info_incoming_obj.return_result_to_app = 0
        price_info_incoming_obj.info_status = 1
        price_info_incoming_obj.save()
        send_info(from_number, final_result)
    else:
        price_info_incoming_obj.save()
    PriceInfoLog.objects.bulk_create(price_info_log_list)
