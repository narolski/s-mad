"""Fixed-threshold re-read of existing scores (EV1): shared loaders and statistics.

Draw and wauc are copied unchanged from src/AD1/ad1_read.py (the pigeonhole person bootstrap of a41_read.py and the
weighted Mann-Whitney AUC of a36_read.wauc). Never opens files whose name contains fst, valx, A12SP or A12-SP.
"""
import csv, hashlib, pathlib, re
import numpy as np
from scipy.stats import beta

MC = pathlib.Path("/home/narolski/mambamorph-code")
SN = pathlib.Path("/home/narolski/smad-next")
OUT = SN / "experiments/EV1_fixed-threshold-reread"
BIG = pathlib.Path("/mnt/t7/smad_next/EV1")
EVAL = MC / "smadcvpr_data/manifests/eval.csv"
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
GTEST = MC / "smadcvpr_data/manifests/gtest.csv"
GTEST_SHA = "5ededd6fbeded7f2d480fe10838cfb7de82319ef5772771ac73eebcefb556a9b"
FFHQM = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs/manifests/ffhqm.csv")
FFHQM_SHA = "732b53c8a8c4b875645c99f11f81b401550a4050361090dea90998d45035234c"
A12REL = MC / "smadcvpr_runs/A12_scored/A12REL"
A12BR = MC / "smadcvpr_runs/A12_scored/A12BR"
SELFMAD_OWN = MC / "experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz"
A36NET = MC / "experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv"
A47I3 = pathlib.Path("/mnt/t7/smad_heldout/a47/runs/A47I3")
SEED = 20261111
B_FULL = 2000

FRLLM = ("amsl", "facemorpher", "opencv", "stylegan", "webmorph")
DIM = ("dim_a", "dim_c", "fast_dim", "fast_dim_ode", "greedy_dim", "greedy_dim_s")
FAMS = FRLLM + ("mordiff",) + DIM
LANDMARK = ("amsl", "facemorpher", "opencv", "webmorph")
GEN_FAMS = ("stylegan", "mordiff") + DIM
FAM_SET = {**{f: "frllm" for f in FRLLM}, "mordiff": "mordiff", **{f: "dim" for f in DIM}}
NATIVE_BONA = {**{f: "frll_bona" for f in FRLLM}, "mordiff": "mordiff_bona", **{f: "dim_bona" for f in DIM}}
FAM_LABEL = {"amsl": "FRLL-Morphs AMSL", "facemorpher": "FRLL-Morphs FaceMorpher", "opencv": "FRLL-Morphs OpenCV",
             "stylegan": "FRLL-Morphs StyleGAN", "webmorph": "FRLL-Morphs WebMorph", "mordiff": "MorDIFF",
             "dim_a": "DiM-A", "dim_c": "DiM-C", "fast_dim": "Fast-DiM", "fast_dim_ode": "Fast-DiM-ODE",
             "greedy_dim": "Greedy-DiM", "greedy_dim_s": "Greedy-DiM-S"}
GVARS = ("orig", "jpeg90", "jpeg70", "jpeg50", "blur1", "resample50")
GATED_FRLL = ("orig", "jpeg90", "jpeg70", "resample50")

RELEASES = [  # (dir, label)
    ("madation_vitb16", "MADation ViT-B/16 release"),
    ("madation_vitl14", "MADation ViT-L/14 release"),
    ("madation_fe_vitb16", "MADation FE ViT-B/16 release"),
    ("madation_fe_vitl14", "MADation FE ViT-L/14 release"),
    ("madation_fs_vitb16", "MADation FS ViT-B/16 release"),
    ("madation_fs_vitl14", "MADation FS ViT-L/14 release"),
    ("madation_vitb16_dnorm", "MADation ViT-B/16 dnorm (diagnostic variant)"),
    ("madation_vitb16_dscale", "MADation ViT-B/16 dscale (diagnostic variant)"),
    ("selfmad_hrnet_w18", "SelfMAD release, our pipeline"),
    ("mixfacenet_mad_smdd", "MixFaceNet-MAD release, our frames"),
]


