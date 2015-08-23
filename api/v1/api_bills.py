from flask import request, jsonify
from utlity import mongo
from api.v1 import api_v1

######################
# /bills
######################

@api_v1.route('/bills/devices', methods = ['GET'])
@api_v1.route('/bills/devices/<devices_id>', methods = ['GET'])
def get_bills_devices(devices_id=None):
    month = request.values.get('month')
    bill_res = mongo.get_bills_devices(devices_id, month)
    return jsonify(bill_res)