import json,sys,io,websocket,urllib.request
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def targets(): return json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in targets() if 'doubao-chat/chat' in (x.get('url') or '')][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=30,suppress_origin=True)
mid=[0]
def send(m,p=None):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':m,'params':p or {}}))
    while True:
        r=json.loads(ws.recv())
        if r.get('id')==i: return r
def ev(e,awaitP=False):
    r=send('Runtime.evaluate',{'expression':e,'awaitPromise':awaitP,'returnByValue':True,'userGesture':True})
    res=r.get('result',{})
    if res.get('exceptionDetails'): return 'EXC '+json.dumps(res['exceptionDetails'])[:300]
    return res.get('result',{}).get('value')
raw=ev("localStorage.getItem('__tea_sdk_ab_version_582478')")
d=json.loads(raw)
data=d.get('data') or {}
print('experiments',len(data))
pat=('tri','mem','sub','vip','pay','incentive','campaign','activity','beta','pro','price','discount','elig','fission','invite','benefit','reward','task')
hit={k:v for k,v in data.items() if any(p in k.lower() for p in pat)}
print('matched',len(hit))
for k,v in list(hit.items())[:80]:
    print('%-52s %s'%(k,json.dumps(v,ensure_ascii=False)[:160]))
json.dump(d,open('client_ab.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
ws.close()