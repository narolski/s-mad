"""FZ1 shared helpers: manifests, groups, persons, the AD1 / AG5 bootstraps, weighted AUC / EER.

wauc and Draw are copied verbatim from src/AD1/ad1_read.py (the a41_read.py pigeonhole person bootstrap), so A43
intervals use exactly AD1's draw (seed [20261107, 43, 1], persons = every person of the A43 manifest).
"""
import csv, hashlib, pathlib, re
import numpy as np

MC = pathlib.Path("/home/narolski/mambamorph-code")
EVAL_ROOT = MC / "smadcvpr_data"
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
A43_ROOT = A43 / "data"
MAN = A43 / "data/manifests/a43.csv"
MAN_SHA = "ce3a264adb30928d6ae3abfb63619ed4b35fcb0ebb7fcca7e5001b212a5df4b8"
EVAL = MC / "smadcvpr_data/manifests/eval.csv"
EVAL_SHA = "86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9"
H3 = pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/data")
H3_MAN = H3 / "manifests/h3sg3.csv"
A37 = pathlib.Path("/mnt/t7/smad_heldout/a37_sg3ctl/data")
A37_MAN = A37 / "manifests/a37spread.csv"
TRAIN = MC / "smadcvpr_data/manifests/train.csv"
OUT = pathlib.Path("/home/narolski/smad-next/experiments/FZ1")
BIG = pathlib.Path("/mnt/t7/smad_next/FZ1")
SEED_A43 = [20261107, 43, 1]
SEED_SG3 = [20261111, 5, 1]
LANDMARK = ("amsl", "facemorpher", "opencv", "webmorph")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


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


RXB = re.compile(r"^(\d{3})_(\d{2})_")
RXM = re.compile(r"^morph_(\d{3})_\d{2}_and_(\d{3})_\d{2}")
RXF = re.compile(r"^(\d{3})_(\d{3})_")


def pers_eval(r):
    n = pathlib.PurePath(r["path"]).name
    if r["label"] == "0":
        return (RXB.match(n).group(1),)
    m = RXM.match(n) or RXF.match(n)
    return (m.group(1), m.group(2))


def pers_a43(r):
    if r["source"] == "eval":
        return pers_eval(r)
    if r["src_b"]:
        return (r["src_a"][:3], r["src_b"][:3])
    return (r["src_a"][:3],)


def a43_rows():
    assert sha(MAN) == MAN_SHA
    return list(csv.DictReader(open(MAN)))


def a43_groups(rows):
    g = {}
    for i, r in enumerate(rows):
        k = r["arm"] if r["source"] == "a43" else {"mordiff_bona": "R0", "mordiff": "A_reg"}.get(r["family"], "frll_bona_a43")
        g.setdefault(k, []).append(i)
    return g


def a43_path(r):
    """Absolute path of the 512 frame a release scored for this A43 manifest row."""
    return (A43_ROOT if r["source"] == "a43" else EVAL_ROOT) / r["path"]


def eval_rows():
    assert sha(EVAL) == EVAL_SHA
    return list(csv.DictReader(open(EVAL)))


def eval_cells(ev):
    """{cell name: (morph rows, native genuine rows, E7 genuine rows)} for the landmark FRLL-Morphs families and MorDIFF,
    plus 'frll_bona' (FRLL-Morphs genuine) and 'R1' (MorDIFF E7). Never the old MAD22 rows."""
    sel = lambda s, f, v: [r for r in ev if r["set"] == s and r["family"] == f and r["variant"] == v]  # noqa: E731
    cells = {}
    fb = sel("frllm", "frll_bona", "orig")
    for f in LANDMARK:
        cells[f"FRLLM/{f}"] = (sel("frllm", f, "orig"), fb, sel("frllm", f, "resmatch"))
    cells["MorDIFF"] = (sel("mordiff", "mordiff", "orig"), sel("mordiff", "mordiff_bona", "orig"), sel("mordiff", "mordiff", "resmatch"))
    return cells


