import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
hit=ck(pool[120]['cookie_string'])
print('HIT keys (%d):'%len(hit), sorted(hit))
for i in (4,47,53,57,75,78,86,114):
    c=ck(pool[i]['cookie_string'])
    extra_hit=[k for k in hit if k not in c]
    extra_neg=[k for k in c if k not in hit]
    print('idx%-4d n=%-3d only_hit=%s only_neg=%s'%(i,len(c),extra_hit,extra_neg))