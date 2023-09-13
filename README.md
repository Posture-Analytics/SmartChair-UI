# SmartChair-UI
User interface for SmartChair project, building with Dash, Plotly and Polars.

## Description
This project is a web application that allows the user to visualize the data collected by the sensors in the chair. There are features for visualizing a general analysis of the data from previous days, for real time data visualization and for visualizing and downloading the data from a specific day. 

## Runnning the app
To run the app, you need to install the dependencies first. You can do this by running the following command in the root directory of the project:
```bash
pip install -r requirements.txt
```
After installing the dependencies, you can run the app by running the following command in the root directory of the project:
```bash
python app.py
```
The app will be running on the address especified in the terminal.

## Other Apps

### Running the data sender

***Description:*** *The data sender is a script that simulates the data sent by the sensors. It sends the data to the server using the same protocol as the sensors. The data sender is useful for testing the app without access to the chair.*

The dependencies are the same as the app, so you are ready to run the data sender if you have already installed the dependencies. To run the data sender, you can run the following command in the main directory:
```bash
python data_sender/data_sender.py
```

### Running the model training app

***Description:*** *The model training app is an application that allows the user to train a model based on his sitting behavior. This is app is being used to allow for findings regarding the best model to be used for predictions, particularly if there should be a generalized model or fine-tuned models for each user.*

The dependencies are the same as the app, so you are ready to run the model training app if you have already installed the dependencies. To run the model training app, you can run the following command in the main directory:
```bash
python model_training_app/app.py
```
