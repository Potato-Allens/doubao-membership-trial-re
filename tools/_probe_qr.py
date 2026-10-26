# -*- coding: utf-8 -*-
"""探测登录页的二维码元素"""
import json, time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900}, locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
    pg=ctx.new_page()
    for url in ("https://www.doubao.com/chat/","https://www.doubao.com/"):
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=45000); time.sleep(6)
            print("==",url,"| title:",pg.title())
            n=pg.evaluate("""() => {
              const out=[];
              document.querySelectorAll('canvas,img').forEach(e=>{
                const r=e.getBoundingClientRect();
                if(r.width>80&&r.height>80) out.push([e.tagName,Math.round(r.width)+'x'+Math.round(r.height),
                   (e.className||'').toString().slice(0,40), (e.src||'').slice(0,60)]);
              });
              return out;
            }""")
            print("  big canvas/img:",n[:8])
            t=pg.inner_text("body")[:200].replace("\n"," | ")
            print("  body:",t)
            if "扫码" in t or "登录" in t:
                pg.screenshot(path="_probe_login.png", full_page=False)
                print("  shot -> _probe_login.png")
                break
        except Exception as e:
            print("==",url,"ERR",str(e)[:70])
    b.close()
