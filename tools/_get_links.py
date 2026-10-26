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
links=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1000},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck); pg=ctx.new_page()
    pg.goto("https://www.doubao.com/member/subscription",wait_until="networkidle",timeout=60000); time.sleep(4)
    links=pg.evaluate("[...document.querySelectorAll('a')].map(a=>[a.innerText.trim(),a.href]).filter(x=>x[1]&&!x[1].startsWith('javascript'))")
    b.close()
print("links",len(links))
for t,h in links:
    if any(k in (t+h) for k in ("协议","agreement","rule","条款")):
        print("  ",t[:24],"|",h[:120])
