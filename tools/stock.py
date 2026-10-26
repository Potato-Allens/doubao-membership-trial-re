#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stock.py -- 资格库存 + 保底出码（R474）

目标：把「一单一元」从抽奖变成库存管理。
  · 每次扫码/回收账号后，read-only 打 trade/init，命中即入库（不消耗资格）
  · 出码时永远从「已验证仍带 trial_stage=1」的库存里取，永不把没验过的号递出去

用法:
  python stock.py                 # 看库存（会实时复验，不建单）
  python stock.py --mint          # 从库存里取一个，直接出 ¥1 支付链接 + 二维码
  python stock.py --mint --uid 639260239604313
  python stock.py --refresh       # 扫 pool/live_intake.jsonl 的新号，命中的自动入库
  python stock.py --json stock.json
"""
from __future__ import annotations
import argparse, json, os, sys, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import doubao_yuan as D   # SCOPE_PERSONAL / HEADERS / init_scan / mint / load_pool

HITS = os.path.join(HERE, "pool", "hits_1yuan.json")
LIVE = os.path.join(HERE, "pool", "live_intake.jsonl")


def parse(s):
    return D.ck_dict(s) or {}


def load_hits():
    if not os.path.exists(HITS):
        return []
    obj = json.load(open(HITS, encoding="utf-8"))
    acc = obj.get("accounts") if isinstance(obj, dict) else obj
    out = []
    for a in acc or []:
        ck = parse(a.get("cookie_string") or a.get("ck") or a)
        if ck:
            out.append({"name": a.get("name") or a.get("uid") or "hit", "uid": a.get("uid"), "ck": ck})
    return out


def save_hits(items):
    acc = [{"name": it["name"], "uid": it["uid"], "cookie_string": "; ".join("%s=%s" % kv for kv in it["ck"].items())}
           for it in items]
    json.dump({"accounts": acc}, open(HITS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def verify(item):
    s = D.session_of(item["ck"])
    s.headers.update(D.HEADERS)
    who = D.whoami(s, D.SCOPE_PERSONAL)
    r = D.init_scan(s, D.SCOPE_PERSONAL)
    item.update(uid=who.get("uid") or item.get("uid"), cc=who.get("cc"), ct=who.get("ct"),
                disc=r.get("disc"), stage=(r.get("trial") or {}).get("trial_stage"),
                elig=((json.loads(r["extra"]) if isinstance(r.get("extra"), str) and r.get("extra") else {}).get("selected_eligibility_id")),
                code=r.get("code"))
    item["live"] = bool((r.get("disc") or 0) >= 6000 and item["stage"] == 1)
    return item


def refresh():
    """把 live_intake.jsonl 里扫码进来的新号全部验一遍，命中就入库。"""
    seen = {it["ck"].get("sessionid") for it in load_hits()}
    added = 0
    if os.path.exists(LIVE):
        for line in open(LIVE, encoding="utf-8"):
            line = line.strip()
            if not line or "|" not in line:
                continue
            uid, ck = line.split("|", 1)
            c = parse(ck)
            if not c or c.get("sessionid") in seen:
                continue
            it = verify({"name": "live_%s" % uid, "uid": uid.strip(), "ck": c})
            if it["live"]:
                h = load_hits() + [it]
                save_hits(h)
                seen.add(c.get("sessionid"))
                added += 1
                print("  + %s cc=%s elig=%s" % (it["uid"], it.get("cc"), it.get("elig")))
    return added


def mint_one(item, qr=None):
    s = D.session_of(item["ck"]); s.headers.update(D.HEADERS)
    r = D.init_scan(s, D.SCOPE_PERSONAL)
    extra = r.get("extra")
    m = D.mint(s, D.SCOPE_PERSONAL, extra)
    if m.get("pay_url") and qr:
        try:
            import qrcode
            qrcode.make(m["pay_url"]).save(qr)
        except Exception as e:
            print("qr err", e)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mint", action="store_true")
    ap.add_argument("--uid")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--json")
    ap.add_argument("--qr", default=os.path.join(HERE, "pay_stock.png"))
    a = ap.parse_args()

    if a.refresh:
        print("refresh from live_intake ...")
        print("added", refresh())

    items = load_hits()
    if not items:
        print("库存为空：先跑 qr_batch / qr_login 扫码，再 --refresh")
        return 2
    for it in items:
        verify(it)
        print("%-4s %-18s cc=%-4s disc=%-5s stage=%-4s elig=%s" %
              ("LIVE" if it["live"] else "dead", it["uid"], it.get("cc"), it.get("disc"),
               it.get("stage"), it.get("elig")))
    live = [x for x in items if x["live"]]
    uids = {str(x["uid"]) for x in live}
    print("STOCK=%d uid  (rows=%d, total in file=%d)" % (len(uids), len(live), len(items)))
    if a.json:
        json.dump({"ts": int(time.time()), "stock": len(uids), "uids": sorted(uids), "items": items},
                  open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if a.mint:
        cand = [x for x in live if not a.uid or str(x["uid"]) == str(a.uid)]
        if not cand:
            print("没有可用库存 -> 需要新号（扫码）")
            return 3
        it = cand[0]
        m = mint_one(it, a.qr)
        print("MINT uid=%s code=%s order=%s expire=%ss" % (it["uid"], m.get("code"), m.get("order_id"), m.get("expire_seconds")))
        print("PAY", m.get("pay_url"))
        if m.get("pay_url"):
            print("QR", a.qr)
    return 0


if __name__ == "__main__":
    sys.exit(main())