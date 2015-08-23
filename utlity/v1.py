from flask import Blueprint, request, jsonify
from utlity import mongo, snmp

api_v1 = Blueprint('v1', __name__)

api_function = [
    {
        "url":"/",
        "method":"get",
        "desc":"返回可用函数列表"
    },
]

# /，返回所有可用API
@api_v1.route('/',  methods = ['GET'])
def index():
    return jsonify({'data':api_function, 'res':0})

######################
# Devices
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

######################
# Ports
######################

# /ports，返回所有 port 列表
@api_v1.route('/ports', methods = ['GET'])
@api_v1.route('/ports/<port_id>', methods = ['GET'])
def get_ports(port_id=None):
    dev_id = request.values.get('dev_id')
    if dev_id is None:
        return jsonify({'err': 'need device id', 'res': 1})

    port_res = mongo.get_ports(dev_id, port_id)
    return jsonify(port_res)

# /ports，返回所有 port 列表
@api_v1.route('/ports', methods = ['PUT'])
def update_ports():
    dev_id = request.values.get('dev_id')
    if dev_id is None:
        return jsonify({'err': 'need device id', 'res': 1})

    port_res = mongo.update_ports(dev_id)
    return jsonify(port_res)

######################
# Bills
######################
@api_v1.route('/bills/devices', methods = ['GET'])
@api_v1.route('/bills/devices/<devices_id>', methods = ['GET'])
def get_bills_devices(devices_id=None):
    month = request.values.get('month')
    bill_res = mongo.get_bills_devices(devices_id, month)
    return jsonify(bill_res)

######################
# Snmp
######################

# /snmp/devices，返回所有 devices 列表
@api_v1.route('/snmp/devices', methods = ['GET'])
def get_snmp_devices():
    device_ip = request.values.get('ip')
    device_community = request.values.get('community', 'public')

    if device_ip:
        sys_info = snmp.get_snmp_device(device_ip, device_community)
    else:
        return jsonify({'data': 'params error', 'res': 2})

    if sys_info:
        return jsonify({'data': sys_info, 'res': 0})
    else:
        return jsonify({'data': 'cannot get snmp message', 'res': 1})


# /snmp/ports，返回所有 devices 列表
@api_v1.route('/snmp/ports', methods = ['GET'])
def get_snmp_ports():
    device_ip = request.values.get('ip')
    device_community = request.values.get('community', 'public')

    if device_ip:
        port_info = snmp.get_snmp_port(device_ip, device_community)
    else:
        return jsonify({'data': 'params error', 'res': 2})

    if port_info:
        return jsonify({'data': port_info, 'res': 0})
    else:
        return jsonify({'data': 'cannot get snmp message', 'res': 1})


@api_v1.route('/snmp/flow', methods = ['GET'])
def get_snmp_flow():
    dev_id = request.values.get('dev_id')
    ifIndex = request.values.get('ifIndex')

    if dev_id is None or ifIndex is None:
        return jsonify({'err': 'params error', 'res': 2})

    device_info = mongo.get_devices(dev_id, community_flag=True)

    if device_info is None:
        return jsonify({'err': 'cannot find device', 'res': 1})

    device_info = device_info['data']

    flow_res = snmp.get_snmp_flow(device_info['snmp_ip'], device_info['snmp_community'],ifIndex)

    if flow_res:
        return jsonify({'data': flow_res, 'res': 0})
    else:
        return jsonify({'data': 'cannot get snmp flow data', 'res': 1})