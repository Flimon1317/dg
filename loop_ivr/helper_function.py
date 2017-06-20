# -*- coding: utf-8 -*-
__author__ = 'Vikas Saini'

import requests
import time

from django.db import connection
from django.db.models import get_model

from dg.settings import EXOTEL_ID, EXOTEL_TOKEN

from loop.models import Crop, Mandi
from loop.utils.ivr_helpline.helpline_data import HELPLINE_LOG_FILE, SMS_REQUEST_URL

from loop_ivr.utils.marketinfo import raw_sql
from loop_ivr.models import PriceInfoLog


def send_sms(from_number,to_number,sms_body):
    sms_request_url = SMS_REQUEST_URL%(EXOTEL_ID,EXOTEL_TOKEN,EXOTEL_ID)
    parameters = {'From':from_number,'To':to_number,'Body':sms_body,'Priority':'high'}
    response = requests.post(sms_request_url,data=parameters)
    if response.status_code == 200:
        pass
    else:
        module = 'send_sms'
        log = "Status Code: %s (Parameters: %s)"%(str(response.status_code),parameters)
        write_log(HELPLINE_LOG_FILE,module,log)

def get_valid_list(app_name, model_name, requested_item):
    model = get_model(app_name, model_name)
    id_list = set(model.objects.values_list('id', flat=True))
    requested_list = set(int(item) for item in requested_item.split('*') if item)
    if 0 in requested_list:
        return list(id_list)
    return list(requested_list.intersection(id_list))

def run_query(query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def send_info(to_number, content):
    index = 0
    from_number = '01139589707'
    while index < len(content):
        send_sms(from_number, to_number, content[index:index+1998])
        index += 1998
        time.sleep(1)

def get_price_info(from_number, crop_list, mandi_list, price_info_incoming_obj):
    price_info_list = []
    price_info_log_list = []
    crop_map = dict()
    mandi_map = dict()
    all_crop = Crop.objects.filter(id__in=crop_list).values('id', 'crop_name')
    all_mandi = Mandi.objects.filter(id__in=mandi_list).values('id', 'mandi_name')
    for crop in all_crop:
        crop_map[crop['id']] = crop['crop_name']
    for mandi in all_mandi:
        mandi_map[mandi['id']] = mandi['mandi_name']
    # Fetching price from DB
    for crop in crop_list:
        for mandi in mandi_list:
            # creating obj for log
            price_info_log_obj = PriceInfoLog(price_info_incoming=price_info_incoming_obj,
                                    crop_id=crop, mandi_id=mandi)
            price_info_log_list.append(price_info_log_obj)
            # Preparing Raw SQL Query
            last_three_trans = raw_sql.last_three_trans%(crop,mandi)
            query_result = run_query(last_three_trans)
            temp_str = ('\n%s,%s\n')%(crop_map[crop].encode("utf-8"),mandi_map[mandi].encode("utf-8"))
            price_info_list.append(temp_str)
            for row in query_result:
                date, min_price, max_price, mean = row[2], row[3], row[4], row[5]
                if max_price-min_price >= 2:
                    min_price = mean-1
                    max_price = mean+1
                temp_str = ('%s: %s to %s\n')%(date.strftime('%d-%m-%Y'),str(min_price),str(max_price))
                price_info_list.append(temp_str)
    final_result = ''.join(price_info_list)
    send_info(from_number, final_result)
    price_info_incoming_obj.info_status = 1
    price_info_incoming_obj.save()
    PriceInfoLog.objects.bulk_create(price_info_log_list)
    '''
    last_three_trans = raw_sql.last_three_trans%(','.join(map(str,crop_list)),','.join(map(str,mandi_list)))
    query_result = run_query(last_three_trans)
    pre_mandi = -1
    pre_crop = -1
    for row in query_result:
        if (pre_crop != row[0]) or (pre_mandi != row[1]):
            temp_str = ('\n%s,%s\n')%(crop_map[row[0]].encode("utf-8"),mandi_map[row[1]].encode("utf-8"))
            price_info_list.append(temp_str)
            pre_crop, pre_mandi = row[0], row[1]
        date, min_price, max_price, mean = row[2], row[3], row[4], row[5]
        if max_price-min_price >= 2:
            min_price = mean-1
            max_price = mean+1
        temp_str = ('%s: %s to %s\n')%(date.strftime('%d-%m-%Y'),str(min_price),str(max_price))
        price_info_list.append(temp_str)
    '''
