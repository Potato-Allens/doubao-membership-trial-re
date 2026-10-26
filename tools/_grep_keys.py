# -*- coding: utf-8 -*-
import re
b=open("_js_blob.txt",encoding="utf-8").read()
print("feature_key hits",b.count("feature_key"))
for m in list(re.finditer("feature_key",b))[:10]:
    print("  ...",b[max(0,m.start()-150):m.start()+200].replace("\n"," ")[:340])
Q="[\"']"
pat1=re.compile("feature_key\\s*[:=]\\s*"+Q+"([A-Za-z0-9_\\-]{2,40})"+Q)
pat2=re.compile("activity_id\\s*[:=]\\s*"+Q+"([A-Za-z0-9_\\-]{2,40})"+Q)
print("feature_key literals",sorted(set(pat1.findall(b))))
print("activity_id literals",sorted(set(pat2.findall(b))))
print("activity_id hits",b.count("activity_id"))
for m in list(re.finditer("activity_id",b))[:6]:
    print("  A...",b[max(0,m.start()-140):m.start()+180].replace("\n"," ")[:320])