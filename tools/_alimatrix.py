# -*- coding: utf-8 -*-
import base64, json, os, time, urllib.parse, requests
from urllib.parse import urlparse, parse_qs
BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web","aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription","origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
CH={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com","referer":"https://tp-pay.snssdk.com/","user-agent":UA}
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
pu=cred.get("pay_url") or ""; q=parse_qs(urlparse(pu).query)
papi=q["papi_id"][0]; tno=q["trade_no"][0]
print("order",d.get("order_id"),"trade",tno)
def confirm(scene, ptcode, channel):
    bc={"trade_no":tno,"ptcode":ptcode,
        "ptcode_info":{"bank_card_id":"","business_scene":"",
          "return_url":"https://tp-pay.snssdk.com/cashdesk?cj_new_api=1&cj_source=%s&cj_trade_no=%s&cj_process=%s&cj_remain_time=0&cj_result_extra=&cj_qrcode_env=qrcode"%(ptcode,tno,base64.b64encode(papi.encode()).decode())},
        "support_evoke_channels":""}
    form={"biz_content":json.dumps(bc,separators=(",",":")),"channel_support_scene":channel,
          "process":papi,"scene":scene,"risk_info":'{"device_platform":"android"}',
          "trace_id":str(int(time.time()*1000))+os.urandom(4).hex(),
          "dev_info":'{"os":"Android","device_platform":"android","is_h5":true,"front_type":"h5"}'}
    r=requests.post("https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm",data=form,headers=CH,timeout=25)
    try: return r.json()
    except Exception: return {"_raw":r.text[:200]}
for scene in ("h5","qrcode","pc"):
    for ch in ("ALI_H5","ALI_NATIVE","ALI_QR"):
        jj=confirm(scene,"alipay",ch)
        pp=(jj.get("data") or {}).get("pay_params") or {}
        tt=(jj.get("data") or {}).get("trade_info") or {}
        data=pp.get("data") or ""
        inner={}
        try: inner=json.loads(data)
        except Exception: pass
        u=inner.get("url") or ""
        print("%-7s %-11s code=%-6s trade_type=%-8s len=%-5d qr.alipay=%s head=%s" % (
            scene,ch,jj.get("code"),pp.get("trade_type"),len(u),"YES" if "qr.alipay.com" in u else "-", (u or data)[:40]))
        time.sleep(0.5)
json.dump({"papi":papi,"trade_no":tno,"order":d.get("order_id")},open("_last_order.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
