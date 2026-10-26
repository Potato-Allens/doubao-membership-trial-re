# -*- coding: utf-8 -*-
"""Live payment monitor: watch subscription state / order list / intro-offer availability."""
import json, os, sys, time, requests

BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
       "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
       "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
       "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
UID="0000000000000001"
LOG=os.path.join(os.path.dirname(os.path.abspath(__file__)),"_monitor_pay.log")
STATE=os.path.join(os.path.dirname(os.path.abspath(__file__)),"_monitor_state.json")

def log(m):
    line="[%s] %s" % (time.strftime("%H:%M:%S"), m)
    if sys.stdout is not None:
        print(line, flush=True)
    with open(LOG,"a",encoding="utf-8") as f: f.write(line+"\n")

def ck_of(uid):
    raw=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "pool","trial_batch_212.json"),encoding="utf-8"))["accounts"]
    for a in raw:
        if str(a.get("uid"))==uid:
            d={}
            for p in a["cookie_string"].split(";"):
                if "=" in p:
                    k,v=p.split("=",1); d[k.strip()]=v.strip()
            return d
    return None

def post(s,ep,body=None):
    try:
        j=s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},
                 headers=H,timeout=15).json()
        return j
    except Exception as e:
        return {"code":-1,"message":str(e)[:60]}

def main():
    minutes=int(sys.argv[1]) if len(sys.argv)>1 else 45
    ck=ck_of(UID)
    if not ck:
        log("no cookie for uid"); return 2
    s=requests.Session(); s.cookies.update(ck)
    log("monitor start uid=%s for %d min" % (UID,minutes))
    last={}
    end=time.time()+minutes*60
    while time.time()<end:
        snap={}
        ov=post(s,"/alice/commerce/sale/subscription/overview/")
        cs=((ov.get("data") or {}).get("current_subscription") or {})
        snap["ov_code"]=ov.get("code")
        snap["has"]=cs.get("has_switched")
        snap["sku"]=cs.get("sku_key")
        snap["eff"]=cs.get("effective_time")
        snap["end"]=cs.get("end_time")
        snap["next_deduct"]=cs.get("next_deduct_time")
        snap["price"]=cs.get("agreement_price")
        snap["status"]=cs.get("agreement_status")
        st=post(s,"/alice/commerce/sale/subscription/status/")
        snap["st"]=json.dumps(st.get("data") or {},ensure_ascii=False)[:160]
        ol=post(s,"/alice/commerce/sale/order/list/")
        orders=(ol.get("data") or {}).get("order_list") or (ol.get("data") or {}).get("orders") or []
        snap["orders"]=[{"id":o.get("order_id"),"status":o.get("order_status"),
                         "amount":o.get("pay_amount") or o.get("total_amount"),
                         "ct":o.get("create_time")} for o in orders[:5]]
        es=post(s,"/alice/commerce/sale/trade/estimate/",
                {"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
                 "purchase_channel":2,"support_diff_price":True,"timezone":-480,
                 "total_price":100,"trade_extra":"{}","is_eligible_for_intro_offer":True})
        pi=((es.get("data") or {}).get("price_info") or {})
        pinf=((es.get("data") or {}).get("purchase_info") or {})
        snap["est"]={"code":es.get("code"),"pay":pi.get("pay_amount"),
                     "start":pinf.get("start_time"),"end":pinf.get("end_time")}
        sig=(snap["ov_code"],snap["has"],snap["end"],snap["next_deduct"],
             snap["status"],snap["st"],json.dumps(snap["orders"]),snap["est"]["pay"],snap["est"]["code"])
        if sig!=last:
            log("CHANGE " + json.dumps(snap,ensure_ascii=False))
            json.dump(snap,open(STATE,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
            last=sig
        elif sys.stdout is not None:
            sys.stdout.write("."); sys.stdout.flush()
        time.sleep(5)
    log("monitor end")
    return 0

if __name__=="__main__":
    sys.exit(main())
