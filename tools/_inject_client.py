# -*- coding: utf-8 -*-
"""Inject cookie into Doubao desktop client (Electron CDP 9224) and verify login."""
import json, time
from playwright.sync_api import sync_playwright

RAW = json.load(open("pool/trial_batch_212.json", encoding="utf-8"))["accounts"]
A = [x for x in RAW if str(x.get("uid")) == "0000000000000001"][0]
PAIRS = []
for p in A["cookie_string"].split(";"):
    if "=" in p:
        k, v = p.split("=", 1); PAIRS.append((k.strip(), v.strip()))
print("src cookies", len(PAIRS))

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    print("contexts", len(b.contexts))
    ctx = b.contexts[0]
    print("pages:", [pg.url[:70] for pg in ctx.pages])
    ck = [{"name": k, "value": v, "domain": ".doubao.com", "path": "/",
           "secure": True, "sameSite": "Lax"} for k, v in PAIRS]
    ok = 0
    for c in ck:
        try:
            ctx.add_cookies([c]); ok += 1
        except Exception as e:
            print("fail", c["name"], str(e)[:60])
    print("cookies set", ok, "/", len(ck))
    got = {c["name"]: c["value"] for c in ctx.cookies() if c["name"] in ("sessionid","sid_tt","uid_tt","passport_csrf_token")}
    print("readback:", {k: len(v) for k, v in got.items()})
    tgt = next((pg for pg in ctx.pages if "client-login" in pg.url), None)
    if not tgt:
        print("login page not found"); 
    else:
        print("reloading", tgt.url[:90])
        tgt.reload(wait_until="domcontentloaded", timeout=45000)
        time.sleep(7)
        print("after url:", tgt.url[:100])
        try:
            body = tgt.inner_text("body")[:200].replace("\n", " | ")
            print("body:", body)
        except Exception as e:
            print("body err", str(e)[:60])
        try:
            tgt.screenshot(path="_shot_client_login.png")
        except Exception as e:
            print("shot err", str(e)[:60])
    print("--- all pages now ---")
    for pg in ctx.pages:
        print("  ", pg.url[:90])
print("DONE (client left running)")
