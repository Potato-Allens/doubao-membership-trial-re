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
neg=pool[4]
s=requests.Session(); s.cookies.update(ck(neg['cookie_string']))
for body in ({'scene_key':'default_member_link'}, {'scene_key':'default_member_link','is_eligible_for_intro_offer':True}):
    j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=SCOPE,json=body,headers=H,timeout=25).json()
    d=j.get('data') or {}
    print('BODY',body,'code',j.get('code'))
    print('top keys',list(d.keys()))
    for sku in (d.get('sku_list') or []):
        print(' sku',sku.get('sku_key'),'keys',list(sku.keys())[:20])
        for c in (sku.get('purchase_card_list') or []):
            print('   card',c.get('card_id'),'disc',c.get('discount_amount'),'price',c.get('total_price'),'trial',c.get('trial_info'))
            print('   card keys',[k for k in c.keys()])
    print()