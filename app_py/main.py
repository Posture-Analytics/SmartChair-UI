from flask import Flask, send_from_directory, json, jsonify

from get_data import *

app = Flask(__name__, static_folder="public")

@app.route("/")
def index():
    # Retorna o arquivo index.html da pasta public
    return send_from_directory("public", "index.html")

@app.route("/<path:path>")
def static_file(path):
    # Retorna qualquer outro arquivo estático da pasta public
    return app.send_static_file(path)

@app.route("/data")
def data():
    # obter os dados da consulta
    data = last_day()
    # converter os dados em JSON
    data_json = jsonify(data)
    # retornar os dados em JSON como resposta
    return data_json


if __name__ == "__main__":
    app.run(debug=True)
