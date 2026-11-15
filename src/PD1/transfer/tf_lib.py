"""Signal isolation by paired differences (PD1), cross-family transfer: data tables, bootstrap, AUC, paired heads.

wauc and the pigeonhole person draw are copied from src/PD1/diffae/pd1_common.py (themselves verbatim from
src/FZ1/fz1_common.py and src/AD1/ad1_read.py, the a41_read.py two-way person bootstrap).

Families (primary pools of the family analyses):
  L landmark ladder (AR1), OpenCV-style engine, 536 FRGC/colorFERET hosts: x0, x1 (warp-only), xm, x2, x3
  D diffusion autoencoder (DiffAE, 20 steps), 516 hosts / 258 persons: x0, x1 (reconstruction), x2, x3
  G GAN (StyleGAN3-T, GAN32 set G), 256 hosts / 128 persons: x0, x1 (reconstruction), x2, x3
Persons are real FERET / FRGC subject ids ('feret:00268', 'frgc:04934').
"""
import csv
import hashlib
import math
import pathlib

import numpy as np

OUT = pathlib.Path("/mnt/t7/smad_next/PD1/transfer")
RES = pathlib.Path("/home/narolski/smad-next/experiments/PD1_signal-isolation-paired-differences/transfer")
GAN = pathlib.Path("/mnt/t7/smad_next/PD1/gan")
DIF = pathlib.Path("/mnt/t7/smad_next/PD1/diffae")
LAN = pathlib.Path("/mnt/t7/smad_next/PD1/landmark")
SEED = 20261111
CS = (1e-3, 1e-2, 1e-1, 1.0, 10.0)
FEATS = (("clip", "pool"), ("clip", "patch"), ("dinov3", "pool"))
FNAME = {("clip", "pool"): "CLIP ViT-L/14 pooled", ("clip", "patch"): "CLIP ViT-L/14 mean patch token",
         ("dinov3", "pool"): "DINOv3 ViT-L/16 pooled"}
FKEY = {("clip", "pool"): "clip_pool", ("clip", "patch"): "clip_patch", ("dinov3", "pool"): "dino_pool"}
FAMS = ("L", "D", "G")
FAMNAME = {"L": "landmark", "D": "diffusion", "G": "GAN"}
MY_SETS = ("Lad", "Lbench", "Lsoft", "Lblank", "Lx1g", "Dtr", "Dev", "Df256")
GAN_SETS = ("G", "Hr", "S", "Fm")


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def rows(p):
    return list(csv.DictReader(open(p)))


