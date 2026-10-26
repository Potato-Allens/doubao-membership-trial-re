# -*- coding: utf-8 -*-
import json, time
from playwright.sync_api import sync_playwright
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
a=[x for x in raw if str(x.get("uid"))=="0000000000000001"][0]
ck=[]
for p in a["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); ck.append({"name":k.strip(),"value":v.strip(),"domain":".doubao.com","path":"/"})
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
caps=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1000},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck)
    pg=ctx.new_page()
    pg.on("response", lambda r: caps.append((r.url, r.status)) if "subscription/overview" in r.url else None)
    pg.goto("https://www.doubao.com/member/subscription",wait_until="domcontentloaded",timeout=45000); time.sleep(5)
    for sel in ["text=标准"]:
        try:
            pg.locator(sel).first.click(timeout=8000); print("clicked",sel); time.sleep(4)
        except Exception as e: print("miss",sel,str(e)[:60])
    txt=pg.inner_text("body")
    print("--- BODY ---"); print(txt[:1200])
    pg.screenshot(path="_shot_std.png", full_page=True)
    print("--- API calls ---"); print(caps[:6])
    b.close()
