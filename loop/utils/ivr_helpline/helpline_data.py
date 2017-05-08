# -*- coding: utf-8 -*-

helpline_data = {'sms_body':'लूप मे कॉल के लिए धन्यवाद,आपको कुछ समय मे संपर्क करेगे, न.-01139595953', 
				 'working_hours_start': 9,
				 'working_hours_end': 21
				 }
CALL_STATUS_URL = 'https://%s:%s@twilix.exotel.in/v1/Accounts/%s/Calls/%s?details=true'
CALL_REQUEST_URL = 'https://%s:%s@twilix.exotel.in/v1/Accounts/%s/Calls/connect'
#CALL_RESPONSE_URL = 'http://www.digitalgreen.org/loop/helpline_call_response/'
CALL_RESPONSE_URL = 'http://sandbox.dgtest.org/loop/helpline_call_response/'
SMS_REQUEST_URL = 'https://%s:%s@twilix.exotel.in/v1/Accounts/%s/Sms/send'
APP_REQUEST_URL = 'https://%s:%s@twilix.exotel.in/v1/Accounts/%s/Calls/connect'
APP_URL = 'http://my.exotel.in/exoml/start/%s'
#BROADCAST_RESPONSE_URL = 'http://dgtest.org:2345/loop/broadcast_call_response/'
BROADCAST_RESPONSE_URL = 'http://sandbox.dgtest.org/loop/broadcast_call_response/'
BROADCAST_S3_BUCKET_NAME = 'dg_ivrs'
BROADCAST_S3_UPLOAD_PATH = 'broadcast/%s'
BROADCAST_S3_AUDIO_URL = 'https://s3.amazonaws.com/%s/%s'%(BROADCAST_S3_BUCKET_NAME,BROADCAST_S3_UPLOAD_PATH)
