import sys
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QMessageBox, QDialog, QMainWindow
from PyQt5.QtWidgets import QWidget

from map import *
from tram_receiver import *


class MainWidget(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.dock_widget = QtWidgets.QDockWidget(self)
        self.dock_widget.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)
        self.tram_routes = [str(i) for i in range(1, 35) if i not in [12, 28, 29, 30]]
        self.trolley_routes = [str(i) for i in range(1, 21)]
        self.init_ui()
        self.mapper = MapReceiver()
        self.x = 56.842963648401295
        self.y = 60.6005859375
        self.zoom = 15
        self.render_map(self.x, self.y, self.zoom)
        self.dock_widget.show()
        trammer = TransportReceiver()
        trammer.get_trams()
        trammer.get_trolleys()

    def init_ui(self):
        refresh_action = QtWidgets.QAction('&Refresh', self)
        refresh_action.setShortcut('Ctrl+R')
        refresh_action.triggered.connect(lambda x: x)

        close_action = QtWidgets.QAction("&Close", self)
        close_action.setShortcut("Ctrl+Q")
        close_action.triggered.connect(lambda x: sys.exit())

        menu_bar = self.menuBar()
        menu_bar.addAction(close_action)
        menu_bar.addAction(refresh_action)

        self.showMaximized()
        self.dock_widget.setWidget(DockWidget(self.tram_routes, self.trolley_routes))
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dock_widget)

        self.setWindowTitle("Где трамвай")
        # self.resize(300,300)

    def render_map(self, x, y, zoom):
        self.setCentralWidget(MapWidget(self.mapper))
        # self.centralWidget().render_map_2(x, y, zoom)


