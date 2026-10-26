import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
s=open('_js_blob.txt',encoding='utf-8',errors='ignore').read()
pat=re.compile(r'([A-Za-z0-9_\.\-]{3,70})\s*:\s*"((?:[^"\\]|\\.){0,200})"')
hits=[]
for m in pat.finditer(s):
    v=m.group(2)
    if ('\\u8BD5\\u7528' in v) or ('试用' in v) or ('\\u5143' in v and '\\u8BD5' in v):
        hits.append((m.group(1),v))
seen=set(); n=0
for k,v in hits:
    if k in seen: continue
    seen.add(k); n+=1
    try: dv=v.encode().decode('unicode_escape')
    except Exception: dv=v
    print('%-52s %s'%(k,dv[:110]))
    if n>=120: break
print('total unique',len(seen))