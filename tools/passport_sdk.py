#!/usr/bin/env python3
"""Decode ByteDance passport SDK fingerprints (R478).

Two query params on accounts.doubao.com are obfuscated the same way:

    plaintext  ->  hex( bytes(plaintext, "utf-8") XOR 0x05 )

    account_sdk_source_info : browser / automation fingerprint (JSON)
    qs                      : the list of parameter names covered by `sign`

This module is read-only: it never sends a request and never touches cookies.

Usage
-----
    python passport_sdk.py decode 7e276d6477617264...
    python passport_sdk.py capture _passport_reqs.json
    python passport_sdk.py capture _passport_reqs.json --json

`capture` accepts either a JSON list of {url, method, ...} dicts, or a single
URL string. Cookies / tokens are never printed.
"""
from __future__ import annotations

import argparse
import binascii
import json
import sys
import urllib.parse as up

KEY = 0x05


def decode(value: str) -> str:
    """hex(XOR(utf-8, 0x05)) -> plaintext."""
    raw = binascii.unhexlify(value.strip())
    return bytes(b ^ KEY for b in raw).decode("utf-8", "replace")


def encode(plain: str) -> str:
    """Inverse of decode(), handy for building test fixtures."""
    return binascii.hexlify(bytes(b ^ KEY for b in plain.encode("utf-8"))).decode()


def _urls(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        for key in ("url", "request_url", "href"):
            if isinstance(obj.get(key), str):
                return [obj[key]]
        return []
    out: list[str] = []
    if isinstance(obj, list):
        for item in obj:
            out.extend(_urls(item))
    return out


def inspect(urls: list[str]) -> list[dict]:
    rows = []
    for url in urls:
        parsed = up.urlparse(url)
        if "account_sdk_source_info" not in parsed.query and "qs" not in parsed.query:
            continue
        q = up.parse_qs(parsed.query, keep_blank_values=True)
        row = {
            "path": parsed.path,
            "host": parsed.netloc,
            "has_sign": "sign" in q,
            "has_a_bogus": "a_bogus" in q,
        }
        if "qs" in q:
            try:
                row["signed_params"] = decode(q["qs"][0]).split(",")
            except (binascii.Error, ValueError):
                row["signed_params"] = None
        if "account_sdk_source_info" in q:
            try:
                row["sdk_info"] = json.loads(decode(q["account_sdk_source_info"][0]))
            except (binascii.Error, ValueError):
                row["sdk_info"] = None
        if "sign" in q:
            row["sign_len"] = len(q["sign"][0])
        if "a_bogus" in q:
            row["a_bogus_len"] = len(q["a_bogus"][0])
        rows.append(row)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("decode", help="decode one hex value")
    d.add_argument("hex_value")

    c = sub.add_parser("capture", help="decode every matching request in a capture")
    c.add_argument("path")
    c.add_argument("--json", action="store_true", help="emit JSON instead of a summary")
    args = ap.parse_args(argv)

    if args.cmd == "decode":
        print(decode(args.hex_value))
        return 0

    with open(args.path, encoding="utf-8") as fh:
        obj = json.load(fh)
    rows = inspect(_urls(obj))
    if args.json:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    print(f"{len(rows)} request(s) with SDK params")
    for row in rows:
        print(f"- {row['host']}{row['path']}")
        print(f"  sign={row.get('has_sign')} a_bogus={row.get('has_a_bogus')}")
        if row.get("signed_params"):
            print(f"  qs: {','.join(row['signed_params'])}")
        info = row.get("sdk_info") or {}
        if info:
            print(f"  webdriver={info.get('webdriver')} cores={info.get('hardwareConcurrency')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())