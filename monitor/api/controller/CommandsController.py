from BaseController import BaseController
import tornado.ioloop
import tornado.web
import dateutil.parser
import datetime


class CommandsController(BaseController):

    def get(self):
        """Serves a GET request.
        """
        return_data = dict(data=[],
                           timestamp=datetime.datetime.now().isoformat())

        server = self.get_argument("server")
        from_date = self.get_argument("from", None)
        to_date = self.get_argument("to", None)

        if from_date==None or to_date==None or len(from_date)==0:
            end = datetime.datetime.now()
            delta = datetime.timedelta(seconds=900)
            start = end - delta
        else:
            start = dateutil.parser.parse(from_date)
            end   = dateutil.parser.parse(to_date)

        data = self.stats_provider.get_keys_info(server, start, end)
       
        return_data['data']=data

        self.write(return_data)
