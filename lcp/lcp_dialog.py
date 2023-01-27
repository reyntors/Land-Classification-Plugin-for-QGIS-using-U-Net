import os
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QMainWindow, QToolButton
from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingMultiStepFeedback, QgsProcessingOutputRasterLayer, QgsProcessingParameterExtent, QgsProcessingParameterRasterLayer, QgsRasterLayer
import sys
from .clip import ClipRasterByExtent
from PyQt5.QtWidgets import QgsFileWidget


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'lcp_dialog_base.ui'))   


class LandClassificationPluginDialog(QtWidgets.QDialog, FORM_CLASS,):
    def __init__(self, parent=None):
        super(LandClassificationPluginDialog, self).__init__(parent)
        """Constructor."""
        self.setupUi(self)
        self.clip.clicked.connect(self.run)
        self.forSelectFile.clicked.connect(self.selectFile)

    def run(self):
        print("Hello")

    def selectFile(self):
        print("selected")
       
   



       
        


        

