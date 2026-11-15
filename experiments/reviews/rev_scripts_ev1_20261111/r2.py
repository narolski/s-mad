import sys, csv, numpy as np, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
R = rows_eval(); ids = [r["id"] for r in R]
dev = sel(R, "devbona","devbona","orig","0")
P = {v: sel(R,"frllm","frll_bona",v,"0") for v in ("orig","jpeg50","resample50")}
for f in FAMS: P["E7 "+f] = sel(R, SETOF[f], f, "resmatch", "0")
M = {f: sel(R, SETOF[f], f, "orig", "1") for f in FAMS}
q = [1, 5, 25, 50, 75, 95, 99]
# devbona source split
src = np.array(["FRGC" if ("nd1" in R[i]["name"] or "d" in R[i]["name"].split("_")[0]) else "FERET" for i in dev])
print("devbona sources", collections.Counter(src), [R[i]["name"] for i in dev[:3]], [R[i]["name"] for i in dev[-3:]])
names = [R[i]["name"] for i in dev]
pref = collections.Counter(n.split("_")[0][:3] if not n[0].isdigit() else "digits" for n in names); print(pref)
print("manifest native ied/w by pool:")
for k in ["orig","resample50"]+["E7 "+f for f in FAMS]:
    v = P[k]; print(f"  {k:16s} native_w med {np.median([float(R[i]['native_w']) for i in v]):6.0f} h {np.median([float(R[i]['native_h']) for i in v]):6.0f} ied med {np.median([float(R[i]['ied']) for i in v]):6.1f} bytes med {np.median([float(R[i]['file_bytes']) for i in v]):9.0f}")
for f in FAMS:
    v = M[f]; print(f"  morph {f:13s} native_w med {np.median([float(R[i]['native_w']) for i in v]):6.0f} h {np.median([float(R[i]['native_h']) for i in v]):6.0f} ied med {np.median([float(R[i]['ied']) for i in v]):6.1f} bytes med {np.median([float(R[i]['file_bytes']) for i in v]):9.0f}")
for nm, d in (("ViT-L/14","madation_vitl14"),("ViT-B/16","madation_vitb16"),("SelfMAD ours","selfmad_hrnet_w18")):
    s = rel(d, ids); pr = rel(d, ids, key="score_noTTA")
    print(f"\n== {nm} logit quantiles {q}")
    print("  devbona      ", np.round(np.percentile(s[dev], q), 3), " prob median %.2e" % np.median(pr[dev]))
    for sname in ("FERET","FRGC"):
        x = s[dev][src==sname]; t = thr(s[dev], .05)
        print(f"  devbona {sname:5s} n={len(x)}", np.round(np.percentile(x, q), 3), f" FA at dev thr {100*(x>t).mean():.1f}%")
    for k in ("orig","jpeg50","resample50","E7 mordiff","E7 dim_a","E7 amsl"):
        print(f"  {k:13s}", np.round(np.percentile(s[P[k]], q), 3))
    for f in FAMS:
        print(f"  m {f:11s}", np.round(np.percentile(s[M[f]], q), 3), " prob median %.2e" % np.median(pr[M[f]]), f"share prob>0.5: {100*(pr[M[f]]>0.5).mean():.1f}%")
    print(f"  genuine FRLL orig share prob>0.5: {100*(pr[P['orig']]>0.5).mean():.1f}%; devbona {100*(pr[dev]>0.5).mean():.1f}%")
    # shift relative to the morph-genuine median gap
    o = np.median(s[P["orig"]])
    for k in ("jpeg50","resample50","E7 mordiff","E7 dim_a"):
        sh = np.median(s[P[k]] - s[P["orig"]]) if k != "E7 mordiff" or True else 0
        print(f"   shift {k:12s} {sh:+.3f}; as share of morph-genuine median gap:", " ".join(f"{f[:6]}:{sh/(np.median(s[M[f]])-o):+.2f}" for f in FAMS))
z = np.load(OWN, allow_pickle=False); own = load(OWN, ids, "score")
print("\n== SelfMAD own score quantiles", q)
for k in ("orig","jpeg50","resample50","E7 mordiff","E7 dim_a","E7 amsl","E7 facemorpher","E7 stylegan"):
    print(f"  {k:13s}", np.round(np.percentile(own[P[k]], q), 4))
for f in FAMS: print(f"  m {f:11s}", np.round(np.percentile(own[M[f]], q), 4), f"share>0.5: {100*(own[M[f]]>0.5).mean():.1f}")
for k in ("orig","resample50","E7 amsl","E7 facemorpher","E7 opencv","E7 webmorph","E7 mordiff","E7 dim_a"):
    print(f"  genuine {k:14s} share score>0.5: {100*(own[P[k]]>0.5).mean():.1f}%  >0.9: {100*(own[P[k]]>0.9).mean():.1f}%")
