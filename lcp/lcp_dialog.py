import os

from PyQt5 import uic, QtCore, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QImage, QColor
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QApplication, QMainWindow, QToolButton, QComboBox, QMessageBox, QLineEdit, QGraphicsPixmapItem, QLabel, QFileDialog, QProgressBar

from qgis.PyQt.QtWidgets import QRadioButton
import sys
from qgis.utils import iface
from osgeo import gdal
import processing
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout
from osgeo import gdal
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from PyQt5.QtWidgets import QAction
import numpy as np
import torchvision.transforms as transforms

from .load_model import Generator
import cv2
from .draw_rect import RectangleAreaTool
import pyproj
from PyQt5.QtWidgets import QListWidget
from qgis.core import QgsLayout, QgsProject
from PyQt5.QtCore import QSizeF
from PyQt5.QtWidgets import QLabel, QApplication
from PyQt5.QtCore import QFile
from qgis.core import (QgsProject, QgsLayout, QgsPrintLayout, QgsReadWriteContext, 
                       QgsLayoutItemMap, QgsLayoutPoint, QgsUnitTypes, QgsLayoutSize, 
                       QgsLayoutItemLabel, QgsLayerTree, QgsLayoutItemLegend, QgsLayoutItemScaleBar, 
                       QgsLayoutItemPicture, QgsLayoutExporter, QgsLayoutItemPage)
