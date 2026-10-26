import json, requests, sys, io, time
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
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
s=requests.Session(); s.cookies.update(ck(pool[4]['cookie_string']))
keys=['member_page','member_page_init','professional_beta','professional_beta_landing','pro_beta','beta',
 'ug_free_subs_download_pc','ug_free_subs_landing','scene_default_v1','direct_landing','launch_landing',
 'landing','guest_landing','campaign','member','subscription','doubao_member','pc_new_user_campaign',
 'download-doubao-gift-toaster','default_member_link','member_subscription','subs_member','professional']
for k in keys:
    try:
        j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=SCOPE,json={'scene_key':k},headers=H,timeout=20).json()
        d=j.get('data') or {}
        skus=[x.get('sku_key') for x in (d.get('sku_list') or [])]
        discs=[(c.get('card_id'),c.get('discount_amount'),bool(c.get('trial_info'))) for x in (d.get('sku_list') or []) for c in (x.get('purchase_card_list') or []) if (c.get('discount_amount') or 0)>0]
        print('%-28s code=%-6s n=%d skus=%s disc=%s'%(k,j.get('code'),len(skus),skus[:4],discs[:3]))
    except Exception as e:
        print(k,'ERR',str(e)[:50])
    time.sleep(0.25)