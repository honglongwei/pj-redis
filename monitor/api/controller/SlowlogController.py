from BaseController import BaseController
import datetime
import redis

class SlowlogController(BaseController):

    def get(self):
        data={}
        data['data']=[]
        server = self.get_argument("server").split(':')
        connection = redis.Redis(host=server[0], port=(int)(server[1]), db=0,socket_timeout=1)
        logs = connection.execute_command('slowlog','get','128')
        for lid,timeticks,run_micro,commands in logs:
            timestamp = datetime.datetime.fromtimestamp(int(timeticks))
            cmd=' '.join(commands)
            data['data'].append({'id':lid,'time':str(timestamp),'escapeMs':(float)(run_micro)/1000,'cmd':cmd})
        self.write(data)