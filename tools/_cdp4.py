import json,sys,io,websocket,urllib.request
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def targets(): return json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in targets() if 'doubao-chat/chat' in (x.get('url') or '')][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=40,suppress_origin=True)
mid=[0]
def send(method,params=None):
    mid[0]+=1; i=mid[0]; ws.send(json.dumps({'id':i,'method':method,'params':params or {}}))
    while True:
        m=json.loads(ws.recv())
        if m.get('id')==i: return m
def ev(e,awaitP=True):
    r=send('Runtime.evaluate',{'expression':e,'awaitPromise':awaitP,'returnByValue':True,'userGesture':True})
    res=r.get('result',{})
    if res.get('exceptionDetails'): return 'EXC '+json.dumps(res['exceptionDetails'])[:200]
    return res.get('result',{}).get('value')
Q=("version_code=20800&language=zh&device_platform=web&doubao_device_platform=desktop"
   "&aid=582478&real_aid=582478&pkg_type=release_version&device_id=0000000000000002"
   "&pc_version=2.33.5&doubao_pc_version=2.33.5&region=CN&sys_region=CN"
   "&samantha_web=1&web_platform=desktop&use-olympus-account=1&runtime=web"
   "&runtime_version=3.42.4&client_platform=pc_client&chromium_version=147.0.7727.149")
vals=["pc_invite_entry","invite_entry","pc_guide","sidebar_invite","avatar","profile","profile_setting",
"setting","settings","menu_avatar","right_top","home","chat","toolbar","banner","toast","popup","push",
"activity","credit","points","task_center","taskcenter","benefit","fission","referral_entry","invite_friend",
"share","guide","onboarding","pc_client","pc_sidebar","sidebar_menu","user_menu","dropdown_menu","toolbar_invite"]
js='''(async()=>{const q=%s;const vals=%s;const out=[];for(const v of vals){try{const r=await fetch('https://www.doubao.com/samantha/fission/entrance?enter_from='+encodeURIComponent(v)+'&'+q,{credentials:'include'});const txt=await r.text();if(!txt.includes('671010000'))out.push(v+' => '+txt.slice(0,220));}catch(e){out.push(v+' ERR')}}return out.length?out.join('\\n'):'ALL 671010000'})()''' % (json.dumps(Q), json.dumps(vals))
print(ev(js))
ws.close()