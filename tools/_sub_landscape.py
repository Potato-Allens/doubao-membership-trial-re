# -*- coding: utf-8 -*-
"""Map subscription landscape across alive pool: who has the free exp_work month vs nobody."""
import json, time, random, collections
import concurrent.futures as cf
import requests
BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
scan={r["idx"]:r for r in json.load(open("scan_rotate.json",encoding="utf-8"))}
alive=[i for i,r in scan.items() if r.get("code")==0]
def ckof(a):
    d={}
    for p in a["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
def one(i):
    a=raw[i]; s=requests.Session(); s.cookies.update(ckof(a))
    def post(ep,body):
        for _ in range(3):
            try:
                j=s.post(BASE+ep,params=SCOPE,json=body,headers=H,timeout=25).json()
                if j.get("code")==611060900:
                    time.sleep(1.2+random.random()); continue
                return j
            except Exception:
                time.sleep(1.0)
        return {"code":-1}
    st=post("/alice/commerce/sale/subscription/status/",{})
    d=st.get("data") or {}
    out={"idx":i,"sub":d.get("has_subscribed"),"is_sub":d.get("is_subscribing"),"sku":None,
         "price":None,"start":None,"end":None,"status":None}
    if d.get("has_subscribed") or d.get("is_subscribing"):
        ov=post("/alice/commerce/sale/subscription/overview/",{"product_line":"membership"})
        cs=((ov.get("data") or {}).get("current_subscription") or {})
        out.update(sku=cs.get("sku_key"),price=cs.get("agreement_price"),
                   start=cs.get("start_time"),end=cs.get("end_time"),status=cs.get("status"))
    out["disc"]=(scan[i].get("disc") or 0)
    return out
rows=[]
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    for n,r in enumerate(ex.map(one,alive),1):
        rows.append(r)
        if n%30==0: print("  %d/%d"%(n,len(alive)),flush=True)
json.dump(rows,open("sub_landscape.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("alive",len(rows))
print("subscribed:",sum(1 for r in rows if r["sub"] or r["is_sub"]))
print("sku dist:",collections.Counter(r["sku"] for r in rows))
print("price dist:",collections.Counter(r["price"] for r in rows))
print("disc by sub:",collections.Counter((bool(r["sub"]),r["disc"]) for r in rows))