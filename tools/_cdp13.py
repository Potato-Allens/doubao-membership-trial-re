import json,sys,io,websocket,urllib.request,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
lst=json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in lst if 'member/subscription' in (x.get('url') or '')][0]
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
        u=m['params']['request']['url']
        if '/marketing/' in u or 'subscribe/init' in u:
            reqs[m['params']['requestId']]=(u,m['params']['request'].get('postData'))
for rid,(u,pd) in reqs.items():
    print('###',u.split('?')[0]); print('  BODY:',(pd or '')[:600])
    try:
        b=snd('Network.getResponseBody',{'requestId':rid}).get('result',{}).get('body','')
        print('  RESP:',b[:600])
    except Exception: pass
    print()
ws.close()