def forbidden(p):
    s = str(p).lower()
    return any(t in s for t in ("fst", "a12sp", "a12-sp")) or ("valx" in s and "valx_a.csv" not in s)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load_npz(p):
    assert not forbidden(p), p
    return np.load(p, allow_pickle=False)


# ----------------------------------------------------------------------------------------------- manifests
RXB = re.compile(r"^(\d{3})_(\d{2})_")
RXM_MD = re.compile(r"^morph_(\d{3})_(\d{2})_and_(\d{3})_(\d{2})")
RXM_AB = re.compile(r"^(\d{3})_(\d{3})_")


def eval_rows():
    assert sha(EVAL) == EVAL_SHA
    rows = list(csv.DictReader(open(EVAL)))
    for r in rows:
        n = pathlib.PurePath(r["path"]).name
        r["name"] = n
        r["expr"] = None
        if r["set"] in ("mad22", "devbona"):
            r["pers"] = None
            continue
        if r["label"] == "0":
            m = RXB.match(n)
            r["pers"] = (m.group(1),)
            r["expr"] = m.group(2)
        else:
            m = RXM_MD.match(n)
            if m:
                r["pers"] = (m.group(1), m.group(3))
                r["expr"] = m.group(2) + m.group(4)
            else:
                m = RXM_AB.match(n)
                r["pers"] = (m.group(1), m.group(2))
                r["expr"] = "0303"  # DiM README / FRLL-Morphs inferred (C1 probe)
            # stem without variant suffix (to match variants)
        r["stem"] = n[: -len("_" + r["variant"] + ".png")] if r["variant"] != "resmatch" else n
    return rows


class Index:
    """row-index groups of eval.csv."""

    def __init__(self, rows):
        self.rows = rows
        self.g = {}
        for i, r in enumerate(rows):
            self.g.setdefault((r["set"], r["family"], r["variant"], r["label"]), []).append(i)
        self.g = {k: np.array(v) for k, v in self.g.items()}

    def bona(self, fam, var="orig"):
        st = {"frll_bona": "frllm", "dim_bona": "dim", "mordiff_bona": "mordiff"}[fam]
        return self.g[(st, fam, var, "0")]

    def resmatch(self, fam):
        return self.g[(FAM_SET[fam], fam, "resmatch", "0")]

    def morph(self, fam, var="orig"):
        return self.g[(FAM_SET[fam], fam, var, "1")]

    def devbona(self):
        return self.g[("devbona", "devbona", "orig", "0")]


def gtest_rows():
    assert sha(GTEST) == GTEST_SHA
    rows = list(csv.DictReader(open(GTEST)))
    for r in rows:
        r["subj"] = pathlib.PurePath(r["path"]).stem if r["label"] == "0" else None
    return rows


def ffhqm_rows():
    assert sha(FFHQM) == FFHQM_SHA
    return list(csv.DictReader(open(FFHQM)))


# ----------------------------------------------------------------------------------------------- detectors
def recipe_networks():
    out = []
    for ln in open(A36NET):
        if ln.startswith("#"):
            continue
        f = ln.rstrip("\n").split("\t")
        if len(f) < 7 or f[3] != "primary":
            continue
        run = pathlib.PurePath(f[0]).name
        meth = f[4].split()[0]
        out.append({"run": run, "method": meth, "method_label": f[4], "seed": int(f[6])})
    return out


def detectors():
    """list of dicts: name, block, kind, paths."""
    D = []
    for d, lab in RELEASES:
        D.append({"name": lab, "block": "release", "kind": "rel", "dir": A12REL / d})
    D.append({"name": "SelfMAD release, own preprocessing", "block": "release", "kind": "own", "dir": None})
    for n in recipe_networks():
        blk = n["method"] if n["method"] in ("M3", "M3L") else "other recipe"
        D.append({"name": f"{n['method']} seed {n['seed']}", "block": blk, "kind": "recipe", "dir": A12BR / n["run"],
                  "method": n["method"], "method_label": n["method_label"], "seed": n["seed"]})
    return D


