import json, math
from urllib.parse import urlencode
from urllib.request import urlopen, Request
POWER_URL="https://power.larc.nasa.gov/api/temporal/daily/point"
def _svp(t): return 0.6108*math.exp(17.27*t/(t+237.3))
def _eto(lat,elev,doy,tmax,tmin,rh,wind2,rs):
    t=(tmax+tmin)/2; es=(_svp(tmax)+_svp(tmin))/2; ea=es*rh/100
    delta=4098*_svp(t)/((t+237.3)**2); p=101.3*((293-0.0065*elev)/293)**5.26; gamma=.000665*p
    phi=math.radians(lat); dr=1+.033*math.cos(2*math.pi*doy/365); dec=.409*math.sin(2*math.pi*doy/365-1.39)
    ws=math.acos(max(-1,min(1,-math.tan(phi)*math.tan(dec))))
    ra=(24*60/math.pi)*.0820*dr*(ws*math.sin(phi)*math.sin(dec)+math.cos(phi)*math.cos(dec)*math.sin(ws))
    rso=(.75+2e-5*elev)*ra; ratio=min(1,rs/rso) if rso>0 else 0
    rnl=4.903e-9*(((tmax+273.16)**4+(tmin+273.16)**4)/2)*(.34-.14*math.sqrt(max(0,ea)))*(1.35*ratio-.35)
    rn=.77*rs-rnl
    return max(0,(.408*delta*rn+gamma*(900/(t+273))*wind2*(es-ea))/(delta+gamma*(1+.34*wind2)))
def power_eto_daily(lat,lon,start,end,elevation_m=0,timeout=45):
    q={"parameters":"T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN","community":"AG","longitude":lon,"latitude":lat,"start":start.replace("-",""),"end":end.replace("-",""),"format":"JSON"}
    req=Request(POWER_URL+"?"+urlencode(q),headers={"User-Agent":"QGIS-Irrigation-Designer/1.2"})
    with urlopen(req,timeout=timeout) as r: data=json.loads(r.read().decode())
    P=data["properties"]["parameter"]; out=[]
    from datetime import datetime
    for k in sorted(P["T2M_MAX"]):
        vals=[P[x].get(k) for x in ["T2M_MAX","T2M_MIN","RH2M","WS2M","ALLSKY_SFC_SW_DWN"]]
        if any(v is None or float(v)<-900 for v in vals): continue
        out.append(_eto(lat,elevation_m,datetime.strptime(k,"%Y%m%d").timetuple().tm_yday,*map(float,vals)))
    if not out: raise ValueError("NASA POWER no devolvió días válidos para ETo.")
    return {"eto_mean":sum(out)/len(out),"n_days":len(out),"source":"NASA POWER + FAO-56 Penman-Monteith"}
