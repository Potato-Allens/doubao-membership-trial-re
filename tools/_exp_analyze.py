# -*- coding: utf-8 -*-
import json, datetime
rows=json.load(open("sub_landscape.json",encoding="utf-8"))
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
def ts(v):
    try: return datetime.datetime.fromtimestamp(int(v)/1000,datetime.timezone(datetime.timedelta(hours=8)))
    except: return None
print("total",len(rows))
exp=[]
for r in rows:
    e=ts(r.get("end")) if r.get("end") else None
    if e and e<now:
        exp.append((r["idx"],r.get("sku"),e.strftime("%Y-%m-%d %H:%M"),r.get("status"),r.get("price")))
print("expired subs:",len(exp))
for x in exp[:10]: print("  ",x)
print("\nodd sku rows:")
for r in rows:
    if r.get("sku") in ("","None") or (r.get("sku") is None and r.get("sub")):
        print("  ",r)
print("\nsub start/end sample (first 5 exp_work):")
n=0
for r in rows:
    if r.get("sku")=="doubao_personal_exp_work":
        s=ts(r.get("start")); e=ts(r.get("end"))
        print("   idx%-4s %s -> %s status=%s price=%s"%(r["idx"],s.strftime("%m-%d %H:%M") if s else None,
              e.strftime("%m-%d %H:%M") if e else None, r.get("status"), r.get("price")))
        n+=1
        if n>=5: break