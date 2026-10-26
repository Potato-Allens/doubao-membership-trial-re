import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
 "aid":"497858","real_aid":"497858","pkg_type":"release_version","device_id":"0000000000000005",
 "pc_version":"0.1.0","doubao_pc_version":"0.1.0","region":"CN","sys_region":"CN",
 "samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
H={"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
   "origin":BASE,"user-agent":UA,"accept":"application/json, text/plain, */*"}
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
keys=["subscription_bottom_toast","exit_retention","member_trial","member_trial_offer","trial_offer",
"intro_offer","first_purchase_trial","first_purchase_offer","first_purchase_discount","new_user_trial",
"new_user_gift","new_user_campaign","member_page","member_page_banner","member_center","subscription_page",
"price_tag","price_label","price_badge","discount_badge","campaign_entry","activity_entry","activity_banner",
"home_banner","sidebar_banner","professional_beta","beta_landing","professional_beta_landing",
"doubao_member_trial","doubao_member_intro","renewal_guidance_v1","free_trial","trial_banner",
"student_offer","edu_offer","edu_discount","pc_new_user","pc_new_user_campaign","download_gift",
"gift_toaster","download-doubao-gift-toaster","ug_free_subs_download_pc","member_trial_banner",
"member_benefit","member_price_toast","subscription_entry","subscription_banner","subscribe_entry",
"pay_success_toast","cancel_retention","downgrade_retention","upgrade_guidance","trial_reminder",
"trial_expire_reminder","member_expire_reminder","member_renewal_toast","first_purchase_banner"]
for idx in (4,120):
    a=pool[idx]; s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
    try:
        j=s.post(BASE+'/alice/commerce/marketing/resource/mget/v2/',params=SCOPE,
                 json={'resource_keys':keys,'is_eligible_for_intro_offer':True},headers=H,timeout=30).json()
    except Exception as e:
        print(idx,'ERR',e); continue
    res=(j.get('data') or {}).get('results') or {}
    print('### idx',idx,a.get('uid'),'code',j.get('code'),'returned keys',len(res))
    for k,v in res.items():
        print('   %-32s activity_id=%-24s hit=%s'%(k,(v or {}).get('activity_id'),(v or {}).get('hit')))
    print()
    time.sleep(0.5)