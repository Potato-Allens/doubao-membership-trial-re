# -*- coding: utf-8 -*-
"""生成可注入的 cookie JSON 数组（Playwright / Puppeteer / Selenium / CDP），并实测注入验证。"""
import json, os, time
EXP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export")
state = json.load(open(os.path.join(EXP, "0000000000000001.state.json"), encoding="utf-8"))["cookies"]
CANON = ["device_id","iid","install_id","s_v_web_id","webid","_tea_web_id","ttwid",
         "passport_csrf_token","passport_csrf_token_default","multi_sids","odin_tt","n_mh",
         "sid_guard","uid_tt","uid_tt_ss","sid_tt","sessionid","sessionid_ss",
         "session_tlb_tag","is_staff_user","has_biz_token","sid_ucp_v1","ssid_ucp_v1"]

def norm(c):
    d = c.get("domain") or ".doubao.com"
    if not d.startswith("."):
        d = "." + d.lstrip(".")
    exp = c.get("expires")
    try: exp = int(exp)
    except Exception: exp = -1
    if exp is not None and exp < 0: exp = -1
    ss = c.get("sameSite") or "Lax"
    if ss.lower() == "none": ss = "None"
    elif ss.lower() == "strict": ss = "Strict"
    else: ss = "Lax"
    return {"name": c["name"], "value": c["value"], "domain": d, "path": c.get("path") or "/",
            "expires": exp, "httpOnly": bool(c.get("httpOnly")), "secure": bool(c.get("secure")),
            "sameSite": ss}

full = [norm(c) for c in state]
by = {c["name"]: c for c in full}
slim = [by[k] for k in CANON if k in by]

def dump(name, obj):
    p = os.path.join(EXP, name)
    json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("  %-34s %6d bytes  %d cookies" % (name, os.path.getsize(p), len(obj) if isinstance(obj, list) else -1))
    return p

print("== 生成 ==")
dump("ck_array_slim.json", slim)          # Playwright/Puppeteer 直接 add_cookies(array)
dump("ck_array_full.json", full)

# Selenium: expires -> expiry, 去掉 sameSite
sel = [{"name": c["name"], "value": c["value"], "domain": c["domain"].lstrip("."),
        "path": c["path"], "expiry": (c["expires"] if c["expires"] > 0 else None),
        "secure": c["secure"], "httpOnly": c["httpOnly"]} for c in slim]
dump("ck_array_selenium.json", sel)

# CDP Network.setCookie: 用 url 字段更稳
cdp = [{"name": c["name"], "value": c["value"], "url": "https://www.doubao.com",
        "path": c["path"], "secure": True, "httpOnly": c["httpOnly"],
        "sameSite": c["sameSite"]} for c in slim]
dump("ck_array_cdp.json", cdp)

# ---- 实测：Playwright 新开浏览器注入 slim 数组 ----
print("\n== 注入验证（headless chrome）==")
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    ctx = b.new_context()
    ctx.add_cookies(slim)
    pg = ctx.new_page()
    pg.goto("https://www.doubao.com/blank", wait_until="domcontentloaded", timeout=45000)
    r = pg.evaluate("""async () => {
      const a = await fetch('/alice/user/get_account_info', {method:'POST',
        headers:{'content-type':'application/json','agw-js-conv':'str'}, body:'{}', credentials:'include'});
      const b = await fetch('/alice/commerce/sale/subscription/overview/', {method:'POST',
        headers:{'content-type':'application/json','agw-js-conv':'str'}, body:'{}', credentials:'include'});
      return [await a.text(), await b.text()];
    }""")
    print("  account:", r[0][:120])
    try:
        ov = json.loads(r[1]); cs = (ov.get("data") or {}).get("current_subscription") or {}
        end = cs.get("end_time")
        print("  sub    :", cs.get("sku_key"), "| end:",
              time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end/1000)) if end else None)
    except Exception as e:
        print("  sub parse err", str(e)[:60])
    b.close()
print("\n== OK ==")
