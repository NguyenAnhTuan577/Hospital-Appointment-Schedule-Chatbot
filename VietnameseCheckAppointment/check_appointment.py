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
        "name": "VietnameseCheckAppointment",
        "slots": {
            "AccountFBMakeAppointment": "Tài khoản này",
    "Appointment": None,
    "DateOfBird": None,
    "HospitalService": None,
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


def elicit_slot_with_message(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
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
                cursor.execute(
                    "SELECT a.doctor, a.date FROM appointment_schedule as a WHERE a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time));".format(name, DateOfBird, PhoneNumber))
                records = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT a.doctor, a.date FROM appointment_schedule as a WHERE a.psid='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time));".format(psid))
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
            #date_of_appointment = row[1]
            #if date_of_appointment >= datetime.date.today():
            set_doctor.add(str_value)
        for i in set_doctor:
            temp = ({
                    'text': i,
                    'value': i})
            res.append(temp)
        temp = ({
                'text': 'Kết thúc',
                'value': 'Kết thúc'})
        res.append(temp)
        return res
    elif slot == 'ChangeType':
        res = [{'text': 'Bác sĩ', 'value': 'Bác sĩ'}, {
            'text': 'Ngày', 'value': 'Ngày'}, {'text': 'Giờ', 'value': 'Giờ'}]
        return res
    elif slot == 'Confirmation':
        res = [{'text': 'Có', 'value': 'Có'}, {
            'text': 'Không', 'value': 'Không'}]
        return res


""" --- Functions that control the bot's behavior --- """


def check_appointment(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    AccountFBMakeAppointment = intent_request['currentIntent']['slots']['AccountFBMakeAppointment']
    Appointment = intent_request['currentIntent']['slots']['Appointment']
    name = intent_request['currentIntent']['slots']['Name']
    DateOfBird = intent_request['currentIntent']['slots']['DateOfBird']
    PhoneNumber = intent_request['currentIntent']['slots']['PhoneNumber']
    HospitalService = intent_request['currentIntent']['slots']['HospitalService']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
    }
    # booking_map = json.loads(try_ex(lambda: output_session_attributes['bookingMap']) or '{}')
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
    print(data)
    fb_name = data['name']
    fb_first_name = data['first_name']
    fb_last_name = data['last_name']
    print('name= ', fb_name)
    if source == 'DialogCodeHook':
        slots = intent_request['currentIntent']['slots']
        if HospitalService=='Không làm gì cả' or Appointment=='Kết thúc':
            return close2(
                output_session_attributes,
                'Fulfilled',
                {
                    'contentType': 'PlainText',
                    'content': 'Bạn có thể tham khảo thêm các hỗ trợ khác của chatbot ở đây:'
                })
        if not AccountFBMakeAppointment:
            # AccountFBMakeAppointment = "Tài khoản này"
            # slots['AccountFBMakeAppointment'] = "Tài khoản này"
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'AccountFBMakeAppointment',
                {
                    'contentType': 'PlainText',
                    'content': ':) Bạn muốn xem lịch hẹn được đặt bởi tài khoản facebook này hay tài khoản khác ạ?  ;)'
                },
                build_response_card(
                    'Tài khoản Facebook đã dùng để đặt lịch',
                    'Mời bạn chọn loại tài khoản',
                    build_options('AccountFBMakeAppointment', None, None, None, None, psid, None, None, None)))
        if AccountFBMakeAppointment == 'Tài khoản này':
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
                        'content': 'Hiện tài khoản này chưa đặt lịch hẹn nào. Có thể bạn muốn xem lịch hẹn được đặt bởi một tài khoản facebook khác. Làm ơn cho tôi biết tên bệnh nhân mà bạn muốn xem.'
                    },None)
        elif AccountFBMakeAppointment=='Tài khoản khác':
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
                        'content': 'Bây giờ tôi cần biết thêm NGÀY THÁNG NĂM SINH của bệnh nhân {}?'.format(name)
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
                        'content': 'Tôi chỉ cần biết SỐ ĐIỆN THOẠI đã đặt lịch hẹn nữa thôi? ^_^'
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
                        'content': 'Bệnh nhân {} sinh ngày {} có số điện thoại {} không có lịch hẹn nào cả. Mời bạn nhập lại thông tin. Họ tên bệnh nhân là gì?. :)'.format(name, date_of_bird_display, PhoneNumber)
                    },
                    None)
        if not Appointment:
            try:
                connection = psycopg2.connect(
                    "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                cursor = connection.cursor()
                if name and DateOfBird and PhoneNumber:
                    query="SELECT distinct a.speciality, a.doctor, a.date, a.time FROM appointment_schedule as a WHERE a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time)) order by a.date, a.time;".format(name,DateOfBird,PhoneNumber)
                else:
                    query="SELECT distinct a.speciality, a.doctor, a.date, a.time FROM appointment_schedule as a WHERE a.psid='{}' and (a.date>current_date or (a.date=current_date and a.time>current_time)) order by a.date, a.time;".format(psid)
                cursor.execute(query)
                records = cursor.fetchall()
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL", error)
            finally:
                if(connection):
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")
            options = []
            set_doctor = set()
            if cursor.rowcount == 0:#đã chặn các trường hợp ko có lịch hẹn xử lý ở trên
                return None
            for row in records:
                # str_value=row[1]+', '+row[4].strftime("%H:%M")+', '+row[3].strftime("%d/%m/%Y")
                str_value = row[1]
                #date_of_appointment = row[2]
                #if date_of_appointment >= datetime.date.today():
                if(str_value in set_doctor):
                    continue
                set_doctor.add(str_value)
                temp = ({
                    'text': str_value,
                    'value': str_value})
                options.append(temp)
            temp = ({
                    'text': 'Kết thúc',
                    'value': 'Kết thúc'})
            options.append(temp)
            message = "Đây là các lịch hẹn hiện có của bạn: <3"
            for row in records:
                #date_of_appointment = row[2]
                #time_of_appointment = row[3]
                #if date_of_appointment > datetime.datetime.now().date() or (date_of_appointment == datetime.datetime.now().date() and time_of_appointment>datetime.datetime.now().time()):
                element = "\n * Bác sĩ {} của {} lúc {} ngày {},".format(
                    row[1], row[0], row[3].strftime("%H:%M"), row[2].strftime("%d/%m/%Y"))
                message = message+element
            message = message[0: -1]
            return elicit_slot(
                output_session_attributes,
                'VietnameseCheckAppointment',
                slots,
                'Appointment', {
                    'contentType': 'PlainText',
                    'content': message
                },
                build_response_card(
                    'Bạn muốn thay đổi thông tin với bác sĩ nào?',
                    'Bạn có các lịch hẹn với các bác sĩ sau đây:',
                    options)
            )
        elif not HospitalService:
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
                    if options==None:#đã xử lý từ trước nên options ở trong này không bao giờ null
                        return delegate(output_session_attributes, slots)
                    message=''
                    if Appointment!='Khác':
                        message=message+'Không tồn tại lịch hẹn với bác sĩ {}. '.format(Appointment)
                    message=message+'Bạn cần thay đổi hoặc hủy lịch hẹn với bác sĩ nào ạ?'
                    return elicit_slot(
                        output_session_attributes,
                        intent_request['currentIntent']['name'],
                        slots, 'Appointment', {
                            'contentType': 'PlainText',
                            'content': message
                        },
                        build_response_card(
                            'Các lịch hẹn hiện có:',
                            'Mời bạn chọn lịch hẹn muốn hủy',
                            options))
                elif count==1:
                    slots['Name'] = records[0][0]
                    slots['DateOfBird'] = records[0][1].strftime('%Y-%m-%d')
                    slots['PhoneNumber'] = records[0][2]
                    slots['Appointment'] = records[0][3]
                    Appointment=records[0][3]
                    return delegate(output_session_attributes, slots)
                else:
                    element_of_name = Appointment.split(' ')
                    if len(element_of_name) == 1:
                        options = []
                        for row in records:
                            temp = {
                                'text': row[3],
                                'value': row[3]}
                            options.append(temp)
                        return elicit_slot(
                            output_session_attributes,
                            intent_request['currentIntent']['name'],
                            slots, 'Appointment', {
                                'contentType': 'PlainText',
                                'content': 'Có nhiều bác sĩ tên {}. Bạn muốn hủy hẹn với bác sĩ nào ạ?'.format(Appointment)
                            },
                            build_response_card(
                                'Các bác sĩ tên {} của khoa'.format(Appointment),
                                'Mời bạn chọn họ và tên đầy đủ của bác sĩ',
                                options))
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
                                'content': 'Tài khoản này đã đặt nhiều lịch hẹn với bác sĩ {}, để cập nhật chính xác lịch hẹn, mình cần biết HỌ TÊN của bệnh nhân?'.format(Appointment)
                            },
                            None)
                    #nếu lịch hẹn cùng 1 bệnh nhân, cùng 1 tài khoản đặt thì hủy toàn bộ lịch đó(nhưng sẽ chặn trường hợp này trong xử lý MakeAppointment)
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL", error)
            finally:
                if(connection):
                    cursor.close()
                    connection.close()
        elif HospitalService == 'Chỉnh sửa lịch hẹn':
            slots = {
                "AccountFBMakeAppointment": AccountFBMakeAppointment,
                "Appointment": Appointment,
                "ChangeType": None,
                "Confirmation": None,
                "Date": None,
                "DateOfBird": DateOfBird,
                "Doctor": None,
                "Name": name,
                "PhoneNumber": PhoneNumber,
                "Speciality": None,
                "Time": None
            }
            return elicit_slot(
                output_session_attributes,
                'VietnameseUpdateAppointment',
                slots,
                'ChangeType', {
                    'contentType': 'PlainText',
                    'content': 'Bạn muốn cập nhật thông tin nào ạ? O:)'
                },
                build_response_card(
                    'Danh mục muốn thay đổi:',
                    'Mời bạn chọn thông tin cần thay đổi',
                    build_options('ChangeType', None, None, None, None, psid, None, None, None))
            )
        elif HospitalService == 'Hủy lịch hẹn':
            slots = {"AccountFBMakeAppointment": AccountFBMakeAppointment,
                     "Appointment": Appointment,
                     "Confirmation": None,
                     "DateOfBird": DateOfBird,
                     "Name": name,
                     "PhoneNumber": PhoneNumber}
            return elicit_slot(
                output_session_attributes,
                'VietnameseCancelAppointment',
                slots,
                'Confirmation', {
                    'contentType': 'PlainText',
                    'content': 'Bạn có chắc chắn muốn hủy lịch hẹn với bác sĩ {}? O:)'.format(Appointment)
                },
                build_response_card(
                    'Bạn có chắc chắn muốn hủy lịch hẹn',
                    'Các lựa chọn dành cho bạn',
                    build_options('Confirmation', None, None, None, None, psid, None, None, None))
            )
        else:
            slots['HospitalService']=None
            return delegate(output_session_attributes, slots)
        return delegate(output_session_attributes, slots)
    return elicit_slot(
        output_session_attributes,
        intent_request['currentIntent']['name'],
        slots,
        'Appointment', {
            'contentType': 'PlainText',
            'content': '<3 Đây là các lịch khám bệnh hiện có của bạn:'
        },
        build_response_card(
            'Bạn có các lịch hẹn với các bác sĩ sau đây',
            'Mời bạn xem',
            build_options('Appointment', None, None, None, None, psid, None, None, None)))


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(
        intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'VietnameseCheckAppointment':
        return check_appointment(intent_request)

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


#check_appointment(xxx)
# SELECT * FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name='Dr Do Thanh Long' and ms.name='Cardiology'
