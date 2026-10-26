# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
hits=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900},locale="zh-CN",user_agent=UA)
    pg=ctx.new_page()
    def on_resp(r):
        if "get_qrcode" in r.url or "check_qrconnect" in r.url:
            try: body=r.text()[:600]
            except Exception: body=""
            hits.append((r.url, body))
    pg.on("response", on_resp)
    pg.goto("https://www.doubao.com/chat/",wait_until="domcontentloaded",timeout=45000)
    time.sleep(4); pg.keyboard.press("Escape"); time.sleep(1)
    try: pg.locator("button[aria-label*=关闭]").first.click(timeout=2000)
    except Exception: pass
    pg.evaluate("""()=>{const els=[...document.querySelectorAll('button,div,span,a')];
      const t=els.filter(e=>e.children.length===0 && (e.innerText||'').trim()==='登录'); if(t.length)t[0].click();}""")
    time.sleep(3)
    try: pg.locator("text=飞书账号一键登录").first.click(timeout=5000)
    except Exception: pass
    time.sleep(5)
    # QR element?
    info=pg.evaluate("""()=>{const o={bg:[],img:[],canvas:[],text:document.body.innerText.slice(-500)};
      document.querySelectorAll('div,span,img,canvas').forEach(e=>{const s=getComputedStyle(e);
        const r=e.getBoundingClientRect();
        if(r.width>120&&r.width<400&&((s.backgroundImage||'').includes('data:image'))) o.bg.push([Math.round(r.width),s.backgroundImage.slice(0,60)]);
        if(e.tagName==='IMG'&&r.width>120) o.img.push([Math.round(r.width),e.src.slice(0,80)]);
        if(e.tagName==='CANVAS') o.canvas.push([Math.round(r.width)]);});
      return o;}""")
    print("QR info:", json.dumps(info,ensure_ascii=False)[:900])
    b.close()
for u,body in hits[:6]:
    print("URL:",u[:400])
    print("BODY:",body[:400])
    print("-"*60)