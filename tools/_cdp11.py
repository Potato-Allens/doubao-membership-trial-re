import json,sys,io,websocket,urllib.request,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
lst=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
cand=[x for x in lst if 'member' in (x.get('url') or '')]
print('cands',[ (x['url'],x['type']) for x in cand][:5])
t=cand[0] if cand else lst[0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=60,suppress_origin=True)
mid=[0]
def snd(m,p=None):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':m,'params':p or {}}))
    while True:
        r=json.loads(ws.recv())
        if r.get('id')==i: return r
snd('Network.enable'); snd('Page.enable'); snd('Runtime.enable')
print('url',snd('Runtime.evaluate',{'expression':'location.href','returnByValue':True})['result']['result'].get('value'))
snd('Page.reload',{'ignoreCache':True})
reqs={}; t0=time.time(); ws.settimeout(2)
while time.time()-t0<30:
    try: m=json.loads(ws.recv())
    except Exception: continue
    if m.get('method')=='Network.requestWillBeSent':
        u=m['params']['request']['url']
        if '/alice/' in u or '/samantha/' in u:
            reqs[m['params']['requestId']]={'url':u,'method':m['params']['request']['method'],'post':m['params']['request'].get('postData')}
print('captured',len(reqs))
n=0
for rid,v in reqs.items():
    if any(k in v['url'] for k in ('trade/init','campaign/','subscription/overview','member')):
        try: body=snd('Network.getResponseBody',{'requestId':rid})['result']['body'][:800]
        except Exception as e: body='ERR'
        print('\n###',v['method'],v['url'][:300]); print('  post:',(v.get('post') or '')[:300]); print('  resp:',body)
        n+=1
        if n>=5: break
if n==0:
    print('sample urls:')
    for rid,v in list(reqs.items())[:10]: print(' ',v['method'],v['url'][:180])
ws.close()