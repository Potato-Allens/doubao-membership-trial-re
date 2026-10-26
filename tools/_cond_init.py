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
def post(s,ep,body=None):
    try:
        r=s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=25)
        return r.json()
    except Exception as e:
        return {"code":-1,"message":str(e)[:100]}

def summary(j):
    d=j.get("data") or {}
    out={"code":j.get("code"),"msg":str(j.get("message") or "")[:40],
         "activities":d.get("activities"),
         "claim":d.get("entitlement_claim_status"),
         "hist":d.get("has_history_paid_subscription"),
         "page_display_type":d.get("page_display_type"),
         "top_keys":sorted(d.keys()),
         "cards":[]}
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            out["cards"].append({k:c.get(k) for k in
              ("card_id","button_text","label","discount_amount","discount_total_price",
               "list_total_price","currency_code","period_type","subscription_type",
               "trade_extra","trial_info","display_only","action","card_sub_title")})
    return out

if __name__=="__main__":
    res={}
    for idx in (57,71,0,79,117,120,1,2):
        s=sess(idx)
        j=post(s,"/alice/commerce/sale/trade/init/",{"scene_key":"default_member_link"})
        res[str(idx)]=summary(j)
    print(json.dumps(res,ensure_ascii=False,indent=1))
    json.dump(res,open("_cond_init.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)