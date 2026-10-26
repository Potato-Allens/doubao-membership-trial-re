#!/usr/bin/env python3
"""qr_batch.py - 循环扫码：每轮出一张登录码，扫完立刻判资格，命中当场出 1 元支付码。

每轮调用 qr_login.py（Playwright 打开登录页 -> 抓 get_qrcode -> 等 session），
把二维码另存到 qr/round_NN.png，结果写进 batch_ledger.jsonl。

用法:
  python tools/qr_batch.py --rounds 20 --timeout 300
  python tools/qr_batch.py --rounds 5 --stop-on-hit
"""
import argparse, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
QRDIR = os.path.join(HERE, "qr")
LEDGER = os.path.join(HERE, "batch_ledger.jsonl")


def run_round(i, timeout):
    t0 = time.time()
    p = subprocess.run([sys.executable, os.path.join(HERE, "qr_login.py"), str(timeout)],
                       cwd=HERE, capture_output=True, text=True, timeout=timeout + 120)
    out = (p.stdout or "") + (p.stderr or "")
    res_path = os.path.join(HERE, "qr_login_result.json")
    state = {}
    if os.path.exists(res_path):
        try:
            state = json.load(open(res_path, encoding="utf-8"))
        except Exception:
            state = {}
    os.makedirs(QRDIR, exist_ok=True)
    qr = os.path.join(HERE, "login_qr.png")
    saved = None
    if state.get("qr_saved") and os.path.exists(qr):
        saved = os.path.join(QRDIR, "round_%02d.png" % i)
        shutil.copy2(qr, saved)
    rec = {"round": i, "ts": int(time.time()), "elapsed": round(time.time() - t0, 1),
           "qr": saved, "uid": state.get("uid"), "hit": bool(state.get("hit")),
           "disc": (state.get("probe") or {}).get("disc"),
           "pay_url": state.get("pay_url"), "order_id": state.get("order_id"),
           "mint_code": state.get("mint_code")}
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=20)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--stop-on-hit", action="store_true")
    a = ap.parse_args()
    hits = []
    for i in range(1, a.rounds + 1):
        rec, out = run_round(i, a.timeout)
        tag = "HIT" if rec["hit"] else ("scan" if rec["uid"] else "no-login")
        print("[round %02d] %-8s uid=%s disc=%s %ss" % (i, tag, rec["uid"], rec["disc"], rec["elapsed"]),
              flush=True)
        if rec["qr"]:
            print("           qr ->", rec["qr"], flush=True)
        if rec["pay_url"]:
            print("           PAY  ->", rec["pay_url"], flush=True)
            hits.append(rec)
        if rec["hit"] and a.stop_on_hit:
            break
    print("\n== batch done ==  rounds=%d hits=%d" % (i, len(hits)))
    for h in hits:
        print("  uid=%s order=%s" % (h["uid"], h["order_id"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())