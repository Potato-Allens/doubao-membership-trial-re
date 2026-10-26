# -*- coding: utf-8 -*-
import re
b=open("_js_blob.txt",encoding="utf-8").read()
for pat in ["eligibility","selected_eligibility_id","eligibility_id","Eligibility"]:
    print("="*20,pat,"hits",b.count(pat))
for m in list(re.finditer("eligibility",b))[:20]:
    seg=b[max(0,m.start()-200):m.start()+240].replace("\n"," ")
    print("  ...",seg[:420])
    print()