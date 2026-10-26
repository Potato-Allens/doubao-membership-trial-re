# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900}, locale="zh-CN",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
    pg=ctx.new_page()
    pg.goto("https://www.doubao.com/chat/", wait_until="domcontentloaded", timeout=45000); time.sleep(5)
    for sel in ["text=登录", "button:has-text('登录')", "[class*=login]"]:
        try:
            pg.locator(sel).first.click(timeout=6000); print("clicked", sel); break
        except Exception as e: print("miss", sel, str(e)[:50])
    time.sleep(5)
    info=pg.evaluate("""() => {
      const out={canvas:[],img:[],text:document.body.innerText.slice(0,300)};
      document.querySelectorAll('canvas').forEach(e=>{const r=e.getBoundingClientRect();
        if(r.width>60) out.canvas.push([Math.round(r.width)+'x'+Math.round(r.height), e.className||'']);});
      document.querySelectorAll('img').forEach(e=>{const r=e.getBoundingClientRect();
        if(r.width>100&&r.height>100) out.img.push([Math.round(r.width)+'x'+Math.round(r.height),(e.src||'').slice(0,70)]);});
      return out;
    }""")
    print("text:", info["text"].replace("\n"," | ")[:260])
    print("canvas:", info["canvas"][:6])
    print("img:", info["img"][:6])
    pg.screenshot(path="_login_page.png")
    # 尝试单独截 canvas
    try:
        c=pg.locator("canvas").first
        if c.count()>0:
            c.screenshot(path="_login_qr.png"); print("qr canvas shot -> _login_qr.png", c.bounding_box())
    except Exception as e: print("canvas shot err", str(e)[:60])
    b.close()
