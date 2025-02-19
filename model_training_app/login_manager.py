import numpy as np
import pickle
import polars as pl

from firebase_admin import firestore
from firebase_admin import auth

import predictor

db = firestore.client()

def login(email: str) -> str | None:
    """
    Logs the user in.

    Parameters
    ----------
    email : str
        The email of the user.

    Returns
    -------
    str | None
        The uid of the user if the user was logged in successfully, None otherwise.
    """
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    except Exception as e:
        print(e)
        return None

def register(email: str, password: str, data: dict[str, str]) -> str | None:
    """
    Registers the user.

    Parameters
    ----------
    email : str
        The email of the user.
    password : str
        The password of the user.
    data : dict[str, str]
        The data of the user.

    Returns
    -------
    str | None
        The uid of the user if the user was registered successfully, None otherwise.
    """
    try:
        user = auth.create_user(email=email, password=password)

        db.collection(u"users").document(user.uid).set(data)
        return user.uid
    except Exception as e:
        print(e)
        return None

def get_current_data() -> pl.DataFrame | None:
    """
    Gets the last reading of a user reading from the database.

    Returns
    -------
    polars.DataFrame | None
        The last reading from the database if there's one, None otherwise.
    """
    label, data = predictor.get_current_data()
    if label != "Not Sitting":
        return data
    else:
        return None

def recategorize_y(y_vec: np.ndarray[str]) -> np.ndarray[str]:
    """
    Recategorizes the labels.

    Parameters
    ----------
    y_vec : numpy.ndarray
        The labels to recategorize.

    Returns
    -------
    numpy.ndarray[str]
        The recategorized labels.
    """
    result = y_vec.copy()
    result[y_vec == "0"] = "Not Sitting"
    result[y_vec == "1"] = "Sitting Correctly"
    result[y_vec == "2"] = "Sitting Correctly"
    result[y_vec == "12"] = "Sitting Correctly"
    result[y_vec == "3"] = "Leaning Forward"
    result[y_vec == "6"] = "Leaning Forward"
    result[y_vec == "7"] = "Leaning Backward"
    result[y_vec == "4"] = "Unbalanced"
    result[y_vec == "5"] = "Unbalanced"
    result[y_vec == "8"] = "Unbalanced"
    result[y_vec == "9"] = "Unbalanced"
    result[y_vec == "10"] = "Unbalanced"
    result[y_vec == "11"] = "Unbalanced"

    return result

def train_model(data: pl.DataFrame, labels: pl.DataFrame, email: str) -> bool:
    """
    Trains the model.

    Parameters
    ----------
    data : polars.DataFrame
        The data to train the model with.
    labels : polars.DataFrame
        The labels to train the model with.
    email : str
        The email of the user.

    Returns
    -------
    bool
        True if the model was trained successfully, False otherwise.
    """
    model = predictor.get_model()

    try:
        user = auth.get_user_by_email(email)
        user_id = user.uid

        print(recategorize_y(labels.to_numpy()))

        model.fit(data.to_numpy(), recategorize_y(labels.to_numpy()))
        with open(f"model_training_app/models/model_{user_id}.pkl", "wb") as f:
            pickle.dump(model, f)

        return True
    except Exception as e:

        print(e)
        return False
