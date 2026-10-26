# -*- coding: utf-8 -*-
"""Probe the pc_new_user_campaign: detail + join, before/after subscription state."""
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
def ck_from_str(s):
    d={}
    for p in s.split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
def post(s,ep,body):
    r=s.post(BASE+ep,params=SCOPE,json=body,headers=H,timeout=25)
    try: return r.json()
    except Exception: return {"code":-1,"raw":r.text[:120]}
targets=[]
# new account from qr login
try:
    line=open("pool/live_intake.jsonl",encoding="utf-8").read().strip().splitlines()[-1]
    uid,cks=line.split("|",1)
    targets.append(("qr:"+uid, ck_from_str(cks)))
except Exception as e:
    print("no live ck", e)
# dormant accounts
for i in (4,0):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    targets.append(("idx%d:%s"%(i,raw[i]["uid"]), d))
for tag,ck in targets:
    s=requests.Session(); s.cookies.update(ck)
    print("="*24,tag)
    st=post(s,"/alice/commerce/sale/subscription/status/",{}).get("data") or {}
    print("  before:",json.dumps(st,ensure_ascii=False))
    det=post(s,"/alice/commerce/incentive/campaign/pc_new_user_page/detail/",{"campaign_id":"pc_new_user_campaign"})
    print("  detail:",det.get("code"),json.dumps(det.get("data"),ensure_ascii=False)[:400])
    for body in ({"campaign_id":"pc_new_user_campaign"},{"campaign_id":"ug_free_subs_download_pc"}):
        j=post(s,"/alice/commerce/incentive/campaign/join/",body)
        print("  join %-28s -> %s %s"%(body["campaign_id"],j.get("code"),
              json.dumps(j.get("data"),ensure_ascii=False)[:200]))
        time.sleep(0.5)
    st2=post(s,"/alice/commerce/sale/subscription/status/",{}).get("data") or {}
    print("  after :",json.dumps(st2,ensure_ascii=False))