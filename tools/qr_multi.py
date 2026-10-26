#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qr_multi.py -- 多槽扫码：一次开 N 个登录会话，摆 N 张码，扫中哪张算哪张。

每个槽位独立 context + 独立二维码（qr/slot_k.png），扫完立刻判资格；命中当场出 ¥1 支付码。
比 qr_batch 串行版吞吐高 N 倍：爷爷可以连着扫 3~5 张，不用等上一轮 7 分钟超时。

用法:
  python qr_multi.py --slots 3 --timeout 300
  python qr_multi.py --slots 5 --stop-on-hit
"""
from __future__ import annotations
import argparse, base64, io, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import requests
from playwright.sync_api import sync_playwright
import intake

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36")
QDIR = os.path.join(HERE, "qr")
LEDGER = os.path.join(HERE, "multi_ledger.jsonl")


def save_qr(slot, data_url):
    if not data_url or "base64," not in data_url:
        return False
    os.makedirs(QDIR, exist_ok=True)
    p = os.path.join(QDIR, "slot_%02d.png" % slot)
    open(p, "wb").write(base64.b64decode(data_url.split("base64,", 1)[1]))
    return True


def open_slot(ctx, slot, state):
    pg = ctx.new_page()

    def on_resp(r):
        if "get_qrcode" in r.url:
            try:
                d = (r.json().get("data") or {})
            except Exception:
                return
            if save_qr(slot, d.get("qrcode") or ""):
                state["qr"] = os.path.join(QDIR, "slot_%02d.png" % slot)
                print("[slot %d] QR -> %s" % (slot, state["qr"]), flush=True)

    pg.on("response", on_resp)
    pg.goto("https://www.doubao.com/chat/", wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)
    try:
        pg.keyboard.press("Escape")
    except Exception:
        pass
    pg.evaluate("""()=>{const els=[...document.querySelectorAll('button,div,span,a')];
      const t=els.filter(e=>e.children.length===0 && (e.innerText||'').trim()==='登录');
      if(t.length)t[0].click();}""")
    return pg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slots", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--stop-on-hit", action="store_true")
    a = ap.parse_args()

    states = [{"slot": i, "qr": None, "uid": None, "hit": False, "done": False,
               "pay_url": None, "order_id": None, "disc": None} for i in range(1, a.slots + 1)]
    hits = []
    t0 = time.time()
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True,
                              args=["--disable-blink-features=AutomationControlled"])
        ctxs, pgs = [], []
        for st in states:
            ctx = b.new_context(viewport={"width": 1280, "height": 900}, locale="zh-CN", user_agent=UA)
            ctxs.append(ctx)
            pgs.append(open_slot(ctx, st["slot"], st))
        deadline = t0 + a.timeout
        while time.time() < deadline:
            for st, ctx in zip(states, ctxs):
                if st["done"]:
                    continue
                try:
                    ck = {c["name"]: c["value"] for c in ctx.cookies("https://www.doubao.com")}
                except Exception:
                    continue
                if not ck.get("sessionid"):
                    continue
                ckstr = "; ".join("%s=%s" % kv for kv in ck.items())
                s = requests.Session(); s.cookies.update(ck)
                r = intake.probe(s, mint=False)
                st.update(uid=r.get("uid"), disc=r.get("disc"), hit=bool(r.get("hit")), done=True)
                print("[slot %d] login uid=%s disc=%s hit=%s" % (st["slot"], r.get("uid"), r.get("disc"), bool(r.get("hit"))), flush=True)
                with open(os.path.join(HERE, "pool", "live_intake.jsonl"), "a", encoding="utf-8") as f:
                    f.write("%s|%s\n" % (r.get("uid"), ckstr))
                if r.get("hit"):
                    r2 = intake.probe(s, mint=True)
                    st.update(pay_url=r2.get("pay_url"), order_id=r2.get("order_id"))
                    hits.append(st)
                    print("[slot %d] MINT order=%s pay=%s" % (st["slot"], r2.get("order_id"), (r2.get("pay_url") or "")[:70]), flush=True)
                    if r2.get("pay_url"):
                        try:
                            import qrcode
                            fn = os.path.join(QDIR, "pay_slot_%02d.png" % st["slot"])
                            qrcode.make(r2["pay_url"]).save(fn)
                            print("[slot %d] PAYQR %s" % (st["slot"], fn), flush=True)
                        except Exception:
                            pass
                    if a.stop_on_hit:
                        deadline = 0
            if all(x["done"] for x in states):
                break
            time.sleep(2)
        b.close()

    with open(LEDGER, "a", encoding="utf-8") as f:
        for st in states:
            f.write(json.dumps(dict(st, ts=int(time.time())), ensure_ascii=False) + "\n")
    got = [x for x in states if x["done"]]
    print("== done slots=%d/%d hits=%d elapsed=%.0fs" % (len(got), a.slots, len(hits), time.time() - t0))
    for st in states:
        print("  slot %d qr=%s uid=%s disc=%s hit=%s" % (st["slot"], os.path.basename(st["qr"] or "-"), st["uid"], st["disc"], st["hit"]))
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())