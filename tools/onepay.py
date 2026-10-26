# -*- coding: utf-8 -*-
"""onepay.py -- 扫码上号后一条命令：抓客户端 CK -> 检测 1 元资格 -> 出支付二维码

用法:
  python onepay.py --client            # 从豆包客户端 CDP 9224 直接抓当前登录账号的 CK
  python onepay.py --ck "<cookie>"     # 手动给 cookie
  python onepay.py --pool pool.json --uid <uid>

行为:
  资格命中 (discount_amount == 6700) -> 建单 + 支付宝 H5 + 短链 + 两张二维码
  资格未命中 -> 只打印当前真实价格，绝不建单
"""
from __future__ import annotations
import argparse, base64, json, os, sys, time, urllib.parse
import requests, qrcode
from urllib.parse import urlparse, parse_qs

BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
       "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
       "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
       "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
CH={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com",
    "referer":"https://tp-pay.snssdk.com/","user-agent":UA}
SKU="doubao_personal_std"; CARD="doubao_personal_std_auto_renew_month"
OUT=os.path.dirname(os.path.abspath(__file__))

def kv(s):
    d={}
    for p in str(s).split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d

def ck_from_client(port=9224):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b=p.chromium.connect_over_cdp("http://127.0.0.1:%d"%port)
        ctx=b.contexts[0]
        pg=next((x for x in ctx.pages if "doubao" in x.url), ctx.pages[0])
        cdp=ctx.new_cdp_session(pg)
        allc=cdp.send("Network.getAllCookies").get("cookies") or []
    got={}
    for c in allc:
        if "doubao.com" in (c.get("domain") or ""):
            got[c["name"]]=c["value"]
    for need in ("sessionid","sid_tt","uid_tt","passport_csrf_token"):
        if not got.get(need):
            print("[warn] 客户端里没有 %s，可能未登录"%need)
    return got

def build_session(ckd):
    s=requests.Session(); s.cookies.update(ckd); return s

def check(s):
    j=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,json={"scene_key":"default_member_link"},headers=H,timeout=25).json()
    d=j.get("data") or {}
    best={"disc":0,"card":None,"btn":None,"trial":None,"extra":"{}","price":None}
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("card_id")!=CARD: continue
            best={"disc":c.get("discount_amount") or 0,"card":c.get("card_id"),
                  "btn":c.get("button_text"),"trial":c.get("trial_info"),
                  "extra":c.get("trade_extra") or "{}","price":c.get("price")}
    return {"code":j.get("code"),"msg":str(j.get("message") or "")[:60],
            "claim":d.get("entitlement_claim_status"),"hist":d.get("has_history_paid_subscription"),**best}

def mint(s, extra):
    body={"sku_key":SKU,"card_id":CARD,"estimated_pay_amount":"100","purchase_channel":2,
          "upgrade_mode":0,"is_gift_deferred":False,"start_time":int(time.time()*1000),
          "trade_extra":extra,"is_eligible_for_intro_offer":True}
    j=s.post(BASE+"/alice/commerce/sale/trade/create/",params=SCOPE,json=body,headers=H,timeout=30).json()
    d=j.get("data") or {}; cred=d.get("payment_credential") or {}
    return {"code":j.get("code"),"msg":str(j.get("message") or "")[:60],
            "order_id":d.get("order_id"),"subscription_id":d.get("subscription_id"),
            "pay_url":cred.get("pay_url") or "",
            "expire":cred.get("order_expire_seconds") or 1799}

def alipay(s, pay_url):
    q=parse_qs(urlparse(pay_url).query)
    papi=q["papi_id"][0]; tno=q["trade_no"][0]
    bc={"trade_no":tno,"ptcode":"alipay","ptcode_info":{"bank_card_id":"","business_scene":"",
        "return_url":"https://tp-pay.snssdk.com/cashdesk?cj_new_api=1&cj_source=alipay&cj_trade_no=%s&cj_process=%s&cj_remain_time=0&cj_result_extra=&cj_qrcode_env=qrcode"%(tno,base64.b64encode(papi.encode()).decode())},
        "support_evoke_channels":""}
    form={"biz_content":json.dumps(bc,separators=(",",":")),"channel_support_scene":"ALI_H5",
          "process":papi,"scene":"h5","risk_info":'{"device_platform":"android"}',
          "trace_id":str(int(time.time()*1000))+os.urandom(4).hex(),
          "dev_info":'{"os":"Android","device_platform":"android","is_h5":true,"front_type":"h5"}'}
    r=requests.post("https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm",data=form,headers=CH,timeout=30).json()
    pp=(r.get("data") or {}).get("pay_params") or {}
    h5=""
    try: h5=json.loads(pp.get("data") or "{}").get("url") or ""
    except Exception: pass
    cash="https://tp-pay.snssdk.com/cashdesk?papi_id=%s&qrcode_env=qrcode&withhold_scene=sign_and_pay&trade_no=%s"%(papi,tno)
    return {"trade_no":tno,"papi":papi,"h5":h5,"cashdesk":cash,"trade_type":pp.get("trade_type")}

