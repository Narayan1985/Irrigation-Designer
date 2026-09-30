# Irrigation Designer QGIS v0.6
Incluye: Esri World Imagery como referencia, catálogo ampliado (cacao, café, banano, caña de azúcar, aguacate, cítricos, maíz, papa), marco de siembra editable, densidad, hidrología DEM mediante GRASS r.stream.extract, semáforo de fuente, sectorización propuesta, emisores editables y preselección de espaciamiento de aspersores.
## Limitaciones
La imagen base es referencia visual. No se infieren automáticamente hileras/obstáculos desde la imagen.
Los cauces DEM son candidatos topográficos, no prueba de agua permanente.
La separación de aspersores es una preselección geométrica; CU requiere patrón radial/datos del aspersor.
La validación automatizada fuera de QGIS no sustituye una prueba GUI real con QGIS + GRASS.

## v0.6.1
Acepta DEM geográfico WGS84/EPSG:4326. Si el DEM está en grados, crea automáticamente una copia de trabajo UTM métrica según el centro del DEM, usando remuestreo bilinear, conserva el original y ejecuta la hidrología sobre la copia.

## v0.6.4
La red vectorial final derivada del DEM se presenta en QGIS con el nombre visible `Hidrología`.

## v0.7.0 — disponibilidad hídrica
- Calcula automáticamente la distancia entre lote y cauce candidato más próximo de `Hidrología`.
- Descarga precipitación diaria NASA POWER PRECTOTCORR para el centro del lote.
- Estima Qmean, Q75, Q90 y Q95 a partir de precipitación, área aportante y C de escorrentía.
- El Q estimado se etiqueta como estimación preliminar; no sustituye aforo.
- Área aportante y C permanecen explícitos/editables hasta implementar delimitación automática de cuenca y runoff directo ERA5-Land/GLDAS.

## v0.8.0 — Spatial Hydraulic Design
- Nueva capa editable `Unidades de cultivo` para digitalización sobre ortofoto/Esri World Imagery.
- El diseño deja de usar sectores en bandas como producto principal.
- Genera: `Bomba`, `Tubería principal`, `Tuberías secundarias`, `Laterales`, `Emisores`.
- Atributos hidráulicos y etiquetas visibles en QGIS: DN, Q, Hf, TDH y potencia.
- Laterales orientados inicialmente por el eje mayor del lote y recortados a su geometría.
- Emisores distribuidos sobre laterales según marco indicado.
- Esri World Imagery se usa como referencia visual; no se redistribuye ni se presenta como ortofoto propia.
- La digitalización manual de unidades reales tiene prioridad sobre inferencias visuales automáticas.

## v0.9.0 — QGIS runtime fixes and real digitizing workflow
1. Add Esri World Imagery or load own orthophoto.
2. Select original lot even if it is EPSG:4326.
3. Press `Crear capa para digitalizar unidades de cultivo`.
4. QGIS activates its native Add Polygon Feature tool. Click vertices following visible real crop-unit boundaries; right-click to finish each polygon.
5. Save edits. If `Unidades de cultivo` contains polygons, Design uses these polygons instead of blindly partitioning the original lot.
6. Geographic lot layers are copied/reprojected internally to a local metric UTM layer. Original geometry is preserved.
7. Outputs show Pump, Main, Secondary, Laterals and Emitters with map labels.
The plugin package name changed to `irrigation_designer_spatial` to prevent stale files from old versions being imported.

## v0.9.1 — QGIS 3.44 renderer compatibility
Corrected all vector renderer assignments to use QgsSingleSymbolRenderer around QgsMarkerSymbol/QgsLineSymbol.
Validated statically against the QGIS API contract exposed by the user's QGIS 3.44.5 traceback.

## v1.0.0 — Multi-unit and portable spatial design
- Every polygon in `Unidades de cultivo` is processed; no `next()`-only first-unit design.
- Total irrigation flow is distributed among units proportional to their actual area.
- Each pump/main/secondary/lateral/emitter carries `unidad`.
- Labels are applied after merging all unit outputs.
- Corrected QGIS scale visibility: laterals <=1:5000; emitter labels <=1:2500.
- Geographic input is transformed to a local UTM work CRS based on the dataset itself, independent of country.
- No Colombia-specific EPSG is hardcoded.

## v1.1.0 — plano hidráulico
- Etiquetas de tubería: DN, diámetro interno, longitud, Q, velocidad, Hf [mca], presión inicial/final [mca].
- Emisor: tipo, caudal [L/h] y presión objetivo [mca].
- Nueva capa `Accesorios y uniones`, inicialmente con T y conexiones de lateral derivadas de la topología.
- Campos K, velocidad y pérdida menor Hm [mca].
- Los accesorios automáticos quedan editables. No se asigna pared/SDR ficticia: hasta seleccionar catálogo/PN/SDR, Dint=DN explícitamente.

## v1.1.1 — accessory scope hotfix
- Fixed NameError `acc is not defined` in `_design_single`.
- `Accesorios y uniones` is created only after all crop-unit designs are merged.
- Added guards for empty/invalid line geometries before accessory-node extraction.

## v1.2.0
Interfaz reactiva por cultivo/método/material; ETo NASA POWER+FAO56 y desnivel DEM automáticos opcionales; valores editables y origen visible.

## v1.2.1 — geometría dependiente del método
- Goteo: espaciamiento de emisores/laterales basado en marco de plantación.
- Microaspersión y aspersión: espaciamiento calculado como fracción editable/derivable del diámetro mojado; mayor diámetro reduce automáticamente el número de emisores.
- El factor automático disminuye con viento para aumentar solape (0.65, 0.60, 0.55, 0.50).
- Gravedad: no debe crear emisores puntuales.
- La interfaz muestra el espaciamiento hidráulico resultante.

# Autor / Author

## Español

**Creador:** Julián Valencia  
**Formación:** Ingeniero Agrónomo, MSc, PhD  
**Correo electrónico:** julian.valencia@unisarc.edu.co

## English

**Creator:** Julián Valencia  
**Qualifications:** Agronomist, MSc, PhD  
**Email:** julian.valencia@unisarc.edu.co

