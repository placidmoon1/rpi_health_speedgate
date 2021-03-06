#importing libraries
from imutils.video import VideoStream
from firebase_format import firebase_format
from smbus2 import SMBus
from mlx90614 import MLX90614
from pyzbar import pyzbar
import argparse
import imutils
import datetime
import time
import cv2
import pyrebase
import random
import logging
import threading
import RPi.GPIO as GPIO

"""Constants"""

machine_name = "RPI_2" # name of machine
#pin definition
pwmPinL = 16 # GPIO 22
dirPinL = 15 # GPIO 23
pwmPinR = 22
dirPinR = 21
buzzerPin = 11 

dc = 100 # duty cycle (0-100) for PWM pin

# Pin Setup
GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme
GPIO.setup(pwmPinL, GPIO.OUT) # PWM pin set as output
GPIO.setup(dirPinL, GPIO.OUT) # PWM pin set as output
GPIO.setup(pwmPinR, GPIO.OUT) # PWM pin set as output
GPIO.setup(dirPinR, GPIO.OUT) # PWM pin set as output

"""Setup GPIO"""
GPIO.setmode(GPIO.BOARD) # Broadcom pin-numbering scheme
GPIO.setup(buzzerPin, GPIO.OUT) # PWM pin set as output

"""temp sensor"""
bus = SMBus(1)
sensor = MLX90614(bus, address=0x5A)

def ring_buzzer():
    GPIO.output(buzzerPin,GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(buzzerPin,GPIO.LOW)

def open_gate():  
  GPIO.output(dirPinL, GPIO.HIGH)
  GPIO.output(dirPinR, GPIO.LOW)
  for i in range(20000):
    GPIO.output(pwmPinR,GPIO.HIGH)
    GPIO.output(pwmPinL,GPIO.HIGH)
    time.sleep(0.0000015)
    GPIO.output(pwmPinL,GPIO.LOW)
    GPIO.output(pwmPinR,GPIO.LOW)
    time.sleep(0.0000015)
  GPIO.output(dirPinL, GPIO.LOW)
  GPIO.output(dirPinR, GPIO.HIGH)
  time.sleep(2)
  for i in range(20000):
    GPIO.output(pwmPinR,GPIO.HIGH)
    GPIO.output(pwmPinL,GPIO.HIGH)
    time.sleep(0.0000015)
    GPIO.output(pwmPinR,GPIO.LOW)
    GPIO.output(pwmPinL,GPIO.LOW)
    time.sleep(0.0000015)

#config for logging
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(relativeCreated)6d %(threadName)s %(message)s'
)

#config for firebase
config = {
    "apiKey": "AIzaSyDskRTvi-3adT4i0LinEqzDrB67z6U6pZA",
    "authDomain": "temperature-monitor-speedgate.firebaseapp.com",
    "databaseURL": "https://temperature-monitor-speedgate.firebaseio.com",
    "projectId": "temperature-monitor-speedgate",
    "storageBucket": "temperature-monitor-speedgate.appspot.com",
    "messagingSenderId": "520308142005",
    "appId": "1:520308142005:web:c5ae8204b7a2d03b6b73fc",
    "measurementId": "G-115LZQVGGY"
}
firebase = pyrebase.initialize_app(config)

# Get a reference to the database service
db = firebase.database()

#parsing arguments to take command line values
ap = argparse.ArgumentParser()

#output to a csv file all the informations scanned
ap.add_argument("-o", "--output", type = str, default="barcodes.csv", help = "path to output CSV file containing barcodes")
args = vars(ap.parse_args())

#indication of stram starting
print("[INFO] starting video stream ...")

#starting videostream through webcam
vs = VideoStream(src=0).start()

#waiting time for warming up the camera, this can be eliminated
time.sleep(2.0)

#opening the csv file
csv = open(args["output"], "w")

#to keep the file unique
found = set()

# instantiate firebase format
f_format = firebase_format()

while True:
    
    #reading video stream
    frame = vs.read()

    #resizing the window
    frame = imutils.resize(frame, width = 400)
    
    #decoding the codes scanned
    codes = pyzbar.decode(frame)

    #iterating each code scanned
    for code in codes:

        #drawing a rectangle round the codes
        (x,y,w,h) = code.rect
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 0, 255), 2)

        #decoding the contents into string
        codeData = code.data.decode("utf-8")

        #type of code
        codeType = code.type

        #putting into texts
        text = "{} ({})".format(codeData, codeType)
        scanned = "Scan Complete"
        cv2.putText(frame, scanned, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

        #hecking if data found is unique or previously scanned
        if codeData not in found:
            
            #if not previously scanned then adding the data in csv
            csv.write("{}, {}\n".format(datetime.datetime.now(),codeData))
            csv.flush()
    
            #also adding into found set
            found.add(codeData)
            try:
                real_data = codeData.split('+') #key value pair of userID, authToken
                match = db.child("authentication").child(real_data[0]).get().val()

                #authentication success! open door
                if real_data[1] == match:
                    t = time.localtime()
                    logging.debug("authentication success!")
                    env_temp = sensor.get_ambient()
                    body_temp = sensor.get_object_1()
                    f_format.update_data(round(env_temp, 1), round(45+random.random(),1), 33, 37, round(body_temp, 1), 3.2)
                    current_time = time.strftime("%Y-%m-%d|%H:%M:%S", t)
                    
                    db.child("user").child(real_data[0]).child("current_data").set(f_format.return_data())
                    db.child("user").child(real_data[0]).child("past_data").child(current_time).set(f_format.return_data())
                    db.child("entrance_data").child(machine_name).child(current_time).set({real_data[0]: real_data[1]})
                    logging.debug(current_time)
                    logging.debug(real_data)
                    if body_temp < 38.0: 
                      threading.Thread(target=open_gate).start() 

            except Exception as e:
                print("invalid data {}".format(e))
                
    #showing the result
    cv2.imshow("Scanner", frame)
    key = cv2.waitKey(1) & 0xFF
    
    #quit if pressed q
    if key == ord("q"):
        break

#cleaning and closing
print("[INFO] cleaning...")
csv.close()
cv2.destroyAllWindows()
vs.stop()