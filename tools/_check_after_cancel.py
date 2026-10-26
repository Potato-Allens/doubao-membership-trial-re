# -*- coding: utf-8 -*-
import json, time, requests
BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
       "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
       "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
       "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def pck(s):
    d={}
    for p in s.split(";"):
        if "=" in p: k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
ck=[pck(a["cookie_string"]) for a in raw if str(a.get("uid"))=="0000000000000001"][0]
s=requests.Session(); s.cookies.update(ck)
def post(ep,body=None):
    try: return s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=20).json()
    except Exception as e: return {"code":-1,"message":str(e)[:80]}
now=time.time()
ov=post("/alice/commerce/sale/subscription/overview/")
cs=(ov.get("data") or {}).get("current_subscription") or {}
print("=== 取消后状态 ===")
print(json.dumps(cs,ensure_ascii=False)[:1200])
for k in ("start_time","end_time","next_deduct_time","agreement_status","agreement_price","status"):
    v=cs.get(k)
    if isinstance(v,(int,float)) and v>1e12:
        print("  %-18s %s  (+%.3f d)"%(k,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(v/1000)),(v/1000-now)/86400))
    else: print("  %-18s %s"%(k,v))
print("trial",cs.get("trial_info"))
st=post("/alice/commerce/sale/subscription/status/")
print("status",json.dumps(st.get("data") or {},ensure_ascii=False))
json.dump({"ov":ov,"st":st},open("_after_cancel.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
