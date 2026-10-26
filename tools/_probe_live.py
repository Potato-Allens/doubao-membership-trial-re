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
line=open('pool/live_intake.jsonl',encoding='utf-8').readline().strip()
uid,cs=line.split('|',1)
s=requests.Session(); s.cookies.update(ck(cs))
info=s.get('https://accounts.doubao.com/passport/account/info/v2/?aid=497858',headers={'user-agent':UA},timeout=20).json().get('data') or {}
print('uid',info.get('user_id_str'),'cc',info.get('country_code'),'hm',info.get('hm_region'),'mob',info.get('mobile'),'ct',info.get('user_create_time'))
j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=SCOPE,json={'scene_key':'default_member_link'},headers=H,timeout=25).json()
d=j.get('data') or {}
best=[]
for sku in d.get('sku_list') or []:
    for c in sku.get('purchase_card_list') or []:
        if (c.get('discount_amount') or 0)>0 or c.get('trial_info'):
            best.append((sku.get('sku_key'),c.get('card_id'),c.get('discount_amount'),c.get('trial_info'),c.get('button_text'),c.get('trade_extra')))
print('init code',j.get('code'),'hist',d.get('has_history_paid_subscription'),'offers',best)
p=s.post(BASE+'/alice/commerce/sale/campaign/page/query/',params=SCOPE,json={},headers=H,timeout=20).json()
print('page',json.dumps(p.get('data'),ensure_ascii=False))
b=s.post(BASE+'/alice/commerce/sale/trade/beta/check/',params=SCOPE,json={'activity_id':''},headers=H,timeout=20).json()
print('beta',json.dumps(b,ensure_ascii=False))