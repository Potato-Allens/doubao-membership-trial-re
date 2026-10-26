import json,sys,io,websocket,urllib.request,itertools
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def targets(): return json.load(urllib.request.urlopen('http://127.0.0.1:9224/json/list',timeout=5))
t=[x for x in targets() if 'doubao-chat/chat' in (x.get('url') or '')][0]
ws=websocket.create_connection(t['webSocketDebuggerUrl'],timeout=60,suppress_origin=True)
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
roots=['incentive_task_mvp','new_user_campaign','free_subs_download_pc','member_trial','trial','1yuan_trial',
 'one_yuan_trial','first_purchase_trial','professional_beta','member_beta','member_campaign','subscription_trial',
 'subs_trial','std_trial','personal_trial','member_1yuan','pc_trial','daily_task','checkin','credit_task',
 'invite_task','fission','new_user','newcomer','retention','winback','recall','gift_subs','free_subs','member_offer']
prefixes=['pc_','doubao_','doubao_pc_','member_','subs_','ug_','alice_','']
cands=set()
for r in roots:
    for p in prefixes: cands.add(p+r)
for i in range(1,6):
    cands.add('pc_incentive_task_mvp_v%d'%i); cands.add('incentive_task_mvp_v%d'%i)
cands|= {'pc_incentive_task','pc_task_center','pc_credit_task','pc_daily_checkin','doubao_pc_incentive_task_mvp_v3'}
cands=sorted(c for c in cands if c)
print('candidates',len(cands))
js='''(async()=>{const q=%s;const cs=%s;const hits=[];const other=[];
for(const c of cs){try{const r=await fetch('https://www.doubao.com/alice/ug/campaign/list/?'+q,{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:JSON.stringify({campaign_group_code:c,scene:'pc_incentive_task'})});const t=await r.text();
if(!t.includes('campaign not found')){if(t.includes('"code":0')){hits.push(c+' => '+t.slice(0,600))}else{other.push(c+' => '+t.slice(0,200))}}
}catch(e){}}
return JSON.stringify({hits:hits.slice(0,10),other:other.slice(0,10),n:cs.length})})()''' % (json.dumps(Q), json.dumps(cands))
print(ev(js,True))
ws.close()