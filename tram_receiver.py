import requests

class TransportReceiver:
    def __init__(self):
        super().__init__()
        self.tram_routes = [str(i) for i in range(1, 35) if i not in [12, 28, 29, 30]]
        self.trolley_routes = [str(i) for i in range(1, 21) if i!=2]

    def get_trams(self):
        return self.receive_transport(1,self.tram_routes)

    def get_trolleys(self):
        return self.receive_transport(2,self.trolley_routes)

    def receive_transport(self, transport_type, routes):
        url='http://online.ettu.ru/map/getTrams/?p={},1,{}'.format(transport_type,','.join(routes))
        req=requests.get(url)
        dic=req.json()
        print(dic['T'])
        return dic['T']
