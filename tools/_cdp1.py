import json,sys,io,websocket,urllib.request,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def targets(): return json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=None
for x in targets():
    if 'doubao-chat/chat' in (x.get('url') or ''): t=x;break
if not t:
    for x in targets():
        if x.get('type')=='page' and 'doubao-launcher' in (x.get('url') or ''): t=x;break
print('target',t['url'])
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=25,suppress_origin=True)
mid=[0]
def send(method,params=None,wait=True):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':method,'params':params or {}}))
    if not wait: return
    while True:
        m=json.loads(ws.recv())
        if m.get('id')==i: return m
def ev(expr,awaitP=True):
    r=send('Runtime.evaluate',{'expression':expr,'awaitPromise':awaitP,'returnByValue':True,'userGesture':True})
    if not r: return None
    res=r.get('result',{})
    if res.get('exceptionDetails'): return 'EXC '+json.dumps(res['exceptionDetails'])[:200]
    return res.get('result',{}).get('value')
print('href',ev('location.href'))
print('title',ev('document.title'))
print('texts',ev('''(()=>{const k=['免费试用','邀请','试用','会员','福利'];const out=[];document.querySelectorAll('*').forEach(e=>{if(e.children.length===0){const t=(e.textContent||'').trim();if(t&&t.length<40&&k.some(x=>t.includes(x)))out.push(t)}});return JSON.stringify([...new Set(out)].slice(0,40))})()'''))
print('fetch ent',ev('''(async()=>{try{const r=await fetch('https://www.doubao.com/samantha/fission/entrance?enter_from=profile_setting',{credentials:'include'});return r.status+'|'+(await r.text()).slice(0,400)}catch(e){return 'ERR '+e}})()'''))
ws.close()