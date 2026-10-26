# -*- coding: utf-8 -*-
"""Desktop cashdesk: pick Alipay and capture the precreate / qr payload."""
import json, os, re, time
from playwright.sync_api import sync_playwright

o=json.load(open("_order_full.json",encoding="utf-8"))
url=o["credential"]["pay_url"]
OUT=os.path.dirname(os.path.abspath(__file__))
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/147.0.0.0 Safari/537.36")
net=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900}, user_agent=UA, locale="zh-CN")
    pg=ctx.new_page()
    def on_resp(r):
        u=r.url
        if any(k in u for k in ("cashdesk","/api/","alipay","pay")):
            try:
                t=r.text()
            except Exception:
                return
            if len(t)>40:
                net.append({"url":u[:160],"ct":r.headers.get("content-type",""),"body":t[:700]})
    pg.on("response",on_resp)
    pg.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(3)
    print("A url", pg.url[:130])
    pg.screenshot(path=os.path.join(OUT,"_cd_desktop_1.png"), full_page=True)
    # click alipay
    for sel in ["text=支付宝","text=支付宝支付"]:
        try:
            pg.locator(sel).first.click(timeout=4000); print("clicked",sel); break
        except Exception as e:
            print("miss",sel,str(e)[:50])
    time.sleep(2)
    pg.screenshot(path=os.path.join(OUT,"_cd_desktop_2.png"), full_page=True)
    for sel in ["text=付款并开通","text=立即支付","text=确认支付"]:
        try:
            pg.locator(sel).first.click(timeout=4000); print("clicked",sel); break
        except Exception as e:
            print("miss",sel,str(e)[:50])
    time.sleep(6)
    print("B url", pg.url[:200])
    pg.screenshot(path=os.path.join(OUT,"_cd_desktop_3.png"), full_page=True)
    body=pg.inner_text("body")[:300].replace("\n"," | ")
    print("B text", body)
    for n in net[-8:]:
        print("NET", n["url"][:110], "|", n["body"][:200].replace("\n"," "))
    json.dump(net[-25:],open(os.path.join(OUT,"_cd_net.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    ctx.close(); b.close()
