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
neg=pool[4]
s=requests.Session(); s.cookies.update(ck(neg['cookie_string']))
tests=[
 ('empty',{}),
 ('page_type0',{'page_type':0}),
 ('page_type1',{'page_type':1}),
 ('page_type2',{'page_type':2}),
 ('page_type3',{'page_type':3}),
 ('scene',{'scene_key':'default_member_link'}),
 ('scene2',{'scene_key':'member_subscription'}),
 ('camp',{'campaign_id':'pc_new_user_campaign'}),
 ('camp2',{'campaign_id':'doubao_personal_trial'}),
 ('page_key',{'page_key':'member_subscription'}),
 ('sku',{'sku_key':'doubao_personal_std'}),
]
for name,body in tests:
    try:
        j=s.post(BASE+'/alice/commerce/sale/campaign/page/query/',params=SCOPE,json=body,headers=H,timeout=20).json()
        print('%-10s %s'%(name,json.dumps(j,ensure_ascii=False)[:300]))
    except Exception as e:
        print(name,'ERR',str(e)[:80])
    time.sleep(0.4)
print('--- GET mode')
for name,body in tests[:3]:
    try:
        r=s.get(BASE+'/alice/commerce/sale/campaign/page/query/',params={**SCOPE,**body},headers=H,timeout=20)
        print(name,r.status_code,r.text[:200])
    except Exception as e: print(name,'ERR',e)