# -*- coding: utf-8 -*-
import json, datetime, collections
scan={r["idx"]:r for r in json.load(open("scan_rotate.json",encoding="utf-8"))}
val={r["name"]:r for r in json.load(open("scan_val.json",encoding="utf-8"))}
sub=json.load(open("sub_landscape.json",encoding="utf-8"))
def day(i):
    r=val.get("trial_batch_212.json/accounts[%d]"%i) or {}
    ct=r.get("ct")
    return datetime.datetime.fromtimestamp(int(ct),datetime.timezone(datetime.timedelta(hours=8))).strftime("%m-%d") if ct else "?"
tab=collections.Counter((day(r["idx"]), bool(r["sub"]), r["sku"]) for r in sub)
for k in sorted(tab,key=str): print(k,tab[k])
print()
starts=[(r["idx"],day(r["idx"]),datetime.datetime.fromtimestamp(int(r["start"])/1000,datetime.timezone(datetime.timedelta(hours=8))).strftime("%m-%d %H:%M")) for r in sub if r.get("start")]
print("start-time sample:",starts[:8])
print("start days:",collections.Counter(s[2][:5] for s in starts))