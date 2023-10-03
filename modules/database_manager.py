import firebase_admin
import polars as pl

from datetime import datetime, timedelta, date, time
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin = firebase_admin.initialize_app(
    cred, options={
        "databaseURL": "https://friendly-bazaar-334818-default-rtdb.firebaseio.com"
    }
)

# The DataFrame doesn't accept the dtype int in the constructor, for some reason
schema = {f"p{i:02}": pl.Int32 for i in range(12)}

root_ref = db.reference("/yet_another_test/")

def get_list_of_days() -> list[str]:
    """
    Gets the list of days that have data.

    Returns
    -------
        A list of strings with the dates.
    """
    return list(root_ref.get(shallow=True).keys())

def ordered_dict_to_df(data: dict) -> pl.DataFrame:
    """
    Converts a dictionary of dictionaries to a DataFrame.

    Parameters
    ----------
    data : dict
        The dictionary of dictionaries.

    Returns
    -------
    polars.DataFrame
    """
    global schema
    # Convert the integer keys to the unix time (seconds), then datetime objects
    index = [datetime.fromtimestamp(float(key) / 1000) for key in data.keys()]
    # Convert the data to a DataFrame
    result = pl.DataFrame(list(data.values()), schema=schema).with_columns([
        pl.Series(name="index", values=index),
    ])
    # Drop the rows with pressure values above 4095
    predicate = pl.all(pl.all().exclude("index") < 4096)
    return result.filter(predicate)

def get_data_from_day(day: str) -> pl.DataFrame:
    """
    Gets the data from a specific day.

    Parameters
    ----------
    day : date
        The day whose data will be retrieved.

    Returns
    -------
    polars.DataFrame
        A DataFrame with the data from the given day.
    """

    result = root_ref.child(day).get()
    if result is None:
        return pl.DataFrame()
    data = ordered_dict_to_df(result)

    return data

def get_current_data() -> pl.DataFrame:
    """
    Gets the data currently being sent by the sensors.
    If there's no data being sent, an empty DataFrame is returned.

    Returns
    -------
    polars.DataFrame
        A one-row DataFrame.
    """
    result = root_ref.child(str(date.today())).order_by_key().limit_to_last(1).get()
    if result is None:
        return pl.DataFrame()
    df = ordered_dict_to_df(result)
    # A safe threshold of slightly over two times the data sending interval
    if datetime.now() - df[0, "index"] >= timedelta(seconds=1.05):
        return pl.DataFrame()
    return df

def get_last_active_day_data() -> tuple[date, pl.DataFrame]:
    """
    Gets the data from the last day that has data.
    If there's no data, an empty DataFrame is returned.

    Returns
    -------
    datetime.date, polars.DataFrame
        A tuple with the date and the DataFrame.
    """
    result = root_ref.order_by_key().limit_to_last(1).get()
    if result is None:
        return date.today(), pl.DataFrame()
    day = list(result.keys())[0]
    return date.fromisoformat(day), ordered_dict_to_df(result[day])
