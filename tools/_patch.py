# -*- coding: utf-8 -*-
"""Patch doubao_yuan.py: add `status` and `cancel` subcommands (verified contract)."""
import io, re
p="doubao_yuan.py"
src=open(p,encoding="utf-8").read()

BLOCK = r'''
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
    if str(snap.get("has_subscribed")).lower() != "true" and not a.sid:
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

'''

assert "def cmd_status" not in src
src = src.replace("def main():", BLOCK.strip("\n") + "\n\n\ndef main():", 1)

NEW_MAIN = '''def main():
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
'''
i = src.index("def main():")
j = src.index('if __name__ == "__main__":')
src = src[:i] + NEW_MAIN + "\n\n" + src[j:]
open(p,"w",encoding="utf-8").write(src)
print("patched, len", len(src))
