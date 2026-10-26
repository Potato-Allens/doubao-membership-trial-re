#!/usr/bin/env python3
"""triage.py - 先分流再出单: 手机国家码 + 订阅历史 -> 候选 -> trade/init.

R471 实测(243 活号): cc=86 的 79 行 0 命中; 境外号里"有过订阅记录"的 117 行 0 命中;
"境外 + 零订阅记录" 的 26 行里 6 行命中。先分流能把扫描成本砍掉一个数量级,
并把注意力放在真正可能出 1 元单的号上。

用法:
  python triage.py --pool pool.json -c 8                 # 只分流, 不打 trade/init
  python triage.py --pool pool.json -c 8 --with-init     # 候选号再打 trade/init
  python triage.py --pool pool.json --mint --qr pay.png  # 命中直接出码
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doubao_yuan as dy

INFO = "/passport/account/info/v2/"
SUBS = "/alice/commerce/sale/subscription/list/"
FOREIGN = {"1", "852", "44", "65", "81", "82", "61", "49", "33", "31", "7", "66", "60", "84", "62", "91", "971", "972", "886"}


def triage_one(item, scope, with_init):
    name, ck = item["name"], item["ck"]
    out = {"name": name, "cc": None, "hm": None, "records": None, "disc": None, "code": None}
    try:
        s = dy.session_of(ck)
        j = dy.post_json(s, INFO, {}, scope)
        d = j.get("data") or {}
        out["cc"] = str(d.get("country_code"))
        out["hm"] = d.get("hm_region")
        out["uid"] = d.get("user_id_str")
        out["ct"] = d.get("user_create_time")
        j2 = dy.post_json(s, SUBS, {"page": 1, "page_size": 10}, scope)
        d2 = j2.get("data") or {}
        out["records"] = sum(len(g.get("records") or []) for g in (d2.get("groups") or []))
        if with_init and out["cc"] in FOREIGN and out["records"] == 0:
            r = dy.init_scan(s, scope)
            out["disc"] = r.get("disc") or 0
            out["code"] = r.get("code")
    except Exception as e:
        out["err"] = type(e).__name__
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("-c", "--concurrency", type=int, default=8)
    ap.add_argument("--with-init", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--mint", action="store_true")
    ap.add_argument("--qr", default=None)
    a = ap.parse_args()
    pool = dy.load_pool(a.pool)
    scope = dy.SCOPE_PERSONAL
    rows = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = [ex.submit(triage_one, it, scope, a.with_init) for it in pool]
        for i, f in enumerate(futs):
            rows.append(f.result())
            if (i + 1) % 100 == 0:
                print("  %d/%d %.0fs" % (i + 1, len(pool), time.time() - t0), flush=True)
    cand = [r for r in rows if r.get("cc") in FOREIGN and r.get("records") == 0]
    hits = [r for r in rows if (r.get("disc") or 0) >= 6000]
    print("\n== triage ==")
    print("total %d  alive %d  candidates(overseas+clean) %d  hits %d  %.1fs" % (
        len(rows), sum(1 for r in rows if r.get("cc")), len(cand), len(hits), time.time() - t0))
    for r in hits:
        print("  HIT %s uid=%s cc=%s disc=%s" % (r["name"], r.get("uid"), r["cc"], r["disc"]))
    if a.json:
        json.dump({"rows": rows, "candidates": cand, "hits": hits},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("saved", a.json)


if __name__ == "__main__":
    main()