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
CARD="doubao_personal_std_auto_renew_month"
def sess(i):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    s=requests.Session(); s.cookies.update(d); return s
def post(s,ep,body=None):
    try:
        r=s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=25)
        try: return r.json()
        except Exception: return {"code":-1,"message":r.text[:100]}
    except Exception as e:
        return {"code":-1,"message":str(e)[:80]}
def pick(j):
    d=j.get("data") or {}
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("card_id")==CARD:
                return {"code":j.get("code"),"msg":str(j.get("message") or "")[:30],
                        "disc":c.get("discount_amount") or 0,"dtp":c.get("discount_total_price"),
                        "btn":c.get("button_text"),"trial":c.get("trial_info"),"extra":c.get("trade_extra")}
    return {"code":j.get("code"),"msg":str(j.get("message") or "")[:60]}

CAMPAIGN=[("POST","/alice/commerce/sale/campaign/trial/init/",None),
          ("POST","/alice/commerce/sale/campaign/page/query/",None),
          ("POST","/alice/commerce/sale/marketing/cta/resolve_fixed_cta",{"scene_key":"default_member_link","sku_key":"doubao_personal_std"}),
          ("POST","/alice/commerce/sale/trade/beta/check/",{"activity_id":""}),
          ("POST","/alice/commerce/incentive/campaign/pc_new_user_page/detail/",None),
          ("POST","/alice/commerce/marketing/reward/renewal/status/",None)]
ACTS=["", "1", "trial", "intro_offer", "doubao_trial", "new_user", "first_purchase", "retention"]
for idx in (0,57,120):
    s=sess(idx); print("="*30,"idx",idx,"uid",raw[idx]["uid"])
    for m,ep,body in CAMPAIGN:
        j=post(s,ep,body)
        print("  %-52s %s %s"%(ep.split("/alice")[-1],j.get("code"),json.dumps(j.get("data"),ensure_ascii=False)[:300]))
    for a in ACTS:
        r=pick(post(s,"/alice/commerce/sale/trade/init/",
                    {"scene_key":"default_member_link","activity_id":a}))
        print("  init activity_id=%-14r -> %s disc=%s btn=%s trial=%s"%(
            a,r.get("code"),r.get("disc"),r.get("btn"),json.dumps(r.get("trial"),ensure_ascii=False)))