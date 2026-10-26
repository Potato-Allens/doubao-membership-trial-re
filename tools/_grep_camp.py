# -*- coding: utf-8 -*-
import re
b=open("_js_blob.txt",encoding="utf-8").read()
def show(pat,n=6,w=260):
    print("="*20,pat,b.count(pat))
    for m in list(re.finditer(re.escape(pat),b))[:n]:
        print("   ...",b[max(0,m.start()-w):m.start()+w].replace("\n"," ")[:2*w])
show("InitCampaignTrial",8)
show("campaign/page/query",4)
show("page_status",4)
show("feature_key=",4)
show("activity_id=",6)