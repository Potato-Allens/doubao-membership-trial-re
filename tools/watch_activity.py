#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""watch_activity.py -- 资格「活性」观测器（R475）

每轮对候选号打一次 `marketing/resource/mget/v2`，看 `exit_retention.activity_id`：
  · first_purchase_discount  = 有 1 元首购资格
  · 其它（renewal_guidance_v1 等） = 没有
只读、不建单、不消耗。用来回答一个问题：**资格会不会随时间自己出现？**

用法:
  python watch_activity.py --interval 300 --hours 6
  python watch_activity.py --pool pool/trial_batch_all2.json --interval 600
"""
from __future__ import annotations
import argparse, json, os, sys, time
import requests
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doubao_yuan as D

W = HERE
LOG = os.path.join(HERE, "activity_watch.jsonl")
BASE = "https://www.doubao.com"
SCOPE = D.SCOPE_PERSONAL
H = dict(D.HEADERS)


def probe(ck):
    s = D.session_of(ck); s.headers.update(H)
    try:
        j = s.post(BASE + "/alice/commerce/marketing/resource/mget/v2/", params=SCOPE,
                   json={"resource_keys": ["exit_retention"]}, timeout=20).json()
        r = ((j.get("data") or {}).get("results") or {}).get("exit_retention") or {}
        return {"code": j.get("code"), "activity": r.get("activity_id"), "resource_id": r.get("resource_id")}
    except Exception as e:
        return {"err": type(e).__name__}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=os.path.join(HERE, "pool", "trial_batch_all2.json"))
    ap.add_argument("--interval", type=int, default=300)
    ap.add_argument("--hours", type=float, default=6)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    items = D.load_pool(a.pool)
    print("watch %d accounts, every %ds for %.1fh" % (len(items), a.interval, a.hours), flush=True)
    end = time.time() + a.hours * 3600
    rounds = 0
    flips = []
    while time.time() < end:
        rounds += 1
        t0 = time.time()
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            res = list(ex.map(probe, [it["ck"] for it in items]))
        row = {"ts": int(time.time()), "round": rounds, "hits": [], "errs": 0}
        for it, r in zip(items, res):
            if r.get("err"):
                row["errs"] += 1
                continue
            if r.get("activity") == "first_purchase_discount":
                row["hits"].append({"name": it["name"], "activity": r.get("activity")})
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print("round %d: hits=%d errs=%d (%.1fs)" % (rounds, len(row["hits"]), row["errs"], time.time() - t0), flush=True)
        for h in row["hits"]:
            print("   HIT", h["name"], flush=True)
        # 提前结束：如果原本没资格的号出现了资格，立刻记录
        if row["hits"]:
            flips.append(row)
        time.sleep(max(5, a.interval - (time.time() - t0)))
    print("done rounds=%d flips=%d" % (rounds, len(flips)))
    return 0


if __name__ == "__main__":
    sys.exit(main())