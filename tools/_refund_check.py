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
a=[x for x in pool if x.get('uid')=='0000000000000001'][0]
s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
for ep,b in (('/alice/commerce/sale/debook/check/',{'order_id':'0000000000000004'}),
             ('/alice/commerce/sale/debook/reasons/',{}),
             ('/alice/commerce/sale/subscription/status/',{'required_fields':[],'product_lines':[]})):
    try:
        j=s.post(BASE+ep,params=SCOPE,json=b,headers=H,timeout=20).json()
        print('###',ep); print(json.dumps(j,ensure_ascii=False)[:900]); print()
    except Exception as e:
        print(ep,'ERR',str(e)[:80])
    time.sleep(0.3)