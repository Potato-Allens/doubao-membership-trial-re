import json,sys,io,websocket,urllib.request,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
VER=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/version',timeout=5))
bws=websocket.create_connection(VER['webSocketDebuggerUrl'],timeout=40,suppress_origin=True)
mid=[0]
def snd(ws,m,p=None):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':m,'params':p or {}}))
    while True:
        r=json.loads(ws.recv())
        if r.get('id')==i: return r
r=snd(bws,'Target.createTarget',{'url':'https://www.doubao.com/member/subscription'})
tid=r['result']['targetId']; print('target',tid)
time.sleep(6)
lst=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in lst if x.get('id')==tid][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=40,suppress_origin=True)
snd(ws,'Network.enable'); snd(ws,'Page.enable')
reqs={}
t0=time.time(); ws.settimeout(2)
while time.time()-t0<25:
    try: m=json.loads(ws.recv())
    except Exception: continue
    if m.get('method')=='Network.requestWillBeSent':
        u=m['params']['request']['url']
        if '/alice/commerce/' in u:
            reqs[m['params']['requestId']]={'url':u,'method':m['params']['request']['method'],'post':m['params']['request'].get('postData')}
    elif m.get('method')=='Network.responseReceived':
        rid=m['params']['responseId'] if 'responseId' in m['params'] else m['params']['requestId']
        if rid in reqs:
            reqs[rid]['status']=m['params']['response']['status']
            reqs[rid]['ctype']=m['params']['response'].get('mimeType')
print('captured',len(reqs))
n=0
for rid,v in reqs.items():
    if '/sale/trade/init' in v['url'] or '/campaign/' in v['url'] or '/subscription/overview' in v['url']:
        body=''
        try:
            rb=snd(ws,'Network.getResponseBody',{'requestId':rid})
            body=(rb.get('result') or {}).get('body','')[:700]
        except Exception as e: body='ERR '+str(e)[:60]
        print('\n###',v['method'],v['url'][:260])
        print('  post:',(v.get('post') or '')[:300])
        print('  resp:',body)
        n+=1
        if n>=6: break
ws.close()