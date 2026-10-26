import os,re,io,sys,json,collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
root=r"D:\1\OpenAI.Codex_26.715.3651.0_x64(免安装版 适合大多数电脑)\data\AppData\Local\Doubao\Application\app\local_webcontents"
print("exists",os.path.exists(root))
pat=re.compile(r'campaign_group_code["\']?\s*[:=]\s*["\']([A-Za-z0-9_\-]{3,60})["\']')
c=collections.Counter(); files=0
for dp,dn,fn in os.walk(root):
    for f in fn:
        if not f.endswith((".js",".json",".html")): continue
        p=os.path.join(dp,f)
        try:
            if os.path.getsize(p)>8*1024*1024: continue
            s=open(p,encoding="utf-8",errors="ignore").read()
        except Exception: continue
        files+=1
        for m in pat.finditer(s): c[m.group(1)]+=1
print("files",files); print(json.dumps(c.most_common(40),ensure_ascii=False))
