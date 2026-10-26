# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
def dump(pg,tag):
    info=pg.evaluate("""()=>{const o={canvas:[],iframe:[],img:[],text:document.body.innerText.slice(0,500)};
      document.querySelectorAll('canvas').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>30)o.canvas.push([Math.round(r.width)+'x'+Math.round(r.height)]);});
      document.querySelectorAll('iframe').forEach(e=>o.iframe.push((e.src||'').slice(0,120)));
      document.querySelectorAll('img').forEach(e=>{const r=e.getBoundingClientRect();if(r.width>90)o.img.push([Math.round(r.width)+'x'+Math.round(r.height),(e.src||'').slice(0,80)]);});
      return o;}""")
    print("[%s] url=%s"%(tag,pg.url[:110]))
    print("   canvas",info["canvas"][:4],"iframe",info["iframe"][:3])
    print("   img",info["img"][:4])
    print("   text:",info["text"][:240].replace("\n"," | "))
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900},locale="zh-CN",user_agent=UA)
    pg=ctx.new_page()
    pg.goto("https://www.doubao.com/chat/",wait_until="domcontentloaded",timeout=45000)
    time.sleep(4); pg.keyboard.press("Escape"); time.sleep(1)
    try: pg.locator("button[aria-label*=关闭]").first.click(timeout=2500)
    except Exception: pass
    pg.evaluate("""()=>{const els=[...document.querySelectorAll('button,div,span,a')];
      const t=els.filter(e=>e.children.length===0 && (e.innerText||'').trim()==='登录'); if(t.length)t[0].click();}""")
    time.sleep(4); dump(pg,"modal")
    # 飞书一键登录
    try:
        pg.locator("text=飞书账号一键登录").first.click(timeout=5000); print("clicked feishu")
    except Exception as e: print("feishu click err",str(e)[:60])
    time.sleep(6); dump(pg,"after-feishu"); pg.screenshot(path="_login_feishu.png")
    for c in ctx.pages: print("page:",c.url[:120])
    b.close()