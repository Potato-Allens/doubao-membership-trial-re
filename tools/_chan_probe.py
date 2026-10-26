# -*- coding: utf-8 -*-
import json, requests
BASE="https://www.doubao.com"
UA_WEB=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
UA_CLI=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
S_WEB={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
S_WORK=dict(S_WEB,aid="582478",real_aid="582478",pc_version="2.33.3",doubao_pc_version="2.33.3",channel="win")
CARD="doubao_personal_std_auto_renew_month"
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def sess(i):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    s=requests.Session(); s.cookies.update(d); return s
def init(s,scope,ua,body):
    H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
       "origin":BASE,"user-agent":ua,"accept":"application/json, text/plain, */*"}
    r=s.post(BASE+"/alice/commerce/sale/trade/init/",params=scope,json=body,headers=H,timeout=25)
    j=r.json(); d=j.get("data") or {}
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("card_id")==CARD:
                return {"code":j.get("code"),"disc":c.get("discount_amount") or 0,
                        "btn":c.get("button_text"),"trial":c.get("trial_info"),"extra":c.get("trade_extra")}
    return {"code":j.get("code"),"msg":str(j.get("message") or j.get("msg") or "")[:40]}
for idx in (0,1,4):
    s=sess(idx); print("="*26,"idx",idx,raw[idx]["uid"])
    base={"scene_key":"default_member_link"}
    for ch in (1,2,3,4,5,100):
        r=init(s,S_WEB,UA_CLI,dict(base,purchase_channel=ch))
        print("  web-scope ch=%-4s %s disc=%s btn=%s"%(ch,r.get("code"),r.get("disc"),r.get("btn")))
    for ch in (1,2,3):
        r=init(s,S_WORK,UA_CLI,dict(base,purchase_channel=ch))
        print("  work-scope ch=%-3s %s disc=%s btn=%s"%(ch,r.get("code"),r.get("disc"),r.get("btn")))
    for fk in ("member","trial","intro","intro_offer","student","renewal","paywall","default","first_purchase",""):
        r=init(s,S_WEB,UA_CLI,dict(base,feature_key=fk))
        print("  feature_key=%-14r %s disc=%s btn=%s"%(fk,r.get("code"),r.get("disc"),r.get("btn")))
    for dk in ("doubao_personal_std","doubao_personal_plus","doubao_personal_pro"):
        r=init(s,S_WEB,UA_CLI,dict(base,default_sku_key=dk))
        print("  default_sku=%-20s %s disc=%s btn=%s"%(dk,r.get("code"),r.get("disc"),r.get("btn")))