import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for key in ['fission/entrance','fission/home_page','fission/draw','benefit_supply']:
    idxs=[m.start() for m in re.finditer(re.escape(key),s)]
    print('#####',key,len(idxs))
    for i in idxs[:3]:
        print('---',i); print(s[max(0,i-600):i+400].replace('\n',' '))