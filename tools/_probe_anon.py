import json, requests, sys, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","pc_version":"0.1.0",
 "doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN","samantha_web":"1",
 "web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
s=requests.Session()
for body in ({}, {'page_type':0}):
    j=s.post(BASE+'/alice/commerce/sale/campaign/page/query/',params=SCOPE,json=body,headers=H,timeout=20).json()
    print('anon',json.dumps(j,ensure_ascii=False))
j=s.post(BASE+'/alice/commerce/incentive/campaign/pc_new_user_page/detail/',params=SCOPE,json={'campaign_id':'pc_new_user_campaign'},headers=H,timeout=20).json()
print('anon pcnew',json.dumps(j,ensure_ascii=False)[:400])