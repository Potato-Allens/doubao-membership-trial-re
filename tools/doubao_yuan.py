#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""doubao_yuan.py -- Doubao 7-day / 1-CNY intro-offer scanner + pay-link minter.

Read-only stage  : POST /alice/commerce/sale/trade/init/   (no order created)
Mint stage       : POST /alice/commerce/sale/trade/create/ (creates an order, 30 min TTL)

Eligibility rule (verified 2026-10-26):
  sku doubao_personal_std -> card doubao_personal_std_auto_renew_month
  gets discount_amount = 6700 (6800 -> 100 fen) and
  trial_info = {duration:7, duration_unit:3, trial_period_amount:100, trial_stage:1}
  i.e. pay CNY 1.00 -> 7 days, then CNY 68/month auto-renew.

Usage:
  python doubao_yuan.py scan  --pool pool.json [--work] [--json out.json] [-c 8]
  python doubao_yuan.py mint  --ck "<cookie string>" [--work]
  python doubao_yuan.py mint  --pool pool.json --name <entry name>
  python doubao_yuan.py scan  --pool pool.json --mint --json out.json
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
import concurrent.futures as cf
import requests

BASE = "https://www.doubao.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE_PERSONAL = {
    "version_code": "20800", "language": "zh", "device_platform": "web",
    "doubao_device_platform": "web", "aid": "497858", "real_aid": "497858",
    "pkg_type": "release_version", "pc_version": "0.1.0",
    "doubao_pc_version": "0.1.0", "region": "CN", "sys_region": "CN",
    "samantha_web": "1", "web_platform": "desktop", "use-olympus-account": "1",
}
SCOPE_WORK = dict(SCOPE_PERSONAL, aid="582478", real_aid="582478",
                  pc_version="2.33.3", doubao_pc_version="2.33.3", channel="win")
HEADERS = {
    "content-type": "application/json", "agw-js-conv": "str",
    "referer": BASE + "/member/subscription", "origin": BASE,
    "user-agent": UA, "accept": "application/json, text/plain, */*",
}
CARD = "doubao_personal_std_auto_renew_month"
SKU = "doubao_personal_std"
TARGET_DISC = 6700          # 6800 -> 100 fen
KV = re.compile(r"([A-Za-z0-9_\-\.]{2,48})=([^;\"'\\\s]{1,600})")


# ----------------------------------------------------------------- pool
def ck_dict(s):
    if isinstance(s, dict):
        d = {str(k): str(v) for k, v in s.items() if v is not None}
    else:
        d = {}
        for m in KV.finditer(str(s)):
            d[m.group(1)] = m.group(2)
    return d if d.get("sessionid") else None


def _walk(obj, acc, depth=0):
    if depth > 7:
        return acc
    if isinstance(obj, dict):
        d = ck_dict(obj)
        if d:
            acc.append(d)
        for v in obj.values():
            if isinstance(v, str) and "sessionid=" in v:
                d = ck_dict(v)
                if d:
                    acc.append(d)
            elif isinstance(v, (dict, list)):
                _walk(v, acc, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, acc, depth + 1)
    return acc


