from flask import Flask, send_from_directory, json, jsonify, request, render_template,request, redirect, flash
import json
from get_data import *


app = Flask(__name__, static_folder="public")
with open('secret.json') as config_file:
    config = json.load(config_file)
app.config['SECRET_KEY'] = config['SECRET_KEY']

@app.route("/")
def index():
    # Retorna o arquivo index.html da pasta public
    return send_from_directory("public", "index.html")

@app.route("/<path:path>")
def static_file(path):
    print(path)
    # Retorna qualquer outro arquivo estático da pasta public
    return app.send_static_file(path)

@app.route("/data")
def data():
    # obter os dados da consulta
    data = get_data_from_day("2023-10-31")
    # converter os dados em JSON
    data_json = jsonify(data)
    # retornar os dados em JSON como resposta
    return data_json

@app.route("/admin")
def admin():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login():
    
    name = request.form.get('username')
    password = request.form.get('password')

    if name == config['ADMIN_USER'] and password == config['ADMIN_PASSWORD']:
        return render_template('submit.html')
    else:
        flash('Login Unsuccessful. Please check username and password')
        return redirect('/admin')
    
@app.route('/submit',methods=['POST'])
def submit():
    print('submit')
    name = request.form.get('name')
    birth = request.form.get('birthdate')
    height = request.form.get('height')
    weight = request.form.get('weight')
    
    print(name, birth, height, weight)
    return redirect('/admin')


if __name__ == "__main__":
    app.run(debug=True)
