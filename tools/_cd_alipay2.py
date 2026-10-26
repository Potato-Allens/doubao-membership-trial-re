# -*- coding: utf-8 -*-
import base64, json, os, re, time
from playwright.sync_api import sync_playwright
o=json.load(open("_order_full.json",encoding="utf-8"))
url=o["credential"]["pay_url"]
OUT=os.path.dirname(os.path.abspath(__file__))
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
net=[]
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":1280,"height":900}, user_agent=UA, locale="zh-CN")
    pg=ctx.new_page()
    def on_resp(r):
        u=r.url
        try:
            ct=r.headers.get("content-type","")
            if "json" in ct or any(k in u for k in ("cashdesk","alipay","/api/")):
                t=r.text()
                if t and len(t)>30:
                    net.append({"url":u[:200],"body":t[:900]})
        except Exception:
            pass
    pg.on("response",on_resp)
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(3)
    try: pg.locator("text=支付宝").first.click(timeout=5000)
    except Exception as e: print("alipay click",str(e)[:60])
    time.sleep(1.5)
    try: pg.locator("text=付款并开通").first.click(timeout=5000)
    except Exception as e: print("pay click",str(e)[:60])
    time.sleep(8)
    final=pg.url
    print("final", final[:400])
    m=re.search(r"[?&]process=([A-Za-z0-9_\-=]+)", final)
    if m:
        raw=m.group(1)
        for pad in ("","=", "=="):
            try:
                dec=base64.b64decode(raw+pad).decode("utf-8","replace")
                print("PROCESS decoded:", dec[:600]); break
            except Exception: pass
    json.dump(net,open(os.path.join(OUT,"_cd_net.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print("net entries",len(net))
    for n in net:
        bd=n["body"]
        if any(k in bd for k in ("qr","alipay","scheme","precreate","code_url")):
            print("---",n["url"][:120]); print("   ",bd[:400].replace("\n"," "))
    try:
        pg.screenshot(path=os.path.join(OUT,"_cd_desktop_3.png"), timeout=8000)
        print("shot ok")
    except Exception as e:
        print("shot fail", str(e)[:60])
    ctx.close(); b.close()
