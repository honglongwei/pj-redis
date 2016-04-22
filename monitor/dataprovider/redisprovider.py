from api.util import settings
from datetime import datetime, timedelta
import redis
import json
import ast
import time
import struct

def datetime2_unix_int(timestamp):
    return (int)(time.mktime(timestamp.timetuple()))

class RedisStatsProvider(object):
    def __init__(self):
        stats_server = settings.get_redis_stats_server()
        self.server = stats_server["server"]
        self.port = stats_server["port"]
        self.conn = redis.StrictRedis(host=self.server, port=self.port, db=0)

    def save_keys_Info(self, server,rediskey,timestamp, expires, persists,expired,evicted
                     ,hit_rate,commands,used,peak):
        score=datetime2_unix_int(timestamp)
        data=struct.pack('iiiiiiiqq',
                         score,
                         commands,
                         expires,
                         persists,
                         expired,
                         evicted,
                         hit_rate,
                         peak,
                         used)
        self.conn.zadd(server +':'+ rediskey, score, data)
            
    def get_keys_info(self, server, from_date, to_date):
        data = []
        start = datetime2_unix_int(from_date)
        end = datetime2_unix_int(to_date)
        key=server + ":info"
        if(end-start>=3600*2):
            key=key+"_hours"
        rows = self.conn.zrangebyscore(key, start, end)

        rate=1
        if(len(rows)> 400):
            rate=len(rows)/300
            
        index=0
        for row in rows:
            index+=1
            if(index%rate==0):
                row=struct.unpack('iiiiiiiqq',row)
                timestamp = datetime.fromtimestamp(int(row[0]))
                item=list(row)
                item[0]=tuple(timestamp.timetuple())[:-2]
               
                data.append(item)
        return data
        
    def save_status_info(self, server, timestamp, data):
        timestamp=datetime2_unix_int(timestamp)
        data['timestamp']=timestamp
        self.conn.zadd(server + ":status", timestamp, json.dumps(data))

    def get_status_info(self, server, from_date, to_date):
        data = []
        start = datetime2_unix_int(from_date)
        end = datetime2_unix_int(to_date)
        rows = self.conn.zrangebyscore(server + ":status", start, end)
        for row in rows:
            row = ast.literal_eval(row)
            timestamp = datetime.fromtimestamp(int(row['timestamp']))
            data.append([tuple(timestamp.timetuple())[:-2], row])
        return data
    
    def delete_history(self,server,timestamp):
        begin=0
        end = datetime2_unix_int(timestamp)
        self.conn.zremrangebyscore(server + ":info", begin, end)
        self.conn.zremrangebyscore(server + ":info_hours", begin, end-(3600*24*7))
        # status for more then 3 month
        self.conn.zremrangebyscore(server + ":status", begin, end - (3600*24*90))

    def collection_database(self):
        self.conn.bgrewriteaof()