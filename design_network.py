from math import pi,ceil,sqrt
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor
from qgis.core import (
    QgsProject,QgsVectorLayer,QgsField,QgsFeature,QgsGeometry,QgsPointXY,
    QgsMarkerSymbol,QgsLineSymbol,QgsFillSymbol,QgsPalLayerSettings,
    QgsVectorLayerSimpleLabeling,QgsTextFormat,QgsProperty,QgsWkbTypes,QgsSingleSymbolRenderer
)
from .engine import hf_hw
from .irrigation_spacing import irrigation_spacing


def _velocity(q_lps,d_mm):
    if d_mm<=0:return 0.0
    area=pi*(d_mm/1000.0)**2/4.0
    return (q_lps/1000.0)/area if area else 0.0

def _minor_loss_mca(k,v):
    return float(k)*v*v/(2*9.80665)

def _internal_diameter(dn_mm,material):
    # Until a manufacturer/SDR/PN catalogue is selected, DN is retained as Dint.
    # This is explicit rather than fabricating a wall thickness.
    return float(dn_mm)

def _layer(uri,name,crs,fields):
    v=QgsVectorLayer(f"{uri}?crs={crs.authid()}",name,"memory")
    v.dataProvider().addAttributes([QgsField(n,t) for n,t in fields]); v.updateFields()
    QgsProject.instance().addMapLayer(v); return v

def _label(v,expression,size=9):
    s=QgsPalLayerSettings(); s.fieldName=expression; s.isExpression=True; s.enabled=True
    fmt=QgsTextFormat(); fmt.setSize(size); s.setFormat(fmt)
    v.setLabelsEnabled(True); v.setLabeling(QgsVectorLayerSimpleLabeling(s)); v.triggerRepaint()

def _longest_axis(g):
    # Practical first-order orientation from oriented minimum bounding box.
    ombb=g.orientedMinimumBoundingBox()
    rect=ombb[0] if isinstance(ombb,tuple) else ombb
    pts=list(rect.asPolygon()[0])
    seg=[]
    for a,b in zip(pts[:-1],pts[1:]):
        dx=b.x()-a.x(); dy=b.y()-a.y(); L=sqrt(dx*dx+dy*dy)
        seg.append((L,a,b))
    return max(seg,key=lambda x:x[0])

def _clip_line(g,a,b):
    ln=QgsGeometry.fromPolylineXY([a,b]); inter=ln.intersection(g)
    if inter.isEmpty(): return None
    if inter.type()!=QgsWkbTypes.LineGeometry:return None
    return inter

