# -*- coding: utf-8 -*-
import re
b=open("_js_blob.txt",encoding="utf-8").read()
for pat in ["pc_new_user_campaign","pc_new_user_page","ug_free_subs","AGWJoinCampaign","incentive/campaign/join","campaign/join/"]:
    print("="*20,pat,"hits",b.count(pat))
    for m in list(re.finditer(re.escape(pat),b))[:4]:
        seg=b[max(0,m.start()-260):m.start()+300].replace("\n"," ")
        print("   ...",seg[:560])
        print()