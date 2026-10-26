import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
paths=sorted(set(re.findall(r'["\'](/alice/[A-Za-z0-9_/\-]*(?:refund|debook|revoke|cancel)[A-Za-z0-9_/\-]*)["\']',s)))
print('--- refund paths'); [print(p) for p in paths]
for m in list(re.finditer(r'refund/reasons|debook/reasons|refund/apply|refund/create',s))[:4]:
    i=m.start(); print('---',i); print(s[max(0,i-500):i+400].replace('\n',' '))