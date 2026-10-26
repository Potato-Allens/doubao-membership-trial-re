# -*- coding: utf-8 -*-
import json, time
from playwright.sync_api import sync_playwright
raw=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
a=[x for x in raw if str(x.get("uid"))=="0000000000000001"][0]
ck=[]
for p in a["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); ck.append({"name":k.strip(),"value":v.strip(),"domain":".doubao.com","path":"/"})
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
caps=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1000},locale="zh-CN",user_agent=UA)
    ctx.add_cookies(ck)
    pg=ctx.new_page()
    def on_resp(r):
        if "/alice/commerce/sale/subscription/" in r.url and "overview" in r.url:
            try: caps.append(r.json())
            except Exception: pass
    pg.on("response",on_resp)
    for url in ("https://www.doubao.com/member/subscription","https://www.doubao.com/member"):
        try:
            pg.goto(url,wait_until="domcontentloaded",timeout=45000); time.sleep(6)
            t=pg.title(); body=pg.inner_text("body")[:600]
            print("==",url,"| title:",t)
            print("   body:",body.replace("\n"," | ")[:400])
            pg.screenshot(path="_shot_%s.png"%url.rstrip("/").split("/")[-1], full_page=False)
        except Exception as e:
            print("==",url,"ERR",str(e)[:70])
    if caps:
        cs=(caps[-1].get("data") or {}).get("current_subscription") or {}
        print("API end_time",cs.get("end_time"),time.strftime("%Y-%m-%d %H:%M:%S",time.localtime((cs.get("end_time") or 0)/1000)))
    b.close()
print("done")
