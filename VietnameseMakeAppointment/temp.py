import datetime

print(datetime.datetime.now().date())
date=datetime.datetime.now().date()
time='20:00'
if date==datetime.datetime.now().date():
    if time>datetime.datetime.now().time():
        temp = {
            'text': build_time_output_string(x),
            'value': build_time_output_string(x)}
else:
    temp = {
            'text': build_time_output_string(x),
            'value': build_time_output_string(x)}
#(a.date>current_date or (a.date=current_date and a.time>current_time))