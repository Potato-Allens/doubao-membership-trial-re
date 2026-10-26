# -*- coding: utf-8 -*-
"""Dedicated Chrome on :9455, inject cookies, verify login + member state, leave window open."""
import json, os, subprocess, time, urllib.request
from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9455
PROF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_chrome_prof2")
RAW = json.load(open("pool/trial_batch_212.json", encoding="utf-8"))["accounts"]
A = [x for x in RAW if str(x.get("uid")) == "0000000000000001"][0]
PAIRS = [tuple(p.split("=", 1)) for p in A["cookie_string"].split(";") if "=" in p]
PAIRS = [(k.strip(), v.strip()) for k, v in PAIRS]

def up(port, tries=30):
    for _ in range(tries):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/json/version" % port, timeout=1) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(0.5)
    return None

if not up(PORT, 1):
    os.makedirs(PROF, exist_ok=True)
    subprocess.Popen([CHROME, "--remote-debugging-port=%d" % PORT, "--user-data-dir=" + PROF,
                      "--no-first-run", "--no-default-browser-check", "--start-maximized",
                      "--disable-blink-features=AutomationControlled", "about:blank"], close_fds=True)
    print("launched chrome on", PORT)
print("cdp:", (up(PORT) or {}).get("Browser"))

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % PORT)
    ctx = b.contexts[0]
    ctx.add_cookies([{"name": k, "value": v, "domain": ".doubao.com", "path": "/"} for k, v in PAIRS])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.goto("https://www.doubao.com/member/subscription", wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)
    uid = None
    try:
        r = pg.evaluate("""async (uid) => {
          const out={};
          let res = await fetch('/alice/profile/self',{method:'POST',
            headers:{'content-type':'application/json','agw-js-conv':'str'},
            body: JSON.stringify({visit_id: uid, avatar_format:'png'}), credentials:'include'});
          out.self = await res.json();
          res = await fetch('/alice/user/get_account_info',{method:'POST',
            headers:{'content-type':'application/json','agw-js-conv':'str'}, body:'{}', credentials:'include'});
          out.acct = await res.json();
          return out;
        }""", "0000000000000001")
        s = (r.get("self") or {}).get("data") or {}
        print("profile code:", (r.get("self") or {}).get("code"))
        print("uid:", s.get("user_id_str") or s.get("uid"), "| name:", s.get("name"), "| avatar:", bool(s.get("avatar_url")))
        ac = (r.get("acct") or {}).get("data") or {}
        print("account mobile:", ((ac.get("base_account_info") or {}).get("mobile")))
    except Exception as e:
        print("probe err", str(e)[:100])
    try:
        pg.locator("text=标准").first.click(timeout=8000); time.sleep(3)
    except Exception as e:
        print("tab miss", str(e)[:50])
    t = pg.inner_text("body")
    i = t.find("到期时间")
    print("到期文案:", t[i:i+24] if i >= 0 else "NOT FOUND")
    pg.screenshot(path="_shot_verify.png", full_page=False)
    print("url:", pg.url, "| title:", pg.title())
print("WINDOW_KEPT_OPEN")
