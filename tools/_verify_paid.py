# -*- coding: utf-8 -*-
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
print("=== OVERVIEW ===")
print(json.dumps(ov,ensure_ascii=False)[:1800])
cs=(ov.get("data") or {}).get("current_subscription") or {}
for k in ("end_time","next_deduct_time","effective_time","agreement_price","agreement_status","sku_key","card_id"):
    v=cs.get(k)
    if isinstance(v,(int,float)) and v>1e12:
        print("  %-20s %s  (%s)  +%.3f 天" % (k, v, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(v/1000)),
              (v/1000-now)/86400))
    else:
        print("  %-20s %s" % (k, v))
print()
print("=== STATUS ===")
st=post("/alice/commerce/sale/subscription/status/")
print(json.dumps(st,ensure_ascii=False)[:800])
print()
print("=== ORDER LIST ===")
ol=post("/alice/commerce/sale/order/list/")
print(json.dumps(ol,ensure_ascii=False)[:1500])
print()
print("=== ESTIMATE (intro offer still?) ===")
es=post("/alice/commerce/sale/trade/estimate/",
        {"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
         "purchase_channel":2,"support_diff_price":True,"timezone":-480,
         "total_price":100,"trade_extra":"{}","is_eligible_for_intro_offer":True})
print(json.dumps(es,ensure_ascii=False)[:1200])
print()
print("=== STACK TEST: direct create ===")
body={"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
      "estimated_pay_amount":"100","purchase_channel":2,"upgrade_mode":0,
      "is_gift_deferred":False,"start_time":int(now*1000),
      "trade_extra":json.dumps({"selected_eligibility_id":0000000000000003},separators=(",",":")),
      "is_eligible_for_intro_offer":True}
cr=post("/alice/commerce/sale/trade/create/",body)
print("create code",cr.get("code"),"msg",cr.get("message"))
print(json.dumps(cr,ensure_ascii=False)[:700])
json.dump({"ov":ov,"st":st,"ol":ol,"es":es,"cr":cr},open("_verify_paid.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
