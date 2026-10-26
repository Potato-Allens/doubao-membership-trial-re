# -*- coding: utf-8 -*-
"""Probe: reach the doubao login modal and screenshot whatever QR surface is there."""
import time
from playwright.sync_api import sync_playwright
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900},locale="zh-CN",user_agent=UA)
    pg=ctx.new_page()
    pg.goto("https://www.doubao.com/chat/",wait_until="domcontentloaded",timeout=45000)
    time.sleep(5)
    print("title",pg.title())
    txt=pg.inner_text("body")[:300].replace("\n"," | ")
    print("body:",txt)
    for sel in ("text=登录","text=立即登录","text=登录/注册"):
        try:
            el=pg.locator(sel).first
            if el.count() and el.is_visible():
                el.click(timeout=4000); print("clicked",sel); break
        except Exception as e:
            print("miss",sel,str(e)[:40])
    time.sleep(5)
    info=pg.evaluate("""()=>{const o={canvas:[],iframe:[],img:[],text:document.body.innerText.slice(0,300)};
      document.querySelectorAll('canvas').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>40)o.canvas.push([Math.round(r.width)+'x'+Math.round(r.height),Math.round(r.x),Math.round(r.y)]);});
      document.querySelectorAll('iframe').forEach(e=>o.iframe.push((e.src||'').slice(0,90)));
      document.querySelectorAll('img').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>80)o.img.push([Math.round(r.width)+'x'+Math.round(r.height),(e.src||'').slice(0,60)]);});
      return o;}""")
    print("canvas",info["canvas"][:6])
    print("iframe",info["iframe"][:4])
    print("img",info["img"][:6])
    print("text:",info["text"][:220].replace("\n"," | "))
    pg.screenshot(path="_login_modal.png",full_page=False)
    if info["canvas"]:
        try:
            pg.locator("canvas").first.screenshot(path="_login_qr.png")
            print("qr -> _login_qr.png")
        except Exception as e: print("qr shot err",str(e)[:60])
    b.close()