"""
 This code sample demonstrates an implementation of the Lex Code Hook Interface
 in order to serve a bot which manages dentist appointments.
 Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
 as part of the 'MakeAppointment' template.

 For instructions on how to set up and test this bot, as well as additional samples,
 visit the Lex Getting Started documentation http://docs.aws.amazon.com/lex/latest/dg/getting-started.html.
"""

import psycopg2
import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
import sys
import urllib.parse as up
from datetime import timedelta
#from datetime import datetime
import urllib3
import re

sys.path.insert(0, '/psycopg2')
up.uses_netloc.append("postgres")

# url = up.urlparse(os.environ[
#     "postgres://ivsnhdra:gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f@john.db.elephantsql.com:5432/ivsnhdra"]
#                   )
# conn = psycopg2.connect(database=url.path[1:],
#                         user=url.username,
#                         password=url.password,
#                         host=url.hostname,
#                         port=url.port)
##conn = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")


xxx = {
    "messageVersion": "1.0",
    "invocationSource": "DialogCodeHook",
    "userId": "user-1",
    "sessionAttributes": {},
    "bot": {
        "name": "VietnameseHospitalBot",
        "alias": "$LATEST",
        "version": "$LATEST"
    },
    "outputDialogMode": "Text",
    "currentIntent": {
        "name": "VietnameseMakeAppointment",
        "slots": {
            "Confirmation": None,
    "Date": None,
    "DateOfBird": None,
    "DiseaseOne": None,
    "DiseaseTwo": None,
    "Doctor": "thảo",
    "FormattedDate": None,
    "Name": None,
    "PhoneNumber": None,
    "Speciality": "Trung Tâm Điều Trị Ung Thư Hy Vọng",
    "Time": None,
    "UpdateSlot": None
        }
    },
    "requestAttributes": {
        "x-amz-lex:facebook-page-id": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "x-amz-lex:channel-id": "XXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
        "x-amz-lex:webhook-endpoint-url": "https://channels.lex.us-east-1.amazonaws.com/facebook/webhook/XXX-XXXX-XXXXXXXXX",
        "x-amz-lex:accept-content-types": "PlainText",
        "x-amz-lex:user-id": "2768186586569088",
        "x-amz-lex:channel-name": "FacebookLexBotAppName",
        "x-amz-lex:channel-type": "Facebook"
    }
}


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit,
                message, response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message,
            'responseCard': response_card
        }
    }


# import urllib.parse as up
# import psycopg2


# up.uses_netloc.append("postgres")
# url = up.urlparse(os.environ[
#     "postgres://ivsnhdra:gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f@john.db.elephantsql.com:5432/ivsnhdra"]
#                   )
# conn = psycopg2.connect(database=url.path[1:],
#                         user=url.username,
#                         password=url.password,
#                         host=url.hostname,
#                         port=url.port)
def confirm_intent(session_attributes, intent_name, slots, message,
                   response_card):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message,
            'responseCard': response_card
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def close2(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message,
            "responseCard": {
                "version": 1,
                "contentType": "application/vnd.amazonaws.card.generic",
                "genericAttachments": [
                    {
                        "title": "Các dịch vụ hỗ trợ của Chatbot",
                        "subTitle": "Bạn muốn được hỗ trợ dịch vụ nào?",
                        "imageUrl": "https://moitruong.net.vn/wp-content/uploads/2019/08/bo-y-te-ly-giai-ve-gia-giuong-dich-vu-4-trieu-dong-ngay-ngang-khach-san-hang-sang-hinh-anh0556686901.jpg",
                        "attachmentLinkUrl": "https://www.fvhospital.com/vi/trang-chu/",
                        "buttons": [
                            {
                                "text": "Lấy lịch hẹn",
                                "value": "lấy lịch hẹn"
                            },
                            {
                                "text": "Chỉnh sửa lịch hẹn",
                                "value": "Chỉnh sửa lịch hẹn"
                            },
                            {
                                "text": "Hủy lịch hẹn",
                                "value": "hủy hẹn"
                            }]
                    },{
                        "title": "Các dịch vụ hỗ trợ của Chatbot",
                        "subTitle": "Bạn muốn được hỗ trợ dịch vụ nào?",
                        "imageUrl": "https://moitruong.net.vn/wp-content/uploads/2019/08/bo-y-te-ly-giai-ve-gia-giuong-dich-vu-4-trieu-dong-ngay-ngang-khach-san-hang-sang-hinh-anh0556686901.jpg",
                        "attachmentLinkUrl": "https://www.fvhospital.com/vi/trang-chu/",
                        "buttons": [
                            {
                                "text": "Xem lịch hẹn",
                                "value": "xem lịch hẹn"
                            },
                            {
                                "text": "Xem thông tin bệnh viện",
                                "value": "Xem thông tin bệnh viện"
                            }]
                    }]
            }
        }
    }
    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


