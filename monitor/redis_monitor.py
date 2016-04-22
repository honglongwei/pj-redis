# -*- coding: utf-8 -*-
#! /usr/bin/env python

from api.util import settings
from dataprovider.dataprovider import RedisLiveDataProvider
from threading import Timer
import redis
import datetime
import threading
import traceback
import time
import json
from daemonized import daemonized
import httplib
import urllib

class InfoItem(object):
    def __init__(self, key):
        self.expired_keys = 0
        self.evicted_keys = 0
        self.keyspace_hits = 0
        self.keyspace_misses = 0
        self.total_commands_processed = 0
        self.checkTime = datetime.datetime.now()
        self.key = key
        
    def datetime2_unix_int(self, timestamp):
        return (int)(time.mktime(timestamp.timetuple()))
    
    def gettick_sec(self, current_time):
        return self.datetime2_unix_int(current_time) - self.datetime2_unix_int(self.checkTime)
         
class InfoThread(threading.Thread):
    def __init__(self, server, port, instancename, password=None):
        threading.Thread.__init__(self)
        
        self.server = server
        self.port = port
        self.password = password
        self.instancename = instancename
        self.id = self.server + ":" + str(self.port)
        
        self._stop = threading.Event()
        self.stats_provider = None
        
        self.monitor_tick = 3  # log times every sec
        self.reserved_min = 1440 * 7  # data reserved time,1day=1440
        
        self.last = InfoItem('info')  # for every tick
        self.last2 = InfoItem('info_hours')  # for every minutes
        
        self.last_role_status = ""
        self.last_role = {}
        self.continueFaildTimes = 0
        
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()
    
    def run(self):
        self.stats_provider = RedisLiveDataProvider.get_provider()
        redis_client = redis.StrictRedis(host=self.server, port=self.port, db=0,
                                        password=self.password, socket_timeout=3)

        doitems = 0
        while not self.stopped():
            time.sleep(self.monitor_tick)
            doitems += 1
            try:
                redis_info = {}
                current_time = datetime.datetime.now()
               
                try:
                    redis_info = redis_client.info()
                except Exception:
                    self.servicedown()
                    print traceback.format_exc()
                    continue
                
                # remove history
                if(doitems % 30 == 0):
                    delta = datetime.timedelta(seconds=self.reserved_min * 60)
                    start = current_time - delta
                    self.stats_provider.delete_history(self.id, start)
                
                
                self.LogInfo(redis_info, current_time, self.last)
                
                if(self.last2.gettick_sec(current_time) >= 60):
                    self.LogInfo(redis_info, current_time, self.last2)
                
                self.CheckMasterStatus(redis_info, current_time)
                
            except Exception:
                tb = traceback.format_exc()
                print "==============================\n"
                print datetime.datetime.now()
                print tb
                print "==============================\n"
                
    def LogInfo(self, redis_info, current_time, last):
        ticksec = last.gettick_sec(current_time)
        last.checkTime = current_time;
        
        # memory
        used_memory = int(redis_info['used_memory'])
        try:
            peak_memory = int(redis_info['used_memory_peak'])
        except:
            peak_memory = used_memory
        
        # keys info
        databases = []
        for key in sorted(redis_info.keys()):
            if key.startswith("db"):
                database = redis_info[key]
                database['name'] = key
                databases.append(database)
        
        expires = 0
        persists = 0
        for database in databases:
            expires += database.get("expires")
            persists += database.get("keys") - database.get("expires")
        
        expired_keys = redis_info["expired_keys"]
        evicted_keys = redis_info["evicted_keys"]
        keyspace_hits = redis_info["keyspace_hits"]
        keyspace_misses = redis_info["keyspace_misses"]
        total_commands_processed = redis_info["total_commands_processed"]
        
        expired = 0
        evicted = 0
        if(last.expired_keys > 0 or last.evicted_keys > 0):
            expired = expired_keys - last.expired_keys
            if(expired >= 0):
                expired = (int)(expired / ticksec)
                last.expired_keys = expired_keys
            else:
                expired = 0
                last.expired_keys = 0
                
            evicted = evicted_keys - last.evicted_keys 
            if(evicted >= 0):
                evicted = (int)(evicted / ticksec)
                last.evicted_keys = evicted_keys
            else:
                evicted = 0
                last.evicted_keys = 0
        else:
            last.expired_keys = expired_keys
            last.evicted_keys = evicted_keys
        
        hit_rate = 0
        if(last.keyspace_hits > 0 or last.keyspace_misses > 0):
            hits = keyspace_hits - last.keyspace_hits
            miss = keyspace_misses - last.keyspace_misses
            if(hits >= 0 and miss >= 0):
                total = hits + miss
                if(total > 0):
                    hit_rate = (int)((hits * 100) / (hits + miss))
                    last.keyspace_hits = keyspace_hits
                    last.keyspace_misses = keyspace_misses
            else:
                last.keyspace_hits = 0
                last.keyspace_misses = 0
        else:
            last.keyspace_hits = keyspace_hits
            last.keyspace_misses = keyspace_misses
            
        commands = 0
        if(last.total_commands_processed > 0):
            commands = total_commands_processed - last.total_commands_processed 
            if(commands >= 0):
                commands = (int)(commands / ticksec)
                last.total_commands_processed = total_commands_processed
            else:
                last.total_commands_processed = 0
                commands = 0
        else:
            last.total_commands_processed = total_commands_processed
            
        self.stats_provider.save_keys_Info(self.id, last.key , current_time, expires, persists,
                               expired, evicted, hit_rate, commands, used_memory, peak_memory)
            
    def CheckMasterStatus(self, redis_info, current_time):
        role = redis_info["role"]
        role_status = {}
        
        if(role == "master"):
            connected_slaves = (int)(redis_info["connected_slaves"])
            slaves = ""
            for i in range(0, connected_slaves):
                slaves += redis_info["slave" + (str)(i)]
                
            role_status = {"role":role, "slaves":slaves}
        else:
            master_host = redis_info["master_host"]
            master_port = (str)(redis_info["master_port"])
            master_link_status = redis_info["master_link_status"]
            master_sync_in_progress = redis_info["master_sync_in_progress"]
            role_status = {"role":role,
                       "master_host_port":master_host + ":" + master_port,
                       "master_link_status":master_link_status,
                       "master_sync_in_progress":master_sync_in_progress }
        
        role_cur = json.dumps(role_status)
        if(role_cur != self.last_role_status):
            # monitor first start,not save
            if(self.last_role_status != ""):
                self.stats_provider.save_status_info(self.id, current_time, role_status)
                self.sendslavesms(role_status, self.last_role)
                
            self.last_role_status = role_cur
            self.last_role = role_status
                    
    def sendslavesms(self, current, last):
        try:
            sms_repl = 0;
            sms_stats = 0;
            try:
                sms = settings.get_master_slave_sms_type()
                sms = sms.split(',')
                sms_repl = (int)(sms[0])
                sms_stats = (int)(sms[1])
            except:
                pass
            if( current['role'] != last['role']):
                if(sms_repl == 1):
                    self.sendsms('from: %s changeto: %s' % (last['role'], current['role']))
            elif(sms_stats == 1 and current['role'] =='master'):
                stat='slave status OK.'
                slv=current['slaves']
                if(slv.find('wait_bgsave')!=-1):
                    stat='dumping data to prepare send to slave.'
                elif(slv.find('send_bulk')!=-1):
                    stat='sending dump data to slave.'
                self.sendsms(stat+'(%s)' % slv)
                
        except Exception, ex:
            print ex

    def servicedown(self):
        self.continueFaildTimes += 1
        if(self.continueFaildTimes % 20 == 0):
            self.sendsms('ping retry 20 times,all faild!!')
        
    def sendsms(self, content):
        url = "192.168.110.207:9999"
        try:
            url = settings.get_redis_alerturi()
        finally:
            pass
        content = '[redis]%s(%s):' % (self.instancename , self.id) + content
        conn = httplib.HTTPConnection(url)
        print content
        conn.request("POST", "/SendSms", body=urllib.urlencode({'text':content}))
        r1 = conn.getresponse()
        
        print r1.status, r1.reason 

