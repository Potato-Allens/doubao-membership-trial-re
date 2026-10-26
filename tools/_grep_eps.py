# -*- coding: utf-8 -*-
"""Grep doubao member-page JS bundles for subscription endpoints (cancel / agreement / auto_renew)."""
import re, json, requests
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
s=requests.Session(); s.headers.update({"user-agent":UA})
h=s.get("https://www.doubao.com/member/subscription",timeout=25).text
print("html len",len(h))
srcs=re.findall(r'<script[^>]+src="([^"]+)"',h)
srcs=[u if u.startswith("http") else "https://www.doubao.com"+u for u in srcs]
print("scripts",len(srcs))
pat=re.compile(r'["\'](/alice/commerce/[A-Za-z0-9_/\-]+)["\']')
kw=re.compile(r'cancel|unsubscribe|auto_renew|autoRenew|agreement|refund|close',re.I)
found={}
total=0
for u in srcs[:40]:
    try:
        t=s.get(u,timeout=30).text
    except Exception as e:
        continue
    total+=len(t)
    for m in pat.finditer(t):
        p=m.group(1)
        if kw.search(p): found.setdefault(p,set()).add(u.rsplit("/",1)[-1][:18])
    # 中文文案附近找接口
    for m in re.finditer(r'取消自动续费|关闭自动续费|解约',t):
        seg=t[max(0,m.start()-160):m.start()+160]
        for p in pat.findall(seg): found.setdefault(p,set()).add("TXT:"+u.rsplit("/",1)[-1][:14])
print("scanned bytes",total)
for p,v in sorted(found.items()):
    print("  ",p,"<-",list(v)[:3])
json.dump({k:list(v) for k,v in found.items()},open("_cancel_eps.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
