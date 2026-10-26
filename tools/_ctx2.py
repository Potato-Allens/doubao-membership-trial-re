import re
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for pat in ['resource_keys','resource_key','MGetMarketingResources','mget/v2','activity_key','is_eligible_for_intro_offer']:
    idxs=[m.start() for m in re.finditer(pat,s)]
    print('###',pat,len(idxs))
    for i in idxs[:8]:
        print('---',i)
        print(s[max(0,i-350):i+350].replace('\n',' '))