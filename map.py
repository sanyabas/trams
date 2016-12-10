import requests
import os.path
import math


class MapReceiver:
    def __init__(self):
        self.cache_dir='cache'
        self.tile_server='http://a.tile2.opencyclemap.org/transport'

    def check_cache(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_tile_from_coords(self, x, y, zoom):
        # self.check_cache()
        x_tile,y_tile=self.coords_to_tile(x,y,zoom)
        return self.get_tile_from_numbers(x_tile,y_tile,zoom)
        # tile_path = os.path.join(self.cache_dir, str(zoom), str(x_tile), str(y_tile)+'.png')
        # if not os.path.isfile(tile_path):
        #     self.create_subfolders(zoom,x_tile)
        #     tile=self.request_tile(zoom,x_tile,y_tile)
        #     with open(tile_path,'wb') as file:
        #         file.write(tile)
        # return tile_path

    def get_tile_from_numbers(self,x,y,zoom):
        self.check_cache()
        tile_path=os.path.join(self.cache_dir, str(zoom), str(x), str(y)+'.png')
        if not os.path.isfile(tile_path):
            self.create_subfolders(zoom,x)
            tile=self.request_tile(zoom,x,y)
            with open(tile_path,'wb') as file:
                file.write(tile)
        return tile_path

    def coords_to_tile(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        x_tile = int((lon_deg + 180.0) / 360.0 * n)
        y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return x_tile, y_tile

    def tile_too_coords(self, x_tile, y_tile, zoom):
        n = 2.0 ** zoom
        lon_deg = x_tile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * y_tile / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    def request_tile(self, zoom, tile_x, tile_y):
        url='{}/{}/{}/{}.png'.format(self.tile_server,zoom,tile_x,tile_y)
        req=requests.get(url)
        print(req.content)
        return req.content

    def create_subfolders(self, zoom, x):
        zoom_path=os.path.join(self.cache_dir,str(zoom))
        if not os.path.exists(zoom_path):
            os.mkdir(zoom_path)
        x_path=os.path.join(zoom_path,str(x))
        if not os.path.exists(x_path):
            os.mkdir(x_path)
