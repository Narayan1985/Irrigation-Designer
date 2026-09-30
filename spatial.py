from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsVectorLayer, QgsProject, QgsField, QgsFeature, QgsRectangle, QgsGeometry, QgsPointXY
def mk(geom,name,crs,fields):
    v=QgsVectorLayer(f"{geom}?crs={crs.authid()}",name,"memory")
    v.dataProvider().addAttributes([QgsField(n,t) for n,t in fields]); v.updateFields(); QgsProject.instance().addMapLayer(v); return v
def split_sectors(lot,n):
    ft=next(lot.getFeatures()); g=ft.geometry(); b=g.boundingBox(); crs=lot.crs()
    out=mk("Polygon","ID_Sectores_Propuestos",crs,[("sector",QVariant.Int),("area_ha",QVariant.Double),("editable",QVariant.String)])
    # split perpendicular to longest bbox axis, clipped to actual lot
    vertical=b.width()>=b.height()
    for i in range(n):
        if vertical:
            x1=b.xMinimum()+b.width()*i/n; x2=b.xMinimum()+b.width()*(i+1)/n
            box=QgsRectangle(x1,b.yMinimum(),x2,b.yMaximum())
        else:
            y1=b.yMinimum()+b.height()*i/n; y2=b.yMinimum()+b.height()*(i+1)/n
            box=QgsRectangle(b.xMinimum(),y1,b.xMaximum(),y2)
        inter=g.intersection(QgsGeometry.fromRect(box))
        if not inter.isEmpty():
            f=QgsFeature(out.fields()); f.setGeometry(inter); f.setAttributes([i+1,inter.area()/10000,"Sí"]); out.dataProvider().addFeature(f)
    out.updateExtents(); out.startEditing(); return out
def make_layout(lot,n,method,plant,row,q_emitter,wet_diam):
    sec=split_sectors(lot,n); ft=next(lot.getFeatures()); g=ft.geometry(); b=g.boundingBox(); crs=lot.crs()
    E=mk("Point","ID_Emisores_Propuestos",crs,[("id",QVariant.Int),("tipo",QVariant.String),("q_Lh",QVariant.Double),("Dmojado_m",QVariant.Double)])
    if not crs.isGeographic():
        dx=max(.1,plant); dy=max(.1,row); count=0; y=b.yMinimum()+dy/2
        while y<b.yMaximum() and count<10000:
            x=b.xMinimum()+dx/2
            while x<b.xMaximum() and count<10000:
                p=QgsPointXY(x,y)
                if g.contains(QgsGeometry.fromPointXY(p)):
                    count+=1; f=QgsFeature(E.fields()); f.setGeometry(QgsGeometry.fromPointXY(p))
                    f.setAttributes([count,method,q_emitter,wet_diam if method=="Aspersión" else 0]); E.dataProvider().addFeature(f)
                x+=dx
            y+=dy
    E.updateExtents(); E.startEditing(); return sec,E
