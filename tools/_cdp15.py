import json,sys,io,websocket,urllib.request,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
lst=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in lst if 'professional-beta' in (x.get('url') or '')][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=60,suppress_origin=True)
mid=[0]
def snd(m,p=None):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':m,'params':p or {}}))
    while True:
        r=json.loads(ws.recv())
        if r.get('id')==i: return r
snd('Network.enable'); snd('Page.enable'); snd('Page.reload',{'ignoreCache':True})
reqs={}; t0=time.time(); ws.settimeout(2)
while time.time()-t0<30:
    try: m=json.loads(ws.recv())
    except Exception: continue
    if m.get('method')=='Network.requestWillBeSent':
        reqs[m['params']['requestId']]=(m['params']['request']['url'],m['params']['request'].get('postData'))
print('total reqs',len(reqs))
for rid,(u,pd) in reqs.items():
    if any(k in u for k in ('/alice/','/samantha/','/commerce/')):
        print('\n###',u[:240]); print('  BODY:',(pd or '')[:260])
        try:
            b=snd('Network.getResponseBody',{'requestId':rid}).get('result',{}).get('body','')
            if len(b)<4000: print('  RESP:',b[:700])
        except Exception: pass
print('\n=== globals')
for expr in ("typeof __INITIAL_STATE__","typeof __NEXT_DATA__","JSON.stringify(Object.keys(window).filter(k=>k.startsWith('__')).slice(0,20))"):
    print(expr,'->',snd('Runtime.evaluate',{'expression':expr,'returnByValue':True})['result']['result'].get('value'))
ws.close()