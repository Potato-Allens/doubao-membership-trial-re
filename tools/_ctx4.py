import re
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for m in re.finditer(r'resource_keys\s*:', s):
    i=m.start(); print('---',i); print(s[max(0,i-400):i+260].replace('\n',' '))