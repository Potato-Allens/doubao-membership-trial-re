# -*- coding: utf-8 -*-
import json, time
from playwright.sync_api import sync_playwright
RAW=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
A=[x for x in RAW if str(x.get("uid"))=="0000000000000001"][0]
PAIRS=[]
for p in A["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); PAIRS.append((k.strip(),v.strip()))
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    ctx=b.contexts[0]
    # 同时写 .doubao.com 与 host-only www.doubao.com
    for dom in (".doubao.com","www.doubao.com","doubao.com"):
        try:
            ctx.add_cookies([{"name":k,"value":v,"domain":dom,"path":"/","secure":True,"sameSite":"Lax"} for k,v in PAIRS])
        except Exception as e:
            print("set",dom,"err",str(e)[:60])
    print("cookies in ctx:",len(ctx.cookies()))
    tgt=next((pg for pg in ctx.pages if "client-login" in pg.url),None)
    hits=[]
    def on_resp(r):
        u=r.url
        if any(k in u for k in ("passport","login","account","sso","session")):
            try: body=r.text()[:300]
            except Exception: body="<bin>"
            hits.append((r.status,u[:110],body.replace("\n"," ")[:200]))
    tgt.on("response",on_resp)
    tgt.reload(wait_until="domcontentloaded",timeout=45000); time.sleep(8)
    print("url:",tgt.url[:110])
    print("--- 登录相关请求 ---")
    for s,u,bd in hits[:14]: print(" %s %s\n     %s"%(s,u,bd))
    print("--- page fetch 探测 ---")
    try:
        r=tgt.evaluate("""async () => {
          const tries=['/passport/web/account/info/?aid=582478','/alice/user/get_account_info'];
          const out={};
          for(const ep of tries){
            try{ const res=await fetch(ep,{method:'POST',headers:{'content-type':'application/json'},body:'{}',credentials:'include'});
                 out[ep]=[res.status,(await res.text()).slice(0,160)]; }
            catch(e){ out[ep]=['ERR',String(e).slice(0,80)]; }
          }
          return out;
        }""")
        for k,v in r.items(): print(" ",k,v)
    except Exception as e:
        print(" eval err",str(e)[:80])
print("DONE")
