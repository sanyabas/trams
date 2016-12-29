import requests
import os.path
import math


class MapReceiver:
    def __init__(self):
        self.cache_dir = 'cache'
        self.tile_server = 'http://a.tile2.opencyclemap.org/transport'

    def check_cache(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_tile_from_coords(self, x, y, zoom):
        x_tile, y_tile = self.coords_to_tile(x, y, zoom)
        return self.get_tile_from_numbers(x_tile, y_tile, zoom)

    def get_tile_from_numbers(self, x, y, zoom):
        self.check_cache()
        tile_path = os.path.join(self.cache_dir, str(zoom), str(x), str(y) + '.png')
        if not os.path.isfile(tile_path):
            self.create_subfolders(zoom, x)
            tile = self.request_tile(zoom, x, y)
            with open(tile_path, 'wb') as file:
                file.write(tile)
        return Tile(x, y, zoom, tile_path)

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

    def get_distance(self, point1, point2):
        r = 6371
        lat_1, lon_1 = point1
        lat_2, lon_2 = point2
        lat_rad = math.radians(lat_2 - lat_1)
        lon_rad = math.radians(lon_2 - lon_1)
        lat_1 = math.radians(lat_1)
        lat_2 = math.radians(lat_2)
        a = math.sin(lat_rad / 2) * math.sin(lat_rad / 2) + math.sin(lon_rad / 2) * math.sin(lon_rad / 2) \
                                                            * math.cos(lat_1) * math.cos(lat_2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return r * c * 1000

    def get_resolution(self, lat, zoom):
        return 156543.03 * math.cos(math.radians(lat)) / (2 ** zoom)

    def request_tile(self, zoom, tile_x, tile_y):
        url = '{}/{}/{}/{}.png'.format(self.tile_server, zoom, tile_x, tile_y)
        req = requests.get(url)
        return req.content

    def create_subfolders(self, zoom, x):
        zoom_path = os.path.join(self.cache_dir, str(zoom))
        if not os.path.exists(zoom_path):
            os.mkdir(zoom_path)
        x_path = os.path.join(zoom_path, str(x))
        if not os.path.exists(x_path):
            os.mkdir(x_path)


class Tile:
    def __init__(self, x, y, zoom, path):
        super().__init__()
        self.x = x
        self.y = y
        self.zoom = zoom
        self.path = path
        self.corner = None
        self.widget_x = 0
        self.widget_y = 0

    def __str__(self, *args, **kwargs):
        return '{}:{},{}'.format(self.zoom, self.x, self.y)
