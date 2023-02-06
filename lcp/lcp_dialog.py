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

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'lcp_dialog_base.ui'))   


class LandClassificationPluginDialog(QtWidgets.QDialog, nn.Module, FORM_CLASS):
    def __init__(self, parent=None):
        super(LandClassificationPluginDialog, self).__init__(parent)
        """Constructor."""
        QtWidgets.QDialog.__init__(self)
        self.ui = FORM_CLASS()      
                # Load the saved model
       
        
        self.ui.setupUi(self)
        self.ui.progressBar.setVisible(False)
        self.ui.autoCoordinates.clicked.connect(self.map_canvas)
        self.ui.classify.clicked.connect(self.classification)
       
        self.model = LandClassificationPluginDialog()
        self.model.load_state_dict(torch.load("E:/Development/Qgis plugin/lcp/pretrained_model/sat2map.pth", map_location=torch.device('cpu')))

      

        self.model.eval() # set the model to evaluation mode
       
                
           
   
    def map_canvas(self):

        import qgis.utils
        
      
        
        
        # Get the active layer in QGIS
        active_layer = qgis.utils.iface.activeLayer()
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
        """Triggered when the classify button is clicked."""
        # Get the input image
        # Set the model to evaluation mode
        

        # Use the model for inference
        input_image = self.ui.file.filePath()
        input_image = input_image.unsqueeze(0) # add a batch dimension to the image
        input_image = input_image.to(device)

        # Show the output image
         # Your code to show the output image
        with torch.no_grad(): # turn off gradient calculation
             output_image = model(input_image)
        
        output_image = output_image.cpu().numpy()[0]
        output_image = 'E:/Development/Qgis plugin/lcp/Output/'
        