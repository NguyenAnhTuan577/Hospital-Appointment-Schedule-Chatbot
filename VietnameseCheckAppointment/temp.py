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

def get_kendra_answer(question):
    try:
        KENDRA_INDEX = os.environ['KENDRA_INDEX']
    except KeyError:
        return 'Configuration error - please set the Kendra index ID in the environment variable KENDRA_INDEX.'
    
    try:
        response = kendra_client.query(IndexId=KENDRA_INDEX, QueryText=question)
    except:
        return None

    logger.debug('<<help_desk_bot>> get_kendra_answer() - response = ' + json.dumps(response)) 
    
    #
    # determine which is the top result from Amazon Kendra, based on the Type attribue
    #  - QUESTION_ANSWER = a result from a FAQ: just return the FAQ answer
    #  - ANSWER = text found in a document: return the text passage found in the document plus a link to the document
    #  - DOCUMENT = link(s) to document(s): check for several documents and return the links
    #
    
    first_result_type = ''
    try:
        first_result_type = response['ResultItems'][0]['Type']
    except KeyError:
        return None

    if first_result_type == 'QUESTION_ANSWER':
        try:
            faq_answer_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
        except KeyError:
            faq_answer_text = "Sorry, I could not find an answer in our FAQs."

        return faq_answer_text

    elif first_result_type == 'ANSWER':
        # return the text answer from the document, plus the URL link to the document
        try:
            document_title = response['ResultItems'][0]['DocumentTitle']['Text']
            document_excerpt_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
            document_url = response['ResultItems'][0]['DocumentURI']
            answer_text = "I couldn't find a specific answer, but here's an excerpt from a document ("
            answer_text += "<" + document_url + "|" + document_title + ">"
            answer_text += ") that might help:\n\n" + document_excerpt_text + "...\n"            
        except KeyError:
            answer_text = "Sorry, I could not find the answer in our documents."

        return answer_text

    elif first_result_type == 'DOCUMENT':
        # assemble the list of document links
        document_list = "Here are some documents you could review:\n"
        for item in response['ResultItems']:
            document_title = None
            document_url = None
            if item['Type'] == 'DOCUMENT':
                if item.get('DocumentTitle', None):
                    if item['DocumentTitle'].get('Text', None):
                        document_title = item['DocumentTitle']['Text']
                if item.get('DocumentId', None):
                    document_url = item['DocumentURI']
            
            if document_title is not None:
                document_list += '-  <' + document_url + '|' + document_title + '>\n'

        return document_list

    else:
        return None 
""" --- Functions that control the bot's behavior --- """
def check_kendra(intent_request):
    """
    Performs dialog management and fulfillment for booking a dentists appointment.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of confirmIntent to support the confirmation of inferred slot values, when confirmation is required
    on the bot model and the inferred slot values fully specify the intent.
    """
    # service_type = intent_request['currentIntent']['slots']['HospitalService']
    Appointment = intent_request['currentIntent']['slots']['Appointment']
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
        if Appointment == None:
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
            # for i in set_doctor:
            #     temp = ({
            #             'text': i,
            #             'value': i})
            #     options.append(temp)
            message = "Đây là các lịch hẹn hiện có của bạn: <3"
            for row in records:
                date_of_appointment = row[2]
                if date_of_appointment >= datetime.date.today():
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
        elif HospitalService == 'Chỉnh sửa lịch hẹn':
            slots = {
                "AccountFBMakeAppointment": "Tài khoản này",
                "Appointment": Appointment,
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
            slots = {"AccountFBMakeAppointment": "Tài khoản này",
                     "Appointment": Appointment,
                     "Confirmation": None,
                     "DateOfBird": None,
                     "Name": None,
                     "PhoneNumber": None}
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
    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'FallBackKendra':
        return check_kendra(intent_request)

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
    return dispatch(event)


