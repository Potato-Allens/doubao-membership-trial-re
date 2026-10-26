# -*- coding: utf-8 -*-
import json, os, time
from playwright.sync_api import sync_playwright
o=json.load(open("_order_full.json",encoding="utf-8"))
url=o["credential"]["pay_url"]
OUT=os.path.dirname(os.path.abspath(__file__))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
reqs=[]; resp=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900}, user_agent=UA, locale="zh-CN")
    pg=ctx.new_page()
    pg.on("request", lambda r: reqs.append({"m":r.method,"u":r.url[:220],"post":(r.post_data or "")[:400]}))
    def on_resp(r):
        try:
            ct=r.headers.get("content-type","")
            if "json" in ct:
                resp.append({"u":r.url[:220],"b":r.text()[:700]})
        except Exception: pass
    pg.on("response",on_resp)
    ok=False
    for i in range(3):
        try:
            pg.goto(url, wait_until="commit", timeout=30000); ok=True; break
        except Exception as e:
            print("goto retry",i,str(e)[:60]); time.sleep(3)
    if not ok:
        print("goto failed"); raise SystemExit(1)
    time.sleep(5)
    print("A", pg.url[:120])
    for sel in ["text=支付宝","text=付款并开通"]:
        try: pg.locator(sel).first.click(timeout=6000); print("clicked",sel)
        except Exception as e: print("miss",sel,str(e)[:50])
        time.sleep(2)
    time.sleep(10)
    print("B", pg.url[:300])
    json.dump({"reqs":reqs,"resp":resp},open(os.path.join(OUT,"_cd_net.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print("reqs",len(reqs),"resp",len(resp))
    for r in resp[-12:]:
        print("R", r["u"][:110], "|", r["b"][:200].replace("\n"," "))
    ctx.close(); b.close()
