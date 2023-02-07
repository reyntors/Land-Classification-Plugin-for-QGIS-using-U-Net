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
from lcp import load_model
import torchvision.transforms as transforms

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
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        model = load_model.model
        print(model)
        print(model.state_dict())
                

        x = torch.randn(1, 10)
        y = model(x)
        print(y)

        if model is not None:
            print("Model loaded successfully")
        else:
            print("Failed to load the model")

        
        
        """Triggered when the classify button is clicked."""
         # Get the input image
        input_path = self.ui.file.filePath()
        input_image = Image.open(input_path)
        
        # Reduce the size of the image
        

        # Preprocess the input image
        # Preprocess the input image
        input_array = np.array(input_image)
        batch_size = 1
        num_channels = input_array.shape[-1]
        height = input_array.shape[0]
        width = input_array.shape[1]
        expected_input_shape = (batch_size, num_channels, height, width)
        input_array = np.resize(input_array, expected_input_shape)

        input_tensor = torch.Tensor(input_array)
        # Reshape the input tensor if needed
        input_tensor = input_tensor.view(*expected_input_shape)
        print("Reshaped Input Tensor Shape: ", input_tensor.shape)
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
       

            
        
        # Use the model for inference
        with torch.no_grad(): # turn off gradient calculation
            output_tensor = model(input_tensor)
        
        output_image = output_tensor.detach().numpy()
        
        # Convert the output tensor to image format
        
        output_image = output_image.squeeze()
        if len(output_image.shape) == 1:
            output_image = np.expand_dims(output_image, axis=0)

        output_scale = np.tile([0.229, 0.224, 0.225], (output_image.shape[0], 1)) + np.tile([0.485, 0.456, 0.406], (output_image.shape[0], 1))
        output_scale = np.tile(output_scale, (output_image.shape[0], 1))
        output_image = output_image * output_scale
        # Save the output image
        output_path = "E:/Development/Qgis plugin/lcp/Output/output_image.jpg"
        output_image.save(output_path)

        pixmap = QPixmap(output_image)
        pixmap_item = QGraphicsPixmapItem(pixmap)

            # Create a QGraphicsScene and add the pixmap item to it
        scene = QGraphicsScene()
        scene.addItem(pixmap_item)

            # Set the scene rect to the pixmap size
        scene.setSceneRect(pixmap_item.boundingRect())
        self.ui.graphicsView2.setRenderHint(QPainter.Antialiasing)
        self.ui.graphicsView2.setRenderHint(QPainter.SmoothPixmapTransform)
        self.ui.graphicsView2.setScene(scene)

            # Fit the view to the pixmap
        self.ui.graphicsView2.fitInView(pixmap_item, QtCore.Qt.KeepAspectRatio)
       

            
        
    
