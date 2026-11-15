"""Reviewer: is the expression cue USED?  Existing registered eval scores only (releases). Genuine neutral (03) vs smiling (08) scored separately."""
import csv, re, pathlib, sys, json, numpy as np
from scipy.stats import binomtest
MC = pathlib.Path("/home/narolski/mambamorph-code")
EV = MC/"smadcvpr_data/manifests/eval.csv"
rows = [r for r in csv.DictReader(open(EV)) if r["set"] in ("frllm","dim","mordiff") and r["variant"]=="orig"]
def pers(name):
    m = re.match(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})", name)
    if m: return (m.group(1), m.group(3)), (m.group(2), m.group(4))
    m = re.match(r"^(\d{3})_(\d{3})_", name)
    if m: return (m.group(1), m.group(2)), (None, None)
    m = re.match(r"^(\d{3})_(\d{2})_", name)
    return (m.group(1),), (m.group(2),)
CELLS = {}
for st, fams, bfam in (("frllm", ("amsl","facemorpher","opencv","stylegan","webmorph"), "frll_bona"),
                       ("dim", ("dim_a","dim_c","fast_dim","fast_dim_ode","greedy_dim","greedy_dim_s"), "dim_bona"),
                       ("mordiff", ("mordiff",), "mordiff_bona")):
    b = [r for r in rows if r["set"]==st and r["family"]==bfam and r["label"]=="0"]
    for f in fams:
        CELLS[f"{st}/{f}"] = ([r for r in rows if r["set"]==st and r["family"]==f and r["label"]=="1"], b)
allp = sorted({p for m,b in CELLS.values() for r in m+b for p in pers(pathlib.PurePath(r["path"]).name)[0]})
pidx = {p:i for i,p in enumerate(allp)}
NB = 600
rng = np.random.default_rng(424242)
CNT = rng.multinomial(len(allp), np.full(len(allp), 1/len(allp)), size=NB).astype(float)
def W(rr):
    pp = [pers(pathlib.PurePath(r["path"]).name)[0] for r in rr]
    a = np.array([pidx[p[0]] for p in pp]); b = np.array([pidx[p[-1]] for p in pp])
    w = CNT[:,a]*CNT[:,b]; same = a==b; w[:,same] = CNT[:,a[same]]; return w
def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable"); ns = neg[ob]
    lo, hi = np.searchsorted(ns,pos,"left"), np.searchsorted(ns,pos,"right")
    C = np.concatenate([np.zeros((wn.shape[0],1)), np.cumsum(wn[:,ob],1)],1)
    return (wp*(C[:,lo]+0.5*(C[:,hi]-C[:,lo]))).sum(1)/np.maximum(wp.sum(1)*C[:,-1],1e-12)
def A(pos,neg): return float(wauc(pos,neg,np.ones((1,len(pos))),np.ones((1,len(neg))))[0])
def eer(b, m, wb=None, wm=None):
    wb = np.ones(len(b)) if wb is None else wb; wm = np.ones(len(m)) if wm is None else wm
    t = np.unique(np.r_[b,m])
    ob = np.argsort(b); om = np.argsort(m)
    cb = np.r_[0,np.cumsum(wb[ob])]; cm = np.r_[0,np.cumsum(wm[om])]
    fpr = 1 - cb[np.searchsorted(b[ob], t, "left")]/cb[-1]     # b >= t
    fnr = cm[np.searchsorted(m[om], t, "left")]/cm[-1]         # m < t
    i = int(np.argmin(np.abs(fpr-fnr))); return 100*(fpr[i]+fnr[i])/2, float(t[i])
DETS = [("MADation ViT-B/16 rel", "smadcvpr_runs/A12_scored/A12REL/madation_vitb16/scores_eval.npz", "score_noTTA"),
        ("MADation ViT-L/14 rel", "smadcvpr_runs/A12_scored/A12REL/madation_vitl14/scores_eval.npz", "score_noTTA"),
        ("SelfMAD rel own prep", "experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz", "score"),
        ("SelfMAD rel our pipe", "smadcvpr_runs/A12_scored/A12REL/selfmad_hrnet_w18/scores_eval.npz", "score_noTTA"),
        ("MixFaceNet rel (our frames, desc.)", "smadcvpr_runs/A12_scored/A12REL/mixfacenet_mad_smdd/scores_eval.npz", None)]
