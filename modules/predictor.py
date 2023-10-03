import numpy as np
import pickle
import polars as pl

from time import time
from datetime import date
from sklearn.ensemble import RandomForestClassifier
from typing import Any, Optional

from modules import database_manager

# ===== Cache variables ===== #
polling_interval = 0.5
last_read: float = 0.0
last_data = pl.DataFrame()
last_state = "Not Sitting"

# ===== Load model ===== #
with open("model.pkl", "rb") as f:
    model: RandomForestClassifier = pickle.load(f)

# ===== Helper functions ===== #
def get_model() -> Any:
    return model

def set_data_polling_interval(interval: float) -> None:
    """
    Sets the minimum time to wait before polling the data from the database.

    Parameters
    ----------
    interval : float
        The interval in seconds.
    """
    global polling_interval
    polling_interval = interval

def get_current_data() -> tuple[str, pl.DataFrame]:
    """
    Gets the current posture state the data currently being sent by the sensors.
    If there's no data being sent, an empty DataFrame is returned.

    Returns
    -------
    tuple[str, polars.DataFrame]
        A tuple with the state and the data.
    """
    global last_read, last_data, last_state, polling_interval
    now = time()
    if now - last_read >= polling_interval:
        last_read = now
        current_data = database_manager.get_current_data()
        if current_data.shape[0] == 0:
            state = ["Not Sitting"]
        else:
            state = model.predict(
                current_data.drop("index").rows(named=False)
            )

        last_state = state[0]
        last_data = current_data

    return last_state, last_data

def get_last_active_day_data() -> tuple[date, np.ndarray, pl.DataFrame]:
    """
    Gets data from the last active day and predicts the posture.

    Returns
    -------
    tuple[datetime.date, numpy.ndarray[str], polars.DataFrame]
        A tuple with the date, the predicted states and the DataFrame.
    """
    day, data = database_manager.get_last_active_day_data()

    values = data.drop("index").rows(named=False)
    states = model.predict(values)
    return day, states, data

def filter_outliers(df: pl.DataFrame, window_size: Optional[int] = 3,
                    threshold: Optional[float] = 1000.0) -> pl.DataFrame:
    """
    Filter outliers from a DataFrame by checking the deviation in consecutive values.

    Parameters
    ----------
    df : polars.DataFrame
        DataFrame to filter.
    window_size : int, optional
        Size of the window to check for outliers, by default 3.
    threshold : float, optional
        Threshold for the deviation, by default 1000.0.

    Returns
    -------
    polars.DataFrame
        Filtered DataFrame.
    """
    standard_deviations = []

    for j in range(df.shape[1] - 1):
        standard_deviations.append(df[:, j].rolling_std(window_size))

    variations = pl.DataFrame(standard_deviations).sum(axis=1)
    # The rolling std considers the previous row for the value of a given row,
    # so the first ones are null and thus calculated separately
    for i in range(window_size - 1):
        # Gets the rows following i and excludes the index
        variations[i] = df[i : i + window_size - 1, :-1].std().sum(axis=1)

    return df.filter(variations < threshold)