def sg3_rows():
    hr = list(csv.DictReader(open(H3_MAN)))
    sr = list(csv.DictReader(open(A37_MAN)))
    R4 = [r for r in hr if r["family"] == "h3_sg3" and r["variant"] == "orig"]
    R2 = [r for r in hr if r["family"] == "h3_bona" and r["variant"] == "orig"]
    RX = [r for r in sr if r["variant"] == "orig"]
    return R4, R2, RX


def eer_thr(b, m):
    """EER (%) and threshold (flag = score >= t), unit weights, t over all scores (AD1's eer_thr)."""
    t = np.unique(np.r_[b, m])
    fpr = np.array([(b >= x).mean() for x in t])
    fnr = np.array([(m < x).mean() for x in t])
    i = int(np.argmin(np.abs(fpr - fnr)))
    return 100 * (fpr[i] + fnr[i]) / 2, float(t[i])


def weer(pos, neg, wp, wn):
    """Weighted EER (%) per bootstrap row; flag = score >= t, t over the unique scores (same rule as eer_thr)."""
    s = np.r_[neg, pos]
    ispos = np.r_[np.zeros(len(neg), bool), np.ones(len(pos), bool)]
    o = np.argsort(s, kind="stable")
    ss, ip = s[o], ispos[o]
    W = np.concatenate([wn, wp], 1)[:, o]
    WN = np.where(ip[None, :], 0.0, W)
    WP = np.where(ip[None, :], W, 0.0)
    cN = np.concatenate([np.zeros((W.shape[0], 1)), np.cumsum(WN, 1)], 1)
    cP = np.concatenate([np.zeros((W.shape[0], 1)), np.cumsum(WP, 1)], 1)
    _, first = np.unique(ss, return_index=True)
    fpr = 1 - cN[:, first] / np.maximum(cN[:, -1:], 1e-12)
    fnr = cP[:, first] / np.maximum(cP[:, -1:], 1e-12)
    i = np.argmin(np.abs(fpr - fnr), 1)
    r = np.arange(W.shape[0])
    return 100 * (fpr[r, i] + fnr[r, i]) / 2


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def neutral_above_smiling(scores_by_name, D):
    """scores_by_name: {'001_03': s, '001_08': s, ...}. Per person 1 / 0.5 / 0; mean over persons, person bootstrap
    (the person counts of draw D; persons absent from the dict get weight 0)."""
    per = sorted({k[:3] for k in scores_by_name if k[:3] + "_03" in scores_by_name and k[:3] + "_08" in scores_by_name})
    v = np.array([1.0 if scores_by_name[p + "_03"] > scores_by_name[p + "_08"] else 0.5 if scores_by_name[p + "_03"] == scores_by_name[p + "_08"] else 0.0 for p in per])
    w = D.C[:, [D.pos[p] for p in per]]
    rep = (w * v).sum(1) / np.maximum(w.sum(1), 1e-12)
    return {"value": float(v.mean()), "ci": ci(rep), "persons": len(per)}


def flag_change(s0, s1, names, t, D):
    """Paired R0 -> R1 flag rates at threshold t (flag = score >= t) on the same photos; person bootstrap of the
    difference (threshold held fixed)."""
    f0, f1 = s0 >= t, s1 >= t
    d = f1.astype(float) - f0.astype(float)
    pc = D.C[:, [D.pos[n[:3]] for n in names]]
    rep = (pc * d).sum(1) / pc.sum(1)
    return {"n": int(len(names)), "flag_R0": float(f0.mean()), "flag_R1": float(f1.mean()), "change_pts": float(100 * d.mean()),
            "change_ci_pts": [100 * x for x in ci(rep)], "newly_flagged": int((~f0 & f1).sum()), "unflagged": int((f0 & ~f1).sum()),
            "threshold": float(t)}
