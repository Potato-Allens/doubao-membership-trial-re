import json,sys,io,websocket,urllib.request,time,re
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
snd('Network.enable'); snd('Page.enable')
snd('Page.reload',{'ignoreCache':True})
reqs={}; t0=time.time(); ws.settimeout(2)
while time.time()-t0<35:
    try: m=json.loads(ws.recv())
    except Exception: continue
    if m.get('method')=='Network.requestWillBeSent':
        u=m['params']['request']['url']
        if '/alice/' in u or '/samantha/' in u: reqs[m['params']['requestId']]=u
print('reqs',len(reqs))
KW=['campaign_group_code','activity_id','eligibility','trial','campaign_id','exp_','beta_activity']
found=0
for rid,u in reqs.items():
    try:
        b=snd('Network.getResponseBody',{'requestId':rid}).get('result',{}).get('body','')
    except Exception: continue
    if len(b)>300000: continue
    for k in KW:
        i=b.find(k)
        if i>=0 and found<12:
            print('\n###',u.split('?')[0])
            print('  ',b[max(0,i-180):i+260].replace('\n',' ')[:440])
            found+=1
            break
print('found',found)
ws.close()