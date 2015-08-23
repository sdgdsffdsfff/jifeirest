from pymongo import MongoClient
from bson.objectid import ObjectId
from time import time
import config
import logging
from utlity import snmp

try:
    mongo_client = MongoClient(config.mongo_server_ip, config.mongo_server_port)
    mongo_common = mongo_client[config.mongo_db_common]
except:
    logging.error("cannot connect to mongodb %s" % config.mongo_db_common)
    exit(1)

def trans_id(item, format):
    if '_id' not in item:
        return None

    if format == 'db':
        item['_id'] = ObjectId(item['_id'])
    else:
        item['_id'] = str(item['_id'])

    return item

######################
# Devices
######################

def add_devices(dev_args):
    # 设备列表
    mongo_devices = mongo_common['devices']

    # 端口列表
    mongo_ports = mongo_common['ports']

    # 查找是否已有该设备
    mongo_key = {'snmp_ip':dev_args['snmp_ip'],
                 'snmp_community':dev_args['snmp_community'],
                 'dev_owner': dev_args['dev_owner']}
    dev_res = mongo_devices.find_one(mongo_key)

    # 对于已经有的设备，直接返回
    if dev_res:
        return {'err': 'db already have this device', 'res': 2}

    # 读取新增设备的 SNMP 信息
    port_list = snmp.get_snmp_port(dev_args['snmp_ip'], dev_args['snmp_community'])

    if port_list is None:
        return {'err': 'get device snmp info error', 'res': 2}

    # 新增设备写入数据库
    try:
        dev_insert_res = mongo_devices.insert_one({
            'snmp_ip': dev_args['snmp_ip'],
            'snmp_community': dev_args['snmp_community'],
            'snmp_port': int(dev_args['snmp_port']),
            'dev_owner': dev_args['dev_owner'],
            'dev_group': dev_args['dev_group'],
            'sys_name': dev_args['sys_name'],
            'sys_desc': dev_args['sys_desc'],
            'update_time': int(time())
        })

        mongo_ports.insert_one({
            'dev_id': str(dev_insert_res.inserted_id),
            'port_list': port_list
        })
    except:
        return {'err': 'db insert error', 'res': 1}

    return {'data': 'insert success', 'res': 0}

def get_devices(device_id=0, community_flag=False):
    # 实际的 SNMP 设备列表
    mongo_devices = mongo_common['devices']

    if device_id:
        try:
            if community_flag:
                device_res = mongo_devices.find_one({'_id':ObjectId(device_id)})
            else:
                device_res = mongo_devices.find_one({'_id':ObjectId(device_id)}, {'snmp_community':0})

            device_data = trans_id(device_res,'json')
            return {'data': device_data, 'res': 0}
        except:
            return {'err': 'device list is empty', 'res': 1}
    else:
        try:
            device_res = mongo_devices.find({},{'snmp_community':0})
            device_data = [trans_id(device,'json') for device in list(device_res)]
            return {'data': device_data, 'res': 0}
        except:
            return {'err': 'device list is empty', 'res': 1}

def update_device(dev_id, dev_args):
    # 设备列表
    mongo_devices = mongo_common['devices']

    # 端口列表
    mongo_ports = mongo_common['ports']

    # 查找是否已有该设备
    dev_res = mongo_devices.find_one({'_id': ObjectId(dev_id)})

    # 没有相应设备，直接返回
    if dev_res is None:
        return {'err': 'db have no device', 'res': 2}

    # 读取新增设备的 SNMP 信息
    if 'snmp_community' in dev_args and dev_args['snmp_community']:
        new_community = dev_args['snmp_community']
    else:
        new_community = dev_res['snmp_community']

        # 读取新增设备的 SNMP 信息
    if 'snmp_port' in dev_args and dev_args['snmp_port']:
        new_port = dev_args['snmp_port']
    else:
        new_port = dev_res['snmp_port']

    port_list = snmp.get_snmp_port(dev_args['snmp_ip'], new_community)

    if port_list is None:
        return {'err': 'update device snmp info error', 'res': 3}

    # 新增设备写入数据库
    update_data = {
        'snmp_ip': dev_args['snmp_ip'],
        'snmp_community': new_community,
        'snmp_port': int(new_port),
        'dev_owner': dev_args['dev_owner'],
        'dev_group': dev_args['dev_group'],
        'sys_name': dev_args['sys_name'],
        'sys_desc': dev_args['sys_desc'],
        'update_time': int(time())
    }
    write_data = {"$set": update_data}

    try:
        # 更新 Devices
        mongo_devices.update_one({'_id': ObjectId(dev_id)}, write_data)

        # 更新 Ports
        mongo_ports.update_one({'dev_id': dev_id}, {
            "$set":{'port_list': port_list}
        }, upsert=True)
    except:
        return {'err': 'db update error', 'res': 1}

    return {'data': 'update success', 'res': 0}

def delete_device(dev_id):
    # 设备列表
    mongo_devices = mongo_common['devices']

    # 端口列表
    mongo_ports = mongo_common['ports']

    # 查找是否已有该设备
    dev_res = mongo_devices.find_one({'_id': ObjectId(dev_id)})

    # 没有相应设备，直接返回
    if dev_res is None:
        return {'err': 'device already deleted', 'res': 2}

    try:
        # 更新 Devices
        mongo_devices.delete_one({'_id': ObjectId(dev_id)})
        mongo_ports.delete_one({'dev_id': dev_id})

    except:
        return {'err': 'db delete error', 'res': 1}

    return {'data': 'delete success', 'res': 0}

######################
# Ports
######################

def get_ports(dev_id, port_id = 0):
    # 实际的 SNMP 设备列表
    mongo_ports = mongo_common['ports']
    port_res = mongo_ports.find_one({'dev_id':dev_id}, {'_id':0})

    if port_res is None or 'port_list' not in port_res:
        return {'err': 'db is empty', 'res': 1}

    port_list = port_res['port_list']

    if port_id:
        for port in port_list:
            if int(port['ifIndex']) == int(port_id):
                return {'data': port, 'res': 0}

        return {'err': 'port index is error', 'res': 2}

    else:
        return {'data': port_list, 'res': 0}

def update_ports(dev_id):
    # 设备列表
    mongo_devices = mongo_common['devices']

    # 端口列表
    mongo_ports = mongo_common['ports']

    mongo_res = mongo_devices.find_one({'_id':ObjectId(dev_id)})
    port_res = mongo_ports.find_one({'dev_id':dev_id})

    if mongo_res is None or port_res is None:
        return {'err': 'port db is empty', 'res': 2}

    port_list = port_list = snmp.get_snmp_port(mongo_res['snmp_ip'], mongo_res['snmp_community'])

    if port_list is None:
        return {'err': 'update port snmp error', 'res': 3}

    try:
        # 更新 Ports
        mongo_ports.update_one({'dev_id': dev_id}, {
            "$set":{'port_list': port_list}
        }, upsert=True)
    except:
        return {'err': 'port db update error', 'res': 1}

    return {'data': 'update port success', 'res': 0}

######################
# Bills
######################

def get_bills_devices(dev_id = None, month = None):
    if dev_id is None and month is None:
        all_bill_collection = mongo_common.collection_names()
        print(all_bill_collection)

    return {'res':0}