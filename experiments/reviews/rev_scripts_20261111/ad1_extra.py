"""Reviewer extras for AD1: paired R0->R1 flag change (same 204 photos), 100-step replication of the main contrast, R0-anchored ladder."""
import csv, re, pathlib, numpy as np
from scipy.stats import binomtest
MC = pathlib.Path("/home/narolski/mambamorph-code"); A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
rows = list(csv.DictReader(open(A43/"data/manifests/a43.csv")))
ev = [r for r in csv.DictReader(open(MC/"smadcvpr_data/manifests/eval.csv")) if r["set"]=="mordiff"]
e7 = [r for r in ev if r["family"]=="mordiff" and r["variant"]=="resmatch"]
def pers(r):
    if r.get("source","eval")=="a43": return (r["src_a"][:3], r["src_b"][:3]) if r["src_b"] else (r["src_a"][:3],)
    n = pathlib.PurePath(r["path"]).name; m = re.match(r"^morph_(\d{3})_\d{2}_and_(\d{3})_\d{2}", n)
    return (m.group(1), m.group(2)) if m else (n[:3],)
allp = sorted({p for r in rows for p in pers(r)}); pidx = {p:i for i,p in enumerate(allp)}
rng = np.random.default_rng(555); NB = 4000
CNT = rng.multinomial(len(allp), np.full(len(allp),1/len(allp)), size=NB).astype(float)
def W(pp):
    a = np.array([pidx[p[0]] for p in pp]); b = np.array([pidx[p[-1]] for p in pp]); w = CNT[:,a]*CNT[:,b]; s = a==b; w[:,s] = CNT[:,a[s]]; return w
def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable"); ns = neg[ob]; lo, hi = np.searchsorted(ns,pos,"left"), np.searchsorted(ns,pos,"right")
    C = np.concatenate([np.zeros((wn.shape[0],1)), np.cumsum(wn[:,ob],1)],1)
    return (wp*(C[:,lo]+0.5*(C[:,hi]-C[:,lo]))).sum(1)/np.maximum(wp.sum(1)*C[:,-1],1e-12)
G = {}
for i,r in enumerate(rows):
    k = r["arm"] if r["source"]=="a43" else {"mordiff_bona":"R0","mordiff":"A_reg"}.get(r["family"],"frll_bona"); G.setdefault(k,[]).append(i)
def eer_thr(b, m):
    t = np.unique(np.r_[b,m]); fpr = np.array([(b>=x).mean() for x in t]); fnr = np.array([(m<x).mean() for x in t]); i = int(np.argmin(np.abs(fpr-fnr))); return float(t[i])
for lab,f43,k43,fev,kev in [("ViT-B/16 rel","madation_vitb16/rel","score_noTTA","smadcvpr_runs/A12_scored/A12REL/madation_vitb16/scores_eval.npz","score_noTTA"),
        ("ViT-L/14 rel","madation_vitl14/rel","score_noTTA","smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz","score_noTTA"),
        ("SelfMAD own","selfmad_hrnet_w18/own","score","experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz","score")]:
    s = np.load(A43/"a43_out/a43"/f43/"scores_a43.npz")[k43].astype(float)
    ze = np.load(MC/fev); em = dict(zip(ze["id"].tolist(), ze[kev].astype(float)))
    S = {k: s[np.array(v)] for k,v in G.items()}; P = {k:[pers(rows[i]) for i in v] for k,v in G.items()}
    t = eer_thr(S["R0"], S["A_reg"])
    key0 = {pathlib.PurePath(rows[i]["path"]).name[:6]: s[i] for i in G["R0"]}
    key1 = {pathlib.PurePath(r["path"]).name[:6]: em[r["id"]] for r in e7}
    keyE = {rows[i]["src_a"][:6]: s[i] for i in G["E"]}
    common = sorted(set(key0)&set(key1))
    f0 = np.array([key0[c]>=t for c in common]); f1 = np.array([key1[c]>=t for c in common])
    b01 = int((~f0 & f1).sum()); b10 = int((f0 & ~f1).sum())
    # person bootstrap of the paired difference in flag rate
    pc = np.array([pidx[c[:3]] for c in common]); d = f1.astype(float)-f0.astype(float)
    reps = (CNT[:,pc]*d).sum(1)/CNT[:,pc].sum(1)
    up = np.array([key1[c]>key0[c] for c in common]).mean()
    line = f"{lab:13s} paired on {len(common)} photos: flagged R0 {f0.sum()} -> R1 {f1.sum()}; newly flagged {b01}, un-flagged {b10}; rise {100*d.mean():+.1f} pts [{100*np.percentile(reps,2.5):+.1f}, {100*np.percentile(reps,97.5):+.1f}]; McNemar p={binomtest(b01,b01+b10,0.5).pvalue:.1e}; score rises for {100*up:.1f}% of photos"
    cE = sorted(set(key0)&set(keyE))
    if cE:
        fE = np.array([keyE[c]>=t for c in cE]); f0e = np.array([key0[c]>=t for c in cE]); line += f" | E (stored small): {fE.sum()}/{len(cE)} flagged, score rises for {100*np.mean([keyE[c]>key0[c] for c in cE]):.1f}%"
    print(line)
    for nm,a,b in (("B vs D (100 steps, main contrast)","B","D"),("B20 vs D20 (20 steps)","B20","D20"),("B20 vs E","B20","E"),("A vs E","A","E")):
        pt = float(wauc(S[a],S[b],np.ones((1,len(S[a]))),np.ones((1,len(S[b]))))[0]); rep = wauc(S[a],S[b],W(P[a]),W(P[b]))
        print(f"      {nm:36s} {pt:.3f} [{np.percentile(rep,2.5):.3f}, {np.percentile(rep,97.5):.3f}]")
    anch = {k: float(wauc(S[k],S["R0"],np.ones((1,len(S[k]))),np.ones((1,len(S["R0"]))))[0]) for k in ("E","D20","C20","B20","A")}
    r1 = np.array([em[r["id"]] for r in e7]); anch["R1(E7)"] = float(wauc(r1,S["R0"],np.ones((1,len(r1))),np.ones((1,len(S["R0"]))))[0])
    print("      R0-anchored AUCs:", {k: round(v,3) for k,v in anch.items()})
