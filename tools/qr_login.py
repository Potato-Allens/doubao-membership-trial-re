# -*- coding: utf-8 -*-
"""qr_login.py -- 生成豆包登录二维码（PNG），用户扫码后自动抓 CK 并立刻判/出 1 元。

输出:
  login_qr.png        <- 发给用户扫的码
  pool/live_intake.jsonl
  qr_login_result.json
"""
from __future__ import annotations
import base64, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import intake, requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
HERE = os.path.dirname(os.path.abspath(__file__))
QR_PNG = os.path.join(HERE, "login_qr.png")
OUT = os.path.join(HERE, "pool", "live_intake.jsonl")
TIMEOUT = int(sys.argv[1]) if len(sys.argv) > 1 else 420


def save_qr(data_url: str) -> bool:
    if not data_url or "base64," not in data_url:
        return False
    b64 = data_url.split("base64,", 1)[1]
    with open(QR_PNG, "wb") as f:
        f.write(base64.b64decode(b64))
    return True


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    state = {"qr_saved": False, "token": None, "expire": None, "status": None,
             "uid": None, "hit": False, "pay_url": None, "order_id": None}
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True,
                              args=["--disable-blink-features=AutomationControlled"])
        ctx = b.new_context(viewport={"width": 1280, "height": 900}, locale="zh-CN", user_agent=UA)
        pg = ctx.new_page()

        def on_resp(r):
            u = r.url
            if "get_qrcode" in u:
                try:
                    j = r.json()
                except Exception:
                    return
                d = j.get("data") or {}
                if save_qr(d.get("qrcode") or ""):
                    state["qr_saved"] = True
                    state["token"] = d.get("token") or d.get("qrcode_token")
                    state["expire"] = d.get("expire_time")
                    print("[QR] saved -> %s" % QR_PNG, flush=True)
            elif "check_qrconnect" in u:
                try:
                    j = r.json()
                except Exception:
                    return
                st = (j.get("data") or {}).get("status")
                if st and st != state["status"]:
                    state["status"] = st
                    print("[QR] status=%s" % st, flush=True)

        pg.on("response", on_resp)
        pg.goto("https://www.doubao.com/chat/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        try:
            pg.keyboard.press("Escape")
        except Exception:
            pass
        try:
            pg.locator("button[aria-label*=关闭]").first.click(timeout=2000)
        except Exception:
            pass
        pg.evaluate("""()=>{const els=[...document.querySelectorAll('button,div,span,a')];
          const t=els.filter(e=>e.children.length===0 && (e.innerText||'').trim()==='登录');
          if(t.length)t[0].click();}""")
        # wait for QR to be fetched
        for _ in range(40):
            if state["qr_saved"]:
                break
            time.sleep(0.5)
        if not state["qr_saved"]:
            # try clicking the QR tab explicitly
            try:
                pg.locator("text=飞书账号一键登录").first.click(timeout=4000)
            except Exception:
                pass
            time.sleep(5)
        print("[QR] ready=%s token=%s" % (state["qr_saved"], state["token"]), flush=True)

        deadline = time.time() + TIMEOUT
        ck = None
        while time.time() < deadline:
            try:
                cookies = ctx.cookies("https://www.doubao.com")
            except Exception:
                cookies = []
            d = {c["name"]: c["value"] for c in cookies}
            if d.get("sessionid"):
                ck = d
                break
            time.sleep(2)

        if not ck:
            print("[QR] timeout, no session", flush=True)
            b.close()
            json.dump(state, open(os.path.join(HERE, "qr_login_result.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            return 3

        ckstr = "; ".join("%s=%s" % (k, v) for k, v in ck.items())
        s = requests.Session(); s.cookies.update(ck)
        r = intake.probe(s, mint=False)
        uid = r.get("uid") or "unknown"
        with open(OUT, "a", encoding="utf-8") as f:
            f.write("%s|%s\n" % (uid, ckstr))
        print("[LOGIN] uid=%s cookies=%d" % (uid, len(ck)), flush=True)
        print("[PROBE] %s" % json.dumps({k: r.get(k) for k in
              ("ok", "uid", "name", "skip", "disc", "btn", "trial", "hit")}, ensure_ascii=False), flush=True)
        state.update(uid=uid, hit=bool(r.get("hit")), probe=r)
        if r.get("hit"):
            r2 = intake.probe(s, mint=True)
            state.update(pay_url=r2.get("pay_url"), order_id=r2.get("order_id"),
                         mint_code=r2.get("mint_code"), expire_seconds=r2.get("expire"))
            print("[MINT] %s" % json.dumps({k: r2.get(k) for k in
                  ("mint_code", "order_id", "pay_url", "expire")}, ensure_ascii=False), flush=True)
            if r2.get("pay_url"):
                try:
                    import qrcode
                    fn = os.path.join(HERE, "pay_1yuan_%s.png" % uid)
                    qrcode.make(r2["pay_url"]).save(fn)
                    print("[PAYQR] %s" % fn, flush=True)
                except Exception as e:
                    print("[PAYQR] err %s" % str(e)[:60], flush=True)
        json.dump(state, open(os.path.join(HERE, "qr_login_result.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        time.sleep(2)
        b.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())