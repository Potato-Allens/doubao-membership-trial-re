import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
qs=sorted(set(re.findall(r'["\']([a-z0-9_]{3,60})["\']',s)))
cand=[q for q in qs if any(k in q for k in ('scene','landing','beta','member_page','subs_page','page_key'))]
print(len(cand))
for q in cand: print(q)
print('=== scene_key: assignments')
for m in list(re.finditer(r'scene_key\s*[:=]\s*["\']([^"\']+)',s))[:40]:
    print(m.group(1))