class MapWidget(QWidget):
    def __init__(self, mapper: MapReceiver):
        QWidget.__init__(self)
        self.mapper = mapper
        self.tile_size = 256
        self.tile_drawn = []

    def render_map(self, x, y, zoom):
        geom = self.geometry()

        self.layout = QtWidgets.QGridLayout()
        x, y = self.mapper.coords_to_tile(x, y, zoom)
        for i in range(-1, 2):
            for j in range(-1, 2):
                label = QLabel(self)
                tile = self.mapper.get_tile_from_numbers(x + i, y + j, zoom)
                label.setPixmap(QPixmap(tile))
                self.layout.addWidget(label, j + 1, i + 1)
        # self.label=QLabel(self)
        # self.label.setPixmap(QPixmap(tile))
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(0)
        self.showMaximized()
        self.setLayout(self.layout)

    # def render_map_2(self,x,y,zoom):
    #     x, y = self.mapper.coords_to_tile(x, y, zoom)
    #     tile=self.mapper.get_tile_from_numbers(x,y,zoom)
    #     pixmap=QPixmap()
    #     tile_size=256
    #     geom=self.geometry()
    #     painter=QPainter()
    #     painter.begin(self)
    #     # painter.translate((geom.width()-tile_size)/2,(geom.height()-tile_size)/2)
    #     tile_rect=QRect(0,0,tile_size,tile_size)
    #     painter.drawPixmap(tile_rect, QPixmap(tile))
    #     # label=QLabel()
    #     # label.setPixmap(pixmap)
    #     # label.show()
    #     painter.end()

    def paintEvent(self, e):
        x = 56.842963648401295
        y = 60.6005859375
        zoom = 15
        painter = QPainter()
        painter.begin(self)
        # self.draw_tiles_around_center(painter,x,y,zoom)
        # self.draw_far_tiles(painter,x,y,zoom)
        self.draw_tiles_from_corner(painter, x, y, zoom)
        # x, y = self.mapper.coords_to_tile(x, y, zoom)
        # tile = self.mapper.get_tile_from_numbers(x, y, zoom)
        # pixmap = QPixmap()
        # tile_size = 256
        # geom = self.geometry()
        # painter.translate((geom.width()-tile_size)/2,(geom.height()-tile_size)/2)
        # tile_rect = QRect(0, 0, tile_size, tile_size)
        # painter.drawPixmap(tile_rect, QPixmap(tile))
        # painter.translate(-tile_size,0)
        # tile = self.mapper.get_tile_from_numbers(x-1, y, zoom)
        # painter.drawPixmap(tile_rect, QPixmap(tile))
        # left=geom.width()/2-3*tile_size/2
        # tile_rect=QRect(-left,0,tile_size,tile_size)
        # tile_rend=QRect(tile_size-left,0,tile_size,tile_size)
        # tile = self.mapper.get_tile_from_numbers(x-2, y, zoom)
        # painter.drawPixmap(tile_rect, QPixmap(tile),tile_rend)
        # q=painter.window()
        # # painter.translate(-tile_size, 0)
        # # tile = self.mapper.get_tile_from_numbers(x - 2, y, zoom)
        # # painter.drawPixmap(tile_rect, QPixmap(tile))
        # # label=QLabel()
        # # label.setPixmap(pixmap)
        # # label.show()
        painter.end()
        print(self.tile_drawn)
        for i in self.tile_drawn:
            print(i.corner)

    def draw_tiles_around_center(self, painter: QPainter, x, y, zoom):
        geom = self.geometry()
        painter.translate((geom.width() - self.tile_size) / 2, (geom.height() - self.tile_size) / 2)
        translated_geom = QRect(-(geom.width() - self.tile_size) / 2, -(geom.height() - self.tile_size) / 2,
                                geom.width(), geom.height())
        center_x, center_y = self.mapper.coords_to_tile(x, y, zoom)
        for row in range(-1, 2):
            for column in range(-1, 2):
                target_rect = QRect(column * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size)
                self.tile_drawn.append(target_rect)
                if self.outside_bounds(target_rect, translated_geom):
                    continue
                tile = self.mapper.get_tile_from_numbers(center_x + column, center_y + row, zoom)
                painter.drawPixmap(target_rect, QPixmap(tile))

    def draw_far_tiles(self, painter: QPainter, x, y, zoom):
        # painter.resetTransform()
        top_drawn = min(self.tile_drawn, key=lambda rect: rect.top()).top()
        left_drawn = min(self.tile_drawn, key=lambda rect: rect.left()).left()
        right_drawn = max(self.tile_drawn, key=lambda rect: rect.right()).right()
        bottom_drawn = max(self.tile_drawn, key=lambda rect: rect.bottom()).bottom()
        geom = self.geometry()
        start_x = 0
        start_y = 0
        # while start_x<geom.width():
        center_x, center_y = self.mapper.coords_to_tile(x, y, zoom)
        target_rect = QRect(start_x, start_y, left_drawn, top_drawn)
        tile_rect = QRect(self.tile_size - left_drawn, self.tile_size - top_drawn, math.fabs(left_drawn),
                          math.fabs(top_drawn))
        tile = self.mapper.get_tile_from_numbers(center_x - 2, center_y - 2, zoom)
        painter.drawPixmap(target_rect, QPixmap(tile), tile_rect)
        start_x += left_drawn

    def draw_tiles_from_corner(self, painter: QPainter, x, y, zoom):
        geom = self.geometry()
        corner_x, corner_y = self.mapper.coords_to_tile(x, y, zoom)
        row_number = 0
        for row in range(geom.top(), geom.height(), self.tile_size):
            col_number = 0
            for column in range(geom.left(), geom.right(), self.tile_size):
                target_rect = QRect(column, row, self.tile_size, self.tile_size)
                tile_rect = QRect(0, 0, self.tile_size, self.tile_size)
                if self.outside_bounds(target_rect, geom):
                    height = geom.bottom() - row if row + self.tile_size > geom.bottom() else self.tile_size
                    width = geom.right() - column if column + self.tile_size > geom.right() else self.tile_size
                    target_rect = QRect(column, row, width, height)
                    tile_rect = QRect(0, 0, width, height)
                res_x = corner_x + col_number
                res_y = corner_y + row_number
                tile = self.mapper.get_tile_from_numbers(res_x, res_y, zoom)
                tile.corner = target_rect.topLeft()
                self.tile_drawn.append(tile)
                painter.drawPixmap(target_rect, QPixmap(tile.path), tile_rect)
                col_number += 1
            row_number += 1

    def outside_bounds(self, rect: QRect, bounds: QRect):
        return rect.top() < bounds.top() or rect.bottom() > bounds.bottom() or rect.left() < bounds.left() or rect.right() > bounds.right()


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
