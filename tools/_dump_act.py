import json, requests, sys, io
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
for idx in (4,120,47,53,57):
    a=pool[idx]; s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
    j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=SCOPE,json={'scene_key':'default_member_link'},headers=H,timeout=25).json()
    d=j.get('data') or {}
    print('### idx',idx,a.get('uid'),'code',j.get('code'),'pdt',d.get('page_display_type'),'hist',d.get('has_history_paid_subscription'),'sub_type',d.get('sub_type'),'claim',d.get('entitlement_claim_status'))
    print(json.dumps(d.get('activities'),ensure_ascii=False)[:1200])
    print()