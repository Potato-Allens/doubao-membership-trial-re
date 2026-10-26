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
s=requests.Session(); s.cookies.update(ck(pool[4]['cookie_string']))
vals=['profile_setting','profile','avatar_menu','sidebar','pc_sidebar','settings','dropdown','menu','invite','client']
for v in vals:
    for extra in ({},{'activity_id':''}):
        q={**SCOPE,'enter_from':v,**extra}
        try:
            j=s.get(BASE+'/samantha/fission/entrance',params=q,headers=H,timeout=20).json()
            d=json.dumps(j,ensure_ascii=False)
            if j.get('code')==671010000:
                print('%-16s %-14s ERR %s'%(v,list(extra),d[:80]))
            else:
                print('%-16s %-14s >>> %s'%(v,list(extra),d[:600]))
        except Exception as e:
            print(v,'ERR',str(e)[:50])
        time.sleep(0.25)