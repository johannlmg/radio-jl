import json, re, urllib.request, urllib.parse, concurrent.futures as cf
UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15"}
def get(u,n=400000):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=15) as r: return r.read(n).decode("utf8","ignore")
    except Exception as e: return ""
def test(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=12) as r:
            ct=r.headers.get("Content-Type",""); d=r.read(8192)
            return r.status==200 and len(d)>2000 and any(x in ct for x in ("audio","ogg","aac","mpeg","octet")), ct, r.geturl()
    except Exception as e: return False,str(e)[:60],""
PAT=re.compile(r'''https?://[^\s"'<>\\]+?(?:\.mp3|\.aac|\.ogg|/stream|/live|;stream|:\d{4}/[^\s"'<>\\]*|ice[^\s"'<>\\]*infomaniak[^\s"'<>\\]*|streamakaci[^\s"'<>\\]*|creacast[^\s"'<>\\]*)[^\s"'<>\\]*''',re.I)
PAGES={
 "arverne":["http://fluxradios.blogspot.com/2014/07/flux-url-radio-arverne.html","https://www.radio-en-ligne.fr/radio-arverne","https://radioenlignefrance.com/arverne","https://radiofrench.fr/ecouter/radio-arverne.html","https://www.tunedradios.com/fr/radio/radio-arverne-fr","https://ecouterradioenligne.com/arverne-gerzat/","https://www.radioarverne.fr/","https://radioarverne.fr/"],
 "variance":["http://fluxradios.blogspot.com/2018/01/flux-url-variance-fm-france.html","https://variancefm.com/ecouter-en-ligne/","https://variancefm.com/","https://www.radio.fr/s/variancefm"],
 "rcf63":["https://radiomap.eu/fr/play/rcf63","http://fluxradios.blogspot.com/2014/06/flux-url-rcf-puy-de-dome.html","https://www.radio-en-ligne.fr/rcf-puy-de-dome","https://radiome.fr/rcfpuydedome"],
 "rva":["http://fluxradios.blogspot.com/2023/01/flux-url-radio-rva-puy-de-dome-france.html"],
 "altitude":[],"onde":[],"logos":[],"esperance":["https://www.radio-esperance.fr/"],"campus":["https://campus-clermont.net/"],"fusion":[]
}
NAMES={"arverne":["Arverne"],"variance":["Variance"],"rcf63":["RCF Puy","RCF 63","RCF Clermont"],"rva":["RVA"],"altitude":["Altitude"],"onde":["Onde Porteuse"],"logos":["Logos"],"esperance":["Radio Esperance","Radio Espérance"]}
# radiomap Clermont page: discover play pages
idx=get("https://radiomap.eu/fr/clermont-ferrand")
plays=sorted(set(re.findall(r'/fr/play/[a-z0-9\-_]+',idx)))
out={"radiomap_plays":plays,"stations":{}}
def scan(item):
    k,pages=item; found={}
    for p in pages:
        for u in PAT.findall(get(p)): found.setdefault(u.rstrip(').,;'),p)
    for nm in NAMES.get(k,[]):
        for h in ["de1","de2","fi1"]:
            t=get(f"https://{h}.api.radio-browser.info/json/stations/search?"+urllib.parse.urlencode({"name":nm,"limit":"15"}))
            if t:
                for r in json.loads(t): found.setdefault(r.get("url_resolved") or r.get("url"),"rb:"+r["name"]+"|"+(r.get("state") or "")+"|"+r.get("countrycode",""))
                break
    res=[]
    for u,src in list(found.items())[:40]:
        ok,ct,fin=test(u.replace("http://","https://"))
        res.append({"url":u,"src":src,"ok":ok,"ct":ct,"final":fin})
    return k,res
with cf.ThreadPoolExecutor(6) as ex:
    for k,v in ex.map(scan,PAGES.items()): out["stations"][k]=v
# radiomap play pages for Clermont
rm={}
for p in plays[:60]:
    h=get("https://radiomap.eu"+p)
    us=list(dict.fromkeys(PAT.findall(h)))[:5]
    rm[p]=[{"url":u,**dict(zip(("ok","ct","final"),test(u.replace("http://","https://"))))} for u in us]
out["radiomap"]=rm
json.dump(out,open("tools/locals.json","w"),indent=1,ensure_ascii=False)
