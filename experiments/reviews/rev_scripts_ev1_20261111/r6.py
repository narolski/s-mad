import sys, csv, re, numpy as np, pathlib, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lib import *
from scipy.stats import spearmanr
R = rows_eval(); ids = [r["id"] for r in R]
G = list(csv.DictReader(open(GTEST))); gid = [r["id"] for r in G]
orig = sel(R,"frllm","frll_bona","orig","0")
M = {f: sel(R, SETOF[f], f, "orig", "1") for f in FAMS}
# ---------------- Part B sample: file width and border nulls
z = np.load("/mnt/t7/smad_next/EV1/feat.npz", allow_pickle=False)
suf = {str(k)[str(k).find("eval/"):]: float(v) for k, v in zip(z["al_path"], z["al_zero"]) if "eval/" in str(k)}
print("Part B sample: O = max(AUC, 1-AUC) of stored width and of zero-border fraction (all photos / neutral-only)")
for f in FAMS:
    b = sel(R, NATB[f][0], NATB[f][1], "orig", "0"); m = M[f]
    neu = np.array([R[i]["name"][4:6]=="03" for i in b])
    w = lambda ix: np.array([float(R[i]["native_w"]) for i in ix]); zb = lambda ix: np.array([suf[R[i]["path"]] for i in ix])
    a1 = auc(w(m), w(b)); a2 = auc(zb(m), zb(b)); a2n = auc(zb(m), zb(b)[neu])
    print(f"  {f:13s} width O {max(a1,1-a1):.3f}  border O {max(a2,1-a2):.3f} (neutral-only {max(a2n,1-a2n):.3f}); border median genuine {np.median(zb(b)):.3f} morph {np.median(zb(m)):.3f}")
# ---------------- Part B.2 sample: detector AUC neutral-only vs all
sL = rel("madation_vitl14", ids); sB = rel("madation_vitb16", ids); own = load(OWN, ids, "score")
neu = np.array([R[i]["name"][4:6]=="03" for i in orig])
for nm, s, f in (("ViT-L/14", sL, "amsl"), ("ViT-L/14", sL, "stylegan"), ("ViT-B/16", sB, "greedy_dim"), ("SelfMAD own", own, "amsl"), ("ViT-L/14", sL, "greedy_dim")):
    b = s[orig]; m = s[M[f]]
    print(f"  {nm:12s} {f:11s} AUC neutral-only {auc(m, b[neu]):.3f} EER {eer(b[neu], m):.1f} | all {auc(m, b):.3f} EER {eer(b, m):.1f} | smiling-only EER {eer(b[~neu], m):.1f}")
# ---------------- Part B.3: within-person neutral above smiling
def share(s, ix):
    d = {}
    for i in ix: d.setdefault(R[i]["name"][:3], {})[R[i]["name"][4:6]] = s[i]
    v = [1.0 if q["03"] > q["08"] else 0.5 if q["03"] == q["08"] else 0.0 for q in d.values() if len(q) == 2]
    return np.mean(v), len(v)
pools = {"FRLL orig (202->132)": orig, "resample50 (eff 101)": sel(R,"frllm","frll_bona","resample50","0"), "jpeg50": sel(R,"frllm","frll_bona","jpeg50","0"),
         "E7 facemorpher (138)": sel(R,"frllm","facemorpher","resmatch","0"), "E7 opencv (130)": sel(R,"frllm","opencv","resmatch","0"),
         "E7 amsl (113)": sel(R,"frllm","amsl","resmatch","0"), "E7 webmorph (112)": sel(R,"frllm","webmorph","resmatch","0"),
         "E7 dim_a (63)": sel(R,"dim","dim_a","resmatch","0"), "E7 greedy_dim (63.5)": sel(R,"dim","greedy_dim","resmatch","0"),
         "MorDIFF alignment (tight frame, full res)": sel(R,"mordiff","mordiff_bona","orig","0"), "E7 mordiff (65, tight frame)": sel(R,"mordiff","mordiff","resmatch","0")}
fn = {pathlib.PurePath(r["path"]).stem: i for i, r in enumerate(G) if r["family"]=="fei_bona_neutral"}
fs = {pathlib.PurePath(r["path"]).stem: i for i, r in enumerate(G) if r["family"]=="fei_bona_smiling"}
both = sorted(set(fn) & set(fs), key=int)
print("\nPart B.3 sample: share of persons with neutral scored above smiling")
dets = [("ViT-L/14 release", rel("madation_vitl14", ids), rel("madation_vitl14", gid, "gtest")), ("ViT-B/16 release", sB, rel("madation_vitb16", gid, "gtest")),
        ("FE ViT-L/14 release", rel("madation_fe_vitl14", ids), rel("madation_fe_vitl14", gid, "gtest"))]
import glob
for p in sorted(glob.glob(str(A12BR/"*"))):
    pass
for nm, s, sg in dets:
    print(" ", nm)
    for k, ix in pools.items():
        v, n = share(s, ix); print(f"     {k:42s} {v:.2f} (n={n})")
    xs = np.array([sg[fn[p]] for p in both]); xm = np.array([sg[fs[p]] for p in both])
    print(f"     FEI (native IED 90 -> 132, n={len(both)})            {np.mean(np.where(xs>xm,1,np.where(xs==xm,.5,0))):.2f}; median paired diff neutral-smiling {np.median(xs-xm):+.3f}")
    # FRLL: does the within-person score gap follow the within-person file-size ratio?
    d = {}
    for i in orig: d.setdefault(R[i]["name"][:3], {})[R[i]["name"][4:6]] = (s[i], float(R[i]["file_bytes"]))
    gap = np.array([q["03"][0]-q["08"][0] for q in d.values()]); lr = np.array([np.log(q["08"][1]/q["03"][1]) for q in d.values()])
    r_ = spearmanr(gap, lr)
    print(f"     FRLL: median gap neutral-smiling {np.median(gap):+.3f}; file-size ratio smiling/neutral median {np.exp(np.median(lr)):.2f}; Spearman(gap, log size ratio) {r_.statistic:+.2f} p={r_.pvalue:.3f}")
    # FEI
    fb = np.array([np.log(float(G[fs[p]]["file_bytes"])/float(G[fn[p]]["file_bytes"])) for p in both]); gapf = xs-xm
    r_ = spearmanr(gapf, fb)
    print(f"     FEI : file-size ratio smiling/neutral median {np.exp(np.median(fb)):.2f} (share >1: {100*(fb>0).mean():.0f}%); Spearman(gap, log size ratio) {r_.statistic:+.2f} p={r_.pvalue:.3f}")
