# -*- coding: utf-8 -*-
"""Record subscription/cancel requests from the Doubao desktop client (CDP 9224)."""
import json, os, sys, time
from playwright.sync_api import sync_playwright
LOG=os.path.join(os.path.dirname(os.path.abspath(__file__)),"_cancel_rec.log")
KEY=("subscription","cancel","agreement","order","trade")
def log(m):
    line="[%s] %s"%(time.strftime("%H:%M:%S"),m)
    with open(LOG,"a",encoding="utf-8") as f: f.write(line+"\n")
    print(line,flush=True)
def attach(pg):
    def on_req(r):
        u=r.url
        if not any(k in u for k in KEY): return
        try: post=r.post_data or ""
        except Exception: post=""
        if post or "cancel" in u or "agreement" in u:
            log("REQ %s %s\n     POST: %s" % (r.method,u,post[:600]))
    def on_resp(r):
        u=r.url
        if not any(k in u for k in KEY): return
        if "cancel" in u or "agreement" in u or "subscription" in u:
            try: body=r.text()[:400]
            except Exception: body="<bin>"
            log("RESP %s %s\n     %s" % (r.status,u[:110],body.replace("\n"," ")))
    pg.on("request",on_req); pg.on("response",on_resp)
mins=int(sys.argv[1]) if len(sys.argv)>1 else 25
log("recorder start for %d min (client cdp 9224)"%mins)
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    for ctx in b.contexts:
        for pg in ctx.pages: attach(pg)
        ctx.on("page", lambda pg: (log("NEW PAGE %s"%pg.url[:80]), attach(pg)))
    log("attached %d pages"%sum(len(c.pages) for c in b.contexts))
    end=time.time()+mins*60
    while time.time()<end:
        time.sleep(5)
    log("recorder end")
