"""Reviewer analyses for C1b: alternative explanations, second pool (FERET fa/fb), morph-side check, es/last reversal."""
import csv, re, sys, collections
import numpy as np
from scipy.stats import spearmanr, rankdata
MC = "/home/narolski/mambamorph-code/"
S = MC + "smadcvpr_runs/A12_scored/"
SP = "/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/c1b_review/"
rows = [r for r in csv.DictReader(open(MC + "smadcvpr_data/manifests/eval.csv")) if r["variant"] == "orig"]
_Z = np.load(SP + "feats.npz")
F = {k: _Z[k] for k in _Z.files}
fid = {i: k for k, i in enumerate(F["id"].tolist())}
COV = ["bytes", "ied", "lum", "zero", "ge_all", "ge_mouth", "ge_upper", "ge_cheek", "lum_mouth", "lum_upper", "angle"]

def rel(n): return (S + f"A12REL/{n}/scores_eval.npz", "score_noTTA")
def rec(arch, lr, seed, ck, suf="r"): return (S + f"A12BR/a12_{arch}_d0_train90_none_lr{lr}_s{seed}_{suf}/scores_eval_{ck}.npz", "score")
DET = collections.OrderedDict()
DET["REL ViT-L/14"] = rel("madation_vitl14"); DET["REL ViT-B/16"] = rel("madation_vitb16")
DET["REL FE ViT-B/16"] = rel("madation_fe_vitb16"); DET["REL FE ViT-L/14"] = rel("madation_fe_vitl14")
DET["REL FS ViT-B/16"] = rel("madation_fs_vitb16"); DET["REL FS ViT-L/14"] = rel("madation_fs_vitl14")
DET["REL SelfMAD ourpipe"] = rel("selfmad_hrnet_w18"); DET["REL MixFaceNet"] = rel("mixfacenet_mad_smdd")
for ck in ("last", "es"):
    for s in range(1, 6): DET[f"M3L s{s} {ck}"] = rec("clip_vitl14_madation_r224", "3.33e-06", s, ck)
    for s in range(1, 9): DET[f"M3 s{s} {ck}"] = rec("clip_vitb16_madation_r224", "3.33e-06", s, ck)
for s in range(1, 6): DET[f"M1 s{s} last"] = rec("inception_v3_scratch_r299", "0.0003", s, "last")
for s in range(1, 9): DET[f"M5 s{s} last"] = rec("pwmad_densenet121_r224", "0.0001", s, "last")
SC = {}
for n, (f, k) in DET.items():
    z = np.load(f, allow_pickle=False)
    assert str(z["manifest_sha256"]).startswith("86d055d3")
    SC[n] = dict(zip(z["id"].tolist(), z[k].astype(np.float64)))

def logit(p):
    p = np.clip(p, 1e-12, 1 - 1e-12); return np.log(p / (1 - p))

def gen(fam):
    out = {}
    for r in rows:
        if r["family"] == fam and r["label"] == "0":
            m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1]); out[(m.group(1), m.group(2))] = r["id"]
    return out
GF, GM = gen("frll_bona"), gen("mordiff_bona")
P = sorted({p for p, e in GF})

def boot_ci(x, B=2000, seed=7, clusters=None):
    rng = np.random.default_rng(seed); x = np.asarray(x, float)
    if clusters is None:
        bs = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)]
    else:
        cl = np.asarray(clusters); u, inv = np.unique(cl, return_inverse=True)
        sums = np.bincount(inv, weights=x); cnts = np.bincount(inv)
        bs = []
        for _ in range(B):
            k = rng.integers(0, len(u), len(u)); bs.append(sums[k].sum() / cnts[k].sum())
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)

# ---------------- A. covariates on the FRLL frames
print("## A. Do the 03 and 08 frames differ in simple capture/geometry statistics? (frll_bona frames; mordiff_bona for zero/angle)")
cov = {}
for c in COV:
    G = GM if c in ("zero", "angle") else GF
    n3 = np.array([F[c][fid[G[(p, "03")]]] for p in P]); n8 = np.array([F[c][fid[G[(p, "08")]]] for p in P])
    if c == "angle": n3, n8 = np.abs(n3), np.abs(n8)
    cov[c] = (n3, n8)
    print(f"  {c:10s} ({'mordiff crop' if G is GM else 'frll crop'}): median 03 {np.median(n3):10.3f}  08 {np.median(n8):10.3f}   share persons 03 > 08: {np.mean(n3 > n8):.3f}   median rel. diff (08-03)/03 {np.median((n8 - n3) / np.where(n3 == 0, np.nan, n3)):+.3f}")
