import math
from qgis.core import (
    QgsProject,QgsVectorLayer,QgsFeature,QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,QgsWkbTypes
)
def utm_crs_for_layer(layer):
    wgs=QgsCoordinateReferenceSystem("EPSG:4326")
    c=layer.extent().center()
    if layer.crs()!=wgs:
        tr=QgsCoordinateTransform(layer.crs(),wgs,QgsProject.instance()); c=tr.transform(c)
    lon,lat=c.x(),c.y()
    zone=max(1,min(60,int(math.floor((lon+180)/6)+1)))
    return QgsCoordinateReferenceSystem(f"EPSG:{(32600 if lat>=0 else 32700)+zone}")
def ensure_metric_polygon(layer,name="Lote_Trabajo_Metrico"):
    if not layer.crs().isGeographic(): return layer,False
    target=utm_crs_for_layer(layer)
    out=QgsVectorLayer(f"Polygon?crs={target.authid()}",name,"memory")
    out.dataProvider().addAttributes(layer.fields()); out.updateFields()
    tr=QgsCoordinateTransform(layer.crs(),target,QgsProject.instance())
    feats=[]
    for f in layer.getFeatures():
        nf=QgsFeature(out.fields()); g=f.geometry(); g.transform(tr); nf.setGeometry(g); nf.setAttributes(f.attributes()); feats.append(nf)
    out.dataProvider().addFeatures(feats); out.updateExtents(); QgsProject.instance().addMapLayer(out)
    return out,True
