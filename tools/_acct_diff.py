import json, requests
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
def cookies(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
def get(ck, url, **kw):
    s=requests.Session(); s.cookies.update(ck)
    return s.get(url, headers={'user-agent':UA,'referer':BASE+'/'}, timeout=25).json()

pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
targets={'hit':None}
for a in pool:
    if a.get('uid')=='0000000000000001': targets['hit']=a
for i in (0,4,18):
    targets['idx%d'%i]=pool[i]
for name,a in targets.items():
    if not a: continue
    ck=cookies(a['cookie_string'])
    for url in ('https://accounts.doubao.com/passport/account/info/v2/?aid=497858',
                'https://www.doubao.com/passport/web/user/info/?aid=497858'):
        try:
            j=get(ck,url)
        except Exception as e:
            print(name,url,'ERR',e); continue
        d=str(j.get('data'))
        print('#####',name,url.split('/')[-1])
        print(json.dumps(j,ensure_ascii=False)[:2200])
        print()