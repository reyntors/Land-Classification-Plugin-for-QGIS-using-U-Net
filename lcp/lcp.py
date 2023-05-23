
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from .resources import *
from .lcp_dialog import LandClassificationPluginDialog


import os.path





pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]

class LandClassificationPlugin():
    

    
    def __init__(self, iface):
        super().__init__()
        self.iface = iface
        self.action = QAction(QIcon("C:/Users/Reynard Z. Torculas/OneDrive/Documents/Thesis/plugin/lcp/lcp/LCP.png"), "Land Classification Plugin", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.action.triggered.connect(self.initAlgorithm)
    
    

    def initAlgorithm(self, config=None):
        
        self.name = "Land Classification Plugin"
        self.display_name = "Land Classification Plugin"
        

    
    def initGui(self):
        print("I am GUI")
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.iface.addToolBarIcon(self.action)



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        print(" I am Unload!")
        self.iface.removeToolBarIcon(self.action)


    def run(self):
        
             # Check if the dialog instance already exists and whether it is visible or not
        if hasattr(self, 'dlg') and self.dlg is not None and self.dlg.isVisible():
            self.dlg.close()  # Close the dialog
            
             # Create a new instance of the dialog
        self.dlg = LandClassificationPluginDialog()
        
        # Show the dialog
        self.dlg.show()
        
        # Run the dialog event loop
        self.dlg.exec_()
        
