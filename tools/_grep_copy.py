# -*- coding: utf-8 -*-
import re
b=open("_js_blob.txt",encoding="utf-8").read()
def show(pat,n=5,w=200):
    print("="*18,pat,"hits",b.count(pat))
    for m in list(re.finditer(re.escape(pat),b))[:n]:
        seg=b[max(0,m.start()-w):m.start()+w].replace("\n"," ")
        print("   ...",seg[:2*w])
for p in ["1 \\u5143","\\u5143\\u8BD5\\u7528","\\u8BD5\\u75287\\u5929","7\\u5929","\\u9996\\u6708","\\u9650\\u65F6"]:
    show(p,3)