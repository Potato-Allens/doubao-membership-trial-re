# -*- coding: utf-8 -*-
import json, time
from playwright.sync_api import sync_playwright
RAW=json.load(open("pool/trial_batch_212.json",encoding="utf-8"))["accounts"]
A=[x for x in RAW if str(x.get("uid"))=="0000000000000001"][0]
PAIRS={}
for p in A["cookie_string"].split(";"):
    if "=" in p:
        k,v=p.split("=",1); PAIRS[k.strip()]=v.strip()
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    ctx=b.contexts[0]
    cdp=ctx.new_cdp_session(ctx.pages[0]) if ctx.pages else None
    got=ctx.cookies()
    print("browser cookies:",len(got))
    for c in got:
        if c["name"] in ("sessionid","sessionid_ss","sid_tt","uid_tt","passport_csrf_token","ttwid"):
            src=PAIRS.get(c["name"],"")
            print("  %-22s dom=%-16s len=%-4d src_len=%-4d match=%s"%(
                c["name"],c.get("domain"),len(c["value"]),len(src),c["value"]==src))
    pg=ctx.pages[0]
    print("url:",pg.url)
    dc=pg.evaluate("document.cookie")
    names=sorted({x.split("=")[0] for x in dc.split("; ") if "=" in x})
    print("document.cookie names:",len(names))
    print("  has sessionid:", "sessionid" in names, " has sid_tt:", "sid_tt" in names)
    try:
        r=pg.evaluate("""async () => {
          const out={};
          for (const ep of ['/alice/profile/self','/alice/user/get_account_info']) {
            const res=await fetch(ep,{method:'POST',headers:{'content-type':'application/json','agw-js-conv':'str'},
              body:'{}',credentials:'include'});
            out[ep]=[res.status, await res.text()];
          }
          return out;
        }""")
        for k,v in r.items(): print(k, v[0], v[1][:180])
    except Exception as e:
        print("fetch err",str(e)[:90])
