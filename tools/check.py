import json, urllib.request, urllib.parse, concurrent.futures as cf, time
UA={"User-Agent":"RadioJL-check/1.0"}
def test(url):
    try:
        req=urllib.request.Request(url,headers=UA)
        with urllib.request.urlopen(req,timeout=12) as r:
            ct=r.headers.get("Content-Type","")
            data=r.read(8192)
            ok=r.status==200 and len(data)>2000 and ("audio" in ct or "ogg" in ct or "aac" in ct or "mpeg" in ct or "octet" in ct)
            return {"ok":ok,"status":r.status,"ct":ct,"final":r.geturl(),"https":r.geturl().startswith("https")}
    except Exception as e:
        return {"ok":False,"err":str(e)[:120]}
def rb(q):
    for h in ["de1","de2","fi1","nl1","at1"]:
        try:
            u=f"https://{h}.api.radio-browser.info/json/stations/search?"+urllib.parse.urlencode({"name":q,"countrycode":"FR","hidebroken":"true","order":"votes","reverse":"true","limit":"12"})
            with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=15) as r: return json.load(r)
        except Exception: continue
    return []
st=json.load(open("tools/stations.json"))
out={}
def run(s):
    res={"n":s["n"],"known":[], "alts":[]}
    for u in s["urls"]:
        u=u.replace("http://","https://"); res["known"].append({"url":u,**test(u)})
    for r in rb(s["q"])[:12]:
        u=r.get("url_resolved") or r.get("url")
        if not u: continue
        t=test(u.replace("http://","https://"))
        res["alts"].append({"name":r["name"],"state":r.get("state"),"votes":r.get("votes"),"url":u.replace("http://","https://"),**t})
    return s["id"],res
with cf.ThreadPoolExecutor(8) as ex:
    for k,v in ex.map(run,st): out[k]=v
json.dump(out,open("tools/results.json","w"),indent=1,ensure_ascii=False)
