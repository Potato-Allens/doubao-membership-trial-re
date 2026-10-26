# -*- coding: utf-8 -*-
import json, time, urllib.request
from playwright.sync_api import sync_playwright
try:
    print("port ok", bool(urllib.request.urlopen("http://127.0.0.1:9224/json/version",timeout=3).read()))
except Exception as e:
    print("PORT DEAD", e); raise SystemExit
RAW=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
A=[x for x in RAW if str(x.get("uid"))=="0000000000000001"][0]
PAIRS=[]
for p in A["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); PAIRS.append((k.strip(),v.strip()))
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    ctx=b.contexts[0]
    pg=next((x for x in ctx.pages if "client-login" in x.url), None)
    if not pg:
        print("no login page; pages:",[x.url[:60] for x in ctx.pages]); raise SystemExit
    print("target:", pg.url[:90])
    # 1) 看当前这个页面自己的 cookie 视图
    dc=pg.evaluate("document.cookie")
    names=sorted({x.split("=")[0] for x in dc.split("; ") if "=" in x})
    print("document.cookie before:",len(names), "has ttwid:", "ttwid" in names, "has uid_tt:", "uid_tt" in names)
    # 2) 页面级 CDP 写入（分区正确）
    cdp=ctx.new_cdp_session(pg)
    cookies=[{"name":k,"value":v,"domain":".doubao.com","path":"/","secure":True,"httpOnly":True,
              "sameSite":"Lax"} for k,v in PAIRS]
    try:
        r=cdp.send("Network.setCookies",{"cookies":cookies}); print("Network.setCookies ->", r)
    except Exception as e:
        print("setCookies err", str(e)[:100])
    # 3) 顺便用 Storage.setCookies（旧协议兼容）
    try:
        cdp.send("Storage.setCookies",{"cookies":[dict(c, expires=-1) for c in cookies]})
        print("Storage.setCookies ok")
    except Exception as e:
        print("Storage.setCookies err", str(e)[:80])
    dc2=pg.evaluate("document.cookie")
    n2=sorted({x.split("=")[0] for x in dc2.split("; ") if "=" in x})
    print("document.cookie after:",len(n2),"has ttwid:", "ttwid" in n2, "has uid_tt:", "uid_tt" in n2)
    pg.reload(wait_until="domcontentloaded",timeout=45000); time.sleep(8)
    print("url after reload:", pg.url[:100])
    try:
        r=pg.evaluate("""async () => {
          const out={};
          for (const ep of ['/alice/user/get_account_info','/alice/profile/self']) {
            const res=await fetch(ep,{method:'POST',headers:{'content-type':'application/json','agw-js-conv':'str'},
              body: ep.includes('profile')? JSON.stringify({visit_id:'0000000000000001',avatar_format:'png'}) : '{}',
              credentials:'include'});
            out[ep]=[res.status,(await res.text()).slice(0,200)];
          }
          return out;
        }""")
        for k,v in r.items(): print(" ",k,v)
    except Exception as e:
        print("eval err",str(e)[:80])
    print("pages:",[x.url[:60] for x in ctx.pages])
print("DONE")
