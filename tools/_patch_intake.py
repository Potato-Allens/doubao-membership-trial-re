# -*- coding: utf-8 -*-
p="intake.py"
s=open(p,encoding="utf-8").read()
old = (
'        d = r.get("data") or {}\n'
'        who = {"uid": d.get("user_id_str"), "name": d.get("screen_name"),\n'
'               "ct": d.get("user_create_time"), "code": r.get("code")}\n'
'        if r.get("code") != 0:\n'
'            return {"ok": False, "reason": "login_invalid", **who}\n'
)
new = (
'        d = r.get("data") or {}\n'
'        who = {"uid": d.get("user_id_str"), "name": d.get("screen_name"),\n'
'               "ct": d.get("user_create_time")}\n'
'        if not d.get("user_id_str"):\n'
'            return {"ok": False, "reason": "login_invalid", **who}\n'
)
assert old in s, "block not found"
open(p,"w",encoding="utf-8").write(s.replace(old,new))
print("patched")