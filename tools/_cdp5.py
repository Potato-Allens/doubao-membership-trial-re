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
    if res.get('exceptionDetails'): return 'EXC '+json.dumps(res['exceptionDetails'])[:200]
    return res.get('result',{}).get('value')
print('keys', ev("JSON.stringify(Object.keys(window).filter(k=>/samantha|doubao|sdk|api|request|fission|abtest|webpack|chunk/i.test(k)).slice(0,80))"))
print('wp', ev("JSON.stringify(Object.keys(window).filter(k=>k.startsWith('webpackChunk')).slice(0,10))"))
print('ls keys', ev("JSON.stringify(Object.keys(localStorage).filter(k=>/exp|ab|trial|member|sub|fission|activity|campaign/i.test(k)).slice(0,60))"))
print('ls sample', ev("(()=>{const o={};for(const k of Object.keys(localStorage)){if(/exp|ab_|abtest|trial|member|subs|fission|activity|campaign|eligib/i.test(k))o[k]=(localStorage.getItem(k)||'').slice(0,180)}return JSON.stringify(o).slice(0,1500)})()"))
ws.close()