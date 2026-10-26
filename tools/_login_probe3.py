# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900},locale="zh-CN",user_agent=UA)
    pg=ctx.new_page()
    pg.goto("https://www.doubao.com/chat/",wait_until="domcontentloaded",timeout=45000)
    time.sleep(4)
    pg.keyboard.press("Escape"); time.sleep(1)
    # close any modal via the X button (top-right inside dialog)
    for sel in ("button[aria-label*=关闭]","div[role=dialog] button:has(svg)","button:has-text('×')"):
        try:
            loc=pg.locator(sel)
            if loc.count():
                loc.first.click(timeout=2500); print("closed via",sel); break
        except Exception: pass
    time.sleep(1)
    # force-click 登录 by text
    try:
        pg.evaluate("""()=>{const els=[...document.querySelectorAll('button,div,span,a')];
          const t=els.filter(e=>e.children.length===0 && (e.innerText||'').trim()==='登录');
          if(t.length){t[0].click(); return 'js-click';} return 'none';}""")
        print("login click ok")
    except Exception as e: print("click err",str(e)[:60])
    time.sleep(6)
    info=pg.evaluate("""()=>{const o={canvas:[],iframe:[],img:[],text:document.body.innerText.slice(0,400)};
      document.querySelectorAll('canvas').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>40)o.canvas.push([Math.round(r.width)+'x'+Math.round(r.height)]);});
      document.querySelectorAll('iframe').forEach(e=>o.iframe.push((e.src||'').slice(0,110)));
      document.querySelectorAll('img').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>100)o.img.push([Math.round(r.width)+'x'+Math.round(r.height),(e.src||'').slice(0,70)]);});
      return o;}""")
    print("canvas",info["canvas"][:5]); print("iframe",info["iframe"][:5]); print("img",info["img"][:6])
    print("text:",info["text"][:260].replace("\n"," | "))
    pg.screenshot(path="_login_modal2.png")
    if info["canvas"]:
        pg.locator("canvas").first.screenshot(path="_login_qr.png"); print("saved _login_qr.png")
    b.close()