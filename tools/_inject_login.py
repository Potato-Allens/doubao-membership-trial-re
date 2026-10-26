# -*- coding: utf-8 -*-
"""Launch a dedicated Chrome (CDP 9333), inject the account cookies, navigate, verify, leave open."""
import json, os, subprocess, time, urllib.request
from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_chrome_prof")
RAW = json.load(open("pool/trial_batch_212.json", encoding="utf-8"))["accounts"]
A = [x for x in RAW if str(x.get("uid")) == "0000000000000001"][0]
PAIRS = []
for p in A["cookie_string"].split(";"):
    if "=" in p:
        k, v = p.split("=", 1); PAIRS.append((k.strip(), v.strip()))

def cdp_up(port=9333, tries=40):
    for _ in range(tries):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/json/version" % port, timeout=1) as r:
                return json.loads(r.read().decode())
        except Exception:
            time.sleep(0.5)
    return None

if not cdp_up(9333, 2):
    os.makedirs(PROF, exist_ok=True)
    args = [CHROME, "--remote-debugging-port=9333", "--user-data-dir=" + PROF,
            "--no-first-run", "--no-default-browser-check", "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "about:blank"]
    subprocess.Popen(args, close_fds=True)
    print("chrome launched")
else:
    print("chrome already on 9333")
v = cdp_up(9333)
print("cdp", (v or {}).get("Browser"))

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9333")
    ctx = b.contexts[0]
    cookies = [{"name": k, "value": q, "domain": ".doubao.com", "path": "/"} for k, q in PAIRS]
    ok = 0
    for c in cookies:
        try:
            ctx.add_cookies([c]); ok += 1
        except Exception as e:
            print("cookie fail", c["name"], str(e)[:50])
    print("cookies set %d/%d" % (ok, len(cookies)))
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.goto("https://www.doubao.com/member/subscription", wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)
    print("title:", pg.title())
    try:
        info = pg.evaluate("""async () => {
          const r = await fetch('/alice/profile/self', {method:'POST',
            headers:{'content-type':'application/json','agw-js-conv':'str'},
            body:'{}', credentials:'include'});
          return await r.json();
        }""")
        d = info.get("data") or {}
        print("profile uid:", d.get("user_id_str") or d.get("uid_str") or d.get("uid") or "?",
              "| name:", d.get("name") or d.get("screen_name") or d.get("nickname") or "?")
        print("profile code:", info.get("code"))
    except Exception as e:
        print("profile err", str(e)[:80])
    body = pg.inner_text("body")[:300].replace("\n", " | ")
    print("body:", body)
    pg.screenshot(path="_shot_login.png", full_page=False)
    print("page url:", pg.url)
