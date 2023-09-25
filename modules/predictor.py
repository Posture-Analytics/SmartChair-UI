import pickle
import polars as pl

from datetime import date
from typing import Any, Optional

from modules import database_manager
from modules.base_app import app, DEBUG_STATE

# ===== Load model ===== #
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# ===== Helper functions ===== #
def get_model() -> Any:
    return model

def get_current_data() -> tuple[str, pl.DataFrame]:
    """
    Gets the current posture state the data currently being sent by the sensors.
    If there's no data being sent, an empty DataFrame is returned.

    Returns
    -------
    tuple[str, polars.DataFrame]
        A tuple with the state and the data.
    """
    current_data = database_manager.get_current_data()
    if current_data.shape[0] == 0:
        state = ["Not Sitting"]
    else:
        current_data = current_data.drop("index")
        current_data_ = current_data
        current_data = current_data.rows(named=False)
        state = model.predict(current_data)

    return state[0], current_data_

def get_last_active_day_data() -> tuple[date, pl.DataFrame]:
    """
    Gets data from the last active day and predicts the posture.

    Returns
    -------
    tuple[datetime.date, polars.DataFrame]
        A tuple with the date and the DataFrame.
    """
    day, data = database_manager.get_last_active_day_data()

    data_ = data
    data = data.drop("index")
    data = data.rows(named=False)
    state = model.predict(data)
    return day, state, data_

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
