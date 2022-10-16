import os
from twilio.rest import Client

from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__)

users = {"+12407510959": (38.9658, -77.068)}

#set up twilio client
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)
twilio_phone = '+18507883830'

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        phone = request.form.get('phone')
        dest = request.form.get('dest')
    

@app.route('/call', methods=['GET', 'POST'])
def call():
    call = client.calls.create(
                        twiml='<Response><Gather input="dtmf" timeout="3" numDigits="1" action="/success" actionOnEmptyResult=false><Say>Press any key to confirm that you are awake.</Say></Gather></Response>',
                        to='+12407510959',
                        from_='+18507883830'
                    )

@app.route('/success')
def success():
    digits = request.args.get('Digits')
    print("success: " + str(digits))


if __name__ == '__main__':
    application.run(debug=True)