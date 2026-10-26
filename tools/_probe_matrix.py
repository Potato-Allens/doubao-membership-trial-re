# -*- coding: utf-8 -*-
import base64, json, os, time, requests
o=json.load(open("_probe_order.json",encoding="utf-8"))
papi=o["papi"]; tno=o["trade_no"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
CH={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com","referer":"https://tp-pay.snssdk.com/","user-agent":UA}
URL="https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm"
res=[]
def confirm(scene,channel,ptcode,is_h5,plat,front,osname,tag):
    bc={"trade_no":tno,"ptcode":ptcode,
        "ptcode_info":{"bank_card_id":"","business_scene":"",
          "return_url":"https://tp-pay.snssdk.com/cashdesk?cj_new_api=1&cj_source=%s&cj_trade_no=%s&cj_process=%s&cj_remain_time=0&cj_result_extra=&cj_qrcode_env=qrcode"%(ptcode,tno,base64.b64encode(papi.encode()).decode())},
        "support_evoke_channels":""}
    form={"biz_content":json.dumps(bc,separators=(",",":")),"channel_support_scene":channel,
          "process":papi,"scene":scene,
          "risk_info":json.dumps({"device_platform":plat}),
          "trace_id":str(int(time.time()*1000))+os.urandom(4).hex(),
          "dev_info":json.dumps({"os":osname,"device_platform":plat,"is_h5":is_h5,"front_type":front},separators=(",",":"))}
    t0=time.time()
    try:
        r=requests.post(URL,data=form,headers=CH,timeout=20); j=r.json()
    except Exception as e:
        print("%-34s ERR %s"%(tag,str(e)[:60])); return
    d=j.get("data") or {}; pp=d.get("pay_params") or {}
    tt=pp.get("trade_type"); inner={}
    try: inner=json.loads(pp.get("data") or "{}")
    except Exception: pass
    u=inner.get("url") or ""; au=inner.get("alipay_url") or ""
    blob=json.dumps(j,ensure_ascii=False)
    has_qr="qr.alipay.com" in blob
    print("%-34s code=%-6s type=%-10s qr=%-3s len=%-5d %s"%(tag,j.get("code"),tt,"YES" if has_qr else "-",len(u),(au or u)[:70]))
    res.append({"tag":tag,"scene":scene,"channel":channel,"ptcode":ptcode,"code":j.get("code"),"type":tt,"qr":has_qr,"url":u,"alipay_url":au,"ms":int((time.time()-t0)*1000)})

scenes=["h5","qrcode","pc","native","app","scan"]
channels=["ALI_H5","ALI_QR","ALI_NATIVE","ALI_PC","ALI_F2F","ALI_QRCODE","ALI_PRECREATE","ALI_SCAN","ALIPAY_QR","ALI_APP","ALI_WAP",""]
for sc in scenes:
    for ch in channels:
        confirm(sc,ch,"alipay", sc not in ("pc",), "android" if sc not in ("pc",) else "pc", "h5" if sc not in ("pc",) else "pc","Android" if sc not in ("pc",) else "Windows","%s|%s"%(sc,ch or "-"))
        time.sleep(0.35)
print("--- ptcode variants @ best ---")
for pc in ["alipay_qr","alipay_scan","alipay_pc","alipay_wap","alipay_native","ALIPAY"]:
    confirm("qrcode","ALI_QR",pc,False,"pc","pc","Windows","ptcode="+pc)
    time.sleep(0.35)
json.dump(res,open("_probe_matrix.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("saved",len(res))
