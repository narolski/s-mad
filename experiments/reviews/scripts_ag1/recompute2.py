import sys, csv, json, pathlib, zlib, collections
sys.path.insert(0, "/home/narolski/smad-next/src/AG1")
import numpy as np
import ag1_read as A
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
DATA = pathlib.Path("/mnt/t7/smad_next/AG1/data")
rows = list(csv.DictReader(open(DATA / "manifests/ag1.csv")))
lg = {}
for f in pathlib.Path("/mnt/t7/smad_next/AG1/results").glob("AG1_*.log.csv"):
    if "smoke" in f.name: continue
    for r in csv.DictReader(open(f)): lg[r["stem"]] = r
for r in rows:
    if r["id"] in lg:
        for k in ("latdist", "loss", "cos_b", "w600k_cos_b_img"):
            if lg[r["id"]].get(k) not in (None, ""): r[k] = float(lg[r["id"]][k])
z = dict(np.load(DATA / "baselines.npz"))
BASE = {i: {k: z[k][j] for k in ("bytes", "lapvar", "hfband", "sym", "thumb")} for j, i in enumerate(z["id"].tolist())}
S = A.load_scores(rows, "/mnt/t7/smad_next/AG1/scoring/a41g_out/ag1", False)
# FRLL R0 vs R1 identity
sc = S["madation_vitb16"]
r0 = {r["photo_a"]: sc[r["id"]] for r in rows if r["rung"] == "R0" and r["db"] == "frll"}
r1 = {r["photo_a"]: sc[r["id"]] for r in rows if r["rung"] == "R1" and r["gen"] == "mip1"}
print("R0 vs R1 max |score diff|", max(abs(r0[k] - r1[k]) for k in r1), "bytes diff", max(abs(BASE["R0__"+k]["bytes"]-BASE[[r["id"] for r in rows if r["rung"]=="R1" and r["photo_a"]==k][0]]["bytes"]) for k in list(r1)[:20]) if ("R0__"+list(r1)[0]) in BASE else "id?")
pool = "primary"
sub = [r for r in rows if A.in_pool(r, pool) and r["gen"] in ("mip1", "camera")]
pers = sorted({r["pa"] for r in sub} | {r["pb"] for r in sub})
D = A.Draw(pers, 10000, A.SEED + zlib.crc32(pool.encode()) % 100000)
plat = {r["pa"]: r["platform"] for r in sub if r["rung"] in ("R2", "R3", "R4") and r["source"] == "ours"}
def G(hosts=None):
    g = collections.defaultdict(list)
    for r in sub:
        if hosts is None or r["pa"] in hosts: g[r["rung"]].append(r)
    return g
def allreps(pos, neg):
    wp = D.w([r["pa"] for r in pos], [r["pb"] for r in pos]); wn = D.w([r["pa"] for r in neg], [r["pb"] for r in neg])
    pt, reps = {}, {}
    for k in A.SCALAR_BASELINES:
        sp = np.array([BASE[r["id"]][k] for r in pos]); sn = np.array([BASE[r["id"]][k] for r in neg])
        a = A.auc(sp, sn); s = 1 if a >= .5 else -1
        pt[k] = max(a, 1 - a); reps[k] = A.wauc(s*sp, s*sn, wp, wn)
    X = np.stack([BASE[r["id"]]["thumb"] for r in pos + neg]); y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    g = np.array([r["pa"] for r in pos + neg]); oof = np.zeros(len(y))
    for tr, te in GroupKFold(n_splits=5).split(X, y, g):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=1.0)).fit(X[tr], y[tr]); oof[te] = m.decision_function(X[te])
    pt["thumb"] = A.auc(oof[:len(pos)], oof[len(pos):]); reps["thumb"] = A.wauc(oof[:len(pos)], oof[len(pos):], wp, wn)
    return pt, reps, wp, wn
