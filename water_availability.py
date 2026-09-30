import json, math
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from datetime import date, timedelta

POWER_URL="https://power.larc.nasa.gov/api/temporal/daily/point"

def runoff_to_flow_lps(runoff_mm_day, area_km2):
    """1 mm over 1 km2 = 1,000 m3; divide by 86400 s and convert to L/s."""
    if runoff_mm_day < 0 or area_km2 <= 0: raise ValueError("Runoff/área inválidos")
    return runoff_mm_day * area_km2 * 1000.0 / 86.4

def rainfall_runoff_flow_lps(precip_mm_day, area_km2, runoff_coeff):
    if not 0 <= runoff_coeff <= 1: raise ValueError("Coeficiente C debe estar entre 0 y 1")
    return runoff_to_flow_lps(precip_mm_day*runoff_coeff, area_km2)

def percentile(values,p):
    vals=sorted(float(v) for v in values if v is not None and math.isfinite(float(v)))
    if not vals: raise ValueError("Serie vacía")
    # Flow exceedance Qp: value equaled/exceeded p% of time = lower-tail quantile 1-p.
    q=max(0,min(1,1-p/100.0)); pos=q*(len(vals)-1); lo=int(math.floor(pos)); hi=int(math.ceil(pos))
    return vals[lo] if lo==hi else vals[lo]+(vals[hi]-vals[lo])*(pos-lo)

def power_precip_daily(lat,lon,start,end,timeout=30):
    params={"parameters":"PRECTOTCORR","community":"AG","longitude":lon,"latitude":lat,
            "start":start.replace("-",""),"end":end.replace("-",""),"format":"JSON"}
    req=Request(POWER_URL+"?"+urlencode(params),headers={"User-Agent":"QGIS-Irrigation-Designer/0.7"})
    with urlopen(req,timeout=timeout) as r: data=json.loads(r.read().decode("utf-8"))
    series=data["properties"]["parameter"]["PRECTOTCORR"]
    return [float(v) for _,v in sorted(series.items()) if v is not None and float(v)>-900]

def estimate_power_q(lat,lon,area_km2,runoff_coeff,start,end):
    p=power_precip_daily(lat,lon,start,end)
    q=[rainfall_runoff_flow_lps(x,area_km2,runoff_coeff) for x in p]
    return {"Pmean_mm_d":sum(p)/len(p),"Qmean_Ls":sum(q)/len(q),
            "Q75_Ls":percentile(q,75),"Q90_Ls":percentile(q,90),"Q95_Ls":percentile(q,95),
            "n_days":len(q),"source":"NASA POWER PRECTOTCORR + coeficiente de escorrentía"}
