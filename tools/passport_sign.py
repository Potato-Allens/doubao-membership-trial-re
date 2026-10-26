#!/usr/bin/env python3
"""Rebuild ByteDance passport `sign` / `qs` (R479).

The passport SDK (dg.*.js, jssdk 4.4.6) signs requests like this:

    keys   = sorted(params)[:10]                  # splice(10)
    pstr   = "&".join(f"{k}={v}" for k in keys)   # objects -> JSON.stringify
    bstr   = same for the request body
    sign   = sha256(f"{pstr}&{bstr}&app_key={APP_KEY}").hexdigest()
    qs     = hex( (",".join(keys)).encode() XOR 0x05 )

Only the first ten keys (alphabetical) are covered. `ts`, `sign`, `qs`,
`a_bogus` are added *after* signing and must be excluded from the input.

The app key below is Doubao's public web app key (aid=497858); it is not a
credential. Everything here is offline and read-only.

Usage
-----
    python passport_sign.py --selftest _passport_reqs.json
    python passport_sign.py --params aid=497858 --params language=zh
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse as up

APP_KEY = "2094abfcccefaeaffd24c622475fba10"
SKIP = {"sign", "qs", "ts", "a_bogus"}


def _js_str(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _flat(obj: dict, keep: int | None = None) -> tuple[str, list[str]]:
    keys = sorted(obj.keys())
    if keep is not None:
        keys = keys[:keep]
    return "&".join(f"{k}={_js_str(obj[k])}" for k in keys), keys


def xor5(text: str) -> str:
    """Same encoder the SDK uses for `qs` (one hex byte per char, no padding)."""
    return "".join(format(b ^ 0x05, "x") for b in text.encode("utf-8"))


def sign(params: dict, data: dict | None = None, app_key: str = APP_KEY) -> dict:
    data = data or {}
    pstr, keys = _flat(params, 10)
    dstr, _ = _flat(data)
    raw = f"{pstr}&{dstr}&app_key={app_key}"
    return {
        "sign": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "qs": xor5(",".join(keys)),
        "raw": raw,
    }


def selftest(path: str) -> int:
    reqs = json.load(open(path, encoding="utf-8"))
    ok = 0
    for i, req in enumerate(reqs):
        url = req["url"] if isinstance(req, dict) else req
        q = up.parse_qs(up.urlparse(url).query, keep_blank_values=True)
        given_sign = q.pop("sign", [""])[0]
        given_qs = q.pop("qs", [""])[0]
        for key in SKIP:
            q.pop(key, None)
        params = {k: v[0] for k, v in q.items()}
        body = {}
        for part in ((req.get("post") or "") if isinstance(req, dict) else "").split("&"):
            if "=" in part:
                k, v = part.split("=", 1)
                body[up.unquote_plus(k)] = up.unquote_plus(v)
        got = sign(params, body)
        good = got["sign"] == given_sign and got["qs"] == given_qs
        ok += good
        print(f"[{i}] {'OK ' if good else 'FAIL'} {up.urlparse(url).path}")
    print(f"{ok}/{len(reqs)} reproduced")
    return 0 if ok == len(reqs) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", metavar="CAPTURE.json", help="verify against captured URLs")
    ap.add_argument("--params", action="append", default=[], metavar="K=V", help="parameter (repeatable)")
    ap.add_argument("--json", action="store_true", help="print raw JSON")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(args.selftest)

    if not args.params:
        ap.print_help()
        return 2
    params = dict(item.split("=", 1) for item in args.params)
    out = sign(params)
    if args.json:
        json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(out["sign"])
        print(out["qs"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())