def _design_single(lot,method,plant_spacing,row_spacing,q_emitter_lh,q_total_lps,material,dn_main,dn_sec,dn_lat,
                   pump_tdh,pump_kw,source_point=None,max_emitters=6000,unit_id=1,wetted_diameter_m=0.0,wind_ms=0.0,overlap_factor=None):
    if lot.crs().isGeographic(): raise ValueError("Error interno: la capa de trabajo no fue reproyectada a CRS métrico.")
    spacing=irrigation_spacing(method,plant_spacing,row_spacing,wetted_diameter_m,wind_ms,overlap_factor)
    emitter_spacing=spacing["along_m"]
    lateral_spacing=spacing["between_m"]
    if "gravedad" in method.lower():
        emitter_spacing=0.0

    ft=next(lot.getFeatures(),None)
    if not ft: raise ValueError("Lote vacío")
    g=ft.geometry(); crs=lot.crs(); b=g.boundingBox()
    L,a0,a1=_longest_axis(g); ux=(a1.x()-a0.x())/L; uy=(a1.y()-a0.y())/L
    # normal to row direction
    nx=-uy; ny=ux
    c=g.centroid().asPoint()
    diag=sqrt(b.width()**2+b.height()**2)*1.5
    # Layers
    pump=_layer("Point","Bomba",crs,[("unidad",QVariant.Int),("Q_Ls",QVariant.Double),("TDH_m",QVariant.Double),("Pot_kW",QVariant.Double)])
    main=_layer("LineString","Tubería principal",crs,[("unidad",QVariant.Int),("DN_mm",QVariant.Double),("Dint_mm",QVariant.Double),("Long_m",QVariant.Double),
("Q_Ls",QVariant.Double),("Vel_ms",QVariant.Double),("Hf_mca",QVariant.Double),("P_ini_mca",QVariant.Double),
("P_fin_mca",QVariant.Double),("Material",QVariant.String)])
    sec=_layer("LineString","Tuberías secundarias",crs,[("unidad",QVariant.Int),("sector",QVariant.Int),("DN_mm",QVariant.Double),("Dint_mm",QVariant.Double),
("Long_m",QVariant.Double),("Q_Ls",QVariant.Double),("Vel_ms",QVariant.Double),("Hf_mca",QVariant.Double),
("P_ini_mca",QVariant.Double),("P_fin_mca",QVariant.Double)])
    lat=_layer("LineString","Laterales",crs,[("unidad",QVariant.Int),("id",QVariant.Int),("sector",QVariant.Int),("DN_mm",QVariant.Double),("Dint_mm",QVariant.Double),
("Long_m",QVariant.Double),("Q_Ls",QVariant.Double),("Vel_ms",QVariant.Double),("n_emis",QVariant.Int),
("Hf_mca",QVariant.Double),("P_ini_mca",QVariant.Double),("P_fin_mca",QVariant.Double)])
    emit=_layer("Point","Emisores",crs,[("unidad",QVariant.Int),("id",QVariant.Int),("sector",QVariant.Int),("tipo",QVariant.String),("q_Lh",QVariant.Double),("P_obj_m",QVariant.Double)])
    # Main line follows normal through centroid, clipped to lot
    pA=QgsPointXY(c.x()-nx*diag,c.y()-ny*diag); pB=QgsPointXY(c.x()+nx*diag,c.y()+ny*diag)
    mg=_clip_line(g,pA,pB)
    if mg is None: raise RuntimeError("No fue posible generar la tubería principal.")
    # choose pump at endpoint nearest source, otherwise first endpoint
    parts=mg.asMultiPolyline() if mg.isMultipart() else [mg.asPolyline()]
    longest=max(parts,key=lambda x: sum(sqrt((x[i+1].x()-x[i].x())**2+(x[i+1].y()-x[i].y())**2) for i in range(len(x)-1)))
    p0,p1=longest[0],longest[-1]
    pp=p0
    if source_point:
        d0=(p0.x()-source_point.x())**2+(p0.y()-source_point.y())**2
        d1=(p1.x()-source_point.x())**2+(p1.y()-source_point.y())**2
        pp=p0 if d0<=d1 else p1
    pf=QgsFeature(pump.fields()); pf.setGeometry(QgsGeometry.fromPointXY(pp)); pf.setAttributes([unit_id,q_total_lps,pump_tdh,pump_kw]); pump.dataProvider().addFeature(pf)
    mlen=mg.length(); dint_main=_internal_diameter(dn_main,material); vmain=_velocity(q_total_lps,dint_main)
    mhf=hf_hw(q_total_lps,mlen,dint_main,150); p_ini=pump_tdh; p_fin=max(0.0,p_ini-mhf)
    mf=QgsFeature(main.fields()); mf.setGeometry(mg); mf.setAttributes([unit_id,dn_main,dint_main,mlen,q_total_lps,vmain,mhf,p_ini,p_fin,material]); main.dataProvider().addFeature(mf)
    # Rows/laterals across lot along longest parcel axis.
    offsets=[]; off=-diag
    while off<=diag:
        center=QgsPointXY(c.x()+nx*off,c.y()+ny*off)
        aa=QgsPointXY(center.x()-ux*diag,center.y()-uy*diag); bb=QgsPointXY(center.x()+ux*diag,center.y()+uy*diag)
        gg=_clip_line(g,aa,bb)
        if gg and gg.length()>max(2,emitter_spacing if emitter_spacing>0 else 2): offsets.append((off,gg))
        off+=lateral_spacing if lateral_spacing>0 else max(1.0,row_spacing)
    # sectors based on manageable emitter groups, preserving neighboring laterals
    expected=0 if "gravedad" in method.lower() else sum(max(1,int(x[1].length()/emitter_spacing)) for x in offsets)
    nsec=max(1,ceil(expected/max_emitters)); per=max(1,ceil(len(offsets)/nsec))
    eid=0; lid=0
    sector_q={}
    sector_lines={}
    for j,(off,gg) in enumerate(offsets):
        sid=min(nsec,1+j//per); lid+=1
        parts2=gg.asMultiPolyline() if gg.isMultipart() else [gg.asPolyline()]
        line=max(parts2,key=lambda x: QgsGeometry.fromPolylineXY(x).length())
        gl=QgsGeometry.fromPolylineXY(line); llen=gl.length()
        n=0 if "gravedad" in method.lower() else max(1,int(llen/emitter_spacing)); ql=n*q_emitter_lh/3600
        dint_lat=_internal_diameter(dn_lat,material); vlat=_velocity(ql,dint_lat)
        lhf=hf_hw(ql,llen,dint_lat,150) if ql>0 else 0
        lp_ini=max(0.0,pump_tdh-mhf); lp_fin=max(0.0,lp_ini-lhf)
        lf=QgsFeature(lat.fields()); lf.setGeometry(gl); lf.setAttributes([unit_id,lid,sid,dn_lat,dint_lat,llen,ql,vlat,n,lhf,lp_ini,lp_fin]); lat.dataProvider().addFeature(lf)
        sector_q[sid]=sector_q.get(sid,0)+ql
        sector_lines.setdefault(sid,[]).append(gl)
        # place emitters along actual clipped lateral
        for k in range(n):
            dist=(k+.5)*llen/n; pt=gl.interpolate(dist).asPoint(); eid+=1
            ef=QgsFeature(emit.fields()); ef.setGeometry(QgsGeometry.fromPointXY(pt)); ef.setAttributes([unit_id,eid,sid,method,q_emitter_lh,10.0]); emit.dataProvider().addFeature(ef)
    # secondary: connect centroids/nearest points of lateral groups approximately along main
    for sid,lines in sector_lines.items():
        pts=[x.centroid().asPoint() for x in lines]
        if len(pts)>=2:
            sg=QgsGeometry.fromPolylineXY([pts[0],pts[-1]])
        else:
            cp=pts[0]; sg=QgsGeometry.fromPolylineXY([cp,mg.nearestPoint(QgsGeometry.fromPointXY(cp)).asPoint()])
        q=sector_q[sid]; slen=sg.length(); dint_sec=_internal_diameter(dn_sec,material); vsec=_velocity(q,dint_sec)
        shf=hf_hw(q,slen,dint_sec,150) if slen>0 else 0
        sp_ini=max(0.0,pump_tdh-mhf); sp_fin=max(0.0,sp_ini-shf)
        sf=QgsFeature(sec.fields()); sf.setGeometry(sg); sf.setAttributes([unit_id,sid,dn_sec,dint_sec,slen,q,vsec,shf,sp_ini,sp_fin]); sec.dataProvider().addFeature(sf)
    for v in [pump,main,sec,lat,emit]: v.updateExtents()
    # Symbology and labels
    pump.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({"name":"circle","size":"5"})))
    main.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({"width":"1.4"})))
    sec.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({"width":"0.9"})))
    lat.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({"width":"0.35"})))
    emit.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({"name":"circle","size":"1.5"})))
    pump_expr = """concat('Bomba | Q=',round("Q_Ls",2),' L/s | TDH=',round("TDH_m",1),' m | P=',round("Pot_kW",2),' kW')"""
    main_expr = """concat('Principal DN',round("DN_mm",0),' | Q=',round("Q_Ls",2),' L/s | Hf=',round("Hf_m",2),' m')"""
    sec_expr = """concat('S',"sector",' DN',round("DN_mm",0),' | Q=',round("Q_Ls",2),' L/s')"""
    emit_expr = """concat("tipo",' | ',round("q_Lh",2),' L/h')"""
    # labels applied after multi-unit merge
    # labels applied after multi-unit merge
    # labels applied after multi-unit merge
    lat_expr = """concat('Lateral ', "id",' | DN',round("DN_mm",0),' | ', "n_emis",' emis. | Q=',round("Q_Ls",3),' L/s')"""
    # labels applied after multi-unit merge

    # labels applied after multi-unit merge

    return {"pump":pump,"main":main,"secondary":sec,"laterals":lat,"emitters":emit,
            "n_emitters":eid,"n_laterals":lid,"n_sectors":nsec}

