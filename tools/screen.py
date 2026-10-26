#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""screen.py -- 用营销资源做「资格预筛」（R475，read-only）

原理：`/alice/commerce/marketing/resource/mget/v2/` 的 `exit_retention` 资源对
  · 有 1 元首购资格 -> activity_id = first_purchase_discount / free_trial_v2
  · 没有            -> renewal_guidance_v1 或空
一次请求即可判断，不建单、不消耗资格，比 trade/init 更轻。

用法:
  python screen.py --pool pool.json [-c 8] [--json out.json]
  python screen.py --pool pool.json --only-alive scan.json   # 只看 code==0 的号
"""
from __future__ import annotations
import argparse, json, os, sys, time
import requests
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doubao_yuan as D

BASE = "https://www.doubao.com"
HIT_ACTS = {"first_purchase_discount", "free_trial_v2"}


def screen_one(ck):
    s = D.session_of(ck); s.headers.update(D.HEADERS)
    try:
        j = s.post(BASE + "/alice/commerce/marketing/resource/mget/v2/", params=D.SCOPE_PERSONAL,
                   json={"resource_keys": ["exit_retention"]}, timeout=20).json()
        res = ((j.get("data") or {}).get("results") or {}).get("exit_retention") or {}
        act = res.get("activity_id")
        return {"code": j.get("code"), "activity": act, "flag": act in HIT_ACTS,
                "resource_id": res.get("resource_id")}
    except Exception as e:
        return {"err": type(e).__name__, "flag": False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("--only-alive")
    ap.add_argument("-c", "--conc", type=int, default=8)
    ap.add_argument("--json")
    a = ap.parse_args()

    items = D.load_pool(a.pool)
    if a.only_alive:
        alive = {r["name"] for r in json.load(open(a.only_alive, encoding="utf-8"))
                 if r.get("code") == 0}
        items = [it for it in items if it["name"] in alive]
    print("screen %d accounts" % len(items), flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.conc) as ex:
        res = list(ex.map(lambda it: screen_one(it["ck"]), items))
    out = []
    for it, r in zip(items, res):
        out.append({"name": it["name"], "uid": it.get("uid"), **r})
    flagged = [x for x in out if x["flag"]]
    errs = sum(1 for x in out if x.get("err"))
    print("flagged=%d errs=%d (%.1fs)" % (len(flagged), errs, time.time() - t0))
    for x in flagged:
        print("  FLAG", x["name"], x.get("activity"))
    if a.json:
        json.dump({"ts": int(time.time()), "total": len(out), "flagged": flagged, "rows": out},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())