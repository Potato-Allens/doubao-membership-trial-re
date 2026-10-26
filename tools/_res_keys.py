import re,sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
print('=== web blob literal arrays')
for m in re.finditer(r'resource_keys\s*:\s*\[([^\]]{0,300})\]',s):
    print('  ',m.group(1)[:300])
print('=== client literal arrays')
root=r"D:\1\OpenAI.Codex_26.715.3651.0_x64(免安装版 适合大多数电脑)\data\AppData\Local\Doubao\Application\app\local_webcontents"
for dp,dn,fn in os.walk(root):
    for f in fn:
        if not f.lower().endswith('.js'): continue
        p=os.path.join(dp,f)
        try:
            if os.path.getsize(p)>6*1024*1024: continue
            t=open(p,encoding='utf-8',errors='ignore').read()
        except: continue
        for m in re.finditer(r'resource_keys\s*:\s*\[([^\]]{0,300})\]',t):
            print('  %-28s %s'%(f,m.group(1)[:260]))