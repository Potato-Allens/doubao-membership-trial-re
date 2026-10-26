# -*- coding: utf-8 -*-
import json, requests, itertools
BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def sess(i):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    s=requests.Session(); s.cookies.update(d); return s
def post(s,ep,body=None):
    try:
        r=s.post(BASE+ep,params=SCOPE,json=body if body is not None else {},headers=H,timeout=25)
        return r.json()
    except Exception as e:
        return {"code":-1,"message":str(e)[:100]}
def pick(j):
    d=j.get("data") or {}
    best=None
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("card_id")==CARD:
                best=c
    if best is None: return {"code":j.get("code"),"msg":str(j.get("message") or "")[:30]}
    return {"code":j.get("code"),"disc":best.get("discount_amount") or 0,
            "dtp":best.get("discount_total_price"),"btn":best.get("button_text"),
            "trial":(best.get("trial_info") or {}).get("trial_stage"),
            "extra":best.get("trade_extra")}
CARD="doubao_personal_std_auto_renew_month"
SCENES=["default_member_link","user_setting","renewal_guidance_v1","first_purchase","new_user",
 "trial","intro_offer","intro_offer_1","upgrade","retention","exit_retention","student",
 "member_center","quota_management","chat_limit","model_limit","video_limit","image_limit",
 "paywall","paywall_chat","paywall_image","paywall_video","paywall_ppt","out_of_quota",
 "task_limit","expire_intercept","cancel_retention","downgrade","win_client","client_paywall",
 "pc_client","doubao_pc","app_paywall","app_client","member_link","default","subscribe",
 "subscription","home_banner","chat_banner","side_bar","settings","onboarding","guide",
 "first_purchase_price_1","first_purchase_price_38","trail_1","trial_1_yuan","one_yuan","1yuan"]
if __name__=="__main__":
    res={}
    for idx in (0,57):
        s=sess(idx)
        for sk in SCENES:
            r=pick(post(s,"/alice/commerce/sale/trade/init/",{"scene_key":sk}))
            res.setdefault(str(idx),{})[sk]=r
        # alternate bodies
        for body in ({}, {"scene_key":"default_member_link","purchase_channel":1},
                     {"scene_key":"default_member_link","purchase_channel":2},
                     {"scene_key":"default_member_link","is_eligible_for_intro_offer":True},
                     {"scene_key":"default_member_link","sku_key":"doubao_personal_std"},
                     {"scene_key":"default_member_link","card_id":"doubao_personal_std_auto_renew_month"},
                     {"scene_key":"default_member_link","entrance":"paywall"},
                     {"scene_key":"default_member_link","source":"client"},
                     {"scene_key":"default_member_link","platform":"pc"}):
            r=pick(post(s,"/alice/commerce/sale/trade/init/",body))
            res[str(idx)]["BODY:"+json.dumps(body,ensure_ascii=False)]=r
    json.dump(res,open("_scene_probe.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
    for idx,v in res.items():
        print("### idx",idx)
        for sk,r in v.items():
            flag="  <<< HIT" if (r.get("disc") or 0)==6700 or r.get("trial")==1 else ""
            print("  %-46s %s %s %s%s"%(sk,r.get("code"),r.get("btn"),r.get("disc"),flag))