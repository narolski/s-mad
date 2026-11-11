"""Independent re-check of AD1 (reviewer). Own AUC (scipy mannwhitneyu), own person bootstrap (explicit resampling, different seed)."""
import csv, re, pathlib, hashlib, numpy as np
from scipy.stats import mannwhitneyu, rankdata, beta
MC = pathlib.Path("/home/narolski/mambamorph-code")
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
MAN = A43/"data/manifests/a43.csv"; EVAL = MC/"smadcvpr_data/manifests/eval.csv"
print("a43.csv sha", hashlib.sha256(open(MAN,"rb").read()).hexdigest()[:16], "eval.csv sha", hashlib.sha256(open(EVAL,"rb").read()).hexdigest()[:16])
rows = list(csv.DictReader(open(MAN)))
ev = [r for r in csv.DictReader(open(EVAL)) if r["set"]=="mordiff"]
RXB = re.compile(r"^(\d{3})_(\d{2})"); RXM = re.compile(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})")
def pers(r):
    n = pathlib.PurePath(r["path"]).name
    if r.get("source","eval")=="a43":
        return (r["src_a"][:3], r["src_b"][:3]) if r["src_b"] else (r["src_a"][:3],)
    m = RXM.match(n)
    if m: return (m.group(1), m.group(3))
    return (RXB.match(n).group(1),)
def auc(pos, neg):
    return mannwhitneyu(pos, neg, alternative="two-sided").statistic/(len(pos)*len(neg))
def wauc(pos, neg, wp, wn):
    # weighted AUC, explicit
    allv = np.r_[pos, neg]; 
    order = np.argsort(neg, kind="stable"); ns = neg[order]; cw = np.r_[0, np.cumsum(wn[order])]
    lo = np.searchsorted(ns, pos, "left"); hi = np.searchsorted(ns, pos, "right")
    return float((wp*(cw[lo] + 0.5*(cw[hi]-cw[lo]))).sum()/(wp.sum()*cw[-1]))
allp = sorted({p for r in rows for p in pers(r)})
pidx = {p:i for i,p in enumerate(allp)}
print("persons", len(allp))
def idxs(pp):
    a = np.array([pidx[p[0]] for p in pp]); b = np.array([pidx[p[-1]] for p in pp]); return a,b
rng = np.random.default_rng(987654321)
NB = 4000
CNT = np.stack([np.bincount(rng.integers(0,len(allp),len(allp)), minlength=len(allp)) for _ in range(NB)]).astype(float)
def weights(pp):
    a,b = idxs(pp); w = CNT[:,a]*CNT[:,b]; same = a==b; w[:,same] = CNT[:,a[same]]; return w
def boot(sa, pa, sb, pb):
    wa, wb = weights(pa), weights(pb)
    reps = np.array([wauc(sa, sb, wa[i], wb[i]) for i in range(NB)])
    return np.percentile(reps,[2.5,97.5]), reps
def eer_thr(b, m):
    t = np.unique(np.r_[b,m]); fpr = np.array([(b>=x).mean() for x in t]); fnr = np.array([(m<x).mean() for x in t])
    i = int(np.argmin(np.abs(fpr-fnr))); return 100*(fpr[i]+fnr[i])/2, float(t[i])
def cp(k,n):
    lo = 0.0 if k==0 else beta.ppf(0.025,k,n-k+1); hi = 1.0 if k==n else beta.ppf(0.975,k+1,n-k); return lo,hi
G = {}
for i,r in enumerate(rows):
    k = r["arm"] if r["source"]=="a43" else {"mordiff_bona":"R0","mordiff":"A_reg"}.get(r["family"],"frll_bona")
    G.setdefault(k,[]).append(i)
e7 = [r for r in ev if r["family"]=="mordiff" and r["variant"]=="resmatch"]
allm = [r for r in ev if r["family"]=="mordiff" and r["label"]=="1"]
bona_ev = [r for r in ev if r["family"]=="mordiff_bona"]
print({k:len(v) for k,v in G.items()}, "E7", len(e7), "all pub morphs", len(allm))
# are the A_reg rows the same ids as arm A? compare pub_eval_id
DETS = [("ViT-B/16 rel","madation_vitb16/rel","score_noTTA","smadcvpr_runs/A12_scored/A12REL/madation_vitb16/scores_eval.npz","score_noTTA"),
        ("ViT-L/14 rel","madation_vitl14/rel","score_noTTA","smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz","score_noTTA"),
        ("SelfMAD own","selfmad_hrnet_w18/own","score","experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz","score"),
        ("SelfMAD pipe","selfmad_hrnet_w18/rel","score_noTTA","smadcvpr_runs/A12_scored/A12REL/selfmad_hrnet_w18/scores_eval.npz","score_noTTA")]
