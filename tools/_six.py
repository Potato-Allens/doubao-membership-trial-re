# -*- coding: utf-8 -*-
import json, datetime
d=json.load(open("scan_val.json",encoding="utf-8"))
by={r["name"]:r for r in d}
for i in (130,163,171,193,202,204,120,79,117):
    r=by.get("trial_batch_212.json/accounts[%d]"%i)
    if not r: print(i,"missing"); continue
    ct=r.get("ct")
    dstr=datetime.datetime.fromtimestamp(int(ct),datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y-%m-%d") if ct else None
    print("idx %-4d code=%-9s ct=%s hist=%s disc=%s trial=%s btn=%s uid=%s"%(
        i,r.get("code"),dstr,r.get("hist"),r.get("disc"),
        json.dumps(r.get("trial"),ensure_ascii=False) if r.get("trial") else None,r.get("btn"),r.get("uid")))