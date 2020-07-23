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
import urllib3
# import requests
# from botocore.vendored import requests


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
# conn = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")


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
        "name": "VietnameseUpdateAppointment",
        "slots": {
             "AccountFBMakeAppointment": "Tài khoản này",
    "Appointment": "Lê Trọng Phát",
    "ChangeType": None,
    "Confirmation": None,
    "Date": None,
    "DateOfBird": None,
    "Doctor": None,
    "Name": None,
    "PhoneNumber": None,
    "Speciality": None,
    "Time": None
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
                        "imageUrl": "https://article.images.consumerreports.org/f_auto/prod/content/dam/CRO%20Images%202018/Health/May/CR-Health-InlineHero-C-Section-Risk-Hospital-05-18",
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
                        "imageUrl": "https://article.images.consumerreports.org/f_auto/prod/content/dam/CRO%20Images%202018/Health/May/CR-Health-InlineHero-C-Section-Risk-Hospital-05-18",
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


def build_response_card(title, subtitle, options):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    genericAttachments = []
    if options is not None:
        buttons = []
        genericAttachmentElement = {}
        cnt = 0
        for i in range(len(options)):
            buttons.append(options[i])
            cnt = cnt+1
            if cnt == 3 or i == len(options)-1:
                genericAttachmentElement = {
                    'title': title,
                    'subTitle': subtitle,
                    'buttons': buttons
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


def build_options(slot, speciality, doctor, date, time, psid, name, DateOfBird, PhoneNumber):
    """
    Build a list of potential options for a given slot, to be used in responseCard generation.
    """
    day_strings = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    if slot == "AccountFBMakeAppointment":
        temp1 = {
            'text': "Tài khoản này",
            'value': "Tài khoản này"}
        temp2 = {
            'text': "Tài khoản khác",
            'value': "Tài khoản khác"
        }
        res = []
        res.append(temp1)
        res.append(temp2)
        return res
    elif slot == 'Speciality':
        try:
            connection = psycopg2.connect(
                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
            # connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT * FROM medical_specialities;")
            records = cursor.fetchall()
            # cnt=0
            # print("Records of books in the table")
            # for row in records:
            #     print("\nid = ", row[0])
            #     print("name = ", row[1])
            #     print("image = ", row[2])
            #     print("languge = ", row[3])
            #     print("rank = ", row[4], "\n")
            # cnt=cnt+1
            # print(cnt)

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
            # connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

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
            # connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            # print ("hi", connection.get_dsn_parameters(),"\n")
            # print("khoa:%s"%speciality)
            # print("bacsi:%s"%doctor)

            # Print PostgreSQL version
            cursor.execute("SELECT distinct wh.day FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name ILIKE '%{}%' and ms.name ILIKE '%{}%';".format(doctor, speciality))
            records = cursor.fetchall()
            if len(records) == 0:
                return None
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            # closing database connection.
            if(connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
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
        # potential_date.strftime('%A, %B %d, %Y')
        while len(options) < 30:
            potential_date = potential_date + datetime.timedelta(days=1)
            # print(potential_date.weekday())
            if dict_date[day_strings[potential_date.weekday()]] == True:
                options.append({'text': '{}-{} ({})'.format(potential_date.day, potential_date.month, day_strings[potential_date.weekday()]),
                                'value': potential_date.strftime('%Y-%d-%m')})  # value chỉnh từ format %Y-%m-d sang %Y-%d-%m cho trùng với định dạng người dùng nhập vào
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
                    #print('time begin update: %s' % time_begin)
                # print('***************************************')
            # print('end')
            for x in value_time:
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
    elif slot == 'Appointment':
        try:
            connection = psycopg2.connect(
                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
            # connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            if name and DateOfBird and PhoneNumber:
                query="SELECT a.doctor, a.date FROM appointment_schedule as a WHERE a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and a.date>=now()".format(name, DateOfBird, PhoneNumber)
            else:
                query="SELECT a.doctor, a.date FROM appointment_schedule as a WHERE a.psid='{}' and a.date>=now()".format(psid)
            if speciality:
                query=query+" and speciality='{}';".format(speciality)
            else:
                query=query+";"
            cursor.execute(query)
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
        set_doctor = set()
        if len(records) == 0:
            return None
        for row in records:
            # str_value=row[1]+', '+row[4].strftime("%H:%M")+', '+row[3].strftime("%d/%m/%Y")
            str_value = row[0]
            date_of_appointment = row[1]
            if date_of_appointment >= datetime.date.today():
                set_doctor.add(str_value)
        for i in set_doctor:
            temp = ({
                    'text': i,
                    'value': i})
            res.append(temp)
        temp = ({
                'text': 'Khác',
                'value': 'Khác'})
        res.append(temp)
        return res
    elif slot == 'ChangeType':
        res = [{'text': 'Bác sĩ', 'value': 'Bác sĩ'}, {
            'text': 'Ngày', 'value': 'Ngày'}, {'text': 'Giờ', 'value': 'Giờ'}]
        return res


""" --- Functions that control the bot's behavior --- """


def update_appointment(intent_request):
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
    AccountFBMakeAppointment = intent_request['currentIntent']['slots']['AccountFBMakeAppointment']
    Appointment = intent_request['currentIntent']['slots']['Appointment']
    ChangeType = intent_request['currentIntent']['slots']['ChangeType']
    speciality = intent_request['currentIntent']['slots']['Speciality']
    doctor = intent_request['currentIntent']['slots']['Doctor']
    time = intent_request['currentIntent']['slots']['Time']
    date = intent_request['currentIntent']['slots']['Date']
    name = intent_request['currentIntent']['slots']['Name']
    DateOfBird = intent_request['currentIntent']['slots']['DateOfBird']
    PhoneNumber = intent_request['currentIntent']['slots']['PhoneNumber']
    Confirmation = intent_request['currentIntent']['slots']['Confirmation']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request[
        'sessionAttributes'] if intent_request[
            'sessionAttributes'] is not None else {}
    psid = "2768186586569088"
    # psid="2872158819534978"
    try:
        psid = intent_request['requestAttributes']['x-amz-lex:user-id']
    except Exception as error:
        print("get psid error", error)
    finally:
        print("get psid final")
    print("psid type:", type(psid))
    # # api-endpoint
    # ,profile_pic,locale,timezone,gender
    URL = "https://graph.facebook.com/{}?fields=name,first_name,last_name&access_token=EAACtffPGBe4BAGvNefOdwJDnB8s2wZAQgNlEBJZCfxgbdZC8ktRuB3NGTIPBR47QDc5KDwa9w3osAbZAnpWQNQneMr4v4SbBauZAjgx06x1xZCZA2dSPFV1rBa1dhnkRcrSM8sgKL5ZAtM20Ww3mnD11jWYweE41x5a8HjkDISWyUFF2TyzhORj5".format(
        psid)
    # r = requests.get(url = URL)
    # data = r.json()
    ###
    http = urllib3.PoolManager()
    r = http.request('GET', URL)
    # data=r.data
    data = json.loads(r.data.decode('utf-8'))

    print(data)
    # extracting latitude, longitude and formatted address
    # of the first matching location
    # latitude = data['results'][0]['geometry']['location']['lat']
    # longitude = data['results'][0]['geometry']['location']['lng']
    # formatted_address = data['results'][0]['formatted_address']
    fb_name = data['name']
    fb_first_name = data['first_name']
    fb_last_name = data['last_name']
    print('name= ', fb_name)

    # # printing the output
    # print("Latitude:%s\nLongitude:%s\nFormatted Address:%s"%(latitude, longitude,formatted_address))

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['currentIntent']['slots']
        # validation_result = validate_book_appointment(appointment_type, date, appointment_time)
        # if not validation_result['isValid']:
        #     slots[validation_result['violatedSlot']] = None
        #     return elicit_slot(
        #         output_session_attributes,
        #         intent_request['currentIntent']['name'],
        #         slots,
        #         validation_result['violatedSlot'],
        #         validation_result['message'],
        #         build_response_card(
        #             'Specify {}'.format(validation_result['violatedSlot']),
        #             validation_result['message']['content'],
        #             build_options(validation_result['violatedSlot'], appointment_type, date, booking_map)
        #         )
        #     )
        # https://graph.facebook.com/2768186586569088?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token=EAACtffPGBe4BAGvNefOdwJDnB8s2wZAQgNlEBJZCfxgbdZC8ktRuB3NGTIPBR47QDc5KDwa9w3osAbZAnpWQNQneMr4v4SbBauZAjgx06x1xZCZA2dSPFV1rBa1dhnkRcrSM8sgKL5ZAtM20Ww3mnD11jWYweE41x5a8HjkDISWyUFF2TyzhORj5
        # if Appointment and (not name or not DateOfBird or not PhoneNumber):
        #     return delegate(output_session_attributes, slots)
        if AccountFBMakeAppointment==None:
                AccountFBMakeAppointment = "Tài khoản này"
                slots['AccountFBMakeAppointment'] = "Tài khoản này"
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
                            'content': 'Xin lỗi nhưng bạn cần chọn giờ khám bệnh là giờ tròn ví dụ như {}:{} hoặc {}:{}. Bạn muốn hẹn bác sĩ lúc mấy giờ ạ? ;)'.format(hour, '00', hour, '30')
                        }, None)
                elif minute > 30:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Time', {
                            'contentType': 'PlainText',
                            'content': 'Xin lỗi nhưng bạn cần chọn giờ khám bệnh là giờ tròn ví dụ như {}:{} hoặc {}:{}. Bạn muốn hẹn bác sĩ lúc mấy giờ ạ? ;)'.format(hour, '30', hour+1, '00')
                        }, None)
        if not Appointment:
            if AccountFBMakeAppointment==None:
                AccountFBMakeAppointment = "Tài khoản này"
                slots['AccountFBMakeAppointment'] = "Tài khoản này"
            if speciality:
                #làm gì đó
                try:
                    connection = psycopg2.connect(
                        "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                    cursor = connection.cursor()
                    if name and DateOfBird and PhoneNumber:
                        query = """Select DISTINCT doctor From appointment_schedule where patient_name ILIKE '%{}' and date_of_birth='{}' and phone_number='{}' and speciality='{}' and date>=now()""".format(
                            name, DateOfBird, PhoneNumber, speciality)
                        cursor.execute(query)
                    else: 
                        query = """Select DISTINCT doctor From appointment_schedule where psid='{}' and speciality='{}' and date>=now()""".format(
                            psid, speciality)
                        cursor.execute(query)
                    records = cursor.fetchall()
                    if cursor.rowcount<1:
                        if name and DateOfBird and PhoneNumber:
                            slots['Name'] = None
                            slots['DateOfBird'] = None
                            slots['PhoneNumber'] = None
                            slots['Speciality'] = None
                            return elicit_slot(
                                output_session_attributes,
                                intent_request['currentIntent']['name'],
                                slots,
                                'Name',
                                {
                                    'contentType': 'PlainText',
                                    'content': 'Bệnh nhân {} với số điện thoại {} không có lịch hẹn với khoa {}. Bạn cần thay đổi lịch hẹn cho bệnh nhân nào ạ?'.format(name,DateOfBird,speciality)
                                },
                                None)
                        else:
                            slots['AccountFBMakeAppointment'] = "Tài khoản khác"
                        return delegate(output_session_attributes, slots)
                except (Exception, psycopg2.Error) as error:
                    print("Error while connecting to PostgreSQL", error)
                finally:
                    if(connection):
                        cursor.close()
                        connection.close()
                        print("PostgreSQL connection is closed")
            if AccountFBMakeAppointment == "Tài khoản này":
                if build_options('Appointment', None, None, None, None, psid, None, None, None) == None:
                    slots['AccountFBMakeAppointment'] = "Tài khoản khác"
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots,
                        'Name',
                        {
                            'contentType': 'PlainText',
                            'content': 'Vì trước đây bạn chưa từng đặt hẹn bằng tài khoản này nên tôi cần thêm thông tin của bệnh nhân. Cho tôi xin họ và tên của bệnh nhân ạ?'
                        },
                        None)
                else:
                    options=build_options('Appointment', speciality, None, None, None, psid, None, None, None)
                    if len(options)==2:
                        slots['Appointment']=options[0]['value']
                        Appointment=options[0]['value']
                        try:
                            connection = psycopg2.connect(
                                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                            cursor = connection.cursor()
                            query = """Select patient_name,date_of_birth,phone_number From appointment_schedule where doctor = '{}' and psid='{}' and speciality='{}' and date>=now()""".format(
                                    Appointment, psid,speciality)
                            cursor.execute(query)
                            records = cursor.fetchall()
                            slots['Name'] = records[0][0]
                            slots['DateOfBird'] = records[0][1].strftime('%Y-%m-%d')
                            slots['PhoneNumber'] = records[0][2]
                        except (Exception, psycopg2.Error) as error:
                            print("Error while connecting to PostgreSQL", error)
                        finally:
                            if(connection):
                                cursor.close()
                                connection.close()
                                print("PostgreSQL connection is closed")
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'ChangeType', {
                                'contentType': 'PlainText',
                                'content': 'Dạ, bạn muốn cập nhật thông tin nào cho lịch hẹn với bác sĩ {} vậy? <3'.format(Appointment)
                            },
                            build_response_card(
                                'Danh mục muốn thay đổi:',
                                'Mời bạn chọn thông tin cần thay đổi',
                                build_options('ChangeType', None, None, None, None, psid, None, None, None)))
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Appointment', {
                            'contentType': 'PlainText',
                            'content': 'Đây là các lịch được đặt bởi tài khoản facebook này. Không biết bạn muốn thay đổi lịch hẹn với bác sĩ nào ạ?'
                        },
                        build_response_card(
                            'Bạn có các lịch hẹn với các bác sĩ sau đây',
                            'Mời bạn chọn lịch hẹn muốn được cập nhật',
                            options))
            if AccountFBMakeAppointment == "Tài khoản khác":
                if not name:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots,
                        'Name',
                        {
                            'contentType': 'PlainText',
                            'content': 'Họ và tên của bệnh nhân là gì ạ?'
                        },
                        None)
                if not DateOfBird:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots,
                        'DateOfBird',
                        {
                            'contentType': 'PlainText',
                            'content': 'Bệnh nhân {} sinh ngày bao nhiêu ạ?'.format(name)
                        },
                        None)
                if not PhoneNumber:
                    # modify format for date input from user become date dd/mm/yyyy->yyyy/mm/dd
                    print(intent_request['currentIntent']['slots'])
                    arr_date = DateOfBird.split('-')
                    if int(arr_date[2]) < 13:
                        arr_date[1], arr_date[2] = arr_date[2], arr_date[1]
                    DateOfBird = arr_date[0]+'-'+arr_date[1]+'-'+arr_date[2]
                    slots['DateOfBird'] = DateOfBird
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'PhoneNumber', {
                            'contentType': 'PlainText',
                            'content': 'Số điện thoại đã đặt lịch hẹn là gì ạ?'
                        }, None)
                if build_options('Appointment', None, None, None, None, psid, name, DateOfBird, PhoneNumber) == None:
                    name_temp = name
                    DateOfBird_temp = DateOfBird
                    PhoneNumber_temp = PhoneNumber
                    slots['Name'] = None
                    slots['DateOfBird'] = None
                    slots['PhoneNumber'] = None
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots,
                        'Name',
                        {
                            'contentType': 'PlainText',
                            'content': 'Bệnh nhân {} sinh ngày {} có số điện thoại {} không có lịch hẹn nào cả. Mời bạn nhập lại thông tin. Họ tên bệnh nhân là gì?.'.format(name, DateOfBird, PhoneNumber)
                        },
                        None)
                else:
                    options = build_options('Appointment', speciality, None, None, None, psid, name, DateOfBird, PhoneNumber)
                    if(len(options)==2):
                        slots['Appointment']=options[0]['value']
                        Appointment=options[0]['value']
                        try:
                            connection = psycopg2.connect(
                                "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                            cursor = connection.cursor()
                            query = """Select patient_name,date_of_birth,phone_number From appointment_schedule where doctor = '{}' and psid='{}' and speciality='{}' and date>=now()""".format(
                                    Appointment, psid,speciality)
                            cursor.execute(query)
                            records = cursor.fetchall()
                            slots['Name'] = records[0][0]
                            slots['DateOfBird'] = records[0][1].strftime('%Y-%m-%d')
                            slots['PhoneNumber'] = records[0][2]
                        except (Exception, psycopg2.Error) as error:
                            print("Error while connecting to PostgreSQL", error)
                        finally:
                            if(connection):
                                cursor.close()
                                connection.close()
                                print("PostgreSQL connection is closed")
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'ChangeType', {
                                'contentType': 'PlainText',
                                'content': 'Dạ, bạn muốn cập nhật thông tin nào cho lịch hẹn với bác sĩ {} vậy? <3'.format(Appointment)
                            },
                            build_response_card(
                                'Danh mục muốn thay đổi:',
                                'Mời bạn chọn thông tin cần thay đổi',
                                build_options('ChangeType', None, None, None, None, psid, None, None, None)))
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Appointment', {
                            'contentType': 'PlainText',
                            'content': 'Bây giờ bạn cần thay đổi lịch hẹn với bác sĩ nào ạ?'
                        },
                        build_response_card(
                            'Bệnh nhân {} có lịch hẹn với các bác sĩ sau:'.format(
                                name),
                            'Mời bạn chọn lịch hẹn muốn được cập nhật',
                            options))
        elif Appointment=='Khác':
            slots['AccountFBMakeAppointment'] = "Tài khoản khác"
            slots['Name'] = None
            slots['DateOfBird'] = None
            slots['PhoneNumber'] = None
            slots['Appointment'] = None
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                'Name',
                {
                    'contentType': 'PlainText',
                    'content': 'Để cập nhật lịch hẹn tôi cần được biết họ tên của bệnh nhân! <3'
                },
                None)
        # elif AccountFBMakeAppointment=="Tài khoản khác"and (not name or not DateOfBird or not PhoneNumber):
        #     if not name:
        #         return elicit_slot(
        #             output_session_attributes,
        #             intent_request['currentIntent']['name'],
        #             intent_request['currentIntent']['slots'],
        #             'Name',
        #             {
        #                 'contentType': 'PlainText',
        #                 'content': 'Tên của bệnh nhân là gì ạ?'
        #             },
        #             None)
        #     if not DateOfBird:
        #         return elicit_slot(
        #             output_session_attributes,
        #             intent_request['currentIntent']['name'],
        #             intent_request['currentIntent']['slots'],
        #             'DateOfBird',
        #             {
        #                 'contentType': 'PlainText',
        #                 'content': 'Tôi cần biết ngày sinh của bệnh nhân'
        #             },
        #             None)
        #     if not PhoneNumber:
        #         return elicit_slot(
        #             output_session_attributes,
        #             intent_request['currentIntent']['name'],
        #             intent_request['currentIntent']['slots'],
        #             'PhoneNumber',
        #             {
        #                 'contentType': 'PlainText',
        #                 'content': 'Cho tôi xin số điện thoại đã đặt lịch hẹn.'
        #             },
        #             None)
        elif not ChangeType:
            try:
                connection = psycopg2.connect(
                    "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                cursor = connection.cursor()
                if name and DateOfBird and PhoneNumber:
                    cursor.execute(
                        "SELECT a.patient_name, a.date_of_birth, a.phone_number FROM appointment_schedule as a WHERE a.doctor = '{}' and a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and a.date>=now();".format(Appointment, name, DateOfBird, PhoneNumber))
                else:
                    cursor.execute(
                        "SELECT a.patient_name, a.date_of_birth, a.phone_number FROM appointment_schedule as a WHERE a.doctor = '{}' and a.psid='{}' and a.date>=now();".format(Appointment,psid))
                records = cursor.fetchall()
                if cursor.rowcount<1:
                    slots['Appointment']=None
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Appointment', {
                            'contentType': 'PlainText',
                            'content': 'Mình muốn biết bạn cần thay đổi lịch hẹn với bác sĩ nào ạ?'
                        },
                        build_response_card(
                            'Hiện tại có các lịch hẹn với các bác sĩ sau:',
                            'Mời bạn chọn lịch hẹn muốn được cập nhật',
                            build_options('Appointment', None, None, None, None, psid, name, DateOfBird, PhoneNumber)))
                if cursor.rowcount==1:
                    slots['Name'] = records[0][0]
                    slots['DateOfBird'] = records[0][1].strftime('%Y-%m-%d')
                    slots['PhoneNumber'] = records[0][2]
                elif cursor.rowcount>1:
                    if not name:
                        slots['Name'] = None
                        slots['DateOfBird'] = None
                        slots['PhoneNumber'] = None
                        slots['AccountFBMakeAppointment'] = "Tài khoản khác"
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots,
                            'Name',
                            {
                                'contentType': 'PlainText',
                                'content': 'Tài khoản này đã đặt nhiều lịch hẹn với bác sĩ {}, để cập nhật chính xác lịch hẹn, mình cần biết họ tên của bệnh nhân?'.format(Appointment)
                            },
                            None)
                    elif not DateOfBird:
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots,
                            'DateOfBird',
                            {
                                'contentType': 'PlainText',
                                'content': 'Bệnh nhân {} sinh ngày bao nhiêu ạ?'.format(name)
                            },
                            None)
                    elif not PhoneNumber:
                        # modify format for date input from user become date dd/mm/yyyy->yyyy/mm/dd
                        print(intent_request['currentIntent']['slots'])
                        arr_date = DateOfBird.split('-')
                        if int(arr_date[2]) < 13:
                            arr_date[1], arr_date[2] = arr_date[2], arr_date[1]
                        DateOfBird = arr_date[0]+'-'+arr_date[1]+'-'+arr_date[2]
                        slots['DateOfBird'] = DateOfBird
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'PhoneNumber', {
                                'contentType': 'PlainText',
                                'content': 'Số điện thoại đã đặt lịch hẹn là gì ạ?'
                            }, None)
                    cursor.execute(
                            "SELECT * FROM appointment_schedule as a WHERE a.doctor = '{}' and a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and a.date>=now();".format(Appointment,name,DateOfBird,PhoneNumber))
                    records = cursor.fetchall()
                    if cursor.rowcount==0:
                        name_temp = name
                        DateOfBird_temp = DateOfBird
                        PhoneNumber_temp = PhoneNumber
                        slots['Name'] = None
                        slots['DateOfBird'] = None
                        slots['PhoneNumber'] = None
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots,
                            'Name',
                            {
                                'contentType': 'PlainText',
                                'content': 'Bệnh nhân {} sinh ngày {} có số điện thoại {} không có lịch hẹn với bác sĩ {}. Mời bạn nhập lại thông tin. Họ tên bệnh nhân là gì?.'.format(name, DateOfBird, PhoneNumber,Appointment)
                            },
                            None)
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL", error)
            finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                slots, 'ChangeType', {
                    'contentType': 'PlainText',
                    'content': 'Dạ, bạn muốn cập nhật thông tin nào cho lịch hẹn với bác sĩ {} vậy? <3'.format(Appointment)
                },
                build_response_card(
                    'Danh mục muốn thay đổi:',
                    'Mời bạn chọn thông tin cần thay đổi',
                    build_options('ChangeType', None, None, None, None, psid, None, None, None)))
        elif not doctor and not date and not time:
            records = []
            try:
                connection = psycopg2.connect(
                    "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                # connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")
                cursor = connection.cursor()
                if name and DateOfBird and PhoneNumber: #dữ liệu đúng trong thực tế thì chỉ có 1 dòng dữ liệu duy nhất
                    query = """Select speciality,doctor,date,time,patient_name,date_of_birth,phone_number From appointment_schedule where doctor = '{}' and patient_name ILIKE '%{}' and date_of_birth='{}' and phone_number='{}' and date>=now() ORDER BY date""".format(
                        Appointment, name, DateOfBird, PhoneNumber)
                    cursor.execute(query)
                    records = cursor.fetchall()
                else: #luôn luôn chỉ có 1 dòng dữ liệu duy nhất
                    query = """Select speciality,doctor,date,time, patient_name,date_of_birth,phone_number From appointment_schedule where doctor = '{}' and psid='{}' and date>=now() ORDER BY date""".format(
                        Appointment, psid)
                    cursor.execute(query)
                    records = cursor.fetchall()
                    slots['Name'] = records[0][4]
                    slots['DateOfBird'] = records[0][5].strftime('%Y-%m-%d')
                    slots['PhoneNumber'] = records[0][6]    
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL", error)
            finally:
                # closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")
            if ChangeType == 'Bác sĩ':
                slots['Speciality'] = records[0][0]
                speciality = records[0][0]
            elif ChangeType == 'Ngày':
                slots['Speciality'] = records[0][0]
                slots['Doctor'] = records[0][1]
                speciality = records[0][0]
                doctor = records[0][1]
            elif ChangeType == 'Giờ':
                slots['Speciality'] = records[0][0]
                slots['Doctor'] = records[0][1]
                slots['Date'] = records[0][2].strftime('%Y-%m-%d')
                speciality = records[0][0]
                doctor = records[0][1]
                date = records[0][2].strftime('%Y-%m-%d')
        if not doctor:
            if build_options('Doctor', speciality, None, None, None, psid, None, None, None) == None:
                slots['Speciality'] = None
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Speciality', {
                        'contentType': 'PlainText',
                        'content': 'Bạn có thể cho tôi biết bạn muốn tới khoa nào khám bệnh không? <3'
                    },
                    build_response_card(
                        'Cập nhật lịch hẹn',
                        'Mời bạn chọn khoa mình muốn khám',
                        build_options('Speciality', None, None, None, None, psid, None, None, None)))
            else:
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Doctor', {
                        'contentType': 'PlainText',
                        'content': 'Bạn muốn tôi lấy lịch cho bạn với bác sĩ nào ạ? :D'
                    },
                    build_response_card(
                        'Cập nhật lịch hẹn',
                        'Mời bạn chọn bác sĩ của {}'.format(speciality),
                        build_options('Doctor', speciality, None, None, None, psid, None, None, None)))
        # có bác sĩ
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
                        message = 'Bệnh viện chúng tôi có nhiều bác sĩ tên {}, bạn muốn khám với bác sĩ nào ạ?'.format(
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
                                build_options('Doctor', speciality, doctor, date, time, None, None, None, None)))
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
                                    'content': 'Có nhiều khoa có bác sĩ tên {}, bạn muốn khám với khoa nào ạ?'.format(doctor)
                                },
                                build_response_card(
                                    'Các khoa có bác sĩ tên {}'.format(doctor),
                                    'Mời bạn chọn khoa',
                                    build_options('Speciality', speciality, doctor, date, time, None, None, None, None)))
                    except (Exception, psycopg2.Error) as error:
                        print("Error while connecting to PostgreSQL", error)
                    finally:
                        # closing database connection.
                        if(connection):
                            cursor.close()
                            connection.close()
                            print("PostgreSQL connection is closed")
        if not date:
            if build_options('Date', speciality, doctor, None, None, psid, None, None, None) == None:
                slots['Doctor'] = None
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Doctor', {
                        'contentType': 'PlainText',
                        'content': 'Bây giờ hãy chọn bác sĩ mà bạn muốn hẹn'
                    },
                    build_response_card(
                        'Cập nhật lịch hẹn',
                        'Mời bạn chọn bác sĩ',
                        build_options('Doctor', speciality, None, None, None, psid, None, None, None)))
            else:
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Date',
                    {
                        'contentType': 'PlainText',
                        'content': 'Dạ! Bạn có thể gặp bác sĩ {} vào ngày nào ạ? ^_^'.format(doctor)
                    },
                    build_response_card(
                        'Cập nhật lịch hẹn',
                        'Mời bạn chọn ngày khám bệnh',
                        build_options('Date', speciality, doctor, None, None, psid, None, None, None)))
        elif not time:
            print(slots)
            arr_date = date.split('-')
            if ChangeType != "Giờ":
                # modify format for date input from user become date dd/mm/yyyy->yyyy/mm/dd
                if int(arr_date[2]) < 13:
                    arr_date[1], arr_date[2] = arr_date[2], arr_date[1]
                date = arr_date[0]+'-'+arr_date[1]+'-'+arr_date[2]
                today = datetime.date.today()
                # fix bug loi format 4/5/2020->4/5/2021
                if int(arr_date[0]) == today.year+1:
                    print(today.year+1)
                    if today.month < int(arr_date[1]) or (today.month == int(arr_date[1]) and today.day < int(arr_date[2])):
                        arr_date[0] = str(today.year)
                date = arr_date[0]+'-'+arr_date[1]+'-'+arr_date[2]

            date_display = arr_date[2]+'/'+arr_date[1]+'/'+arr_date[0]
            slots['Date'] = date
            print("date nek", date)
            if build_options('Time', speciality, doctor, date, None, psid, None, None, None) == None:
                slots['Date'] = None
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Date', {
                        'contentType': 'PlainText',
                        'content': 'Tôi cần biết bạn muốn thay đổi lịch hẹn đến ngày nào? ;)'
                    },
                    build_response_card(
                        'Cập nhật lịch hẹn',
                        'Mời bạn chọn ngày khám bệnh',
                        build_options('Date', speciality, doctor, None, None, psid, None, None, None)))
            else:
                return elicit_slot(
                    output_session_attributes,
                    intent_request['currentIntent']['name'],
                    slots, 'Time', {
                        'contentType': 'PlainText',
                        'content': 'Bạn có thể gặp bác sĩ {} vào lúc nào trong ngày {} ^_^'.format(Appointment ,date_display)
                    },
                    build_response_card(
                        'Cập nhật lịch hẹn',
                        'Mời bạn chọn thời gian hẹn bác sĩ',
                        build_options('Time', speciality, doctor, date, None, psid, None, None, None)))
        elif Confirmation == "Có":
            try:
                connection = psycopg2.connect(
                    "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                # connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

                cursor = connection.cursor()
                sql_update_query = """Update appointment_schedule set doctor = '{}' , speciality='{}' , date='{}', time='{}' where doctor = '{}' and patient_name ILIKE '%{}' and date_of_birth='{}' and phone_number='{}' and date >= now()""".format(
                        doctor, speciality, date, time, Appointment, name, DateOfBird, PhoneNumber)
                cursor.execute(sql_update_query)
                # sql_update_query = """Update appointment_schedule set date=%s , time=%s where patient_name = %s and date_of_birth=%s and phone_number=%s"""
                # cursor.execute(sql_update_query, (date,time,name,DateOfBird,PhoneNumber))
                connection.commit()
                count = cursor.rowcount

                if count == 0:
                    return close2(
                        output_session_attributes,
                        'Fulfilled',
                        {
                            'contentType': 'PlainText',
                            'content': '<3 Thông tin lịch hẹn trên không tồn tại. Cập nhật lịch hẹn thất bại. Bạn có thể tham khảo các dịch vụ hỗ  trợ khác của chat bot.'
                        }
                    )
                print(count, "Record Updated successfully ")
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
            return close2(
                output_session_attributes,
                'Fulfilled',
                {
                    'contentType': 'PlainText',
                    'content': 'Cập nhật lịch hẹn thất bại. Bạn có thể tham khảo các dịch vụ hỗ trợ khác của chat bot. O:) '
                }
            )
        # if appointment_type and not date:
        #     return elicit_slot(
        #         output_session_attributes,
        #         intent_request['currentIntent']['name'],
        #         intent_request['currentIntent']['slots'],
        #         'Date',
        #         {'contentType': 'PlainText', 'content': 'When would you like to schedule your {}?'.format(appointment_type)},
        #         build_response_card(
        #             'Specify Date',
        #             'When would you like to schedule your {}?'.format(appointment_type),
        #             build_options('Date', appointment_type, date, None)
        #         )
        #     )

        # if appointment_type and date:
        #     # Fetch or generate the availabilities for the given date.
        #     booking_availabilities = try_ex(lambda: booking_map[date])
        #     if booking_availabilities is None:
        #         booking_availabilities = get_availabilities(date)
        #         booking_map[date] = booking_availabilities
        #         output_session_attributes['bookingMap'] = json.dumps(booking_map)

        #     appointment_type_availabilities = get_availabilities_for_duration(get_duration(appointment_type), booking_availabilities)
        #     if len(appointment_type_availabilities) == 0:
        #         # No availability on this day at all; ask for a new date and time.
        #         slots['Date'] = None
        #         slots['Time'] = None
        #         return elicit_slot(
        #             output_session_attributes,
        #             intent_request['currentIntent']['name'],
        #             slots,
        #             'Date',
        #             {'contentType': 'PlainText', 'content': 'We do not have any availability on that date, is there another day which works for you?'},
        #             build_response_card(
        #                 'Specify Date',
        #                 'What day works best for you?',
        #                 build_options('Date', appointment_type, date, booking_map)
        #             )
        #         )

        #     message_content = 'What time on {} works for you? '.format(date)
        #     if appointment_time:
        #         output_session_attributes['formattedTime'] = build_time_output_string(appointment_time)
        #         # Validate that proposed time for the appointment can be booked by first fetching the availabilities for the given day.  To
        #         # give consistent behavior in the sample, this is stored in sessionAttributes after the first lookup.
        #         if is_available(appointment_time, get_duration(appointment_type), booking_availabilities):
        #             return delegate(output_session_attributes, slots)
        #         message_content = 'The time you requested is not available. '

        #     if len(appointment_type_availabilities) == 1:
        #         # If there is only one availability on the given date, try to confirm it.
        #         slots['Time'] = appointment_type_availabilities[0]
        #         return confirm_intent(
        #             output_session_attributes,
        #             intent_request['currentIntent']['name'],
        #             slots,
        #             {
        #                 'contentType': 'PlainText',
        #                 'content': '{}{} is our only availability, does that work for you?'.format
        #                            (message_content, build_time_output_string(appointment_type_availabilities[0]))
        #             },
        #             build_response_card(
        #                 'Confirm Appointment',
        #                 'Is {} on {} okay?'.format(build_time_output_string(appointment_type_availabilities[0]), date),
        #                 [{'text': 'yes', 'value': 'yes'}, {'text': 'no', 'value': 'no'}]
        #             )
        #         )

        #     available_time_string = build_available_time_string(appointment_type_availabilities)
        #     return elicit_slot(
        #         output_session_attributes,
        #         intent_request['currentIntent']['name'],
        #         slots,
        #         'Time',
        #         {'contentType': 'PlainText', 'content': '{}{}'.format(message_content, available_time_string)},
        #         build_response_card(
        #             'Specify Time',
        #             'What time works best for you?',
        #             build_options('Time', appointment_type, date, booking_map)
        #         )
        #     )

        return delegate(output_session_attributes, slots)

    # Book the appointment.  In a real bot, this would likely involve a call to a backend service.
    # duration = get_duration(appointment_type)
    # booking_availabilities = booking_map[date]
    # if booking_availabilities:
    #     # Remove the availability slot for the given date as it has now been booked.
    #     booking_availabilities.remove(appointment_time)
    #     if duration == 60:
    #         second_half_hour_time = increment_time_by_thirty_mins(appointment_time)
    #         booking_availabilities.remove(second_half_hour_time)

    #     booking_map[date] = booking_availabilities
    #     output_session_attributes['bookingMap'] = json.dumps(booking_map)
    # else:
    #     # This is not treated as an error as this code sample supports functionality either as fulfillment or dialog code hook.
    #     logger.debug('Availabilities for {} were null at fulfillment time.  '
    #                  'This should have been initialized if this function was configured as the dialog code hook'.format(date))

    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thông tin chi tiết của bạn như sau: Bệnh nhân {} sinh ngày {} có số điện thoại {} có lịch hẹn với bác sĩ {} của {} vào lúc {} ngày {}'.format(name, DateOfBird, PhoneNumber, doctor, speciality, time, date)
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
    if intent_name == 'VietnameseUpdateAppointment':
        return update_appointment(intent_request)

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


update_appointment(xxx)
# SELECT * FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name='Dr Do Thanh Long' and ms.name='Cardiology'
