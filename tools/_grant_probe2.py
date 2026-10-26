# -*- coding: utf-8 -*-
"""Try every claim/grant surface on a no-sub account; report state change."""
import json, requests, time
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
        j=s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=25).json()
        return j
    except Exception as e:
        return {"code":-1,"message":str(e)[:60]}
IDX=4
s=sess(IDX)
st0=post(s,"/alice/commerce/sale/subscription/status/")
print("before:",json.dumps(st0.get("data"),ensure_ascii=False))
EPS=[("/alice/commerce/sale/campaign/fixed_subscription/claim/",{"AgwCommonParam":{}}),
     ("/alice/commerce/sale/campaign/trial/init/",{}),
     ("/alice/commerce/sale/campaign/page/query/",{}),
     ("/alice/commerce/incentive/campaign/join/",{}),
     ("/alice/commerce/incentive/campaign/pc_new_user_page/detail/",{}),
     ("/alice/commerce/sale/student/entitlement/receive/",{}),
     ("/alice/commerce/intake/entitlement/query",{}),
     ("/alice/commerce/marketing/gift/redeem/",{}),
     ("/alice/commerce/marketing/card/list/",{}),
     ("/alice/commerce/marketing/subscribe/init/",{}),
     ("/alice/commerce/sale/subscription/benefit_package/",{})]
for ep,body in EPS:
    j=post(s,ep,body)
    print("  %-58s code=%-9s data=%s"%(ep.split("/alice")[-1][:58],j.get("code"),
          json.dumps(j.get("data"),ensure_ascii=False)[:180]))
    time.sleep(0.6)
st1=post(s,"/alice/commerce/sale/subscription/status/")
print("after:",json.dumps(st1.get("data"),ensure_ascii=False))