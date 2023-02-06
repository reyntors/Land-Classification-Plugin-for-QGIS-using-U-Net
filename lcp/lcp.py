from qgis.PyQt5.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt5.QtGui import QIcon
from qgis.PyQt5.QtWidgets import QAction
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from .resources import *
from .lcp_dialog import LandClassificationPluginDialog

import os.path
from PyQt5.QtWidgets import QAction, QToolBar
from qgis.core import  (QgsProcessing,
                       QgsProcessingMultiStepFeedback, QgsProcessingOutputRasterLayer, 
                       QgsProcessingParameterExtent, QgsProcessingParameterRasterLayer, 
                       QgsRasterLayer, QgsVectorLayer, QgsApplication)
from qgis.core import QgsProcessingAlgorithm
from processing.algs.gdal.GdalAlgorithm import GdalAlgorithm
import processing
from osgeo import gdal
from processing.algs.gdal.GdalUtils import GdalUtils



pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]

class LandClassificationPlugin(GdalAlgorithm):
    INPUT = 'INPUT'
    EXTENT = 'PROJWIN'
    OVERCRS = 'OVERCRS'
    NODATA = 'NODATA'
    OPTIONS = 'OPTIONS'
    DATA_TYPE = 'DATA_TYPE'
    EXTRA = 'EXTRA'
    OUTPUT = 'OUTPUT'

    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.action = QAction(QIcon("E:/Development/Qgis plugin/lcp/icon2.jpg"), "Land Classification Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.action.triggered.connect(self.initAlgorithm)
    
    

    def initAlgorithm(self, config=None):
        print("initAlgorithm is functioning!")
        self.name = "Land Classification Plugin"
        self.display_name = "Land Classification Plugin"
        self.group = "Raster"

        self.TYPES = [self.tr('Use Input Layer Data Type'), 'Byte', 'Int16', 'UInt16', 'UInt32', 'Int32', 'Float32', 'Float64', 'CInt16', 'CInt32', 'CFloat32', 'CFloat64']

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Input layer')))
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT,
                                                       self.tr('Clipping extent')))
        self.addParameter(QgsProcessingParameterBoolean(self.OVERCRS,
                                                        self.tr('Override the projection for the output file'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterNumber(self.NODATA,
                                                       self.tr('Assign a specified nodata value to output bands'),
                                                       type=QgsProcessingParameterNumber.Double,
                                                       defaultValue=None,
                                                       optional=True))

        options_param = QgsProcessingParameterString(self.OPTIONS,
                                                     self.tr('Additional creation options'),
                                                     defaultValue='',
                                                     optional=True)
        options_param.setFlags(options_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        options_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.algs.gdal.ui.RasterOptionsWidget.RasterOptionsWidgetWrapper'}})
        self.addParameter(options_param)

        dataType_param = QgsProcessingParameterEnum(self.DATA_TYPE,
                                                    self.tr('Output data type'),
                                                    self.TYPES,
                                                    allowMultiple=False,
                                                    defaultValue=0)
        dataType_param.setFlags(dataType_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(dataType_param)

        extra_param = QgsProcessingParameterString(self.EXTRA,
                                                   self.tr('Additional command-line parameters'),
                                                   defaultValue=None,
                                                   optional=True)
        extra_param.setFlags(extra_param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(extra_param)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Clipped (extent)')))
    
    def name(self):
        return 'cliprasterbyextent'

    def displayName(self):
        return self.tr('Clip raster by extent')

    def group(self):
        return self.tr('Raster extraction')

    def groupId(self):
        return 'rasterextraction'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'gdaltools', 'raster-clip.png'))

    def commandName(self):
        return "gdal_translate"

                       
    def processAlgorithm(self, parameters, context, feedback):
        
         print("processAlgorithm is functioning!")     
        
         inLayer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
         bbox = self.parameterAsExtent(parameters, self.EXTENT, context, inLayer.crs())
         override_crs = self.parameterAsBoolean(parameters, self.OVERCRS, context)
         no_data = self.parameterAsDouble(parameters, self.NODATA, context)
         options = self.parameterAsString(parameters, self.OPTIONS, context)
         data_type = self.parameterAsEnum(parameters, self.DATA_TYPE, context)
         extra = self.parameterAsString(parameters, self.EXTRA, context)

         out_file = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)

         if data_type == 0:
             data_type = inLayer.dataProvider().dataType(1)

         arguments = []
         if bbox is not None:
              arguments.append('-projwin')
              arguments.append(str(bbox.xMinimum()))
              arguments.append(str(bbox.yMaximum()))
              arguments.append(str(bbox.xMaximum()))
              arguments.append(str(bbox.yMinimum()))

         if override_crs:
             arguments.append('-a_srs')
             arguments.append(inLayer.crs().authid())

         if no_data is not None:
              arguments.append('-a_nodata')
              arguments.append(str(no_data))

         if data_type:
              arguments.append('-ot')
              arguments.append(GdalAlgorithm.TYPES[data_type])

         if options:
             arguments.extend(GdalUtils.parseCreationOptions(options))

         if extra:
             arguments.extend(extra.split(' '))

             arguments.append(inLayer.source())
             arguments.append(out_file)

             return GdalUtils.runGdal(['gdal_translate', GdalUtils.escapeAndJoin(arguments)], feedback)
             
    def createInstance(self):
             return LandClassificationPlugin()

    def name(self):
             return 'LandClassificationPlugin'

    def displayName(self):
             return 'LandClassificationPlugin'

    def group(self):
             return 'Plugins'

    def groupId(self):
         return 'Plugins'

    def shortHelpString(self):
         return 'This is a short help string for the LandClassificationPlugin algorithm'


    def svgIconPath(self):
         return os.path.join(pluginPath, 'icon.jpg')

    def helpUrl(self):
         return 'https://www.example.com/help'

    def createUserUI(self, dialog):
         pass
    
    def initGui(self):
        print("I am GUI")
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.iface.addToolBarIcon(self.action)



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        print(" I am Unload!")
        self.iface.removeToolBarIcon(self.action)


    def run(self):
        """Run method that performs all the real work"""
        print("I am RUN!")
        
        # show the dialog
        self.dlg = LandClassificationPluginDialog()
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        if result:
            print("Algorithm finished successfully!")

    # show the dialog
            
            self.dlg = LandClassificationPluginDialog()
            self.dlg.show()
    # Run the dialog event loop
            result = self.dlg.exec_()
        else:
             print("Algorithm failed or was canceled!")