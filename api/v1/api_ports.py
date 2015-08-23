from flask import request, jsonify
from utlity import mongo
from api.v1 import api_v1

######################
# /ports
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