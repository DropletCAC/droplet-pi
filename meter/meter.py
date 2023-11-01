from flask import Flask, request 
import json
import RPi.GPIO as GPIO
import time, sys, os
from datetime import datetime 
import threading 
import numpy as np
import requests

app = Flask(__name__)


class Meter:
    def __init__(self, user_id, section):
        self.count = 0
        self.start_counter = 0
        self.user_id = user_id
        self.section = section 
        self.total = 0
        
    def send(self, gal):
        requests.post(f"https://bengal-sought-bedbug.ngrok-free.app/setCurrentUsage?user={self.user_id}&section={self.section}&usage={gal}")

    def countPulse(self, channel):
        if self.start_counter == 1:
            self.count = self.count+1


    def start(self):
        FLOW_SENSOR_GPIO = 13
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(FLOW_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        

        GPIO.add_event_detect(FLOW_SENSOR_GPIO, GPIO.FALLING, callback=self.countPulse)

        while True:
            try:                
                # start_counter = 1
                # print("Starting counter...")
                # time.sleep(1)
                # print("Calculating")
                # start_counter = 0
                # flow = (self.count / 7.5) # Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
                # print(self.count, flow)
                # gal = flow / 3.785

                # message = f"Flow Rate: {flow} L/min | {gal} gal/min"
                # print(message)

                # self.count = 0
                # time.sleep(5)


                # USE THIS IN REAL WORLD
                # x = 0
                # flows = []
                # while (x < 5):
                #     self.start_counter = 1
                #     time.sleep(1)
                #     self.start_counter = 0
                #     flows.append(self.count / 7.5 / 3.785) # Pulse frequency (Hz) = 7.5Q, Q is flow rate in L/min.
                #     print("The flow is: %.3f gal/min" % (flows[-1]), x)
                #     self.count = 0
                #     if flows[-1] > 0:
                #         x += 1

                # flows = np.array(flows)
                # avg_flow = np.mean(flows)
                # print("AVG FLOW", avg_flow)
                # self.send(avg_flow)
                
                #DEMO ONLY
                self.start_counter = 1
                time.sleep(1)
                self.start_counter = 0
                print("The flow is", self.count / 7.5 / 3.785, "gal/min")
                self.send(round(self.count / 7.5 / 3.785), 1)
            except KeyboardInterrupt:
                print('\nkeyboard interrupt!')
                GPIO.cleanup()
                sys.exit()


@app.route('/setup', methods=['GET'])
def setup():
    user = request.args.get('user')
    section = request.args.get('section')

    print("Setting up and pairing to user", user)
    
    with open("user.json", "w+") as file:
        file.write(json.dumps({"user": user, "section": section}))
    
    meter = Meter(user, section)
    func = threading.Thread(target=meter.start)
    func.start()

    return json.dumps({"success": True, "user": user})


if __name__ == "__main__":
    if os.path.exists("user.json"):
        with open("user.json") as file:
            user_data = json.load(file)
            print(user_data)
            meter = Meter(user_data['user'], user_data['section'])
            meter.start()
    else:
        app.run(host="0.0.0.0", port=8080)