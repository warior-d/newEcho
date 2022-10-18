from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QFileDialog, QLabel, QWidget, QMainWindow, QApplication, QSlider, \
    QAction, qApp, QToolBar, QStackedWidget, QPushButton
# import newReady as myWidget
from pathlib import Path
from PyQt5 import QtWidgets, QtCore
import csv
import os
from geopy import Point
from geopy.distance import geodesic, distance
import xml.etree.ElementTree as ET
from math import atan2, degrees, pi, sin, cos, tan, radians, sqrt
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QIcon


def getCoordsFromKML(kmlfile):
    tree = ET.parse(kmlfile)
    root = tree.getroot()
    north = None
    west = None
    east = None
    south = None
    for elem in root[0]:
        for subelem in elem:
            if subelem.tag == 'north':
                north = subelem.text
            if subelem.tag == 'west':
                west = subelem.text
            if subelem.tag == 'east':
                east = subelem.text
            if subelem.tag == 'south':
                south = subelem.text
    coordinates = {'north': north, 'west': west, 'east': east, 'south': south}
    return coordinates

# по координатам реперной точки на экране дает координаты нужной точки
def getCoord(x_ground, y_ground, x_current, y_current):
    # https://github.com/geopy/geopy/blob/master/geopy/distance.py
    grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
    gridStep = Settings.GRID_STEP
    pixelLenght = grid / gridStep
    delta_x = x_current - x_ground
    delta_y = y_ground - y_current
    lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
    lengh_meters = lengh_pixels * pixelLenght
    rads = atan2(delta_y, -delta_x)
    rads %= 2 * pi
    degs = degrees(rads) - 90
    need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.LAT_NW, Settings.LON_NW),
                                                                      degs).format_decimal()
    # вывод - в координатах.
    return need_point

# расстояние в метрах между двумя координатами
def distanceBetweenPointsMeters(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).meters

# расстояние в пикселях между двумя точками на экране
def distanceInPixels(x1, y1, x2, y2):
    return ((x1 - x2) ** (2) + (y1 - y2) ** (2)) ** (0.5)

def getPointbyCoords(lat_base, lon_base, lat_current, lon_current, baseX, baseY):
    point1 = (lat_base, lon_base)
    point2 = (lat_current, lon_current)
    real_dist = geodesic(point1, point2).meters
    grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
    gridStep = Settings.GRID_STEP
    pixelLenght = grid / gridStep  #40m/80px = 0.5m in pixel
    real_dist_in_pixels = real_dist / pixelLenght
    dLon = float(lon_current) - float(lon_base)
    y = sin(dLon) * cos(lat_current)
    x = cos(float(lat_base)) * sin(float(lat_current)) - sin(float(lat_base)) * cos(float(lat_current)) * cos(dLon)
    rads = atan2(y, x)
    rads %= 2 * pi
    degsa = 90 - degrees(rads)
    if degsa < 0:
        degsa += 360
    degreeses = degsa * pi / 180
    grad = degrees(degreeses)
    relX = baseX + (real_dist_in_pixels * cos(degreeses))
    relY = baseY - (real_dist_in_pixels * sin(degreeses)) # 0 & 180

    point = (int(relX), int(relY))
    return point

class Settings():
    GRID_STEP = 80
    NEED_GRID = 0
    NEED_FISHING_CIRCLE = 1
    FISHING_SIRCLE_RADIUS = 60
    FISHING_SIRCLE_QNT = 2
    MASHTAB_MIN = 1
    MASHTAB_MAX = 9
    FILE_NAME = None  # "OKA_19_160.jpg"
    KML_FILE_NAME = None
    FILE_DEPTH_NAME = "djer.csv"  # "OKA_19_160.jpg"
    IMAGE_WIDTH = None
    IMAGE_HEIGHT = None
    LAT_NW = None
    LON_NW = None
    LAT_SE = None
    LON_SE = None
    DEFAULT_MASHTAB = 4
    CURRENT_MASHTAB = 4
    KOEFFICIENT = None
    DEFAULT_TRANSPARENCY = 9
    DESCTOP_WIDHT = None
    DESCTOP_HEIGHT = None
    CENTR_LAT = None
    CENTR_LON = None
    ZOOMING = None
    # Для увеличения можно поменять обратно сделать!
    GRID_SCALE = ["10", "20", "40", "80", "160", "320", "640", "1000", "2000"]
    #               0     1     2     3     4      5      6       7       8
    #               1     2     3     4     5      6      7       8       9
    POS_X = 200
    POS_Y = 150
    POS_SHIP_X = 500
    POS_SHIP_Y = 500
    COURSE = None
    PAINT_POSx = None
    PAINT_POSy = None

    # установка текущего масштаба (1 - 9)
    def setScale(self, scale):
        self.CURRENT_MASHTAB = scale

    # получение текущего масштаба
    def getScale(self):
        return self.CURRENT_MASHTAB

    # получение цены деления сетки
    def getGridScale(self):
        return self.GRID_SCALE[self.CURRENT_MASHTAB - 1]

    def getGrid(self):
        return self.GRID_STEP

    def setImageMap(self, filename):
        self.FILE_NAME = filename
        return self.FILE_NAME

