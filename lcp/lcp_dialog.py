import os
from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QMainWindow, QToolButton, QComboBox, QMessageBox, QLineEdit, QGraphicsPixmapItem, QLabel, QFileDialog, QProgressBar
from qgis.core import  (QgsProcessing, QgsProcessingAlgorithm, 
                       QgsProcessingMultiStepFeedback, QgsProcessingOutputRasterLayer, 
                       QgsProcessingParameterExtent, QgsProcessingParameterRasterLayer, 
                       QgsRasterLayer, QgsVectorLayer, QgsProject, QgsMapLayer, QgsPointXY, QgsWkbTypes, QgsPointXY)
from qgis.PyQt.QtWidgets import QRadioButton
import sys
from qgis.utils import iface
from osgeo import gdal
import processing
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from osgeo import gdal_array, osr
import numpy as np
from PIL import Image
from qgis.gui import QgsMapTool
import torch
import torch.nn as nn

import torchvision.transforms as transforms
from collections import OrderedDict
import collections
import pickle
from .load_model import Generator

# #imported by Mayol hehe
# from qgis.gui import QgsMapCanvas
# from PyQt5.QtGui import QPen
# from PyQt5.QtGui import QBrush
# from PyQt5.QtCore import Qt, QPointF
# from PyQt5.QtGui import QImage, QPainter, QColor
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QAction, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QDialog
# from qgis.core import QgsRasterLayer, QgsProject, QgsRectangle
# from qgis.gui import QgsMapCanvas, QgsMapCanvasItem

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'lcp_dialog_base.ui'))  




