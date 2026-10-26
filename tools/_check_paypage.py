import json,requests,re
u=open("_paylink_live.txt",encoding="utf-8").read().strip()
print("len",len(u))
r=requests.get(u,headers={"user-agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148"},timeout=25,allow_redirects=True)
print("status",r.status_code,"final",r.url[:120])
t=r.text
for pat in [r"1\.00", r"68\.00", r"amount[^,;]{0,30}"]:
    m=re.findall(pat,t)[:3]
    if m: print(pat,"->",m)
print("head:",t[:200].replace("\n"," "))
