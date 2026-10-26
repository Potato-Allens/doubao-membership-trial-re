# -*- coding: utf-8 -*-
import json, time, requests
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
ck=[parse(a["cookie_string"]) for a in raw if str(a.get("uid"))=="0000000000000001"][0]
s=requests.Session(); s.cookies.update(ck)
ini=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,json={"scene_key":"default_member_link"},headers=H,timeout=20).json()
extra="{}"
for sku in (ini.get("data") or {}).get("sku_list") or []:
    for c in sku.get("purchase_card_list") or []:
        if c.get("card_id")=="doubao_personal_std_auto_renew_month" and c.get("discount_amount"):
            extra=c.get("trade_extra") or "{}"
body={"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
      "estimated_pay_amount":"100","purchase_channel":2,"upgrade_mode":0,
      "is_gift_deferred":False,"start_time":int(time.time()*1000),
      "trade_extra":extra,"is_eligible_for_intro_offer":True}
j=s.post(BASE+"/alice/commerce/sale/trade/create/",params=SCOPE,json=body,headers=H,timeout=25).json()
d=j.get("data") or {}
cred=d.get("payment_credential") or {}
print("order",d.get("order_id"),"sub",d.get("subscription_id"))
print("credential keys:",list(cred.keys()))
print(json.dumps(cred,ensure_ascii=False,indent=1)[:2500])
json.dump({"order_id":d.get("order_id"),"subscription_id":d.get("subscription_id"),
           "credential":cred,"created":time.strftime("%Y-%m-%d %H:%M:%S")},
          open("_order_full.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
