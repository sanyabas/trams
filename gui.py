import sys
import json
import math
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QRect, QPoint, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMainWindow
from PyQt5.QtWidgets import QWidget

from map import *
from tram_receiver import *


class MainWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.dock_widget = QtWidgets.QDockWidget(self)
        self.dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.tram_routes = [str(i) for i in range(1, 35) if i not in [12, 28, 29, 30]]
        self.trolley_routes = [str(i) for i in range(1, 21) if i != 2]
        self.settings_file = 'settings.json'
        self.init_ui()
        self.mapper = MapReceiver()
        self.render_map()

    def init_ui(self):
        refresh_action = QtWidgets.QAction('&Refresh', self)
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.triggered.connect(self.draw_trams)

        close_action = QtWidgets.QAction("&Close", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(sys.exit)

        menu_bar = self.menuBar()
        menu_bar.addAction(close_action)
        menu_bar.addAction(refresh_action)

        self.showMaximized()
        self.dock_widget.setWidget(DockWidget(self.tram_routes, self.trolley_routes))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_widget)

        self.setWindowTitle("Где трамвай")

    def render_map(self):
        self.setCentralWidget(MapWidget(self.mapper, self.load_settings()))

    def draw_trams(self):
        self.centralWidget().update()

    def closeEvent(self, e):
        with open(self.settings_file, 'w') as file:
            json.dump(self.centralWidget().get_settings(), file)

    def load_settings(self):
        with open(self.settings_file) as file:
            return json.load(file)


