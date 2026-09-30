from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsVectorLayer,QgsField,QgsProject,Qgis
def create_crop_units(crs):
    v=QgsVectorLayer(f"Polygon?crs={crs.authid()}","Unidades de cultivo","memory")
    v.dataProvider().addAttributes([
        QgsField("unidad",QVariant.String),QgsField("cultivo",QVariant.String),
        QgsField("marco_p_m",QVariant.Double),QgsField("marco_h_m",QVariant.Double),
        QgsField("observacion",QVariant.String)])
    v.updateFields(); QgsProject.instance().addMapLayer(v); v.startEditing()
    return v
def start_polygon_digitizing(iface,layer):
    iface.setActiveLayer(layer)
    # Trigger QGIS native Add Polygon Feature action; user clicks vertices on imagery.
    act=iface.actionAddFeature()
    if act:
        act.trigger()
    return layer
