# -*- coding: utf-8 -*-
"""Capture the real member page flow for a given pool index: every /alice/commerce/ request+response."""
import json, sys, time
from playwright.sync_api import sync_playwright
IDX=int(sys.argv[1]) if len(sys.argv)>1 else 0
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
ck=[]
for p in raw[IDX]["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1)
        ck.append({"name":k.strip(),"value":v.strip(),"domain":".doubao.com","path":"/","expires":-1,
                   "httpOnly":False,"secure":True,"sameSite":"Lax"})
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
store={}
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1100},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck)
    pg=ctx.new_page()
    def on_req(r):
        if "/alice/commerce/" in r.url:
            store.setdefault(r.url.split("?")[0].split("/alice")[-1],[]).append(
                {"m":r.method,"post":(r.post_data or "")[:600],"q":r.url.split("?")[1][:300] if "?" in r.url else ""})
    def on_resp(r):
        if "/alice/commerce/" in r.url:
            try: t=r.text()
            except Exception: return
            k=r.url.split("?")[0].split("/alice")[-1]
            store.setdefault(k,[]).append({"RESP":t[:1200]})
    pg.on("request",on_req); pg.on("response",on_resp)
    pg.goto("https://www.doubao.com/member/subscription",wait_until="domcontentloaded",timeout=60000)
    time.sleep(8)
    try: body=pg.inner_text("body")
    except Exception: body=""
    print("=== BODY ===")
    print(body[:1200])
    try:
        pg.screenshot(path="_flow_%d.png"%IDX, full_page=False)
    except Exception: pass
    b.close()
print("=== REQUESTS ===")
for k,v in store.items():
    for it in v[:3]:
        if "RESP" in it:
            print("  <- %-52s %s"%(k,it["RESP"][:200]))
        else:
            print("  -> %-52s %s %s"%(k,it["post"][:150],("?q="+it["q"][:80]) if it["q"] else ""))
json.dump(store,open("_flow_%d.json"%IDX,"w",encoding="utf-8"),ensure_ascii=False,indent=1)