def short(url):
    for svc in ("https://is.gd/create.php?format=simple&url=","https://tinyurl.com/api-create.php?url="):
        try:
            r=requests.get(svc+urllib.parse.quote(url,safe=""),timeout=20)
            if r.status_code==200 and r.text.strip().startswith("http"):
                return r.text.strip()
        except Exception: pass
    return ""

def make_qr(payload, path, bs=14, ecc="M"):
    q=qrcode.QRCode(error_correction=getattr(qrcode.constants,"ERROR_CORRECT_"+ecc),box_size=bs,border=4)
    q.add_data(payload); q.make(fit=True); q.make_image().save(path)
    return q.version

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--client",action="store_true")
    ap.add_argument("--port",type=int,default=9224)
    ap.add_argument("--ck",default="")
    ap.add_argument("--pool",default="")
    ap.add_argument("--uid",default="")
    a=ap.parse_args()
    ckd=None
    if a.ck: ckd=kv(a.ck); src="cli"
    elif a.client: ckd=ck_from_client(a.port); src="client:%d"%a.port
    elif a.pool:
        raw=json.load(open(a.pool,encoding="utf-8"))
        accs=raw.get("accounts") if isinstance(raw,dict) else raw
        for it in accs:
            if str(it.get("uid"))==str(a.uid):
                ckd=kv(it.get("cookie_string") or ""); src="pool:%s"%a.uid; break
    if not ckd or not ckd.get("sessionid"):
        print("no valid cookie"); return 2
    s=build_session(ckd)
    r=check(s)
    print("[1/3] 资格检测  src=%s"%src)
    print("      code=%s  disc=%s  price=%s  btn=%s"%(r["code"],r["disc"],r["price"],r["btn"]))
    print("      trial=%s"%json.dumps(r["trial"],ensure_ascii=False))
    print("      hist_paid=%s  claim=%s"%(r["hist"],r["claim"]))
    if r["code"]!=0:
        print("      -> init 失败，cookie 可能已失效（710012001 / 710010202 等）"); return 3
    if r["disc"]!=6700:
        print("      -> ✗ 无 1 元资格（disc=%s）。此 uid 只能按原价购买，不建单。"%r["disc"])
        return 4
    print("      -> ✓ 命中 ¥1 / 7 天")
    m=mint(s, r["extra"])
    print("[2/3] 建单  code=%s order=%s"%(m["code"],m["order_id"]))
    if m["code"]!=0 or not m["pay_url"]:
        print("      -> 建单失败: %s"%m["msg"]); return 5
    pay=alipay(s, m["pay_url"])
    print("[3/3] 支付宝  trade=%s type=%s h5_len=%d"%(pay["trade_no"],pay["trade_type"],len(pay["h5"])))
    sl=short(pay["h5"]) if pay["h5"] else ""
    deadline=time.strftime("%H:%M:%S",time.localtime(time.time()+m["expire"]))
    qa=os.path.join(OUT,"pay_qr_main.png"); qb=os.path.join(OUT,"pay_qr_backup.png")
    v1=make_qr(sl or pay["h5"], qa, 16, "M")
    v2=make_qr(pay["cashdesk"], qb, 14, "M")
    info={"order_id":m["order_id"],"subscription_id":m["subscription_id"],"trade_no":pay["trade_no"],
          "short":sl,"cashdesk":pay["cashdesk"],"deadline":deadline,
          "created":time.strftime("%Y-%m-%d %H:%M:%S"),
          "qr_main":qa,"qr_backup":qb,"qr_version":[v1,v2]}
    json.dump(info,open(os.path.join(OUT,"pay_last.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print()
    print("  ✅ 支付码已生成")
    print("  主码 v%d : %s   (%s)"%(v1,qa,sl))
    print("  备码 v%d : %s"%(v2,qb))
    print("  订单 %s   失效 %s"%(m["order_id"],deadline))
    return 0

if __name__=="__main__":
    sys.exit(main())
