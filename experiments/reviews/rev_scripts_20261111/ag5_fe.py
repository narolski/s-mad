import csv, pathlib, numpy as np
MC = pathlib.Path("/home/narolski/mambamorph-code"); S = MC/"smadcvpr_runs/A12_scored/A12REL"
hr = list(csv.DictReader(open("/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv")))
sr = list(csv.DictReader(open("/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/a37spread.csv")))
ev = [r for r in csv.DictReader(open(MC/"smadcvpr_data/manifests/eval.csv")) if r["family"]=="frll_bona" and r["variant"]=="orig"]
R4 = [r for r in hr if r["family"]=="h3_sg3" and r["variant"]=="orig"]; R2 = [r for r in hr if r["family"]=="h3_bona" and r["variant"]=="orig"]; RX = [r for r in sr if r["variant"]=="orig"]
pairs = sorted({int(r["pair"]) for r in hr}); ppos = {p:i for i,p in enumerate(pairs)}
rng = np.random.default_rng(99); NB = 4000
Wp = rng.multinomial(len(pairs), np.full(len(pairs),1/len(pairs)), size=NB).astype(float)
def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable"); ns = neg[ob]; lo, hi = np.searchsorted(ns,pos,"left"), np.searchsorted(ns,pos,"right")
    C = np.concatenate([np.zeros((wn.shape[0],1)), np.cumsum(wn[:,ob],1)],1)
    return (wp*(C[:,lo]+0.5*(C[:,hi]-C[:,lo]))).sum(1)/np.maximum(wp.sum(1)*C[:,-1],1e-12)
def one(a,b): return float(wauc(a,b,np.ones((1,len(a))),np.ones((1,len(b))))[0])
w4 = Wp[:,[ppos[int(r["pair"])] for r in R4]]; w2 = Wp[:,[ppos[int(r["pair"])] for r in R2]]; wx = Wp[:,[ppos[int(r["pair"])] for r in RX]]
for net in ("madation_fe_vitl14","madation_fe_vitb16","madation_fs_vitl14","madation_fs_vitb16","madation_vitl14","madation_vitb16"):
    z = np.load(S/net/"scores_h3sg3.npz", allow_pickle=False); m = dict(zip(z["id"].tolist(), z["score_noTTA"].astype(float)))
    ze = np.load(S/net/"scores_eval.npz", allow_pickle=False); me = dict(zip(ze["id"].tolist(), ze["score_noTTA"].astype(float)))
    s4 = np.array([m[r["id"]] for r in R4]); s2 = np.array([m[r["id"]] for r in R2]); s0 = np.array([me[r["id"]] for r in ev])
    rep = wauc(s4, s2, w4, w2)
    line = f"{net:20s} R0vsR4 {one(s4,s0):.3f}  R0vsR2 {one(s2,s0):.3f}  R2vsR4 {one(s4,s2):.3f} [{np.percentile(rep,2.5):.3f}, {np.percentile(rep,97.5):.3f}]"
    fx = pathlib.Path(f"/mnt/t7/smad_heldout/a41g/a41g_out/x4/{net}/rel/scores_a37spread.npz")
    if fx.exists():
        zx = np.load(fx, allow_pickle=False); mx = dict(zip(zx["id"].tolist(), zx["score_noTTA"].astype(float))); sx = np.array([mx[r["id"]] for r in RX]); repx = wauc(s4, sx, w4, wx)
        line += f"  X4: R2x4vsR4 {one(s4,sx):.3f} [{np.percentile(repx,2.5):.3f}, {np.percentile(repx,97.5):.3f}]"
    else: line += "  X4: no scores"
    print(line)
