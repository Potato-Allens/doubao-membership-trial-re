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
reqs=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1000},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck)
    pg=ctx.new_page()
    def on_req(r):
        if "/alice/" in r.url or "commerce" in r.url:
            reqs.append({"m":r.method,"u":r.url.split("?")[0],"post":(r.post_data or "")[:400]})
    pg.on("request",on_req)
    pg.goto("https://www.doubao.com/member/subscription",wait_until="domcontentloaded",timeout=45000); time.sleep(6)
    try: pg.locator("text=标准").first.click(timeout=8000); time.sleep(3)
    except Exception as e: print("tab",str(e)[:50])
    txt=pg.inner_text("body")
    for kw in ("自动续费","续费","取消","管理","解约","到期时间"):
        i=txt.find(kw)
        print("[%s] %s" % (kw, (txt[max(0,i-40):i+80].replace("\n"," | ") if i>=0 else "NOT FOUND")))
    pg.screenshot(path="_shot_member2.png", full_page=True)
    print("--- endpoints ---")
    seen=set()
    for r in reqs:
        key=(r["m"],r["u"])
        if key in seen: continue
        seen.add(key)
        print(r["m"], r["u"].replace("https://www.doubao.com",""), r["post"][:120])
    b.close()
