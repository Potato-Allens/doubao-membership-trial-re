import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
idxs=[m.start() for m in re.finditer('page_status',s)]
print('count',len(idxs))
for i in idxs[:12]:
    print('---',i); print(s[max(0,i-350):i+250].replace('\n',' '))