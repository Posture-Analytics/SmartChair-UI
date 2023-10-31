# import the firebase_admin module
import firebase_admin
from firebase_admin import credentials
import base64_decoder as b64d

# check if the app has already been initialized
if not firebase_admin._apps:
    # initialize the Firebase app
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://friendly-bazaar-334818-default-rtdb.firebaseio.com'})

# create a reference to the Firebase Realtime Database
from firebase_admin import db

# create a reference to the path that contains the data
root_ref = db.reference('fake_data_base64')


def get_data_from_day(day: str) -> dict:
    """
    Get the data from a specific day
    
    :param day: the day to get the data from
    :return: the data from the day
    """
    data_base64 = root_ref.child(day).get()
    data = {key: b64d.decode_base64(value) for key, value in data_base64.items()}

    return data