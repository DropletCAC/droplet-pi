from flask import Flask, request 
import json
import RPi.GPIO as GPIO
import time, sys, os
import threading 
import requests
import math 

app = Flask(__name__)


class Bucket:
    def __init__(self, user_id, bucket, base_dim, height_dim):
        self.user_id = user_id
        self.bucket = bucket 
        self.base_dim = float(base_dim)
        self.height_dim = float(height_dim)
        
        
    def send(self, gal):
        requests.post(f"https://bengal-sought-bedbug.ngrok-free.app/setTankCapacity?user={self.user_id}&bucket={self.bucket}&volume={gal}")


    def start(self):
        GPIO.setmode(GPIO.BCM)

        TRIG = 2
        ECHO = 3
        i=0

        GPIO.setup(TRIG ,GPIO.OUT)
        GPIO.setup(ECHO,GPIO.IN)

        GPIO.output(TRIG, False)
        print("Starting.....")
        time.sleep(2)

        while True:
            try:
                GPIO.output(TRIG, True)
                time.sleep(0.00001)
                GPIO.output(TRIG, False)

                while GPIO.input(ECHO)==0:
                    pulse_start = time.time()

                while GPIO.input(ECHO)==1:
                    pulse_stop = time.time()

                pulse_time = pulse_stop - pulse_start

                distance = pulse_time * 17150
                print(round(distance, 2));

                time.sleep(1)

                print("Distance (cm)", distance)
                distance /= 2.54
                print("Distance (in)", distance)
                
                print("Height of Water (in)", self.height_dim - distance)
                
                water_height = self.height_dim - distance 
                vol = water_height * ((self.base_dim ^ 2) * math.pi)
                
                print("Vol (Inches^3)", vol)
                vol /= 231
                
                print("Vol (gal)", vol)
                
                self.send(vol)
                
                time.sleep(60)
            except KeyboardInterrupt:
                print("Keyboard Interrupt")
                exit()


@app.route('/setup', methods=['GET'])
def setup():
    user = request.args.get('user')
    bucket = request.args.get('bucket')
    base_dim = request.args.get('base_dim') #radius in inches
    height_dim = request.args.get('height_dim') #height in inches

    print("Setting up and pairing to user", user)
    
    with open("user.json", "w+") as file:
        file.write(json.dumps({"user": user, "bucket": bucket, "base_dim": base_dim, "height_dim": height_dim}))
    
    bucket = Bucket(user, bucket, base_dim, height_dim)
    func = threading.Thread(target=bucket.start)
    func.start()

    return json.dumps({"success": True, "user": user})


if __name__ == "__main__":
    if os.path.exists("user.json"):
        with open("user.json") as file:
            user_data = json.load(file)
            print(user_data)
            bucket = Bucket(user_data['user'], user_data['bucket'], user_data['base_dim'], user_data['height_dim'])
            bucket.start()
    else:
        app.run(host="0.0.0.0", port=8080)