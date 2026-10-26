# -*- coding: utf-8 -*-
import json, requests, random, uuid
BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
CARD="doubao_personal_std_auto_renew_month"
def pick(j):
    d=j.get("data") or {}
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("card_id")==CARD:
                return {"code":j.get("code"),"disc":c.get("discount_amount") or 0,
                        "btn":c.get("button_text"),"trial":c.get("trial_info"),"extra":c.get("trade_extra")}
    return {"code":j.get("code"),"msg":str(j.get("message") or j.get("msg") or "")[:60]}
print("--- anonymous, no cookies ---")
for i in range(3):
    s=requests.Session()
    r=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,
             json={"scene_key":"default_member_link","purchase_channel":2},headers=H,timeout=25)
    print(" anon%d"%i, json.dumps(pick(r.json()),ensure_ascii=False)[:300])
print("--- anonymous with synthetic device cookies ---")
for i in range(3):
    s=requests.Session()
    did=str(random.randint(7000000000000000000,7999999999999999999))
    s.cookies.update({"device_id":did,"install_id":did,"iid":did,"web_id":str(random.randint(7e18,7.9e18)),
                      "ttwid":"1%7C"+uuid.uuid4().hex,"s_v_web_id":"verify_"+uuid.uuid4().hex[:10]})
    r=s.post(BASE+"/alice/commerce/sale/trade/init/",params=SCOPE,
             json={"scene_key":"default_member_link","purchase_channel":2},headers=H,timeout=25)
    print(" synth%d"%i, json.dumps(pick(r.json()),ensure_ascii=False)[:300])