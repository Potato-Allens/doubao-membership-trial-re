import json, requests, sys, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
BASE='https://www.doubao.com'
UA_PC=('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 SamanthaDoubao/2.33.3')
def scope(aid, pc=True):
    return {"version_code":"20800","language":"zh","device_platform":"web" if not pc else "pc",
     "doubao_device_platform":"web","aid":str(aid),"real_aid":str(aid),
     "pkg_type":"release_version","pc_version":"0.1.0","doubao_pc_version":"0.1.0",
     "region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1"}
def H():
    return {"content-type":"application/json","agw-js-conv":"str","referer":BASE+"/member/subscription",
     "origin":BASE,"user-agent":UA_PC,"accept":"application/json, text/plain, */*"}
def ck(s):
    d={}
    for p in s.split(';'):
        if '=' in p:
            k,v=p.split('=',1); d[k.strip()]=v.strip()
    return d
pool=json.load(open('pool/trial_batch_212.json',encoding='utf-8'))['accounts']
amap={r['uid']:r for r in json.load(open('app_id_map.json',encoding='utf-8')) if r.get('app')}
idx_of={a.get('uid'):i for i,a in enumerate(pool)}
picks=[(i,pool[i]) for i in range(len(pool)) if amap.get(pool[i].get('uid'),{}).get('app')==582478][:4]
picks+= [(idx_of['0000000000000006'],pool[idx_of['0000000000000006']]),(idx_of['0000000000000001'],pool[idx_of['0000000000000001']])]
for i,a in picks:
    s=requests.Session(); s.cookies.update(ck(a['cookie_string']))
    for aid in (582478,497858,1128):
        try:
            j=s.post(BASE+'/alice/commerce/sale/trade/init/',params=scope(aid),json={'scene_key':'default_member_link'},headers=H(),timeout=20).json()
            d=j.get('data') or {}
            best=None
            for sku in d.get('sku_list') or []:
                for c in sku.get('purchase_card_list') or []:
                    if (c.get('discount_amount') or 0)>0 or c.get('trial_info'):
                        best=(sku.get('sku_key'),c.get('discount_amount'),c.get('trial_info'),c.get('button_text'))
            print('idx%-4d app=%-7s aid=%-7s code=%-4s n=%d %s'%(i,amap.get(a.get('uid'),{}).get('app'),aid,j.get('code'),len(d.get('sku_list') or []),best))
        except Exception as e:
            print('idx',i,'aid',aid,'ERR',str(e)[:40])
        time.sleep(0.25)
    print()