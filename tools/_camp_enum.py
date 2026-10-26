# -*- coding: utf-8 -*-
import json, requests, time
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
def ck(i):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
print("=== page_status enum ===")
for i in (163,47,53,120,4):
    s=requests.Session(); s.cookies.update(ck(i))
    j=s.post(BASE+"/alice/commerce/incentive/campaign/pc_new_user_page/detail/",params=SCOPE,
             json={"campaign_id":"pc_new_user_campaign"},headers=H,timeout=25).json()
    d=j.get("data") or {}
    print("  idx%-4s code=%s page_status=%s toast=%s"%(i,j.get("code"),d.get("page_status"),
          (d.get("dynamic_state") or {}).get("toast")))
    time.sleep(0.4)

print("=== campaign/trial/init with campaign_id fuzz ===")
s=requests.Session(); s.cookies.update(ck(4))
cands=["","std_trial","trial","trial_7d","7d_trial","first_purchase_trial","new_user_trial",
       "doubao_trial","member_trial","intro_offer","intro_offer_trial","std_trial_7d",
       "pc_trial","app_trial","trial_campaign","doubao_personal_std_trial"]
for c in cands:
    body={"campaign_id":c} if c else {}
    j=s.post(BASE+"/alice/commerce/sale/campaign/trial/init/",params=SCOPE,json=body,headers=H,timeout=25).json()
    if j.get("code")!=710010702:
        print("  %-24r -> %s %s"%(c,j.get("code"),json.dumps(j.get("data"),ensure_ascii=False)[:200]))
    time.sleep(0.4)
print("  (only non-710010702 shown)")