class MapWidget(QWidget):
    def __init__(self, mapper: MapReceiver, settings=None):
        QWidget.__init__(self)
        self.mapper = mapper
        self.tile_size = 256
        self.tile_drawn = []
        self.lat = 56.842963648401295
        self.lon = 60.6005859375
        self.zoom = 15
        self.delta = QPoint(0, 0)
        self.to_rerender = False
        self.load_settings(settings)
        self.trammer = TransportReceiver()
        self.drag_start = None
        self.current_pos = None

    def load_settings(self, settings):
        if settings is None:
            return
        self.lat = settings['lat']
        self.lon = settings['lon']

    def get_settings(self):
        return {
            'lat': self.lat,
            'lon': self.lon
        }

    def paintEvent(self, e):
        zoom = 15
        painter = QPainter()
        painter.begin(self)
        try:
            if self.to_rerender:
                self.rerender(painter)
            else:
                self.draw_tiles_from_corner(painter, self.lat, self.lon, zoom)
            self.draw_trams(painter)
        except Exception as e:
            print(e)
        painter.end()

    def draw_tiles_from_corner(self, painter: QPainter, x, y, zoom):
        geom = self.geometry()
        corner_x, corner_y = self.mapper.coords_to_tile(x, y, zoom)
        row_number = 0
        for row in range(geom.top() - self.tile_size, geom.height(), self.tile_size):
            col_number = 0
            for column in range(geom.left() - self.tile_size, geom.right(), self.tile_size):
                target_rect = QRect(column, row, self.tile_size, self.tile_size)
                tile_rect = QRect(0, 0, self.tile_size, self.tile_size)
                res_x = corner_x + col_number
                res_y = corner_y + row_number
                tile = self.mapper.get_tile_from_numbers(res_x, res_y, zoom)
                tile.corner = target_rect.topLeft()
                self.tile_drawn.append(tile)
                painter.drawPixmap(target_rect, QPixmap(tile.path), tile_rect)
                tile.widget_x = target_rect.x()
                tile.widget_y = target_rect.y()
                col_number += 1
            row_number += 1

    def rerender(self, painter: QPainter):
        for tile in self.tile_drawn:
            tile.widget_x += self.delta.x()
            tile.widget_y += self.delta.y()
            target_rect = QRectF(tile.widget_x, tile.widget_y, self.tile_size, self.tile_size)
            tile_rect = QRectF(0, 0, self.tile_size, self.tile_size)
            painter.drawPixmap(target_rect, QPixmap(tile.path), tile_rect)
        self.fill_perimeter(painter)
        self.clear_tiles()

    def fill_perimeter(self, painter):
        self.fill_top_row(painter)
        self.fill_bottom_row(painter)
        self.fill_left_column(painter)
        self.fill_right_column(painter)

    def fill_top_row(self, painter: QPainter):
        top_tile = min(self.get_tiles_on_screen(), key=lambda tile: tile.widget_y)
        if top_tile.widget_y > -self.tile_size:
            row = top_tile.widget_y - self.tile_size
            col_number = 0
            res_row = top_tile.y - 1
            for column in range(int(top_tile.widget_x), self.geometry().width() + 1, self.tile_size):
                res_col = top_tile.x + col_number
                tile = self.mapper.get_tile_from_numbers(res_col, res_row, self.zoom)
                target_rect = QRectF(column, row, self.tile_size, self.tile_size)
                tile_rect = QRectF(0, 0, self.tile_size, self.tile_size)
                self.tile_drawn.append(tile)
                painter.drawPixmap(target_rect, QPixmap(tile.path), tile_rect)
                tile.widget_x = target_rect.x()
                tile.widget_y = target_rect.y()
                col_number += 1

    def fill_bottom_row(self, painter: QPainter):
        bottom_tile = max(self.get_tiles_on_screen(), key=lambda cur_tile: cur_tile.widget_y)
        if bottom_tile.widget_y < self.geometry().height():
            row = bottom_tile.widget_y + self.tile_size
            col_number = 0
            res_row = bottom_tile.y + 1
            for column in range(int(bottom_tile.widget_x), self.geometry().width() + 1, self.tile_size):
                res_col = bottom_tile.x + col_number
                tile = self.mapper.get_tile_from_numbers(res_col, res_row, self.zoom)
                target_rect = QRectF(column, row, self.tile_size, self.tile_size)
                tile_rect = QRectF(0, 0, self.tile_size, self.tile_size)
                self.tile_drawn.append(tile)
                painter.drawPixmap(target_rect, QPixmap(tile.path), tile_rect)
                tile.widget_x = target_rect.x()
                tile.widget_y = target_rect.y()
                col_number += 1

    def fill_left_column(self, painter: QPainter):
        left_tile = min(self.get_tiles_on_screen(), key=lambda tile: tile.widget_x)
        if left_tile.widget_x > -self.tile_size:
            column = left_tile.widget_x - self.tile_size
            row_number = 0
            res_col = left_tile.x - 1
            for row in range(int(left_tile.widget_y), self.geometry().height() + 1, self.tile_size):
                res_row = left_tile.y + row_number
                tile = self.mapper.get_tile_from_numbers(res_col, res_row, self.zoom)
                target_rect = QRectF(column, row, self.tile_size, self.tile_size)
                tile_rect = QRectF(0, 0, self.tile_size, self.tile_size)
                self.tile_drawn.append(tile)
                painter.drawPixmap(target_rect, QPixmap(tile.path), tile_rect)
                tile.widget_x = target_rect.x()
                tile.widget_y = target_rect.y()
                row_number += 1

    def fill_right_column(self, painter: QPainter):
        right_tile = max(self.get_tiles_on_screen(), key=lambda tile: tile.widget_x)
        if right_tile.widget_x < self.geometry().width() + 256:
            column = right_tile.widget_x + self.tile_size
            row_number = 0
            res_col = right_tile.x + 1
            for row in range(int(right_tile.widget_y), self.geometry().height() + 1, self.tile_size):
                res_row = right_tile.y + row_number
                tile = self.mapper.get_tile_from_numbers(res_col, res_row, self.zoom)
                target_rect = QRectF(column, row, self.tile_size, self.tile_size)
                tile_rect = QRectF(0, 0, self.tile_size, self.tile_size)
                self.tile_drawn.append(tile)
                painter.drawPixmap(target_rect, QPixmap(tile.path), tile_rect)
                tile.widget_x = target_rect.x()
                tile.widget_y = target_rect.y()
                row_number += 1

    def clear_tiles(self):
        geom = self.geometry()
        bounds = QRect(-self.tile_size, -self.tile_size, geom.width() + self.tile_size, geom.height() + self.tile_size)
        tiles = [tile for tile in self.tile_drawn if
                 self.fully_outside(QRect(tile.widget_x, tile.widget_y, self.tile_size, self.tile_size), bounds)]
        for tile in tiles:
            self.tile_drawn.remove(tile)

    def outside_bounds(self, rect: QRect, bounds: QRect):
        return rect.top() < bounds.top() or rect.bottom() > bounds.bottom() or rect.left() < bounds.left() or rect.right() > bounds.right()

    def fully_outside(self, rect: QRect, bounds: QRect):
        return rect.bottom() < bounds.top() or rect.right() < bounds.left() or rect.top() > bounds.bottom() or rect.left() > bounds.right()

    def get_tiles_on_screen(self):
        geom = self.geometry()
        return [tile for tile in self.tile_drawn if
                not self.outside_bounds(QRect(tile.widget_x, tile.widget_y, self.tile_size, self.tile_size),
                                        geom)]

    def point_is_outside(self, point: QPointF, bounds: QRectF):
        return point.x() < bounds.left() or point.x() > bounds.right() or point.y() < bounds.top() or point.y() > bounds.bottom()

    def draw_trams(self, painter: QPainter):
        trams = self.trammer.get_trams()
        last_tile = self.tile_drawn[-1]
        right_bottom = self.mapper.tile_too_coords(last_tile.x + 1, last_tile.y + 1, self.zoom)
        right_bottom = QPointF(right_bottom[1], right_bottom[0])
        width = math.fabs(right_bottom.x() - self.lon)
        height = math.fabs(right_bottom.y() - self.lat)
        bounds = QRectF(self.lon, right_bottom.y(), width, height)
        for tram in trams:
            location = QPointF(tram.lon, tram.lat)
            if self.point_is_outside(location, bounds):
                continue
            coords = self.count_tram_tile_coords(tram)
            if coords is not None:
                x, y = coords
                painter.setBrush(QColor(255, 0, 0))
                painter.drawEllipse(x, y, 10, 10)
                painter.drawText(x, y, tram.route)

    def count_tram_tile_coords(self, tram):
        tile = self.mapper.coords_to_tile(tram.lat, tram.lon, self.zoom)
        drawn_tile = self.find_tile(tile[0], tile[1])
        if drawn_tile is None:
            return
        tile_lat, tile_lon = self.mapper.tile_too_coords(tile[0], tile[1], self.zoom)
        dy = self.mapper.get_distance((tile_lat, tile_lon), (tram.lat, tile_lon))
        dx = self.mapper.get_distance((tile_lat, tile_lon), (tile_lat, tram.lon))
        resolution = self.mapper.get_resolution(tram.lat, self.zoom)
        tile_dy = dy / resolution
        tile_dx = dx / resolution
        return drawn_tile.widget_x + tile_dx, drawn_tile.widget_y + tile_dy

    def find_tile(self, x, y):
        for tile in self.tile_drawn:
            if tile.x == x and tile.y == y:
                return tile
        return None

    def find_tile_by_drawn_coords(self, x, y):
        for tile in self.tile_drawn:
            if x - tile.widget_x <= 256 and y - tile.widget_y <= 256:
                return tile
        return None

    def mousePressEvent(self, event):
        self.drag_start = event.localPos()

    def mouseMoveEvent(self, event):
        self.current_pos = event.localPos()
        tile = self.find_tile_by_drawn_coords(self.current_pos.x(), self.current_pos.y())
        if tile is None:
            return
        delta = self.current_pos - self.drag_start
        new_x, new_y = tile.x + delta.x() / 256, tile.y + delta.y() / 256
        new_lat, new_lon = self.mapper.tile_too_coords(new_x, new_y, self.zoom)
        old_lat, old_lon = self.mapper.tile_too_coords(tile.x, tile.y, self.zoom)
        coords_delta = (new_lat - old_lat, new_lon - old_lon)
        self.lat -= coords_delta[0]
        self.lon -= coords_delta[1]
        self.drag_start = self.current_pos
        self.delta = delta
        self.to_rerender = True
        self.update()


