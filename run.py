#!/home/jyyl/env/flask/bin/python3
#coding: utf-8

from api import app

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001)