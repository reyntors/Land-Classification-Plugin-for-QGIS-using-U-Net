
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

        x1, y1 = self.startPoint.x(), self.startPoint.y()
        x2, y2 = self.endPoint.x(), self.endPoint.y()

        if x2 < x1 and y2 < y1:
            x1, y1, x2, y2 = x2, y2, x1, y1

        self.rectangleCreated.emit(x1, y1, x2, y2)

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return
        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)

        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return
        
        side_length = max(endPoint.x() - startPoint.x(), endPoint.y() - startPoint.y())
        # Get the end point of the square
        endPoint = QgsPointXY(startPoint.x() + side_length, startPoint.y() - side_length)

        # Get the upper-left point and lower-right point of the rectangle
        x1, y1 = min(startPoint.x(), endPoint.x()), min(startPoint.y(), endPoint.y())
        x2, y2 = max(startPoint.x(), endPoint.x()), max(startPoint.y(), endPoint.y())

        point1 = QgsPointXY(x1, y1)
        point2 = QgsPointXY(x1, y2)
        point3 = QgsPointXY(x2, y2)
        point4 = QgsPointXY(x2, y1)

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)  # true to update canvas
        self.rubberBand.show()

    def transformCoordinates(self):
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None

        # Define point coordinates in EPSG:4326
        x1, y1 = self.startPoint.x(), self.startPoint.y()
        x2, y2 = self.endPoint.x(), self.endPoint.y()

        # Create a coordinate transform to transform the points from the canvas' CRS to EPSG:4326
        crsSrc = self.canvas.mapSettings().destinationCrs()
        crsDest = QgsCoordinateReferenceSystem(4326)
        xform = QgsCoordinateTransform(crsSrc, crsDest, QgsProject.instance())
        pt1 = QgsPointXY(x1, y1)
        pt2 = QgsPointXY(x2, y2)
            # Transform the points to EPSG:4326
        pt1 = xform.transform(pt1)
        pt2 = xform.transform(pt2)

        # Assign the transformed coordinates to x1, y1 and x2, y2
        x1, y1 = pt1.x(), pt1.y()
        x2, y2 = pt2.x(), pt2.y()

        # Check if the transformed coordinates are valid
        if x1 == x2 or y1 == y2:
            return None

        # Swap coordinates if necessary so that x1 <= x2 and y1 <= y2
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        # Set the transformed coordinates to the start and end points
        self.startPoint = QgsPointXY(x1, y1)
        self.endPoint = QgsPointXY(x2, y2)

    def deactivate(self):
        self.rubberBand.hide()
        QgsMapTool.deactivate(self)
        