class redis_monitor(daemonized):
    def __init__(self):
        self.threads = {}
        self.active = True

    def run_daemon(self):
        try:
            doitems = 0
            while self.active:
                try:
                    self.run_info()
                except Exception:
                    print traceback.format_exc()
                    
                time.sleep(10)
                doitems += 1
                
                # try collection DB like:redis bgrewriteaof
                if(doitems % 3600 == 0):
                    stats_provider = RedisLiveDataProvider.get_provider()
                    stats_provider.collection_database()
                
        except (KeyboardInterrupt, SystemExit):
            self.stop()
    
    def run_info(self):
        servers = settings.get_redis_servers()
        
        eids = set(())
        for server in servers:
            eid = server['ep']
            eids.add(eid)
            instancename = '%(group)s-%(instance)s' % server
            info=self.threads.get(eid)
            if( info== None):
                info = InfoThread(server["server"], server["port"],
                               instancename,server.get("password", None))
                info.setDaemon(True)
                info.start()
                self.threads[eid] = info
               
                print 'add %s' % eid
            else:
                info.instancename= instancename
            
        for eid, info2 in self.threads.items():
            if(eid not in eids):
                info2.stop()
                self.threads.pop(eid)
                print 'remove %s' % eid
            
    def stop(self):
        print "shutting down..."
        
        for t in self.threads:
                t.stop()
        self.active = False

if __name__ == '__main__':
    monitor = redis_monitor()
    monitor.start()
