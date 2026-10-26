# -*- coding: utf-8 -*-
import json, re, time, requests
from playwright.sync_api import sync_playwright
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
a=[x for x in raw if str(x.get("uid"))=="0000000000000001"][0]
ck=[]
for p in a["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); ck.append({"name":k.strip(),"value":v.strip(),"domain":".doubao.com","path":"/"})
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
js=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1000},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck); pg=ctx.new_page()
    pg.goto("https://www.doubao.com/member/quota-management",wait_until="networkidle",timeout=60000); time.sleep(3)
    js=pg.evaluate("performance.getEntriesByType('resource').filter(e=>e.name.includes('.js')).map(e=>e.name)")
    b.close()
print("chunks",len(js))
s=requests.Session()
seen=0
for u in js:
    try: t=s.get(u,headers={"user-agent":UA},timeout=30).text
    except Exception: continue
    if "subscription/cancel" in t:
        seen+=1
        i=t.find("subscription/cancel")
        print("### FILE",u.rsplit("/",1)[-1],"len",len(t),"hits",t.count("subscription/cancel"))
        seg=t[max(0,i-1200):i+800]
        print(seg.replace("\n"," ")[:2000])
        print()
        open("_cancel_ctx.txt","w",encoding="utf-8").write(t)
        if seen>=2: break
print("files with endpoint:",seen)