def _merge_layers(layer_list,name):
    if not layer_list: return None
    first=layer_list[0]
    geom={QgsWkbTypes.PointGeometry:"Point",QgsWkbTypes.LineGeometry:"LineString",QgsWkbTypes.PolygonGeometry:"Polygon"}[first.geometryType()]
    out=QgsVectorLayer(f"{geom}?crs={first.crs().authid()}",name,"memory")
    out.dataProvider().addAttributes(first.fields()); out.updateFields()
    feats=[]
    for lyr in layer_list:
        for f in lyr.getFeatures():
            nf=QgsFeature(out.fields()); nf.setGeometry(f.geometry()); nf.setAttributes(f.attributes()); feats.append(nf)
        QgsProject.instance().removeMapLayer(lyr.id())
    out.dataProvider().addFeatures(feats); out.updateExtents(); QgsProject.instance().addMapLayer(out)
    return out

def design_network(lot,method,plant_spacing,row_spacing,q_emitter_lh,q_total_lps,material,dn_main,dn_sec,dn_lat,
                   pump_tdh,pump_kw,source_point=None,max_emitters=6000,wetted_diameter_m=0.0,wind_ms=0.0,overlap_factor=None):
    features=list(lot.getFeatures())
    if not features: raise ValueError("No existen unidades de cultivo.")
    # Allocate total design flow by polygon area, not equally.
    areas=[max(0,f.geometry().area()) for f in features]; total=sum(areas)
    if total<=0: raise ValueError("Las unidades de cultivo no tienen área válida.")
    collections={"pump":[],"main":[],"secondary":[],"laterals":[],"emitters":[]}
    stats={"n_emitters":0,"n_laterals":0,"n_sectors":0}
    for idx,(f,a) in enumerate(zip(features,areas),1):
        tmp=QgsVectorLayer(f"Polygon?crs={lot.crs().authid()}",f"_unidad_{idx}","memory")
        tmp.dataProvider().addAttributes(lot.fields()); tmp.updateFields()
        nf=QgsFeature(tmp.fields()); nf.setGeometry(f.geometry()); nf.setAttributes(f.attributes()); tmp.dataProvider().addFeature(nf)
        q_unit=q_total_lps*(a/total)
        r=_design_single(tmp,method,plant_spacing,row_spacing,q_emitter_lh,q_unit,material,dn_main,dn_sec,dn_lat,
                         pump_tdh,pump_kw,source_point,max_emitters,idx,wetted_diameter_m,wind_ms,overlap_factor)
        for k in collections: collections[k].append(r[k])
        for k in stats: stats[k]+=r[k]
    pump=_merge_layers(collections["pump"],"Bomba")
    main=_merge_layers(collections["main"],"Tubería principal")
    sec=_merge_layers(collections["secondary"],"Tuberías secundarias")
    lat=_merge_layers(collections["laterals"],"Laterales")
    emit=_merge_layers(collections["emitters"],"Emisores")
    acc=_layer("Point","Accesorios y uniones",lot.crs(),[
        ("unidad",QVariant.Int),("tipo",QVariant.String),("K",QVariant.Double),("Q_Ls",QVariant.Double),
        ("Dint_mm",QVariant.Double),("Vel_ms",QVariant.Double),("Hm_mca",QVariant.Double),("nota",QVariant.String)])
    # Connections of secondary/lateral lines are represented as tees/connections.
    aid=0
    for lyr,typ,kval in [(sec,"T",0.9),(lat,"Conexión lateral",0.5)]:
        for f in lyr.getFeatures():
            g=f.geometry()
            if g is None or g.isEmpty(): continue
            parts=g.asMultiPolyline() if g.isMultipart() else [g.asPolyline()]
            parts=[part for part in parts if part]
            if not parts: continue
            pt=parts[0][0]; aid+=1
            q=float(f["Q_Ls"]); di=float(f["Dint_mm"]); vv=_velocity(q,di); hm=_minor_loss_mca(kval,vv)
            af=QgsFeature(acc.fields()); af.setGeometry(QgsGeometry.fromPointXY(pt))
            af.setAttributes([int(f["unidad"]),typ,kval,q,di,vv,hm,"Clasificación automática; editable"])
            acc.dataProvider().addFeature(af)
    acc.updateExtents()
    # Renderers after merge
    pump.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({"name":"circle","size":"5"})))
    main.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({"width":"1.4"})))
    sec.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({"width":"0.9"})))
    lat.setRenderer(QgsSingleSymbolRenderer(QgsLineSymbol.createSimple({"width":"0.35"})))
    emit.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({"name":"circle","size":"1.8"})))
    acc.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({"name":"diamond","size":"3"})))
    # Always-visible main labels; emitter labels appear at useful close scale.
    _label(pump, """concat('U',"unidad",' | Bomba | Q=',round("Q_Ls",2),' L/s | TDH=',round("TDH_m",1),' m | ',round("Pot_kW",2),' kW')""",10)
    _label(main, """concat('U',"unidad",' | Principal DN',round("DN_mm",0),' | Dint=',round("Dint_mm",1),' mm | L=',round("Long_m",1),' m | Q=',round("Q_Ls",2),' L/s | Hf=',round("Hf_mca",2),' mca | Pfin=',round("P_fin_mca",1),' mca')""",9)
    _label(sec, """concat('U',"unidad",' S',"sector",' | DN',round("DN_mm",0),' Dint=',round("Dint_mm",1),' mm | L=',round("Long_m",1),' m | Q=',round("Q_Ls",2),' L/s | Pfin=',round("P_fin_mca",1),' mca')""",8)
    _label(lat, """concat('U',"unidad",' L',"id",' | Dint=',round("Dint_mm",1),' mm | L=',round("Long_m",1),' m | ', "n_emis",' emis. | Q=',round("Q_Ls",3),' L/s | Pfin=',round("P_fin_mca",1),' mca')""",7)
    _label(emit, """concat('U',"unidad",' | Emisor: ',"tipo",' | ',round("q_Lh",2),' L/h | P=',round("P_obj_m",1),' mca')""",7)
    _label(acc, """concat("tipo",' | Dint=',round("Dint_mm",1),' mm | Hm=',round("Hm_mca",3),' mca')""",7)
    # Correct scale logic: labels/features visible when zoomed IN (denominator <= threshold)
    lat.setMinimumScale(5000)
    emit.setMinimumScale(2500)
    for v in [pump,main,sec,lat,emit,acc]:
        v.setLabelsEnabled(True); v.triggerRepaint()
    QgsProject.instance().layerTreeRoot().findLayer(pump.id()).setItemVisibilityChecked(True)
    return {"pump":pump,"main":main,"secondary":sec,"laterals":lat,"emitters":emit,"accessories":acc,**stats}
