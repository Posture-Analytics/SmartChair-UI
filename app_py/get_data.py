# import the firebase_admin module
import firebase_admin
from firebase_admin import credentials

# check if the app has already been initialized
if not firebase_admin._apps:
    # initialize the Firebase app
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://friendly-bazaar-334818-default-rtdb.firebaseio.com'})

# create a reference to the Firebase Realtime Database
from firebase_admin import db

root_ref = db.reference('sensor_readings_NEW_STRUCTURE')

# ex P2224;2073;0;198;1478;1062;270;277;553;350;221;657;"
def last_day():
    last = root_ref.order_by_key().limit_to_last(1).get()
    print(last.values())
    return list(last.values())