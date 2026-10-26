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
for idx in (4,57):
    a=pool[idx]; s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
    j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=SCOPE,json={'scene_key':'default_member_link'},headers=H,timeout=25).json()
    d=j.get('data') or {}
    for sku in d.get('sku_list') or []:
        if sku.get('sku_key')!='doubao_personal_std': continue
        for c in sku.get('purchase_card_list') or []:
            if c.get('card_id')=='doubao_personal_std_auto_renew_month':
                print('### idx',idx); print(json.dumps(c,ensure_ascii=False,indent=1)[:1600])
    print('page_display_type',d.get('page_display_type'),'show_consumption',d.get('show_consumption'),'service_time',d.get('service_current_time'))