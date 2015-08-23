from flask import Blueprint, jsonify

# 定义 api_v1
api_v1 = Blueprint('v1', __name__)

# 引入 api_v1 的注册路径
from api.v1 import api_devices, api_ports, api_snmp, api_bills

# 注册函数列表
api_function = [
    {
        "url":"/",
        "method":"get",
        "desc":"返回可用函数列表"
    },
]

# 返回所有可用API
@api_v1.route('/',  methods = ['GET'])
def index():
    return jsonify({'data':api_function, 'res':0})