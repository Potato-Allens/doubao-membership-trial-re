# -*- coding: utf-8 -*-
"""Compare promo/entitlement endpoints: eligible account vs ineligible account."""
import json, requests
BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web","aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription","origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def parse(s):
    d={}
    for p in s.split(";"):
        if "=" in p: k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
ckmap={str(a.get("uid")):parse(a["cookie_string"]) for a in raw}
HIT="0000000000000001"; MISS="256647730305060"
EPS=["/alice/commerce/sale/campaign/trial/init/",
     "/alice/commerce/sale/campaign/fixed_subscription/claim/",
     "/alice/commerce/sale/student/entitlement/receive/",
     "/alice/commerce/sale/student/verify_info/",
     "/alice/commerce/intake/entitlement/query",
     "/alice/commerce/incentive/campaign/subscription/query/",
     "/alice/commerce/marketing/subscribe/init/",
     "/alice/commerce/sale/trade/beta/check/",
     "/alice/ug/campaign/item/reward/claim/",
     "/alice/commerce/sale/subscription/status/"]
for uid,tag in ((HIT,"HIT"),(MISS,"MISS")):
    s=requests.Session(); s.cookies.update(ckmap[uid])
    print("=== %s %s" % (tag,uid))
    for ep in EPS:
        try:
            j=s.post(BASE+ep,params=SCOPE,json={},headers=H,timeout=20).json()
            d=j.get("data")
            print("  %-56s code=%-10s data=%s" % (ep.split("/alice")[-1][:56], j.get("code"), json.dumps(d,ensure_ascii=False)[:110]))
        except Exception as e:
            print("  %-56s ERR %s" % (ep[:56], str(e)[:50]))
