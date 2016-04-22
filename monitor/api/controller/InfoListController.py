from BaseController import BaseController
from api.util import settings
import redis

class InfoListController(BaseController):

    def get(self):
        group = self.get_argument("group", None)
        
        response = {}
        response['data']=[]
        for server in settings.get_redis_servers():
            if(group !=None and group!='all' and server['group'] != group):
                continue;
            
            info=self.getStatsPerServer((server['server'],server['port']))
            
            info.update({"addr" : info.get("server_name")[0].replace(".", "_") +  str(info.get("server_name")[1]),
            })
            info['show_name']=server['group']+'('+server['instance']+')'
            info['group']= server['group']
            screen_strategy = 'normal'
            if info.get("status") == 'down':
                screen_strategy = 'hidden'
    
            info.update({ "screen_strategy": screen_strategy,})

            response["data"].append(info)

        self.write(response)