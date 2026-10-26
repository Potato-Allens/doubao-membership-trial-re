# -*- coding: utf-8 -*-
import json
d=json.load(open("scan_212.json",encoding="utf-8"))
for r in d:
    if (r.get("disc") or 0)>0:
        print(json.dumps(r,ensure_ascii=False,indent=1))