# -*- coding: utf-8 -*-
"""Collect every JS chunk loaded by the subscription page, grep for cancel/unsign endpoints."""
import json, re, time, requests
from playwright.sync_api import sync_playwright
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
a=[x for x in raw if str(x.get("uid"))=="0000000000000001"][0]
ck=[]
for p in a["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); ck.append({"name":k.strip(),"value":v.strip(),"domain":".doubao.com","path":"/"})
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
jsurls=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1000},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck); pg=ctx.new_page()
    pg.goto("https://www.doubao.com/member/subscription",wait_until="networkidle",timeout=60000); time.sleep(4)
    jsurls=pg.evaluate("performance.getEntriesByType('resource').filter(e=>e.name.includes('.js')).map(e=>e.name)")
    b.close()
print("js chunks",len(jsurls))
s=requests.Session(); s.headers.update({"user-agent":UA}) if False else None
s=requests.Session()
pat=re.compile(r'["\'](/alice/[A-Za-z0-9_/\-]+)["\']')
hits={}; total=0; txt_hits=[]
for u in jsurls:
    try: t=s.get(u,headers={"user-agent":UA},timeout=30).text
    except Exception: continue
    total+=len(t)
    for m in pat.finditer(t):
        p=m.group(1)
        if re.search(r'cancel|unsign|unsubscribe|close|terminate|refund',p,re.I):
            hits.setdefault(p,0); hits[p]+=1
    for m in re.finditer(r'取消自动续费|关闭自动续费|管理自动续费|解约',t):
        txt_hits.append((u.rsplit('/',1)[-1][:24], t[max(0,m.start()-200):m.start()+200]))
print("bytes",total)
print("--- cancel-ish endpoints ---")
for p,c in sorted(hits.items()): print("  ",p,c)
print("--- chinese txt hits",len(txt_hits))
for f,seg in txt_hits[:6]:
    print("  [%s] %s"%(f,seg.replace("\n"," ")[:260]))
open("_js_hits.txt","w",encoding="utf-8").write(json.dumps({"eps":hits,"txt":[t for t in txt_hits[:20]]},ensure_ascii=False,indent=1))
