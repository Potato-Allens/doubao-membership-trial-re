import re
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
idxs=[m.start() for m in re.finditer(r'AGWMGetMarketingResourcesV2\(', s)]
print(len(idxs))
for i in idxs:
    print('---',i); print(s[max(0,i-500):i+500].replace('\n',' '))