def valid_appointment(doctor, speciality, date, time):
    day_strings = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    value_time = []
    try:
        connection = psycopg2.connect(
            "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
        #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
        cursor = connection.cursor()
        date_weekday = day_strings[datetime.datetime.strptime(
            date, '%Y-%m-%d').date().weekday()]  # ngày kiểu datetime
        if speciality:
            cursor.execute("SELECT wh.time FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}' and ms.name = '{}' and wh.day='{}'  order by wh.time;".format(
                doctor, speciality, date_weekday))
        else:
            cursor.execute("SELECT wh.time FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}'  and wh.day='{}'  order by wh.time;".format(
                doctor, date_weekday))
        records = cursor.fetchall()
        if len(records) == 0:
            return False
        # print(len(records))
        for row in records:
            time_temp = row[0].split(' – ')
            if(len(time_temp) != 2):
                time_temp = row[0].split(' - ')
            if(len(time_temp) != 2):
                time_temp = row[0].split('–')
            if(len(time_temp) != 2):
                time_temp = row[0].split('-')
            time_begin = time_temp[0]
            time_end = time_temp[1]
            # print('time begin:---%s------'%time_begin)
            # print('time end:----------%s----' %time_end)
            while compare_time(time_begin, time_end) < 0:
                # xxxxxxxxxxxxxxxx
                try:
                    if speciality:
                        cursor.execute("SELECT * FROM appointment_schedule as a where a.doctor = '{}' and a.speciality = '{}' and a.date='{}' and a.time='{}';".format(
                            doctor, speciality, date, time_begin))
                    else:
                        cursor.execute("SELECT * FROM appointment_schedule as a where a.doctor = '{}'  and a.date='{}' and a.time='{}';".format(
                            doctor, date, time_begin))
                    records2 = cursor.fetchall()
                    # nếu lịch hẹn này chưa được đặt trong hệ thống thì xuất 1 button lịch này ra màn hình
                    #print('records2:', records2)
                    if len(records2) == 0:
                        value_time.append(time_begin)
                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL", error)
                time_begin = increment_time_by_thirty_mins(time_begin)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if(connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    for x in value_time:
        if time == x:
            return True
    return False


def build_response_card(title, subtitle, options, imageUrl):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    genericAttachments = []
    if options is not None:
        buttons = []
        genericAttachmentElement = {}
        cnt = 0
        option_length = len(options)
        if option_length > 30:
            option_length = 30
        for i in range(option_length):
            buttons.append(options[i])
            cnt = cnt+1
            if cnt == 3 or i == len(options)-1:
                genericAttachmentElement = {
                    'title': title,
                    'subTitle': subtitle,
                    'buttons': buttons,
                    "imageUrl": imageUrl,
                }
                genericAttachments.append(genericAttachmentElement)
                cnt = 0
                buttons = []

    return {
        'contentType':
        'application/vnd.amazonaws.card.generic',
        'version':
        1,
        'genericAttachments': genericAttachments
    }

    # return
    #   {
    #     "attachmentLinkUrl": null,
    #     "buttons": [
    #       {
    #         "text": "Nam",
    #         "value": "Nam"
    #       },
    #       {
    #         "text": "Nữ",
    #         "value": "Nữ"
    #       }
    #     ],
    #     "imageUrl": null,
    #     "subTitle": null,
    #     "title": "Giới tính của bạn là gì?"
    #   },
    #   {
    #     "attachmentLinkUrl": null,
    #     "buttons": [
    #       {
    #         "text": "nam1",
    #         "value": "Nam"
    #       },
    #       {
    #         "text": "nu1",
    #         "value": "Nữ"
    #       }
    #     ],
    #     "imageUrl": null,
    #     "subTitle": null,
    #     "title": "Giới tính của bạn là gì?"
    #   }
    # }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def increment_time_by_thirty_mins(appointment_time):
    hour, minute = map(int, appointment_time.split(':'))
    temp = hour*60+minute+30
    hour = temp//60
    minute = temp % 60
    hour_str = hour
    minute_str = minute
    if(hour < 10):
        hour_str = '0{}'.format(hour)
    if(minute < 10):
        minute_str = '0{}'.format(minute)
    return '{}:{}'.format(hour_str, minute_str)


def compare_time(time1, time2):
    hour1, minute1 = map(int, time1.split(':'))
    hour2, minute2 = map(int, time2.split(':'))
    if hour1 > hour2:
        return 1
    elif hour1 < hour2:
        return -1
    else:
        if minute1 > minute2:
            return 1
        elif minute1 < minute2:
            return -1
        else:
            return 0


def get_random_int(minimum, maximum):
    """
    Returns a random integer between min (included) and max (excluded)
    """
    min_int = math.ceil(minimum)
    max_int = math.floor(maximum)

    return random.randint(min_int, max_int - 1)


def get_availabilities(date):
    """
    Helper function which in a full implementation would  feed into a backend API to provide query schedule availability.
    The output of this function is an array of 30 minute periods of availability, expressed in ISO-8601 time format.

    In order to enable quick demonstration of all possible conversation paths supported in this example, the function
    returns a mixture of fixed and randomized results.

    On Mondays, availability is randomized; otherwise there is no availability on Tuesday / Thursday and availability at
    10:00 - 10:30 and 4:00 - 5:00 on Wednesday / Friday.
    """
    day_of_week = dateutil.parser.parse(date).weekday()
    availabilities = []
    available_probability = 0.3
    if day_of_week == 0:
        start_hour = 10
        while start_hour <= 16:
            if random.random() < available_probability:
                # Add an availability window for the given hour, with duration determined by another random number.
                appointment_type = get_random_int(1, 4)
                if appointment_type == 1:
                    availabilities.append('{}:00'.format(start_hour))
                elif appointment_type == 2:
                    availabilities.append('{}:30'.format(start_hour))
                else:
                    availabilities.append('{}:00'.format(start_hour))
                    availabilities.append('{}:30'.format(start_hour))
            start_hour += 1

    if day_of_week == 2 or day_of_week == 4:
        availabilities.append('10:00')
        availabilities.append('16:00')
        availabilities.append('16:30')

    return availabilities


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def is_available(appointment_time, duration, availabilities):
    """
    Helper function to check if the given time and duration fits within a known set of availability windows.
    Duration is assumed to be one of 30, 60 (meaning minutes).  Availabilities is expected to contain entries of the format HH:MM.
    """
    if duration == 30:
        return appointment_time in availabilities
    elif duration == 60:
        second_half_hour_time = increment_time_by_thirty_mins(appointment_time)
        return appointment_time in availabilities and second_half_hour_time in availabilities

    # Invalid duration ; throw error.  We should not have reached this branch due to earlier validation.
    raise Exception('Was not able to understand duration {}'.format(duration))


def get_duration(appointment_type):
    appointment_duration_map = {
        'cleaning': 30,
        'root canal': 60,
        'whitening': 30
    }
    return try_ex(lambda: appointment_duration_map[appointment_type.lower()])


def get_availabilities_for_duration(duration, availabilities):
    """
    Helper function to return the windows of availability of the given duration, when provided a set of 30 minute windows.
    """
    duration_availabilities = []
    start_time = '10:00'
    while start_time != '17:00':
        if start_time in availabilities:
            if duration == 30:
                duration_availabilities.append(start_time)
            elif increment_time_by_thirty_mins(start_time) in availabilities:
                duration_availabilities.append(start_time)

        start_time = increment_time_by_thirty_mins(start_time)

    return duration_availabilities


def build_validation_result(is_valid, violated_slot, message_content):
    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {
            'contentType': 'PlainText',
            'content': message_content
        }
    }


def validate_book_appointment(appointment_type, date, appointment_time):
    if appointment_type and not get_duration(appointment_type):
        return build_validation_result(
            False, 'AppointmentType',
            'I did not recognize that, can I book you a root canal, cleaning, or whitening?'
        )

    if appointment_time:
        if len(appointment_time) != 5:
            return build_validation_result(
                False, 'Time',
                'I did not recognize that, what time would you like to book your appointment?'
            )

        hour, minute = appointment_time.split(':')
        hour = parse_int(hour)
        minute = parse_int(minute)
        if math.isnan(hour) or math.isnan(minute):
            return build_validation_result(
                False, 'Time',
                'I did not recognize that, what time would you like to book your appointment?'
            )

        if hour < 10 or hour > 16:
            # Outside of business hours
            return build_validation_result(
                False, 'Time',
                'Our business hours are ten a.m. to five p.m.  What time works best for you?'
            )

        if minute not in [30, 0]:
            # Must be booked on the hour or half hour
            return build_validation_result(
                False, 'Time',
                'We schedule appointments every half hour, what time works best for you?'
            )

    if date:
        if not isvalid_date(date):
            return build_validation_result(
                False, 'Date',
                'I did not understand that, what date works best for you?')
        elif datetime.datetime.strptime(
                date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(
                False, 'Date',
                'Appointments must be scheduled a day in advance.  Can you try a different date?'
            )
        elif dateutil.parser.parse(date).weekday(
        ) == 5 or dateutil.parser.parse(date).weekday() == 6:
            return build_validation_result(
                False, 'Date',
                'Our office is not open on the weekends, can you provide a work day?'
            )

    return build_validation_result(True, None, None)


def build_time_output_string(appointment_time):
    hour, minute = appointment_time.split(
        ':'
    )  # no conversion to int in order to have original string form. for eg) 10:00 instead of 10:0
    if int(hour) > 12:
        return '{}:{} p.m.'.format((int(hour) - 12), minute)
    elif int(hour) == 12:
        return '12:{} p.m.'.format(minute)
    elif int(hour) == 0:
        return '12:{} a.m.'.format(minute)

    return '{}:{} a.m.'.format(hour, minute)


def build_available_time_string(availabilities):
    """
    Build a string eliciting for a possible time slot among at least two availabilities.
    """
    prefix = 'We have availabilities at '
    if len(availabilities) > 3:
        prefix = 'We have plenty of availability, including '

    prefix += build_time_output_string(availabilities[0])
    if len(availabilities) == 2:
        return '{} and {}'.format(prefix,
                                  build_time_output_string(availabilities[1]))

    return '{}, {} and {}'.format(prefix,
                                  build_time_output_string(availabilities[1]),
                                  build_time_output_string(availabilities[2]))


def build_options(slot, speciality, doctor, date, time, psid):
    """
    Build a list of potential options for a given slot, to be used in responseCard generation.
    """
    day_strings = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    if slot == 'Speciality':
        try:
            connection = psycopg2.connect(
                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT * FROM medical_specialities;")
            records = cursor.fetchall()
            cnt = 0
            #print("Records of books in the table")
            # for row in records:
            #     print("\nid = ", row[0])
            #     print("name = ", row[1])
            #     print("image = ", row[2])
            #     print("languge = ", row[3])
            #     print("rank = ", row[4], "\n")
            cnt = cnt+1
            print(cnt)

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            # closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
        res = []
        for row in records:
            temp = {
                'text': row[1],
                'value': row[1]}
            res.append(temp)
        return res
    elif slot == 'Doctor':
        try:
            connection = psycopg2.connect(
                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            if speciality:
                if not doctor:
                    cursor.execute(
                        "SELECT * FROM doctors as d,medical_specialities as ms WHERE ms.id=d.speciality_id and ms.name = '{}';".format(speciality))
                else:
                    cursor.execute(
                        "SELECT * FROM doctors as d,medical_specialities as ms WHERE ms.id=d.speciality_id and ms.name = '{}' and d.name ILIKE '%{}';".format(speciality, doctor))
            else:
                if doctor:
                    cursor.execute(
                        "SELECT * FROM doctors as d,medical_specialities as ms WHERE ms.id=d.speciality_id and d.name ILIKE '%{}';".format(doctor))
            records = cursor.fetchall()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            # closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
        res = []
        if len(records) == 0:
            return None
        for row in records:
            temp = {
                'text': row[1],
                'value': row[1]}
            res.append(temp)
        return res
    # elif slot == 'Date1':
    #     try:
    #         connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

    #         cursor = connection.cursor()
    #         # Print PostgreSQL Connection properties
    #         print ("hi", connection.get_dsn_parameters(),"\n")
    #         print("khoa:%s"%speciality)
    #         print("bacsi:%s"%doctor)

    #          # Print PostgreSQL version
    #         cursor.execute("SELECT distinct wh.day FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name=%s and ms.name=%s;",(doctor,speciality))
    #         records = cursor.fetchall()
    #     except (Exception, psycopg2.Error) as error :
    #          print ("Error while connecting to PostgreSQL", error)
    #     finally:
    #         #closing database connection.
    #         if(connection):
    #             cursor.close()
    #             connection.close()
    #             print("PostgreSQL connection is closed")
    #     res=[]
    #     dict_date = {'Mon': False, 'Tue': False, 'Wed': False,'Thu':False,'Fri':False,'Sat':False,'Sun':False}
    #     date_of_week=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    #     for row in records:
    #         if(row[0]=='Mon'):
    #             dict_date['Mon']=True
    #         elif row[0]=='Tue':
    #             dict_date['Tue']=True
    #         elif row[0]=='Wed':
    #             dict_date['Wed']=True
    #         elif row[0]=='Thu':
    #             dict_date['Thu']=True
    #         elif row[0]=='Fri':
    #             dict_date['Fri']=True
    #         elif row[0]=='Sat':
    #             dict_date['Sat']=True
    #         elif row[0]=='Sun':
    #             dict_date['Sun']=True
    #     day_index=datetime.date.today().weekday()
    #     day_value=datetime.date.today()
    #     i=0
    #     while i<14:
    #         key=date_of_week[day_index]
    #         value=dict_date[key]
    #         if(value==True):
    #             temp={
    #             'text': day_value,
    #             'value': day_value}
    #         res.append(temp)
    #         day_index=day_index+1
    #         day_index=day_index%7
    #         day_value=day_value+ timedelta(days=1)
    #         i=i+1
    #     return res
    elif slot == 'Date':
        # Return the next five weekdays.
        try:
            connection = psycopg2.connect(
                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            # print ("hi", connection.get_dsn_parameters(),"\n")
            # print("khoa:%s"%speciality)
            # print("bacsi:%s"%doctor)

            # Print PostgreSQL version
            if speciality:
                cursor.execute("SELECT distinct wh.day FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}' and ms.name = '{}';".format(
                    doctor, speciality))
            else:
                cursor.execute(
                    "SELECT distinct wh.day FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}';".format(doctor))
            records = cursor.fetchall()
            if len(records) == 0:
                return None
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL ", error)
        # finally:
        #     # closing database connection.
        #     if(connection):
        #         cursor.close()
        #         connection.close()
        #         print("PostgreSQL connection is closed")
        dict_date = {'Mon': False, 'Tue': False, 'Wed': False,
                     'Thu': False, 'Fri': False, 'Sat': False, 'Sun': False}
        for row in records:
            if(row[0] == 'Mon'):
                dict_date['Mon'] = True
            elif row[0] == 'Tue':
                dict_date['Tue'] = True
            elif row[0] == 'Wed':
                dict_date['Wed'] = True
            elif row[0] == 'Thu':
                dict_date['Thu'] = True
            elif row[0] == 'Fri':
                dict_date['Fri'] = True
            elif row[0] == 'Sat':
                dict_date['Sat'] = True
            elif row[0] == 'Sun':
                dict_date['Sun'] = True
        options = []
        potential_date = datetime.date.today()
        #potential_date.strftime('%A, %B %d, %Y')
        while len(options) < 30:
            potential_date = potential_date + datetime.timedelta(days=1)
            # print(potential_date.weekday())
            # print(len(options))
            if dict_date[day_strings[potential_date.weekday()]] == True:
                try:
                    # connection = psycopg2.connect(
                    #     "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                    # #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
                    #cursor = connection.cursor()
                    if speciality:
                        cursor.execute("SELECT count (*) FROM appointment_schedule as a where a.doctor = '{}' and a.speciality= '{}' and a.date='{}';".format(
                            doctor, speciality, potential_date))
                    else:
                        cursor.execute(
                            "SELECT count (*) FROM appointment_schedule as a where a.doctor = '{}' and a.date='{}';".format(doctor, potential_date))
                    records = cursor.fetchall()
                    booked = records[0][0]
                    # lấy số slot có thể có trong ngày đang xét
                    cnt = 0  # số lượng slot có thể có trong ngày đang xét
                    try:
                        #print('potential_date:', potential_date)
                        # ngày kiểu datetime
                        date_weekday = day_strings[potential_date.weekday()]
                        #print('date_weekday:', date_weekday)
                        if speciality:
                            cursor.execute("SELECT wh.time FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}' and ms.name = '{}' and wh.day='{}'  order by wh.time;".format(
                                doctor, speciality, date_weekday))
                        else:
                            cursor.execute("SELECT wh.time FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}'  and wh.day='{}'  order by wh.time;".format(
                                doctor, date_weekday))

                        records = cursor.fetchall()
                        if len(records) == 0:
                            return None
                        for row in records:
                            time_temp = row[0].split(' – ')
                            if(len(time_temp) != 2):
                                time_temp = row[0].split(' - ')
                            if(len(time_temp) != 2):
                                time_temp = row[0].split('–')
                            if(len(time_temp) != 2):
                                time_temp = row[0].split('-')
                            time_begin = time_temp[0]
                            time_end = time_temp[1]
                            #print('time_begin:', time_begin)
                            #print('time_end:', time_end)
                            # trừ lấy số giờ
                            format = '%H:%M'
                            time_begin = datetime.datetime.strptime(
                                time_begin, format)

                            time_end = datetime.datetime.strptime(
                                time_end, format)

                            duration = time_end-time_begin
                            #print('duration:', duration.seconds/60)
                            # đổi giờ thành cnt
                            cnt = cnt+duration.seconds/1800
                    except (Exception, psycopg2.Error) as error:
                        print("Error while connecting to PostgreSQL1", error)
                    # so sánh
                    #print('so luong lich da dat: ', booked)
                    #print('count:', cnt)
                    day_strings_vn=['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ nhật']
                    if booked < cnt:
                        options.append({'text': '{}-{} ({})'.format(potential_date.day, potential_date.month, day_strings_vn[potential_date.weekday()]),
                                        'value': potential_date.strftime('%Y-%d-%m')})
                        # print('hi')
                    if len(records) == 0:
                        return None
                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL2", error)
        if(connection):
            cursor.close()
            connection.close()
            # print('**********************')
        return options
    elif slot == 'Time':
        # Return the availabilities on the given date.
        if not date:
            return None

        # availabilities = try_ex(lambda: booking_map[date])
        # if not availabilities:
        #     return None

        # availabilities = get_availabilities_for_duration(get_duration(appointment_type), availabilities)
        # if len(availabilities) == 0:
        #     return None
        # options = []
        # for i in range(min(len(availabilities), 5)):
        #     options.append({'text': build_time_output_string(availabilities[i]), 'value': build_time_output_string(availabilities[i])})

        # return options
        value_time = []
        res = []
        a = []
        try:
            connection = psycopg2.connect(
                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
            a.append(3)
            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            # print ("hi", connection.get_dsn_parameters(),"\n")
            # print("khoa:%s"%speciality)
            # print("bacsi:%s"%doctor)

            # try:
            #     date_weekdate=datetime.datetime.strptime(date, '%d/%m/%y').date().weekday() #ngày kiểu datetime
            # except ValueError as ve:
            #     print('ValueError Raised:', ve)

            date_weekday = day_strings[datetime.datetime.strptime(
                date, '%Y-%m-%d').date().weekday()]  # ngày kiểu datetime
            # Print PostgreSQL version
            if speciality:
                cursor.execute("SELECT wh.time FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}' and ms.name = '{}' and wh.day='{}'  order by wh.time;".format(
                    doctor, speciality, date_weekday))
            else:
                cursor.execute("SELECT wh.time FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name = '{}'  and wh.day='{}'  order by wh.time;".format(
                    doctor, date_weekday))

            records = cursor.fetchall()
            if len(records) == 0:
                return None
            # print(len(records))
            for row in records:
                time_temp = row[0].split(' – ')
                if(len(time_temp) != 2):
                    time_temp = row[0].split(' - ')
                if(len(time_temp) != 2):
                    time_temp = row[0].split('–')
                if(len(time_temp) != 2):
                    time_temp = row[0].split('-')
                time_begin = time_temp[0]
                time_end = time_temp[1]
                # print('time begin:---%s------'%time_begin)
                # print('time end:----------%s----' %time_end)
                while compare_time(time_begin, time_end) < 0:
                    try:
                        if speciality:
                            cursor.execute("SELECT * FROM appointment_schedule as a where a.doctor = '{}' and a.speciality = '{}' and a.date='{}' and a.time='{}';".format(
                                doctor, speciality, date, time_begin))
                        else:
                            cursor.execute("SELECT * FROM appointment_schedule as a where a.doctor = '{}'  and a.date='{}' and a.time='{}';".format(
                                doctor, date, time_begin))
                        records2 = cursor.fetchall()
                        # nếu lịch hẹn này chưa được đặt trong hệ thống thì xuất 1 button lịch này ra màn hình
                        #print('records2:', records2)
                        if len(records2) == 0:
                            value_time.append(time_begin)
                    except (Exception, psycopg2.Error) as error:
                        print("Error while connecting to PostgreSQL", error)
                    time_begin = increment_time_by_thirty_mins(time_begin)
                    #print('time begin update: %s' % time_begin)
                # print('***************************************')
            # print('end')
            for x in value_time:
                if date==datetime.datetime.now().date():
                    if time>datetime.datetime.now().time():
                        temp = {
                            'text': build_time_output_string(x),
                            'value': build_time_output_string(x)}
                else:
                    temp = {
                            'text': build_time_output_string(x),
                            'value': build_time_output_string(x)}
                res.append(temp)
            return res

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            # closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
        return None
    elif slot == 'UpdateSlot':
        res = [{
            'text': "Bác sĩ",
            'value': "Bác Sĩ"},
            {
            'text': "Ngày",
            'value': "Ngày"},
            {
            'text': "Giờ",
            'value': "Giờ"}]
        return res
    elif slot == 'name':
        try:
            connection = psycopg2.connect(
                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
            cursor = connection.cursor()
            cursor.execute(
                "SELECT distinct a.patient_name FROM appointment_schedule as a where a.psid='{}';".format(psid))
            records = cursor.fetchall()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
        res = []
        for row in records:
            temp = {
                'text': row[0],
                'value': row[0]}
            res.append(temp)
        temp = {
            'text': 'Người khác',
            'value': 'Người khác'}
        res.append(temp)
        return res
    elif slot == 'Confirmation':
        res = [{
            'text': "Có",
            'value': "Có"},
            {
            'text': "Không",
            'value': "Không"}]
        return res
    elif slot == 'UpdateInfor':
        res = [{
            'text': "Có",
            'value': "Có"},
            {
            'text': "Không",
            'value': "Không"}]
        return res


""" --- Functions that control the bot's behavior --- """


def make_appointment(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    # appointment_type = intent_request['currentIntent']['slots']['AppointmentType']
    # date = intent_request['currentIntent']['slots']['Date']
    # appointment_time = intent_request['currentIntent']['slots']['Time']
    # source = intent_request['invocationSource']
    # output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    # booking_map = json.loads(try_ex(lambda: output_session_attributes['bookingMap']) or '{}')
    DiseaseOne = intent_request['currentIntent']['slots']['DiseaseOne']
    speciality = intent_request['currentIntent']['slots']['Speciality']
    doctor = intent_request['currentIntent']['slots']['Doctor']
    time = intent_request['currentIntent']['slots']['Time']
    date = intent_request['currentIntent']['slots']['Date']
    name = intent_request['currentIntent']['slots']['Name']
    DateOfBird = intent_request['currentIntent']['slots']['DateOfBird']
    PhoneNumber = intent_request['currentIntent']['slots']['PhoneNumber']
    FormattedDate = intent_request['currentIntent']['slots']['FormattedDate']
    # UpdateSlot thể hiện slot cần được thay đổi khi tất cả các thông tin khoa, bác sĩ, ngày giờ được chọn không tồn tại
    UpdateSlot = intent_request['currentIntent']['slots']['UpdateSlot']
    UpdateInfor = intent_request['currentIntent']['slots']['UpdateInfor']
    Confirmation = intent_request['currentIntent']['slots']['Confirmation']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request[
        'sessionAttributes'] if intent_request[
            'sessionAttributes'] is not None else {}
    psid = "2768186586569088"
    #psid="2872158819534978"
    try:
        psid = intent_request['requestAttributes']['x-amz-lex:user-id']
    except Exception as error:
        print("get psid error", error)
    finally:
        print("get psid final")
    print("psid type:", type(psid))
    # ,profile_pic,locale,timezone,gender
    URL = "https://graph.facebook.com/{}?fields=name,first_name,last_name&access_token=EAACtffPGBe4BAGvNefOdwJDnB8s2wZAQgNlEBJZCfxgbdZC8ktRuB3NGTIPBR47QDc5KDwa9w3osAbZAnpWQNQneMr4v4SbBauZAjgx06x1xZCZA2dSPFV1rBa1dhnkRcrSM8sgKL5ZAtM20Ww3mnD11jWYweE41x5a8HjkDISWyUFF2TyzhORj5".format(
        psid)
    http = urllib3.PoolManager()
    r = http.request('GET', URL)
    data = json.loads(r.data.decode('utf-8'))
    # print(data)
    fb_name = data['name']
    fb_first_name = data['first_name']
    fb_last_name = data['last_name']
    print('name= ', fb_name)
    if source == 'DialogCodeHook':
        slots = intent_request['currentIntent']['slots']
        if doctor=='Kết thúc':
            return close2(
                output_session_attributes,
                'Fulfilled',
                {
                    'contentType': 'PlainText',
                    'content': 'Bạn có thể tham khảo thêm các hỗ trợ khác của chatbot ở đây:'
                })
        if time:
            arr_time = time.split(':')
            if arr_time[1] != '00' and arr_time[1] != '30':
                hour = int(arr_time[0])
                minute = int(arr_time[1])
                if minute > 0 and minute < 30:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Time', {
                            'contentType': 'PlainText',
                            'content': ';)Bạn cần chọn giờ khám bệnh là giờ tròn ví dụ như {}:{} hoặc {}:{}. Bạn muốn hẹn bác sĩ lúc mấy giờ ạ?'.format(hour, '00', hour, '30')
                        }, None)
                elif minute > 30:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Time', {
                            'contentType': 'PlainText',
                            'content': 'Bạn cần chọn giờ khám bệnh là giờ tròn ví dụ như {}:{} hoặc {}:{}. Bạn muốn hẹn bác sĩ lúc mấy giờ ạ?'.format(hour, '30', hour+1, '00')
                        }, None)
        if date and not FormattedDate:
            # modify format for date input from user become date dd/mm/yyyy->yyyy/mm/dd
            # print(intent_request['currentIntent']['slots'])
            arr_date = date.split('-')
            if int(arr_date[2]) < 13:
                arr_date[1], arr_date[2] = arr_date[2], arr_date[1]
            date = arr_date[0]+'-'+arr_date[1]+'-'+arr_date[2]
            # fix bug loi format 4/5/2020->4/5/2021
            today = datetime.date.today()
            print('today:', today)
            if int(arr_date[0]) == today.year+1:
                print(today.year+1)
                if today.month < int(arr_date[1]) or (today.month == int(arr_date[1]) and today.day < int(arr_date[2])):
                    arr_date[0] = str(today.year)
            date = arr_date[0]+'-'+arr_date[1]+'-'+arr_date[2]
            print('date', date)
            date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
            slots['Date'] = date
            slots['FormattedDate'] = '1'
            # end fix bug
        if UpdateSlot == 'Bác Sĩ':
            slots['Doctor'] = None
            doctor = None
            slots['UpdateSlot'] = None
            UpdateSlot = None
        elif UpdateSlot == 'Khoa':
            slots['Speciality'] = None
            speciality = None
            slots['UpdateSlot'] = None
            UpdateSlot = None
        elif UpdateSlot == 'Ngày':
            slots['Date'] = None
            date = None
            slots['UpdateSlot'] = None
            UpdateSlot = None
        elif UpdateSlot == 'Giờ':
            slots['Time'] = None
            time = None
            slots['UpdateSlot'] = None
            UpdateSlot = None
        # if doctor and date and time:
        #     arr_date = date.split('-')
        #     date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
        #     # nếu lịch không hợp lệ và slottype = null thì hỏi người dùng cần chỉnh UpdateSlot nào. nếu lịch không hợp lệ và slottype khác null thì set slot đang xét về null
        #     # nếu hợp lệ thì set slottype hiện tại bằng null
        #     valid = valid_appointment(doctor, speciality, date, time)
        #     if valid == False:  # cần sửa
        #         if not UpdateSlot:
        #             if speciality:
        #                 message = 'Hiện tại bác sĩ {} của {} không rảnh vào {} ngày {}'.format(
        #                     doctor, speciality, time, date_display)
        #             else:
        #                 message = 'Hiện tại bác sĩ {} không rảnh vào {} ngày {}'.format(
        #                     doctor, time, date_display)
        #             return elicit_slot(
        #                 output_session_attributes,
        #                 intent_request['currentIntent']['name'],
        #                 slots, 'UpdateSlot', {
        #                     'contentType': 'PlainText',
        #                     'content': message
        #                 },
        #                 build_response_card(
        #                     'Để đặt được lịch bạn cần thay đổi 1 yếu tố',
        #                     'Bạn muốn thay đổi yếu tố nào?',
        #                     build_options('UpdateSlot', speciality, doctor, date, time, None)))
        #         else:
        #             if UpdateSlot == 'Bác Sĩ':
        #                 slots['Doctor'] = None
        #                 doctor = None
        #             elif UpdateSlot == 'Khoa':
        #                 slots['Speciality'] = None
        #                 speciality = None
        #             elif UpdateSlot == 'Ngày':
        #                 slots['Date'] = None
        #                 date = None
        #             elif UpdateSlot == 'Giờ':
        #                 slots['Time'] = None
        #                 time = None
        #     else:
        #         slots['UpdateSlot'] = None
        #         UpdateSlot = None

        # không bác sĩ và không khoa
        if not speciality and not doctor:
            slots['UpdateSlot'] = None
            UpdateSlot = None
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                slots, 'Speciality', {
                    'contentType': 'PlainText',
                    'content': '^_^ Bạn muốn khám tại khoa nào ạ?'
                },
                build_response_card(
                    'Các khoa của bệnh viện',
                    'Mời bạn chọn khoa mình muốn khám',
                    build_options('Speciality', speciality, doctor, date, time, None), None))
        # không bác sĩ và có khoa
        elif not doctor:
            options = build_options(
                'Doctor', speciality, doctor, date, time, None)
            if options == None:
                slots['Speciality'] = None
                speciality = None
                slots['UpdateSlot'] = None
                UpdateSlot = None
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Speciality', {
                        'contentType': 'PlainText',
                        'content': 'Vâng, bạn có thể cho tôi biết bạn muốn tới khoa nào khám bệnh không?'
                    },
                    build_response_card(
                        'Các khoa của bệnh viện',
                        'Mời bạn chọn khoa mình muốn khám',
                        build_options('Speciality', speciality, doctor, date, time, None), None))
            else:
                slots['UpdateSlot'] = None
                UpdateSlot = None
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Doctor', {
                        'contentType': 'PlainText',
                        'content': 'Chào mừng bạn đến với {}. Bạn muốn khám với bác sĩ nào ạ? :D'.format(speciality)
                    },
                    build_response_card(
                        'Các bác sĩ hiện có của {}'.format(speciality),
                        'Mời bạn chọn bác sĩ',
                        options, None))
        # có bác sĩ
        #################
        else:
            element_of_name = doctor.split(' ')
            if len(element_of_name) == 1:
                try:
                    connection = psycopg2.connect(
                        "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                    #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
                    cursor = connection.cursor()
                    # Print PostgreSQL Connection properties
                    print(connection.get_dsn_parameters(), "\n")
                    if not speciality:
                        cursor.execute(
                            "SELECT * FROM doctors as d,medical_specialities as ms WHERE ms.id=d.speciality_id and  d.name ILIKE '% {}';".format(doctor))
                        message = 'Có nhiều bác sĩ tên {}, bạn muốn khám với bác sĩ nào ạ?'.format(
                            doctor)
                    else:
                        cursor.execute(
                            "SELECT * FROM doctors as d,medical_specialities as ms WHERE ms.id=d.speciality_id and ms.name = '{}' and d.name ILIKE '% {}';".format(speciality, doctor))
                        message = 'Có nhiều bác sĩ tên {} tại {}, bạn muốn khám với bác sĩ nào ạ?'.format(
                            doctor, speciality)
                    records = cursor.fetchall()
                    if len(records) == 1:
                        doctor = records[0][1]
                        slots['Doctor'] = doctor
                    elif len(records) > 1:
                        slots['UpdateSlot'] = None
                        UpdateSlot = None
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'Doctor', {
                                'contentType': 'PlainText',
                                'content': message
                            },
                            build_response_card(
                                'Các bác sĩ tên {} của khoa'.format(doctor),
                                'Mời bạn chọn họ và tên đầy đủ của bác sĩ',
                                build_options('Doctor', speciality, doctor, date, time, None), None))
                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL", error)
                finally:
                    # closing database connection.
                    if(connection):
                        cursor.close()
                        connection.close()
                        print("PostgreSQL connection is closed")
            elif len(element_of_name) > 1:
                # có bác sĩ nhưng không có khoa
                if not speciality:
                    try:
                        connection = psycopg2.connect(
                            "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                        #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
                        cursor = connection.cursor()
                        # Print PostgreSQL Connection properties
                        print(connection.get_dsn_parameters(), "\n")
                        cursor.execute(
                            "SELECT ms.name FROM doctors as d,medical_specialities as ms WHERE ms.id=d.speciality_id and d.name = '{}';".format(doctor))
                        records = cursor.fetchall()
                        if len(records) == 1:
                            speciality = records[0][0]
                            slots['Speciality'] = speciality
                        elif len(records) > 1:
                            return elicit_slot(
                                output_session_attributes,
                                intent_request['currentIntent']['name'],
                                slots, 'Speciality', {
                                    'contentType': 'PlainText',
                                    'content': 'Bệnh viện có nhiều khoa có bác sĩ tên {}, bạn muốn khám với khoa nào ạ?'.format(doctor)
                                },
                                build_response_card(
                                    'Các khoa có bác sĩ tên {}'.format(doctor),
                                    'Mời bạn chọn khoa',
                                    build_options('Speciality', speciality, doctor, date, time, None), None))
                    except (Exception, psycopg2.Error) as error:
                        print("Error while connecting to PostgreSQL", error)
                    finally:
                        # closing database connection.
                        if(connection):
                            cursor.close()
                            connection.close()
                            print("PostgreSQL connection is closed")
            #########################
            # có bác sĩ và có khoa
            if not date:
                options = build_options(
                    'Date', speciality, doctor, date, time, None)
                slots['UpdateSlot'] = None
                UpdateSlot = None
                if options == None:
                    slots['Doctor'] = None
                    doctor_temp = doctor
                    doctor = None
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Doctor', {
                            'contentType': 'PlainText',
                            'content': '{} không có bác sĩ {}'.format(speciality, doctor_temp)
                        },
                        build_response_card(
                            'Các bác sĩ hiện có của {}'.format(speciality),
                            'Mời bạn chọn bác sĩ',
                            build_options('Doctor', speciality, doctor, date, time, None), None))
                else:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Date', {
                            'contentType': 'PlainText',
                            'content': 'Không biết bạn rảnh vào ngày nào ạ?'
                        },
                        build_response_card(
                            '30 ngày làm việc gần nhất của bác sĩ ' + doctor,
                            'Mời bạn chọn ngày khám bệnh',
                            options, None))
            elif not time:
                if datetime.datetime.strptime(date, '%Y-%m-%d').date()  < datetime.date.today():
                    print("Date invalid")
                    slots['Date']=None
                    slots['FormattedDate']=None
                    options = build_options('Date', speciality, doctor, date, time, None)
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Date', {
                            'contentType': 'PlainText',
                            'content': 'Ngày khám không hợp lệ, mời bạn nhập lại NGÀY muốn khám bệnh?'
                        }, build_response_card(
                            '30 ngày làm việc gần nhất của bác sĩ ' + doctor,
                            'Mời bạn chọn ngày khám bệnh',
                            options, None))
                arr_date = date.split('-')
                date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
                # slots['Date']=date
                # end fix bug
                options = build_options('Time', speciality, doctor, date, time, None)
                slots['UpdateSlot'] = None
                UpdateSlot = None
                if options == None:
                    slots['Date'] = None
                    date = None
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Date', {
                            'contentType': 'PlainText',
                            'content': 'Rất tiếc bác sĩ {} không làm việc vào ngày {}. Bạn có thể chọn ngày khác không ạ?'.format(doctor, date_display)
                        },
                        build_response_card(
                            '30 ngày làm việc gần nhất của bác sĩ ' + doctor,
                            'Mời bạn chọn ngày khám bệnh',
                            build_options('Date', speciality, doctor, date, time, None), None))
                else:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Time', {
                            'contentType': 'PlainText',
                            'content': 'Dạ, bạn muốn hẹn bác sĩ lúc mấy giờ ạ? ;)'
                        },
                        build_response_card(
                            'Thời gian làm việc của bác sĩ {} trong ngày {}'.format(
                                doctor, date_display),
                            'Mời bạn chọn thời gian hẹn bác sĩ',
                            options, None))
            elif not name:
                print('hello1')
                # if doctor and date and time:
                arr_date = date.split('-')
                date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
                # nếu lịch không hợp lệ và slottype = null thì hỏi người dùng cần chỉnh UpdateSlot nào. nếu lịch không hợp lệ và slottype khác null thì set slot đang xét về null
                # nếu hợp lệ thì set slottype hiện tại bằng null
                valid = valid_appointment(doctor, speciality, date, time)
                if valid == False:  # cần sửa
                    if not UpdateSlot:
                        if speciality:
                            message = 'Rất tiếc khi hiện tại bác sĩ {} của {} không rảnh vào {} ngày {}'.format(
                                doctor, speciality, time, date_display)
                        else:
                            message = 'Rất tiếc khi hiện tại bác sĩ {} không rảnh vào {} ngày {}'.format(
                                doctor, time, date_display)
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'UpdateSlot', {
                                'contentType': 'PlainText',
                                'content': message
                            },
                            build_response_card(
                                'Để đặt được lịch bạn cần thay đổi 1 yếu tố',
                                'Bạn muốn thay đổi yếu tố nào?',
                                build_options('UpdateSlot', speciality, doctor, date, time, None), None))
                else:
                    slots['UpdateSlot'] = None
                    UpdateSlot = None
                options = build_options(
                    'name', speciality, doctor, date, time, psid)
                # nếu tài khoản fb này đã từng đặt lịch hẹn thì xuất ra tên bệnh nhân đã từng khám, ngược lại thì chuyển về delegate cho Lex xử lý
                if len(options) > 1:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Name', {
                            'contentType': 'PlainText',
                            'content': 'Vâng! Bạn muốn khám bệnh cho ai ạ?'
                        },
                        build_response_card(
                            'Danh sách các bệnh nhân đã được đặt lịch hẹn bằng tài khoản Facebook này',
                            'Mời bạn chọn tên bệnh nhân',
                            options, None))
            elif name == 'Người khác' or name == 'khác':
                slots['Name'] = None
                name = None
            elif not DateOfBird:
                print('hello2')
                try:
                    connection = psycopg2.connect(
                        "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                    #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT a.patient_name,a.date_of_birth,a.phone_number FROM appointment_schedule as a where a.patient_name ilike '{}' and a.psid='{}';".format(name, psid))
                    record = cursor.fetchone()
                    count=cursor.rowcount
                    if count==0:
                        return delegate(output_session_attributes, slots)
                    name = record[0]
                    DateOfBird = record[1].strftime('%Y-%m-%d')
                    PhoneNumber = record[2]
                    slots['Name'] = record[0]
                    slots['DateOfBird'] = record[1].strftime('%Y-%m-%d')
                    slots['PhoneNumber'] = record[2]
                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL", error)
                finally:
                    if(connection):
                        cursor.close()
                        connection.close()
                        print("PostgreSQL connection is closed")
                options = build_options(
                    'Confirmation', speciality, doctor, date, time, None)
                arr_date = date.split('-')
                date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
                print(DateOfBird)
                arr_date_of_bird = DateOfBird.split('-')
                date_of_bird_display = arr_date_of_bird[2] + \
                    '/'+arr_date_of_bird[1]+'/'+arr_date_of_bird[0]
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Confirmation', {
                        'contentType': 'PlainText',
                        'content': 'Thông tin chi tiết của bạn như sau: Bệnh nhân {} sinh ngày {} có số điện thoại {} có lịch hẹn với bác sĩ {} của {} vào lúc {} ngày {}. ;)'.format(name, date_of_bird_display, PhoneNumber, doctor, speciality, time, date_display)
                    },
                    build_response_card(
                        'Bạn có chắc chắn muốn đặt lịch hẹn không?',
                        'Lựa chọn dành cho bạn',
                        options, 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTyzsYL2jWkqRAexHhYrsFvoWnMMVdcwjeMdwf-0poUPi2-I6jd'))
            elif DateOfBird and not PhoneNumber:
                # modify format for date input from user become date dd/mm/yyyy->yyyy/mm/dd
                # print(intent_request['currentIntent']['slots'])
                slots['UpdateSlot'] = None
                UpdateSlot = None
                arr_date = DateOfBird.split('-')
                if int(arr_date[2]) < 13:
                    arr_date[1], arr_date[2] = arr_date[2], arr_date[1]
                DateOfBird = arr_date[0]+'-'+arr_date[1]+'-'+arr_date[2]
                slots['DateOfBird'] = DateOfBird
                if datetime.datetime.strptime(DateOfBird, '%Y-%m-%d').date()  >= datetime.date.today():
                    print("DateOfBird invalid")
                    slots['DateOfBird']=None
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'DateOfBird', {
                            'contentType': 'PlainText',
                            'content': 'Ngày tháng năm sinh không hợp lệ, mời bạn nhập lại NGÀY THÁNG NĂM SINH?'
                        }, None)
            elif not Confirmation:
                regex= "(03|07|08|09|01[2|6|8|9])+([0-9]{8})\\b"
                if not re.search(regex, PhoneNumber):
                    slots['PhoneNumber']=None
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'PhoneNumber', {
                            'contentType': 'PlainText',
                            'content': 'Số điện thoại trên không hợp lệ, bạn hãy nhập SỐ ĐIỆN THOẠI chính xác?'
                        }, None)
                options = build_options(
                    'Confirmation', speciality, doctor, date, time, None)
                arr_date = date.split('-')
                date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
                arr_date_of_bird = DateOfBird.split('-')
                date_of_bird_display = arr_date_of_bird[2] + \
                    '/'+arr_date_of_bird[1]+'/'+arr_date_of_bird[0]
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Confirmation', {
                        'contentType': 'PlainText',
                        'content': 'Thông tin chi tiết của bạn như sau: Bệnh nhân {} sinh ngày {} có số điện thoại {} có lịch hẹn với bác sĩ {} của {} vào lúc {} ngày {}. ^_^'.format(name, date_of_bird_display, PhoneNumber, doctor, speciality, time, date_display)
                    },
                    build_response_card(
                        'Bạn có chắc chắn muốn đặt lịch hẹn không?',
                        'Lựa chọn dành cho bạn',
                        options, 'https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcTyzsYL2jWkqRAexHhYrsFvoWnMMVdcwjeMdwf-0poUPi2-I6jd'))
            elif Confirmation == "Có":
                # lưu lịch hẹn
                try:
                    connection = psycopg2.connect(
                        "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                    #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
                    cursor = connection.cursor()
                    select_query = "SELECT * FROM appointment_schedule as a where a.doctor='{}' and a.speciality='{}' and a.patient_name ilike '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time));".format(doctor,speciality,name,DateOfBird,PhoneNumber)
                    cursor.execute(select_query)
                    count = cursor.rowcount
                    if count!=0:
                        return close2(
                            output_session_attributes,
                            'Fulfilled',
                            {
                                'contentType': 'PlainText',
                                'content': 'Đã có một lịch hẹn khác với bác sĩ {} của khoa {} được đặt cho bệnh nhân {} mà chưa tới ngày hẹn cho nên bạn không thể đặt hẹn mới. Nếu muốn đặt hẹn mới cho bệnh nhân này thì bạn vui lòng hủy lịch hẹn cũ.'.format(doctor,speciality,name)
                            })
                    postgres_insert_query = """ INSERT INTO appointment_schedule (doctor, speciality, date, time, patient_name,date_of_birth,phone_number,psid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
                    record_to_insert = (
                        doctor, speciality, date, time, name, DateOfBird, PhoneNumber, psid)
                    cursor.execute(postgres_insert_query, record_to_insert)
                    connection.commit()
                    count = cursor.rowcount
                    if count == 0:
                        return close2(
                            output_session_attributes,
                            'Fulfilled',
                            {
                                'contentType': 'PlainText',
                                'content': 'Thêm lịch hẹn thất bại. Bạn có thể tham khảo các dịch vụ hỗ trợ khác của chat bot.'
                            }
                        )
                    print(count, "Record inserted successfully into mobile table")

                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL", error)
                finally:
                    # closing database connection.
                    if(connection):
                        cursor.close()
                        connection.close()
                        print("PostgreSQL connection is closed")
                return delegate(
                    output_session_attributes,
                    slots
                )
            elif Confirmation == "Không":
                # không lưu lịch hẹn
                if UpdateInfor=='Không':
                    return close2(
                        output_session_attributes,
                        'Fulfilled',
                        {
                            'contentType': 'PlainText',
                            'content': 'Thông tin lịch hẹn của bạn không được lưu. Bạn có thể tham khảo các dịch vụ hỗ  trợ khác của chat bot.'
                        }
                    )
                elif UpdateInfor=="Có":
                    slots['Name'] = None
                    slots['DateOfBird'] = None
                    slots['PhoneNumber'] = None
                    slots['Confirmation']=None
                    slots['UpdateInfor']=None
                    options = build_options('name', speciality, doctor, date, time, psid)
                    if len(options) > 1:
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'Name', {
                                'contentType': 'PlainText',
                                'content': 'Cho mình xin TÊN của bệnh nhân ạ?'
                            },
                            build_response_card(
                                'Danh sách các bệnh nhân đã được đặt lịch hẹn bằng tài khoản Facebook này',
                                'Mời bạn chọn tên bệnh nhân',
                                options, None))
                    else:
                        return delegate(output_session_attributes, slots) 
                else:
                    options = build_options('UpdateInfor', None, None, None, None, None)
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'UpdateInfor', {
                            'contentType': 'PlainText',
                            'content': 'Bạn có muốn thay đổi thông tin bệnh nhân vừa nhập không ạ?'
                        }, build_response_card(
                        'Thay đổi thông tin bệnh nhận hoặc không đặt hẹn nữa',
                        'Lựa chọn dành cho bạn',
                        options, 'https://is1-ssl.mzstatic.com/image/thumb/Purple118/v4/d6/d3/c5/d6d3c5f5-681e-47ef-b5a9-7684ebb2609f/source/512x512bb.jpg'))
        return delegate(output_session_attributes, slots)
    arr_date = date.split('-')
    date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
    arr_date_of_bird = DateOfBird.split('-')
    date_of_bird_display = arr_date_of_bird[2] + \
        '/'+arr_date_of_bird[1]+'/'+arr_date_of_bird[0]
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thông tin chi tiết của bạn như sau: Bệnh nhân {} sinh ngày {} có số điện thoại {} có lịch hẹn với bác sĩ {} của {} vào lúc {} ngày {}'.format(name, date_of_bird_display, PhoneNumber, doctor, speciality, time, date_display)
        }
    )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(
        intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'VietnameseMakeAppointment'or intent_name == 'VietnameseUpdateAppointment':
        return make_appointment(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    # Asia/Jakarta
    os.environ['TZ'] = 'Asia/Jakarta'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)


#make_appointment(xxx)
# SELECT * FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name='Dr Do Thanh Long' and ms.name='Cardiology'
