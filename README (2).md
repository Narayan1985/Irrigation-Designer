# Irrigation Designer Spatial for QGIS

**Español:** consulte la primera parte del documento.\
**English:** [English
version](#irrigation-designer-spatial-for-qgis--english)

------------------------------------------------------------------------

**Irrigation Designer Spatial** es un complemento experimental para QGIS
orientado al **prediseño espacial, agronómico e hidráulico de sistemas
de riego**. Integra información del lote, modelos digitales de elevación
(DEM), hidrología, clima, cultivo, método de riego y parámetros
hidráulicos para generar una red de riego editable y visualizable
directamente en QGIS.

> **Versión actual:** 1.2.1\
> **QGIS mínimo:** 3.28\
> **Entorno de prueba principal:** QGIS 3.44.5 Solothurn / Python
> 3.12.12\
> **Estado:** Experimental --- herramienta de prediseño y apoyo a la
> toma de decisiones.

------------------------------------------------------------------------

## Objetivo

El proyecto busca desarrollar una herramienta abierta que permita pasar
de la información espacial y agroclimática a un esquema preliminar de
diseño de riego mediante el flujo:

**Lote → DEM → hidrología → fuente de agua → clima → cultivo → demanda
hídrica → método de riego → distribución espacial → hidráulica → bombeo
→ visualización GIS**

El complemento no pretende reemplazar la verificación hidráulica
detallada, el levantamiento topográfico de campo, los aforos, las fichas
técnicas de fabricantes ni el diseño firmado por un profesional
responsable.

## Funcionalidades actuales

### Información espacial

-   Selección de un lote existente.
-   Digitalización de **unidades de cultivo** directamente sobre
    cartografía o imagen de referencia.
-   Uso de Esri World Imagery como referencia visual.
-   Soporte para DEM en CRS proyectado.
-   Reproyección automática de DEM/lotes geográficos WGS84 a un CRS UTM
    local de trabajo.
-   Procesamiento de múltiples unidades de cultivo.
-   Conservación de la geometría original y uso de copias métricas para
    cálculos de distancia y área.

### DEM e hidrología

-   Generación de productos hidrológicos a partir del DEM mediante
    herramientas disponibles en QGIS/GRASS.
-   Capa vectorial final denominada **`Hidrología`**.
-   Identificación preliminar de drenajes/cauces potenciales.
-   Cálculo de distancia entre lote y cauce candidato.
-   Clasificación preliminar de fuentes mediante un esquema tipo
    semáforo.

Los cauces derivados exclusivamente del DEM representan
**concentraciones topográficas potenciales de flujo**; no demuestran por
sí solos que exista agua permanente ni un caudal aprovechable.

### Clima y ETo

La versión 1.2 incorpora consulta opcional de **NASA POWER** y cálculo
de evapotranspiración de referencia mediante **FAO-56 Penman-Monteith**.

Variables empleadas:

-   temperatura máxima;
-   temperatura mínima;
-   humedad relativa;
-   velocidad del viento a 2 m;
-   radiación solar.

La ETo permanece editable para permitir el uso de estaciones
meteorológicas, series locales u otras fuentes de mayor resolución.

### Cultivos

El catálogo incluye actualmente sistemas como:

-   cacao;
-   café;
-   banano/plátano;
-   caña de azúcar;
-   aguacate;
-   cítricos;
-   maíz;
-   papa;
-   otros sistemas configurables.

Los parámetros agronómicos son editables. Los valores precargados deben
interpretarse como valores iniciales de referencia y no como sustitutos
de información local validada.

### Métodos de riego

Se contemplan:

-   goteo;
-   microaspersión;
-   aspersión;
-   gravedad.

La interfaz es **reactiva**: al cambiar el método se actualizan
parámetros iniciales relacionados con eficiencia, presión requerida,
caudal del emisor, diámetro mojado y diámetros nominales iniciales.

#### Goteo

La geometría de emisores y laterales se relaciona principalmente con el
marco de plantación.

#### Microaspersión y aspersión

La separación de emisores depende del **diámetro mojado** y de un factor
preliminar de espaciamiento/solape. Por tanto, un aspersor con mayor
diámetro mojado genera una malla más amplia y, para una misma
superficie, un menor número de emisores.

El factor de espaciamiento se reduce con el aumento del viento para
incrementar el solape. Estos factores son criterios preliminares y deben
contrastarse con:

-   curva y patrón de distribución del fabricante;
-   presión de funcionamiento;
-   velocidad y dirección del viento;
-   espaciamiento triangular o rectangular;
-   coeficiente de uniformidad;
-   uniformidad de distribución requerida.

#### Gravedad

El modo de gravedad no genera artificialmente emisores puntuales.

## Red hidráulica generada

El complemento puede producir capas editables para:

-   **Bomba**
-   **Tubería principal**
-   **Tuberías secundarias**
-   **Laterales**
-   **Emisores**
-   **Accesorios y uniones**

Entre los atributos hidráulicos disponibles se encuentran:

-   unidad y sector;
-   DN;
-   diámetro interno;
-   longitud;
-   caudal;
-   velocidad;
-   pérdida de carga;
-   presión inicial;
-   presión final;
-   TDH;
-   potencia de bombeo;
-   tipo y caudal del emisor.

Las presiones y pérdidas se expresan también en **metros de columna de
agua (m.c.a.)**.

## Accesorios y pérdidas menores

La capa **`Accesorios y uniones`** permite representar conexiones de la
red. La identificación automática inicial incluye conexiones tipo T y
conexiones de laterales, dejando los atributos editables para corrección
por parte del diseñador.

Las pérdidas menores se representan mediante:

\[ h_m = K`\frac{v^2}{2g}`{=tex} \]

donde:

-   (h_m): pérdida menor, m.c.a.;
-   (K): coeficiente del accesorio;
-   (v): velocidad, m/s;
-   (g): aceleración de la gravedad, m/s².

La geometría por sí sola no siempre permite determinar de manera
inequívoca si existe un codo, T, reducción, válvula o cruce sin
conexión. Por ello, la clasificación automática debe ser revisada.

## Materiales de tubería

Actualmente se contemplan materiales como:

-   PVC;
-   PEAD / HDPE;
-   PEBD;
-   acero comercial;
-   hierro dúctil.

El complemento maneja coeficientes hidráulicos iniciales, pero **no
inventa el espesor de pared**. El diámetro interno real depende de
información como:

-   DN;
-   PN;
-   SDR;
-   clase;
-   serie;
-   fabricante.

Mientras no se disponga de un catálogo específico, el diámetro interno
debe considerarse provisional.

## Disponibilidad hídrica

El módulo permite trabajar con caudal medido o con una estimación
preliminar. Cuando no existe aforo, puede utilizar precipitación NASA
POWER, área aportante y coeficiente de escorrentía para obtener
indicadores exploratorios como:

-   Q medio;
-   Q75;
-   Q90;
-   Q95.

Una estimación hidrológica **no equivale a un aforo** y no demuestra
disponibilidad legal del recurso.

## Instalación

1.  Descargar el ZIP del complemento.
2.  Abrir QGIS.
3.  Ir a **Complementos → Administrar e instalar complementos**.
4.  Seleccionar **Instalar a partir de ZIP**.
5.  Elegir el archivo del complemento.
6.  Activar **Irrigation Designer Spatial**.

Para evitar conflictos con versiones antiguas durante desarrollo, es
recomendable eliminar previamente una instalación anterior de
`irrigation_designer_spatial` antes de instalar una versión nueva.

## Flujo de trabajo recomendado

1.  Cargar o seleccionar el lote.
2.  Cargar el DEM.
3.  Añadir una imagen de referencia u ortofoto si está disponible.
4.  Digitalizar las unidades reales de cultivo.
5.  Generar/revisar la hidrología.
6.  Definir o revisar la fuente de agua.
7.  Seleccionar el cultivo y verificar sus parámetros.
8.  Seleccionar el método de riego.
9.  Revisar material y parámetros de tubería.
10. Calcular o ingresar ETo.
11. Estimar/revisar el desnivel.
12. Verificar presión requerida.
13. Ejecutar **Diseñar y visualizar**.
14. Revisar espacialmente tuberías, emisores, accesorios, caudales,
    pérdidas y presiones.
15. Editar los elementos que no representen adecuadamente las
    condiciones reales del terreno.

## Interpretación de valores automáticos

El proyecto procura diferenciar entre datos:

-   **calculados**;
-   **derivados del DEM**;
-   **obtenidos de NASA POWER**;
-   **procedentes del catálogo**;
-   **recomendados inicialmente**;
-   **ingresados manualmente**.

Los valores automáticos deben poder ser sustituidos cuando se disponga
de información de campo o datos de fabricante de mayor calidad.

## Validación realizada

Durante el desarrollo se han ejecutado pruebas automáticas de:

-   compilación de módulos Python;
-   imports de clases QGIS;
-   cálculos hidráulicos;
-   transformaciones CRS;
-   procesamiento de múltiples unidades;
-   geometría dependiente del método de riego;
-   relación entre diámetro mojado y número de aspersores.

En la versión 1.2.1 se realizaron, entre otras:

-   **100/100 pruebas** de monotonicidad del diámetro mojado: aumentar
    el diámetro no incrementó el número estimado de aspersores;
-   **50/50 modelos** de espaciamiento;
-   verificación de ausencia de emisores puntuales en el modo de
    gravedad.

Estas pruebas no sustituyen la validación en campo ni una campaña formal
de comparación contra redes hidráulicas observadas o software
especializado.

## Limitaciones actuales

La versión actual debe considerarse de **prediseño**. Entre los aspectos
que todavía requieren desarrollo o validación adicional están:

-   selección explícita y persistente del punto de captación y de la
    bomba;
-   cálculo del desnivel sobre la ruta hidráulica real hasta el emisor
    crítico;
-   delimitación automática de la cuenca aportante en el punto de
    captación;
-   incorporación directa de productos de runoff como ERA5-Land/GLDAS;
-   dimensionamiento automático con catálogos comerciales reales;
-   PN/SDR/clase y diámetro interno real;
-   hidráulica nodo a nodo de laterales con múltiples salidas;
-   presión en cada emisor;
-   uniformidad de emisión y distribución;
-   curvas reales Q-H de bombas;
-   punto de operación bomba--sistema;
-   pérdidas en válvulas y accesorios con catálogos específicos;
-   análisis de golpe de ariete;
-   rutas óptimas de tubería condicionadas por topografía y obstáculos;
-   persistencia completa del proyecto en GeoPackage;
-   validación comparativa con EPANET/WNTR y casos de campo.

## Criterio de uso

Los resultados deben entenderse como apoyo al análisis técnico. Antes de
construir una instalación se deben verificar, como mínimo:

1.  topografía;
2.  caudal realmente disponible;
3.  calidad y régimen de la fuente;
4.  derechos/permisos de uso del agua;
5.  propiedades del suelo;
6.  demanda real del cultivo;
7.  especificaciones de emisores;
8.  diámetros internos reales;
9.  presiones máximas y mínimas;
10. curva de la bomba;
11. uniformidad hidráulica;
12. condiciones de operación y mantenimiento.

## Estructura conceptual del proyecto

``` text
irrigation_designer_spatial/
├── plugin.py
├── wizard.py
├── design_network.py
├── irrigation_spacing.py
├── climate_power.py
├── hydrology.py
├── water_availability.py
├── hydraulics.py
├── catalogs.py
├── crs_utils.py
├── digitizing.py
└── ...
```

## Roadmap

Las prioridades de desarrollo son:

**1. Topología hidráulica real.** Una fuente y bomba globales, principal
común y ramificaciones hacia unidades/sectores.

**2. Dimensionamiento automático.** Selección de diámetro comercial
mediante restricciones de velocidad, pérdida de carga, presión y
material.

**3. Emisor crítico.** Muestreo de elevación del DEM y balance de
presión hasta el punto hidráulicamente más desfavorable.

**4. Catálogos reales.** Incorporación de PN/SDR, diámetro interno,
accesorios, goteros, microaspersores, aspersores y bombas.

**5. Hidrología avanzada.** Cuenca aportante automática y escenarios de
disponibilidad hídrica.

**6. Recalcular hidráulica.** Permitir que el usuario edite la red en
QGIS y posteriormente recalcule todos los parámetros.

**7. Validación externa.** Comparación sistemática con cálculos
manuales, EPANET/WNTR y sistemas de riego reales.

## Referencias técnicas principales

-   Allen, R. G., Pereira, L. S., Raes, D. & Smith, M. *Crop
    Evapotranspiration: Guidelines for Computing Crop Water
    Requirements*. FAO Irrigation and Drainage Paper 56.
-   NASA POWER --- Prediction Of Worldwide Energy Resources.
-   QGIS --- Geographic Information System.
-   GRASS GIS --- herramientas de análisis hidrológico utilizadas desde
    el entorno QGIS.

## Contribuciones

El proyecto se encuentra en desarrollo activo. Son especialmente útiles
contribuciones relacionadas con:

-   hidráulica de riego;
-   agronomía;
-   hidrología;
-   QGIS/PyQGIS;
-   validación con casos reales;
-   catálogos de tuberías y emisores;
-   pruebas automatizadas;
-   documentación.

Al reportar un error se recomienda incluir:

-   versión de QGIS;
-   versión de Python;
-   sistema operativo;
-   traceback completo;
-   CRS del lote y DEM;
-   método de riego seleccionado;
-   pasos necesarios para reproducir el problema.

## Licencia

**Pendiente de definir antes de publicar el repositorio.**

Se recomienda incorporar un archivo `LICENSE` explícito. La ausencia de
una licencia no convierte automáticamente el código en software de libre
uso o redistribución.

## Autoría y contacto

**Creador:** Julián Valencia\
**Formación:** Ingeniero Agrónomo, MSc, PhD\
**Correo electrónico:** julian.valencia@unisarc.edu.co

Irrigation Designer Spatial es un proyecto orientado al desarrollo de
herramientas GIS para el prediseño agrohidráulico de sistemas de riego.

------------------------------------------------------------------------

# Irrigation Designer Spatial for QGIS --- English

**Irrigation Designer Spatial** is an experimental QGIS plugin for the
**spatial, agronomic, and hydraulic preliminary design of irrigation
systems**. It integrates field geometry, digital elevation models (DEM),
hydrology, climate, crop information, irrigation method, and hydraulic
parameters to generate an editable irrigation network directly in QGIS.

> **Current version:** 1.2.1\
> **Minimum QGIS:** 3.28\
> **Primary test environment:** QGIS 3.44.5 Solothurn / Python 3.12.12\
> **Status:** Experimental --- preliminary design and decision-support
> tool.

## Objective

The project aims to provide an open GIS-based workflow:

**Field → DEM → hydrology → water source → climate → crop → crop water
demand → irrigation method → spatial layout → hydraulics → pumping → GIS
visualization**

It does not replace detailed engineering verification, field topographic
surveys, streamflow measurements, manufacturer specifications, legal
water-use requirements, or professional engineering review.

## Current capabilities

### Spatial information

-   Select an existing field polygon.
-   Digitize editable **crop units** over reference imagery.
-   Use Esri World Imagery as visual reference.
-   Work with projected DEMs.
-   Automatically transform geographic WGS84 data to a local metric UTM
    working CRS.
-   Process multiple crop units.

### DEM and hydrology

-   Generate preliminary hydrologic products using available QGIS/GRASS
    tools.
-   Produce a final vector layer named **`Hidrología`**.
-   Identify potential drainage/stream paths.
-   Calculate preliminary field-to-water-source distance.
-   Apply a preliminary suitability traffic-light classification.

DEM-derived drainage represents **potential topographic flow
concentration** and does not prove permanent water presence or available
discharge.

### Climate and reference evapotranspiration

Version 1.2 includes optional **NASA POWER** retrieval and reference
evapotranspiration calculation using **FAO-56 Penman-Monteith**.

Inputs include maximum and minimum temperature, relative humidity, 2-m
wind speed, and solar radiation. ETo remains editable so local
weather-station data can replace gridded climate information.

### Crops

The catalog includes crops such as cacao, coffee, banana/plantain,
sugarcane, avocado, citrus, maize, potato, and configurable systems.
Agronomic parameters remain editable and should be validated with local
information.

### Irrigation methods

Supported methods include: - drip irrigation; - microsprinkler
irrigation; - sprinkler irrigation; - gravity irrigation.

The interface is reactive: changing irrigation method updates initial
efficiency, required pressure, emitter discharge, wetted diameter, and
preliminary nominal pipe diameters.

#### Drip irrigation

Emitter and lateral geometry is primarily linked to crop planting
arrangement.

#### Microsprinkler and sprinkler irrigation

Emitter spacing depends on **wetted diameter** and a preliminary
spacing/overlap factor. Therefore, increasing wetted diameter increases
spacing and reduces the number of emitters required for the same area.

The preliminary spacing factor decreases as wind increases to provide
greater overlap. Final spacing must be checked against manufacturer
distribution patterns, operating pressure, wind, layout geometry, and
required distribution uniformity.

#### Gravity irrigation

Gravity mode does not artificially generate point emitters.

## Hydraulic network

The plugin can generate editable layers for: - **Pump** - **Main
pipe** - **Secondary pipes** - **Laterals** - **Emitters** - **Fittings
and joints**

Available attributes include unit/sector, nominal diameter, internal
diameter, length, discharge, velocity, head loss, upstream/downstream
pressure, TDH, pump power, emitter type, and emitter discharge.

Pressure and head-loss values are also expressed in **meters of water
column (m.w.c. / m H₂O)**.

## Fittings and minor losses

The **Fittings and joints** layer represents network connections.
Preliminary automatic classification includes tees and lateral
connections, while attributes remain editable.

Minor losses follow:

\[ h_m = K`\frac{v^2}{2g}`{=tex} \]

Geometry alone cannot always distinguish elbows, tees, reducers, valves,
or non-connected crossings; automatic classification therefore requires
engineering review.

## Pipe materials

Current material options include PVC, HDPE, LDPE, commercial steel, and
ductile iron.

The plugin provides initial hydraulic coefficients but does **not
fabricate pipe wall thickness**. Actual internal diameter depends on DN,
PN, SDR, class/series, and manufacturer data.

## Water availability

The module can use measured discharge or a preliminary estimate. When
gauging data are unavailable, NASA POWER precipitation, contributing
area, and a runoff coefficient can support exploratory Qmean, Q75, Q90,
and Q95 indicators.

A hydrologic estimate is **not equivalent to a streamflow measurement**
and does not establish legal water availability.

## Installation

1.  Download the plugin ZIP.
2.  Open QGIS.
3.  Go to **Plugins → Manage and Install Plugins**.
4.  Select **Install from ZIP**.
5.  Choose the downloaded file.
6.  Enable **Irrigation Designer Spatial**.

During development, removing an older `irrigation_designer_spatial`
installation before installing a new build is recommended.

## Recommended workflow

1.  Load/select the field.
2.  Load the DEM.
3.  Add reference imagery or an orthophoto when available.
4.  Digitize actual crop units.
5.  Generate and review hydrology.
6.  Define/review the water source.
7.  Select the crop and verify agronomic parameters.
8.  Select the irrigation method.
9.  Review pipe material and hydraulic parameters.
10. Calculate or enter ETo.
11. Estimate/review elevation difference.
12. Verify required operating pressure.
13. Run **Design and visualize**.
14. Review pipes, emitters, fittings, discharge, losses, and pressure
    spatially.
15. Edit elements that do not represent actual field conditions.

## Validation

Development testing has included Python module compilation, QGIS import
checks, hydraulic calculations, CRS transformations, multiple crop
units, method-dependent geometry, and wetted-diameter/emitter-count
behavior.

Version 1.2.1 includes: - **100/100 monotonicity tests** confirming that
increasing wetted diameter did not increase the estimated sprinkler
count; - **50/50 spacing-model tests**; - verification that gravity mode
does not generate point emitters.

These tests do not replace field validation or systematic comparison
with observed networks or specialized hydraulic software.

## Current limitations

The current release is a **preliminary-design tool**. Further
development is required for: - explicit persistent intake and pump
locations; - hydraulic-path elevation difference to the critical
emitter; - automatic upstream watershed delineation; - direct
ERA5-Land/GLDAS runoff integration; - automatic commercial pipe
sizing; - real PN/SDR/class and internal diameter catalogs; -
node-by-node multiple-outlet lateral hydraulics; - pressure at every
emitter; - emission/distribution uniformity; - real pump Q-H and
efficiency curves; - pump-system operating point; - catalog-based
fitting/valve losses; - surge/water-hammer analysis; -
terrain/obstacle-aware pipe routing; - full GeoPackage persistence; -
systematic EPANET/WNTR and field validation.

## Technical use criterion

Before construction, users should verify topography, actual water
availability, source regime and quality, legal water-use requirements,
soil properties, crop demand, emitter specifications, real internal pipe
diameters, allowable pressures, pump curves, hydraulic uniformity, and
operation/maintenance conditions.

## Roadmap

1.  Real hydraulic topology with a global source/pump and branched
    network.
2.  Automatic commercial pipe sizing under velocity, head-loss, and
    pressure constraints.
3.  DEM-based critical-emitter hydraulic path.
4.  Real catalogs for pipes, fittings, emitters, sprinklers, and pumps.
5.  Advanced watershed and water-availability analysis.
6.  **Recalculate hydraulics** after manual network editing in QGIS.
7.  Systematic validation against manual calculations, EPANET/WNTR, and
    field systems.

## Main technical references

-   Allen, R. G., Pereira, L. S., Raes, D. & Smith, M. *Crop
    Evapotranspiration: Guidelines for Computing Crop Water
    Requirements*. FAO Irrigation and Drainage Paper 56.
-   NASA POWER --- Prediction Of Worldwide Energy Resources.
-   QGIS --- Geographic Information System.
-   GRASS GIS --- hydrologic analysis tools accessed through QGIS.

## Contributions

Contributions are welcome in irrigation hydraulics, agronomy, hydrology,
PyQGIS, field validation, pipe/emitter catalogs, automated testing, and
documentation.

Bug reports should preferably include QGIS version, Python version,
operating system, complete traceback, field and DEM CRS, irrigation
method, and reproducible steps.

## License

**To be defined before repository publication.**

An explicit `LICENSE` file should be added. Without a license, source
code is not automatically granted open reuse or redistribution rights.

## Author and contact

**Creator:** Julián Valencia\
**Qualifications:** Agronomist, MSc, PhD\
**Email:** julian.valencia@unisarc.edu.co
