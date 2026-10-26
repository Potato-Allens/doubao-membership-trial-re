import re
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for pat in [r'\(0,eY\)', r'[^A-Za-z0-9_]eY\)', r'eY\(']:
    idxs=[m.start() for m in re.finditer(pat,s)]
    print('###',pat,len(idxs))
    for i in idxs[:10]:
        print('---',i); print(s[max(0,i-300):i+200].replace('\n',' '))