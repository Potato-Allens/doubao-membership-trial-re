# -*- coding: utf-8 -*-
"""Capture trade_confirm full request/response."""
import json, os, time
from playwright.sync_api import sync_playwright
o=json.load(open("_order_full.json",encoding="utf-8"))
url=o["credential"]["pay_url"]
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
cap={"req":None,"resp":None}
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900}, user_agent=UA, locale="zh-CN")
    pg=ctx.new_page()
    pg.on("request", lambda r: cap.__setitem__("req", {"u":r.url,"post":r.post_data}) if "trade_confirm" in r.url else None)
    def on_resp(r):
        if "trade_confirm" in r.url:
            try: body=r.text()
            except Exception: body="<bin>"
            cap["resp"]={"status":r.status,"ct":r.headers.get("content-type",""),
                         "loc":r.headers.get("location",""),"body":body}
    pg.on("response",on_resp)
    pg.goto(url, wait_until="commit", timeout=30000); time.sleep(5)
    for sel in ["text=支付宝","text=付款并开通"]:
        try: pg.locator(sel).first.click(timeout=6000); print("clicked",sel)
        except Exception as e: print("miss",sel,str(e)[:40])
        time.sleep(2)
    time.sleep(10)
    json.dump(cap,open("_cd_confirm2.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
    if cap["resp"]:
        print("STATUS",cap["resp"]["status"],"CT",cap["resp"]["ct"])
        print("LOC",cap["resp"]["loc"][:200])
        print("BODY",cap["resp"]["body"][:900])
    else:
        print("no trade_confirm captured")
    if cap["req"]: print("POST len",len(cap["req"]["post"] or ""))
    ctx.close(); b.close()
