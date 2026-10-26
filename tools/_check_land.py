import json, os, time
from playwright.sync_api import sync_playwright
info=json.load(open("_alipay_pay.json",encoding="utf-8"))
UA=("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome", headless=True)
    ctx=b.new_context(viewport={"width":390,"height":844}, user_agent=UA, is_mobile=True,
                      has_touch=True, device_scale_factor=2, locale="zh-CN")
    pg=ctx.new_page()
    seen=[]
    pg.on("request", lambda r: seen.append(r.url[:110]))
    pg.goto(info["short"], wait_until="domcontentloaded", timeout=40000)
    time.sleep(6)
    print("final", pg.url[:180])
    try: print("text", pg.inner_text("body")[:200].replace("\n"," | "))
    except Exception as e: print("text err", str(e)[:50])
    pg.screenshot(path="_qr_land.png", full_page=True)
    print("chain", seen[-4:])
    ctx.close(); b.close()
