import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for key in ['ug/campaign/list','ug/campaign/v3/detail','ug/campaign/landing/get','ug/campaign/item/reward/claim']:
    idxs=[m.start() for m in re.finditer(re.escape(key),s)]
    print('#####',key,len(idxs))
    for i in idxs[:3]:
        print('---',i); print(s[max(0,i-600):i+400].replace('\n',' '))