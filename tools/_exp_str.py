import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
qs=set(re.findall(r'["\']([A-Za-z0-9_\-\.]{4,70})["\']',s))
for q in sorted(qs):
    if 'experiment' in q.lower() or q.lower().startswith('exp_') or 'abtest' in q.lower() or 'ab_test' in q.lower():
        print('Q',q)
print('=== occurrences of experiment')
for m in list(re.finditer('experiment',s,re.I))[:10]:
    i=m.start(); print('---',i); print(s[max(0,i-200):i+200].replace('\n',' '))