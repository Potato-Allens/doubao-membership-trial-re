# -*- coding: utf-8 -*-
"""Find the Feishu login URL/QR behind the doubao login modal."""
import time, json
from playwright.sync_api import sync_playwright
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
urls=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900},locale="zh-CN",user_agent=UA)
    ctx.on("page", lambda pg: (print("NEWPAGE", pg.url[:120]), urls.append(pg.url)))
    pg=ctx.new_page()
    pg.on("request", lambda r: urls.append(r.url) if any(k in r.url for k in ("feishu","lark","passport","login","oauth","sso")) else None)
    pg.goto("https://www.doubao.com/chat/",wait_until="domcontentloaded",timeout=45000)
    time.sleep(4); pg.keyboard.press("Escape"); time.sleep(1)
    try: pg.locator("button[aria-label*=关闭]").first.click(timeout=2000)
    except Exception: pass
    pg.evaluate("""()=>{const els=[...document.querySelectorAll('button,div,span,a')];
      const t=els.filter(e=>e.children.length===0 && (e.innerText||'').trim()==='登录'); if(t.length)t[0].click();}""")
    time.sleep(4)
    try:
        pg.locator("text=飞书账号一键登录").first.click(timeout=5000)
        print("clicked")
    except Exception as e: print("click err",str(e)[:80])
    time.sleep(8)
    print("pages:",[x.url[:130] for x in ctx.pages])
    print("--- interesting urls ---")
    seen=set()
    for u in urls:
        if u in seen: continue
        seen.add(u)
        print("  ",u[:160])
    for i,x in enumerate(ctx.pages):
        try: x.screenshot(path="_fs_page_%d.png"%i)
        except Exception: pass
    b.close()