# -*- coding: utf-8 -*-
import re
b=open("_js_blob.txt",encoding="utf-8").read()
def show(pat,n=4,w=230):
    print("="*18,pat,"hits",b.count(pat))
    for m in list(re.finditer(re.escape(pat),b))[:n]:
        print("   ...",b[max(0,m.start()-w):m.start()+w].replace("\n"," ")[:2*w])
for p in ["crowd","abtest","ab_test","x-tt-ab","ab_sdk","vip_ab","experiment","bucket"]:
    show(p,3)