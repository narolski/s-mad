import sys, csv, numpy as np, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
from scipy.stats import binomtest, wilcoxon
R = rows_eval(); ids = [r["id"] for r in R]
dev = sel(R, "devbona","devbona","orig","0")
P = {v: sel(R,"frllm","frll_bona",v,"0") for v in ("orig","jpeg90","jpeg70","jpeg50","blur1","resample50")}
P["mordiff_align"] = sel(R,"mordiff","mordiff_bona","orig","0")
P["dim_copy"] = sel(R,"dim","dim_bona","orig","0")
for f in FAMS: P["E7 "+f] = sel(R, SETOF[f], f, "resmatch", "0")
M = {f: sel(R, SETOF[f], f, "orig", "1") for f in FAMS}
stem = lambda i: R[i]["name"][:6]
a43 = list(csv.DictReader(open(A43/"data/manifests/a43.csv"))); a43ids = [r["id"] for r in a43]
Eix = [i for i, r in enumerate(a43) if r["source"]=="a43" and r["arm"]=="E"]; Estem = [a43[i]["src_a"] for i in Eix]
dets = {"ViT-L/14": ("rel","madation_vitl14"), "ViT-B/16": ("rel","madation_vitb16"), "FE ViT-L/14": ("rel","madation_fe_vitl14"),
        "SelfMAD ours": ("rel","selfmad_hrnet_w18"), "SelfMAD own": ("own",None)}
for nm, (kind, d) in dets.items():
    if kind == "rel":
        s = rel(d, ids); sE = load(A43/f"a43_out/a43/{d}/rel/scores_a43.npz", a43ids, "logit_noTTA")[Eix]
        t = thr(s[dev], 0.05)
    else:
        s = load(OWN, ids, "score"); sE = load(A43/"a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz", a43ids, "score")[Eix]
        t = thr(s[P["orig"]], 0.05)
    o = dict(zip([stem(i) for i in P["orig"]], s[P["orig"]]))
    t_orig = thr(s[P["orig"]], 0.05)
    neu = np.array([stem(i)[4:6]=="03" for i in P["orig"]])
    t_orig_neu = thr(s[P["orig"]][neu], 0.05)
    print(f"\n=== {nm}: t_dev5 {t:.4f}  t_FRLLorig5 {t_orig:.4f} t_FRLLorigNeutral5 {t_orig_neu:.4f}")
    if kind == "rel":
        d_ = s[dev]; print(f"   devbona realised FA {100*(d_>t).mean():.2f}; AUC(FRLL orig > devbona) {auc(s[P['orig']], d_):.3f}; devbona FA at t_FRLLorig5 {100*(d_>t_orig).mean():.1f}%")
        fer = np.array(["nd1" not in R[i]["name"] and not R[i]["name"].startswith("0") is False for i in dev])
        isfrgc = np.array([("nd1" in R[i]["name"]) or R[i]["name"][:2] in ("02","04") and "d" in R[i]["name"][:12] for i in dev])
    pools = [("stored-small E", sE, Estem)] + [(k, s[v], [stem(i) for i in v]) for k, v in P.items()]
    for k, x, st in pools:
        if not np.isfinite(x).all(): print(f"   {k:16s} not scored"); continue
        st = np.array(st); n3 = np.array([q[4:6]=="03" for q in st])
        ox = np.array([o[q] for q in st])
        fa, fan = 100*(x>t).mean(), 100*(x[n3]>t).mean()
        up = int(((x>t)&~(ox>t)).sum()); dn = int((~(x>t)&(ox>t)).sum())
        upn = int(((x>t)&~(ox>t))[n3].sum()); dnn = int((~(x>t)&(ox>t))[n3].sum())
        p = binomtest(min(up,dn), up+dn, .5).pvalue if up+dn else 1
        # FA at thresholds fitted on FRLL orig itself (pool offset removed)
        fo, fon = 100*(x>t_orig).mean(), 100*(x[n3]>t_orig_neu).mean()
        dl = x - ox
        sd = s[P["orig"]].std()
        try: w = wilcoxon(dl).pvalue
        except Exception: w = float("nan")
        print(f"   {k:16s} FA@dev neu/all {fan:5.1f}/{fa:5.1f}  +{up}/-{dn} (neu +{upn}/-{dnn}) p={p:.1e} | FA@FRLLorig-thr all {fo:5.1f} neu(neu-thr) {fon:5.1f} | paired shift: median {np.median(dl):+.3f} ({np.median(dl)/sd:+.2f} SD) share up {100*(dl>0).mean():.0f}% wilcoxon p={w:.1e}")
    # misses
    line1, line2, line3, line4 = [], [], [], []
    for f in FAMS:
        m = s[M[f]]; b = s[sel(R, NATB[f][0], NATB[f][1], "orig", "0")]
        bn = b[np.array([R[i]["name"][4:6]=="03" for i in sel(R, NATB[f][0], NATB[f][1], "orig", "0")])]
        tb = thr(b, 0.05); tbn = thr(bn, 0.05)
        line1.append(100*(m<=t).mean()); line2.append(100*(m<=tb).mean()); line3.append(100*(m<=tbn).mean()); line4.append(eer(b, m))
    f1 = lambda L: " ".join(f"{v:5.1f}" for v in L) + f" | mean {np.mean(L):5.1f}"
    print("   fams:", " ".join(f"{f[:5]:>5s}" for f in FAMS))
    print("   miss@dev5      ", f1(line1))
    print("   miss@cell-bona5", f1(line2))
    print("   miss@cell-neu5 ", f1(line3))
    print("   EER (cell)     ", f1(line4))
