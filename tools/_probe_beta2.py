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
cands=['','0','1','497858','582478','pc_new_user_campaign','doubao_member_trial','member_trial',
       'doubao_personal_std_trial','first_purchase_trial','intro_offer','doubao_member_intro',
       'trial','7d_trial','new_user_trial','doubao_trial','std_trial']
for a in cands:
    try:
        j=s.post(BASE+'/alice/commerce/sale/trade/beta/check/',params=SCOPE,json={'activity_id':a},headers=H,timeout=20).json()
        d=json.dumps(j,ensure_ascii=False)
        print('%-26r %s'%(a,d[:220]))
    except Exception as e: print(a,'ERR',str(e)[:60])
    time.sleep(0.3)