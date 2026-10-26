# -*- coding: utf-8 -*-
"""Final: one order -> native alipays QR (fit-to-screen) + cashdesk QR."""
import base64, json, os, time, requests, qrcode
from urllib.parse import urlparse, parse_qs
BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web","aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription","origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
CH={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com","referer":"https://tp-pay.snssdk.com/","user-agent":UA}
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def pck(s):
    d={}
    for p in s.split(";"):
        if "=" in p: k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
ck=[pck(a["cookie_string"]) for a in raw if str(a.get("uid"))=="0000000000000001"][0]
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
pu=cred.get("pay_url") or ""; q=parse_qs(urlparse(pu).query)
papi=q["papi_id"][0]; tno=q["trade_no"][0]
exp=cred.get("order_expire_seconds") or 1799
dl=time.strftime("%H:%M:%S",time.localtime(time.time()+exp))
print("ORDER",d.get("order_id"),"TRADE",tno,"DEADLINE",dl)

def confirm(channel):
    bc={"trade_no":tno,"ptcode":"alipay",
        "ptcode_info":{"bank_card_id":"","business_scene":"",
          "return_url":"https://tp-pay.snssdk.com/cashdesk?cj_new_api=1&cj_source=alipay&cj_trade_no=%s&cj_process=%s&cj_remain_time=0&cj_result_extra=&cj_qrcode_env=qrcode"%(tno,base64.b64encode(papi.encode()).decode())},
        "support_evoke_channels":""}
    form={"biz_content":json.dumps(bc,separators=(",",":")),"channel_support_scene":channel,
          "process":papi,"scene":"h5","risk_info":'{"device_platform":"android"}',
          "trace_id":str(int(time.time()*1000))+os.urandom(4).hex(),
          "dev_info":'{"os":"Android","device_platform":"android","is_h5":true,"front_type":"h5"}'}
    r=requests.post("https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm",data=form,headers=CH,timeout=25)
    jj=r.json(); pp=(jj.get("data") or {}).get("pay_params") or {}
    try: inner=json.loads(pp.get("data") or "{}")
    except Exception: inner={}
    return pp.get("trade_type"), inner

tt,inner=confirm("ALI_APP")
osstr=inner.get("url") or ""
scheme="alipays://platformapi/startApp?appId=60000157&orderStr="+osstr
print("APP",tt,"len",len(scheme))
cash="https://tp-pay.snssdk.com/cashdesk?papi_id=%s&qrcode_env=qrcode&withhold_scene=sign_and_pay&trade_no=%s"%(papi,tno)
print("CASH len",len(cash))

arts={}
for tag,payload,bs,bd,ecc in [("qr_native_10",scheme,10,3,"L"),("qr_native_6",scheme,6,3,"L"),
                              ("qr_cashdesk",cash,10,4,"M")]:
    qq=qrcode.QRCode(error_correction=getattr(qrcode.constants,"ERROR_CORRECT_"+ecc),box_size=bs,border=bd)
    qq.add_data(payload); qq.make(fit=True); im=qq.make_image(); im.save(tag+".png")
    arts[tag]={"v":qq.version,"px":(qq.modules_count+2*bd)*bs,"len":len(payload)}
    print(tag,arts[tag])

import shutil
for t in arts: shutil.copy(t+".png", r"C:\Users\Administrator\AppData\Local\Temp\%s.png"%t)

html = """<!doctype html><html><head><meta charset=utf-8><title>1元试用 · 支付宝扫码</title>
<style>html,body{margin:0;height:100%%;background:#fff;font-family:Segoe UI,Microsoft YaHei}
.wrap{height:100%%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px}
img{image-rendering:pixelated;height:min(88vh,1200px);width:auto;max-width:96vw}
.h{font-size:15px;color:#111}.m{font-size:13px;color:#666;max-width:90vw;word-break:break-all;text-align:center}</style></head>
<body><div class="wrap">
<img src="qr_native_10.png">
<div class="h">支付宝「扫一扫」→ 直接进付款页 ¥1.00</div>
<div class="m">订单 %s ｜ 失效 %s ｜ <a href="qr_cashdesk.png" target=_blank>备用：字节收银台码</a></div>
</div></body></html>""" % (d.get("order_id"), dl)
open("alipay_qr2.html","w",encoding="utf-8").write(html)
shutil.copy("alipay_qr2.html", r"C:\Users\Administrator\AppData\Local\Temp\alipay_qr2.html")

json.dump({"order_id":d.get("order_id"),"trade_no":tno,"papi":papi,"cashdesk":cash,
           "scheme_len":len(scheme),"created":time.strftime("%Y-%m-%d %H:%M:%S"),"deadline":dl,
           "trade_type":tt,"qr":arts},open("_final_qr.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("SAVED", dl)
