# -*- coding: utf-8 -*-
import json, sys, time, requests
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
def ckof(i):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
def sess(i):
    s=requests.Session(); s.cookies.update(ckof(i)); return s
def post(s,ep,body=None,timeout=25):
    try:
        r=s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=timeout)
        try: return r.json()
        except Exception: return {"code":-1,"message":r.text[:120]}
    except Exception as e:
        return {"code":-1,"message":str(e)[:100]}

if __name__=="__main__":
    for idx in (57,71,0,79):
        s=sess(idx)
        j=post(s,"/alice/commerce/sale/trade/init/",{"scene_key":"default_member_link"})
        print("="*70); print("idx",idx,"uid",raw[idx]["uid"],"code",j.get("code"))
        print(json.dumps(j,ensure_ascii=False,indent=1)[:6000])