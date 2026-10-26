# -*- coding: utf-8 -*-
"""intake.py -- 收号 → 预筛(跳过已在订阅) → 判 1 元 → 命中立刻出支付链。

用法:
  python intake.py --pool path.json            # 扫描整个池，命中自动建单
  python intake.py --ck "sessionid=...; ..."   # 单个 cookie 字符串
  python intake.py --pool p.json --no-mint     # 只扫不出单
  python intake.py --pool p.json --qr          # 命中时同时生成二维码 png
"""
from __future__ import annotations
import argparse, json, os, sys, time, random, io
import concurrent.futures as cf
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doubao_yuan import (BASE, UA, SCOPE_PERSONAL, HEADERS, SKU, CARD,
                         TARGET_DISC, ck_dict, load_pool, session_of)

EP_STATUS = "/alice/commerce/sale/subscription/status/"
EP_INIT = "/alice/commerce/sale/trade/init/"
EP_CREATE = "/alice/commerce/sale/trade/create/"
SCOPE = SCOPE_PERSONAL


def post(s, ep, body=None, tries=3):
    last = None
    for _ in range(tries):
        try:
            r = s.post(BASE + ep, params=SCOPE, json=body if body is not None else {},
                       headers=HEADERS, timeout=25)
            j = r.json()
        except Exception as e:
            last = {"code": -1, "message": str(e)[:60]}
            time.sleep(1.2); continue
        if j.get("code") == 611060900:          # rate limit
            time.sleep(1.5 + random.random()); last = j; continue
        return j
    return last or {"code": -1}


def probe(s, mint=False):
    who = {}
    try:
        r = s.get("https://accounts.doubao.com/passport/account/info/v2/?aid=%s" % SCOPE["aid"],
                  headers={"user-agent": UA, "referer": BASE + "/"}, timeout=20).json()
        d = r.get("data") or {}
        who = {"uid": d.get("user_id_str"), "name": d.get("screen_name"),
               "ct": d.get("user_create_time")}
        if not d.get("user_id_str"):
            return {"ok": False, "reason": "login_invalid", **who}
    except Exception as e:
        return {"ok": False, "reason": "whoami_err:" + str(e)[:40]}

    st = (post(s, EP_STATUS, {}).get("data") or {})
    if st.get("has_subscribed") or st.get("is_subscribing"):
        return {"ok": True, "skip": "already_subscribed", "uid": who.get("uid"), **st}

    j = post(s, EP_INIT, {"scene_key": "default_member_link", "purchase_channel": 2})
    d = j.get("data") or {}
    card = None
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("card_id") == CARD:
                card = c
    if j.get("code") != 0 or card is None:
        return {"ok": True, "uid": who.get("uid"), "code": j.get("code"),
                "msg": str(j.get("message") or j.get("msg") or "")[:40], "hit": False}

    trial = card.get("trial_info") or {}
    disc = card.get("discount_amount") or 0
    hit = disc == TARGET_DISC or (trial.get("trial_stage") == 1 and disc > 0)
    out = {"ok": True, "uid": who.get("uid"), "name": who.get("name"), "ct": who.get("ct"),
           "disc": disc, "dtp": card.get("discount_total_price"),
           "btn": card.get("button_text"), "trial": trial,
           "extra": card.get("trade_extra"), "hit": hit}
    if hit and mint:
        body = {"sku_key": SKU, "card_id": CARD, "estimated_pay_amount": "100",
                "purchase_channel": 2, "upgrade_mode": 0, "is_gift_deferred": False,
                "start_time": int(time.time() * 1000),
                "trade_extra": card.get("trade_extra") or "{}",
                "is_eligible_for_intro_offer": True}
        m = post(s, EP_CREATE, body)
        md = m.get("data") or {}
        cred = md.get("payment_credential") or {}
        out.update(mint_code=m.get("code"), order_id=md.get("order_id"),
                   subscription_id=md.get("subscription_id"),
                   pay_url=cred.get("pay_url"), expire=cred.get("order_expire_seconds"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", action="append", default=[])
    ap.add_argument("--ck")
    ap.add_argument("--no-mint", action="store_true")
    ap.add_argument("--qr", action="store_true")
    ap.add_argument("--json", default="intake_result.json")
    ap.add_argument("-c", "--conc", type=int, default=3)
    a = ap.parse_args()

    items = []
    if a.ck:
        d = ck_dict(a.ck)
        if d:
            items.append({"name": "cli", "ck": d})
    for p in a.pool:
        items += load_pool(p)
    if not items:
        print("no cookies"); return 2
    print("loaded %d unique accounts" % len(items), flush=True)

    def one(it):
        s = session_of(it["ck"])
        try:
            r = probe(s, mint=not a.no_mint)
        except Exception as e:
            r = {"ok": False, "reason": str(e)[:70]}
        r["name"] = it["name"]
        return r

    rows = []
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=max(1, a.conc)) as ex:
        for i, r in enumerate(ex.map(one, items), 1):
            rows.append(r)
            if r.get("hit"):
                print("[HIT] %s uid=%s disc=%s order=%s" %
                      (r.get("uid"), r.get("uid"), r.get("disc"), r.get("order_id")), flush=True)
                if r.get("pay_url"):
                    print("      pay: %s" % r["pay_url"][:120], flush=True)
            if i % 20 == 0:
                print("  %d/%d  %.0fs" % (i, len(items), time.time() - t0), flush=True)

    hits = [r for r in rows if r.get("hit")]
    skipped = [r for r in rows if r.get("skip")]
    dead = [r for r in rows if not r.get("ok")]
    print("\n== summary ==")
    print("total %d | hit %d | already_subscribed %d | dead %d" %
          (len(rows), len(hits), len(skipped), len(dead)))
    for r in hits:
        print("  %s disc=%s order=%s pay=%s" %
              (r.get("uid"), r.get("disc"), r.get("order_id"), (r.get("pay_url") or "")[:90]))

    if a.qr and hits:
        try:
            import qrcode
            for n, r in enumerate([h for h in hits if h.get("pay_url")], 1):
                fn = "pay_1yuan_%s_%d.png" % (r.get("uid"), n)
                img = qrcode.make(r["pay_url"])
                img.save(fn)
                print("  qr -> %s" % os.path.abspath(fn))
        except Exception as e:
            print("  qr err", str(e)[:60])

    json.dump(rows, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved ->", a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())