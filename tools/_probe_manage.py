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
reqs=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1200},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck); pg=ctx.new_page()
    pg.on("request", lambda r: reqs.append({"m":r.method,"u":r.url.split("?")[0],"post":(r.post_data or "")[:300]}) if "/alice/" in r.url else None)
    pg.goto("https://www.doubao.com/member/quota-management",wait_until="networkidle",timeout=60000); time.sleep(4)
    txt=pg.inner_text("body")
    print("--- BODY (前1800字) ---")
    print(txt[:1800])
    print("--- 关键文案位置 ---")
    for kw in ("自动续费","续费","取消","解约","到期","订阅管理","关闭"):
        i=txt.find(kw)
        print("[%s] %s"%(kw, txt[max(0,i-50):i+90].replace("\n"," | ") if i>=0 else "NOT FOUND"))
    pg.screenshot(path="_shot_quota.png", full_page=True)
    print("--- alice endpoints ---")
    seen=set()
    for r in reqs:
        k=(r["m"],r["u"])
        if k in seen: continue
        seen.add(k); print(r["m"], r["u"].replace("https://www.doubao.com",""), r["post"][:140])
    b.close()
