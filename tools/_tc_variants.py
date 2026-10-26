# -*- coding: utf-8 -*-
import json, time, urllib.parse, requests
c=json.load(open("_cd_confirm2.json",encoding="utf-8"))
base=dict(urllib.parse.parse_qsl(c["req"]["post"]))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
H={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com",
   "referer":"https://tp-pay.snssdk.com/","user-agent":UA}
URL="https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_confirm"
def run(tag, **over):
    d=dict(base); d.update(over)
    try:
        r=requests.post(URL,data=d,headers=H,timeout=25,allow_redirects=False)
        body=r.text
        print("== %-22s status=%s len=%s" % (tag,r.status_code,len(body)))
        loc=r.headers.get("location","")
        if loc: print("   LOC", loc[:180])
        if body and body.strip().startswith("{"):
            j=json.loads(body)
            print("   code=%s keys=%s" % (j.get("code"), list((j.get("data") or {}).keys())))
            s=json.dumps(j,ensure_ascii=False)
            for kw in ("code_url","qr","alipay","pay_url","scheme"):
                i=s.find(kw)
                if i>0: print("   %s -> %s" % (kw, s[max(0,i-50):i+160]))
        else:
            print("   body", body[:200].replace("\n"," "))
    except Exception as e:
        print("== %-22s ERR %s" % (tag,str(e)[:70]))
run("baseline ALI_H5")
time.sleep(1)
for sc in ("ALI_NATIVE","ALI_QR","ALI_PC","ALI_APP","ALI_WAP"):
    run("scene="+sc, channel_support_scene=sc)
    time.sleep(1)
