import re
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
paths=set(re.findall(r'["\'](/alice/[A-Za-z0-9_/\-]+)["\']',s))
print(len(paths))
for p in sorted(paths):
    if any(k in p for k in ('elig','market','campaign','trade','trial','price','discount','promo','benefit','grant','entitle','offer')):
        print(p)