import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for key in ['BetaCheck','BetaActivity','beta/check','BetaActivityState']:
    idxs=[m.start() for m in re.finditer(key,s)]
    print('#####',key,len(idxs))
    for i in idxs[:8]:
        print('---',i); print(s[max(0,i-300):i+300].replace('\n',' '))