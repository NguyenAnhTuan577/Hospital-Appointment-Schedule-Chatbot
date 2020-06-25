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
        "name": "FinancialInformation",
        "slots": {
            "HospitalService": None
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


def close2(session_attributes, fulfillment_state, message, title, subtitle, options, imageUrl, attachmentLinkUrl):
    responseCard = build_response_card(
        title, subtitle, options, imageUrl, attachmentLinkUrl)
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message,
            "responseCard": responseCard
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


def build_response_card(title, subtitle, options, imageUrl, attachmentLinkUrl):
    """
    Build a responseCard with a title, subtitle, and an optional set of options which should be displayed as buttons.
    """
    buttons = None
    genericAttachments = []
    if options is not None:
        buttons = []
        genericAttachmentElement = {}
        if not attachmentLinkUrl:
            attachmentLinkUrl = "https://www.facebook.com/Sai-Gon-Hospital-Bot-109455814006419/?modal=admin_todo_tour"
        if not imageUrl:
            imageUrl = "https://article.images.consumerreports.org/f_auto/prod/content/dam/CRO%20Images%202018/Health/May/CR-Health-InlineHero-C-Section-Risk-Hospital-05-18"
        cnt = 0
        for i in range(len(options)):
            buttons.append(options[i])
            cnt = cnt+1
            if cnt == 3 or i == len(options)-1:
                genericAttachmentElement = {
                    'title': title,
                    'subTitle': subtitle,
                    "imageUrl": imageUrl,
                    "attachmentLinkUrl": attachmentLinkUrl,
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
    #     "attachmentLinkUrl": None,
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
    #     "imageUrl": None,
    #     "subTitle": None,
    #     "title": "Giới tính của bạn là gì?"
    #   },
    #   {
    #     "attachmentLinkUrl": None,
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
    #     "imageUrl": None,
    #     "subTitle": None,
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
    if slot == 'Appointment':
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
                    "SELECT a.doctor, a.date FROM appointment_schedule as a WHERE a.patient_name ILIKE '%{}' and a.date_of_birth='{}' and a.phone_number='{}';".format(name, DateOfBird, PhoneNumber))
                records = cursor.fetchall()
            else:
                cursor.execute(
                    "SELECT a.doctor, a.date FROM appointment_schedule as a WHERE a.psid='{}';".format(psid))
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
        print(res)
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
    elif slot == 'ChangeType':
        res = [{'text': 'Bác sĩ', 'value': 'Bác sĩ'}, {
            'text': 'Ngày', 'value': 'Ngày'}, {'text': 'Giờ', 'value': 'Giờ'}]
        return res
    elif slot == 'Confirmation':
        res = [{'text': 'Tôi muốn hủy', 'value': 'Có'}, {
            'text': 'Tôi chưa muốn hủy', 'value': 'Không'}]
        return res
    elif slot == 'HospitalService':
        res = [{'text': 'Lấy lịch hẹn', 'value': 'Lấy lịch hẹn'}, {
            'text': 'Chỉnh sửa lịch hẹn', 'value': 'Chỉnh sửa lịch hẹn'}, {'text': 'Hủy lịch hẹn', 'value': 'hủy hẹn'}, {'text': 'Xem lịch hẹn', 'value': 'Xem lịch hẹn'}, {'text': 'Xem thông tin bệnh viện', 'value': 'Xem thông tin bệnh viện'}]
        return res
    elif slot == "AccountFBMakeAppointment":
        res = [{'text': 'Tài khoản này', 'value': 'Tài khoản này'}, {
            'text': 'Tài khoản khác', 'value': 'Tài khoản khác'}]
        return res
    elif slot == 'Information':
        res = [{'text': 'Liên hệ', 'value': 'Liên hệ'}, {
            'text': 'Bảo hiểm', 'value': 'Bảo hiểm'}, {'text': 'Viện phí', 'value': 'Viện phí'}, {
            'text': 'Cơ sở vật chất', 'value': 'Cơ sở vật chất'}, {'text': 'Hội viên', 'value': 'Hội viên'}]
        return res


""" --- Functions that control the bot's behavior --- """


def financial_information(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    HospitalService = intent_request['currentIntent']['slots']['HospitalService']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {
    }
    # booking_map = json.loads(try_ex(lambda: output_session_attributes['bookingMap']) or '{}')
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
        if not HospitalService:
            message = "Tại bệnh viện Pháp-Việt, chúng tôi áp dụng chính sách giá hợp lý và tương xứng với dịch vụ y tế chất lượng cao trong khu vực Đông Nam Á. Bấm vào hình bên dưới để biết thêm thông tin chi tiết."
            imageUrl = "https://www.hoanmydongnai.com/upload/hoanmydongnai.com/images/service/2019-05-14/detail_1557819248_8ZfOSJvAeJ.jpg"
            attachmentLinkUrl = "https://www.fvhospital.com/vi/thong-tin-danh-cho-benh-nhan/thong-tin-vien-phi/"
            options = build_options(
                'HospitalService', None, None, None, None, None, None, None, None)
            return close2(
                output_session_attributes,
                'Fulfilled',
                {
                    'contentType': 'PlainText',
                    'content': message
                }, 'Bạn cần gì ạ?',
                'Các dịch vụ hỗ trợ của chatbot',
                options, imageUrl, attachmentLinkUrl
            )
        elif HospitalService == 'Lấy lịch hẹn':
            slots = {
                "Confirmation": None,
                "Date": None,
                "DateOfBird": None,
                "DiseaseOne": None,
                "DiseaseTwo": None,
                "Doctor": None,
                "FormattedDate": None,
                "Name": None,
                "PhoneNumber": None,
                "Speciality": None,
                "Time": None,
                "UpdateSlot": None
            }
            return elicit_slot(
                output_session_attributes,
                'VietnameseMakeAppointment',
                slots,
                'Speciality', {
                    'contentType': 'PlainText',
                    'content': 'Bạn muốn khám tại khoa nào ạ?'
                },
                build_response_card(
                    'Các khoa của bệnh viện',
                    'Mời bạn chọn khoa mình muốn khám',
                    build_options('Speciality', None, None, None, None, psid, None, None, None), None, None)
            )
        elif HospitalService == 'Chỉnh sửa lịch hẹn':
            slots = {
                "AccountFBMakeAppointment": None,
                "Appointment": None,
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
            return elicit_slot(
                output_session_attributes,
                'VietnameseUpdateAppointment',
                slots,
                'AccountFBMakeAppointment', {
                    'contentType': 'PlainText',
                    'content': 'Bạn đã đặt lịch hẹn đó bởi tài khoản facebook này hay tài khoản khác?'
                },
                build_response_card(
                    'Tài khoản Facebook đã dùng để đặt lịch',
                    'Mời bạn chọn loại tài khoản',
                    build_options('AccountFBMakeAppointment', None, None, None, None, psid, None, None, None), None, None)
            )
        elif HospitalService == 'Hủy lịch hẹn':
            slots = {"AccountFBMakeAppointment": None,
                     "Appointment": None,
                     "Confirmation": None,
                     "DateOfBird": None,
                     "Name": None,
                     "PhoneNumber": None}
            return elicit_slot(
                output_session_attributes,
                'VietnameseCancelAppointment',
                slots,
                'AccountFBMakeAppointment', {
                    'contentType': 'PlainText',
                    'content': 'Bạn đã đặt lịch hẹn đó bởi tài khoản facebook này hay tài khoản khác?'
                },
                build_response_card(
                    'Tài khoản Facebook đã dùng để đặt lịch',
                    'Mời bạn chọn loại tài khoản',
                    build_options('AccountFBMakeAppointment', None, None, None, None, psid, None, None, None), None, None)
            )
        elif HospitalService == 'Xem lịch hẹn':
            slots = {
                "Appointment": None,
                "HospitalService": None
            }
            try:
                connection = psycopg2.connect(
                    "dbname='qjunivvc' user='qjunivvc' host='arjuna.db.elephantsql.com' password='qcGs166MeIBq6DTtdOqCOs7l_lIJhcLL'")
                # connection = psycopg2.connect("dbname='ivsnhdra' user='ivsnhdra' host='john.db.elephantsql.com' password='gyN4Z6OPzHvr6jp9ZsNLmYkfm2HkuM3f'")

                cursor = connection.cursor()
                # Print PostgreSQL Connection properties
                print(connection.get_dsn_parameters(), "\n")

                # Print PostgreSQL version
                cursor.execute(
                    "SELECT distinct a.speciality, a.doctor, a.date, a.time FROM appointment_schedule as a WHERE a.psid='{}' order by a.date;".format(psid))
                records = cursor.fetchall()
            except (Exception, psycopg2.Error) as error:
                print("Error while connecting to PostgreSQL", error)
            finally:
                # closing database connection.
                if(connection):
                    cursor.close()
                    connection.close()
                    print("PostgreSQL connection is closed")
            options = []
            set_doctor = set()
            if len(records) == 0:
                return None
            for row in records:
                # str_value=row[1]+', '+row[4].strftime("%H:%M")+', '+row[3].strftime("%d/%m/%Y")
                str_value = row[1]
                date_of_appointment = row[2]
                if date_of_appointment >= datetime.date.today():
                    if(str_value in set_doctor):
                        continue
                    set_doctor.add(str_value)
                    temp = ({
                        'text': str_value,
                        'value': str_value})
                    options.append(temp)
            message = "Các lịch hẹn:"
            for row in records:
                date_of_appointment = row[2]
                if date_of_appointment >= datetime.date.today():
                    element = " Bác sĩ {} của {} lúc {} ngày {},".format(
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
                    options, None, None)
            )
        elif HospitalService == 'Xem thông tin bệnh viện':
            slots = {
                "HospitalService": None,
                "Information": None
            }
            return elicit_slot(
                output_session_attributes,
                'InformationFVHospital',
                slots,
                'Information', {
                    'contentType': 'PlainText',
                    'content': 'Bạn cần tìm hiểu thông tin về vấn đề gì ạ?'
                },
                build_response_card(
                    'Thông tin về bệnh viện',
                    'Mời bạn chọn:',
                    build_options('Information', None, None, None, None, psid, None, None, None), None, None)
            )
        return delegate(output_session_attributes, slots)
    return None


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(
        intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'FinancialInformation':
        return financial_information(intent_request)

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


# financial_information(xxx)
# SELECT * FROM working_hours as wh, doctors as d , medical_specialities as ms where wh.doctor_id=d.id and ms.id=d.speciality_id and d.name='Dr Do Thanh Long' and ms.name='Cardiology'
