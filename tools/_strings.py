import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
qs=set(re.findall(r'["\']([A-Za-z0-9_\-]{3,60})["\']',s))
for q in sorted(qs):
    if 'intro' in q.lower() or 'eligib' in q.lower():
        print('Q',q)