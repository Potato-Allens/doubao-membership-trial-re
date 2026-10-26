# -*- coding: utf-8 -*-
import json, requests
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
def sess(i):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    s=requests.Session(); s.cookies.update(d); return s
def post(s,ep,body=None):
    try:
        r=s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=25)
        return r.json()
    except Exception as e:
        return {"code":-1,"message":str(e)[:80]}
EPS=["/alice/commerce/marketing/subscribe/init/",
     "/alice/commerce/marketing/card/list/",
     "/alice/commerce/marketing/resource/mget/v2/",
     "/alice/commerce/incentive/campaign/subscription/query/",
     "/alice/commerce/marketing/qualification/query/",
     "/alice/commerce/marketing/subscribe/config/",
     "/alice/commerce/sale/subscription/entry/config/"]
out={}
for idx in (57,0,120):
    s=sess(idx); out[str(idx)]={}
    for ep in EPS:
        for body in ({}, {"product_line":"membership"}, {"scene_key":"default_member_link"}):
            j=post(s,ep,body)
            key=ep+" | "+json.dumps(body,ensure_ascii=False)
            out[str(idx)][key]={"code":j.get("code"),"msg":str(j.get("message") or "")[:50],"data":j.get("data")}
            break
json.dump(out,open("_mkt_probe.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
for idx,v in out.items():
    print("### idx",idx)
    for k,r in v.items():
        txt=json.dumps(r.get("data"),ensure_ascii=False)
        print("  %-56s %s %s"%(k.split(" | ")[0],r["code"],txt[:260]))