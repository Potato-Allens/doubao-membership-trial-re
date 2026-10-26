# -*- coding: utf-8 -*-
p="doubao_yuan.py"; s=open(p,encoding="utf-8").read()
old='    st = post_json(s, EP_STATUS, {"required_fields": [2], "product_lines": ["membership"]}, scope)'
new='''    st = post_json(s, EP_STATUS, {}, scope)
    if not (st.get("data") or {}):
        st = post_json(s, EP_STATUS, {"required_fields": [2], "product_lines": ["membership"]}, scope)'''
assert old in s; s=s.replace(old,new,1)
old2='''    if str(snap.get("has_subscribed")).lower() != "true" and not a.sid:
        print("account is not subscribed -> nothing to cancel"); return 3'''
new2='''    if snap.get("has_subscribed") is False and not a.sid and not snap.get("subscription_id"):
        print("account is not subscribed -> nothing to cancel"); return 3'''
assert old2 in s; s=s.replace(old2,new2,1)
open(p,"w",encoding="utf-8").write(s)
print("ok")
