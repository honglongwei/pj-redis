import json
import os

def get_settings():
    return json.load(open(os.path.abspath('.')+ "/redis_live.conf"))

def get_redis_servers():
    config = get_settings()
    servers= config["RedisServers"]
    data=[]
    for server in servers:
        server['ep']='%(server)s:%(port)d' % server
        if(server.get('group')==None or server.get('group')==''):
            server['group']='ungrouped'
        if(server.get('instance')==None or server.get('instance')==''):
            server['instance']=(str)(server['port'])
        data.append(server)
    return data

def get_redis_alerturi():
    config = get_settings()
    return config["sms_alert"]

def get_redis_stats_server():
    config = get_settings()
    return config["RedisStatsServer"]

def get_data_store_type():
    config = get_settings()
    return config["DataStoreType"]

def get_master_slave_sms_type():
    config = get_settings()
    return config['master_slave_sms']

def save_settings(redisServers,smsType):
    config = get_settings()
    config["RedisServers"]= redisServers;
    config['master_slave_sms']=smsType;
    
    data = json.dumps(config)
    data = data.replace('}', '}\r\n')
    output = open(os.path.abspath('.') + "/redis_live.conf", "w")
    output.truncate()
    output.write(data)
    output.close()
