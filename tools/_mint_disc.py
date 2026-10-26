# -*- coding: utf-8 -*-
import base64, json, os, sys, time, urllib.parse, requests, qrcode
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
idx=int(sys.argv[1]) if len(sys.argv)>1 else 57
accs=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
it=accs[idx]
ck={}
for p in it["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); ck[k.strip()]=v.strip()
uid=it.get("uid")
print("target idx=%d uid=%s"%(idx,uid))
s=requests.Session(); s.cookies.update(ck)
j=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,json={"scene_key":"default_member_link"},headers=H,timeout=25).json()
card=None
for sku in (j.get("data") or {}).get("sku_list") or []:
    for c in sku.get("purchase_card_list") or []:
        if c.get("card_id")==CARD: card=c
print("init code",j.get("code"),"| btn",card.get("button_text") if card else None,
      "| disc",card.get("discount_amount") if card else None,
      "| total",card.get("discount_total_price") if card else None,
      "| extra",card.get("trade_extra") if card else None)
total=card.get("discount_total_price") or card.get("list_total_price") or 6800
r={
 "sku_key":SKU,"card_id":CARD,"purchase_channel":2,"support_diff_price":True,"timezone":-480,
 "total_price":total,"trade_extra":card.get("trade_extra") or "{}","is_eligible_for_intro_offer":True,
}
es=s.post(BASE+"/alice/commerce/sale/trade/estimate/",params=SCOPE,json=r,headers=H,timeout=25).json()
d=es.get("data") or {}; pi=d.get("price_info") or {}; pinf=d.get("purchase_info") or {}
pay=pi.get("pay_amount")
print("estimate code",es.get("code"),"pay",pay,"| start",pinf.get("start_time"),"| end",pinf.get("end_time"))
if es.get("code")!=0 or not pay:
    print("estimate failed:",str(es.get("message"))[:60]); sys.exit(3)
body={"sku_key":SKU,"card_id":CARD,"estimated_pay_amount":str(pay),"purchase_channel":2,
      "upgrade_mode":0,"is_gift_deferred":False,"start_time":int(time.time()*1000),
      "trade_extra":card.get("trade_extra") or "{}","is_eligible_for_intro_offer":True}
cr=s.post(BASE+"/alice/commerce/sale/trade/create/",params=SCOPE,json=body,headers=H,timeout=30).json()
dd=cr.get("data") or {}; cred=dd.get("payment_credential") or {}
print("create code",cr.get("code"),"order",dd.get("order_id"),str(cr.get("message"))[:40])
if cr.get("code")!=0: sys.exit(4)
pu=cred.get("pay_url") or ""; q=parse_qs(urlparse(pu).query)
papi=q["papi_id"][0]; tno=q["trade_no"][0]
bc={"trade_no":tno,"ptcode":"alipay","ptcode_info":{"bank_card_id":"","business_scene":"",
    "return_url":"https://tp-pay.snssdk.com/cashdesk?cj_new_api=1&cj_source=alipay&cj_trade_no=%s&cj_process=%s&cj_remain_time=0&cj_result_extra=&cj_qrcode_env=qrcode"%(tno,base64.b64encode(papi.encode()).decode())},
    "support_evoke_channels":""}
form={"biz_content":json.dumps(bc,separators=(",",":")),"channel_support_scene":"ALI_H5",
      "process":papi,"scene":"h5","risk_info":'{"device_platform":"android"}',
      "trace_id":str(int(time.time()*1000))+os.urandom(4).hex(),
      "dev_info":'{"os":"Android","device_platform":"android","is_h5":true,"front_type":"h5"}'}
ans=requests.post("https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm",data=form,headers=CH,timeout=30).json()
pp=(ans.get("data") or {}).get("pay_params") or {}
h5=""
try: h5=json.loads(pp.get("data") or "{}").get("url") or ""
except Exception: pass
cash="https://tp-pay.snssdk.com/cashdesk?papi_id=%s&qrcode_env=qrcode&withhold_scene=sign_and_pay&trade_no=%s"%(papi,tno)
short=""
for svc in ("https://is.gd/create.php?format=simple&url=","https://tinyurl.com/api-create.php?url="):
    try:
        rr=requests.get(svc+urllib.parse.quote(h5,safe=""),timeout=20)
        if rr.status_code==200 and rr.text.strip().startswith("http"): short=rr.text.strip(); break
    except Exception: pass
print("alipay type",pp.get("trade_type"),"h5_len",len(h5),"short",short)
for tag,payload,bs in (("pay_disc_main.png",short or h5,16),("pay_disc_backup.png",cash,14)):
    qq=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=bs,border=4)
    qq.add_data(payload); qq.make(fit=True); qq.make_image().save(tag)
    print("qr",tag,"v",qq.version,"len",len(payload))
exp=cred.get("order_expire_seconds") or 1799
info={"idx":idx,"uid":uid,"order_id":dd.get("order_id"),"subscription_id":dd.get("subscription_id"),
      "trade_no":tno,"pay_amount":pay,"short":short,"cashdesk":cash,
      "deadline":time.strftime("%H:%M:%S",time.localtime(time.time()+exp)),
      "created":time.strftime("%Y-%m-%d %H:%M:%S")}
json.dump(info,open("pay_disc.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(json.dumps(info,ensure_ascii=False,indent=1))
import shutil
for f in ("pay_disc_main.png","pay_disc_backup.png"):
    shutil.copy(f, r"C:\Users\Administrator\AppData\Local\Temp\%s"%f)
print("copied to TEMP")
