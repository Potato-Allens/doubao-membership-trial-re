# -*- coding: utf-8 -*-
import json
line=open("pool/live_intake.jsonl",encoding="utf-8").read().strip().splitlines()[-1]
uid,cks=line.split("|",1)
names=[p.split("=",1)[0].strip() for p in cks.split(";") if "=" in p]
print("uid",uid,"cookies",len(names))
print("lark/feishu:",[n for n in names if any(k in n.lower() for k in ("lark","feishu","suite"))])
print("sample:",names[:18])
# 10-14 cohort lark check
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
val={r["name"]:r for r in json.load(open("scan_val.json",encoding="utf-8"))}
import datetime
for i in range(212):
    r=val.get("trial_batch_212.json/accounts[%d]"%i) or {}
    ct=r.get("ct")
    if not ct: continue
    day=datetime.datetime.fromtimestamp(int(ct),datetime.timezone(datetime.timedelta(hours=8))).strftime("%m-%d")
    if day!="10-14": continue
    nm=[p.split("=",1)[0].strip() for p in raw[i]["cookie_string"].split(";") if "=" in p]
    lk=[n for n in nm if any(k in n.lower() for k in ("lark","feishu","suite"))]
    if lk: print("  10-14 idx",i,"uid",raw[i]["uid"],"lark",lk,"disc",r.get("disc"))