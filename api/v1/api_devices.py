from flask import request, jsonify
from utlity import mongo
from api.v1 import api_v1

######################
# /devices
######################

# /devices，返回所有 device 列表
@api_v1.route('/devices', methods = ['GET'])
@api_v1.route('/devices/<device_id>', methods = ['GET'])
def get_devices(device_id=None):
    device_res = mongo.get_devices(device_id)
    return jsonify(device_res)

@api_v1.route('/devices', methods = ['POST'])
def add_devices():
    args_dict = {}

    args_dict["snmp_ip"] = request.values.get('snmp_ip')
    args_dict["snmp_community"] = request.values.get('snmp_community', 'public')
    args_dict["snmp_port"] = request.values.get('snmp_port', '161')
    args_dict["dev_owner"] = request.values.get('dev_owner')
    args_dict["dev_group"] = request.values.get('dev_group')
    args_dict["sys_name"] = request.values.get('sys_name', '')
    args_dict["sys_desc"] = request.values.get('sys_desc', '')

    if args_dict["snmp_ip"] is None or args_dict['dev_owner'] is None or args_dict['dev_group'] is None:
        return jsonify({'err': 'device params error', 'res': 1})

    add_res = mongo.add_devices(args_dict)
    return jsonify(add_res)

@api_v1.route('/devices/<device_id>', methods = ['PUT'])
def update_devices(device_id=None):
    args_dict = {}
    args_dict["snmp_ip"] = request.values.get('snmp_ip')
    args_dict["snmp_community"] = request.values.get('snmp_community')
    args_dict["snmp_port"] = request.values.get('snmp_port')
    args_dict["dev_owner"] = request.values.get('dev_owner')
    args_dict["dev_group"] = request.values.get('dev_group')
    args_dict["sys_name"] = request.values.get('sys_name')
    args_dict["sys_desc"] = request.values.get('sys_desc')

    device_res = mongo.update_device(device_id, args_dict)
    return jsonify(device_res)

@api_v1.route('/devices/<device_id>', methods = ['DELETE'])
def delete_devices(device_id=None):
    device_res = mongo.delete_device(device_id)
    return jsonify(device_res)