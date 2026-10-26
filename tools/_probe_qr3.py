# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright
URLS=["https://www.doubao.com/flow-account/client-login/client-login-modal?afterLoginToUrl=&from_login=1&entry=app_main",
      "https://www.doubao.com/login",
      "https://www.doubao.com/passport/web/login/"]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    for u in URLS:
        ctx=b.new_context(viewport={"width":1100,"height":900}, locale="zh-CN",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
        pg=ctx.new_page()
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=40000); time.sleep(6)
            print("==",u[:60],"| title:",pg.title())
            info=pg.evaluate("""() => {
              const out={canvas:[],img:[],iframe:[],text:document.body.innerText.slice(0,220)};
              document.querySelectorAll('canvas').forEach(e=>{const r=e.getBoundingClientRect();
                if(r.width>60) out.canvas.push([Math.round(r.width)+'x'+Math.round(r.height)]);});
              document.querySelectorAll('img').forEach(e=>{const r=e.getBoundingClientRect();
                if(r.width>100) out.img.push([Math.round(r.width)+'x'+Math.round(r.height),(e.src||'').slice(0,50)]);});
              document.querySelectorAll('iframe').forEach(e=>out.iframe.push((e.src||'').slice(0,70)));
              return out;
            }""")
            print("   text:",info["text"].replace("\n"," | ")[:200])
            print("   canvas:",info["canvas"][:5]," img:",info["img"][:4]," iframe:",info["iframe"][:3])
            if info["canvas"]:
                pg.locator("canvas").first.screenshot(path="_qr_try.png")
                print("   -> _qr_try.png", pg.locator("canvas").first.bounding_box())
                ctx.close(); break
            pg.screenshot(path="_qr_try_page.png")
        except Exception as e:
            print("==",u[:60],"ERR",str(e)[:60])
        ctx.close()
    b.close()
