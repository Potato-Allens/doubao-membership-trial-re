# -*- coding: utf-8 -*-
"""Does the intro price depend on purchase_channel (web/IAP/app-store)? estimate with total_price=100."""
import json, time, requests
BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
S_WORK=dict(SCOPE,aid="582478",real_aid="582478",pc_version="2.33.3",doubao_pc_version="2.33.3",channel="win")
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
def est(s,scope,total,ch,extra=None,pipo=None,elig=True):
    body={"sku_key":SKU,"card_id":CARD,"purchase_channel":ch,"support_diff_price":True,
          "timezone":-480,"total_price":str(total),
          "trade_extra":json.dumps(extra or {},separators=(",",":")),
          "is_eligible_for_intro_offer":elig}
    if pipo: body["pipo_params"]=pipo
    j=s.post(BASE+"/alice/commerce/sale/trade/estimate/",params=scope,json=body,headers=H,timeout=25).json()
    return {"code":j.get("code"),"msg":str(j.get("message") or j.get("msg"))[:26],
            "amt":(j.get("data") or {}).get("pay_amount")}
for idx in (4,0):
    s=sess(idx); print("="*20,"idx",idx)
    for ch in (1,2,3,4,5):
        print("  ch=%d total=100 -> %s"%(ch, json.dumps(est(s,SCOPE,100,ch),ensure_ascii=False)))
        time.sleep(0.7)
    print("  pipo/iap ch=3 ->", json.dumps(est(s,SCOPE,100,3,pipo={"channel":"doubao_android","platform":"android"},elig=False),ensure_ascii=False))
    print("  work-scope ch=3 ->", json.dumps(est(s,S_WORK,100,3),ensure_ascii=False))