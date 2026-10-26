# -*- coding: utf-8 -*-
import json, time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    ctx=b.contexts[0]
    chat=next((x for x in ctx.pages if "doubao-chat" in x.url), None)
    print("chat target:", chat.url if chat else None)
    if chat:
        try:
            chat.reload(wait_until="domcontentloaded",timeout=45000)
        except Exception as e:
            print("reload err",str(e)[:70])
        time.sleep(9)
        print("url now:", chat.url[:90])
        try:
            txt=chat.inner_text("body")[:400].replace("\n"," | ")
            print("body:", txt)
        except Exception as e:
            print("body err",str(e)[:60])
        try:
            r=chat.evaluate("""async () => {
              const res=await fetch('https://www.doubao.com/alice/user/get_account_info',{method:'POST',
                headers:{'content-type':'application/json','agw-js-conv':'str'},body:'{}',credentials:'include'});
              return [res.status,(await res.text()).slice(0,180)];
            }""")
            print("api:",r)
        except Exception as e:
            print("api err",str(e)[:70])
        try:
            chat.screenshot(path="_shot_client_chat.png", timeout=20000); print("shot ok")
        except Exception as e:
            print("shot err",str(e)[:60])
    print("pages:",[x.url[:60] for x in ctx.pages])
print("DONE")
