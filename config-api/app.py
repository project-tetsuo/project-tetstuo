from flask import Flask, jsonify, request, redirect
from flasgger import Swagger
from flasgger.utils import swag_from, validate
from jsonschema import ValidationError
import json
from pathlib import Path
import requests
import os
import subprocess
import time
import logging


app = Flask(__name__)
swagger = Swagger(app)

@app.route ('/')
def root():
    return redirect("/apidocs", code=302)
@app.route('/app', methods=['GET', 'POST', 'DELETE'])
@swag_from('app.yml')
def config():
    result_data = request.get_data()
    method = request.method
    print(result_data)
    print(method)

    if method == 'GET':
      print("received get")
      # perform get of unit config
      # list out apps and ports 
      message = {"message": "GET RECEIVED"}
      return jsonify(message)
    if method == 'DELETE':
      print("received delete")
      # send delete for listener then the app
      # get all listeners and search for app 
      
      message = {"message": "DELETE RECEIVED"}
      return jsonify(message)
    data = request.get_json(force=True)
    name = data['name']
    port = data['port']
    w_dir = data['directory']

    f = open('unit-configs/foo')

    data = json.load(f)

    logging.basicConfig(filename='/tmp/tetsuo.log', encoding='utf-8', level=logging.DEBUG)

    data['applications'][name] = data['applications'].pop('node')
    data['listeners']={ "*:" + port : { "pass": "applications/" + name} }
    data['applications'][name]['working_directory']=w_dir
    logging.info("**************************************")
    logging.info(data['listeners'])
    logging.info(data['applications'][name]['working_directory'])
    logging.info(data)
    isExist = os.path.exists(w_dir)
    if isExist == False:
      print(isExist)
      message = {"ERROR": "Directory does not exist"}
      return jsonify(message)
    else:
      result = subprocess.run(['/usr/bin/npm', 'install'], capture_output=True, cwd=w_dir)
      logging.info(result)
      unit_module = subprocess.run(['/usr/bin/npm', 'install', 'unit-http'], capture_output=True, cwd=w_dir)
      logging.info(unit_module)

    # update the application component
    url = "http://127.0.0.1:8888/config/applications/" + name
    app_r = requests.put(url, json=data['applications'][name])
    logging.info(app_r.text)
    #time.sleep(15)

    # update the listener
    url = "http://127.0.0.1:8888/config/listeners/" + "*:" + port
    logging.info(url)
    listener_r = requests.put(url, json=data['listeners']['*:' + port])
    logging.info(listener_r.text)
    #return (app_r.content, listener_r.content)
    return (app_r.content)

@app.route('/info', methods=['GET'])
@swag_from('info.yml')
def info():
    msg = 'Tetsuo application deployment API'
    api_ver = '1.0'

    return jsonify(status=msg, version=api_ver)

if __name__ == "__main__":
  app.run(host='0.0.0.0')