def hsh(s):
    return hashlib.sha256(s.encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ features
def load_features(bb, kind, limit_tag=""):
    """id -> L2-normalised float64 vector, from this experiment's extraction (landmark and diffusion images) and the
    GAN family's caches (G, Hr, S, Fm; same code, checked)."""
    F = {}
    for s in MY_SETS:
        p = OUT / "feats" / bb / f"{s}{limit_tag}.npz"
        if not p.exists():
            continue
        z = np.load(p, allow_pickle=False)
        X = z[kind].astype(np.float64)
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        F.update(zip(z["id"].tolist(), X))
    for s in GAN_SETS:
        z = np.load(GAN / "feats" / bb / f"{s}.npz", allow_pickle=False)
        X = z[kind].astype(np.float64)
        X /= np.linalg.norm(X, axis=1, keepdims=True)
        F.update(zip(z["id"].tolist(), X))
    return F


# ------------------------------------------------------------------------------------------------ host tables
def landmark_hosts():
    my = [r for r in rows(OUT / "lists/landmark_items.csv") if r["set"] == "Lad"]
    by = {}
    for r in my:
        by.setdefault(r["p1"], {})[r["rung"]] = r
    hosts = []
    for h in sorted(by):
        d = by[h]
        assert set(d) == {"x0", "x1", "xm", "x2", "x3"}, (h, d.keys())
        assert d["x2"]["p2"] == h and d["xm"]["p2"] == h and d["x3"]["p2"] != h
        hosts.append(dict(fam="L", host=h, person=h, partner=d["x3"]["p2"], cluster=h,
                          **{k: d[k]["id"] for k in ("x0", "x1", "xm", "x2", "x3")}))
    return hosts


def diffusion_hosts():
    tr = [r for r in rows(DIF / "lists/items.csv") if r["set"] == "tr"]
    by = {}
    for r in tr:
        for h in r["host"].split(";"):
            by.setdefault(h, {})[r["rung"]] = r
    hosts = []
    for h in sorted(by):
        d = by[h]
        assert set(d) == {"x0", "x1", "x2", "x3"}, (h, d.keys())
        A = d["x0"]["persons"]
        pp = d["x3"]["persons"].split(";")
        assert A in pp and d["x2"]["persons"] == A
        partner = pp[1] if pp[0] == A else pp[0]
        hosts.append(dict(fam="D", host=h, person=A, partner=partner, cluster=d["x0"]["block"],
                          **{k: d[k]["id"] for k in ("x0", "x1", "x2", "x3")}))
    return hosts


def gan_hosts():
    it = {r["id"]: r for r in rows(GAN / "items.csv")}
    hh = [h for h in rows(GAN / "hosts.csv") if h["set"] == "G"]
    real = {}
    for h in hh:
        x0 = it[h["x0"]]
        real[h["own_tmpl"]] = f"{x0['db']}:{x0['subject']}"
    hosts = []
    for h in hh:
        hosts.append(dict(fam="G", host=h["host"], person=real[h["own_tmpl"]], partner=real[h["partner_lat"]],
                          cluster=h["cluster"], **{k: h[k] for k in ("x0", "x1", "x2", "x3")}))
    for h in hosts:
        assert h["person"] != h["partner"]
    return hosts


def all_hosts():
    return {"L": landmark_hosts(), "D": diffusion_hosts(), "G": gan_hosts()}


def step_persons(h, step):
    """persons involved in a step's two images of host h."""
    return (h["person"], h["partner"]) if step in ("W", "I", "G0") else (h["person"],)


# ------------------------------------------------------------------------------------------------ reference sets
def refs():
    """Reference image sets (ids and clusters)."""
    R = {}
    git = rows(GAN / "items.csv")
    S = [r for r in git if r["set"] == "S"]
    for part in ("S_fit", "S_test"):
        s0 = {r["cluster"]: r["id"] for r in S if r["part"] == part and r["role"] == "s0"}
        s1 = {r["cluster"]: r["id"] for r in S if r["part"] == part and r["role"] == "s1"}
        ks = sorted(set(s0) & set(s1))
        R[f"smdd_{part}"] = dict(a=[s0[k] for k in ks], b=[s1[k] for k in ks], cl=ks)
    hh = [h for h in rows(GAN / "hosts.csv") if h["set"] == "Hr"]
    R["H"] = dict(x1=[h["x1"] for h in hh], x1s=[h["x1s"] for h in hh], x3=[h["x3"] for h in hh],
                  cl=[h["cluster"] for h in hh])
    Fm = [r for r in git if r["set"] == "Fm"]
    R["G_flag"] = dict(native=[r["id"] for r in Fm if r["role"] == "native"],
                       soft=[r["id"] for r in Fm if r["role"] == "e7_FaceMorpher"], name="corrected MAD22 E7 FaceMorpher history")
    my = rows(OUT / "lists/landmark_items.csv")
    lb = [r for r in my if r["set"] == "Lbench"]
    R["L_flag_i"] = dict(native=[r["id"] for r in lb if r["pool"] == "frllm_frll_bona"],
                         soft=[r["id"] for r in lb if r["pool"] == "frllm_opencv"], name="(i) FRLL E7 OpenCV")
    R["L_flag_ii"] = dict(native=[r["id"] for r in lb if r["pool"] == "mad22_BonaFide"],
                          soft=[r["id"] for r in lb if r["pool"] == "mad22_OpenCV"], name="(ii) corrected MAD22 E7 OpenCV")
    ls = [r for r in my if r["set"] == "Lsoft"]
    R["L_soft_hosts"] = dict(ids=[r["id"] for r in ls], person=[r["p1"] for r in ls], rung=[r["rung"] for r in ls])
    bl = [r for r in my if r["set"] == "Lblank"]
    R["L_blank"] = {(r["var"], r["rung"], r["p1"]): r["id"] for r in bl}
    R["L_x1g"] = {r["p1"]: r["id"] for r in my if r["set"] == "Lx1g"}
    dit = rows(DIF / "lists/items.csv")
    R["D_flag"] = dict(native=[r["id"] for r in dit if r["set"] == "ev" and r["arm"] == "mordiff_bona|orig"],
                       soft=[r["id"] for r in dit if r["set"] == "ev" and r["arm"] == "mordiff|resmatch"],
                       name="FRLL E7 (MorDIFF history)")
    f = [r for r in dit if r["set"] == "f256"]
    R["D_f256"] = {a: {r["host"] if a != "B20" else r["id"]: r["id"] for r in f if r["arm"] == a}
                   for a in ("D20", "rec100", "B20")}
    assert len(R["D_f256"]["D20"]) == 204 and len(R["D_f256"]["rec100"]) == 204 and len(R["D_f256"]["B20"]) == 200
    R["D_f256_rows"] = {r["id"]: r for r in f if r["arm"] in ("D20", "rec100", "B20")}
    return R


# ------------------------------------------------------------------------------------------------ AUC and bootstrap
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
    """pigeonhole person draw: persons ~ Multinomial(n, 1/n); a one-person image weighs its person's count, a
    two-person image the product of its two persons' counts."""

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


def ci(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def clopper(k, n):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return [lo, hi]


def flag(untouched, softened):
    """threshold = k-th highest untouched score, k = ceil(0.05 n); share of softened at or above it."""
    u = np.sort(np.asarray(untouched, float))[::-1]
    k = int(math.ceil(0.05 * len(u)))
    t = u[k - 1]
    s = np.asarray(softened, float)
    n1 = int((s >= t).sum())
    return dict(threshold=float(t), k_untouched=k, n_untouched=len(u), flag_untouched=float((u >= t).mean()),
                n_soft=len(s), flagged=n1, rate=n1 / len(s), ci=clopper(n1, len(s)))


# ------------------------------------------------------------------------------------------------ scalers and heads
def balanced_scaler(groups):
    """groups: list of (n_i, D) arrays, one per family; equal weight per family."""
    mus = [g.mean(0) for g in groups]
    vs = [g.var(0) for g in groups]
    mu = np.mean(mus, 0)
    var = np.mean([v + (m - mu) ** 2 for m, v in zip(mus, vs)], 0)
    return mu, np.sqrt(var) + 1e-8


def fit_pair_lr(D, w, C):
    """linear head, no intercept, logistic loss on differences D (both signs), sample weights w."""
    from sklearn.linear_model import LogisticRegression
    X = np.vstack([D, -D])
    y = np.r_[np.ones(len(D)), np.zeros(len(D))]
    m = LogisticRegression(C=C, fit_intercept=False, max_iter=5000, tol=1e-6)
    m.fit(X, y, sample_weight=np.r_[w, w])
    return m.coef_[0].copy()


class Head:
    def __init__(self, mu, sd, w, C, info=None):
        self.mu, self.sd, self.w, self.C, self.info = mu, sd, w, C, info or {}

    def score(self, X):
        return ((np.asarray(X, float) - self.mu) / self.sd) @ self.w


def family_pairs(F, hosts, pos_rungs):
    """(P, N) arrays of positives and x1 negatives of the same host, with the host index of each pair."""
    P, N, hi = [], [], []
    for k, h in enumerate(hosts):
        for r in pos_rungs:
            if r in h:
                P.append(F[h[r]])
                N.append(F[h["x1"]])
                hi.append(k)
    return np.array(P), np.array(N), np.array(hi)


def fit_multi(F, fam_hosts, pos_of, C, weighted=True):
    """fam_hosts: {fam: hosts}; pos_of: {fam: positive rungs}. Scaler over the training images (positives and
    negatives) with equal family weight; sample weights give equal total weight per family (mean weight 1)."""
    Ps, Ns, imgs = [], [], []
    for f, hs in fam_hosts.items():
        P, N, _ = family_pairs(F, hs, pos_of[f])
        Ps.append(P)
        Ns.append(N)
        ids = sorted({h[r] for h in hs for r in list(pos_of[f]) + ["x1"] if r in h})
        imgs.append(np.array([F[i] for i in ids]))
    mu, sd = balanced_scaler(imgs) if weighted else (np.vstack(imgs).mean(0), np.vstack(imgs).std(0) + 1e-8)
    D = np.vstack([(P - N) / sd for P, N in zip(Ps, Ns)])
    ntot = sum(len(P) for P in Ps)
    if weighted:
        wts = np.concatenate([np.full(len(P), ntot / (len(Ps) * len(P))) for P in Ps])
    else:
        wts = np.ones(ntot)
    w = fit_pair_lr(D, wts, C)
    u = np.zeros(D.shape[1])
    for P, N in zip(Ps, Ns):
        u += ((P - N) / sd).mean(0) / len(Ps)
    u /= np.linalg.norm(u)
    return Head(mu, sd, w, C, dict(n_pairs={f: int(len(P)) for f, P in zip(fam_hosts, Ps)})), Head(mu, sd, u, None)


def paired_share_hosts(head, F, hosts, pos):
    s1 = head.score(np.array([F[h["x1"]] for h in hosts]))
    sp = head.score(np.array([F[h[pos]] for h in hosts]))
    return float(np.mean((sp > s1) + 0.5 * (sp == s1)))
