# -*- coding: utf-8 -*-
"""Slow, retry-aware rescan: does the 1-CNY bucket rotate? (rate-limit aware)"""
import json, time, random, collections
import concurrent.futures as cf
import requests
BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
CARD="doubao_personal_std_auto_renew_month"
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def ckof(a):
    d={}
    for p in a["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
def one(i):
    a=raw[i]; s=requests.Session(); s.cookies.update(ckof(a))
    last=None
    for attempt in range(4):
        try:
            r=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,
                     json={"scene_key":"default_member_link","purchase_channel":2},headers=H,timeout=25)
            j=r.json()
        except Exception as e:
            last={"code":-1,"err":str(e)[:50]}; time.sleep(1.5); continue
        code=j.get("code")
        if code==611060900:
            time.sleep(1.2+random.random()); last={"code":code}; continue
        d=j.get("data") or {}
        out={"idx":i,"uid":a.get("uid"),"code":code,
             "claim":d.get("entitlement_claim_status"),"hist":d.get("has_history_paid_subscription"),
             "disc":0,"trial":None,"btn":None,"extra":None}
        for sku in d.get("sku_list") or []:
            for c in sku.get("purchase_card_list") or []:
                if c.get("card_id")==CARD:
                    out.update(disc=c.get("discount_amount") or 0,trial=c.get("trial_info"),
                               btn=c.get("button_text"),extra=c.get("trade_extra"))
        out["hit1"]=out["disc"]==6700 or ((out["trial"] or {}).get("trial_stage")==1 and out["disc"]>0)
        return out
    return {"idx":i,"uid":a.get("uid"),"code":(last or {}).get("code"),"hit1":False,"note":"exhausted"}
t0=time.time(); rows=[]
with cf.ThreadPoolExecutor(max_workers=3) as ex:
    for n,r in enumerate(ex.map(one,range(len(raw))),1):
        rows.append(r)
        if r.get("hit1"): print("HIT idx=%s uid=%s disc=%s"%(r["idx"],r["uid"],r["disc"]),flush=True)
        if n%25==0: print("  %d/%d  %.0fs"%(n,len(raw),time.time()-t0),flush=True)
json.dump(rows,open("scan_rotate.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
alive=[r for r in rows if r.get("code")==0]
print("alive",len(alive),"hits",sum(1 for r in rows if r.get("hit1")))
print("trial_stage",collections.Counter(((r.get("trial") or {}).get("trial_stage")) for r in alive))
print("codes",collections.Counter(r.get("code") for r in rows))