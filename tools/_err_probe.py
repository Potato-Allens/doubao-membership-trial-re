# -*- coding: utf-8 -*-
import json, requests
BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
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
s=sess(0)
j=s.post(BASE+"/alice/commerce/sale/common/error_display_config/",params=SCOPE,json={},headers=H,timeout=25).json()
mp=(j.get("data") or {}).get("error_code_mapping") or {}
print("codes",len(mp))
for k in sorted(mp):
    if k.startswith(("6110601","611080","7100107","611070","6110609")):
        print(" ",k,json.dumps(mp[k],ensure_ascii=False)[:180])
print()
for ep,body in (("/alice/commerce/sale/campaign/trial/init/",{}),
                ("/alice/commerce/sale/marketing/cta/resolve_fixed_cta",{"scene_key":"default_member_link","sku_key":"doubao_personal_std"}),
                ("/alice/commerce/marketing/resource/mget/v2/",{"resource_keys":["exit_retention"]})):
    r=s.post(BASE+ep,params=SCOPE,json=body,headers=H,timeout=25)
    print(ep,"->",r.status_code,r.text[:300])