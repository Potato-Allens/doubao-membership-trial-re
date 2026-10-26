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
for idx in (130,202):
    s=sess(idx)
    j=s.post(BASE+"/alice/commerce/sale/order/list/",params=SCOPE,json={"product_lines":["membership"]},headers=H,timeout=25).json()
    items=((j.get("data") or {}).get("items") or [])
    print("idx",idx,"orders",len(items))
    for o in items[:4]:
        print("   ",{k:o.get(k) for k in ("order_id","display_name","actual_pay_amount","paid_at_ms","status_view","order_status","create_time_ms","expire_time_ms")})