def load_pool(path):
    """Return list of dicts: {name, ck}. Accepts many on-disk shapes."""
    txt = open(path, "rb").read().decode("utf-8", "replace")
    items = []
    try:
        obj = json.loads(txt)
    except Exception:
        obj = None
    if obj is not None:
        if isinstance(obj, dict) and isinstance(obj.get("cookies"), list):
            d = {c["name"]: c["value"] for c in obj["cookies"] if c.get("name")}
            d = ck_dict(d)
            if d:
                items.append({"name": os.path.basename(path), "ck": d})
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    sub = []
                    _walk(v, sub)
                    for i, d in enumerate(sub):
                        items.append({"name": "%s/%s[%d]" % (os.path.basename(path), k, i), "ck": d})
                else:
                    d = ck_dict(v)
                    if d:
                        items.append({"name": "%s/%s" % (os.path.basename(path), k), "ck": d})
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                if isinstance(v, dict):
                    nm = v.get("name") or v.get("id") or v.get("phone") or v.get("uid") or i
                    raw = v.get("cookie_string") or v.get("ck") or v.get("cookies") or v
                    d = ck_dict(raw)
                    if d:
                        items.append({"name": str(nm), "ck": d})
                    else:
                        sub = []
                        _walk(v, sub)
                        for j, dd in enumerate(sub):
                            items.append({"name": "%s#%d" % (nm, j), "ck": dd})
                else:
                    d = ck_dict(v)
                    if d:
                        items.append({"name": str(i), "ck": d})
    if not items:
        for ln, line in enumerate(txt.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            nm, _, body = line.partition("|")
            d = ck_dict(body if body else nm)
            if d:
                items.append({"name": (nm if body else str(ln)), "ck": d})
    uniq, seen = [], set()
    for it in items:
        sid = it["ck"]["sessionid"]
        if sid in seen:
            continue
        seen.add(sid)
        uniq.append(it)
    return uniq


# ----------------------------------------------------------------- api
def session_of(ck):
    s = requests.Session()
    s.cookies.update(ck)
    return s


def whoami(s, scope):
    try:
        r = s.get("https://accounts.doubao.com/passport/account/info/v2/?aid=%s" % scope["aid"],
                  headers={"user-agent": UA, "referer": BASE + "/"}, timeout=20).json()
        d = r.get("data") or {}
        return {"uid": d.get("user_id_str"), "cc": d.get("country_code"),
                "ct": d.get("user_create_time"), "hm": d.get("hm_region"),
                "screen_name": d.get("screen_name")}
    except Exception as e:
        return {"err": str(e)[:60]}


def init_scan(s, scope):
    j = s.post(BASE + "/alice/commerce/sale/trade/init/", params=scope,
               json={"scene_key": "default_member_link"}, headers=HEADERS, timeout=25).json()
    d = j.get("data") or {}
    best = {"disc": 0, "card": None, "trial": None, "btn": None, "extra": None}
    for sku in d.get("sku_list") or []:
        for c in sku.get("purchase_card_list") or []:
            if c.get("discount_amount", 0) > best["disc"]:
                best = {"disc": c["discount_amount"], "card": c.get("card_id"),
                        "trial": c.get("trial_info"), "btn": c.get("button_text"),
                        "extra": c.get("trade_extra")}
    return {"code": j.get("code"), "msg": str(j.get("message") or "")[:40],
            "claim": d.get("entitlement_claim_status"),
            "hist": d.get("has_history_paid_subscription"), **best}


def mint(s, scope, card_extra, pay_fen=100):
    if isinstance(card_extra, str):
        try:
            card_extra = json.loads(card_extra)
        except Exception:
            card_extra = {}
    body = {"sku_key": SKU, "card_id": CARD, "estimated_pay_amount": str(pay_fen),
            "purchase_channel": 2, "upgrade_mode": 0, "is_gift_deferred": False,
            "start_time": int(time.time() * 1000),
            "trade_extra": json.dumps(card_extra or {}, separators=(",", ":")),
            "is_eligible_for_intro_offer": True}
    j = s.post(BASE + "/alice/commerce/sale/trade/create/", params=scope,
               json=body, headers=HEADERS, timeout=25).json()
    d = j.get("data") or {}
    cred = d.get("payment_credential") or {}
    return {"code": j.get("code"), "msg": str(j.get("message") or "")[:40],
            "order_id": d.get("order_id"), "subscription_id": d.get("subscription_id"),
            "pay_url": cred.get("pay_url") or "",
            "expire_seconds": cred.get("order_expire_seconds")}


# ----------------------------------------------------------------- cmds
def cmd_scan(a):
    scope = SCOPE_WORK if a.work else SCOPE_PERSONAL
    pool = []
    targets = []
    for p in a.pool:
        if os.path.isdir(p):
            for dirp, _, fs in os.walk(p):
                for f in fs:
                    if f.lower().endswith((".json", ".txt")):
                        targets.append(os.path.join(dirp, f))
        else:
            targets.append(p)
    for p in targets:
        try:
            got = load_pool(p)
        except Exception:
            continue
        if got:
            print("[pool] %s -> %d unique accounts" % (p, len(got)), flush=True)
        pool += got
    if not pool:
        print("no cookies parsed"); return 2

    def one(it):
        s = session_of(it["ck"])
        try:
            info = whoami(s, scope) if a.validate else {}
            r = init_scan(s, scope)
            return {"name": it["name"], **info, **r,
                    "hit1": r.get("code") == 0 and r.get("disc") == TARGET_DISC}
        except Exception as e:
            return {"name": it["name"], "err": str(e)[:70]}

    rows = []
    with cf.ThreadPoolExecutor(max_workers=max(1, a.conc)) as ex:
        for i, r in enumerate(ex.map(one, pool), 1):
            rows.append(r)
            if r.get("hit1"):
                print("  [HIT] %-28s uid=%s disc=%s" % (r["name"], r.get("uid"), r.get("disc")), flush=True)
            elif i % 25 == 0:
                print("  .. %d/%d" % (i, len(pool)), flush=True)

    hits = [r for r in rows if r.get("hit1")]
    disc = [r for r in rows if r.get("code") == 0 and (r.get("disc") or 0) > 0]
    codes = {}
    for r in rows:
        codes[str(r.get("code"))] = codes.get(str(r.get("code")), 0) + 1
    print("\n== summary ==")
    print("total   :", len(rows))
    print("codes   :", json.dumps(codes))
    print("any disc:", len(disc), " 1-CNY/7d:", len(hits))
    for r in disc:
        print("  %-26s disc=%-5s card=%s trial=%s btn=%s" %
              (r["name"], r.get("disc"), r.get("card"),
               json.dumps(r.get("trial"), ensure_ascii=False), r.get("btn")))

    if a.mint and hits:
        print("\n== minting ==")
        for r in hits:
            it = next(x for x in pool if x["name"] == r["name"])
            m = mint(session_of(it["ck"]), scope, r.get("extra"))
            print("  %-26s code=%s order=%s %s" % (r["name"], m["code"], m["order_id"],
                                                   m["pay_url"][:80]))
            r.update(m)

    if a.json:
        json.dump(rows, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("saved ->", a.json)
    return 0


def cmd_mint(a):
    scope = SCOPE_WORK if a.work else SCOPE_PERSONAL
    if a.ck:
        ck = ck_dict(a.ck)
        name = "cli"
    else:
        pool = load_pool(a.pool[0])
        it = next((x for x in pool if x["name"] == a.name), pool[0])
        ck, name = it["ck"], it["name"]
    if not ck:
        print("no sessionid in cookie"); return 2
    s = session_of(ck)
    r = init_scan(s, scope)
    print("[init]", name, "code", r["code"], "disc", r["disc"], "trial",
          json.dumps(r["trial"], ensure_ascii=False), "btn", r["btn"])
    if r["disc"] != TARGET_DISC:
        print("NOT eligible for the 1-CNY/7d offer -> abort mint")
        return 3
    m = mint(s, scope, r["extra"])
    print("[create]", json.dumps(m, ensure_ascii=False, indent=1))
    return 0 if m.get("pay_url") else 4


# ----------------------------------------------------------------- account state
EP_OVERVIEW = "/alice/commerce/sale/subscription/overview/"
EP_STATUS   = "/alice/commerce/sale/subscription/status/"
EP_ORDERS   = "/alice/commerce/sale/order/list/"
EP_CANCEL   = "/alice/commerce/sale/subscription/cancel/"


def post_json(s, ep, body, scope):
    try:
        r = s.post(BASE + ep, params=scope, json=body if body is not None else {},
                   headers=HEADERS, timeout=25)
        try:
            return r.json()
        except Exception:
            return {"code": -1, "message": (r.text or "")[:80]}
    except Exception as e:
        return {"code": -1, "message": str(e)[:80]}


def snapshot(s, scope):
    """Return a flat dict of the account subscription state."""
    ov = post_json(s, EP_OVERVIEW, {"product_line": "membership"}, scope)
    cs = (ov.get("data") or {}).get("current_subscription") or {}
    st = post_json(s, EP_STATUS, {}, scope)
    if not (st.get("data") or {}):
        st = post_json(s, EP_STATUS, {"required_fields": [2], "product_lines": ["membership"]}, scope)
    ol = post_json(s, EP_ORDERS, {"product_lines": ["membership"]}, scope)
    orders = ((ol.get("data") or {}).get("items") or [])[:5]
    tr = cs.get("trial_info") or {}
    return {
        "ov_code": ov.get("code"),
        "subscription_id": cs.get("subscription_id"),
        "sku": cs.get("sku_key"),
        "start": cs.get("start_time"),
        "end": cs.get("end_time"),
        "next_deduct": cs.get("next_deduct_time"),
        "agreement_status": cs.get("agreement_status"),
        "agreement_price": cs.get("agreement_price"),
        "sub_status": cs.get("status"),
        "is_trialing": tr.get("is_trialing"),
        "trial_price": tr.get("trial_price"),
        "has_subscribed": (st.get("data") or {}).get("has_subscribed"),
        "is_subscribing": (st.get("data") or {}).get("is_subscribing"),
        "orders": [{"id": o.get("order_id"), "paid": o.get("actual_pay_amount"),
                    "paid_at": o.get("paid_at_ms"), "name": o.get("display_name"),
                    "status_view": o.get("status_view")} for o in orders],
    }


def _fmt_ms(v):
    if not isinstance(v, (int, float)) or v < 1e12:
        return "-"
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v / 1000.0))


