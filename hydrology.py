from qgis.core import (
    QgsApplication,QgsProject,QgsRasterLayer,QgsVectorLayer,QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,QgsPointXY
)
import processing, os, tempfile, math

def available_algorithms():
    reg=QgsApplication.processingRegistry()
    return {a.id() for p in reg.providers() for a in p.algorithms()}

def find_alg(candidates):
    ids=available_algorithms()
    for x in candidates:
        if x in ids:
            return x
    return None

def _utm_epsg_for_dem(dem):
    """Return a metric UTM EPSG from the DEM center transformed to WGS84."""
    crs=dem.crs()
    center=dem.extent().center()
    wgs84=QgsCoordinateReferenceSystem("EPSG:4326")
    if crs != wgs84:
        tr=QgsCoordinateTransform(crs,wgs84,QgsProject.instance())
        center=tr.transform(QgsPointXY(center))
    lon=float(center.x()); lat=float(center.y())
    if not (-180 <= lon <= 180 and -80 <= lat <= 84):
        raise ValueError("No fue posible determinar una zona UTM válida para el DEM.")
    zone=int(math.floor((lon+180.0)/6.0)+1)
    zone=max(1,min(60,zone))
    return (32600 if lat >= 0 else 32700)+zone

def ensure_metric_dem(dem):
    """
    Keeps the original DEM untouched.
    If CRS units are degrees, creates a temporary metric UTM working raster.
    Returns (working_layer, message).
    """
    if not dem or not dem.isValid():
        raise ValueError("DEM inválido.")
    crs=dem.crs()
    if not crs.isValid():
        raise ValueError("El DEM no tiene un CRS válido. Asígnele el CRS correcto antes del análisis.")
    if not crs.isGeographic():
        return dem, f"DEM usado directamente: {crs.authid()}."
    epsg=_utm_epsg_for_dem(dem)
    target=QgsCoordinateReferenceSystem(f"EPSG:{epsg}")
    alg=find_alg(["gdal:warpreproject","gdal:warp"])
    if not alg:
        raise RuntimeError("No está disponible GDAL Warp/Reproject en QGIS Processing.")
    tmp=tempfile.mkdtemp(prefix="irrigation_dem_")
    out=os.path.join(tmp,"DEM_trabajo_metrico.tif")
    # QGIS GDAL warp schema
    params={
        "INPUT":dem.source(),
        "SOURCE_CRS":crs,
        "TARGET_CRS":target,
        "RESAMPLING":1, # bilinear for continuous elevation
        "NODATA":None,
        "TARGET_RESOLUTION":None,
        "OPTIONS":"",
        "DATA_TYPE":0,
        "TARGET_EXTENT":None,
        "TARGET_EXTENT_CRS":None,
        "MULTITHREADING":True,
        "EXTRA":"",
        "OUTPUT":out
    }
    res=processing.run(alg,params)
    path=res.get("OUTPUT",out)
    reproj=QgsRasterLayer(path,f"DEM_Trabajo_{target.authid().replace(':','_')}")
    if not reproj.isValid():
        raise RuntimeError("La reproyección terminó, pero el DEM métrico resultante no pudo abrirse.")
    QgsProject.instance().addMapLayer(reproj)
    return reproj, f"DEM original {crs.authid()} reproyectado automáticamente a {target.authid()} para el análisis. Original conservado."

def run_hydrology(dem,threshold=1000):
    work_dem,msg=ensure_metric_dem(dem)
    stream_alg=find_alg(["grass:r.stream.extract","grass7:r.stream.extract"])
    if not stream_alg:
        raise RuntimeError("No está disponible GRASS r.stream.extract. Active/instale el proveedor GRASS de QGIS Processing.")
    tmp=tempfile.mkdtemp(prefix="irrigation_hydro_")
    streams=os.path.join(tmp,"streams.gpkg")
    direction=os.path.join(tmp,"direction.tif")
    params={"elevation":work_dem.source(),"threshold":float(threshold),"stream_vector":streams,"direction":direction}
    try:
        res=processing.run(stream_alg,params)
    except Exception:
        params={"ELEVATION":work_dem.source(),"THRESHOLD":float(threshold),"STREAM_VECTOR":streams,"DIRECTION":direction}
        res=processing.run(stream_alg,params)
    out={"working_dem":work_dem,"message":msg}
    if os.path.exists(streams):
        v=QgsVectorLayer(streams,"Hidrología","ogr")
        if v.isValid(): QgsProject.instance().addMapLayer(v); out["streams"]=v
    if os.path.exists(direction):
        r=QgsRasterLayer(direction,"ID_Direccion_Flujo")
        if r.isValid(): QgsProject.instance().addMapLayer(r); out["direction"]=r
    return out
