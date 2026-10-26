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

print("=== 1) TRADE INIT（看当前卡片折扣）===")
ini=post("/alice/commerce/sale/trade/init/",{"scene_key":"default_member_link"})
print("code",ini.get("code"))
cards=[]
for sku in (ini.get("data") or {}).get("sku_list") or []:
    for c in sku.get("purchase_card_list") or []:
        cards.append({"card":c.get("card_id"),"btn":c.get("button_text"),
                      "disc":c.get("discount_amount"),"price":c.get("price"),
                      "trial":c.get("trial_info"),"extra":c.get("trade_extra")})
for c in cards: print("  ",json.dumps(c,ensure_ascii=False)[:300])
ex=(cards[0].get("extra") if cards else "{}") or "{}"

def est(tag, body):
    r=post("/alice/commerce/sale/trade/estimate/",body)
    d=r.get("data") or {}
    pi=d.get("price_info") or {}; pinf=d.get("purchase_info") or {}
    print("%-42s code=%-10s pay=%-6s disc=%-6s start=%s end=%s" % (tag,r.get("code"),
        pi.get("pay_amount"), pi.get("discount_amount") or pi.get("total_discount_amount"),
        pinf.get("start_time"), pinf.get("end_time")))
    return r

print()
print("=== 2) ESTIMATE 矩阵 ===")
base={"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
      "purchase_channel":2,"support_diff_price":True,"timezone":-480}
est("total=100 intro=True extra={}", dict(base,total_price=100,trade_extra="{}",is_eligible_for_intro_offer=True))
est("total=6800 intro=True extra={}", dict(base,total_price=6800,trade_extra="{}",is_eligible_for_intro_offer=True))
est("total=100 intro=True extra=init", dict(base,total_price=100,trade_extra=ex,is_eligible_for_intro_offer=True))
est("total=100 intro=False extra=init", dict(base,total_price=100,trade_extra=ex,is_eligible_for_intro_offer=False))
est("total=100 intro=True no-extra-key", dict(base,total_price=100,is_eligible_for_intro_offer=True))
print()
print("=== 3) CREATE 矩阵（叠加判定）===")
for tag,extra,amt in (("create total=100 extra=init",ex,"100"),("create total=6800 extra=init",ex,"6800")):
    body={"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
          "estimated_pay_amount":amt,"purchase_channel":2,"upgrade_mode":0,
          "is_gift_deferred":False,"start_time":int(time.time()*1000),
          "trade_extra":extra,"is_eligible_for_intro_offer":True}
    r=post("/alice/commerce/sale/trade/create/",body)
    d=r.get("data") or {}
    print("%-32s code=%-10s order=%s pay=%s" % (tag,r.get("code"),d.get("order_id"),
          (d.get("payment_credential") or {}).get("order_expire_seconds")))
    if r.get("code")!=0: print("   msg:",r.get("message"))
json.dump({"cards":cards,"ini":ini},open("_verify_stack.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
