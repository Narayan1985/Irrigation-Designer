from qgis.core import QgsProject,QgsCoordinateTransform,QgsGeometry,QgsPointXY,QgsCoordinateReferenceSystem
def nearest_hydrology(lot_layer,hydro_layer):
    lot=next(lot_layer.getFeatures(),None)
    if not lot: raise ValueError("Lote vacío")
    lg=lot.geometry()
    tr=None
    if hydro_layer.crs()!=lot_layer.crs():
        tr=QgsCoordinateTransform(hydro_layer.crs(),lot_layer.crs(),QgsProject.instance())
    best=None
    for f in hydro_layer.getFeatures():
        g=f.geometry()
        if tr:
            g=QgsGeometry(g); g.transform(tr)
        d=lg.distance(g)
        if best is None or d<best[0]: best=(d,f.id(),g)
    if best is None: raise ValueError("La capa Hidrología no contiene cauces")
    # closest segment/point pair through shortestLine
    sl=lg.shortestLine(best[2]); length=sl.length()
    return {"distance_m":length,"feature_id":best[1],"connector":sl}
