#!/usr/bin/env python3
"""R467 · samantha/fission 族探测（schema 复核 + 入口枚举）

关键点（R467 实测）:
  - enterprise/entrance 的 enter_from 是 **int 枚举**: 0=Desktop, 1=Web
  - activity_id 必须是 int；未存在的 id → 710022001 record not found
  - share_info / check 都是"先查记录再校验"，空参不会通过

用法:
    python _r467_fission_probe.py --pool ../data/sample_pool.json
"""
import argparse
import json
import sys
import time

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


def pick_account(pool_path):
    raw = json.load(open(pool_path, encoding="utf-8"))
    accounts = raw["accounts"] if isinstance(raw, dict) else raw
    for idx, it in enumerate(accounts):
        it = dict(it)
        ck = it.get("cookie_string")
        if not ck and isinstance(it.get("ck"), dict):
            ck = "; ".join("%s=%s" % (k, v) for k, v in it["ck"].items())
        if not ck:
            continue
        s = requests.Session()
        s.cookies.update(cookie_dict(ck))
        s.headers.update(HEADERS)
        try:
            j = s.get(BASE + "/samantha/fission/entrance",
                      params={**SCOPE, "enter_from": 1}, timeout=15).json()
        except Exception:
            continue
        if j.get("code") == 0:
            print(">>> use account[%d] name=%s" % (idx, it.get("name") or idx))
            return s
    raise SystemExit("no usable account in pool")


def call(s, method, ep, params=None, body=None):
    r = s.request(method, BASE + ep,
                  params={**SCOPE, **(params or {})},
                  json=body if body is not None else None, timeout=20)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, r.text[:160]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True)
    a = ap.parse_args()
    s = pick_account(a.pool)

    print("\n--- entrance: int enum (0=Desktop, 1=Web) vs string")
    for ef in (0, 1, "chat", "member", ""):
        st, j = call(s, "GET", "/samantha/fission/entrance", {"enter_from": ef})
        print(" enter_from=%-8r http=%s %s" % (ef, st, json.dumps(j, ensure_ascii=False)[:240]))
        time.sleep(0.2)

    print("\n--- home_page: int namespace")
    for aid in ("", 1, 100, 1000, 2026, 999999, 10 ** 8):
        st, j = call(s, "GET", "/samantha/fission/home_page", {"activity_id": aid})
        print(" activity_id=%-9r http=%s %s" % (aid, st, json.dumps(j, ensure_ascii=False)[:200]))
        time.sleep(0.2)

    print("\n--- share_info / check / draw / auth/grant")
    cases = [
        ("GET", "/samantha/fission/share_info", {"invited_code": "abc123", "activity_id": 1}, None),
        ("POST", "/samantha/fission/check", None, {"data": ""}),
        ("POST", "/samantha/fission/draw", None, {"is_exchange": False, "activity_id": 1}),
        ("POST", "/alice/auth/grant", None, {"order_id": "", "src_platform": 1, "trigger": 1}),
    ]
    for method, ep, params, body in cases:
        st, j = call(s, method, ep, params, body)
        print(" %-34s http=%s %s" % (ep, st, json.dumps(j, ensure_ascii=False)[:220]))
        time.sleep(0.2)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()