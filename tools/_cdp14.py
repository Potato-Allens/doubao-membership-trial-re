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
for url in ('https://www.doubao.com/member/professional-beta',):
    r=snd(bws,'Target.createTarget',{'url':url}); tid=r['result']['targetId']; print('open',url,tid)
time.sleep(8)
lst=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in lst if 'professional-beta' in (x.get('url') or '')][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=60,suppress_origin=True)
snd(ws,'Network.enable'); snd(ws,'Page.enable'); snd(ws,'Runtime.enable')
time.sleep(1)
href=snd(ws,'Runtime.evaluate',{'expression':'location.href+" | "+document.title','returnByValue':True})['result']['result'].get('value')
print('page',href)
reqs={}; t0=time.time(); ws.settimeout(2)
while time.time()-t0<20:
    try: m=json.loads(ws.recv())
    except Exception: continue
    if m.get('method')=='Network.requestWillBeSent':
        u=m['params']['request']['url']
        if '/alice/commerce/' in u: reqs[m['params']['requestId']]=(u,m['params']['request'].get('postData'))
print('commerce reqs',len(reqs))
for rid,(u,pd) in reqs.items():
    print('\n###',u.split('?')[0]); print('  BODY:',(pd or '')[:500])
    try:
        b=snd(ws,'Network.getResponseBody',{'requestId':rid}).get('result',{}).get('body','')
        print('  RESP:',b[:700])
    except Exception: pass
txt=snd(ws,'Runtime.evaluate',{'expression':"document.body.innerText.slice(0,600)",'returnByValue':True})['result']['result'].get('value')
print('\n=== TEXT ===\n',txt)
ws.close()