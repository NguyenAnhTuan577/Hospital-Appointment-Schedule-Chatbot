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
        "name": "VietnameseCancelAppointment",
        "slots": {
            "AccountFBMakeAppointment": "Tài khoản khác",
            "Appointment": None,
            "Confirmation": None,
            "DateOfBird": None,
            "Name": None,
            "PhoneNumber": None
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
                        "imageUrl": "https://cms.luatvietnam.vn/uploaded/Images/Original/2018/08/28/benh-vien_2808175558.jpg",
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
                        "imageUrl": "https://cms.luatvietnam.vn/uploaded/Images/Original/2018/08/28/benh-vien_2808175558.jpg",
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
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

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
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute(
                "SELECT * FROM doctors as d,medical_specialities as ms WHERE ms.id=d.speciality_id and ms.name ILIKE '%{}%';".format(speciality))
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
        while len(options) < 30:
            potential_date = potential_date + datetime.timedelta(days=1)
            print(potential_date.weekday())
            day_strings_vn=['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ nhật']
            if dict_date[day_strings[potential_date.weekday()]] == True:
                options.append({'text': '{}-{} ({})'.format(potential_date.day, potential_date.month, day_strings_vn[potential_date.weekday()]),
                                'value': potential_date.strftime('%A, %B %d, %Y')})
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
            cursor.execute("SELECT wh.time FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name ILIKE '%{}%' and ms.name ILIKE '%{}%' and wh.day='{}'  order by wh.time;".format(
                doctor, speciality, date_weekday))

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
                print('time begin:---%s------' % time_begin)
                print('time end:----------%s----' % time_end)
                while compare_time(time_begin, time_end) < 0:
                    value_time.append(time_begin)
                    time_begin = increment_time_by_thirty_mins(time_begin)
                    print('time begin update: %s' % time_begin)

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
            #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            if name and DateOfBird and PhoneNumber:
                cursor.execute(
                    "SELECT distinct a.doctor,a.date, a.time FROM appointment_schedule as a WHERE a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time)) order by a.date, a.time;".format(name, DateOfBird, PhoneNumber))
                records = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT distinct a.doctor,a.date, a.time FROM appointment_schedule as a WHERE a.psid='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time)) order by a.date, a.time;".format(psid))
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
            str_value = row[0]
            if(str_value in set_doctor):
                continue
            set_doctor.add(str_value)
            temp = ({
                'text': str_value,
                'value': str_value})
            res.append(temp)
        temp = ({
                'text': 'Khác',
                'value': 'Khác'})
        res.append(temp)
        return res


""" --- Functions that control the bot's behavior --- """


def cancel_appointment(intent_request):
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
    # speciality = "Khoa"
    # doctor = "Bac si"
    # time = "Thoi Gian"
    # date = "Ngay"
    AccountFBMakeAppointment = intent_request['currentIntent']['slots']['AccountFBMakeAppointment']
    Appointment = intent_request['currentIntent']['slots']['Appointment']
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
    # ,profile_pic,locale,timezone,gender
    URL = "https://graph.facebook.com/{}?fields=name,first_name,last_name&access_token=EAACtffPGBe4BAGvNefOdwJDnB8s2wZAQgNlEBJZCfxgbdZC8ktRuB3NGTIPBR47QDc5KDwa9w3osAbZAnpWQNQneMr4v4SbBauZAjgx06x1xZCZA2dSPFV1rBa1dhnkRcrSM8sgKL5ZAtM20Ww3mnD11jWYweE41x5a8HjkDISWyUFF2TyzhORj5".format(
        psid)
    http = urllib3.PoolManager()
    r = http.request('GET', URL)
    data = json.loads(r.data.decode('utf-8'))
    print(data)
    fb_name = data['name']
    fb_first_name = data['first_name']
    fb_last_name = data['last_name']
    print('name= ', fb_name)
    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['currentIntent']['slots']
        if Appointment=='Kết thúc':
            return close2(
                output_session_attributes,
                'Fulfilled',
                {
                    'contentType': 'PlainText',
                    'content': 'Bạn có thể tham khảo thêm các hỗ trợ khác của chatbot ở đây:'
                })
        if not AccountFBMakeAppointment:
            AccountFBMakeAppointment = "Tài khoản này"
            slots['AccountFBMakeAppointment'] = "Tài khoản này"
            # return elicit_slot(
            #     output_session_attributes,
            #     intent_request['currentIntent']['name'],
            #     intent_request['currentIntent']['slots'],
            #     'AccountFBMakeAppointment',
            #     {
            #         'contentType': 'PlainText',
            #         'content': ':) Để hủy lịch hẹn tôi cần biết bạn đã đặt lịch hẹn đó bởi tài khoản facebook này hay tài khoản khác ạ?  ;)'
            #     },
            #     build_response_card(
            #         'Tài khoản Facebook đã dùng để đặt lịch',
            #         'Mời bạn chọn loại tài khoản',
            #         build_options('AccountFBMakeAppointment', None, None, None, None, psid, None, None, None)))
        if not Appointment:
            if AccountFBMakeAppointment == "Tài khoản này":
                options=build_options('Appointment', None, None, None, None, psid, None, None, None)
                if options==None:
                    slots['AccountFBMakeAppointment'] = "Tài khoản khác"
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots,
                        'Name',
                        {
                            'contentType': 'PlainText',
                            'content': 'Hiện tài khoản này chưa đặt lịch hẹn nào. Để hủy lịch hẹn tôi cần được biết HỌ VÀ TÊN của bệnh nhân?'
                        },
                        None)
                # elif len(options)==2:
                #     slots['Appointment']=options[0]['value']
                #     Appointment=options[0]['value']
                #     try:
                #         connection = psycopg2.connect(
                #             "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                #         cursor = connection.cursor()
                #         query = """Select patient_name,date_of_birth,phone_number From appointment_schedule where doctor = '{}' and psid='{}' and date+1>now()""".format(
                #                 Appointment, psid)
                #         cursor.execute(query)
                #         records = cursor.fetchall()
                #         slots['Name'] = records[0][0]
                #         slots['DateOfBird'] = records[0][1].strftime('%Y-%m-%d')
                #         slots['PhoneNumber'] = records[0][2]
                #     except (Exception, psycopg2.Error) as error:
                #         print("Error while connecting to PostgreSQL", error)
                #     finally:
                #         if(connection):
                #             cursor.close()
                #             connection.close()
                #             print("PostgreSQL connection is closed")
                #     return delegate(output_session_attributes, slots)
                else:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Appointment', {
                            'contentType': 'PlainText',
                            'content': 'Chào {}! Đây là các lịch được đặt bởi tài khoản facebook này. Không biết bạn muốn HỦY LỊCH HẸN với BÁC SĨ nào ạ? (Bạn cũng có thể hủy hẹn được đặt bởi tài khoản FB khác thông qua thông tin bệnh nhân)'.format(fb_first_name)
                        },
                        build_response_card(
                            'Bạn có các lịch hẹn với các bác sĩ sau đây',
                            'Mời bạn chọn lịch hẹn muốn hủy',
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
                            'content': 'Dạ, Họ tên của bệnh nhân là gì ạ?'
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
                            'content': 'Bây giờ tôi cần biết NGÀY THÁNG NĂM SINH của bệnh nhân?'
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
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'PhoneNumber', {
                            'contentType': 'PlainText',
                            'content': 'Bây giờ cho tôi xin số điện thoại đã đặt lịch hẹn? ^_^'
                        }, None)
                else:
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
                options=build_options('Appointment', None, None, None, None, psid, name, DateOfBird, PhoneNumber)
                if options==None:
                    slots['Name'] = None
                    slots['DateOfBird'] = None
                    slots['PhoneNumber'] = None
                    arr_date_of_bird = DateOfBird.split('-')
                    date_of_bird_display = arr_date_of_bird[2] + '/'+arr_date_of_bird[1]+'/'+arr_date_of_bird[0]
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots,
                        'Name',
                        {
                            'contentType': 'PlainText',
                            'content': 'Bệnh nhân {} sinh ngày {} có số điện thoại {} không có lịch hẹn nào cả. Mời bạn nhập lại thông tin. HỌ TÊN bệnh nhân là gì?. :)'.format(name, date_of_bird_display, PhoneNumber)
                        },
                        None)
                # elif  len(options)==2:
                #     slots['Appointment']=options[0]['value']
                #     Appointment=options[0]['value']
                #     return delegate(output_session_attributes, slots)
                else:
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Appointment', {
                            'contentType': 'PlainText',
                            'content': 'Cho tôi biết bạn muốn hủy lịch hẹn với bác sĩ nào ạ? ^_^'
                        },
                        build_response_card(
                            'Bệnh nhân {} có lịch hẹn với các bác sĩ sau:'.format(
                                name),
                            'Mời bạn chọn lịch hẹn muốn được hủy',
                            build_options('Appointment', None, None, None, None, psid, name, DateOfBird, PhoneNumber)))
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
                    'content': 'Tôi cần biết họ tên của bệnh nhân để hủy lịch hẹn? <3'
                },
                None)
        elif not Confirmation:
            if AccountFBMakeAppointment=='Tài khoản khác':
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
                                'content': 'Hãy cho tôi biết HỌ TÊN của bệnh nhân là gì ạ?'
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
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'PhoneNumber', {
                            'contentType': 'PlainText',
                            'content': 'Số điện thoại đã đặt lịch hẹn là gì ạ?'
                        }, None)
                else:
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
            try:
                connection = psycopg2.connect(
                    "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                cursor = connection.cursor()
                if name and DateOfBird and PhoneNumber:
                    cursor.execute(
                        "SELECT a.patient_name, a.date_of_birth, a.phone_number, a.doctor FROM appointment_schedule as a WHERE a.doctor ilike '%{}' and a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time));".format(Appointment, name, DateOfBird, PhoneNumber))
                else:
                    cursor.execute(
                        "SELECT a.patient_name, a.date_of_birth, a.phone_number, a.doctor FROM appointment_schedule as a WHERE a.doctor ilike '%{}' and a.psid='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time));".format(Appointment,psid))
                records = cursor.fetchall()
                count = cursor.rowcount
                if count == 0:
                    # vào được đây có nghĩa là build_options('Appointment', None, None, None, None, psid, name, DateOfBird, PhoneNumber) đã oke
                    slots['Appointment']=None
                    options=build_options('Appointment', None, None, None, None, psid, name, DateOfBird, PhoneNumber)
                    if options==None:
                        if AccountFBMakeAppointment=='Tài khoản khác':
                            slots['Name'] = None
                            slots['DateOfBird'] = None
                            slots['PhoneNumber'] = None
                            arr_date_of_bird = DateOfBird.split('-')
                            date_of_bird_display = arr_date_of_bird[2] + '/'+arr_date_of_bird[1]+'/'+arr_date_of_bird[0]
                            return elicit_slot(
                                output_session_attributes,
                                intent_request['currentIntent']['name'],
                                slots,
                                'Name',
                                {
                                    'contentType': 'PlainText',
                                    'content': 'Bệnh nhân {} sinh ngày {} có số điện thoại {} không có lịch hẹn nào cả. Mời bạn nhập lại thông tin. HỌ TÊN bệnh nhân là gì?. :)'.format(name, date_of_bird_display, PhoneNumber)
                                },
                                None)
                        else:
                            slots['AccountFBMakeAppointment'] = "Tài khoản khác"
                            return elicit_slot(
                                output_session_attributes,
                                intent_request['currentIntent']['name'],
                                slots,
                                'Name',
                                {
                                    'contentType': 'PlainText',
                                    'content': 'Hiện tài khoản này chưa đặt lịch hẹn nào. Để hủy lịch hẹn tôi cần được biết HỌ VÀ TÊN của bệnh nhân?'
                                },
                                None)
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Appointment', {
                            'contentType': 'PlainText',
                            'content': 'Không tồn tại lịch hẹn với bác sĩ {}. Bạn cần hủy lịch hẹn với bác sĩ nào ạ?'.format(Appointment)
                        },
                        build_response_card(
                            'Hiện tại có các lịch hẹn với các bác sĩ sau:',
                            'Mời bạn chọn lịch hẹn muốn hủy',
                            options))
                elif count>1:
                    element_of_name = Appointment.split(' ')
                    set_doctor = set()
                    options = []
                    for row in records:
                        str_value = row[3]
                        if(str_value in set_doctor):
                            continue
                        set_doctor.add(str_value)
                        temp = ({
                            'text': str_value,
                            'value': str_value})
                        options.append(temp)
                    if len(options) > 1:
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'Appointment', {
                                'contentType': 'PlainText',
                                'content': 'Có nhiều bác sĩ tên {}. Bạn muốn hủy hẹn với bác sĩ nào ạ?'.format(Appointment)
                            },
                            build_response_card(
                                'Các bác sĩ tên {} của khoa'.format(Appointment),
                                'Mời bạn chọn HỌ VÀ TÊN đầy đủ của bác sĩ',
                                options))
                    elif not name: #chỉ có bác sĩ nhưng có nhiều bệnh nhân đã đặt vs tài khoản này
                        slots['Name'] = None
                        slots['DateOfBird'] = None
                        slots['PhoneNumber'] = None
                        slots['Appointment'] = records[0][3]
                        Appointment  = records[0][3]
                        slots['AccountFBMakeAppointment'] = "Tài khoản khác"
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots,
                            'Name',
                            {
                                'contentType': 'PlainText',
                                'content': 'Tài khoản này đã đặt nhiều lịch hẹn với bác sĩ {}, để việc hủy hẹn được chính xác, mình cần biết HỌ VÀ TÊN của bệnh nhân?'.format(Appointment)
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
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'PhoneNumber', {
                                'contentType': 'PlainText',
                                'content': 'Số điện thoại đã đặt lịch hẹn là gì ạ?'
                            }, None)
                    else:
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
                    #nếu lịch hẹn cùng 1 bệnh nhân, cùng 1 tài khoản đặt thì hủy toàn bộ lịch đó(nhưng sẽ chặn trường hợp này trong xử lý MakeAppointment)
                else:
                    slots['Name'] = records[0][0]
                    slots['DateOfBird'] = records[0][1].strftime('%Y-%m-%d')
                    slots['PhoneNumber'] = records[0][2]
                    slots['Appointment'] = records[0][3]
                    Appointment=records[0][3]
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL", error)
            finally:
                if(connection):
                    cursor.close()
                    connection.close()
            return delegate(
                output_session_attributes,
                slots
            )
        elif Confirmation == "Có":
            try:
                connection = psycopg2.connect(
                    "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                #connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

                cursor = connection.cursor()
                if name and DateOfBird and PhoneNumber:
                    sql_delete_query = """Delete from appointment_schedule where doctor ilike '%{}' and patient_name ILIKE '%{}'  and date_of_birth='{}' and phone_number='{}' and (date>current_date or (date=current_date and time>current_time));""".format(Appointment, name, DateOfBird, PhoneNumber)
                    cursor.execute(sql_delete_query)
                else:
                    sql_delete_query = """Delete from appointment_schedule where doctor ilike '%{}' and psid='{}' and (date>current_date or (date=current_date and time>current_time));""".format(Appointment, psid)
                    cursor.execute(sql_delete_query)
                connection.commit()
                count = cursor.rowcount
                if count == 0:
                    return close2(
                        output_session_attributes,
                        'Fulfilled',
                        {
                            'contentType': 'PlainText',
                            'content': '^_^ Thông tin lịch hẹn trên không tồn tại. Hủy lịch hẹn thất bại. Bạn có thể tham khảo các dịch vụ hỗ  trợ khác của chat bot.'
                        }
                    )
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
                    'content': 'Hủy lịch hẹn không được tiến hành. Bạn có thể tham khảo các dịch vụ hỗ trợ khác của chat bot. O:)'
                }
            )
        return delegate(output_session_attributes, slots)
    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Hủy lịch hẹn.'
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
    if intent_name == 'VietnameseCancelAppointment':
        return cancel_appointment(intent_request)

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


#cancel_appointment(xxx)
