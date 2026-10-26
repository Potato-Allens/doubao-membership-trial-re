# -*- coding: utf-8 -*-
import datetime
IDS={
 "eligibility":0000000000000003,
 "subscription":0000000000000007,
 "order":0000000000000004,
 "sub_disc38":0000000000000008,
 "order_disc38":0000000000000009,
}
# 已知: subscription/order 创建于 2026-10-26 14:33:49 (+08)
known=datetime.datetime(2026,10,26,14,33,49,tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
known_ms=int(known.timestamp()*1000)
print("known_ms",known_ms)
for sh in (12,16,18,20,22,24):
    v=IDS["subscription"]>>sh
    print("shift",sh,"sub>>sh",v, "as ms->",datetime.datetime.fromtimestamp(v/1000,datetime.timezone(datetime.timedelta(hours=8))) if v<4e12 else "n/a")
# calibrate offset with shift 22
sh=22
off=ID32=None
sub=IDS["subscription"]>>sh
print("sub>>22 - known_ms =", sub-known_ms)
for name,i in IDS.items():
    v=(i>>sh) - (sub-known_ms)
    try:
        dt=datetime.datetime.fromtimestamp(v/1000,datetime.timezone(datetime.timedelta(hours=8)))
        print("  %-14s -> %s"%(name,dt.strftime("%Y-%m-%d %H:%M:%S")))
    except Exception as e:
        print("  %-14s err"%name,e)