# -*- coding: utf-8 -*-
"""login_capture.py -- 开一个可见 Chrome，用户扫码/登录后自动抓 CK 并立即判 1 元。

用法: python login_capture.py [--timeout 900] [--headless]
成功后: 写 pool/live_intake.jsonl（name|cookie），并调用 intake.probe 判资格。
"""
from __future__ import annotations
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import intake
import requests

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
PROF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_prof_login")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pool", "live_intake.jsonl")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--headless", action="store_true")
    a = ap.parse_args()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            PROF, channel="chrome", headless=a.headless,
            viewport={"width": 1180, "height": 860}, locale="zh-CN", user_agent=UA,
            args=["--disable-blink-features=AutomationControlled"])
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.goto("https://www.doubao.com/chat/", wait_until="domcontentloaded", timeout=60000)
        try:
            pg.keyboard.press("Escape")
        except Exception:
            pass
        print("[login_capture] 窗口已打开，请在窗口里登录（扫码/飞书/手机号）。等待中…", flush=True)
        deadline = time.time() + a.timeout
        ck = None
        while time.time() < deadline:
            try:
                cookies = ctx.cookies("https://www.doubao.com")
            except Exception:
                cookies = []
            d = {c["name"]: c["value"] for c in cookies}
            if d.get("sessionid") and d.get("sessionid") not in ("", "0"):
                ck = d
                break
            time.sleep(3)
        if not ck:
            print("[login_capture] 超时未检测到登录", flush=True)
            ctx.close(); return 3
        ckstr = "; ".join("%s=%s" % (k, v) for k, v in ck.items())
        s = requests.Session(); s.cookies.update(ck)
        r = intake.probe(s, mint=False)
        uid = r.get("uid") or "unknown"
        with open(OUT, "a", encoding="utf-8") as f:
            f.write("%s|%s\n" % (uid, ckstr))
        print("[login_capture] 登录成功 uid=%s cookies=%d" % (uid, len(ck)), flush=True)
        print("[probe]", json.dumps({k: r.get(k) for k in
              ("ok", "uid", "name", "skip", "disc", "btn", "trial", "hit")}, ensure_ascii=False), flush=True)
        if r.get("hit"):
            print("[login_capture] ★ 命中 1 元，正在出单…", flush=True)
            r2 = intake.probe(s, mint=True)
            print("[mint]", json.dumps({k: r2.get(k) for k in
                  ("mint_code", "order_id", "pay_url", "expire")}, ensure_ascii=False), flush=True)
            if r2.get("pay_url"):
                try:
                    import qrcode
                    fn = os.path.join(os.path.dirname(OUT), "pay_1yuan_%s.png" % uid)
                    qrcode.make(r2["pay_url"]).save(fn)
                    print("[qr]", fn, flush=True)
                except Exception as e:
                    print("[qr] err", str(e)[:60], flush=True)
        print("[login_capture] 已完成，可关闭窗口", flush=True)
        time.sleep(2)
        ctx.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())