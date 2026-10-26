import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
for idx in (4,):
    s=requests.Session(); s.cookies.update(ck(pool[idx]['cookie_string']))
    print('### idx',idx)
    for ef in ('','sidebar','settings','member','pc_sidebar','referral'):
        try:
            j=s.get(BASE+'/samantha/fission/entrance',params={**SCOPE,'enter_from':ef},headers=H,timeout=20).json()
            print(' entrance enter_from=%-10r %s'%(ef,json.dumps(j,ensure_ascii=False)[:420]))
        except Exception as e: print(' entrance',ef,'ERR',str(e)[:60])
        time.sleep(0.3)
    for ep,body in (('/samantha/fission/draw',{'is_exchange':False,'activity_id':''}),
                    ('/samantha/fission/reward_info',{'order_id':'','activity_id':''})):
        try:
            j=s.post(BASE+ep,params=SCOPE,json=body,headers=H,timeout=20).json()
            print(' %-34s %s'%(ep,json.dumps(j,ensure_ascii=False)[:420]))
        except Exception as e: print(ep,'ERR',str(e)[:60])
        time.sleep(0.3)