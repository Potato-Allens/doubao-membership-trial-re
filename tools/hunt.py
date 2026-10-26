#!/usr/bin/env python3
"""hunt.py - 扫描 -> 命中即出单 的无人值守流水线.

用法:
  python hunt.py --pool ../data/sample_pool.json -c 8                # 扫一轮并出单
  python hunt.py --pool pool.json --no-mint                          # 只扫不出单
  python hunt.py --pool pool.json --watch 600                        # 每 10 分钟扫一轮
  python hunt.py --pool pool.json --min-disc 6700 --ledger hits.jsonl

判定: trade/init 返回的 discount_amount >= --min-disc (默认 6700 = 1 元 / 7 天).
命中后立刻 trade/create, 把 pay_url / order_id 追加到 ledger.
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doubao_yuan as dy


def scan_one(item, scope):
    name, ck = item
    try:
        s = dy.session_of(ck)
        r = dy.init_scan(s, scope)
    except Exception as e:
        return {"name": name, "code": -1, "err": str(e)[:60], "disc": 0}
    r["name"] = name
    r["_ck"] = ck
    return r


def mint_one(r, scope):
    try:
        s = dy.session_of(r["_ck"])
        return dy.mint(s, scope, r.get("extra"))
    except Exception as e:
        return {"code": -1, "msg": str(e)[:60], "pay_url": ""}


def load_ledger(path):
    seen = set()
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
                if o.get("order_id"):
                    seen.add(o["order_id"])
            except Exception:
                pass
    return seen


def append_ledger(path, rec):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


HIT_SEEN = set()


def run_once(args, scope, seen):
    pool = dy.load_pool(args.pool)
    items = [(a.get("name") or str(a.get("uid")), a.get("ck") or dy.ck_dict(a.get("cookie_string") or ""))
             for a in pool]
    if args.limit:
        items = items[: args.limit]
    print("[hunt] pool=%d threads=%d min_disc=%d mint=%s" %
          (len(items), args.conc, args.min_disc, not args.no_mint), flush=True)

    alive = hits = minted = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=args.conc) as ex:
        futs = {ex.submit(scan_one, it, scope): it[0] for it in items}
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            if r.get("code") == 0:
                alive += 1
            if (r.get("disc") or 0) >= args.min_disc:
                hits += 1
                ti = r.get("trial") or {}
                print("[HIT] %-22s uid=%s disc=%s stage=%s card=%s btn=%s" %
                      (r.get("name"), r.get("uid", "-"), r.get("disc"),
                       ti.get("trial_stage"), r.get("card"), r.get("btn")), flush=True)
                key = (r.get("name"), r.get("disc"))
                if key not in HIT_SEEN:
                    HIT_SEEN.add(key)
                    append_ledger(args.ledger, {"ts": int(time.time()), "event": "hit",
                                                "name": r.get("name"), "uid": r.get("uid"),
                                                "disc": r.get("disc"), "trial": r.get("trial"),
                                                "card": r.get("card")})
                if not args.no_mint:
                    m = mint_one(r, scope)
                    rec = {"ts": int(time.time()), "event": "mint", "name": r.get("name"),
                           "disc": r.get("disc"), "order_id": m.get("order_id"),
                           "subscription_id": m.get("subscription_id"),
                           "pay_url": m.get("pay_url"), "expire_seconds": m.get("expire_seconds"),
                           "code": m.get("code"), "msg": m.get("msg")}
                    if m.get("order_id") and m.get("order_id") not in seen:
                        seen.add(m["order_id"])
                        append_ledger(args.ledger, rec)
                        minted += 1
                        print("[MINT] order=%s expire=%ss url=%s" %
                              (m.get("order_id"), m.get("expire_seconds"),
                               (m.get("pay_url") or "")[:80]), flush=True)
                    else:
                        print("[MINT-FAIL] code=%s msg=%s" % (m.get("code"), m.get("msg")), flush=True)
            if i % 20 == 0:
                print("[hunt] %d/%d alive=%d hits=%d %.1fs" %
                      (i, len(items), alive, hits, time.time() - t0), flush=True)
    print("[hunt] done alive=%d hits=%d minted=%d elapsed=%.1fs" %
          (alive, hits, minted, time.time() - t0), flush=True)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("-c", "--conc", type=int, default=8)
    ap.add_argument("--min-disc", type=int, default=6700)
    ap.add_argument("--no-mint", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--watch", type=int, default=0, help="seconds between rounds; 0 = single round")
    ap.add_argument("--ledger", default="hits.jsonl")
    ap.add_argument("--work", action="store_true", help="use aid=582478 (Lark workspace)")
    args = ap.parse_args()

    scope = dy.SCOPE_WORK if args.work else dy.SCOPE_PERSONAL
    seen = load_ledger(args.ledger)
    if not args.watch:
        run_once(args, scope, seen)
        return
    while True:
        try:
            run_once(args, scope, seen)
        except Exception as e:
            print("[hunt] round error: %s" % str(e)[:120], flush=True)
        print("[hunt] sleep %ds" % args.watch, flush=True)
        time.sleep(args.watch)


if __name__ == "__main__":
    main()