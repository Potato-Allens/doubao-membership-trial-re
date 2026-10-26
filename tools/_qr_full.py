# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
full=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900},locale="zh-CN",user_agent=UA)
    pg=ctx.new_page()
    pg.on("request", lambda r: full.append(r.url) if "get_qrcode" in r.url else None)
    pg.goto("https://www.doubao.com/chat/",wait_until="domcontentloaded",timeout=45000)
    time.sleep(4); pg.keyboard.press("Escape"); time.sleep(1)
    try: pg.locator("button[aria-label*=关闭]").first.click(timeout=2000)
    except Exception: pass
    pg.evaluate("""()=>{const els=[...document.querySelectorAll('button,div,span,a')];
      const t=els.filter(e=>e.children.length===0 && (e.innerText||'').trim()==='登录'); if(t.length)t[0].click();}""")
    time.sleep(4)
    b.close()
for u in full[:2]:
    print(u)