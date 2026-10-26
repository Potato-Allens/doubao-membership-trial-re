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
for idx in (4,47):
    print('### idx',idx)
    s=requests.Session(); s.cookies.update(ck(pool[idx]['cookie_string']))
    for ch in range(0,21):
        body={'scene_key':'default_member_link','purchase_channel':ch}
        try:
            j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=SCOPE,json=body,headers=H,timeout=20).json()
            d=j.get('data') or {}
            best=None
            for sku in d.get('sku_list') or []:
                for c in sku.get('purchase_card_list') or []:
                    if (c.get('discount_amount') or 0)>0 or c.get('trial_info'):
                        best=(sku.get('sku_key'),c.get('card_id'),c.get('discount_amount'),c.get('trial_info'),c.get('button_text'),c.get('trade_extra'))
            print('  ch=%-3d code=%-6s n=%d %s'%(ch,j.get('code'),len(d.get('sku_list') or []),best))
        except Exception as e:
            print('  ch',ch,'ERR',str(e)[:40])
        time.sleep(0.2)