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
ELIG="0000000000000003"
now=int(time.time()*1000)
body={"sku_key":"doubao_personal_std","card_id":"doubao_personal_std_auto_renew_month",
      "estimated_pay_amount":"100","purchase_channel":2,"upgrade_mode":0,
      "is_gift_deferred":False,"start_time":now,
      "trade_extra":json.dumps({"selected_eligibility_id":int(ELIG)},separators=(",",":")),
      "is_eligible_for_intro_offer":True}
for idx in (4,47,53):
    a=pool[idx]; s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
    try:
        j=s.post(BASE+'/alice/commerce/sale/trade/create/',params=SCOPE,json=body,headers=H,timeout=25).json()
        d=j.get('data') or {}
        cred=d.get('payment_credential') or {}
        print('idx%-4d uid=%-18s code=%-8s msg=%-28s order=%s pay_amount=%s url=%s'%(
            idx,a.get('uid'),j.get('code'),str(j.get('message'))[:26],d.get('order_id'),
            (d.get('price_info') or {}).get('pay_amount') or d.get('pay_amount'),
            (cred.get('pay_url') or '')[:90]))
    except Exception as e:
        print('idx',idx,'ERR',str(e)[:80])
    time.sleep(0.5)