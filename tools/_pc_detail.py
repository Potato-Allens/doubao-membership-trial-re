# -*- coding: utf-8 -*-
import json, requests
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
line=open("pool/live_intake.jsonl",encoding="utf-8").read().strip().splitlines()[-1]
uid,cks=line.split("|",1)
ck={}
for p in cks.split(";"):
    if "=" in p:
        k,v=p.split("=",1); ck[k.strip()]=v.strip()
s=requests.Session(); s.cookies.update(ck)
for scope,tag in ((SCOPE,"web"),(S_WORK,"work")):
    j=s.post(BASE+"/alice/commerce/incentive/campaign/pc_new_user_page/detail/",params=scope,
             json={"campaign_id":"pc_new_user_campaign"},headers=H,timeout=25).json()
    print("== detail",tag,j.get("code"))
    print(json.dumps(j.get("data"),ensure_ascii=False,indent=1)[:2500])
    j2=s.post(BASE+"/alice/commerce/incentive/campaign/join/",params=scope,
              json={"campaign_id":"pc_new_user_campaign"},headers=H,timeout=25).json()
    print("== join",tag,j2.get("code"),json.dumps(j2,ensure_ascii=False)[:300])