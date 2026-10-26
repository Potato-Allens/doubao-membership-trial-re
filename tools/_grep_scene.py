# -*- coding: utf-8 -*-
import re, json, requests
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
s=requests.Session(); s.headers.update({"user-agent":UA})
pages=["https://www.doubao.com/member/subscription","https://www.doubao.com/chat/","https://www.doubao.com/member/quota-management"]
seen=set(); srcs=[]
for u in pages:
    try: h=s.get(u,timeout=25).text
    except Exception: continue
    for m in re.findall(r'<script[^>]+src="([^"]+)"',h):
        uu=m if m.startswith("http") else "https://www.doubao.com"+m
        if uu not in seen:
            seen.add(uu); srcs.append(uu)
print("scripts",len(srcs))
pat=re.compile(r'scene_key["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]{3,60})["\']')
found={}; total=0
for u in srcs[:60]:
    try: t=s.get(u,timeout=30).text
    except Exception: continue
    total+=len(t)
    for m in pat.finditer(t):
        found.setdefault(m.group(1),set()).add(u.rsplit("/",1)[-1][:20])
print("bytes",total,"keys",len(found))
for k in sorted(found): print("  ",k,"<-",list(found[k])[:2])
json.dump({k:list(v) for k,v in found.items()},open("_scene_keys.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)