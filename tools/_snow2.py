import datetime, sys, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
TZ=datetime.timezone(datetime.timedelta(hours=8))
def ts(ms): return datetime.datetime.fromtimestamp(ms/1000,TZ).strftime('%Y-%m-%d %H:%M:%S')
ids={
 'sub_1yuan':0000000000000007,
 'order_1yuan':0000000000000004,
 'sub_38':0000000000000008,
 'order_38':0000000000000009,
 'elig':0000000000000003,
 'order_old':0000000000000011,
 'sub_old':0000000000000012,
}
known={'sub_1yuan':1792996429079,'order_1yuan':1792996503000,'sub_38':1793003819000,'order_38':1793003819000,'order_old':1792994417000,'sub_old':1792994417000}
# offset from sub_1yuan
base=ids['sub_1yuan']>>22
off=known['sub_1yuan']-base
print('offset',off)
for k,v in ids.items():
    est=(v>>22)+off
    print('%-12s %-20d -> %s %s'%(k,v,ts(est),'(known %s)'%ts(known[k]) if k in known else ''))