# signed angle
a3 = np.array([F["angle"][fid[GM[(p, "03")]]] for p in P]); a8 = np.array([F["angle"][fid[GM[(p, "08")]]] for p in P])
print(f"  signed border angle (deg): 03 mean {a3.mean():+.2f} sd {a3.std():.2f}; 08 mean {a8.mean():+.2f} sd {a8.std():.2f}; |angle| mean 03 {np.abs(a3).mean():.2f}, 08 {np.abs(a8).mean():.2f}; nan {np.isnan(a3).sum()} {np.isnan(a8).sum()}")

# ---------------- B. probe (cross-validated by person) on FRLL frames
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import hashlib
ids = [GF[(p, e)] for p in P for e in ("03", "08")]
X = np.array([F["mouth"][fid[i]] for i in ids], float); y = np.array([0, 1] * len(P)); pg = np.repeat(P, 2)
fold = np.array([int(hashlib.sha1(f"c3-{q}".encode()).hexdigest(), 16) % 5 for q in pg])
cvl = np.zeros(len(ids))
for f in range(5):
    m = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(X[fold != f], y[fold != f])
    cvl[fold == f] = m.decision_function(X[fold == f])
probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(X, y)
print(f"\n## B. probe CV accuracy by person {np.mean((cvl > 0) == y):.3f}; within-person share probe(08) > probe(03): {np.mean(cvl[1::2] > cvl[0::2]):.3f}")
pl3, pl8 = cvl[0::2], cvl[1::2]

def wp(name, G=GF):
    sc = SC[name]
    n3 = np.array([sc[G[(p, "03")]] for p in P]); n8 = np.array([sc[G[(p, "08")]] for p in P])
    return n3, n8

print("\n## A/B per detector: AUC_wp, then Spearman of the per-person score difference (logit 03 - logit 08) with covariate differences (03 - 08); and within-expression Spearman(score, covariate)")
hdr = ["probe(08-03)", "ge_all", "ge_upper", "ge_mouth", "lum", "ied", "bytes", "|angle|"]
print("  detector | AUC_wp | " + " | ".join(hdr) + " || within-08: rho(score, probe logit) | within-03: rho(score, probe logit) | within-03 rho(score, ge_upper) | within-08 rho(score, ge_upper)")
def show(name):
    n3, n8 = wp(name); d = logit(n3) - logit(n8)
    out = [f"{spearmanr(d, pl8 - pl3).statistic:+.2f}"]
    for c in ("ge_all", "ge_upper", "ge_mouth", "lum", "ied", "bytes", "angle"):
        c3, c8 = cov[c]; out.append(f"{spearmanr(d, c3 - c8).statistic:+.2f}")
    w8 = spearmanr(logit(n8), pl8).statistic; w3 = spearmanr(logit(n3), pl3).statistic
    u3 = spearmanr(logit(n3), cov["ge_upper"][0]).statistic; u8 = spearmanr(logit(n8), cov["ge_upper"][1]).statistic
    print(f"  {name:20s} | {np.mean(n3 > n8):.3f} | " + " | ".join(out) + f" || {w8:+.2f} | {w3:+.2f} | {u3:+.2f} | {u8:+.2f}")
for n in ["REL ViT-L/14", "REL ViT-B/16", "REL FE ViT-B/16", "REL FE ViT-L/14", "REL SelfMAD ourpipe"] + [f"M3L s{s} last" for s in range(1, 6)] + [f"M3 s{s} last" for s in range(1, 9)]:
    show(n)
print("  (|rho| > 0.195 is p < 0.05 two-sided at n = 102, uncorrected)")

# stratified: does the direction survive in persons whose 08 frame is NOT sharper / NOT larger etc.?
print("\n## A2. AUC_wp within strata of the covariate difference (persons where the covariate goes one way vs the other)")
for name in ["REL ViT-L/14", "M3L s1 last", "M3 s1 last", "M3 s4 last", "REL FE ViT-B/16"]:
    n3, n8 = wp(name); ind = (n3 > n8).astype(float); line = []
    for c in ("ge_all", "ge_upper", "ge_mouth", "lum", "ied", "bytes", "angle"):
        c3, c8 = cov[c]; hi = c3 > c8
        line.append(f"{c}: 03>08 n={hi.sum():3d} {ind[hi].mean() if hi.sum() else float('nan'):.2f} / 03<=08 n={(~hi).sum():3d} {ind[~hi].mean() if (~hi).sum() else float('nan'):.2f}")
    print(f"  {name:16s} " + "; ".join(line))

