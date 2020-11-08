from datetime import datetime
from firebase_format import firebase_format
import time
import threading
import logging
import pyrebase
import random

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
#time to log in seconds(default: 1log/60s)
interval = 60.0

def main():
  logging.basicConfig(
    level=logging.DEBUG, 
    format='%(relativeCreated)6d %(threadName)s %(message)s'
  )

  start_time = time.time()

  #initialize firebase & get reference of firebase db
  firebase = pyrebase.initialize_app(config)
  db = firebase.database()
  logging.debug('initialize db success')

  #initalize firebase_format object
  f_format = firebase_format()

  while (True):

    """
    update_data() values by argument order:
    env_temp|fine_dust|humidity|lactation|sound|temperature|weight
    """
    f_format.update_data(round(25.5+random.random(), 1), round(45+random.random(),1), 33, 37, 36.5, 3.2)

    t = time.localtime()
    current_time = time.strftime("%Y-%m-%d|%H:%M:%S", t)
    db.child("user_1").child("current_data").set(f_format.return_data())
    db.child("user_1").child("past_data").child(current_time).set(f_format.return_data())
    logging.debug(current_time)
    time.sleep(interval - ((time.time() - start_time) % interval))

  logging.debug('exiting firebase')

if __name__ == '__main__':
    main()