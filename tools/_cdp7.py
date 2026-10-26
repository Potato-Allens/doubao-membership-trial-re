import json,sys,io,websocket,urllib.request
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def targets(): return json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in targets() if 'doubao-chat/chat' in (x.get('url') or '')][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=40,suppress_origin=True)
mid=[0]
def send(m,p=None):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':m,'params':p or {}}))
    while True:
        r=json.loads(ws.recv())
        if r.get('id')==i: return r
def ev(e,awaitP=True):
    r=send('Runtime.evaluate',{'expression':e,'awaitPromise':awaitP,'returnByValue':True,'userGesture':True})
    res=r.get('result',{})
    if res.get('exceptionDetails'): return 'EXC '+json.dumps(res['exceptionDetails'])[:250]
    return res.get('result',{}).get('value')
Q=("version_code=20800&language=zh&device_platform=web&doubao_device_platform=desktop"
   "&aid=582478&real_aid=582478&pkg_type=release_version&device_id=0000000000000002"
   "&pc_version=2.33.5&doubao_pc_version=2.33.5&region=CN&sys_region=CN"
   "&samantha_web=1&web_platform=desktop&use-olympus-account=1&runtime=web"
   "&runtime_version=3.42.4&client_platform=pc_client&chromium_version=147.0.7727.149")
js='''(async()=>{const q=%s;const out=[];
async function call(path,body){try{const r=await fetch('https://www.doubao.com'+path+'?'+q,{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:JSON.stringify(body)});out.push(path+' => '+r.status+'|'+(await r.text()).slice(0,700));}catch(e){out.push(path+' ERR '+e)}}
await call('/alice/ug/campaign/list/',{campaign_group_code:'pc_incentive_task_mvp_v3',scene:'pc_incentive_task'});
await call('/alice/ug/campaign/v3/detail/',{campaign_group_code:'pc_incentive_task_mvp_v3'});
await call('/alice/ug/campaign/list/',{campaign_group_code:'pc_incentive_task_mvp_v3',scene:'task_center'});
return out.join('\\n\\n')})()''' % json.dumps(Q)
print(ev(js))
ws.close()