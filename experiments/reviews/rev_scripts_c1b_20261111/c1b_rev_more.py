"""Reviewer follow-ups: FERET saturation / detail response / joint regression; FRLL extra regions; FRGC within-subject."""
import csv, re, sys, collections, os
import numpy as np
from scipy.stats import spearmanr
MC = "/home/narolski/mambamorph-code/"
S = MC + "smadcvpr_runs/A12_scored/"
SP = "/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/c1b_review/"
rows = [r for r in csv.DictReader(open(MC + "smadcvpr_data/manifests/eval.csv")) if r["variant"] == "orig"]
_Z = np.load(SP + "feats.npz"); F = {k: _Z[k] for k in _Z.files}
fid = {i: k for k, i in enumerate(F["id"].tolist())}
def rel(n): return (S + f"A12REL/{n}/scores_eval.npz", "score_noTTA")
def rec(arch, lr, seed, ck): return (S + f"A12BR/a12_{arch}_d0_train90_none_lr{lr}_s{seed}_r/scores_eval_{ck}.npz", "score")
DET = collections.OrderedDict()
for k, n in (("REL ViT-L/14", "madation_vitl14"), ("REL ViT-B/16", "madation_vitb16"), ("REL FE ViT-B/16", "madation_fe_vitb16"), ("REL FE ViT-L/14", "madation_fe_vitl14"), ("REL SelfMAD ourpipe", "selfmad_hrnet_w18")):
    DET[k] = rel(n)
for ck in ("last", "es"):
    for s in range(1, 6): DET[f"M3L s{s} {ck}"] = rec("clip_vitl14_madation_r224", "3.33e-06", s, ck)
    for s in range(1, 9): DET[f"M3 s{s} {ck}"] = rec("clip_vitb16_madation_r224", "3.33e-06", s, ck)
SC = {}
for n, (f, k) in DET.items():
    z = np.load(f, allow_pickle=False); SC[n] = dict(zip(z["id"].tolist(), z[k].astype(np.float64)))
def logit(p):
    p = np.clip(p, 1e-12, 1 - 1e-12); return np.log(p / (1 - p))
def gen(fam):
    out = {}
    for r in rows:
        if r["family"] == fam and r["label"] == "0":
            m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1]); out[(m.group(1), m.group(2))] = r["id"]
    return out
GF = gen("frll_bona"); P = sorted({p for p, e in GF})
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import hashlib
ids = [GF[(p, e)] for p in P for e in ("03", "08")]
X = np.array([F["mouth"][fid[i]] for i in ids], float); y = np.array([0, 1] * len(P)); pg = np.repeat(P, 2)
fold = np.array([int(hashlib.sha1(f"c3-{q}".encode()).hexdigest(), 16) % 5 for q in pg]); cvl = np.zeros(len(ids))
for f in range(5):
    m = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(X[fold != f], y[fold != f]); cvl[fold == f] = m.decision_function(X[fold == f])
probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(X, y)
pl3, pl8 = cvl[0::2], cvl[1::2]

# ---- FERET
dev = [r for r in rows if r["set"] == "devbona"]
d = collections.defaultdict(dict)
for r in dev:
    m = re.match(r"^(\d{5})_(\d{6})_(fa|fb)(_[a-z])?_orig", r["path"].rsplit("/", 1)[1])
    if m: d[(m.group(1), m.group(2), m.group(4) or "")][m.group(3)] = r["id"]
pairs = sorted(k for k, v in d.items() if len(v) == 2); subj = np.array([k[0] for k in pairs])
fa = [d[k]["fa"] for k in pairs]; fb = [d[k]["fb"] for k in pairs]
ia = np.array([fid[i] for i in fa]); ib = np.array([fid[i] for i in fb])
la = probe.decision_function(F["mouth"][ia].astype(float)); lb = probe.decision_function(F["mouth"][ib].astype(float))
print("probe on the pair viewed by the reviewer (00002_930831: fa neutral, fb smiling by eye):", [(round(float(la[j]), 2), round(float(lb[j]), 2)) for j, k in enumerate(pairs) if k[:2] == ("00002", "930831")])
clear = ((la < 0) & (lb > 0)) | ((la > 0) & (lb < 0)); strong = np.abs(lb - la) > np.quantile(np.abs(lb - la), 0.8)
smi_is_b = lb > la
def cb(x, cl, B=2000, seed=3):
    rng = np.random.default_rng(seed); u, inv = np.unique(cl, return_inverse=True); s = np.bincount(inv, weights=x); c = np.bincount(inv)
    bs = [];
    for _ in range(B):
        k = rng.integers(0, len(u), len(u)); bs.append(s[k].sum() / c[k].sum())
    return np.percentile(bs, 2.5), np.percentile(bs, 97.5)
