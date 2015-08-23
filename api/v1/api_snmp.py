from flask import request, jsonify
from utlity import mongo, snmp
from api.v1 import api_v1

######################
# /snmp
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