def show(snap):
    end = snap.get("end")
    left = (end / 1000.0 - time.time()) / 86400.0 if isinstance(end, (int, float)) and end > 1e12 else None
    print("  subscription_id   :", snap.get("subscription_id"))
    print("  sku               :", snap.get("sku"))
    print("  start_time        :", _fmt_ms(snap.get("start")))
    print("  end_time          :", _fmt_ms(end), ("(剩余 %.3f 天)" % left) if left is not None else "")
    print("  next_deduct_time  :", _fmt_ms(snap.get("next_deduct")))
    print("  agreement_status  :", snap.get("agreement_status"), "  price:", snap.get("agreement_price"))
    print("  sub_status        :", snap.get("sub_status"))
    print("  is_trialing       :", snap.get("is_trialing"), " trial_price:", snap.get("trial_price"))
    print("  has_subscribed    :", snap.get("has_subscribed"), " is_subscribing:", snap.get("is_subscribing"))
    for o in snap.get("orders") or []:
        print("  order             : %s  ¥%.2f  %s  %s" %
              (o.get("id"), (o.get("paid") or 0) / 100.0, _fmt_ms(o.get("paid_at")), o.get("name")))


def resolve(a):
    """Return (ck, label) from --ck / --uid / --name / first pool entry."""
    if getattr(a, "ck", ""):
        return ck_dict(a.ck), "cli"
    pools = list(getattr(a, "pool", []) or [])
    uid = str(getattr(a, "uid", "") or "")
    if uid:
        for p in pools:
            try:
                obj = json.load(open(p, encoding="utf-8-sig"))
            except Exception:
                continue
            acc = obj.get("accounts") if isinstance(obj, dict) else None
            for it in (acc or []):
                if str(it.get("uid")) == uid:
                    d = ck_dict(it.get("cookie_string") or it.get("ck") or "")
                    if d:
                        return d, "%s/%s" % (os.path.basename(p), uid)
        return None, "uid-not-found"
    name = getattr(a, "name", "")
    for p in pools:
        try:
            got = load_pool(p)
        except Exception:
            continue
        hit = next((x for x in got if x["name"] == name), None) if name else (got[0] if got else None)
        if hit:
            return hit["ck"], hit["name"]
    return None, "no-source"


