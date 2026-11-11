import csv, re, collections, hashlib
import numpy as np
MC = "/home/narolski/mambamorph-code/"; S = MC + "smadcvpr_runs/A12_scored/"
SP = "/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/c1b_review/"
rows = [r for r in csv.DictReader(open(MC + "smadcvpr_data/manifests/eval.csv")) if r["variant"] == "orig"]
_Z = np.load(SP + "feats.npz"); F = {k: _Z[k] for k in _Z.files}; fid = {i: k for k, i in enumerate(F["id"].tolist())}
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
GF = {}
for r in rows:
    if r["family"] == "frll_bona":
        m = re.match(r"^(\d{3})_(\d{2})_", r["path"].rsplit("/", 1)[1]); GF[(m.group(1), m.group(2))] = r["id"]
P = sorted({p for p, e in GF}); ids = [GF[(p, e)] for p in P for e in ("03", "08")]
probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=5000)).fit(np.array([F["mouth"][fid[i]] for i in ids], float), np.array([0, 1] * len(P)))
d = collections.defaultdict(dict)
for r in rows:
    if r["set"] == "devbona":
        m = re.match(r"^(\d{5})_(\d{6})_(fa|fb)(_[a-z])?_orig", r["path"].rsplit("/", 1)[1])
        if m: d[(m.group(1), m.group(2), m.group(4) or "")][m.group(3)] = r["id"]
pairs = sorted(k for k, v in d.items() if len(v) == 2); subj = np.array([k[0] for k in pairs])
fa = [d[k]["fa"] for k in pairs]; fb = [d[k]["fb"] for k in pairs]
la = probe.decision_function(F["mouth"][[fid[i] for i in fa]].astype(float)); lb = probe.decision_function(F["mouth"][[fid[i] for i in fb]].astype(float))
clear = ((la < 0) & (lb > 0)) | ((la > 0) & (lb < 0)); smi_b = lb > la
def cb(x, cl, fn=np.mean, B=2000, seed=5):
    rng = np.random.default_rng(seed); u = np.unique(cl); idx = {s: np.where(cl == s)[0] for s in u}; out = []
    for _ in range(B):
        k = np.concatenate([idx[s] for s in rng.choice(u, len(u))]); out.append(fn(x[k]))
    return np.percentile(out, 2.5), np.percentile(out, 97.5)
for name, f, key in (("REL ViT-L/14", "A12REL/madation_vitl14/scores_eval.npz", "logit_noTTA"), ("REL ViT-B/16", "A12REL/madation_vitb16/scores_eval.npz", "logit_noTTA"), ("REL FE ViT-B/16", "A12REL/madation_fe_vitb16/scores_eval.npz", "logit_noTTA")):
    z = np.load(S + f, allow_pickle=False); sc = dict(zip(z["id"].tolist(), z[key].astype(np.float64)))
    f3 = np.array([sc[GF[(p, "03")]] for p in P]); f8 = np.array([sc[GF[(p, "08")]] for p in P]); allf = np.r_[f3, f8]
    sa = np.array([sc[i] for i in fa]); sb = np.array([sc[i] for i in fb]); dE = np.where(smi_b, sa - sb, sb - sa)
    lo, hi = allf.min(), allf.max(); inband = (sa >= lo) & (sa <= hi) & (sb >= lo) & (sb <= hi)
    print(f"{name}: FRLL logits: range [{lo:.2f}, {hi:.2f}], median 03 {np.median(f3):.3f} 08 {np.median(f8):.3f}, median gap {np.median(f3 - f8):+.3f}, IQR of gap [{np.percentile(f3-f8,25):+.3f}, {np.percentile(f3-f8,75):+.3f}]")
    print(f"   FERET logits: median {np.median(np.r_[sa, sb]):.2f}, 5-95% [{np.percentile(np.r_[sa,sb],5):.2f}, {np.percentile(np.r_[sa,sb],95):.2f}]; within-pair |d| median {np.median(np.abs(sa-sb)):.3f}")
    c = clear; ci = cb(dE[c], subj[c], np.median)
    print(f"   FERET probe-clear pairs n={c.sum()}: median gap (less - more smiling) {np.median(dE[c]):+.3f} [{ci[0]:+.3f}, {ci[1]:+.3f}], share>0 {np.mean(dE[c] > 0):.3f}")
    c2 = clear & inband
    if c2.sum() > 20:
        ci = cb((dE[c2] > 0).astype(float), subj[c2]); print(f"   ... both photos inside the FRLL logit range: n={c2.sum()} share>0 {np.mean(dE[c2] > 0):.3f} [{ci[0]:.3f}, {ci[1]:.3f}], median gap {np.median(dE[c2]):+.3f}; all pairs in band n={inband.sum()}")
    else: print("   pairs inside the FRLL logit range:", c2.sum(), "of", clear.sum())