def morph_free_networks():
    D = []
    for p in sorted(A47I3.iterdir()):
        if not p.is_dir():
            continue
        meth = "M3" if "clip_vitb16" in p.name else "M1" if "inception" in p.name else None
        s = int(re.search(r"_s(\d+)_i3$", p.name).group(1))
        D.append({"name": f"morph-free {meth} seed {s}", "block": "morph-free", "kind": "recipe", "dir": p,
                  "method": meth, "seed": s})
    return D


def _rel_key(z):
    s = z["score_noTTA"].astype(np.float64)
    if "logit_noTTA" in z.files:
        lg = z["logit_noTTA"].astype(np.float64)
        o = np.argsort(lg, kind="stable")
        if np.all(np.isfinite(lg)) and np.all(np.diff(s[o]) >= 0):
            return lg, "logit_noTTA"
    return s, "score_noTTA"


def load_scores(det, which, ids):
    """scores aligned to `ids` (list of row ids); NaN where the file has no row. which in eval / gtest / ffhqm."""
    if det["kind"] == "own":
        if which != "eval":
            return None, None
        z = load_npz(SELFMAD_OWN)
        assert str(z["manifest_sha256"]) == EVAL_SHA
        s, key = z["score"].astype(np.float64), "score"
    elif det["kind"] == "rel":
        p = det["dir"] / f"scores_{which}.npz"
        if not p.exists():
            return None, None
        z = load_npz(p)
        s, key = _rel_key(z)
    else:
        p = det["dir"] / f"scores_{which}_last.npz"
        if not p.exists():
            return None, None
        z = load_npz(p)
        s, key = z["score"].astype(np.float64), "score"
    sha_need = {"eval": EVAL_SHA, "gtest": GTEST_SHA, "ffhqm": FFHQM_SHA}[which]
    assert str(z["manifest_sha256"]) == sha_need, (det["name"], which)
    m = dict(zip(z["id"].tolist(), s))
    return np.array([m.get(i, np.nan) for i in ids]), key


# ----------------------------------------------------------------------------------------------- statistics
def wauc(pos, neg, wp, wn):
    ob = np.argsort(neg, kind="stable")
    ns = neg[ob]
    lo, hi = np.searchsorted(ns, pos, "left"), np.searchsorted(ns, pos, "right")
    C = np.concatenate([np.zeros((wn.shape[0], 1)), np.cumsum(wn[:, ob], 1)], 1)
    below, tie = C[:, lo], C[:, hi] - C[:, lo]
    return (wp * (below + 0.5 * tie)).sum(1) / np.maximum(wp.sum(1) * C[:, -1], 1e-12)


def auc(pos, neg):
    return float(wauc(np.asarray(pos, float), np.asarray(neg, float), np.ones((1, len(pos))), np.ones((1, len(neg))))[0])


class Draw:
    def __init__(self, pers, B, seed):
        self.per = sorted(set(pers))
        self.pos = {p: i for i, p in enumerate(self.per)}
        n = len(self.per)
        self.C = np.random.default_rng(seed).multinomial(n, np.full(n, 1.0 / n), size=B).astype(np.float64)

    def w(self, pp):
        a = np.array([self.pos[p[0]] for p in pp])
        b = np.array([self.pos[p[-1]] for p in pp])
        w = self.C[:, a] * self.C[:, b]
        same = a == b
        w[:, same] = self.C[:, a[same]]
        return w


def eer_thr(b, m):
    """EER (%) and threshold (flag = score >= t), unit weights, t over all scores (AD1 convention)."""
    t = np.unique(np.r_[b, m])
    fpr = np.array([(b >= x).mean() for x in t])
    fnr = np.array([(m < x).mean() for x in t])
    i = int(np.argmin(np.abs(fpr - fnr)))
    return 100 * (fpr[i] + fnr[i]) / 2, float(t[i])


