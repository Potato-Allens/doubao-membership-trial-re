import json, base64, re, os

def b64d(x):
    x += '=' * (-len(x) % 4)
    return json.loads(base64.urlsafe_b64decode(x))

def cookies(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d

rows=[]
# live intake
try:
    for line in open('pool/live_intake.jsonl',encoding='utf-8'):
        line=line.strip()
        if not line: continue
        o=json.loads(line)
        rows.append(('live:'+str(o.get('uid')), o.get('cookie_string') or o.get('cookie') or ''))
except Exception as e: print('live err',e)
# batch pool
try:
    d=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))
    for i,a in enumerate(d['accounts']):
        rows.append(('idx%d:%s'%(i,a.get('uid')), a.get('cookie_string','')))
except Exception as e: print('batch err',e)

for name,cs in rows:
    ck=cookies(cs)
    lk=ck.get('LARK_SUITE_ACCESS_TOKEN')
    if not lk: continue
    try:
        payload=b64d(lk.split('.')[1])
    except Exception as e:
        print(name,'decode err',e); continue
    keep={k:payload.get(k) for k in ('aid','uid','doubao_uid','user_type','access_mode','unit','client_id','scope','tenant_create_source','tenant_biz_type')}
    print(name, json.dumps(keep,ensure_ascii=False))