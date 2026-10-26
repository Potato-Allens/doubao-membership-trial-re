# -*- coding: utf-8 -*-
"""Render the tp-pay cashdesk on a mobile profile and dump what it shows."""
import json, os, time
from playwright.sync_api import sync_playwright

o=json.load(open("_order_full.json",encoding="utf-8"))
url=o["credential"]["pay_url"]
OUT=os.path.dirname(os.path.abspath(__file__))
UA=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":390,"height":844}, user_agent=UA,
                      device_scale_factor=2, is_mobile=True, has_touch=True,
                      locale="zh-CN", timezone_id="Asia/Shanghai")
    pg=ctx.new_page()
    pg.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(4)
    print("url", pg.url[:140])
    print("title", pg.title())
    txt=pg.inner_text("body")[:400].replace("\n"," | ")
    print("text", txt)
    els=pg.evaluate("""()=>{
      const out=[];
      document.querySelectorAll('img,canvas,svg').forEach(e=>{
        const r=e.getBoundingClientRect();
        out.push({tag:e.tagName,w:Math.round(r.width),h:Math.round(r.height),
                  src:(e.tagName==='IMG'?(e.src||'').slice(0,80):'')});
      });
      return out.filter(x=>x.w>40&&x.h>40).slice(0,12)}""")
    print("media", json.dumps(els,ensure_ascii=False))
    pg.screenshot(path=os.path.join(OUT,"_cashdesk.png"), full_page=True)
    print("shot -> _cashdesk.png")
    ctx.close(); b.close()
