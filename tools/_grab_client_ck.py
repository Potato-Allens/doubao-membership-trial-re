# -*- coding: utf-8 -*-
"""Pull live doubao cookies out of the running client (CDP 9224) -> durable pool file."""
import json, os, sys
from playwright.sync_api import sync_playwright

DEST = os.path.join(os.environ["CODEX_HOME"], "work", "doubao_yuan")

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9224", timeout=20000)
    ctx = b.contexts[0]
    ck = {}
    for c in ctx.cookies("https://www.doubao.com"):
        ck[c["name"]] = c["value"]
    pg = ctx.new_page()
    info = None
    try:
        info = pg.evaluate("""async()=>{const r=await fetch(
          'https://accounts.doubao.com/passport/account/info/v2/?aid=582478',
          {credentials:'include'});return (await r.json()).data}""")
    except Exception as e:
        info = {"err": str(e)[:80]}
    print("cookies", len(ck), "sessionid", "yes" if ck.get("sessionid") else "no")
    print("uid", (info or {}).get("user_id_str"), "name", (info or {}).get("screen_name"),
          "cc", (info or {}).get("country_code"))
    pool = [{"name": "client_live_%s" % ((info or {}).get("user_id_str") or "x"), "ck": ck}]
    json.dump(pool, open(os.path.join(DEST, "_client_pool.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("saved", os.path.join(DEST, "_client_pool.json"))
    pg.close()