print("\n## FERET: within probe-clear pairs (n=%d), share where the MORE-smiling frame has the larger statistic" % clear.sum())
for c in ("ge_all", "ge_mouth", "ge_upper", "ge_cheek", "bytes", "lum"):
    ca, cbv = F[c][ia], F[c][ib]; more = np.where(smi_is_b, cbv > ca, ca > cbv)
    print(f"  {c:9s}: clear pairs {more[clear].mean():.3f}; top-20% |dprobe| pairs {more[strong].mean():.3f}; (FRLL: 08 larger in {np.mean(F[c][[fid[GF[(p,'08')]] for p in P]] > F[c][[fid[GF[(p,'03')]] for p in P]]):.3f})")
print("\n## FERET vs FRLL: score regime and standardised within-pair effect (dz = mean / sd of logit(less-smiling) - logit(more-smiling))")
print("  detector | FRLL median score 03/08, sd logit across photos, dz, share | FERET median score, sd logit across photos, clear pairs: dz, share [CI]; strong pairs share | FERET detail: share s(less ge_all) > s(more ge_all); share s(fewer bytes) > s(more bytes)")
def ols(yv, Xv):
    Xs = np.c_[np.ones(len(yv)), (Xv - Xv.mean(0)) / Xv.std(0)]; b = np.linalg.lstsq(Xs, (yv - yv.mean()) / yv.std(), rcond=None)[0]; return b[1:]
res = {}
for n in DET:
    sc = SC[n]
    f3 = logit(np.array([sc[GF[(p, "03")]] for p in P])); f8 = logit(np.array([sc[GF[(p, "08")]] for p in P])); dF = f3 - f8
    sa = logit(np.array([sc[i] for i in fa])); sb = logit(np.array([sc[i] for i in fb]))
    dE = np.where(smi_is_b, sa - sb, sb - sa)           # less-smiling minus more-smiling
    sh = (dE > 0) + 0.5 * (dE == 0); ci = cb(sh[clear], subj[clear])
    ga, gb = F["ge_all"][ia], F["ge_all"][ib]; dG = np.where(ga < gb, sa - sb, sb - sa)
    ba, bb = F["bytes"][ia], F["bytes"][ib]; dB = np.where(ba < bb, sa - sb, sb - sa)
    # joint standardised regression of (s_fa - s_fb) on d probe (fb - fa) and d log ge_all (fb - fa), d log ge_upper
    Xr = np.c_[lb - la, np.log(gb) - np.log(ga), np.log(F["ge_upper"][ib]) - np.log(F["ge_upper"][ia])]
    b = ols(sa - sb, Xr)
    # same on FRLL
    g3 = np.array([F["ge_all"][fid[GF[(p, "03")]]] for p in P]); g8 = np.array([F["ge_all"][fid[GF[(p, "08")]]] for p in P])
    u3 = np.array([F["ge_upper"][fid[GF[(p, "03")]]] for p in P]); u8 = np.array([F["ge_upper"][fid[GF[(p, "08")]]] for p in P])
    bF = ols(dF, np.c_[pl8 - pl3, np.log(g8) - np.log(g3), np.log(u8) - np.log(u3)])
    res[n] = dict(feret_clear=sh[clear].mean(), feret_strong=sh[strong].mean(), ge=np.mean(dG > 0), by=np.mean(dB > 0), b=b, bF=bF)
    if n.startswith("REL") or n.endswith("s1 last") or n.endswith("s1 es") or n in ("M3 s5 last", "M3L s3 last"):
        print(f"  {n:18s} | {np.median(np.array([sc[GF[(p,'03')]] for p in P])):.4f}/{np.median(np.array([sc[GF[(p,'08')]] for p in P])):.4f}, sd {np.std(np.r_[f3, f8]):.2f}, dz {dF.mean()/dF.std():+.2f}, {np.mean(dF>0):.2f} | {np.median(np.array([sc[i] for i in fa+fb])):.4f}, sd {np.std(np.r_[sa, sb]):.2f}, dz {dE[clear].mean()/dE[clear].std():+.2f}, {sh[clear].mean():.3f} [{ci[0]:.3f},{ci[1]:.3f}]; strong {sh[strong].mean():.3f} | ge {np.mean(dG>0):.3f}; bytes {np.mean(dB>0):.3f} | FERET std. coef dprobe {b[0]:+.2f}, dlog ge_all {b[1]:+.2f}, dlog ge_upper {b[2]:+.2f} | FRLL std. coef dprobe {bF[0]:+.2f}, dlog ge_all {bF[1]:+.2f}, dlog ge_upper {bF[2]:+.2f}")
