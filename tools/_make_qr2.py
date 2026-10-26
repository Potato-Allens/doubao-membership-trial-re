# -*- coding: utf-8 -*-
"""Fresh order -> Alipay H5 scheme -> short link -> QR png (scannable)."""
import base64, json, os, time, urllib.parse, requests, qrcode
from urllib.parse import urlparse, parse_qs

BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web","aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription","origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
CH={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com","referer":"https://tp-pay.snssdk.com/","user-agent":UA}
OUT=os.path.dirname(os.path.abspath(__file__))
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
print("order",d.get("order_id"),"trade_no",tno)
bc={"trade_no":tno,"ptcode":"alipay",
    "ptcode_info":{"bank_card_id":"","business_scene":"",
      "return_url":"https://tp-pay.snssdk.com/cashdesk?cj_new_api=1&cj_source=alipay&cj_trade_no=%s&cj_process=%s&cj_remain_time=0&cj_result_extra=&cj_qrcode_env=qrcode"%(tno,base64.b64encode(papi.encode()).decode())},
    "support_evoke_channels":""}
form={"biz_content":json.dumps(bc,separators=(",",":")),"channel_support_scene":"ALI_H5","process":papi,
      "scene":"h5","risk_info":'{"device_platform":"android"}',
      "trace_id":str(int(time.time()*1000))+os.urandom(4).hex(),
      "dev_info":'{"os":"Android","device_platform":"android","is_h5":true,"front_type":"h5"}'}
r=requests.post("https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm",data=form,headers=CH,timeout=25)
jj=r.json(); pp=(jj.get("data") or {}).get("pay_params") or {}
h5=json.loads(pp.get("data") or "{}").get("url") or ""
print("h5 len",len(h5))
short=""
for svc in ("https://is.gd/create.php?format=simple&url=","https://tinyurl.com/api-create.php?url="):
    try:
        rr=requests.get(svc+urllib.parse.quote(h5,safe=""),timeout=20)
        if rr.status_code==200 and rr.text.strip().startswith("http"):
            short=rr.text.strip(); break
    except Exception as e:
        print("shorten err",str(e)[:50])
print("short",short)
tgt=short or h5
img=qrcode.make(tgt)
img=img.resize((620,620))
path=os.path.join(OUT,"_qr_alipay_pay.png")
img.save(path)
print("qr",path,"payload len",len(tgt))
info={"order_id":d.get("order_id"),"trade_no":tno,"h5":h5,"short":short,
      "qr":path,"created":time.strftime("%Y-%m-%d %H:%M:%S"),
      "deadline":time.strftime("%H:%M:%S",time.localtime(time.time()+(cred.get("order_expire_seconds") or 1800)))}
json.dump(info,open("_alipay_pay.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("DEADLINE",info["deadline"])
