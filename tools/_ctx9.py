import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for m in re.finditer(r'activity_key\s*:', s):
    i=m.start()
    seg=s[max(0,i-260):i+260].replace('\n',' ')
    if 'activity_key:e.activity_key' in seg: continue
    print('---',i); print(seg)
print('### activityKey')
for m in re.finditer(r'activityKey', s):
    i=m.start(); print('---',i); print(s[max(0,i-200):i+200].replace('\n',' '))