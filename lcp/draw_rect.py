from qgis.gui import QgsMapTool, QgsRubberBand
from qgis.core import QgsWkbTypes, QgsPointXY, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import pyqtSignal, QPoint
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPoint
from PyQt5 import Qt
from PyQt5 import QtCore

class RectangleAreaTool(QgsMapTool):

    rectangleCreated = pyqtSignal(float, float, float, float)

    def __init__(self, canvas, action):
        QgsMapTool.__init__(self, canvas)

        self.canvas = canvas
        self.active = False
        self.setAction(action)
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        mFillColor = QColor(0, 0, 255, 63)
        self.rubberBand.setColor(mFillColor)
        self.rubberBand.setWidth(1)
        self.reset()

       
        
    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    def canvasReleaseEvent(self, e):
        
        self.isEmittingPoint = False
        self.rubberBand.hide()
        self.transformCoordinates()
        self.rectangleCreated.emit(self.startPoint.x(), self.startPoint.y(), self.endPoint.x(), self.endPoint.y())
        
    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates( e.pos() )
        self.showRect(self.startPoint, self.endPoint)
        
    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        

        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return

        # Get the side length of the square
        side_length = max(endPoint.x() - startPoint.x(), endPoint.y() - startPoint.y())

        # Check if the side length is within the minimum and maximum dimensions
       

        # Get the end point of the square
        endPoint = QgsPointXY(startPoint.x() + side_length, startPoint.y() + side_length)

        point1 = QgsPointXY(startPoint.x(), startPoint.y())
        point2 = QgsPointXY(startPoint.x(), endPoint.y())
        point3 = QgsPointXY(endPoint.x(), endPoint.y())
        point4 = QgsPointXY(endPoint.x(), startPoint.y())

        
        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)    # true to update canvas
        self.rubberBand.show()

        

    def transformCoordinates(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None

        # Defining the crs from src and destiny
        epsg = self.canvas.mapSettings().destinationCrs().authid()
        crsSrc = QgsCoordinateReferenceSystem(epsg)
        crsDest = QgsCoordinateReferenceSystem(4326)
        # Creating a transformer
        coordinateTransformer = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        # Transforming the points
        self.startPoint = coordinateTransformer.transform(self.startPoint)
        self.endPoint = coordinateTransformer.transform(self.endPoint)

    def deactivate(self):
        self.rubberBand.hide()
        QgsMapTool.deactivate(self)
        