class DockWidget(QWidget):
    def __init__(self, tram_routes, trolley_routes):
        QWidget.__init__(self)
        self.tram_widget = TramPickWidget(tram_routes)
        self.trolley_widget = TrolleyPickWidget(trolley_routes)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(QLabel('Трамваи'), 0, 0)
        layout.addWidget(self.tram_widget, 1, 0)
        layout.addWidget(QLabel('Троллейбусы'), 2, 0)
        layout.addWidget(self.trolley_widget, 3, 0)
        self.setLayout(layout)


class TransportPickWidget(QWidget):
    def __init__(self, routes):
        QWidget.__init__(self)
        self.routes = routes
        self.route_checkboxes = []
        self.init_ui()

    def init_ui(self):
        self.layout = QtWidgets.QGridLayout()
        column = 0
        column_length = 5
        for i in range(len(self.routes)):
            if i % column_length == 0:
                column += 1
            widget = QWidget()
            layout = QtWidgets.QGridLayout()
            label = QLabel(self.routes[i])
            layout.addWidget(label, 0, 0)
            check = QtWidgets.QCheckBox()
            layout.addWidget(check, 0, 1)
            self.route_checkboxes.append(widget)
            widget.setLayout(layout)
            self.layout.addWidget(widget, i % column_length, column)
        self.layout.addWidget(QWidget(), column_length, 0, -1, -1)
        self.layout.setRowStretch(column_length, 1)
        self.setLayout(self.layout)


class TramPickWidget(TransportPickWidget):
    def __init__(self, routes):
        super().__init__(routes)
        self.init_ui()


class TrolleyPickWidget(TransportPickWidget):
    def __init__(self, routes):
        super().__init__(routes)
        self.init_ui()
