from pymongo import MongoClient
from time import time
from flask import Flask, request, jsonify
import requests
import json, datetime, random, certifi
app = Flask(__name__)

token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMzhRS0QiLCJzdWIiOiJCNEYzNVEiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcm94eSBycHJvIHJudXQgcnNsZSByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNjkxMDQxNzA4LCJpYXQiOjE2NTk1MDU3MDh9.NzxJB3FZxmWDyJx44pvUZOCkqME50heLRhYWD19z1go"
ptoken = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyMzhRUEYiLCJzdWIiOiJCNEYzNVEiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcm94eSBycHJvIHJudXQgcnNsZSByYWN0IHJyZXMgcmxvYyByd2VpIHJociBydGVtIiwiZXhwIjoxNjkyMzIyMTc4LCJpYXQiOjE2NjA3ODYxNzh9.t4-tjP-pBKe-wdbYLTL9t-h7wAOWsAlu-cGurSkfJiU"
myheader = {'Accept' : 'application/json', 'Authorization' : 'Bearer {}'.format(token)}
myPheader = {'Accept' : 'application/json', 'Authorization' : 'Bearer {}'.format(ptoken)}

client = MongoClient("mongodb+srv://Fieryluketaco:Aquarius@cluster0.thwhulr.mongodb.net/?retryWrites=true&w=majority", tlsCAFile=certifi.where())
db = client["mydb"]

# temp = random.randint(60, 100)
# humidity = random.randint(60, 100)
# timestamp = time()
# retstr = {'temp':temp, 'humidity':humidity, 'timestamp':timestamp}
# db.env.insert_one(retstr)

# presence = random.choice(['yes','no'])
# pose = random.choice(['standing','sitting','reclining','laying down','moving','stretching'])
# timestamp = time()
# retstr = {'presence':presence, 'pose':pose, 'timestamp':timestamp}
# db.pose.insert_one(retstr)

@app.route("/sensors/env", methods=["GET"])
def get_env():
    rows = db.env.find({})
    retdict = {}
    retdict.update({})
    for row in rows:
        retdict:dict
        retdict.update(row)
    del retdict['_id']
    return(retdict)



@app.route("/sensors/pose", methods=["GET"])
def get_pose():
    rows = db.pose.find({})
    retdict = {}
    retdict.update({})
    for row in rows:
        retdict:dict
        retdict.update(row)
    del retdict['_id']
    return(retdict)


@app.route("/post/env", methods=["POST"])
def post_env():
    temp = request.get_json.get("temp")
    humidity = request.get_json.get("humid")
    timestamp = time()
    retstr = {'temp':temp, 'humidity':humidity, 'timestamp':timestamp}
    db.env.insert_one(retstr)
    return jsonify(retstr)

@app.route("/post/pose", methods=["POST"])
def post_pose():
    presence = request.get_json.get("presence")
    pose = request.get_json.get("pose")
    timestamp = time()
    retstr = {'presence':presence, 'pose':pose, 'timestamp':timestamp}
    db.pose.insert_one(retstr)
    return jsonify(retstr)

userurl = "https://api.fitbit.com/1/user/-/profile.json"
userresp = request.get(userurl, headers=myPheader).json()
@app.route("/name", methods=["GET"])
def get_name():
    global name
    name = userresp["user"]["fullName"]
    retStr = {'Name': name}
    return jsonify(retStr)


hearturl  = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1min.json"
heartresp = request.get(hearturl, headers=myPheader).json()
@app.route("/heartrate/last", methods=["GET"])
def get_last_heartrate():
    heart_rate = heartresp['activities-heart-intraday']['dataset'][-1]['value']
    time_taken = heartresp['activities-heart-intraday']['dataset'][-1]['time']
    current_time = datetime.datetime.strptime(datetime.datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
    time_adjust = datetime.timedelta(0,14400,0)
    time_offset = current_time - datetime.datetime.strptime(time_taken, '%H:%M:%S')
    time_offset_timezone = time_offset - time_adjust
    str_time_offset:str = str(time_offset_timezone)

    retStr = {'Heartrate': heart_rate, 'time-offset':str_time_offset}
    return jsonify(retStr)

stepsurl = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d.json"
stepstimeurl = "https://api.fitbit.com/1/user/-/activities/steps/date/today/1d/1min.json"
stepsresp = request.get(stepsurl, headers=myPheader).json()
stepstimeresp = request.get(stepstimeurl, headers=myPheader).json()
@app.route("/steps/last", methods=["GET"])
def get_last_steps():
    steps = stepsresp["activities-steps"][0]["value"]
    current_time = datetime.datetime.strptime(datetime.datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
    last_steps_time = datetime.datetime.strptime(stepstimeresp["activities-steps-intraday"]["dataset"][-1]["time"], "%H:%M:%S")
    time_offset = current_time - last_steps_time
    str_time_offset:str = str(time_offset - datetime.timedelta(0,14400,0))

    retStr = {'steps': steps, 'time-offset': str_time_offset}
    return jsonify(retStr)


@app.route("/sleep/<date>")
def sleep_stages(date):
    sleepurl = "https://api.fitbit.com/1.2/user/-/sleep/date/" + date + ".json"
    sleepresp = request.get(sleepurl, headers=myPheader).json()

    try:
        deep = sleepresp["summary"]["stages"]["deep"]
        light = sleepresp["summary"]["stages"]["light"]
        rem = sleepresp["summary"]["stages"]["rem"]
        wake = sleepresp["summary"]["stages"]["wake"]
    except:
        return "Nothing recorded on given day."

    retStr = {'deep': deep, 'light': light, 'rem': rem, 'wake': wake}
    return jsonify(retStr)
    

@app.route("/activity/<date>")
def activity_stages(date):
    myurl = "https://api.fitbit.com/1/user/-/activities/date/" + date + ".json"
    resp = request.get(myurl, headers=myheader).json()

    sedentary = resp["summary"]["sedentaryMinutes"]
    light = resp["summary"]["lightlyActiveMinutes"]
    fair = resp["summary"]["fairlyActiveMinutes"]
    very = resp["summary"]["veryActiveMinutes"]

    retStr = {'very-active': very, 'fairly-active': fair, 'lightly-active': light, 'sedentary': sedentary}
    return jsonify(retStr)


if __name__ == '__main__':
    app.run(debug=True)