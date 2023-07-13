import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime, timedelta, date, time
import polars as pl

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://friendly-bazaar-334818-default-rtdb.firebaseio.com'})

root_ref = db.reference('/sensor_readings/')

def ord_dict_to_df(data: dict) -> pl.DataFrame:
    """
    Converts a dictionary of dictionaries to a DataFrame.

    Parameters
    ----------
        data : dict
            The dictionary of dictionaries.
    Returns
    -------
        A DataFrame.
    """
    # convert the keys to datetime objects
    index = [datetime.fromtimestamp(float(key.replace('_', '.'))) for key in data.keys()]
    # convert the data to a DataFrame, but it doesn't accept the dtype int in the constructor, for some reason
    schema = {f'p{i:02}': pl.Int32 for i in range(12)}
    result = pl.DataFrame(list(data.values()), schema=schema).with_columns([
        pl.Series(name="index", values=index),
    ])
    # convert the DataFrame elements to integers no greater than 4096
    predicate = pl.all(pl.all().exclude("index") < 4096)
    return result.filter(predicate)

def get_data_from_day(day: str) -> pl.DataFrame:
    """
    Gets the data from a specific day.
    
    Parameters
    ----------
        day : date
            The day to get the data from.
    Returns
    -------
        A DataFrame.
    """

    result = root_ref.child(day).get()
    data = ord_dict_to_df(result)

    return data