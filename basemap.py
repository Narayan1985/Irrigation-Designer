from qgis.core import QgsRasterLayer,QgsProject
ESRI_XYZ="type=xyz&url=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}&zmax=19&zmin=0"
def add_esri_world_imagery():
    lyr=QgsRasterLayer(ESRI_XYZ,"Esri World Imagery","wms")
    if not lyr.isValid(): raise RuntimeError("No se pudo cargar Esri World Imagery. Revise conexión y condiciones del servicio.")
    QgsProject.instance().addMapLayer(lyr); return lyr