def cmd_status(a):
    scope = SCOPE_WORK if a.work else SCOPE_PERSONAL
    ck, nm = resolve(a)
    if not ck:
        print("[status] no cookie (%s)" % nm); return 2
    s = session_of(ck)
    snap = snapshot(s, scope)
    print("[status] %s" % nm)
    show(snap)
    if a.json:
        json.dump(snap, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("  saved ->", a.json)
    return 0


def cmd_cancel(a):
    """Cancel auto-renew. DRY by default: pass --yes to actually call."""
    scope = SCOPE_WORK if a.work else SCOPE_PERSONAL
    ck, nm = resolve(a)
    if not ck:
        print("[cancel] no cookie (%s)" % nm); return 2
    s = session_of(ck)
    snap = snapshot(s, scope)
    sid = a.sid or snap.get("subscription_id")
    print("[cancel] %s" % nm)
    print("-- before --"); show(snap)
    if not sid:
        print("no subscription_id -> nothing to cancel"); return 3
    if snap.get("has_subscribed") is False and not a.sid and not snap.get("subscription_id"):
        print("account is not subscribed -> nothing to cancel"); return 3
    if not a.yes:
        print("\n[dry-run] would POST %s  body={\"subscription_id\":\"%s\"}" % (EP_CANCEL, sid))
        print("[dry-run] re-run with --yes to actually cancel auto-renew")
        return 0
    r = post_json(s, EP_CANCEL, {"subscription_id": str(sid)}, scope)
    print("\n[cancel] code=%s msg=%s" % (r.get("code"), str(r.get("message"))[:80]))
    time.sleep(2)
    after = snapshot(s, scope)
    print("-- after --"); show(after)
    lost = (snap.get("end") or 0) != (after.get("end") or 0)
    print("\nend_time %s" % ("CHANGED -> 剩余时长受影响，请核对" if lost else "unchanged -> 已付时长保留"))
    return 0 if r.get("code") == 0 else 4


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--pool", nargs="+", required=True)
    s.add_argument("--work", action="store_true")
    s.add_argument("--validate", action="store_true")
    s.add_argument("--mint", action="store_true")
    s.add_argument("--json", default="")
    s.add_argument("-c", "--conc", type=int, default=8)
    m = sub.add_parser("mint")
    m.add_argument("--ck", default="")
    m.add_argument("--pool", nargs="+", default=[])
    m.add_argument("--name", default="")
    m.add_argument("--work", action="store_true")
    for name in ("status", "cancel"):
        q = sub.add_parser(name)
        q.add_argument("--ck", default="")
        q.add_argument("--pool", nargs="+", default=[])
        q.add_argument("--name", default="")
        q.add_argument("--uid", default="")
        q.add_argument("--work", action="store_true")
        if name == "status":
            q.add_argument("--json", default="")
        else:
            q.add_argument("--sid", default="")
            q.add_argument("--yes", action="store_true",
                           help="actually call the cancel API (default is dry-run)")
    a = ap.parse_args()
    return {"scan": cmd_scan, "mint": cmd_mint,
            "status": cmd_status, "cancel": cmd_cancel}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())