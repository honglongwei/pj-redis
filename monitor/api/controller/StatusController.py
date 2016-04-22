from BaseController import BaseController
import tornado.ioloop
import tornado.web
import dateutil.parser
import datetime

class StatusController(BaseController):

    def get(self):
        return_data = {}
        return_data['data']=[]

        server = self.get_argument("server")
        from_date = self.get_argument("from", None)
        to_date = self.get_argument("to", None)

        if from_date == None or to_date == None or len(from_date) == 0:
            end = datetime.datetime.now()
            delta = datetime.timedelta(seconds=300)
            start = end - delta
        else:
            start = dateutil.parser.parse(from_date)
            end = dateutil.parser.parse(to_date)

        data = self.stats_provider.get_status_info(server, start, end)
       
        for item in data:
            row=item[1]
            timestamp = datetime.datetime.fromtimestamp(int(row['timestamp']))
            row['time']= timestamp.strftime('%Y-%m-%d %H:%M:%S')
            return_data['data'].append(row)

        self.write(return_data)
