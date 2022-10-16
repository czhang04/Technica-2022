import os
from multiprocessing import Process, Value
import time
from twilio.rest import Client
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import geocoder

from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__)

users = {"+12407510959": [(38.9658, -77.068), "bus"]}

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
        dest = request.form.get('dest')
        dest_loc = loc.geocode(dest)
        coords = (dest_loc.latitude, dest_loc.longitude)
        users = {phone: coords}
    return render_template('home.html')

def call(phone):
    call = client.calls.create(
                        twiml='<Response><Say>You have almost arrived at your destination!</Say></Response>',
                        to=phone,
                        from_=twilio_phone
                    )

def track(phone, dest, threshold):
    curr_loc = geocoder.ip('me') # multiple users out of scope of this project
    curr_coords = (curr_loc.latitude, curr_loc.longitude)
    if geodesic(curr_coords, dest).miles <= threshold: # user close enough to dest, call user
        call(phone)
        del users[phone]
        

def big_loop():
    for k, v in users:
        phone = k
        dest = v[0]
        threshold = 0.5 # train
        if (v[1] == "bus"):
            threshold = 0.25 # bus
        track(phone, dest, threshold)

if __name__ == '__main__':
    print("start")
    recording_on = Value('b', True)
    p = Process(target=big_loop)
    p.start()  
    app.run(debug=True, use_reloader=False)
    p.join()
