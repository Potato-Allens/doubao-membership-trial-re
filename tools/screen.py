#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""screen.py -- 资格预筛（R475/R476，read-only）

两种口径：
  init     （默认，ground truth）POST sale/trade/init，读 purchase_card_list 的
           discount_amount / trial_info。eligible = trial_stage==1 且 trial_period_amount==100
           —— 这才是「能不能出 1 元单」的直接判据。
  resource （快，但会漏）POST marketing/resource/mget/v2 看 exit_retention.activity_id
           in {first_purchase_discount, free_trial_v2}。
           注意：用户看过挽留弹窗后客户端会打 frequency/report，服务端把这条「展示资源」
           消费掉（act -> None），但资格（trade/init 的 6700 / stage=1）仍在。
           所以 resource 口径只适合「没弹过窗」的新号，负结果必须用 init 复核。

用法:
  python screen.py --pool pool.json -c 8
  python screen.py --pool pool.json --only-alive scan.json --json screen.json
  python screen.py --pool pool.json --mode resource -c 8
"""
from __future__ import annotations
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doubao_yuan as D

BASE = "https://www.doubao.com"
HIT_ACTS = {"first_purchase_discount", "free_trial_v2"}
SCENE = "default_member_link"


def screen_init(ck):
    s = D.session_of(ck); s.headers.update(D.HEADERS)
    try:
        j = s.post(BASE + "/alice/commerce/sale/trade/init/", params=D.SCOPE_PERSONAL,
                   json={"scene_key": SCENE}, timeout=25).json()
        d = j.get("data") or {}
        best = None
        for sku in d.get("sku_list") or []:
            for c in sku.get("purchase_card_list") or []:
                if best is None or (c.get("discount_amount") or 0) > (best.get("discount_amount") or 0):
                    best = c
        if not best:
            return {"code": j.get("code"), "disc": 0, "stage": None, "eligible": False}
        t = best.get("trial_info") or {}
        stage = t.get("trial_stage")
        amount = t.get("trial_period_amount")
        return {"code": j.get("code"), "disc": best.get("discount_amount") or 0,
                "stage": stage, "trial_amount": amount,
                "eligible": bool(stage == 1 and amount == 100)}
    except Exception as e:
        return {"err": type(e).__name__, "eligible": False}


def screen_resource(ck):
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
    ap.add_argument("--only-alive", help="scan json: only names with code==0")
    ap.add_argument("--mode", choices=["init", "resource"], default="init")
    ap.add_argument("-c", "--conc", type=int, default=8)
    ap.add_argument("--json")
    a = ap.parse_args()

    items = D.load_pool(a.pool)
    if a.only_alive:
        alive = {r["name"] for r in json.load(open(a.only_alive, encoding="utf-8"))
                 if r.get("code") == 0}
        items = [it for it in items if it["name"] in alive]

    fn = screen_init if a.mode == "init" else screen_resource
    key = "eligible" if a.mode == "init" else "flag"
    print("screen %d accounts (mode=%s)" % (len(items), a.mode), flush=True)
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.conc) as ex:
        res = list(ex.map(lambda it: fn(it["ck"]), items))
    out = [{"name": it["name"], "uid": it.get("uid"), **r} for it, r in zip(items, res)]
    hits = [x for x in out if x.get(key)]
    errs = sum(1 for x in out if x.get("err"))
    print("eligible=%d errs=%d (%.1fs)" % (len(hits), errs, time.time() - t0))
    for x in hits:
        extra = ("disc=%s stage=%s" % (x.get("disc"), x.get("stage"))) if a.mode == "init" else x.get("activity")
        print("  HIT", x["name"], extra)
    if a.json:
        json.dump({"ts": int(time.time()), "mode": a.mode, "total": len(out),
                   "hits": hits, "rows": out},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
