# -*- coding: utf-8 -*-
import json, urllib.parse, collections
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
def ck(i):
    d={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); d[k.strip()]=v.strip()
    return d
HIT=120  # uid 0000000000000001
rows=[]
for i in range(212):
    c=ck(i)
    src=c.get("flow_account_sync_event")
    s=None
    if src:
        try: s=json.loads(urllib.parse.unquote(src)).get("source")
        except Exception: s=src[:60]
    rows.append((i, raw[i].get("uid"), s))
cnt=collections.Counter(r[2] for r in rows)
print("source dist:", dict(cnt))
print("\nHIT row:", [r for r in rows if r[0]==HIT])
print("\nrows with source containing doubao.com/member or act:")
for r in rows:
    if r[2] and ("member" in r[2] or "/act" in r[2] or "campaign" in r[2]):
        print("  ",r)