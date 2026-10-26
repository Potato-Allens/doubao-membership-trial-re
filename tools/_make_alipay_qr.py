# -*- coding: utf-8 -*-
"""Mint a fresh 1-CNY order and materialise an Alipay QR (H5 scheme + app orderStr)."""
import base64, json, os, time, urllib.parse, requests, qrcode
from urllib.parse import urlparse, parse_qs

BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web","aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription","origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
OUT=os.path.dirname(os.path.abspath(__file__))
CH={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com",
    "referer":"https://tp-pay.snssdk.com/","user-agent":UA}

raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def parse(s):
    d={}
    for p in s.split(";"):
        if "=" in p: k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
ck=[parse(a["cookie_string"]) for a in raw if str(a.get("uid"))=="0000000000000001"][0]
s=requests.Session(); s.cookies.update(ck)
ini=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,json={"scene_key":"default_member_link"},headers=H,timeout=20).json()
extra="{}"
for sku in (ini.get("data") or {}).get("sku_list") or []:
    for c in sku.get("purchase_card_list") or []:
        if c.get("card_id")=="doubao_personal_std_auto_renew_month" and c.get("discount_amount"):
            extra=c.get("trade_extra") or "{}"
body={"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
      "estimated_pay_amount":"100","purchase_channel":2,"upgrade_mode":0,
      "is_gift_deferred":False,"start_time":int(time.time()*1000),
      "trade_extra":extra,"is_eligible_for_intro_offer":True}
j=s.post(BASE+"/alice/commerce/sale/trade/create/",params=SCOPE,json=body,headers=H,timeout=25).json()
d=j.get("data") or {}; cred=d.get("payment_credential") or {}
pay_url=cred.get("pay_url") or ""
q=parse_qs(urlparse(pay_url).query)
papi=q.get("papi_id",[""])[0]; trade_no=q.get("trade_no",[""])[0]
print("order", d.get("order_id"), "trade_no", trade_no)

def confirm(scene):
    bc={"trade_no":trade_no,"ptcode":"alipay",
        "ptcode_info":{"bank_card_id":"","business_scene":"",
          "return_url":("https://tp-pay.snssdk.com/cashdesk?cj_new_api=1&cj_source=alipay"
                        "&cj_trade_no=%s&cj_process=%s&cj_remain_time=0&cj_result_extra=&cj_qrcode_env=qrcode"
                        % (trade_no, base64.b64encode(papi.encode()).decode()))},
        "support_evoke_channels":""}
    form={"biz_content":json.dumps(bc,separators=(",",":")),
          "channel_support_scene":scene,"process":papi,"scene":"h5",
          "risk_info":'{"device_platform":"android"}',
          "trace_id":str(int(time.time()*1000))+os.urandom(4).hex(),
          "dev_info":'{"os":"Android","device_platform":"android","is_h5":true,"front_type":"h5"}'}
    r=requests.post("https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm",
                    data=form,headers=CH,timeout=25)
    try: return r.json()
    except Exception: return {"_raw":r.text[:300]}

h5=confirm("ALI_H5")
h5url=""
try:
    pp=h5.get("data",{}).get("pay_params") or {}
    inner=json.loads(pp.get("data") or "{}")
    h5url=inner.get("url") or ""
except Exception as e:
    print("h5 parse err",str(e)[:80])
print("H5 url len",len(h5url))

app=confirm("ALI_APP")
appdata=(app.get("data") or {}).get("pay_params") or {}
print("APP pay_params keys",list(appdata.keys()))
s_app=json.dumps(appdata,ensure_ascii=False)
orderStr=""
for key in ("orderStr","order_str","data"):
    v=appdata.get(key)
    if isinstance(v,str) and "alipay_root_cert_sn" in v:
        orderStr=v; break
    if isinstance(v,str) and v.startswith("{"):
        try:
            inner=json.loads(v)
            for k2 in ("orderStr","order_str"):
                if isinstance(inner.get(k2),str) and inner[k2]:
                    orderStr=inner[k2]; break
        except Exception: pass
if not orderStr:
    i=s_app.find("alipay_root_cert_sn")
    print("orderStr not found; sample:", s_app[:300])
print("orderStr len",len(orderStr))

alipays=""
if orderStr:
    alipays="alipays://platformapi/startapp?appId=60000157&orderStr="+urllib.parse.quote(orderStr,safe="")

def qr(text,name):
    if not text: return ""
    img=qrcode.make(text)
    img=img.resize((560,560))
    p=os.path.join(OUT,name)
    img.save(p)
    return p

p1=qr(h5url,"_qr_alipay_h5.png")
p2=qr(alipays,"_qr_alipay_app.png")
p3=qr(pay_url,"_qr_cashdesk.png")
info={"order_id":d.get("order_id"),"trade_no":trade_no,"papi_id":papi,
      "h5_url":h5url,"alipays":alipays,"cashdesk":pay_url,
      "created":time.strftime("%Y-%m-%d %H:%M:%S"),
      "deadline":time.strftime("%H:%M:%S", time.localtime(time.time()+(cred.get("order_expire_seconds") or 1800)))}
json.dump(info,open("_alipay_qr.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("QR files:",p1,p2,p3)
print("H5URL",h5url[:300])
print("DEADLINE",info["deadline"])
