from math import pi,ceil
G=9.80665
def demand(area_ha,eto,kc,eff,hours):
    if area_ha<=0 or eto<0 or kc<=0 or not 0<eff<=1 or not 0<hours<=24: raise ValueError("Entradas inválidas")
    net=eto*kc; gross=net/eff; vol=area_ha*gross*10; q=vol*1000/(hours*3600)
    return {"net_mm":net,"gross_mm":gross,"volume_m3d":vol,"q_lps":q}
def density(plant,row): 
    if plant<=0 or row<=0: raise ValueError("Espaciamiento inválido")
    return 10000/(plant*row)
def hf_hw(q_lps,L,D_mm,C):
    if q_lps<0 or L<0 or D_mm<=0 or C<=0: raise ValueError("Hazen-Williams inválido")
    return 10.67*L*(q_lps/1000)**1.852/(C**1.852*(D_mm/1000)**4.8704)
def hydraulics(q,L,D,C,dz,pressure,eta=.70):
    hf=hf_hw(q,L,D,C); tdh=max(0,dz)+pressure+hf
    v=(q/1000)/(pi*(D/1000)**2/4); power=1000*G*(q/1000)*tdh/eta/1000
    return {"hf_m":hf,"tdh_m":tdh,"velocity_ms":v,"power_kw":power}
def water_status(distance,qa,qr,regime,tdh=0):
    if qr<=0 or qa is None or qa<0 or regime=="Desconocido": return "GRIS","Faltan datos confiables de caudal/permanencia."
    ratio=qa/qr
    if regime=="Efímero": return "ROJO","Cauce efímero: no asumir suministro continuo."
    if ratio<1: return "ROJO",f"Caudal disponible cubre {ratio:.0%} de demanda pico."
    if ratio>=1.25 and regime=="Permanente" and distance<=1000 and tdh<=60: return "VERDE","Favorable preliminar; verificar estiaje, calidad y permisos."
    return "AMARILLO","Posible con restricciones; revisar estacionalidad, conducción y energía."
def sprinkler_spacing(wetted_diameter,wind_ms=2):
    if wetted_diameter<=0: raise ValueError("Diámetro mojado inválido")
    # preselección conservadora; no equivale a uniformidad medida
    frac=.60 if wind_ms<=2 else .50 if wind_ms<=4 else .40
    return wetted_diameter*frac, frac
def sectors_needed(q_total,q_available,desired_max=8):
    if q_total<=0: return 1
    if q_available is None or q_available<=0: return 1
    return max(1,min(desired_max,ceil(q_total/q_available)))