# probe dose-response: tertiles of probe(08)-probe(03)
print("\n## B2. dose-response: mean logit-score difference (03 - 08) by tertile of the probe difference (08 - 03)")
dp = pl8 - pl3; q = np.quantile(dp, [1 / 3, 2 / 3]); ter = np.digitize(dp, q)
for name in ["REL ViT-L/14", "M3L s1 last", "M3L s3 last", "M3 s1 last", "M3 s5 last", "REL FE ViT-B/16"]:
    n3, n8 = wp(name); d = logit(n3) - logit(n8)
    print(f"  {name:16s} " + "  ".join(f"T{t+1}: median {np.median(d[ter == t]):+.3f} (share>0 {np.mean(d[ter == t] > 0):.2f})" for t in range(3)) + f"   rho {spearmanr(d, dp).statistic:+.2f} p {spearmanr(d, dp).pvalue:.3f}")

# ---------------- C. FERET fa/fb second pool
print("\n## C. Second pool: FERET fa/fb same-session pairs in devbona (already scored)")
dev = [r for r in rows if r["set"] == "devbona"]
d = collections.defaultdict(dict)
for r in dev:
    m = re.match(r"^(\d{5})_(\d{6})_(fa|fb)(_[a-z])?_orig", r["path"].rsplit("/", 1)[1])
    if m: d[(m.group(1), m.group(2), m.group(4) or "")][m.group(3)] = r["id"]
pairs = sorted(k for k, v in d.items() if len(v) == 2)
subj = np.array([k[0] for k in pairs])
fa = [d[k]["fa"] for k in pairs]; fb = [d[k]["fb"] for k in pairs]
la = probe.decision_function(np.array([F["mouth"][fid[i]] for i in fa], float)); lb = probe.decision_function(np.array([F["mouth"][fid[i]] for i in fb], float))
print(f"  pairs {len(pairs)}, subjects {len(set(subj))}. FRLL-trained probe on FERET: share flagged smiling fa {np.mean(la > 0):.3f}, fb {np.mean(lb > 0):.3f}; share pairs probe(fb) > probe(fa) {np.mean(lb > la):.3f}; median |dlogit| {np.median(np.abs(lb - la)):.2f}")
clear_fb = (lb > 0) & (la < 0); clear_fa = (la > 0) & (lb < 0)
print(f"  pairs with fa neutral & fb smiling by probe: {clear_fb.sum()}; fa smiling & fb neutral: {clear_fa.sum()}; both neutral {((la<0)&(lb<0)).sum()}; both smiling {((la>0)&(lb>0)).sum()}")
for c in ("ge_all", "ge_upper", "ge_mouth", "lum", "bytes", "ied"):
    ca = np.array([F[c][fid[i]] for i in fa]); cb = np.array([F[c][fid[i]] for i in fb])
    print(f"    covariate {c:9s}: share fa > fb {np.mean(ca > cb):.3f}")
dl = lb - la; qq = np.quantile(np.abs(dl), [1 / 3, 2 / 3]); tt = np.digitize(np.abs(dl), qq)
print("  detector | share s(fa) > s(fb) [95% subject bootstrap] | share s(less-smiling) > s(more-smiling) by probe, all pairs [CI] | by |dprobe| tertile T1 T2 T3 | probe-clear pairs (one <0, other >0) [CI] n | rho(dscore fa-fb, dprobe fb-fa)")
def feret(name):
    sc = SC[name]; sa = np.array([sc[i] for i in fa]); sb = np.array([sc[i] for i in fb])
    x1 = (sa > sb) + 0.5 * (sa == sb); c1 = boot_ci(x1, clusters=subj)
    less_is_a = la < lb
    x2 = np.where(less_is_a, (sa > sb) + 0.5 * (sa == sb), (sb > sa) + 0.5 * (sa == sb)); c2 = boot_ci(x2, clusters=subj)
    t = [x2[tt == k].mean() for k in range(3)]
    cl = clear_fb | clear_fa; c3 = boot_ci(x2[cl], clusters=subj[cl])
    rho = spearmanr(logit(sa) - logit(sb), dl).statistic
    return f"  {name:20s} | {x1.mean():.3f} [{c1[0]:.3f},{c1[1]:.3f}] | {x2.mean():.3f} [{c2[0]:.3f},{c2[1]:.3f}] | {t[0]:.2f} {t[1]:.2f} {t[2]:.2f} | {x2[cl].mean():.3f} [{c3[0]:.3f},{c3[1]:.3f}] n={cl.sum()} | {rho:+.2f}", x2[cl].mean()
for n in ["REL ViT-L/14", "REL ViT-B/16", "REL FE ViT-B/16", "REL FE ViT-L/14", "REL FS ViT-B/16", "REL FS ViT-L/14", "REL SelfMAD ourpipe", "REL MixFaceNet"]:
    print(feret(n)[0])
