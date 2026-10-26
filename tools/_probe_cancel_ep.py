# -*- coding: utf-8 -*-
import json, requests
BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
       "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
       "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
       "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def pck(s):
    d={}
    for p in s.split(";"):
        if "=" in p: k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
ck=[pck(a["cookie_string"]) for a in raw if str(a.get("uid"))=="0000000000000001"][0]
s=requests.Session(); s.cookies.update(ck)
def post(ep,body):
    r=s.post(BASE+ep,params=SCOPE,json=body,headers=H,timeout=20)
    try: return r.status_code, r.json()
    except Exception: return r.status_code, {"_raw":r.text[:200]}
print("=== 零副作用探针：假 subscription_id ===")
for sid in ("0","0000000000000000000"):
    sc,j=post("/alice/commerce/sale/subscription/cancel/",{"subscription_id":sid})
    print(" sid=%s http=%s code=%s msg=%s"%(sid,sc,j.get("code"),str(j.get("message"))[:80]))
print()
print("=== 空 body ===")
sc,j=post("/alice/commerce/sale/subscription/cancel/",{})
print(" http=%s code=%s msg=%s"%(sc,j.get("code"),str(j.get("message"))[:80]))
print()
print("=== 真实 id 只做 estimate 级检查（不调用）===")
ov=s.post(BASE+"/alice/commerce/sale/subscription/overview/",params=SCOPE,json={},headers=H,timeout=20).json()
cs=(ov.get("data") or {}).get("current_subscription") or {}
print(" subscription_id",cs.get("subscription_id"),"agreement_status",cs.get("agreement_status"),"status",cs.get("status"))