out = {}
for lab, f, key in DETS:
    z = np.load(MC/f, allow_pickle=False)
    if key is None: key = "score_noTTA" if "score_noTTA" in z.files else "score"
    em = dict(zip(z["id"].tolist(), z[key].astype(float)))
    print(f"\n===== {lab} ({key})")
    print(f"{'cell':22s} {'nM':>5s} {'AUC all':>8s} {'AUC neu':>8s} {'AUC smi':>8s} {'smi-neu [95%]':>24s} | {'EER all':>7s} {'EER neu':>7s} {'EER smi':>7s} {'neu-all [95%]':>22s} | {'P(neu>smi) genuine [95%]':>26s} {'paired':>7s} | BPCER@EERthr neu/smi")
    for cn,(mr,br) in CELLS.items():
        if not all(r["id"] in em for r in mr+br):
            miss = sum(r["id"] not in em for r in mr+br); print(f"{cn:22s} missing {miss} scores"); continue
        sm = np.array([em[r["id"]] for r in mr]); sb = np.array([em[r["id"]] for r in br])
        ex = np.array([pers(pathlib.PurePath(r["path"]).name)[1][0] for r in br]); neu = ex=="03"; smi = ex=="08"
        wm, wb = W(mr), W(br)
        a_all, a_n, a_s = A(sm,sb), A(sm,sb[neu]), A(sm,sb[smi])
        rep_d = wauc(sm,sb[smi],wm,wb[:,smi]) - wauc(sm,sb[neu],wm,wb[:,neu])
        e_all,t = eer(sb,sm); e_n,_ = eer(sb[neu],sm); e_s,_ = eer(sb[smi],sm)
        rep_e = np.array([eer(sb[neu],sm,wb[i][neu],wm[i])[0]-eer(sb,sm,wb[i],wm[i])[0] for i in range(0,NB,2)])
        g = A(sb[neu], sb[smi]); rep_g = wauc(sb[neu],sb[smi],wb[:,neu],wb[:,smi])
        # paired by person
        pn = {pers(pathlib.PurePath(r["path"]).name)[0][0]: s for r,s,e in zip(br,sb,ex) if e=="03"}
        ps = {pers(pathlib.PurePath(r["path"]).name)[0][0]: s for r,s,e in zip(br,sb,ex) if e=="08"}
        common = sorted(set(pn)&set(ps)); k = sum(pn[c]>ps[c] for c in common)
        pv = binomtest(k, len(common), 0.5).pvalue
        bn, bs = float((sb[neu]>=t).mean()), float((sb[smi]>=t).mean())
        print(f"{cn:22s} {len(sm):5d} {a_all:8.3f} {a_n:8.3f} {a_s:8.3f} {a_s-a_n:+7.3f} [{np.percentile(rep_d,2.5):+.3f},{np.percentile(rep_d,97.5):+.3f}] | {e_all:7.2f} {e_n:7.2f} {e_s:7.2f} {e_n-e_all:+6.2f} [{np.percentile(rep_e,2.5):+.2f},{np.percentile(rep_e,97.5):+.2f}] | {g:6.3f} [{np.percentile(rep_g,2.5):.3f},{np.percentile(rep_g,97.5):.3f}] {k:3d}/{len(common)} p={pv:.1e} | {bn:.3f}/{bs:.3f}")
        out[f"{lab}|{cn}"] = dict(auc_all=a_all, auc_neu=a_n, auc_smi=a_s, d=[float(np.percentile(rep_d,2.5)), float(np.percentile(rep_d,97.5))], eer_all=e_all, eer_neu=e_n, eer_smi=e_s, g=g)
    # MorDIFF balanced cell: 2x2
    mr, br = CELLS["mordiff/mordiff"]
    if all(r["id"] in em for r in mr+br):
        sm = np.array([em[r["id"]] for r in mr]); sb = np.array([em[r["id"]] for r in br])
        exm = np.array([pers(pathlib.PurePath(r["path"]).name)[1][0] for r in mr]); exb = np.array([pers(pathlib.PurePath(r["path"]).name)[1][0] for r in br])
        print("  MorDIFF 2x2 AUC (morph expr vs genuine expr): " + ", ".join(f"M{a}/G{b} {A(sm[exm==a], sb[exb==b]):.3f}" for a in ("03","08") for b in ("03","08")) + f" | morph smi vs morph neu {A(sm[exm=='08'], sm[exm=='03']):.3f}")
