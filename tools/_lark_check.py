# -*- coding: utf-8 -*-
import json, collections, datetime
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
d=json.load(open("scan_val.json",encoding="utf-8")); by={r["name"]:r for r in d}
def ck(i):
    out={}
    for p in raw[i]["cookie_string"].split(";"):
        if "=" in p:
            k,v=p.split("=",1); out[k.strip()]=v.strip()
    return out
hits={130,163,171,193,202,204}
def day(i):
    r=by.get("trial_batch_212.json/accounts[%d]"%i) or {}
    ct=r.get("ct")
    return datetime.datetime.fromtimestamp(int(ct),datetime.timezone(datetime.timedelta(hours=8))).strftime("%m-%d") if ct else None
feishu=collections.Counter()
for i in range(212):
    c=ck(i)
    names=" ".join(c.keys()).lower()
    has=any(k in names for k in ("lark","feishu","suite"))
    feishu[(has,i in hits)]+=1
print("feishu-cookie cross (has_cookie, is_hit):",dict(feishu))
print()
for i in sorted(hits):
    c=ck(i)
    lk=[k for k in c if any(x in k.lower() for x in ("lark","feishu","suite"))]
    print("hit idx %-3d day %-5s lark-cookies=%s n=%d"%(i,day(i),lk,len(c)))
print()
# which accounts have lark cookies at all
withk=[i for i in range(212) if any(x in " ".join(ck(i).keys()).lower() for x in ("lark","feishu","suite"))]
print("accounts with lark/feishu cookies:",len(withk),withk[:30])