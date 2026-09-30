def classFactory(iface):
    from .plugin import IrrigationDesignerPlugin
    return IrrigationDesignerPlugin(iface)
