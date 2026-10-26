import json,sys,io,websocket,urllib.request,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def targets(): return json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in targets() if 'doubao-chat/chat' in (x.get('url') or '')][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=30,suppress_origin=True)
mid=[0]
def send(method,params=None):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':method,'params':params or {}}))
    while True:
        m=json.loads(ws.recv())
        if m.get('id')==i: return m
send('Network.enable')
send('Page.enable')
send('Page.reload',{'ignoreCache':False})
urls=[]
t0=time.time()
ws.settimeout(3)
while time.time()-t0<25:
    try: m=json.loads(ws.recv())
    except Exception: continue
    if m.get('method')=='Network.requestWillBeSent':
        u=m['params']['request']['url']
        if '/samantha/' in u or '/alice/' in u:
            urls.append(u)
seen=set(); n=0
for u in urls:
    base=u.split('?')[0]
    if base in seen: continue
    seen.add(base); n+=1
    print(u[:420]); print()
    if n>=8: break
print('total',len(urls))
ws.close()