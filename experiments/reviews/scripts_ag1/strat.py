import sys, csv, pathlib, zlib, collections
sys.path.insert(0, "/home/narolski/smad-next/src/AG1")
import numpy as np, ag1_read as A
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
DATA = pathlib.Path("/mnt/t7/smad_next/AG1/data")
rows = list(csv.DictReader(open(DATA / "manifests/ag1.csv")))
z = dict(np.load(DATA / "baselines.npz")); idx = {i: j for j, i in enumerate(z["id"].tolist())}
S = A.load_scores(rows, "/mnt/t7/smad_next/AG1/scoring/a41g_out/ag1", False)
sub = [r for r in rows if A.in_pool(r, "primary") and r["gen"] in ("mip1", "camera")]
pers = sorted({r["pa"] for r in sub} | {r["pb"] for r in sub})
D = A.Draw(pers, 2000, 7)
g = collections.defaultdict(list)
for r in sub: g[r["rung"]].append(r)
def oof_thumb(pos, neg):
    X = np.stack([z["thumb"][idx[r["id"]]] for r in pos + neg]); y = np.r_[np.ones(len(pos)), np.zeros(len(neg))]
    gg = np.array([r["pa"] for r in pos + neg]); o = np.zeros(len(y))
    for tr, te in GroupKFold(5).split(X, y, gg):
        o[te] = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X[tr], y[tr]).decision_function(X[te])
    return o
def strat(pos, neg, cov, sc, nb=5):
    c = np.r_[cov[:len(pos)], cov[len(pos):]]
    qs = np.quantile(c, np.linspace(0, 1, nb + 1)[1:-1])
    bp = np.searchsorted(qs, cov[:len(pos)]); bn = np.searchsorted(qs, cov[len(pos):])
    num = 0; rep = 0; den = 0
    for k in range(nb):
        P = [pos[i] for i in np.where(bp == k)[0]]; N = [neg[i] for i in np.where(bn == k)[0]]
        if len(P) < 3 or len(N) < 3: continue
        sp = np.array([sc[r["id"]] for r in P]); sn = np.array([sc[r["id"]] for r in N])
        w = len(P) * len(N)
        num += w * A.auc(sp, sn); rep = rep + w * A.wauc(sp, sn, D.w([r["pa"] for r in P], [r["pb"] for r in P]), D.w([r["pa"] for r in N], [r["pb"] for r in N])); den += w
    return num / den, A.ci(rep / den)
for a, b, base in (("R2", "R4", "bytes"), ("R2", "R4", "lapvar"), ("R2s", "R4", "thumb"), ("R3", "R4", "bytes"), ("R0", "R2", "thumb")):
    pos, neg = g[b], g[a]
    cov = oof_thumb(pos, neg) if base == "thumb" else np.array([z[base][idx[r["id"]]] for r in pos + neg])
    for rel in ("madation_vitb16", "madation_vitl14", "selfmad_hrnet_w18__own"):
        a0, ci = strat(pos, neg, cov, S[rel])
        print(f"{a}>{b} stratified on {base} quintiles  {rel:24s} {a0:.3f} {[round(x,3) for x in ci]}")
