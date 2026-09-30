from qgis.PyQt.QtWidgets import *
from qgis.core import QgsProject, QgsVectorLayer, QgsRasterLayer, QgsWkbTypes, QgsDistanceArea, QgsRasterBandStats
from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
from .catalogs import *
from .engine import *
from .hydrology import run_hydrology
from .basemap import add_esri_world_imagery
from .spatial import make_layout
from .design_network import design_network
from .digitizing import create_crop_units, start_polygon_digitizing
from .crs_utils import ensure_metric_polygon
from .source_analysis import nearest_hydrology
from .water_availability import estimate_power_q
from .climate_power import power_eto_daily
class Wizard(QDialog):
    def __init__(self,iface):
        super().__init__(iface.mainWindow()); self.iface=iface; self.setWindowTitle("Irrigation Designer Spatial v1.2.0"); self.resize(760,650)
        self.t=QTabWidget(); QVBoxLayout(self).addWidget(self.t); self.site(); self.crop(); self.water(); self.system(); self.final()
    def site(self):
        w=QWidget(); f=QFormLayout(w); self.lot=QComboBox(); self.dem=QComboBox(); self.dem.addItem("(seleccione DEM)",None)
        for l in QgsProject.instance().mapLayers().values():
            if isinstance(l,QgsVectorLayer) and l.geometryType()==QgsWkbTypes.PolygonGeometry:self.lot.addItem(l.name(),l.id())
            if isinstance(l,QgsRasterLayer):self.dem.addItem(l.name(),l.id())
        b=QPushButton("Agregar Esri World Imagery"); b.clicked.connect(lambda: self.safe(add_esri_world_imagery))
        bd=QPushButton("Crear capa para digitalizar unidades de cultivo"); bd.clicked.connect(self.create_units)
        self.th=QSpinBox(); self.th.setRange(1,100000000); self.th.setValue(1000)
        h=QPushButton("Generar hidrología DEM"); h.clicked.connect(self.hydro)
        f.addRow("Lote:",self.lot); f.addRow("DEM:",self.dem); f.addRow("",b); f.addRow("",bd); f.addRow("Umbral cauces (celdas):",self.th); f.addRow("",h); self.t.addTab(w,"1. Terreno")
    def safe(self,fn):
        try: fn()
        except Exception as e: QMessageBox.critical(self,"Irrigation Designer",str(e))
    def create_units(self):
        lot=QgsProject.instance().mapLayer(self.lot.currentData())
        if not lot:
            QMessageBox.warning(self,"Digitalización","Seleccione primero el lote."); return
        units=create_crop_units(lot.crs())
        start_polygon_digitizing(self.iface,units)
        QMessageBox.information(self,"Digitalización",
            "Se creó 'Unidades de cultivo' y quedó activa la herramienta Agregar polígono. "
            "Digitalice directamente sobre Esri/ortofoto: clic en cada vértice y clic derecho para terminar. "
            "Puede crear varios polígonos y después guardar las ediciones.")
    def hydro(self):
        d=QgsProject.instance().mapLayer(self.dem.currentData())
        if not d: QMessageBox.warning(self,"DEM","Seleccione un DEM."); return
        try:
            result=run_hydrology(d,self.th.value())
            QMessageBox.information(self,"Hidrología DEM",result.get("message","Análisis hidrológico terminado."))
        except Exception as e:
            QMessageBox.critical(self,"Irrigation Designer",str(e))
    def crop(self):
        w=QWidget(); f=QFormLayout(w); self.cp=QComboBox(); self.cp.addItems(CROPS); self.cp.currentTextChanged.connect(self.loadcrop)
        self.kc=QDoubleSpinBox(); self.kc.setRange(.05,2); self.pl=QDoubleSpinBox(); self.pl.setRange(.05,30); self.row=QDoubleSpinBox(); self.row.setRange(.05,30); self.ref=QLabel(); self.ref.setWordWrap(True)
        for a,b in [("Cultivo:",self.cp),("Kc diseño:",self.kc),("Distancia planta (m):",self.pl),("Distancia hileras (m):",self.row),("Referencia:",self.ref)]:f.addRow(a,b)
        self.t.addTab(w,"2. Cultivo"); self.loadcrop(self.cp.currentText())
    def loadcrop(self,n):
        d=CROPS[n]; self.kc.setValue(d["kc"]); self.pl.setValue(d["plant"]); self.row.setValue(d["row"]); self.ref.setText(d["ref"]+" | Sistema inicial: "+d["method"]); self.sync_crop_method() if hasattr(self,"m") else None
    def water(self):
        w=QWidget(); f=QFormLayout(w); self.reg=QComboBox(); self.reg.addItems(REGIMES)
        self.qa=QDoubleSpinBox(); self.qa.setRange(0,100000); self.dist=QDoubleSpinBox(); self.dist.setRange(0,1000000)
        self.area_c=QDoubleSpinBox(); self.area_c.setRange(.001,1000000); self.area_c.setDecimals(3); self.area_c.setValue(1)
        self.crun=QDoubleSpinBox(); self.crun.setRange(0,1); self.crun.setSingleStep(.05); self.crun.setValue(.30)
        self.qperc=QComboBox(); self.qperc.addItems(["Q75","Q90","Q95"]); self.qperc.setCurrentText("Q90")
        self.years=QSpinBox(); self.years.setRange(1,30); self.years.setValue(10)
        ba=QPushButton("Analizar Hidrología + lote"); ba.clicked.connect(self.analyze_source)
        bp=QPushButton("Estimar Q con NASA POWER"); bp.clicked.connect(self.estimate_q)
        self.qinfo=QLabel("Q manual/aforado tiene prioridad. Q satelital es estimación preliminar."); self.qinfo.setWordWrap(True)
        f.addRow("Régimen fuente:",self.reg); f.addRow("Q disponible/adoptado (L/s):",self.qa); f.addRow("Distancia fuente-lote (m):",self.dist)
        f.addRow("",ba); f.addRow("Área aportante (km²):",self.area_c); f.addRow("Coef. escorrentía C:",self.crun)
        f.addRow("Caudal de diseño:",self.qperc); f.addRow("Años NASA POWER:",self.years); f.addRow("",bp); f.addRow(self.qinfo)
        self.t.addTab(w,"3. Agua")
    def _hydrology_layer(self):
        ls=QgsProject.instance().mapLayersByName("Hidrología")
        return ls[0] if ls else None
    def analyze_source(self):
        lot=QgsProject.instance().mapLayer(self.lot.currentData()); h=self._hydrology_layer()
        if not lot or not h:
            QMessageBox.warning(self,"Fuente","Se requieren el lote y la capa Hidrología."); return
        try:
            r=nearest_hydrology(lot,h); self.dist.setValue(r["distance_m"])
            self.qinfo.setText(f"Cauce candidato más próximo: {r['distance_m']:.1f} m. Distancia calculada geométricamente.")
        except Exception as e: QMessageBox.critical(self,"Fuente",str(e))
    def estimate_q(self):
        lot=QgsProject.instance().mapLayer(self.lot.currentData())
        if not lot: QMessageBox.warning(self,"NASA POWER","Seleccione el lote."); return
        try:
            ft=next(lot.getFeatures()); c=ft.geometry().centroid().asPoint()
            wgs=QgsCoordinateReferenceSystem("EPSG:4326")
            if lot.crs()!=wgs:
                tr=QgsCoordinateTransform(lot.crs(),wgs,QgsProject.instance()); c=tr.transform(c)
            from datetime import date
            end=date.today(); start=end.replace(year=end.year-self.years.value())
            r=estimate_power_q(c.y(),c.x(),self.area_c.value(),self.crun.value(),start.isoformat(),end.isoformat())
            key=self.qperc.currentText()+"_Ls"; self.qa.setValue(r[key])
            self.qinfo.setText(f"{self.qperc.currentText()} estimado = {r[key]:.3f} L/s | P media={r['Pmean_mm_d']:.2f} mm/d | {r['n_days']} días. Método: {r['source']}. NO equivale a aforo.")
        except Exception as e: QMessageBox.critical(self,"NASA POWER",str(e))
    def system(self):
        w=QWidget(); f=QFormLayout(w); self.m=QComboBox(); self.m.addItems(METHODS); self.mat=QComboBox(); self.mat.addItems(MATERIALS)
        self.eff=QDoubleSpinBox(); self.eff.setRange(.1,1); self.eff.setDecimals(2); self.hours=QDoubleSpinBox(); self.hours.setRange(.5,24); self.hours.setValue(12)
        self.dn=QDoubleSpinBox(); self.dn.setRange(10,1000); self.dnsec=QDoubleSpinBox(); self.dnsec.setRange(10,500); self.dnlat=QDoubleSpinBox(); self.dnlat.setRange(8,200)
        self.eq=QDoubleSpinBox(); self.eq.setRange(0,10000); self.eq.setDecimals(2); self.wet=QDoubleSpinBox(); self.wet.setRange(0,200); self.wind=QDoubleSpinBox(); self.wind.setRange(0,20)
        self.methodinfo=QLabel(); self.methodinfo.setWordWrap(True); self.matinfo=QLabel(); self.matinfo.setWordWrap(True)
        for aa,bb in [("Método:",self.m),("Material:",self.mat),("Eficiencia:",self.eff),("Horas/día:",self.hours),("DN principal mm:",self.dn),("DN secundaria mm:",self.dnsec),("DN lateral mm:",self.dnlat),("Caudal emisor L/h:",self.eq),("Diámetro mojado m:",self.wet),("Viento m/s:",self.wind),("Método - origen:",self.methodinfo),("Material - hidráulica:",self.matinfo)]: f.addRow(aa,bb)
        self.m.currentTextChanged.connect(self.load_method); self.mat.currentTextChanged.connect(self.load_material)
        self.wet.valueChanged.connect(lambda _: self.load_method(self.m.currentText()))
        self.wind.valueChanged.connect(lambda _: self.load_method(self.m.currentText()))
        self.t.addTab(w,"4. Riego")
        self.sync_crop_method(); self.load_method(self.m.currentText()); self.load_material(self.mat.currentText())
    def sync_crop_method(self):
        if not hasattr(self,"m"): return
        pref=CROPS[self.cp.currentText()]["method"].split("/")[0]; i=self.m.findText(pref)
        if i>=0: self.m.setCurrentIndex(i)
    def load_method(self,n):
        d=METHOD_PROFILES[n]
        for obj,key in [(self.eff,"eff"),(self.dn,"dn_main"),(self.dnsec,"dn_sec"),(self.dnlat,"dn_lat"),(self.eq,"emitter_lh"),(self.wet,"wet_m"),(self.wind,"wind")]: obj.setValue(d[key])
        if hasattr(self,"pr"): self.pr.setValue(d["pressure_mca"])
        from .irrigation_spacing import irrigation_spacing
        try:
            sp=irrigation_spacing(n,self.pl.value() if hasattr(self,"pl") else 1,self.row.value() if hasattr(self,"row") else 1,self.wet.value(),self.wind.value())
            extra=(" | Espaciamiento hidráulico ≈ %.2f × %.2f m (%.0f%% del diámetro mojado)"%(sp["along_m"],sp["between_m"],100*sp["factor"])) if sp["factor"] else ""
        except Exception: extra=""
        self.methodinfo.setText(d["note"]+" | Presión inicial: %.1f mca"%d["pressure_mca"]+extra)
    def load_material(self,n):
        self.matinfo.setText(MATERIAL_INFO[n]["note"])
    def final(self):
        w=QWidget(); f=QFormLayout(w); self.eto=QDoubleSpinBox(); self.eto.setRange(0,20); self.eto.setDecimals(3); self.eto.setValue(4.5)
        self.dz=QDoubleSpinBox(); self.dz.setRange(-200,5000); self.dz.setDecimals(2); self.dz.setValue(10); self.pr=QDoubleSpinBox(); self.pr.setRange(0,200); self.pr.setDecimals(2)
        self.designinfo=QLabel("ETo: manual | Desnivel: manual | Presión: método"); self.designinfo.setWordWrap(True)
        be=QPushButton("Calcular ETo con NASA POWER"); be.clicked.connect(self.auto_eto); bz=QPushButton("Estimar desnivel con DEM"); bz.clicked.connect(self.auto_dz)
        go=QPushButton("DISEÑAR Y VISUALIZAR"); go.clicked.connect(self.go); self.out=QTextEdit(); self.out.setReadOnly(True)
        f.addRow("ETo diseño mm/d:",self.eto); f.addRow("",be); f.addRow("Desnivel m:",self.dz); f.addRow("",bz); f.addRow("Presión requerida mca:",self.pr); f.addRow("Origen:",self.designinfo); f.addRow("",go); f.addRow(self.out); self.t.addTab(w,"5. Diseño"); self.load_method(self.m.currentText())
    def _lot_center_wgs84(self):
        lot=QgsProject.instance().mapLayer(self.lot.currentData())
        if not lot or lot.featureCount()==0: raise ValueError("Seleccione un lote.")
        c=next(lot.getFeatures()).geometry().centroid().asPoint(); wgs=QgsCoordinateReferenceSystem("EPSG:4326")
        if lot.crs()!=wgs: c=QgsCoordinateTransform(lot.crs(),wgs,QgsProject.instance()).transform(c)
        return c
    def auto_eto(self):
        try:
            c=self._lot_center_wgs84(); d=QgsProject.instance().mapLayer(self.dem.currentData()); elev=0.0; wgs=QgsCoordinateReferenceSystem("EPSG:4326")
            if d and d.isValid():
                pt=QgsCoordinateTransform(wgs,d.crs(),QgsProject.instance()).transform(c) if d.crs()!=wgs else c; val,ok=d.dataProvider().sample(pt,1)
                if ok: elev=float(val)
            from datetime import date,timedelta
            end=date.today()-timedelta(days=1); start=end-timedelta(days=29); r=power_eto_daily(c.y(),c.x(),start.isoformat(),end.isoformat(),elev)
            self.eto.setValue(r["eto_mean"]); self.designinfo.setText("ETo automática %.3f mm/d | %s | %d días | elev. %.1f m"%(r["eto_mean"],r["source"],r["n_days"],elev))
        except Exception as e: QMessageBox.critical(self,"ETo NASA POWER",str(e))
    def auto_dz(self):
        d=QgsProject.instance().mapLayer(self.dem.currentData()); lot=QgsProject.instance().mapLayer(self.lot.currentData())
        if not d or not lot: QMessageBox.warning(self,"Desnivel","Seleccione lote y DEM."); return
        try:
            ext=lot.extent()
            if lot.crs()!=d.crs(): ext=QgsCoordinateTransform(lot.crs(),d.crs(),QgsProject.instance()).transformBoundingBox(ext)
            st=d.dataProvider().bandStatistics(1,QgsRasterBandStats.Min|QgsRasterBandStats.Max,ext,0); dz=max(0,float(st.maximumValue)-float(st.minimumValue))
            self.dz.setValue(dz); self.designinfo.setText("Desnivel DEM preliminar %.2f m (máx-mín lote) | Presión %.1f mca según %s"%(dz,self.pr.value(),self.m.currentText()))
        except Exception as e: QMessageBox.critical(self,"Desnivel DEM",str(e))
    def go(self):
        lot=QgsProject.instance().mapLayer(self.lot.currentData())
        if not lot or lot.featureCount()==0: QMessageBox.warning(self,"Lote","Seleccione un lote."); return
        units=QgsProject.instance().mapLayersByName("Unidades de cultivo")
        if units and units[0].featureCount()>0:
            lot=units[0]
        lot,was_reprojected=ensure_metric_polygon(lot,"Lote_Trabajo_Metrico")
        ft=next(lot.getFeatures()); da=QgsDistanceArea(); da.setSourceCrs(lot.crs(),QgsProject.instance().transformContext()); da.setEllipsoid("WGS84"); ha=da.measureArea(ft.geometry())/10000
        dem=demand(ha,self.eto.value(),self.kc.value(),self.eff.value(),self.hours.value()); L=max(1,self.dist.value()+da.measurePerimeter(ft.geometry())/4); hyd=hydraulics(dem["q_lps"],L,self.dn.value(),MATERIALS[self.mat.currentText()],self.dz.value(),self.pr.value()); sem,rec=water_status(self.dist.value(),self.qa.value(),dem["q_lps"],self.reg.currentText(),hyd["tdh_m"]); ns=sectors_needed(dem["q_lps"],self.qa.value()); net=design_network(lot,self.m.currentText(),self.pl.value(),self.row.value(),self.eq.value(),dem["q_lps"],self.mat.currentText(),self.dn.value(),self.dnsec.value(),self.dnlat.value(),hyd["tdh_m"],hyd["power_kw"],wetted_diameter_m=self.wet.value(),wind_ms=self.wind.value())
        extra=""
        if self.m.currentText()=="Aspersión":
            ss,fr=sprinkler_spacing(self.wet.value(),self.wind.value()); extra=f"\nSeparación inicial aspersores: {ss:.1f} m ({fr:.0%} D mojado)."
        self.out.setText(f"Área {ha:.2f} ha | densidad teórica {density(self.pl.value(),self.row.value()):.0f} plantas/ha\nETc {dem['net_mm']:.2f} mm/d | Q {dem['q_lps']:.2f} L/s\nSectores propuestos: {ns}\nHf {hyd['hf_m']:.2f} m | TDH {hyd['tdh_m']:.2f} m | Potencia {hyd['power_kw']:.2f} kW\nFuente {sem}: {rec}{extra}\nDiseño generado para todas las unidades digitalizadas: {net['n_laterals']} laterales y {net['n_emitters']} emisores. Capas con atributos y etiquetas.")