class LabelShip(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        # self.move(100, 100)
        self.setGeometry(0, 0, 1000, 1000)

    def paintEvent(self, event):
        ship_height = 10
        ship_weight = 20
        x1, y1 = Settings.POS_SHIP_X - int(ship_weight / 2), Settings.POS_SHIP_Y - int(ship_height / 2)
        x2, y2 = Settings.POS_SHIP_X - int(ship_weight / 2), Settings.POS_SHIP_Y + int(ship_height / 2)
        x3, y3 = Settings.POS_SHIP_X + int(ship_weight / 2), Settings.POS_SHIP_Y
        pixmap = QPixmap()
        painter = QPainter(pixmap)
        painter.begin(self)
        pen = QPen(Qt.GlobalColor.green, 2, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
        painter.setPen(pen)
        painter.drawLine(x1, y1, x2, y2)
        painter.drawLine(x2, y2, x3, y3)
        painter.drawLine(x3, y3, x1, y1)
        if Settings.NEED_FISHING_CIRCLE == 1:
            centr = QPoint()
            centr.setX(Settings.POS_SHIP_X)
            centr.setY(Settings.POS_SHIP_Y)
            rad = (Settings.GRID_STEP * Settings.FISHING_SIRCLE_RADIUS) / int(
                Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
            painter.drawEllipse(centr, rad, rad)
        painter.end()
        self.setPixmap(pixmap)

class LabelGrid(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        # self.move(100, 100)
        self.setGeometry(0, 0, 1900, 1800)

    def paintEvent(self, event):
        if Settings.NEED_GRID == 1:
            pixmap = QPixmap()
            x = Settings.POS_X
            y = Settings.POS_Y
            if None not in (Settings.IMAGE_HEIGHT, Settings.IMAGE_WIDTH):
                x = Settings.POS_X + int(Settings.IMAGE_WIDTH / 2)
                y = Settings.POS_Y + int(Settings.IMAGE_HEIGHT / 2)
            painter = QPainter(pixmap)
            painter.begin(self)
            for i in range(-10000, 10000, Settings.GRID_STEP):
                painter.drawLine(x + i, 0, x + i, 10000)
                painter.drawLine(x - i, 0, x - i, 10000)
                painter.drawLine(0, y + i, 10000, y + i)
                painter.drawLine(0, y - i, 10000, y - i)
            pen = QPen(Qt.GlobalColor.green, 5, Qt.PenStyle.SolidLine)
            pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
            painter.setPen(pen)
            painter.drawPoint(int(Settings.DESCTOP_WIDHT / 2), int(Settings.DESCTOP_HEIGHT / 2))
            if Settings.PAINT_POSx is not None:
                pen = QPen(Qt.GlobalColor.yellow, 5, Qt.PenStyle.SolidLine)
                pen.setCapStyle(Qt.PenCapStyle.MPenCapStyle)
                painter.setPen(pen)
                painter.drawPoint(int(Settings.PAINT_POSx), int(Settings.PAINT_POSy))
            painter.end()
            self.setPixmap(pixmap)

class LabelIma(QLabel):
    def __init__(self, parent):
        super().__init__(parent=parent)
        # self.move(100, 100)
        self.move(562, 210)
        #self.setGeometry(0, 0, 1900, 1800)
        # pixmap = QPixmap("hata17.jpg")
        # self.setPixmap(pixmap)

class Main(QWidget):
    mouse_old_pos = None
    label_old_pos = None
    old_pos = None
    mashtab = Settings.DEFAULT_MASHTAB
    FILE_NAME = None
    KMLfileName = Settings.KML_FILE_NAME

    def __init__(self):
        super().__init__()
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        self.setGeometry(0, 0, screen_width, screen_height)
        self.pixmapMap = QPixmap(Settings.FILE_NAME)
        #self.settings = Settings()
        # в самом начале установим координаты центральной точки в 0 - 0
        Settings.CENTR_LAT = 0
        Settings.CENTR_LON = 0

        self.supposedCentr = QPoint()
        self.doCentrPixels()
        #тут хранятся ТЕКУЩИЕ центральные координаты
        self.newCentr = ''
        # Получим список координат
        self.labelMap = QLabel(self)
        self.labelMap.move(350, 210)
        self.updateCentrPoint()
        self.addImage()

        # включим отслеживание мышки
        self.setMouseTracking(True)

        # Объект - Label с наложенной сеткой
        self.labelGrid = LabelGrid(self)
        self.labelIma = LabelIma(self)
        self.labelIma.move(200, 150)

        # Определим РЕАЛЬНОЕ (по координатам) расстояние между точками из KML
        # И отобразим на карте!
        # TODO : возможно, ресайзить нужно backgroung...

    # выдает координаты относительно ЦЕНТРА
    # ВНИМАНИЕ! Последовательность переменных играет роль!
    # Неверная последовательность приводит к противоположным координатам!!!
    def getCoordFromCentrPoint(self, x_ground, y_ground, x_current, y_current):
        grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
        gridStep = Settings.GRID_STEP
        pixelLenght = grid / gridStep
        delta_x = x_current - x_ground
        delta_y = y_ground - y_current
        lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        rads = atan2(delta_y, -delta_x)
        rads %= 2 * pi
        degs = degrees(rads) - 90
        # toDo: заменить сеттингс на get_method!
        need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.CENTR_LAT, Settings.CENTR_LON),
                                                                          degs).format_decimal()
        # вывод - в координатах.
        return need_point

    def setImageMap(self, filename):
        Settings.FILE_NAME = filename

    def getImageMap(self):
        return Settings.FILE_NAME

    def updateCentrPoint(self, newLat = 0, newLon = 0):
        # по-правильному, оно должно меняться ТОЛЬКО при перемещении
        # при рескейле - нет.
        if Settings.CENTR_LAT == 0 and Settings.CENTR_LON == 0:
            coordinatesFromFile = getCoordsFromKML(Settings.KML_FILE_NAME)
            Settings.LAT_NW, Settings.LON_NW = coordinatesFromFile['north'], coordinatesFromFile['west']

            center = getCoord(self.labelMap.pos().x(), self.labelMap.pos().y(), int(Settings.DESCTOP_WIDHT / 2),
                              int(Settings.DESCTOP_HEIGHT / 2))
            newLatitude, newLongitude = center.split(', ')
            Settings.CENTR_LAT = float(newLatitude)
            Settings.CENTR_LON = float(newLongitude)
            print('initcoords',  Settings.CENTR_LAT, Settings.CENTR_LON)
        else:
            Settings.CENTR_LAT = newLat
            Settings.CENTR_LON = newLon

    def doCentrPixels(self):
        self.supposedCentr.setX(int(Settings.DESCTOP_WIDHT / 2))
        self.supposedCentr.setY(int(Settings.DESCTOP_HEIGHT / 2))

    # получить точку X, Y в текущем масштабе по геогр. координатам
    def getPointByCoordsWide(self, LatBase, LonBase, Lat, Lon, Xbase, Ybase):
        point1 = (LatBase, LonBase)
        point2 = (Lat, Lon)
        real_dist = geodesic(point1, point2).meters
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP  #40m/80px = 0.5m in pixel
        real_dist_in_pixels = real_dist / pixelLenght
        lon1, lat1, lon2, lat2 = float(LonBase), float(LatBase), float(Lon), float(Lat)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        bearing1 = atan2(cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1), sin(lon2 - lon1) * cos(lat2))
        bearing = degrees(bearing1)
        relX = Xbase + (real_dist_in_pixels * cos(bearing1))
        relY = Ybase - (real_dist_in_pixels * sin(bearing1))
        point = (int(relX), int(relY))
        return point

    def getPointByCoords(self, Lat, Lon):
        point1 = (Settings.CENTR_LAT, Settings.CENTR_LON)
        point2 = (Lat, Lon)
        real_dist = geodesic(point1, point2).meters
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP  #40m/80px = 0.5m in pixel
        real_dist_in_pixels = real_dist / pixelLenght
        lon1, lat1, lon2, lat2 = float(Settings.CENTR_LON), float(Settings.CENTR_LAT), float(Lon), float(Lat)
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        bearing1 = atan2(cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1), sin(lon2 - lon1) * cos(lat2))
        bearing = degrees(bearing1)
        relX = int(Settings.DESCTOP_WIDHT / 2) + (real_dist_in_pixels * cos(bearing1))
        relY = int(Settings.DESCTOP_HEIGHT / 2) - (real_dist_in_pixels * sin(bearing1))
        point = (int(relX), int(relY))
        return point

    def getCoord(self, x_ground, y_ground, x_current, y_current):
        # https://github.com/geopy/geopy/blob/master/geopy/distance.py
        grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
        gridStep = Settings.GRID_STEP
        pixelLenght = grid / gridStep
        delta_x = x_current - x_ground
        delta_y = y_ground - y_current
        lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        rads = atan2(delta_y, -delta_x)
        rads %= 2 * pi
        degs = degrees(rads) - 90
        need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.LAT_NW, Settings.LON_NW),
                                                                          degs).format_decimal()
        # вывод - в координатах.
        return need_point

    def getCoordScale(self, x_ground, y_ground, x_current, y_current, koef):
        # https://github.com/geopy/geopy/blob/master/geopy/distance.py
        grid = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1])
        gridStep = Settings.GRID_STEP
        pixelLenght = grid / gridStep
        delta_x = x_current - x_ground
        delta_y = y_ground - y_current
        lengh_pixels = (((y_current - y_ground) ** (2)) + ((x_current - x_ground) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght / koef
        rads = atan2(delta_y, -delta_x)
        rads %= 2 * pi
        degs = degrees(rads) - 90
        need_point = geodesic(kilometers=lengh_meters / 1000).destination(Point(Settings.LAT_NW, Settings.LON_NW),
                                                                          degs).format_decimal()
        # вывод - в координатах.
        return need_point

    # первоначальная загрузка изображения на плоттер
    # TODO: добавить возможность передачи координаты для привязки сразу (в newWork есть идеи)
    def addImage(self):
        # первоначальное добавление картинки
        coordinatesFromFile = getCoordsFromKML(Settings.KML_FILE_NAME)
        Settings.LAT_NW, Settings.LON_NW, Settings.LAT_SE, Settings.LON_SE = coordinatesFromFile['north'], \
                                                                             coordinatesFromFile['west'], \
                                                                             coordinatesFromFile['south'], \
                                                                             coordinatesFromFile['east']
        real_distance_map = distanceBetweenPointsMeters(Settings.LAT_NW,
                                                        Settings.LON_NW,
                                                        Settings.LAT_SE,
                                                        Settings.LON_SE)
        x1, y1 = self.labelMap.pos().x(), self.labelMap.pos().y()
        x2, y2 = x1 + self.pixmapMap.width(), y1 + self.pixmapMap.height()
        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP
        lengh_pixels = (((y2 - y1) ** (2)) + ((x2 - x1) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        koef = real_distance_map / lengh_meters
        width_new = self.pixmapMap.width() * koef
        height_new = self.pixmapMap.height() * koef

        # TODO: сделать добавление, чтобы по координатам был (в центре экрана - нужная координата)
        self.labelMap.resize(int(width_new), int(height_new))
        self.labelMap.setPixmap(self.pixmapMap.scaled(int(width_new), int(height_new), Qt.KeepAspectRatio, Qt.FastTransformation))

    # увеличение / уменьшение картинки
    # TODO: возможно, добавить и смещение - отдельной функцией.
    def zoomMap(self):
        # все, что ту делается - берем изначальный image, и сжимаем (растягиваем) его
        # то есть, из исходного (как есть) делаем сразу готовый.
        coordinatesFromFile = getCoordsFromKML(Settings.KML_FILE_NAME)
        Settings.LAT_NW, Settings.LON_NW, Settings.LAT_SE, Settings.LON_SE = coordinatesFromFile['north'], \
                                                                             coordinatesFromFile['west'], \
                                                                             coordinatesFromFile['south'], \
                                                                             coordinatesFromFile['east']
        real_distance_map = distanceBetweenPointsMeters(Settings.LAT_NW,
                                                        Settings.LON_NW,
                                                        Settings.LAT_SE,
                                                        Settings.LON_SE)

        # давайте прикинем, где в текущих координатах будет край картинки
        newMapCorner = self.getPointByCoords(Settings.LAT_NW, Settings.LON_NW)
        Settings.PAINT_POSx, Settings.PAINT_POSy = newMapCorner
        self.labelMap.move(Settings.PAINT_POSx, Settings.PAINT_POSy)
        x1, y1 = self.labelMap.pos().x(), self.labelMap.pos().y()
        x2, y2 = x1 + self.pixmapMap.width(), y1 + self.pixmapMap.height()

        Settings.POS_X = self.labelMap.pos().x()
        Settings.POS_Y = self.labelMap.pos().y()

        pixelLenght = int(Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]) / Settings.GRID_STEP
        lengh_pixels = (((y2 - y1) ** (2)) + ((x2 - x1) ** (2))) ** (0.5)
        lengh_meters = lengh_pixels * pixelLenght
        koef = real_distance_map / lengh_meters

        # пересчитаем картинку и изменим ее
        width_new = self.pixmapMap.width() * koef
        height_new = self.pixmapMap.height() * koef

        self.labelMap.resize(int(width_new), int(height_new))
        self.labelMap.setPixmap(
            self.pixmapMap.scaled(
                int(width_new),
                int(height_new),
                Qt.KeepAspectRatio,
                Qt.FastTransformation))

    def updateScale(self, scale):
        if (scale > Settings.CURRENT_MASHTAB):
            Settings.ZOOMING = False
        else:
            Settings.ZOOMING = True
        Settings.CURRENT_MASHTAB = scale
        self.zoomMap()

    def createGrid(self):
        if Settings.NEED_GRID == 0:
            Settings.NEED_GRID = 1
            self.update()
        else:
            Settings.NEED_GRID = 0
            self.update()

    # def updateSliderScale(self):
    #     Settings.CURRENT_MASHTAB = self.scale.value()
    #     scale_grid = Settings.GRID_SCALE[Settings.CURRENT_MASHTAB - 1]
    #     self.rescaleMap()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = event.pos()  # позиция Мыши
            self.label_old_pos = self.labelMap.pos()  # позиция Карты
            print(getCoord(self.labelMap.pos().x(), self.labelMap.pos().y(), self.mouse_old_pos.x(),
                           self.mouse_old_pos.y()), " ... mouse on: ", event.pos())

            tochka = self.getCoordFromCentrPoint(int(Settings.DESCTOP_WIDHT / 2),
                                                         int(Settings.DESCTOP_HEIGHT / 2),
                                                         event.pos().x(),
                                                         event.pos().y())
            curLat, curLon = tochka.split(', ')
            print('click! ', curLat, curLon)
            #print('vot: ', self.getPointByCoords(curLat, curLon))
        if event.button() == Qt.RightButton:
            #d = distanceInPixels(self.labelMap.pos().x(), self.labelMap.pos().y(), Settings.DESCTOP_WIDHT / 2, Settings.DESCTOP_HEIGHT / 2)
            print('center is: ', Settings.CENTR_LAT, ',', Settings.CENTR_LON)
            if self.labelIma.isVisible():
                self.labelIma.setVisible(False)
            else:
                self.labelIma.setVisible(True)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_old_pos = None
            self.doCentrPixels()
            if self.newCentr != '':
                Settings.CENTR_LAT, Settings.CENTR_LON = self.newCentr.split(', ')

    def mouseMoveEvent(self, event):
        if not self.mouse_old_pos:
            return
        # разница в передвижении:
        delta = event.pos() - self.mouse_old_pos
        #self.update()
        new_pos_label_map = self.label_old_pos + delta
        self.labelMap.move(new_pos_label_map)

        # после движения мышкой - обновим координаты угла
        Settings.POS_X = new_pos_label_map.x()
        Settings.POS_Y = new_pos_label_map.y()

        #пересчитаем координаты нового центра:
        new_pos_center = self.supposedCentr + delta
        self.newCentr = self.getCoordFromCentrPoint(new_pos_center.x(), new_pos_center.y(),
                                               int(Settings.DESCTOP_WIDHT / 2), int(Settings.DESCTOP_HEIGHT / 2))


class Login(QDialog):
    def __init__(self, parent=None):
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        Settings.DESCTOP_WIDHT = screen_width
        Settings.DESCTOP_HEIGHT = screen_height
        print(Settings.DESCTOP_WIDHT, Settings.DESCTOP_HEIGHT)
        super(Login, self).__init__(parent)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QHBoxLayout(self)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        result = ['false', '', '']
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open image (.jpg, .png) file", "",
                                                  "JPEG(*.jpg *.jpeg);;PNG(*.png *.PNG);;All Files(*.*)",
                                                  options=options)
        # распарсим на ФАЙЛ и ПУТЬ
        filename = Path(fileName).name
        dir = Path(fileName).parent
        # распарсим ФАЙЛ на ИМЯ и РАСШИРЕНИЕ
        fileSourseName, fileSourseExtension = filename.split('.')
        KMLfile = None

        with os.scandir(dir) as files:
            for file in files:
                if file.is_file():
                    KMLfilename, KMLfile_extension = file.name.split('.')
                    if (KMLfile_extension.upper() == "KML") and (KMLfilename.upper() == fileSourseName.upper()):
                        KMLfile = KMLfilename + '.' + KMLfile_extension
        if (KMLfile != None):
            Settings.FILE_NAME = filename
            Settings.KML_FILE_NAME = KMLfile
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Chosen image file have not .kml file around!')


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.myWidget = Main()
        self.exitAction = QAction(QIcon('icons/exit.png'), 'Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)

        self.mainmenu = self.menuBar()
        # File ->
        self.menuFile = self.mainmenu.addMenu('File')
        # File -> Open
        self.menuOpen = self.menuFile.addMenu('Open...')
        # File -> Open -> Open Map File
        self.openMapFileAction = QAction(QIcon('icons/open.png'), 'Map File', self)
        self.openMapFileAction.triggered.connect(self.createGrid)
        self.menuOpenMap = self.menuOpen.addAction(self.openMapFileAction)
        # File -> Open -> Open Depth File
        self.menuOpenDepth = self.menuOpen.addAction('Depth File')
        # File.actions
        self.menuFile.addAction(self.exitAction)

        # Settings ->
        self.menuSettings = self.mainmenu.addMenu('Settings')
        self.menuGridAction = QAction(QIcon('grid.png'), 'Add Grid', self)
        self.menuGridAction.triggered.connect(self.createGrid)
        self.menuGrid = self.menuSettings.addAction(self.menuGridAction)

        # self.toolbar = self.addToolBar('Exit')

        self.setCentralWidget(self.myWidget)

        self.statusBar = self.statusBar()
        strStatus = str(Settings().getGridScale()) + 'm, Grid=' + str(Settings().getScale())
        self.statusBar.showMessage(strStatus)

        self.scale = QSlider(self)
        self.scale.invertedControls()
        self.scale.setMinimum(1)
        self.scale.setMaximum(9)
        self.scale.setPageStep(1)
        self.scale.setSliderPosition(Settings().getScale())
        self.scale.setTickInterval(1)
        self.scale.setOrientation(QtCore.Qt.Vertical)
        self.scale.setTickPosition(QtWidgets.QSlider.TicksAbove)
        self.labelScale1 = QLabel(self)
        self.labelScale1.setText('1')
        self.labelScale1.setGeometry(1560, 590, 50, 50)
        self.labelScale9 = QLabel(self)
        self.labelScale9.setText('9')
        self.labelScale9.setGeometry(1560, 300, 50, 50)
        self.labelScale5 = QLabel(self)
        self.labelScale5.setText('5')
        self.labelScale5.setGeometry(1560, 444, 50, 50)
        if Settings.DESCTOP_WIDHT is not None:
            self.scale.setGeometry(int(Settings.DESCTOP_WIDHT - 30), int(Settings.DESCTOP_HEIGHT/2) - 150, 25, 300)
        else:
            self.scale.setGeometry(1575, 320, 22, 300)
        self.scale.valueChanged.connect(self.updateScale)

    def updateScale(self):
        current_scale = self.scale.value()
        self.myWidget.updateScale(current_scale)
        strStatus = str(Settings().getGridScale()) + 'm, Grid=' + str(Settings().getScale())
        self.statusBar.showMessage(strStatus)

    def createGrid(self):
        self.myWidget.createGrid()


if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    login = Login()

    if login.exec_() == QtWidgets.QDialog.Accepted:
        window = MainWindow()
        window.showFullScreen()
        sys.exit(app.exec_())