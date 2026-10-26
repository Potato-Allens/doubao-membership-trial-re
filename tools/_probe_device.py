import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
def scope(device_id, aid='497858'):
    return {"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web",
     "aid":aid,"real_aid":aid,"pkg_type":"release_version","device_id":device_id,
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
devs=['0000000000000005','0000000000000010','0000000000000002']
for idx in (4,47,53,57):
    a=pool[idx]; s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
    for dv in devs:
        try:
            j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=scope(dv),json={'scene_key':'default_member_link','purchase_channel':2},headers=H,timeout=25).json()
            d=j.get('data') or {}
            best=None
            for sku in d.get('sku_list') or []:
                for c in sku.get('purchase_card_list') or []:
                    if (c.get('discount_amount') or 0)>0 or c.get('trial_info'):
                        best=(sku.get('sku_key'),c.get('card_id'),c.get('discount_amount'),c.get('trial_info'))
            print('idx%-3d dv=%-20s code=%-4s hist=%-5s n=%d %s'%(idx,dv,j.get('code'),d.get('has_history_paid_subscription'),len(d.get('sku_list') or []),best))
        except Exception as e:
            print('idx',idx,dv,'ERR',str(e)[:50])
        time.sleep(0.3)
    print()