import json, requests, sys, io, time
from concurrent.futures import ThreadPoolExecutor
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
appmap={}
for r in json.load(open('app_id_map.json',encoding='utf-8')):
    if r.get('app'): appmap[r['uid']]=r
def one(i):
    a=pool[i]; s=requests.Session(); s.cookies.update(ck(a.get('cookie_string','')))
    out={'idx':i,'uid':a.get('uid')}
    try:
        j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=SCOPE,json={'scene_key':'default_member_link'},headers=H,timeout=20).json()
        d=j.get('data') or {}
        best={'disc':0,'trial':None,'extra':None,'btn':None,'card':None}
        for sku in d.get('sku_list') or []:
            for c in sku.get('purchase_card_list') or []:
                if (c.get('discount_amount') or 0)>best['disc']:
                    best={'disc':c.get('discount_amount'),'trial':c.get('trial_info'),'extra':c.get('trade_extra'),'btn':c.get('button_text'),'card':c.get('card_id')}
        out.update(best); out['hist']=d.get('has_history_paid_subscription'); out['claim']=d.get('entitlement_claim_status')
        out['skus']=len(d.get('sku_list') or []); out['acts']=d.get('activities')
    except Exception as e:
        out['err']=str(e)[:40]
    try:
        p=s.post(BASE+'/alice/commerce/sale/campaign/page/query/',params=SCOPE,json={},headers=H,timeout=20).json()
        out['page']=(p.get('data') or {}).get('page_status')
    except Exception: out['page']=None
    try:
        b=s.post(BASE+'/alice/commerce/sale/trade/beta/check/',params=SCOPE,json={'activity_id':''},headers=H,timeout=20).json()
        out['beta']=(b.get('data') or {}).get('state')
    except Exception: out['beta']=None
    time.sleep(0.1)
    return out
rows=[]
with ThreadPoolExecutor(max_workers=3) as ex:
    for k,r in enumerate(ex.map(one, range(len(pool))),1):
        rows.append(r)
        if (r.get('disc') or 0)>0 or (r.get('page') not in (3,None)):
            print('[SIGNAL]', json.dumps(r,ensure_ascii=False)[:300], flush=True)
        if k%40==0: print('..',k,flush=True)
json.dump(rows,open('sweep_elig_434.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
from collections import Counter
print('codes: disc>0',sum(1 for r in rows if (r.get('disc') or 0)>0))
print('page:',Counter(r.get('page') for r in rows))
print('beta:',Counter(r.get('beta') for r in rows))
print('skus:',Counter(r.get('skus') for r in rows))
print('acts:',Counter(json.dumps(r.get('acts'),ensure_ascii=False,sort_keys=True) for r in rows).most_common(5))
print('hist:',Counter(r.get('hist') for r in rows))