def q(x): return [round(float(v), 3) for v in x]
for hname, hosts in (("all", None), ("athena", {h for h, p in plat.items() if p.startswith("athena")})):
    g = G(hosts)
    for a, b in (("R2", "R4"), ("R2s", "R4"), ("R3", "R4"), ("R0", "R2")):
        pos, neg = g[b], g[a]
        pt, reps, wp, wn = allreps(pos, neg)
        M = np.max(np.stack(list(reps.values())), 0)
        best = max(pt, key=pt.get)
        line = f"{hname} {a}>{b} floors " + " ".join(f"{k}={pt[k]:.3f}" for k in pt) + f" | max-per-draw floor mean {M.mean():.3f}"
        print(line)
        for rel in ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own", "selfmad_hrnet_w18__rel"):
            sc = S[rel]
            sp = np.array([sc[r["id"]] for r in pos]); sn = np.array([sc[r["id"]] for r in neg])
            rep = A.wauc(sp, sn, wp, wn); a0 = A.auc(sp, sn)
            print(f"   {rel:26s} auc {a0:.3f} ex_point {a0-pt[best]:+.3f} {q(A.ci(rep-reps[best]))}  ex_retake {a0-pt[best]:+.3f} {q(A.ci(rep-M))} p(ex<=0) {np.mean(rep-M<=0):.3f}")
# AG3 vs AG3T at matched alpha, same hosts
g = G()
hosts = sorted({r["pa"] for r in g["AG3"]})
print("AG3 hosts", len(hosts))
R2s1 = [r for r in g["R2"] if r["pa"] in hosts and r["photo_a"].endswith("__s1")]
for rel in ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own"):
    sc = S[rel]; C = A.contrast_fn(sc, D)
    out = []
    for al in (0.1, 0.2, 0.3, 0.4, 0.5):
        L3 = [r for r in g["AG3"] if abs(float(r["alpha"]) - al) < 1e-9] if al < .5 else [r for r in g["R4"] if r["pa"] in hosts]
        LT = [r for r in g["AG3T"] if abs(float(r["alpha"]) - al) < 1e-9] if al < .5 else [r for r in g["R3"] if r["pa"] in hosts]
        c3 = C(L3, R2s1); cT = C(LT, R2s1); d = C(L3, LT)
        diff = c3["rep"] - cT["rep"]
        out.append(f"a{al}: AG3 {c3['auc']:.3f} AG3T {cT['auc']:.3f} diff {c3['auc']-cT['auc']:+.3f} {q(A.ci(diff))} direct AG3vsAG3T {d['auc']:.3f} {q(d['ci'])}")
    print(rel); [print("   ", o) for o in out]
# achieved dose glint
zE = np.load(DATA / "oracle_glint.npz"); E = dict(zip(zE["id"].tolist(), zE["emb"]))
cam = {r["photo_a"]: r["id"] for r in g["R0"]}
for arm in ("AG3", "AG3T"):
    for al in (0.0, 0.1, 0.2, 0.3, 0.4):
        L = [r for r in g[arm] if abs(float(r["alpha"]) - al) < 1e-9]
        if not L: continue
        cb = np.mean([E[r["id"]] @ E[cam[r["photo_b"]]] for r in L if r["id"] in E and r["photo_b"] in cam])
        ca = np.mean([E[r["id"]] @ E[cam[r["photo_a"]]] for r in L if r["id"] in E])
        print(arm, al, "cosA %.3f cosB %.3f" % (ca, cb), "n", len(L))
for rung in ("R3", "R4"):
    L = [r for r in g[rung] if r["pa"] in hosts]
    print(rung, "cosA %.3f cosB %.3f" % (np.mean([E[r["id"]] @ E[cam[r["photo_a"]]] for r in L]), np.mean([E[r["id"]] @ E[cam[r["photo_b"]]] for r in L])))
# latent distance: R2s vs R4 restricted overlap; score vs latdist correlation
from scipy.stats import spearmanr
for rel in ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own"):
    sc = S[rel]
    for rung in ("R2", "R2s", "R3", "R4"):
        L = [r for r in g[rung] if "latdist" in r]
        print(rel, rung, "median lat %.2f" % np.median([r["latdist"] for r in L]), "spearman(score, latdist) %.3f" % spearmanr([sc[r["id"]] for r in L], [r["latdist"] for r in L])[0], "n", len(L))
    # R2s vs R4 among R4 with latdist <= median R2s ... matched: pair R2s and R4 with latdist within band
    R2s = [r for r in g["R2s"] if "latdist" in r]; R4 = [r for r in g["R4"] if "latdist" in r]
    lo, hi = 5.9, 6.3
    a = [r for r in R2s if lo <= r["latdist"] <= hi]; b = [r for r in R4 if lo <= r["latdist"] <= hi]
    print("   band", lo, hi, "n", len(a), len(b), "AUC R2s>R4 %.3f" % A.auc([sc[r["id"]] for r in b], [sc[r["id"]] for r in a]))
