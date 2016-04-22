from dataprovider.dataprovider import RedisLiveDataProvider
import tornado.ioloop
import tornado.web
import dateutil.parser
import redis

class BaseController(tornado.web.RequestHandler):

    stats_provider = RedisLiveDataProvider.get_provider()
    
    def getStatsPerServer(self, server):
        try:
            connection = redis.Redis(host=server[0], port=(int)(server[1]), db=0,socket_timeout=0.1)
            info = connection.info()
            # when instances down ,this maybe slowly...
            info.update({
                "server_name"        : server,
                "status"             : info.get("role"),
                "last_save_humanized": info.get("last_save_time")
            })
            
            #master status
            role = info["role"]
            slaves=""
            
            if(role == "master"):
                connected_slaves = (int)(info["connected_slaves"])
                slaves = ""
                for i in range(0, connected_slaves):
                    slaves += info["slave" + (str)(i)]
            else:
                master_host = info["master_host"]
                master_port = (str)(info["master_port"])
                master_link_status = info["master_link_status"]
                master_sync_in_progress = info["master_sync_in_progress"]
                if(master_host!=""):
                    slaves=master_host+":"+(str)(master_port)+","+master_link_status
                    if(master_sync_in_progress==1):
                        slaves+=",syncing"
            info['master_slaves']=slaves
                    
                
        except redis.exceptions.ConnectionError:
            info = {
                "role"              :"down",
                "uptime_in_seconds" :0,
                "total_commands_processed":0,
                "used_memory_human" :"",
                "connected_clients" :"",
                "status"            : "down",
                "server_name"       : server,
                "connected_clients" : 0,
                "used_memory_human" : '?',
            }

        return info

    def datetime_to_list(self, datetime):
        """Converts a datetime to a list.

        Args:
            datetime (datetime): The datetime to convert.
        """
        parsed_date = dateutil.parser.parse(datetime)
        # don't return the last two fields, we don't want them.
        return tuple(parsed_date.timetuple())[:-2]

    # todo : fix this
    def average_data(self, data):
        """Averages data.

        TODO: More docstring here, once functionality is understood.
        """
        average = []

        deviation = 1024 * 1024

        start = dateutil.parser.parse(data[0][0])
        end = dateutil.parser.parse(data[-1][0])
        difference = end - start
        weeks, days = divmod(difference.days, 7)
        minutes, seconds = divmod(difference.seconds, 60)
        hours, minutes = divmod(minutes, 60)

        # TODO: These if/elif/else branches chould probably be broken out into
        # individual functions to make it easier to follow what's going on.
        if difference.days > 0:
            current_max = 0
            current_current = 0
            current_d = 0

            for dt, max_memory, current_memory in data:
                d = dateutil.parser.parse(dt)
                if d.day != current_d:
                    current_d = d.day
                    average.append([dt, max_memory, current_memory])
                    current_max = max_memory
                    current_current = current_memory
                else:
                    if max_memory > current_max or \
                       current_memory > current_current:
                        average.pop()
                        average.append([dt, max_memory, current_memory])
                        current_max = max_memory
                        current_current = current_memory
        elif hours > 0:
            current_max = 0
            current_current = 0
            current = -1
            keep_flag = False

            for dt, max_memory, current_memory in data:
                d = dateutil.parser.parse(dt)
                if d.hour != current:
                    current = d.hour
                    average.append([dt, max_memory, current_memory])
                    current_max = max_memory
                    current_current = current_memory
                    keep_flag = False
                elif abs(max_memory - current_max) > deviation or \
                     abs(current_memory - current_current) > deviation:
                    # average.pop()
                    average.append([dt, max_memory, current_memory])
                    current_max = max_memory
                    current_current = current_memory
                    keep_flag = True
                elif max_memory > current_max or \
                     current_memory > current_current:
                    if keep_flag != True:
                        average.pop()
                    average.append([dt, max_memory, current_memory])
                    current_max = max_memory
                    current_current = current_memory
                    keep_flag = False
        else:
            current_max = 0
            current_current = 0
            current_m = -1
            keep_flag = False
            for dt, max_memory, current_memory in data:
                d = dateutil.parser.parse(dt)
                if d.minute != current_m:
                    current_m = d.minute
                    average.append([dt, max_memory, current_memory])
                    current_max = max_memory
                    current_current = current_memory
                    keep_flag = False
                elif abs(max_memory - current_max) > deviation or \
                     abs(current_memory - current_current) > deviation:
                    # average.pop()
                    average.append([dt, max_memory, current_memory])
                    current_max = max_memory
                    current_current = current_memory
                    keep_flag = True
                elif max_memory > current_max or \
                    current_memory > current_current:
                    if keep_flag != True:
                        average.pop()
                    average.append([dt, max_memory, current_memory])
                    current_max = max_memory
                    current_current = current_memory
                    keep_flag = False

        return average
