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
hit=[a for a in pool if a.get('uid')=='0000000000000001'][0]
neg=pool[4]
PROBES=[
 ('ug/campaign/list','/alice/ug/campaign/list/',{}),
 ('ug/list scene','/alice/ug/campaign/list/',{'scene':'member'}),
 ('mget/v2 empty','/alice/commerce/marketing/resource/mget/v2/',{'resource_keys':[],'is_eligible_for_intro_offer':True}),
 ('mget/v2 guess','/alice/commerce/marketing/resource/mget/v2/',{'resource_keys':['member_page','intro_offer','first_purchase_trial','trial_offer','member_trial','subscription_page'],'is_eligible_for_intro_offer':True}),
 ('activity detail','/alice/commerce/marketing/activity/detail/',{'activity_key':'doubao_member_trial','channel':'web'}),
 ('trial init','/alice/commerce/sale/campaign/trial/init/',None),
 ('campaign page','/alice/commerce/sale/campaign/page/query/',None),
 ('resolve cta','/alice/commerce/sale/marketing/cta/resolve_fixed_cta',{'scene_key':'default_member_link','sku_key':'doubao_personal_std'}),
]
for label,a in (('HIT',hit),('NEG',neg)):
    s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
    print('==========',label,a.get('uid'))
    for name,path,body in PROBES:
        try:
            kw={'params':SCOPE,'headers':H,'timeout':25}
            if body is None:
                r=s.post(BASE+path,**kw)
            else:
                r=s.post(BASE+path,json=body,**kw)
            try: j=r.json()
            except Exception: j={'raw':r.text[:200]}
            s2=json.dumps(j,ensure_ascii=False)
            print('--',name,r.status_code,s2[:400])
        except Exception as e:
            print('--',name,'ERR',str(e)[:80])
        time.sleep(0.5)