import requests

class TransportReceiver:
    def __init__(self):
        super().__init__()
        self.tram_routes = [str(i) for i in range(1, 35) if i not in [12, 28, 29, 30]]
        self.trolley_routes = [str(i) for i in range(1, 21) if i!=2]

    def get_trams(self):
        trams = self.receive_transport(1,self.tram_routes)
        return [Tram(tram[0],tram[1],tram[2],tram[3]) for tram in trams]

    def get_trolleys(self):
        trolleys = self.receive_transport(2,self.trolley_routes)
        return [Trolley(trolley[0],trolley[1],trolley[2],trolley[3]) for trolley in trolleys]

    def receive_transport(self, transport_type, routes):
        url='http://online.ettu.ru/map/getTrams/?p={},1,{}'.format(transport_type,','.join(routes))
        req=requests.get(url)
        dic=req.json()
        print(dic['T'])
        return dic['T']

class Transport:
    def __init__(self, id, route, x,y, type):
        super().__init__()
        self.id=id
        self.route=route
        self.type=type
        self.x=x
        self.y=y


class Tram(Transport):
    def __init__(self, id, route, x, y):
        super().__init__(id, route, x,y,1)


class Trolley(Transport):
    def __init__(self, id,route, x, y):
        super().__init__(id, route, x, y,2)
