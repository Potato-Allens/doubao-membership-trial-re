#!/usr/bin/env python3
"""R467 · fission 入口全池扫描

对池内每个账号打 GET /samantha/fission/entrance?enter_from=0|1，
统计 show_entrance / show_popup / activity_info / entrance_banner。

结论（2026-10-27 实测）: 212/212 code=0，hits=0 —— entrance 是活动级开关，
当前没有在投放的 fission 活动，不是 uid 资格。

用法:
    python _r467_fission_sweep.py --pool ../data/sample_pool.json -c 8
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import requests

BASE = "https://www.doubao.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE = {
    "version_code": "20800", "language": "zh", "device_platform": "web",
    "doubao_device_platform": "web", "aid": "497858", "real_aid": "497858",
    "pkg_type": "release_version", "pc_version": "0.1.0",
    "doubao_pc_version": "0.1.0", "region": "CN", "sys_region": "CN",
    "samantha_web": "1", "web_platform": "desktop", "use-olympus-account": "1",
}
HEADERS = {
    "content-type": "application/json", "agw-js-conv": "str",
    "referer": BASE + "/", "origin": BASE, "user-agent": UA,
    "accept": "application/json, text/plain, */*",
}


def cookie_dict(s):
    d = {}
    for part in s.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            d[k.strip()] = v.strip()
    return d


def load(path):
    raw = json.load(open(path, encoding="utf-8"))
    return raw["accounts"] if isinstance(raw, dict) else raw


def one(args):
    idx, it = args
    ck = it.get("cookie_string")
    if not ck and isinstance(it.get("ck"), dict):
        ck = "; ".join("%s=%s" % (k, v) for k, v in it["ck"].items())
    if not ck:
        return idx, it.get("name") or str(idx), None
    s = requests.Session()
    s.cookies.update(cookie_dict(ck))
    s.headers.update(HEADERS)
    out = {}
    for ef in (0, 1):
        try:
            out[ef] = s.get(BASE + "/samantha/fission/entrance",
                            params={**SCOPE, "enter_from": ef}, timeout=15).json()
        except Exception as e:
            out[ef] = {"code": "ERR", "message": str(e)[:80]}
    return idx, it.get("name") or str(idx), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    ap.add_argument("-c", "--concurrency", type=int, default=8)
    ap.add_argument("--json", default="_r467_fission_sweep.json")
    a = ap.parse_args()
    pool = load(a.pool)
    live = 0
    hits = []
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        for idx, name, out in ex.map(one, list(enumerate(pool))):
            j = (out or {}).get(1) or {}
            if j.get("code") == 0:
                live += 1
                d = j.get("data") or {}
                if (d.get("show_entrance") or d.get("show_popup")
                        or d.get("show_settings_entrance") or d.get("activity_info")
                        or d.get("entrance_banner")):
                    hits.append({"idx": idx, "name": name, "data": d})
                    print("HIT", idx, name, json.dumps(d, ensure_ascii=False)[:400])
    print("pool=%d live(code=0)=%d hits=%d" % (len(pool), live, len(hits)))
    json.dump({"pool": len(pool), "live": live, "hits": hits},
              open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()