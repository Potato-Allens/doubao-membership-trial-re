# -*- coding: utf-8 -*-
import json, time, urllib.parse, requests
d=json.load(open("_cd_net.json",encoding="utf-8"))
post=None
for r in d["reqs"]:
    if "trade_create" in r["u"]:
        post=r["post"]; break
print("post len",len(post))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
H={"content-type":"application/x-www-form-urlencoded","origin":"https://tp-pay.snssdk.com",
   "referer":"https://tp-pay.snssdk.com/","user-agent":UA}
url="https://tp-pay.snssdk.com/gateway-cashier2/tp/cashier/trade_create"
r=requests.post(url,data=post.encode(),headers=H,timeout=25)
print("status",r.status_code,"len",len(r.text))
j=r.json()
print("keys",list(j.keys()))
data=j.get("data") or {}
print("data keys",list(data.keys()))
for k in ("paytype_items","exts","jh_pass_through","merchant_info"):
    print(k,":",json.dumps(data.get(k),ensure_ascii=False)[:500])
s=json.dumps(j,ensure_ascii=False)
for kw in ("qr","code_url","alipay","ALI"):
    idx=s.find(kw)
    print("%-9s first@%s" % (kw,idx), s[max(0,idx-60):idx+140].replace("\n"," ") if idx>0 else "")
open("_trade_create_full.json","w",encoding="utf-8").write(json.dumps(j,ensure_ascii=False,indent=1))
