import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
s=requests.Session(); s.cookies.update(ck(pool[4]['cookie_string']))
for aid in (0,1,100,497858,582478,0000000000000003):
    try:
        j=s.post(BASE+'/alice/commerce/sale/trade/beta/check/',params=SCOPE,json={'activity_id':aid},headers=H,timeout=20).json()
        print('beta',aid,json.dumps(j,ensure_ascii=False)[:260])
    except Exception as e: print('beta',aid,'ERR',str(e)[:60])
    time.sleep(0.3)
print('--- entitlements/cards')
probes=[
 ('intake ent','/alice/commerce/intake/entitlement/query',{}),
 ('card list','/alice/commerce/marketing/card/list/',{}),
 ('card list all','/alice/commerce/marketing/card/list/',{'status_in':[],'with_limit_status':True}),
 ('benefit pkg','/alice/commerce/sale/subscription/benefit_package/',{}),
 ('gift detail','/alice/commerce/marketing/gift/detail/',{'code':'','scene':0}),
]
for name,p,b in probes:
    try:
        j=s.post(BASE+p,params=SCOPE,json=b,headers=H,timeout=20).json()
        print(name,json.dumps(j,ensure_ascii=False)[:300])
    except Exception as e: print(name,'ERR',str(e)[:60])
    time.sleep(0.3)