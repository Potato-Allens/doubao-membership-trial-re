import json, requests, time, sys, io
from concurrent.futures import ThreadPoolExecutor
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
scan={r.get('uid'):r for r in json.load(open('scan_212.json',encoding='utf-8'))}
def one(i):
    a=pool[i]; s=requests.Session(); s.cookies.update(ck(a.get('cookie_string','')))
    try:
        j=s.get('https://accounts.doubao.com/passport/account/info/v2/?aid=497858',
                headers={'user-agent':UA,'referer':'https://www.doubao.com/'},timeout=20).json()
    except Exception as e:
        return {'i':i,'err':str(e)[:50]}
    d=j.get('data') or {}
    time.sleep(0.15)
    return {'i':i,'uid':d.get('user_id_str'),'app':d.get('app_id'),'cc':d.get('country_code'),
            'hm':d.get('hm_region'),'mob':d.get('mobile'),'ct':d.get('user_create_time'),
            'odin':d.get('odin_user_type'),'err':d.get('error_code')}
out=[]
with ThreadPoolExecutor(max_workers=4) as ex:
    for r in ex.map(one, range(len(pool))):
        out.append(r)
json.dump(out,open('app_id_map.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
from collections import Counter
ok=[r for r in out if r.get('app')]
print('ok',len(ok),'err',len(out)-len(ok))
print('app_id:',Counter(r['app'] for r in ok))
print('cc:',Counter(r.get('cc') for r in ok))
print()
for r in ok:
    if r.get('cc') in (1,0) or r.get('app')!=582478:
        print(r)