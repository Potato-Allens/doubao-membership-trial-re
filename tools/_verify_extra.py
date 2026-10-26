# -*- coding: utf-8 -*-
import json, time, requests
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
def pck(s):
    d={}
    for p in s.split(";"):
        if "=" in p: k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
ck=[pck(a["cookie_string"]) for a in raw if str(a.get("uid"))=="0000000000000001"][0]
s=requests.Session(); s.cookies.update(ck)
def post(ep,body=None):
    try: return s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=20).json()
    except Exception as e: return {"code":-1,"message":str(e)[:80]}
print("=== 其它档位是否还有首购优惠 ===")
for card,full in (("doubao_personal_plus_auto_renew_month",6800),("doubao_personal_pro_auto_renew_month",6800),
                  ("doubao_personal_std_fixed_month",6800)):
    r=post("/alice/commerce/sale/trade/estimate/",
      {"sku_key":card.rsplit("_",1)[0].replace("_auto_renew","").replace("_fixed","") if False else "doubao_personal_std",
       "card_id":card,"purchase_channel":2,"support_diff_price":True,"timezone":-480,
       "total_price":full,"trade_extra":"{}","is_eligible_for_intro_offer":True})
    d=r.get("data") or {}; pi=d.get("price_info") or {}
    print("%-38s code=%-9s pay=%s"%(card,r.get("code"),pi.get("pay_amount")))
print()
print("=== 未付的 68 元单能否撤 ===")
for ep in ("/alice/commerce/sale/order/cancel/","/alice/commerce/sale/trade/cancel/"):
    r=post(ep,{"order_id":"0000000000000013","trade_no":"2001002610260703724304409027"})
    print(ep,"->",r.get("code"),str(r.get("message"))[:60])
