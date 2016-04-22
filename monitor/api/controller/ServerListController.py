from BaseController import BaseController
from api.util import settings

class ServerListController(BaseController):

    def get(self):
        servers = {"servers": self.read_server_config()}
        self.write(servers)

    def read_server_config(self):
        server_list = []
        redis_servers = settings.get_redis_servers()

        for server in redis_servers:
            server['id']= "%(server)s:%(port)s" % server
            server_list.append(server)

        return server_list
