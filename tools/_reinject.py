# -*- coding: utf-8 -*-
import json, time
from playwright.sync_api import sync_playwright
RAW=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
A=[x for x in RAW if str(x.get("uid"))=="0000000000000001"][0]
PAIRS=[]
for p in A["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); PAIRS.append((k.strip(),v.strip()))
print("cookies",len(PAIRS))
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    ctx=b.contexts[0]
    print("pages:",[x.url[:50] for x in ctx.pages])
    pg=next((x for x in ctx.pages if "doubao-chat" in x.url), ctx.pages[0])
    cdp=ctx.new_cdp_session(pg)
    c=[{"name":k,"value":v,"domain":".doubao.com","path":"/","secure":True,"httpOnly":True,"sameSite":"Lax"} for k,v in PAIRS]
    cdp.send("Network.setCookies",{"cookies":c})
    print("setCookies ok")
    # 顺便去一个 doubao.com 页面确认
    pg.goto("https://www.doubao.com/blank", wait_until="domcontentloaded", timeout=45000)
    time.sleep(3)
    r=pg.evaluate("""async () => {
      const out={};
      for (const ep of ['/alice/user/get_account_info','/alice/commerce/sale/subscription/status/']) {
        const res=await fetch(ep,{method:'POST',headers:{'content-type':'application/json','agw-js-conv':'str'},body:'{}',credentials:'include'});
        out[ep]=[res.status,(await res.text()).slice(0,150)];
      }
      return out;
    }""")
    for k,v in r.items(): print(k,v)
    # 回到客户端聊天页
    pg.goto("chrome://doubao-chat/chat/", wait_until="domcontentloaded", timeout=45000)
    time.sleep(8)
    t=pg.inner_text("body")[:260].replace("\n"," | ")
    print("chat body:", t)
    print("url:", pg.url)
print("DONE")
