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
for idx in (57,0,120):
    s=sess(idx)
    r=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,
             json={"scene_key":"default_member_link"},headers=H,timeout=25)
    j=r.json(); d=j.get("data") or {}
    print("idx",idx,"sub_type",d.get("sub_type"),"page_display_type",d.get("page_display_type"),
          "claim",d.get("entitlement_claim_status"),"hist",d.get("has_history_paid_subscription"),
          "activities",json.dumps(d.get("activities"),ensure_ascii=False))
    print("   resp headers:", {k:v for k,v in r.headers.items() if k.lower() in
          ("set-cookie","x-tt-logid","x-tt-trace-id","server-timing","x-tt-abtest","x-tt-ab")})
    for c in r.cookies:
        print("   set-cookie:",c.name,"=",c.value[:60])