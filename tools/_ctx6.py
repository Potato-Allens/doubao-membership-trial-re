import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
for key in ['doubao_member_intro','IntroductoryTrial','scene_not_eligible','moaFE_apply_trial_intro','lastTerminalEligibleCardId']:
    idxs=[m.start() for m in re.finditer(re.escape(key),s)]
    print('#####',key,len(idxs))
    for i in idxs[:4]:
        print('---',i); print(s[max(0,i-450):i+450].replace('\n',' '))