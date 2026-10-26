import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
BASE="https://www.doubao.com"
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
def ck(s):
    d={}
    for p in s.split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
pool=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
a=pool[4]; s=requests.Session(); s.cookies.update(ck(a["cookie_string"]))
def post(ep,b):
    try: return s.post(BASE+ep,params=SCOPE,json=b,headers=H,timeout=15).json()
    except Exception as e: return {"EXC":str(e)[:60]}
scenes=["member","settings","setting","home","chat","sidebar","profile","activity_center","task_center",
        "incentive","pc_client","app","doubao","default","main","main_page","member_center","subscription",
        "0","1","2","3","4","5","6","member_page","user_setting","personal","uprofile","assistant"]
codes=["pc_new_user_campaign","download_doubao_gift","member_trial","membership","pc_growth","doubao_pc_gift",""]
hits=0; tried=0
for code in codes:
    for sc in scenes:
        tried+=1
        j=post("/alice/ug/campaign/list/",{"campaign_group_code":code,"scene":sc})
        c=j.get("code")
        if c==0 and (j.get("data")):
            hits+=1; print("HIT code=%r scene=%r -> %s"%(code,sc,json.dumps(j,ensure_ascii=False)[:500]))
        elif c not in (710010702,710010201,"InvalidRequest"):
            print("ODD code=%r scene=%r -> %s"%(code,sc,json.dumps(j,ensure_ascii=False)[:300]))
        time.sleep(0.12)
print("tried",tried,"hits",hits)