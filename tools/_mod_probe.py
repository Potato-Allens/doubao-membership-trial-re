# -*- coding: utf-8 -*-
import json, datetime
d=json.load(open("scan_val.json",encoding="utf-8"))
by={r["name"]:r for r in d}
def day(r):
    ct=r.get("ct")
    return datetime.datetime.fromtimestamp(int(ct),datetime.timezone(datetime.timedelta(hours=8))).strftime("%m-%d") if ct else None
hits={130,163,171,193,202,204}
cohort=[]  # 10-21/10-22/10-14 accounts, hist False
for i in range(212):
    r=by.get("trial_batch_212.json/accounts[%d]"%i)
    if not r or r.get("code")!=0: continue
    dd=day(r)
    if dd in ("10-14","10-21","10-22") and not r.get("hist"):
        cohort.append((i,int(r["uid"]),i in hits))
print("cohort",len(cohort),"hits",sum(1 for c in cohort if c[2]))
best=[]
for m in range(2,201):
    buckets={}
    for i,u,h in cohort:
        buckets.setdefault(u%m,[0,0])[0 if h else 1]+=1
    for r,(hh,nn) in buckets.items():
        if hh>=4 and nn<=1:
            best.append((m,r,hh,nn))
print("strong rules (>=4 hits, <=1 fp):",best[:20])
best2=[]
for m in range(2,201):
    buckets={}
    for i,u,h in cohort:
        buckets.setdefault(u%m,[0,0])[0 if h else 1]+=1
    for r,(hh,nn) in buckets.items():
        if hh==5 and nn==0:
            best2.append((m,r))
print("exact 5/0:",best2[:20])
print("hits uid%100:",[(i,u%100) for i,u,h in cohort if h])
print("hits uid%10:",[(i,u%10) for i,u,h in cohort if h])