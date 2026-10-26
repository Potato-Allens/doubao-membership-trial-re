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
def ev(expr,awaitP=True):
    r=send('Runtime.evaluate',{'expression':expr,'awaitPromise':awaitP,'returnByValue':True,'userGesture':True})
    res=r.get('result',{})
    if res.get('exceptionDetails'): return 'EXC '+json.dumps(res['exceptionDetails'])[:300]
    return res.get('result',{}).get('value')
Q=("version_code=20800&language=zh&device_platform=web&doubao_device_platform=desktop"
   "&aid=582478&real_aid=582478&pkg_type=release_version&device_id=0000000000000002"
   "&pc_version=2.33.5&doubao_pc_version=2.33.5&region=CN&sys_region=CN"
   "&samantha_web=1&web_platform=desktop&use-olympus-account=1&runtime=web"
   "&runtime_version=3.42.4&client_platform=pc_client&chromium_version=147.0.7727.149")
js_ent='''(async()=>{const q=%s;const out=[];for(const ef of ['profile_setting','sidebar','invite','settings','']){
 try{const r=await fetch('https://www.doubao.com/samantha/fission/entrance?enter_from='+encodeURIComponent(ef)+'&'+q,{credentials:'include'});out.push(ef+' => '+r.status+'|'+(await r.text()).slice(0,300));}catch(e){out.push(ef+' ERR '+e)}}return out.join('\\n')})()''' % json.dumps(Q)
print('=== entrance'); print(ev(js_ent))
js_home='''(async()=>{try{const r=await fetch('https://www.doubao.com/samantha/fission/home_page?activity_id=&'+%s,{credentials:'include'});return r.status+'|'+(await r.text()).slice(0,600)}catch(e){return 'ERR '+e}})()''' % json.dumps(Q)
print('=== home_page'); print(ev(js_home))
js_trial='''(async()=>{try{const r=await fetch('https://www.doubao.com/alice/commerce/sale/campaign/trial/init/?'+%s,{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:''});return r.status+'|'+(await r.text()).slice(0,600)}catch(e){return 'ERR '+e}})()''' % json.dumps(Q)
print('=== trial init'); print(ev(js_trial))
js_page='''(async()=>{try{const r=await fetch('https://www.doubao.com/alice/commerce/sale/campaign/page/query/?'+%s,{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:'{}'});return r.status+'|'+(await r.text()).slice(0,600)}catch(e){return 'ERR '+e}})()''' % json.dumps(Q)
print('=== page query'); print(ev(js_page))
ws.close()