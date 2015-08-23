#coding: utf-8
from flask import Flask
from api.v1 import api_v1

# Init flask app
app = Flask(__name__)

# Init app blueprint
app.register_blueprint(api_v1,url_prefix="/v1")
