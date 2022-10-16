import os
import phonenumbers
from multiprocessing import Process, Value
import time
from twilio.rest import Client
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import geocoder

from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__)

users = {"+12407510959": [(38.9658, -77.068), "bus",True]}

#set up twilio client
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)
twilio_phone = '+18507883830'

# set up Nominatim client
loc = Nominatim(user_agent="GetLoc")

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        phone = request.form.get('phone')
        val_phone = validate_phone(phone)
        dest = request.form.get('dest')
        dest_loc = loc.geocode(dest)
        mode = request.form.get('mode')
        print(val_phone)
        if(val_phone is not None and dest_loc is not None):
            coords = (dest_loc.latitude, dest_loc.longitude)
            values = [coords, mode, True]
            users[val_phone] = values
            print(users)
            return render_template('home.html', msg="Successfully added!")
        elif(val_phone is None):
            return render_template('home.html', msg="Invalid phone.")
        elif(dest_loc is None):
            return render_template('home.html', msg="Invalid destination.")

    return render_template('home.html')

def validate_phone(phone):
    try:
        p = phonenumbers.parse(phone,"US")
        print(p)
        if not phonenumbers.is_valid_number(p):
            p = "+1" + p
            p = phonenumbers.parse(phone,"US")
        if not phonenumbers.is_valid_number(p):
            return None
        return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        return None

def call(phone):
    call = client.calls.create(
                        twiml='<Response><Say>You have almost arrived at your destination!</Say></Response>',
                        to=phone,
                        from_=twilio_phone
                    )

def track(phone, dest, threshold):
    curr_loc = geocoder.ip('me') # multiple users out of scope of this project
    curr_coords = curr_loc.latlng
    if geodesic(curr_coords, dest).miles <= threshold: # user close enough to dest, call user
        #call(phone) # commented out because i have no twilio
        users[phone][2] = False
        print("byebye " + phone)
        

def big_loop():
    while True:
        for u in users:
            phone = u
            if users[phone][2]:
                dest = users[u][0]
                mode = users[u][1]
                threshold = 0.5 # train
                if (mode == "bus"):
                    threshold = 0.25 # bus
                print("tracking " + u + " on " + mode)
                track(phone, dest, threshold)

if __name__ == '__main__':
    print("start")
    recording_on = Value('b', True)
    p = Process(target=big_loop)
    p.start()  
    app.run(debug=True, use_reloader=False)
    p.join()
