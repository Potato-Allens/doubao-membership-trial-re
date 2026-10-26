import re,io,sys,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
root=r"D:\1\OpenAI.Codex_26.715.3651.0_x64(免安装版 适合大多数电脑)\data\AppData\Local\Doubao\Application\app\local_webcontents\extensions\ai-views\static\js\async"
for f in ("10102.js","15504.js"):
    p=os.path.join(root,f)
    s=open(p,encoding="utf-8",errors="ignore").read()
    print("="*20,f,len(s))
    for m in list(re.finditer(r'campaign_group_code',s))[:4]:
        i=m.start(); print("  @%d %s"%(i,s[max(0,i-420):i+320].replace("\n"," ")[:740])); print()