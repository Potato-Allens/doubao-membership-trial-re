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
for idx in (163,171,193,202,204,130):
    s=sess(idx)
    j=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,
             json={"scene_key":"default_member_link","purchase_channel":2},headers=H,timeout=25).json()
    d=j.get("data") or {}
    std=[]
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("card_id","").startswith("doubao_personal_std"):
                std.append((c["card_id"],c.get("button_text"),c.get("discount_amount"),
                            (c.get("trial_info") or {}).get("trial_stage"),c.get("label")))
    st=s.post(BASE+"/alice/commerce/sale/subscription/status/",params=SCOPE,json={},headers=H,timeout=25).json()
    print("idx %-4d hist=%s claim=%s status=%s"%(idx,d.get("has_history_paid_subscription"),
          d.get("entitlement_claim_status"),json.dumps(st.get("data"),ensure_ascii=False)[:90]))
    for x in std: print("     ",x)