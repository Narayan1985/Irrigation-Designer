from qgis.PyQt.QtWidgets import QAction
from .wizard import Wizard
class IrrigationDesignerPlugin:
    def __init__(self,iface): self.iface=iface
    def initGui(self):
        self.a=QAction("Irrigation Designer",self.iface.mainWindow()); self.a.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Irrigation Designer",self.a); self.iface.addToolBarIcon(self.a)
    def unload(self):
        self.iface.removePluginMenu("&Irrigation Designer",self.a); self.iface.removeToolBarIcon(self.a)
    def run(self): self.d=Wizard(self.iface); self.d.show()