from PyQt5.QtXml import QDomDocument
from PyQt5.QtGui import QFont





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
        self.ui.progressBar3.setVisible(False)
        self.ui.autoCoordinates.clicked.connect(self.map_canvas)
        self.ui.drawButton.clicked.connect(self.draw_raster)
        self.ui.clip.clicked.connect(self.draw_raster)
        self.ui.File.setFilter("Image files (.png *.jpg *.tif);;PNG(*.png);;JPG(*.jpg);;TIFF(*.tif);;All files (*.*)")
        self.ui.file.fileChanged.connect(self.classification1)
        self.ui.classify.clicked.connect(self.classification2)
        self.ui.layout.clicked.connect(self.layout)
        
    
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
        
        self.ui.clip.clicked.connect(lambda: self.clip(src_ds, output_raster, xmin, xmax, ymax, xres, yres, raster_xsize, raster_ysize)) 
   
        
    def clip(self, src_ds, output_raster, xmin, xmax, ymax, xres, yres, raster_xsize, raster_ysize):
        
        
        self.ui.progressBar.show()
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)

            
        dst_ds = gdal.GetDriverByName('GTiff').Create(output_raster, raster_xsize, raster_ysize, src_ds.RasterCount, gdal.GDT_Byte)
        print(raster_xsize,raster_ysize)   
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
       
        iface.addRasterLayer(output_raster, "Clipped Raster")

 

    def draw_raster(self):
        
        active_layer = iface.activeLayer()
        input_raster = active_layer.dataProvider().dataSourceUri()


        output_path = self.ui.File.filePath()
        
        if output_path:
            
            output_raster = os.path.join(output_path)
        

        # Read the input raster file
        src_ds = gdal.Open(input_raster)  
        
        btn_click = self.sender()   
        if btn_click is self.ui.clip:
            if output_path:      
               print("canvas")
          # Get the extent values in two QLineEdit widgets
               valueux = self.ui.Upxlon.text()
               floatvalux = float(valueux)
               valueuy = self.ui.Upylat.text()
               floatvaluy = float(valueuy)
               valuelx = self.ui.lrxlon.text()  
               floatvallx = float(valuelx)
               valuely = self.ui.lrylat.text()
               floatvally = float(valuely)

               xmin, ymin = floatvalux, floatvaluy
               xmax, ymax = floatvallx, floatvally

               xres = (xmax - xmin) / src_ds.RasterXSize 
               yres = (ymax - ymin) / src_ds.RasterYSize

               raster_xsize = src_ds.RasterXSize // 2
               raster_ysize = src_ds.RasterYSize // 2

        
               self.perform_clip(src_ds, output_raster, xmin, xmax, ymax, xres, yres, raster_xsize, raster_ysize)
            else:
                 QMessageBox.warning(self, "Warning", "File directory not set. Please select a directory for the output raster.")
                 return

        elif btn_click is self.ui.drawButton :
                print("draw")
                self.hide()
                action = QAction(iface.mainWindow())
                self.clip = RectangleAreaTool(iface.mapCanvas(), action)
                iface.mapCanvas().setMapTool(self.clip)
                self.clip.rectangleCreated.connect(self.update_coordinates)

              

        elif btn_click is self.ui.autoCoordinates:
                print("display ni")
                extent = iface.mapCanvas().extent()
                xmin, ymin = extent.xMinimum(), extent.yMinimum()
                xmax, ymax = extent.xMaximum(), extent.yMaximum()

                # Set the extent values in two QLineEdit widgets
                self.ui.Upxlon.setText(str(xmin))
                self.ui.Upylat.setText(str(ymin))
                self.ui.lrxlon.setText(str(xmax))
                self.ui.lrylat.setText(str(ymax))
                
    def update_coordinates(self, startX, startY, endX, endY):
    
        
         # Get the reference to the active map canvas
        canvas = iface.mapCanvas()

        # Get the active layer
        layer = canvas.currentLayer()

        # Get the layer's CRS
        layer_crs = layer.crs()

        # Print the EPSG code of the layer's CRS
        print(layer_crs.authid())
        if layer_crs.authid() == "EPSG:4326":
            # Define input and output coordinate reference systems
            wgs84 = pyproj.Proj('EPSG:4326')
            utm51n = pyproj.Proj('EPSG:32651')

            # Define point coordinates in EPSG:4326
            x1, y1 = startX, startY
            x2, y2 = endX, endY

        elif layer_crs.authid() == "EPSG:32651":
            wgs84 = pyproj.Proj(proj='latlong', datum='WGS84')
            utm51n = pyproj.Proj(proj='utm', zone=51, datum='WGS84')

            x1, y1 = startX, startY
            x2, y2 = endX, endY

            x1, y1 = pyproj.transform(wgs84, utm51n, x1, y1)
            x2, y2 = pyproj.transform(wgs84, utm51n, x2, y2)

        self.ui.Upxlon.setText(str(x1))
        self.ui.Upylat.setText(str(y1))
        self.ui.lrxlon.setText(str(x2))
        self.ui.lrylat.setText(str(y2))


        print(x1, y1)
        print(x2, y2)
    
        iface.mapCanvas().unsetMapTool(self.clip)
        self.show()
                    
    def perform_clip(self, src_ds, output_raster, xmin, xmax, ymax, xres, yres, raster_xsize, raster_ysize):
        
        
        self.ui.progressBar.show()
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(0)

        

          
        dst_ds = gdal.GetDriverByName('GTiff').Create(output_raster, raster_xsize, raster_ysize, src_ds.RasterCount, gdal.GDT_Byte)
        self.ui.progressBar.setValue(10)   
        error = dst_ds.SetGeoTransform((xmin, xres * 2, 0, ymax, 0, -yres * 2))
        self.ui.progressBar.setValue(20)
        if error !=0:
            print("SetGeoTransform is failed!", error)
        else:
            print("SetGeoTransform is succesful!", error)                  
        dst_ds.SetProjection(src_ds.GetProjection())
        self.ui.progressBar.setValue(30)
      
            # Perform the clip
        error_code = gdal.ReprojectImage(src_ds, dst_ds, src_ds.GetProjection(), dst_ds.GetProjection(), gdal.GRA_NearestNeighbour)
        self.ui.progressBar.setValue(50)
        if error_code != 0:
            print("Error: Reprojection failed with error code", error_code)
            return
        else:
            print("Succesfully Reprojection", error_code)
        
        # Close the datasets
        src_ds = None
        dst_ds = None

        
        input_image = Image.open(output_raster)
        input_image = input_image.resize((600, 600))
        input_image = input_image.convert('RGB')
        
        pixmap = QPixmap.fromImage(QtGui.QImage(input_image.tobytes(), input_image.size[0], input_image.size[1], QtGui.QImage.Format_RGB888))
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
       
        iface.addRasterLayer(output_raster, "Clipped Raster" )

        self.ui.progressBar.setValue(100)
        self.ui.progressBar.hide() 

    
    def classification1(self):
         
        # Get the input image
        input_path = self.ui.file.filePath()
        if input_path:
            
            input_image = Image.open(input_path)
            input_image = input_image.resize((600, 600))
            input_image = input_image.convert('RGB')
            pixmap = QPixmap.fromImage(QtGui.QImage(input_image.tobytes(), input_image.size[0], input_image.size[1], QtGui.QImage.Format_RGB888))
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

            
            
        
            self.ui.classify.clicked.connect(lambda: self.classification2(input_image))

    def classification2(self, input_image):
                
            if input_image:    
                self.ui.progressBar3.show()
                self.ui.progressBar3.setRange(0, 100)
                self.ui.progressBar3.setValue(0) 

            
                model = Generator()           
                dir_path = os.path.dirname(os.path.realpath(__file__))
                model_path = os.path.join(dir_path, 'pre_trained model', 'gen.pth.tar')
                checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
                            
                model_state_dict = checkpoint["state_dict"]
                            
                optimizer_state_dict = checkpoint["optimizer"]
                            
                model.load_state_dict(model_state_dict, optimizer_state_dict)
                            
                model.eval()

                

                self.ui.progressBar3.setValue(50)
                        # Pre-process the input image
                transform = transforms.Compose([
                                        
                            transforms.Resize((256, 256)),
                            transforms.ToTensor(),
                            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
                                    ])
                input_tensor = transform(input_image).unsqueeze(0)
                                    
                        # Run the input tensor through the model
                with torch.no_grad():
                        output = model(input_tensor)
    
                                            # Post-process the output tensor
                output = output.detach().squeeze().clamp(-1, 1).add(1).div(2).mul(255).permute(1, 2, 0).to(torch.uint8).numpy()

                        
                input_path = self.ui.file
                line_edit = input_path.lineEdit()
                current_file_path = line_edit.text()
                current_directory, file_name = os.path.split(current_file_path)
                file_path = os.path.join(current_directory, file_name)
                current_directory = current_directory.replace('\\', '/')

                # check if the output folder is present 
                folder_name = "Output"

                if os.path.exists(os.path.join(current_directory, folder_name)):
                    print("The folder exists in the directory.")
                else:
                    print("The folder does not exist in the directory.")
                    os.makedirs(os.path.join(current_directory, folder_name))

                # Save the output image
                output_image = Image.fromarray(output)
                output_image.save(current_directory+"/Output/output.png")

                # Convert the output image to a QPixmap
                pixmap = QPixmap(current_directory+"/Output/output.png")

                        # Create a QGraphicsPixmapItem from the QPixmap
                pixmap_item = QGraphicsPixmapItem(pixmap)

                        # Create a QGraphicsScene and add the pixmap item to it
                scene = QGraphicsScene()
                scene.addItem(pixmap_item)
                scene.setSceneRect(pixmap_item.boundingRect())
                self.ui.graphicsView2.setRenderHint(QPainter.Antialiasing)
                self.ui.graphicsView2.setRenderHint(QPainter.SmoothPixmapTransform)
                self.ui.graphicsView2.setScene(scene)
                self.ui.graphicsView2.fitInView(pixmap_item, QtCore.Qt.KeepAspectRatio)
                        
                
                #Georeferencing
    
                self.ui.progressBar3.setValue(80)
            
                file_widget = self.ui.file
            
                line_edit = file_widget.lineEdit()
            
                current_file_path = line_edit.text()
            
                current_directory, file_name = os.path.split(current_file_path)
        
                file_path = os.path.join(current_directory, file_name)
        
                file_path = file_path.replace('\\', '/')
        
                current_directory = current_directory.replace('\\', '/')

            

                sgmntd_pth = current_directory + "/Output/" + os.path.splitext(file_name)[0] + "-sgmntd.tif"
        

                # #Resize the output

                image = QImage(current_directory+"/Output/output.png")
            
                imageopen = Image.open(file_path)
            
                width, height = imageopen.size
        
                print("dimension :" ,width, height)
            
            

                # Resize the image to the desired dimensions
                new_image = image.scaled(width, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            
                # Save the output image to a file
                new_image.save(current_directory+"/Output/output.png")
            
                

                #Create a geotransform

                tgt_file = file_path
        
                src_file = os.path.join(current_directory+"/Output/output.png") #ang butangan
            
                # Open the georeferenced image
                tgt_ds = gdal.Open(tgt_file, gdal.GA_ReadOnly)
            
                if tgt_ds is None:
                    print(f"Error: could not open file {tgt_file}")
                else:
                    # Get the extent and resolution of the target image
                    tgt_geotransform = tgt_ds.GetGeoTransform()
                
                    tgt_extent = [tgt_geotransform[0], tgt_geotransform[3] + tgt_ds.RasterYSize*tgt_geotransform[5],
                                tgt_geotransform[0] + tgt_ds.RasterXSize*tgt_geotransform[1], tgt_geotransform[3]]
                    tgt_resolution = [abs(tgt_geotransform[1]), abs(tgt_geotransform[5])]
                

                    # Open the non-georeferenced image
                    src_ds = gdal.Open(src_file, gdal.GA_ReadOnly)
            
                    if src_ds is None:
                        print(f"Could not open {src_file}")
                    else:
                    
                        # Get the extent and resolution of the source image
                        src_geotransform = (tgt_extent[0], tgt_resolution[0], 0.0, tgt_extent[3], 0.0, -tgt_resolution[1])
                    
                        src_extent = [src_geotransform[0], src_geotransform[3] + src_ds.RasterYSize*src_geotransform[5],
                                    src_geotransform[0] + src_ds.RasterXSize*src_geotransform[1], src_geotransform[3]]
                        src_resolution = [abs(src_geotransform[1]), abs(src_geotransform[5])]
                    

                        

                        # Create an output image
                        out_driver = gdal.GetDriverByName('GTiff')
                    
                        out_ds = out_driver.CreateCopy(sgmntd_pth, src_ds, 0)
                
                        out_ds.SetGeoTransform(tgt_geotransform)
                    
                        out_ds.SetProjection(tgt_ds.GetProjection())
                    

                        # Warp the non-georeferenced image
                        gdal.Warp(out_ds, src_ds, format='GTiff', 
                                outputBounds=tgt_extent,
                                xRes=tgt_resolution[0],
                                yRes=tgt_resolution[1],
                                srcSRS='EPSG:4326',
                                dstSRS=tgt_ds.GetProjection(),
                                resampleAlg=gdal.GRA_Bilinear)
                    

                        # Close the datasets
                        tgt_ds = None
                        src_ds = None
                        out_ds = None

                src_file = sgmntd_pth#source
            
                stc_file = os.path.join(current_directory+"/Output/output.png")#ang baguhon, ang georeferenced
            
                gdal.Translate(stc_file, src_file, options=['-ot', 'Byte', '-co', 'PHOTOMETRIC=RGB'])
            
                src_file = sgmntd_pth#source
                stc_file = os.path.join(current_directory+"/Output/output.jpg")#ang baguhon, ang georeferenced
                gdal.Translate(stc_file, src_file, options=['-ot', 'Byte', '-co', 'PHOTOMETRIC=RGB'])
            
                #add the layer
                iface.addRasterLayer(sgmntd_pth, "Clipped Segmented")

                self.ui.progressBar3.setValue(100)
                self.ui.progressBar3.hide()
            
    def layout(self):

          # Get the current project instance
        project = QgsProject.instance()
        
        # Define the page settings for the print layout
        manager = project.layoutManager()
        layout_name = 'My Print Layout'
        existing_layout = manager.layoutByName(layout_name)
        
        if existing_layout:
            # Remove the existing layout if it exists
            manager.removeLayout(existing_layout)
        
        # Create a new print layout
        layout = QgsPrintLayout(project)
        layout.initializeDefaults()
        layout.setName(layout_name)
        pc = layout.pageCollection()
        page = pc.pages()[0]
        page.setPageSize('A4', QgsLayoutItemPage.Orientation.Landscape)
        
        # Add the new print layout to the manager
        manager.addLayout(layout)

        # Load the template file into the print layout
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_file = os.path.join(dir_path,'LCPTEMPLATE.qpt')
        with open(template_file, 'rt') as f:
            template_content = f.read()
        document = QDomDocument()
        document.setContent(template_content)
        context = QgsReadWriteContext()
        layout.loadFromTemplate(document, context)

         # Get the map item from the layout
        map_item = layout.itemById('Main Map')
        map_item.zoomToExtent(iface.mapCanvas().extent())

        # Refresh the layout to update the changes
        layout.refresh()
        
        # Open the new print layout in the print composer window
        iface.openLayoutDesigner(layout) 
     