for grp, names in (("M3L last", [f"M3L s{s} last" for s in range(1, 6)]), ("M3 last", [f"M3 s{s} last" for s in range(1, 9)]), ("M3L es", [f"M3L s{s} es" for s in range(1, 6)]), ("M3 es", [f"M3 s{s} es" for s in range(1, 9)])):
    print(f"  == {grp}: FERET clear " + " ".join(f"{res[n]['feret_clear']:.2f}" for n in names) + " | strong " + " ".join(f"{res[n]['feret_strong']:.2f}" for n in names)
          + " | s(less ge) > s(more ge) " + " ".join(f"{res[n]['ge']:.2f}" for n in names) + " | s(fewer bytes) > " + " ".join(f"{res[n]['by']:.2f}" for n in names))
    print(f"       FERET std coef (dprobe, dlog ge_all, dlog ge_upper), seed mean: " + " ".join(f"{np.mean([res[n]['b'][j] for n in names]):+.2f}" for j in range(3)) + "   FRLL: " + " ".join(f"{np.mean([res[n]['bF'][j] for n in names]):+.2f}" for j in range(3)))

# ---- FRGC within-subject (third pool, not session-matched)
fr = [r for r in dev if r["path"].rsplit("/", 1)[1].startswith("nd1")]
sj = np.array([re.match(r"nd1_[A-Za-z]+\d{4}_(\d{5})d", r["path"].rsplit("/", 1)[1]).group(1) for r in fr]); ii = np.array([fid[r["id"]] for r in fr])
lp = probe.decision_function(F["mouth"][ii].astype(float)); lg = np.log(F["ge_all"][ii])
print(f"\n## FRGC in devbona: {len(fr)} photos, {len(set(sj))} subjects; probe flags smiling {np.mean(lp > 0):.3f}")
def within(v):
    out = v.astype(float).copy()
    for s_ in np.unique(sj):
        k = sj == s_; out[k] -= out[k].mean()
    return out
wp_, wg = within(lp), within(lg)
# within-subject pairs: most vs least smiling photo by probe, requiring one >0 and one <0
print("  detector | within-subject: share s(least-smiling photo) > s(most-smiling photo), subjects with probe-clear extremes | within-subject Spearman(score, probe) | within-subject Spearman(score, log ge_all)")
subs = [s_ for s_ in np.unique(sj) if (lp[sj == s_].max() > 0.5) and (lp[sj == s_].min() < -0.5)]
for n in ["REL ViT-L/14", "REL ViT-B/16", "REL FE ViT-B/16", "REL FE ViT-L/14", "REL SelfMAD ourpipe"] + [f"M3L s{s} last" for s in range(1, 6)] + [f"M3 s{s} last" for s in (1, 4, 5)] + ["M3L s1 es", "M3 s1 es"]:
    sc = SC[n]; s = logit(np.array([sc[r["id"]] for r in fr])); ws = within(s)
    x = []
    for s_ in subs:
        k = np.where(sj == s_)[0]; lo, hi = k[np.argmin(lp[k])], k[np.argmax(lp[k])]; x.append(1.0 if s[lo] > s[hi] else 0.5 if s[lo] == s[hi] else 0.0)
    print(f"  {n:18s} | {np.mean(x):.3f} (n={len(subs)}) | {spearmanr(ws, wp_).statistic:+.2f} | {spearmanr(ws, wg).statistic:+.2f}")
