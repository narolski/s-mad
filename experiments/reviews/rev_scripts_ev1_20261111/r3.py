import sys, csv, numpy as np, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
from scipy.stats import binomtest
R = rows_eval(); ids = [r["id"] for r in R]
z = np.load("/mnt/t7/smad_next/EV1/feat.npz", allow_pickle=False)
alp = z["al_path"]; print(alp[0], alp[-1], z["cells"])
zero = {}
for p, v in zip(alp, z["al_zero"]):
    zero[str(p)] = float(v)
# match by path suffix
key = lambda r: r["path"]
ex = next(iter(zero)); print("example key", ex)
def zf(ix):
    out = []
    for i in ix:
        p = R[i]["path"]
        c = [k for k in (p, "/home/narolski/mambamorph-code/smadcvpr_data/"+p) if k in zero]
        if c: out.append(zero[c[0]])
    return np.array(out)
# build suffix map
suf = {}
for k, v in zero.items():
    j = k.find("eval/")
    if j >= 0: suf[k[j:]] = v
def zf(ix): return np.array([suf[R[i]["path"]] for i in ix if R[i]["path"] in suf])
pools = {"FRLL orig": sel(R,"frllm","frll_bona","orig","0"), "MorDIFF alignment": sel(R,"mordiff","mordiff_bona","orig","0"), "DiM copy": sel(R,"dim","dim_bona","orig","0")}
for v in ("jpeg50","resample50"): pools["FRLL "+v] = sel(R,"frllm","frll_bona",v,"0")
for f in FAMS: pools["E7 "+f] = sel(R, SETOF[f], f, "resmatch", "0")
for f in FAMS: pools["morph "+f] = sel(R, SETOF[f], f, "orig", "1")
for k, ix in pools.items():
    x = zf(ix)
    if len(x): print(f"{k:22s} n={len(x):5d} zero-border fraction: min {x.min():.3f} med {np.median(x):.3f} max {x.max():.3f}")
    else: print(f"{k:22s} not in feature file")
a43 = list(csv.DictReader(open(A43/"data/manifests/a43.csv")))
for arm in ("E","D","D20","A","B"):
    x = np.array([float(r["border_frac"]) for r in a43 if r["source"]=="a43" and r["arm"]==arm and r["border_frac"]])
    print("A43 arm", arm, "border_frac med", np.median(x), "ied", np.median([float(r["ied"]) for r in a43 if r["source"]=="a43" and r["arm"]==arm]))
# paired: E7 MorDIFF and stored-small vs MorDIFF alignment (same frame crop), at dev thr
dev = sel(R, "devbona","devbona","orig","0")
a43ids = [r["id"] for r in a43]; Eix = [i for i, r in enumerate(a43) if r["source"]=="a43" and r["arm"]=="E"]; Est = [a43[i]["src_a"] for i in Eix]
st = lambda ix: [R[i]["name"][:6] for i in ix]
for nm, d in (("ViT-L/14","madation_vitl14"),("ViT-B/16","madation_vitb16"),("FE ViT-L/14","madation_fe_vitl14"),("FE ViT-B/16","madation_fe_vitb16"),("SelfMAD own",None)):
    if d:
        s = rel(d, ids); t = thr(s[dev], .05); sE = load(A43/f"a43_out/a43/{d}/rel/scores_a43.npz", a43ids, "logit_noTTA")[Eix]
    else:
        s = load(OWN, ids, "score"); t = thr(s[pools["FRLL orig"]], .05); sE = load(A43/"a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz", a43ids, "score")[Eix]
    ref = dict(zip(st(pools["MorDIFF alignment"]), s[pools["MorDIFF alignment"]]))
    refo = dict(zip(st(pools["FRLL orig"]), s[pools["FRLL orig"]]))
    for lab, x, sx in (("E7 MorDIFF", s[pools["E7 mordiff"]], st(pools["E7 mordiff"])), ("stored-small", sE, Est), ("E7 DiM-A", s[pools["E7 dim_a"]], st(pools["E7 dim_a"]))):
        for rn, rf in (("MorDIFF alignment", ref), ("FRLL orig", refo)):
            r_ = np.array([rf[q] for q in sx]); up = int(((x>t)&~(r_>t)).sum()); dn = int((~(x>t)&(r_>t)).sum())
            print(f"{nm:12s} {lab:13s} vs {rn:18s}: FA {100*(x>t).mean():5.1f} ref {100*(r_>t).mean():5.1f}  +{up}/-{dn} p={binomtest(min(up,dn),up+dn,.5).pvalue if up+dn else 1:.1e}; share of photos up {100*(x>r_).mean():.0f}%")
