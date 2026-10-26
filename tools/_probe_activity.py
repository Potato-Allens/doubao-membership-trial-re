import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","device_id":"0000000000000005",
 "pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN",
 "samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/professional-beta",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
s=requests.Session(); s.cookies.update(ck(pool[4]['cookie_string']))
for ch in (0,1,2,3,4,5):
    try:
        j=s.post(BASE+'/alice/commerce/marketing/activity/detail/',params=SCOPE,json={'activity_key':'k7m3qx9p','channel':ch},headers=H,timeout=20).json()
        print('channel',ch,json.dumps(j,ensure_ascii=False)[:700])
    except Exception as e: print('channel',ch,'ERR',str(e)[:60])
    time.sleep(0.3)
print('--- beta check exact')
for a in ('k7m3qx9p',''):
    j=s.post(BASE+'/alice/commerce/sale/trade/beta/check/',params=SCOPE,json={'activity_id':a},headers=H,timeout=20).json()
    print(repr(a),json.dumps(j,ensure_ascii=False)[:300])