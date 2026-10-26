import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for pat in ['PROFESSIONAL_BETA_LANDING','nF=','BETA_LANDING']:
    idxs=[m.start() for m in re.finditer(re.escape(pat),s)]
    print('#####',pat,len(idxs))
    for i in idxs[:6]:
        print('---',i); print(s[max(0,i-400):i+400].replace('\n',' '))