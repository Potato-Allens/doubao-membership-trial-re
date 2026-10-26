import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for pat in ['activity_id=','?activity','&activity','activity_id":"','campaign_id=','?campaign','invite_code','referral','Referral']:
    idxs=[m.start() for m in re.finditer(re.escape(pat),s)]
    print('#####',pat,len(idxs))
    for i in idxs[:5]:
        print('---',i); print(s[max(0,i-220):i+220].replace('\n',' '))