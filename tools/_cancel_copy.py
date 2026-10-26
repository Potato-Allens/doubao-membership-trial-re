# -*- coding: utf-8 -*-
import re, json
t=open("_cancel_ctx.txt",encoding="utf-8").read()
print("file len",len(t))
# 1) 找中文串里含 续费/失效/取消/退 的片段
pat=re.compile(r'[\u4e00-\u9fa5，。！？、：""''（）\w ]{0,40}(?:自动续费|续费|失效|取消订阅|解约|退款)[\u4e00-\u9fa5，。！？、：""''（）\w ]{0,60}')
hits=[]
for m in pat.finditer(t):
    s=m.group(0).strip()
    if len(s)>=4: hits.append(s)
uniq=[]
for h in hits:
    if h not in uniq: uniq.append(h)
print("--- 中文文案 ---")
for h in uniq[:40]: print("  ",h)
# 2) 找 AGWCancelSubscription 调用点上下文
for m in re.finditer(r'AGWCancelSubscription',t):
    seg=t[max(0,m.start()-300):m.start()+200].replace("\n"," ")
    print("--- call site ---"); print(seg[:500])
