#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""watch_activity2.py -- 资格状态观测器（R476）

每轮对每个号记录**全量**状态：
  activity  来自 marketing/resource/mget/v2 的 exit_retention.activity_id（可为 None）
  disc/stage 来自 sale/trade/init（ground truth）
用途：回答「标记会不会漂 / 资格会不会过期 / 未命中的号会不会后来被选中」。
只读，不建单，**不调 frequency/report**（那个会消费展示资源）。

用法:
  python watch_activity2.py --pool pool/trial_batch_all2.json --screen _r476_init_all.json --extra 12
  python watch_activity2.py --names names.txt --interval 60 --hours 6
"""
from __future__ import annotations
import argparse, json, os, random, sys, time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doubao_yuan as D

LOG = os.path.join(HERE, "activity_watch2.jsonl")
BASE = "https://www.doubao.com"


def probe(ck):
    s = D.session_of(ck); s.headers.update(D.HEADERS)
    act = None
    try:
        j = s.post(BASE + "/alice/commerce/marketing/resource/mget/v2/", params=D.SCOPE_PERSONAL,
                   json={"resource_keys": ["exit_retention"]}, timeout=20).json()
        r = ((j.get("data") or {}).get("results") or {}).get("exit_retention") or {}
        act = r.get("activity_id")
    except Exception as e:
        act = "ERR:" + type(e).__name__
    disc = stage = None
    try:
        sc = D.init_scan(s, D.SCOPE_PERSONAL)
        disc = sc.get("disc"); stage = (sc.get("trial") or {}).get("trial_stage")
    except Exception:
        pass
    return {"act": act, "disc": disc, "stage": stage}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=os.path.join(HERE, "pool", "trial_batch_all2.json"))
    ap.add_argument("--screen", help="screen.py --json 输出；取 hits 加 --extra 个随机对照")
    ap.add_argument("--extra", type=int, default=10)
    ap.add_argument("--names", help="一行一个 name")
    ap.add_argument("--interval", type=int, default=60)
    ap.add_argument("--hours", type=float, default=6)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()

    items = {it["name"]: it for it in D.load_pool(a.pool)}
    names = []
    if a.names:
        names = [l.strip() for l in open(a.names, encoding="utf-8") if l.strip()]
    if a.screen:
        d = json.load(open(a.screen, encoding="utf-8"))
        names += [x["name"] for x in d.get("hits") or []]
        pool = [n for n in items if n not in names]
        random.shuffle(pool)
        names += pool[:a.extra]
    names = list(dict.fromkeys(names))
    print("watch2 %d accounts, every %ds for %.1fh" % (len(names), a.interval, a.hours), flush=True)
    end = time.time() + a.hours * 3600
    rnd = 0
    prev = {}
    while time.time() < end:
        rnd += 1; t0 = time.time()
        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            res = list(ex.map(lambda n: probe(items[n]["ck"]), names))
        row = {"ts": int(time.time()), "round": rnd,
               "rows": [{"name": n, **r} for n, r in zip(names, res)]}
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        ch = [(x["name"], prev[x["name"]], (x["act"], x["disc"], x["stage"]))
              for x in row["rows"] if x["name"] in prev and prev[x["name"]] != (x["act"], x["disc"], x["stage"])]
        prev = {x["name"]: (x["act"], x["disc"], x["stage"]) for x in row["rows"]}
        elig = sum(1 for x in row["rows"] if x["stage"] == 1 and x["disc"] == 6700)
        print("round %d: eligible=%d changes=%d (%.1fs)" % (rnd, elig, len(ch), time.time() - t0), flush=True)
        for c in ch:
            print("   CHANGE", c[0], c[1], "->", c[2], flush=True)
        time.sleep(max(5, a.interval - (time.time() - t0)))
    print("done rounds=%d" % rnd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
