import os
from twilio.rest import Client
from geopy.geocoders import Nominatim
import geocoder

from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__)

users = {"+12407510959": (38.9658, -77.068)}

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
    

@app.route('/call', methods=['GET', 'POST'])
def call():
    call = client.calls.create(
                        twiml='<Response><Say>You have almost arrived at your destination!</Say></Response>',
                        to='+12407510959',
                        from_='+18507883830'
                    )

@app.route('/success')
def success():
    digits = request.args.get('Digits')
    print("success: " + str(digits))


if __name__ == '__main__':
    application.run(debug=True)