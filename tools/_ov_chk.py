# -*- coding: utf-8 -*-
import json, requests, datetime
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
def ts(v):
    try: return datetime.datetime.fromtimestamp(int(v)/1000,datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
    except: return v
for idx in (163,202,204):
    s=sess(idx)
    j=s.post(BASE+"/alice/commerce/sale/subscription/overview/",params=SCOPE,json={"product_line":"membership"},headers=H,timeout=25).json()
    cs=((j.get("data") or {}).get("current_subscription") or {})
    print("idx",idx,"code",j.get("code"))
    for k in ("subscription_id","sku_key","start_time","end_time","next_deduct_time","agreement_status",
              "agreement_price","status","trial_info","source","create_time","channel"):
        if k in cs: print("   %-18s %s"%(k, ts(cs[k]) if "time" in k else json.dumps(cs[k],ensure_ascii=False)[:120]))