# -*- coding: utf-8 -*-
"""Capture every JS chunk the member page loads, then grep commerce endpoints / pricing keys."""
import json, re, time
from playwright.sync_api import sync_playwright
UA=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
js={}
with sync_playwright() as p:
    b=p.chromium.launch(channel="chrome",headless=True)
    ctx=b.new_context(viewport={"width":1440,"height":1000},locale="zh-CN",user_agent=UA)
    pg=ctx.new_page()
    def on_resp(r):
        try:
            ct=(r.headers or {}).get("content-type","")
        except Exception:
            return
        if ".js" in r.url.split("?")[0] or "javascript" in ct:
            try:
                t=r.text()
            except Exception:
                return
            if len(t)>200: js[r.url.split("?")[0]]=t
    pg.on("response",on_resp)
    for u in ("https://www.doubao.com/member/subscription","https://www.doubao.com/chat/"):
        try:
            pg.goto(u,wait_until="networkidle",timeout=60000)
            pg.mouse.wheel(0,3000); time.sleep(3)
        except Exception as e:
            print("nav err",u,str(e)[:60])
    b.close()
print("chunks",len(js),"bytes",sum(len(v) for v in js.values()))
blob="\n".join(js.values())
eps=sorted(set(re.findall(r'["\'`](/alice/commerce/[A-Za-z0-9_/\-]{3,60})["\'`]',blob)))
print("endpoints",len(eps))
for e in eps: print("  ",e)
keys=["dynamic_scene","first_purchase_price","trial_period_amount","is_eligible_for_intro_offer",
      "trial_stage","discount_total_price","entitlement_claim","has_history_paid_subscription",
      "qualification_id","intro_offer","dynamic_price"]
print("--- key hits ---")
for k in keys:
    n=blob.count(k)
    print("  %-34s %d"%(k,n))
    if n and n<40:
        for m in re.finditer(re.escape(k),blob):
            seg=blob[max(0,m.start()-120):m.start()+160].replace("\n"," ")
            print("      ...",seg[:260])
            break
json.dump(eps,open("_eps_all.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
open("_js_blob.txt","w",encoding="utf-8").write(blob)