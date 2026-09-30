import math
def sprinkler_overlap_factor(wind_ms):
    """Preliminary spacing/wetted-diameter ratio; more overlap as wind rises."""
    w=max(0.0,float(wind_ms))
    if w < 2.0: return 0.65
    if w < 4.0: return 0.60
    if w < 6.0: return 0.55
    return 0.50

def irrigation_spacing(method, plant_spacing, row_spacing, wetted_diameter_m, wind_ms=0.0, overlap_factor=None):
    m=(method or "").lower()
    if "aspers" in m:
        d=float(wetted_diameter_m)
        if d<=0: raise ValueError("Aspersión/microaspersión requiere diámetro mojado > 0.")
        f=float(overlap_factor) if overlap_factor is not None else sprinkler_overlap_factor(wind_ms)
        if not (0.30 <= f <= 0.80): raise ValueError("Factor de espaciamiento/diámetro fuera de rango 0.30–0.80.")
        spacing=d*f
        return {"along_m":spacing,"between_m":spacing,"factor":f,"basis":"diametro_mojado_solape"}
    if "gravedad" in m:
        return {"along_m":0.0,"between_m":0.0,"factor":0.0,"basis":"sin_emisores_puntuales"}
    if plant_spacing<=0 or row_spacing<=0: raise ValueError("Goteo requiere marco de plantación > 0.")
    return {"along_m":float(plant_spacing),"between_m":float(row_spacing),"factor":None,"basis":"marco_plantacion"}

def estimated_emitters(area_m2, method, plant_spacing, row_spacing, wetted_diameter_m, wind_ms=0.0, overlap_factor=None):
    sp=irrigation_spacing(method,plant_spacing,row_spacing,wetted_diameter_m,wind_ms,overlap_factor)
    if sp["along_m"]<=0 or sp["between_m"]<=0: return 0
    return max(1, math.ceil(float(area_m2)/(sp["along_m"]*sp["between_m"])))
