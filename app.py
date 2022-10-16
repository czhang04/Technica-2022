import os
import phonenumbers
from multiprocessing import Process, Value
import time
import pickle
from twilio.rest import Client
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import geocoder

from flask import Flask, render_template, request, session, redirect, url_for
app = Flask(__name__)

users = {"+12407510959": [(38.9658, -77.068), "bus", True]}
pickle_out = open("user.pickle","wb")
pickle.dump(users, pickle_out)
pickle_out.close()

#set up twilio client
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)
twilio_phone = '+18507883830'

# set up Nominatim client
loc = Nominatim(user_agent="GetLoc")

@app.route('/', methods=['GET', 'POST'])
def form():
    global users
    users = readPickleDict(users)
    if request.method == 'POST':
        phone = request.form.get('phone')
        val_phone = validate_phone(phone)
        dest = request.form.get('dest')
        dest_loc = loc.geocode(dest)
        mode = request.form['radio']
        print("mode: " + str(mode))
        print(val_phone)
        if(val_phone is not None and dest_loc is not None):
            coords = (dest_loc.latitude, dest_loc.longitude)
            values = [coords, mode, True]
            users[val_phone] = values
            print(users)
            writePickleDict(users)
            return render_template('redirect.html')
        elif(val_phone is None):
            return render_template('home.html', msg="Invalid phone.")
        elif(dest_loc is None):
            return render_template('home.html', msg="Invalid destination.")

    return render_template('home.html', msg=None)

def validate_phone(phone):
    try:
        p = phonenumbers.parse(phone,"US")
        print(p)
        if not phonenumbers.is_valid_number(p):
            p = "+1" + str(p)
            p = phonenumbers.parse(phone,"US")
        if not phonenumbers.is_valid_number(p):
            return None
        return phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164)
    except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
        return None

@app.route('/success', methods=['GET', 'POST'])
def success():
    if request.method == 'POST':
        return redirect(url_for('form'))
    return render_template('redirect.html')

def call(phone):
    call = client.calls.create(
                        twiml='<Response><Say>You have almost arrived at your destination!</Say></Response>',
                        to=phone,
                        from_=twilio_phone
                    )

def track(phone, dest, threshold):
    #curr_loc = geocoder.ip('me') # multiple users out of scope of this project
    #curr_coords = (38.9658, -77.068)#curr_loc.latlng
    f = open("demo.txt", "r")
    longitude = f.readline()
    latitude = f.readline()
    curr_coords = (longitude, latitude)
    if geodesic(curr_coords, dest).miles <= threshold: # user close enough to dest, call user
        #call(phone) # commented out to avoid too many phone calls
        users[phone][2] = False
        print("byebye " + phone)
        writePickleDict(users)
        

def big_loop():
    while True:
        print("arrived in big loop")
        global users
        users = readPickleDict(users)
        print(users)
        for u in users:
            print("arrived in for loop")
            print("User has arrived: " + str(users[u][2]))
            if users[u][2]:
                dest = users[u][0]
                mode = users[u][1]
                threshold = 0.5 # train
                if (mode == "bus"):
                    threshold = 0.25 # bus
                print("tracking " + str(u) + " on " + str(mode))
                track(u, dest, threshold)
        time.sleep(5)

def writePickleDict(x):
    pickle_out = open("users.pickle","wb")
    pickle.dump(x, pickle_out)
    pickle_out.close()

def readPickleDict(x):
    pickle_in = open("users.pickle","rb")
    x = pickle.load(pickle_in)
    return x

if __name__ == '__main__':
    print("start")
    recording_on = Value('b', True)
    p = Process(target=big_loop)
    p.start()  
    app.run(debug=True, use_reloader=False)
    p.join()
