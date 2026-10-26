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
cands=['','0','1','497858','582478','pc_new_user_campaign','professional_beta','doubao_professional_beta',
 'doubao_member_trial','trial','member_trial','1yuan','one_yuan','first_purchase_trial','intro_offer']
for a in cands:
    q={**SCOPE,'activity_id':a}
    try:
        j=s.post(BASE+'/alice/commerce/sale/campaign/page/query/',params=q,json={},headers=H,timeout=20).json()
        print('%-28r %s %s'%(a,json.dumps(j.get('data'),ensure_ascii=False),j.get('code')))
    except Exception as e: print(a,'ERR',str(e)[:50])
    time.sleep(0.3)