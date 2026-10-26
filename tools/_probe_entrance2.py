import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
c=ck(pool[4]['cookie_string'])
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1",
 "device_id":c.get('device_id',''),"iid":c.get('iid',''),"install_id":c.get('install_id',''),
 "cdid":c.get('cdid',''),"channel":"pc","app_id":"497858","os":"windows","os_version":"10"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
s=requests.Session(); s.cookies.update(c)
for v in ('profile_setting','sidebar'):
    j=s.get(BASE+'/samantha/fission/entrance',params={**SCOPE,'enter_from':v},headers=H,timeout=20).json()
    print(v,json.dumps(j,ensure_ascii=False)[:400])
# try POST too
for v in ('profile_setting',):
    for body in ({'enter_from':v},{'enter_from':v,'activity_id':''}):
        j=s.post(BASE+'/samantha/fission/entrance',params=SCOPE,json=body,headers=H,timeout=20).json()
        print('POST',body,json.dumps(j,ensure_ascii=False)[:300])