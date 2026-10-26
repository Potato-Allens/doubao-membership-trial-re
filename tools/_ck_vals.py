import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
for i in (120,4,57,71,75,78,86,114,0):
    c=ck(pool[i]['cookie_string'])
    keys=['is_staff_user','multi_sids','n_mh','odin_tt','iid','install_id','ttwid','s_v_web_id','webid','_tea_web_id','device_id','sid_tt','uid_tt','sessionid']
    print('idx%-4d'%i, {k:(c.get(k)[:28] if c.get(k) else None) for k in keys})