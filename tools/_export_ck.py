# -*- coding: utf-8 -*-
"""export_ck.py -- 导出客户端当前登录账号的 CK（实时），并验证 + 多格式落盘"""
import json, os, time, requests
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "export")
os.makedirs(OUT, exist_ok=True)
SEP = "; "

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    ctx = b.contexts[0]
    pg = next((x for x in ctx.pages if "doubao" in x.url), ctx.pages[0])
    cdp = ctx.new_cdp_session(pg)
    allc = cdp.send("Network.getAllCookies").get("cookies") or []

# 只取 doubao.com 域下的，按域名优先级去重（.doubao.com 优先）
picked = {}
for c in allc:
    dom = c.get("domain") or ""
    if "doubao.com" not in dom:
        continue
    n = c["name"]
    if n in picked and dom.startswith(".") is False:
        continue
    if n not in picked or dom.startswith("."):
        picked[n] = c
ck_str = SEP.join("%s=%s" % (k, v["value"]) for k, v in sorted(picked.items()))
print("cookies:", len(picked))

# 验证
BASE = "https://www.doubao.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3")
SCOPE = {"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
         "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
         "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
         "web_platform":"desktop","use-olympus-account":"1"}
s = requests.Session()
s.cookies.update({k: v["value"] for k, v in picked.items()})
info = {}
try:
    r = s.get("https://accounts.doubao.com/passport/account/info/v2/?aid=497858",
              headers={"user-agent": UA, "referer": BASE + "/"}, timeout=20).json()
    d = r.get("data") or {}
    info = {"uid": d.get("user_id_str"), "screen_name": d.get("screen_name"),
            "ct": d.get("user_create_time")}
    print("whoami:", json.dumps(info, ensure_ascii=False))
except Exception as e:
    print("whoami err", str(e)[:80])
try:
    ov = s.post(BASE + "/alice/commerce/sale/subscription/overview/", params=SCOPE, json={},
                headers={"content-type":"application/json","agw-js-conv":"str",
                         "referer":BASE+"/member/subscription","origin":BASE,"user-agent":UA},
                timeout=20).json()
    cs = (ov.get("data") or {}).get("current_subscription") or {}
    end = cs.get("end_time")
    print("sub:", cs.get("sku_key"), "| end:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end/1000)) if end else None,
          "| agreement:", cs.get("agreement_status"))
    info["sku"] = cs.get("sku_key")
    info["end_time"] = end
    info["subscription_id"] = cs.get("subscription_id")
except Exception as e:
    print("sub err", str(e)[:80])

uid = info.get("uid") or "unknown"
tagname = "0000000000000001" if uid == "0000000000000001" else uid
# 1) 原始串
open(os.path.join(OUT, tagname + ".txt"), "w", encoding="utf-8").write(ck_str + "\n")
# 2) JSON（含元数据）
json.dump({"uid": uid, "name": info.get("screen_name"), "cookie_string": ck_str,
           "cookies": {k: v["value"] for k, v in sorted(picked.items())},
           "sku": info.get("sku"), "end_time": info.get("end_time"),
           "exported_at": time.strftime("%Y-%m-%d %H:%M:%S")},
          open(os.path.join(OUT, tagname + ".json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
# 3) Playwright storage_state
json.dump({"cookies": [{"name": c["name"], "value": c["value"], "domain": c["domain"],
                        "path": c.get("path", "/"), "expires": c.get("expires", -1),
                        "httpOnly": c.get("httpOnly", False), "secure": c.get("secure", False),
                        "sameSite": (c.get("sameSite") or "Lax")}
                       for c in picked.values()], "origins": []},
          open(os.path.join(OUT, tagname + ".state.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
# 4) Netscape cookies.txt
lines = ["# Netscape HTTP Cookie File"]
for c in picked.values():
    exp = int(c.get("expires") or 0)
    if exp < 0: exp = 0
    dom = c["domain"]
    lines.append("\t".join([dom, "TRUE" if dom.startswith(".") else "FALSE", c.get("path", "/"),
                            "TRUE" if c.get("secure") else "FALSE", str(exp),
                            c["name"], c["value"]]))
open(os.path.join(OUT, tagname + ".cookies.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
# 5) 纯 name=value 一行（给号池用）
open(os.path.join(OUT, tagname + ".oneLine.txt"), "w", encoding="utf-8").write(
    "%s|%s\n" % (tagname, ck_str))

print("\n== 导出完成 ==")
for f in sorted(os.listdir(OUT)):
    if f.startswith(tagname):
        print("  ", os.path.join(OUT, f), os.path.getsize(os.path.join(OUT, f)), "bytes")
print("\ncookie 长度:", len(ck_str))
print("关键字段:", {k: len(picked[k]["value"]) for k in ("sessionid","sid_tt","uid_tt","passport_csrf_token","ttwid") if k in picked})
