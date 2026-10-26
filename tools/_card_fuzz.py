# -*- coding: utf-8 -*-
import json, requests, itertools
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
def est(s,sku,card,total=100,extra=None):
    body={"sku_key":sku,"card_id":card,"purchase_channel":2,"support_diff_price":True,
          "timezone":-480,"total_price":str(total),"trade_extra":json.dumps(extra or {},separators=(",",":")),
          "is_eligible_for_intro_offer":True}
    j=s.post(BASE+"/alice/commerce/sale/trade/estimate/",params=SCOPE,json=body,headers=H,timeout=25).json()
    d=j.get("data") or {}
    return {"code":j.get("code"),"msg":str(j.get("message") or j.get("msg") or "")[:40],
            "pay":d.get("pay_amount") or d.get("estimated_pay_amount"),
            "price":json.dumps(d.get("price_info"),ensure_ascii=False)[:160] if d.get("price_info") else None,
            "keys":sorted(d.keys())[:12]}
s=sess(0)
print("=== base ===")
print(json.dumps(est(s,"doubao_personal_std","doubao_personal_std_auto_renew_month"),ensure_ascii=False))
cards=["doubao_personal_std_auto_renew_month","doubao_personal_std_trial_month","doubao_personal_std_trial",
 "doubao_personal_std_intro_month","doubao_personal_std_first_month","doubao_personal_std_1yuan",
 "doubao_personal_std_new_user_month","doubao_personal_std_auto_renew_month_trial",
 "doubao_personal_std_auto_renew_week","doubao_personal_std_auto_renew_trial_month",
 "doubao_personal_std_trial_week","doubao_personal_std_intro_week"]
skus=["doubao_personal_std","doubao_personal_std_trial","doubao_personal_std_intro","doubao_personal_trial"]
print("=== card/sku fuzz ===")
for sku in skus:
    for c in cards:
        r=est(s,sku,c)
        if r["code"]!=611060114:
            print("  %-26s %-42s code=%s pay=%s"%(sku,c,r["code"],r["pay"]))