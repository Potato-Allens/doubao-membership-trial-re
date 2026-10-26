# -*- coding: utf-8 -*-
"""Capture the full trade_confirm response (headers+body) to find the alipay payload."""
import json, os, time
from playwright.sync_api import sync_playwright
o=json.load(open("_order_full.json",encoding="utf-8"))
url=o["credential"]["pay_url"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
hits=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900}, user_agent=UA, locale="zh-CN")
    pg=ctx.new_page()
    def on_resp(r):
        if "gateway-cashier2" in r.url:
            try: body=r.text()
            except Exception: body="<bin>"
            hits.append({"status":r.status,"url":r.url[:150],
                         "loc":r.headers.get("location",""),
                         "ct":r.headers.get("content-type",""),
                         "body":body[:1500]})
    pg.on("response",on_resp)
    pg.goto(url, wait_until="commit", timeout=30000); time.sleep(5)
    for sel in ["text=支付宝","text=付款并开通"]:
        try: pg.locator(sel).first.click(timeout=6000)
        except Exception: pass
        time.sleep(2)
    time.sleep(8)
    print("final", pg.url[:200])
    json.dump(hits,open("_cd_confirm.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
    for h in hits:
        print("===", h["status"], h["url"][:90])
        if h["loc"]: print("   LOC", h["loc"][:200])
        print("   ", h["body"][:400].replace("\n"," "))
    ctx.close(); b.close()
