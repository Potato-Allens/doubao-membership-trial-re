#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R468 · 从历史目录里回收 sessionid，去重成可用号池。

背景：R468 用它在旧 ck 导出/备份里回收出 508 个 unique sessionid，
      其中 3 个是「1 元 / 7 天」资格号（全部来自 US/HK 注册环境）。

用法:
    python _r468_recover_pool.py --root D:\\ck_export --root D:\\backup --out pool.json
    python _r468_recover_pool.py --root . --out pool.json --exclude pool.json

支持:
    - .json：递归遍历所有字符串值（对象/数组都行）
    - .txt/.log/.csv：逐行匹配
    - 自动跳过 > --max-size 的文件
    - 按 sessionid 去重；同一 sid 保留最长的 cookie 串

只读取本地文件，不发网络请求。校验请配合 doubao_yuan.py scan --validate。
"""
import argparse
import json
import os
import re
import sys

SID_RE = re.compile(r"sessionid=([0-9a-fA-F]{16,})")
ALL_RE = re.compile(r"sessionid=[0-9a-fA-F]{16,}")
EXTS = (".json", ".txt", ".log", ".csv", ".ini", ".yaml", ".yml")


def sid_of(s):
    m = SID_RE.search(s or "")
    return m.group(1).lower() if m else None


def walk_json(obj, found):
    if isinstance(obj, str):
        if "sessionid=" in obj:
            for m in ALL_RE.finditer(obj):
                found.setdefault(sid_of(m.group(0)), obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            walk_json(v, found)
    elif isinstance(obj, list):
        for v in obj:
            walk_json(v, found)


def scan_file(path, found, max_size):
    try:
        if os.path.getsize(path) > max_size:
            return
    except OSError:
        return
    try:
        if path.lower().endswith(".json"):
            walk_json(json.load(open(path, encoding="utf-8-sig")), found)
            return
        for line in open(path, encoding="utf-8", errors="ignore"):
            if "sessionid=" in line:
                for m in ALL_RE.finditer(line):
                    s = sid_of(m.group(0))
                    old = found.get(s)
                    cand = line.strip().strip(",").strip('"')
                    if old is None or len(cand) > len(old):
                        found[s] = cand
    except Exception:
        return


def load_excluded(paths):
    sids = set()
    for p in paths:
        try:
            raw = json.load(open(p, encoding="utf-8"))
            accs = raw["accounts"] if isinstance(raw, dict) else raw
        except Exception:
            continue
        for a in accs:
            if isinstance(a, str):
                s = sid_of(a)
            else:
                s = sid_of(a.get("cookie_string") or a.get("cookie") or "")
            if s:
                sids.add(s)
    return sids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", required=True, help="要扫描的目录（可重复）")
    ap.add_argument("--out", default="recovered_pool.json")
    ap.add_argument("--exclude", action="append", default=[], help="已有号池，按 sessionid 排除")
    ap.add_argument("--max-size", type=int, default=8 * 1024 * 1024)
    a = ap.parse_args()

    found = {}
    files = 0
    for root in a.root:
        for dirpath, _, names in os.walk(root):
            for n in names:
                if n.lower().endswith(EXTS):
                    files += 1
                    scan_file(os.path.join(dirpath, n), found, a.max_size)
    excluded = load_excluded(a.exclude)
    new = {s: c for s, c in found.items() if s not in excluded}
    accs = [{"name": "r%d" % i, "cookie_string": c} for i, c in enumerate(new.values())]
    json.dump({"accounts": accs}, open(a.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("files=%d unique_sid=%d excluded=%d new=%d -> %s"
          % (files, len(found), len(found) - len(new), len(new), os.path.abspath(a.out)))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    main()