import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime, timedelta, date, time
import polars as pl

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(cred, {'databaseURL': 'https://friendly-bazaar-334818-default-rtdb.firebaseio.com'})

root_ref = db.reference('/sensor_readings_NEW_STRUCTURE/')

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
    if result is None:
        return pl.DataFrame()
    data = ord_dict_to_df(result)

    return data

def get_current_data() -> pl.DataFrame:
    """
    Gets the data currently being sent by the sensors.
    If there's no data being sent, it returns an empty DataFrame.
    
    Returns
    -------
        An one-row DataFrame.
    """
    today_data = get_data_from_day(date.today().strftime("%Y-%m-%d"))
    if today_data.shape[0] == 0:
        return pl.DataFrame()
    else:
        today_data = today_data.sort("index").reverse()
        actual_time = datetime.now()
        # the sensors take around 500ms to send the data, so 2 seconds is a safe threshold
        threshold = timedelta(seconds=2)  
        if actual_time - today_data["index"][0] < threshold:
            return today_data.head(1)
        else:
            return pl.DataFrame()

def get_last_active_day_data() -> tuple[date, pl.DataFrame]:
    """
    Gets the data from the last day that has data.
    If there's no data, it returns an empty DataFrame.
    
    Returns
    -------
        A tuple with the date and the DataFrame.
    """
    day = date.today()
    day_data = get_data_from_day(day.strftime("%Y-%m-%d"))
    # keep going back until it finds a day with data
    while day_data.shape[0] == 0:
        day -= timedelta(days=1)
        day_data = get_data_from_day(day.strftime("%Y-%m-%d"))
    return day, day_data
