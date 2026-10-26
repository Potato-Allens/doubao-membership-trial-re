# -*- coding: utf-8 -*-
import json
for f in ("scan_212.json",):
    d=json.load(open(f,encoding="utf-8"))
    print(f,len(d))
    hits=[r for r in d if r.get("disc")==6700]
    print(" hits",len(hits))
    for h in hits: print("   ",h.get("name"),h.get("uid"),h.get("disc"),h.get("btn"),json.dumps(h.get("trial"),ensure_ascii=False))
    print(" disc>0:",[(r.get("name"),r.get("disc")) for r in d if (r.get("disc") or 0)>0])