class LandClassificationPluginDialog(QtWidgets.QDialog, nn.Module, FORM_CLASS):
    def __init__(self, parent=None):
        super(LandClassificationPluginDialog, self).__init__(parent)
        """Constructor."""
        QtWidgets.QDialog.__init__(self)
        self.ui = FORM_CLASS()      
                
        
        self.ui.setupUi(self)
        self.ui.progressBar.setVisible(False)
        self.ui.autoCoordinates.clicked.connect(self.map_canvas)
        self.ui.classify.clicked.connect(self.classification)
        # self.ui.drawButton.clicked.connect(self.draw_canvas)

    
    def map_canvas(self):
        
        
        # Get the active layer in QGIS
        active_layer = iface.activeLayer()
        input_raster = active_layer.dataProvider().dataSourceUri()
        
        
        output_path = self.ui.File.filePath()
        
        if output_path:
            
            output_raster = os.path.join(output_path)
        else:
            QMessageBox.warning(self, "Warning", "File directory not set. Please select a directory for the output raster.")
            return
        
        # Read the input raster file
        src_ds = gdal.Open(input_raster)

        # Get the current map canvas extent
        extent = iface.mapCanvas().extent()
        xmin, ymin = extent.xMinimum(), extent.yMinimum()
        xmax, ymax = extent.xMaximum(), extent.yMaximum()
        xres = (xmax - xmin) / src_ds.RasterXSize 
        yres = (ymax - ymin) / src_ds.RasterYSize

        raster_xsize = src_ds.RasterXSize // 2
        raster_ysize = src_ds.RasterYSize // 2
        

        # Set the extent values in two QLineEdit widgets
        
        
        self.ui.Upxlon.setText(str(xmin))
        self.ui.Upylat.setText(str(ymin))
        self.ui.lrxlon.setText(str(xmax))
        self.ui.lrylat.setText(str(ymax))
        
        self.ui.clip.clicked.connect(lambda: self.perform_clip(src_ds, output_raster, xmin, xmax, ymax, xres, yres, raster_xsize, raster_ysize)) 
   
        
    def perform_clip(self, src_ds, output_raster, xmin, xmax, ymax, xres, yres, raster_xsize, raster_ysize):
        
        
        self.ui.progressBar.show()
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)

            
        dst_ds = gdal.GetDriverByName('GTiff').Create(output_raster, raster_xsize, raster_ysize, src_ds.RasterCount, gdal.GDT_Byte)
            
        error = dst_ds.SetGeoTransform((xmin, xres * 2, 0, ymax, 0, -yres * 2))
        if error !=0:
            print("SetGeoTransform is failed!", error)
        else:
            print("SetGeoTransform is succesful!", error)                  
        dst_ds.SetProjection(src_ds.GetProjection())

            
            # Perform the clip
        error_code = gdal.ReprojectImage(src_ds, dst_ds, src_ds.GetProjection(), dst_ds.GetProjection(), gdal.GRA_Average)
        if error_code != 0:
            print("Error: Reprojection failed with error code", error_code)
            return
        else:
            print("Succesfully Reprojection", error_code)

            # Load the output raster
            
            # Close the datasets
        src_ds = None
        dst_ds = None

        self.ui.progressBar.setValue(100)
        self.ui.progressBar.hide()

            
        pixmap = QPixmap(output_raster)
        pixmap_item = QGraphicsPixmapItem(pixmap)

            # Create a QGraphicsScene and add the pixmap item to it
        scene = QGraphicsScene()
        scene.addItem(pixmap_item)

            # Set the scene rect to the pixmap size
        scene.setSceneRect(pixmap_item.boundingRect())
        self.ui.View.setRenderHint(QPainter.Antialiasing)
        self.ui.View.setRenderHint(QPainter.SmoothPixmapTransform)
        self.ui.View.setScene(scene)

            # Fit the view to the pixmap
        self.ui.View.fitInView(pixmap_item, QtCore.Qt.KeepAspectRatio)
       

            
            
        
            
            #Add the clipped raster to the map canvas
        iface.addRasterLayer(output_raster, "Clipped Raster")

    def classification(self):

       # Load the pretrained PyTorch model
        model = Generator()
        checkpoint = torch.load("E:/Development/Qgis plugin/lcp/pretrained_model/gen.pth.tar", map_location=torch.device('cpu'))

        # Separate the state dict and optimizer
        model_state_dict = checkpoint["state_dict"]
        optimizer_state_dict = checkpoint["optimizer"]

        # Load the model's state dict
        model.load_state_dict(model_state_dict)

        
        try:
            model.load_state_dict(torch.load("E:/Development/Qgis plugin/lcp/pretrained_model/gen.pth.tar", map_location=torch.device('cpu')))
        except RuntimeError as e:
            print(e)
        model.eval()
        print(type(model))
        print(model)
        if model is not None:
            print("Model successfully loaded!")
        else:
            print("Model Failed to load!")

        
        
        # Get the input image
        input_path = self.ui.file.filePath()
        input_image = Image.open(input_path)

        # Pre-process the input image
        transform = transforms.Compose([
            
            transforms.Resize(256),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        input_tensor = transform(input_image).unsqueeze(0)

        

        pixmap = QPixmap(input_path)
        pixmap_item = QGraphicsPixmapItem(pixmap)

            # Create a QGraphicsScene and add the pixmap item to it
        scene = QGraphicsScene()
        scene.addItem(pixmap_item)

            # Set the scene rect to the pixmap size
        scene.setSceneRect(pixmap_item.boundingRect())
        self.ui.graphicsView1.setRenderHint(QPainter.Antialiasing)
        self.ui.graphicsView1.setRenderHint(QPainter.SmoothPixmapTransform)
        self.ui.graphicsView1.setScene(scene)

            # Fit the view to the pixmap
        self.ui.graphicsView1.fitInView(pixmap_item, QtCore.Qt.KeepAspectRatio)

        # Run the input tensor through the model
        with torch.no_grad():
            output = model(input_tensor)

        # Post-process the output tensor
        output = output.detach().squeeze().clamp(-1, 1).add(1).div(2).mul(255).permute(1, 2, 0).to(torch.uint8).numpy()

        # Save the output image
        output_image = Image.fromarray(output)
        output_image.save("output.png")

        # Convert the output image to a QPixmap
        pixmap = QPixmap("output.png")

        # Create a QGraphicsPixmapItem from the QPixmap
        pixmap_item = QGraphicsPixmapItem(pixmap)

        # Create a QGraphicsScene and add the pixmap item to it
        scene = QGraphicsScene()
        scene.addItem(pixmap_item)

        # Set the scene rect to the pixmap size
        scene.setSceneRect(pixmap_item.boundingRect())

        # Set the render hints for the graphics view
        self.ui.graphicsView2.setRenderHint(QPainter.Antialiasing)
        self.ui.graphicsView2.setRenderHint(QPainter.SmoothPixmapTransform)

        # Set the scene for the graphics view
        self.ui.graphicsView2.setScene(scene)

        # Fit the view to the pixmap
        self.ui.graphicsView2.fitInView(pixmap_item, QtCore.Qt.KeepAspectRatio)

                

    