for lab,f43,k43,fev,kev in DETS:
    z = np.load(A43/"a43_out/a43"/f43/"scores_a43.npz", allow_pickle=False); s = z[k43].astype(float)
    assert list(z["id"])==[r["id"] for r in rows]
    ze = np.load(MC/fev, allow_pickle=False); em = dict(zip(ze["id"].tolist(), ze[kev].astype(float)))
    S = {k: s[np.array(v)] for k,v in G.items()}; P = {k:[pers(rows[i]) for i in v] for k,v in G.items()}
    S["R1"] = np.array([em[r["id"]] for r in e7]); P["R1"] = [pers(r) for r in e7]
    S["PUB1000"] = np.array([em[r["id"]] for r in allm if r["id"] in em]); P["PUB1000"] = [pers(r) for r in allm if r["id"] in em]
    S["R0ev"] = np.array([em[r["id"]] for r in bona_ev])
    print("\n=====", lab, "| n PUB1000 scored:", len(S["PUB1000"]), "| frac unique scores R0:", len(np.unique(S["R0"]))/len(S["R0"]))
    con = [("bench A_reg vs R0","A_reg","R0"),("bench PUB1000 vs R0","PUB1000","R0"),("bridge A vs B20","A","B20"),("R1 vs R0","R1","R0"),("D20 vs R1","D20","R1"),("D20 vs R0","D20","R0"),
           ("C20 vs D20","C20","D20"),("B20 vs C20","B20","C20"),("MAIN B20 vs D20","B20","D20"),("A vs D20","A","D20"),
           ("E vs R0 (storage only)","E","R0"),("E vs R1","E","R1"),("D20 vs E (render only, same storage)","D20","E"),("B20 vs E","B20","E"),("B20 vs R1","B20","R1"),("A_reg vs R1","A_reg","R1"),("D100 vs D20","D","D20"),("B100 vs B20","B","B20")]
    for nm,a,b in con:
        pt = auc(S[a],S[b]); ci,_ = boot(S[a],P[a],S[b],P[b])
        print(f"  {nm:40s} AUC {pt:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]  n={len(S[a])}/{len(S[b])}")
    for nm, mset in (("200-sample","A_reg"),("all 1000","PUB1000")):
        eer,t = eer_thr(S["R0"], S[mset])
        print(f"  EER R0 vs published ({nm}) = {eer:.2f}%  thr={t:.5g}")
        for k in ("R0","R1","E","D20","D","C20","B20","A"):
            kk = int((S[k]>=t).sum()); n=len(S[k]); lo,hi = cp(kk,n)
            print(f"     flagged at thr: {k:4s} {kk}/{n} = {kk/n:.3f} [{lo:.3f},{hi:.3f}]")
    # fixed-BPCER thresholds on R0
    for bp in (0.01,0.05,0.10):
        t = np.quantile(S["R0"], 1-bp, method="higher")
        # flag = score > t so that R0 flagged <= bp
        fr = {k: float((S[k]>t).mean()) for k in ("R0","R1","E","D20","C20","B20","A_reg","PUB1000")}
        print(f"  thr at BPCER<={bp:.2f} on R0 (t={t:.4g}): " + ", ".join(f"{k} {v:.3f}" for k,v in fr.items()))
    # paired R0 -> R1 (same photos?) by file name
    n0 = {pathlib.PurePath(rows[i]["path"]).name.split(".")[0]: s[i] for i in G["R0"]}
    n1 = {pathlib.PurePath(r["path"]).name.split(".")[0]: em[r["id"]] for r in e7}
    common = sorted(set(n0)&set(n1))
    if common:
        d = np.array([n1[c]-n0[c] for c in common]); print(f"  paired R1-R0 on {len(common)} photos: frac R1>R0 = {(d>0).mean():.3f}, ties {(d==0).mean():.3f}")
    else:
        print("  R1/R0 names not matched directly; sample:", list(n0)[:2], list(n1)[:2])
