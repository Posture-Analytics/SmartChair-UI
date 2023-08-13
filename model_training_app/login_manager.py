import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://friendly-bazaar-334818-default-rtdb.firebaseio.com'})

db = firestore.client()

def login(email, password):
    """
    Logs the user in.
    
    Parameters
    ----------
        email : str
            The email of the user.
        password : str
            The password of the user.
    Returns
    -------
        True if the user was logged in successfully, False otherwise.
    """
    try:
        user = auth.get_user_by_email(email)
        uid = user.uid
        return uid
    except Exception as e:
        print(e)
        return False
    return True

def register(email, password, data):
    """
    Registers the user.
    
    Parameters
    ----------
        email : str
            The email of the user.
        password : str
            The password of the user.
    Returns
    -------
        True if the user was registered successfully, False otherwise.
    """
    try:
        user = auth.create_user(email=email, password=password)

        db.collection(u'users').document(user.uid).set(data)
        return user.uid
    except Exception as e:
        print(e)
        return False
    return True
