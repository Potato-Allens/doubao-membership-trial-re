import json,os
from playwright.sync_api import sync_playwright
SCOPE={"version_code":"20800","language":"zh","device_platform":"web","doubao_device_platform":"web","aid":"582478","real_aid":"582478","pkg_type":"release_version","pc_version":"2.33.3","doubao_pc_version":"2.33.3","region":"CN","sys_region":"CN","samantha_web":"1","web_platform":"desktop","use-olympus-account":"1","channel":"win","device_id":"0000000000000002"}
qs="&".join("%s=%s"%(k,v) for k,v in SCOPE.items())
js="""async(qs)=>{
  const r=await fetch('https://www.doubao.com/alice/commerce/sale/trade/init/?'+qs,{
    method:'POST',credentials:'include',
    headers:{'content-type':'application/json','agw-js-conv':'str'},
    body:JSON.stringify({scene_key:'default_member_link'})});
  return {status:r.status, body:(await r.text()).slice(0,600)};
}"""
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp("http://127.0.0.1:9224",timeout=20000)
    ctx=b.contexts[0]
    for pg in ctx.pages[:3]:
        if "doubao" not in (pg.url or ""): continue
        print("PAGE", pg.url[:100])
        try:
            res=pg.evaluate(js,qs)
            print("  ->", res["status"], res["body"][:300].replace("\n"," "))
        except Exception as e:
            print("  ERR", str(e)[:120])
