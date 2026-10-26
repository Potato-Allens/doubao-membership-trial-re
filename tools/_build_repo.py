import os,json,shutil,io,sys,collections,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding="utf-8",errors="replace")
SRC=os.environ["CODEX_HOME"]+r"\work\doubao_yuan"
DST=r"C:\Users\Administrator\Documents\Codex\2026-10-24\qui\outputs\doubao-membership-trial-re"
for d in ("tools","docs","docs/evidence","data"):
    os.makedirs(os.path.join(DST,d),exist_ok=True)

# 1) copy python scripts
n=0
for p in glob.glob(os.path.join(SRC,"*.py")):
    shutil.copy2(p,os.path.join(DST,"tools",os.path.basename(p)))
    n+=1
print("copied py:",n)

def mask_u(uid):
    u=str(uid or "")
    if len(u)<5: return "***"
    return u[:3]+"*"*(len(u)-5)+u[-2:]

# 2) scan_212 summary
rows=json.load(open(os.path.join(SRC,"scan_212.json"),encoding="utf-8"))
buckets=collections.Counter(); hits=[]
for r in rows:
    d=r.get("disc") or 0
    if r.get("code")==710012001: buckets["login_invalid"]+=1; continue
    buckets["disc_%d"%d]+=1
    if d>0:
        hits.append({"uid":mask_u(r.get("uid")),"discount_amount":d,
                     "card":r.get("card"),"button":r.get("btn"),
                     "trial":r.get("trial"),"has_history_paid":r.get("hist")})
out={"source":"scan_212.json","generated":"2026-10-26","accounts":len(rows),
     "buckets":dict(sorted(buckets.items())),
     "discount_hits":hits,
     "note":"uid masked; no cookies included"}
json.dump(out,open(os.path.join(DST,"docs","evidence","scan_212_summary.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("scan_212 hits:",len(hits),dict(buckets))

# 3) sweep_elig_434 summary
rows2=json.load(open(os.path.join(SRC,"sweep_elig_434.json"),encoding="utf-8"))
c2=collections.Counter(); hits2=[]
for r in rows2:
    c2["disc_%d"%(r.get("disc") or 0)]+=1
    c2["page_%s"%r.get("page")]+=1
    c2["beta_%s"%r.get("beta")]+=1
    if (r.get("disc") or 0)>0 or r.get("trial"):
        hits2.append({"uid":mask_u(r.get("uid")),"discount_amount":r.get("disc"),
                      "trial":r.get("trial"),"button":r.get("btn"),"scene":r.get("extra")})
out2={"source":"sweep_elig_434.json","generated":"2026-10-26","accounts":len(rows2),
      "buckets":dict(sorted(c2.items())),"nonzero":hits2,"note":"uid masked"}
json.dump(out2,open(os.path.join(DST,"docs","evidence","sweep_elig_434_summary.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("sweep nonzero:",len(hits2))

# 4) endpoint catalog
eps=json.load(open(os.path.join(SRC,"_eps_all.json"),encoding="utf-8"))
json.dump({"endpoints":sorted(eps),"count":len(eps)},
          open(os.path.join(DST,"docs","evidence","endpoint_catalog.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("endpoints:",len(eps))

# 5) requirements
open(os.path.join(DST,"requirements.txt"),"w",encoding="utf-8").write(
"requests>=2.31\nplaywright>=1.44\nqrcode>=7.4\nPillow>=10.0\n")
print("requirements written")