def eer_fast(b, m):
    """same as eer_thr, vectorised (identical result)."""
    t = np.unique(np.r_[b, m])
    bs, ms = np.sort(b), np.sort(m)
    fpr = 1 - np.searchsorted(bs, t, "left") / len(b)
    fnr = np.searchsorted(ms, t, "left") / len(m)
    i = int(np.argmin(np.abs(fpr - fnr)))
    return 100 * (fpr[i] + fnr[i]) / 2, float(t[i])


def thr_at(s, alpha, W=None):
    """smallest value t among the pool's scores with weighted share(score > t) <= alpha. Unit weights if W is None
    (returns float), else one threshold per replicate row of W (returns array B)."""
    s = np.asarray(s, float)
    o = np.argsort(s, kind="stable")
    ss = s[o]
    u = np.unique(ss)
    ends = np.searchsorted(ss, u, "right") - 1          # last sorted position of each unique value
    if W is None:
        Ws = np.ones((1, len(s)))
    else:
        Ws = W[:, o]
    cw = np.cumsum(Ws, 1)
    tot = cw[:, -1:]
    above = tot - cw[:, ends]                           # weight strictly above u_j
    ok = above <= alpha * tot + 1e-12
    j = np.argmax(ok, 1)                                # first (smallest) u_j that satisfies
    t = u[j]
    return float(t[0]) if W is None else t


def flag_rate(s, t, W=None):
    """share with score > t; t scalar or per-replicate array."""
    s = np.asarray(s, float)
    if W is None:
        return float((s > t).mean())
    t = np.asarray(t, float)
    F = s[None, :] > (t[:, None] if t.ndim else t)
    return (W * F).sum(1) / np.maximum(W.sum(1), 1e-12)


def ci(rep):
    rep = np.asarray(rep, float)
    rep = rep[np.isfinite(rep)]
    if not len(rep):
        return [None, None]
    return [float(np.percentile(rep, 2.5)), float(np.percentile(rep, 97.5))]


def cp(k, n):
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    return [float(lo), float(hi)]


def wranks(x, W):
    """weighted midranks of x under replicate weights W (B x n): rank_i = weight strictly below + half its tie group."""
    x = np.asarray(x, float)
    o = np.argsort(x, kind="stable")
    xs = x[o]
    u, inv = np.unique(xs, return_inverse=True)
    Ws = W[:, o]
    cw = np.concatenate([np.zeros((W.shape[0], 1)), np.cumsum(Ws, 1)], 1)
    starts = np.searchsorted(xs, u, "left")
    ends = np.searchsorted(xs, u, "right")
    mid = (cw[:, starts] + cw[:, ends]) / 2              # B x U
    R = np.empty_like(Ws)
    R[:, o] = mid[:, inv]
    return R


def wspearman(x, y, W):
    rx, ry = wranks(x, W), wranks(y, W)
    sw = W.sum(1, keepdims=True)
    mx, my = (W * rx).sum(1, keepdims=True) / sw, (W * ry).sum(1, keepdims=True) / sw
    cov = (W * (rx - mx) * (ry - my)).sum(1)
    vx, vy = (W * (rx - mx) ** 2).sum(1), (W * (ry - my) ** 2).sum(1)
    return cov / np.sqrt(np.maximum(vx * vy, 1e-300))


def fmt(x, nd=3):
    return "" if x is None or (isinstance(x, float) and not np.isfinite(x)) else f"{x:.{nd}f}"


class RankCache:
    """weighted midranks of y under W, precomputed once; spearman(x) then needs one wranks call."""

    def __init__(self, y, W):
        self.W = W.astype(np.float32)
        self.ry = wranks(y, self.W)
        self.sw = self.W.sum(1, keepdims=True)
        self.my = (self.W * self.ry).sum(1, keepdims=True) / self.sw
        self.dy = self.ry - self.my
        self.vy = (self.W * self.dy ** 2).sum(1)

    def spearman(self, x):
        rx = wranks(x, self.W)
        mx = (self.W * rx).sum(1, keepdims=True) / self.sw
        dx = rx - mx
        cov = (self.W * dx * self.dy).sum(1)
        vx = (self.W * dx ** 2).sum(1)
        return (cov / np.sqrt(np.maximum(vx * self.vy, 1e-30))).astype(np.float64)