for grp, names in (("M3L last", [f"M3L s{s} last" for s in range(1, 6)]), ("M3 last", [f"M3 s{s} last" for s in range(1, 9)]), ("M3L es", [f"M3L s{s} es" for s in range(1, 6)]),
                   ("M3 es", [f"M3 s{s} es" for s in range(1, 9)]), ("M1 last", [f"M1 s{s} last" for s in range(1, 6)]), ("M5 last", [f"M5 s{s} last" for s in range(1, 9)])):
    vals = []
    for n in names:
        line, v = feret(n); vals.append(v)
        if grp in ("M3L last", "M3 last"): print(line)
    print(f"  == {grp}: probe-clear pairs, share s(less-smiling) > s(more-smiling), per seed: " + " ".join(f"{v:.2f}" for v in vals) + f"  mean {np.mean(vals):.3f}")

# ---------------- D. morph-side within-pair check on MorDIFF
print("\n## D. MorDIFF morphs: same person pair, neutral morph (03/03) vs smiling morph (08/08), 361 pairs")
mm = collections.defaultdict(dict)
for r in rows:
    if r["family"] == "mordiff" and r["label"] == "1":
        m = re.match(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1]); mm[(m.group(1), m.group(3))][m.group(2)] = r["id"]
both = sorted(k for k, v in mm.items() if len(v) == 2)
print("  pairs with both:", len(both))
def morphside(name):
    sc = SC[name]; s3 = np.array([sc[mm[k]["03"]] for k in both]); s8 = np.array([sc[mm[k]["08"]] for k in both])
    return np.mean((s3 > s8) + 0.5 * (s3 == s8)), np.median(s3), np.median(s8)
for n in ["REL ViT-L/14", "REL ViT-B/16", "REL FE ViT-B/16", "REL FE ViT-L/14", "REL SelfMAD ourpipe"]:
    a, m3, m8 = morphside(n); g3, g8 = wp(n, GM)
    print(f"  {n:20s} morphs: share s(neutral morph) > s(smiling morph) {a:.3f} (median {m3:.4f} vs {m8:.4f}); genuine on the same crop: {np.mean(g3 > g8):.3f}")
for grp, names in (("M3L last", [f"M3L s{s} last" for s in range(1, 6)]), ("M3 last", [f"M3 s{s} last" for s in range(1, 9)]), ("M3L es", [f"M3L s{s} es" for s in range(1, 6)]), ("M3 es", [f"M3 s{s} es" for s in range(1, 9)])):
    print(f"  {grp:9s} morphs: " + " ".join(f"{morphside(n)[0]:.2f}" for n in names) + "   | genuine, same crop: " + " ".join(f"{np.mean(wp(n, GM)[0] > wp(n, GM)[1]):.2f}" for n in names))

# ---------------- E. es vs last on the MorDIFF crop
print("\n## E. es/last reversal on the MorDIFF crop: relation to the border tilt (|angle| 08 vs 03) and zero share")
A3, A8 = np.abs(a3), np.abs(a8); more_tilt = A8 > A3
z3, z8 = cov["zero"]
print(f"  persons whose 08 frame is more tilted than 03: {more_tilt.sum()} of 102; median |angle| 03 {np.median(A3):.2f} deg, 08 {np.median(A8):.2f} deg; zero share 03>08 in {np.mean(z3 > z8):.2f}")
for grp, names in (("M3L es", [f"M3L s{s} es" for s in range(1, 6)]), ("M3 es", [f"M3 s{s} es" for s in range(1, 9)]), ("M3L last", [f"M3L s{s} last" for s in range(1, 6)]), ("M3 last", [f"M3 s{s} last" for s in range(1, 9)]), ("REL", ["REL ViT-L/14", "REL ViT-B/16", "REL FE ViT-B/16"])):
    for n in names:
        g3, g8 = wp(n, GM); f3, f8 = wp(n, GF); dm = logit(g3) - logit(g8); df = logit(f3) - logit(f8)
        print(f"  {n:16s} mordiff-crop AUC_wp {np.mean(g3 > g8):.2f} (08 more tilted: {np.mean((g3 > g8)[more_tilt]):.2f}, n={more_tilt.sum()}; else {np.mean((g3 > g8)[~more_tilt]):.2f}) rho(dscore, d|angle| 08-03) {spearmanr(dm, A8 - A3).statistic:+.2f}  rho(dscore, dzero 08-03) {spearmanr(dm, z8 - z3).statistic:+.2f}  rho(d mordiff crop, d frll crop) {spearmanr(dm, df).statistic:+.2f} | median score frll crop 03/08 {np.median(f3):.3f}/{np.median(f8):.3f}  mordiff crop 03/08 {np.median(g3):.3f}/{np.median(g8):.3f}")
