"""Value specifications and their evaluation for the rewritten supplement (supplement v2).

Every number printed by make_tables.py / make_figures.py is produced from a *spec*: a small JSON-serialisable list that
names its source (score file, read record, training list) and the computation. The generator evaluates specs with
this module (release metrics: evaluation/metrics.py of the release repository); verify_supplement_v2.py re-evaluates
the same specs with an independent implementation and compares at the printed rounding.

Spec kinds (all EER/rates in %, AUC as a fraction):
  ["t1eer", method, seed, fam, form]                  MAD22 EER from the Table-1 score file; form S (raw genuine) / H
  ["supeer", method, seed, variant, pos, neg]          EER from the supplement score file (pool names as stored)
  ["supauc", method, seed, variant, pos, neg]          AUC (ties half)
  ["suprate", "apcer"|"bpcer", method, seed, variant, pos, neg]   own rule (logit > 0 flags)
  ["supcount", method, seed, variant, pool]            number of rows
  ["t1count", method, seed, pool]
  ["mfeer", method, seed, st, fam, form]               morph-free experiment convention (flip-averaged score,
                                                       threshold EER, see morph_free/reproduce_morph_free.py)
  ["json", path, [keys...], scale]                     value inside a read record
  ["tt1flag", net, family]                             own-rule genuine flag share (%) on the primary pool
  ["medsflag", net]                                    own-rule flag share (%) on the primary mugshot pool
  ["manifest", path, "unique"|"rows"|"pos"]            training-list statistics
  ["lines", path]                                      number of lines of a text file
  ["ref", key...]                                      a value printed by the release reproducer reference
  ["mean"|"sd"|"min"|"max", [spec, ...]]  ["sub", a, b]  ["mul", a, k]
"""
import csv, functools, json, os, sys, tarfile, tempfile
import numpy as np

REL = "/home/narolski/work/dont-cut-corners"
SN = "/home/narolski/smad-next"
T7 = "/mnt/t7/smad_next"
EXP = os.path.join(SN, "experiments")
sys.path.insert(0, os.path.join(REL, "evaluation"))
from metrics import eer, auc  # noqa: E402  (release metrics, verified by the release reproducers)

FAMS = ["FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"]
FRL = ["amsl", "facemorpher", "opencv", "stylegan", "webmorph"]
TT1_TAR = os.path.join(T7, "TT1/results/TT1_A100_pn1fs_fs.tar")
MEDS_TAR = os.path.join(T7, "TT1/results/TT1M_se1d.tar")
TT1_MANIFEST = os.path.join(T7, "TT1/tt1_score.csv")
MEDS_MANIFEST = os.path.join(EXP, "TT1_threshold-transfer-unseen-genuine/meds_score.csv")
TT1_FAMS = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw_calfw", "cfp_ff", "agedb_30"]


@functools.lru_cache(None)
def t1():
    z = np.load(os.path.join(REL, "results/table1/scores_table1.npz"))
    return z["method"], z["seed"].astype(int), z["pool"], z["logit"].astype(np.float64)


@functools.lru_cache(None)
def sup():
    z = np.load(os.path.join(REL, "results/supplement/scores_supplement.npz"))
    return (z["method_names"][z["method"]], z["seed"].astype(int), z["variant_names"][z["variant"]],
            z["pool_names"][z["pool"]], z["logit"].astype(np.float64))


@functools.lru_cache(None)
def mf():
    z = np.load(os.path.join(REL, "results/morph_free/scores_morph_free.npz"))
    return z["method_names"][z["method"]], z["seed"].astype(int), z["pool_names"][z["pool"]], z["score"].astype(np.float64)


@functools.lru_cache(None)
def jload(path):
    return json.load(open(path))


@functools.lru_cache(None)
def tar_scores(tar, suffix):
    out = {}
    with tarfile.open(tar) as tf:
        for m in tf.getmembers():
            if m.name.endswith(suffix):
                z = np.load(tf.extractfile(m))
                out[os.path.basename(m.name)[: -len(suffix)]] = dict(zip(z["id"].tolist(), z["logit"].astype(np.float64)))
    return out


@functools.lru_cache(None)
def tt1_ids():
    fam = {f: [] for f in TT1_FAMS}
    for r in csv.DictReader(open(TT1_MANIFEST)):
        if r["role"] == "tt1" and not r["rung"].startswith("R_") and r["strength"] == "primary" and r["cell"] in fam:
            fam[r["cell"]].append(r["id"])
    return fam


@functools.lru_cache(None)
def meds_ids():
    return [r["id"] for r in csv.DictReader(open(MEDS_MANIFEST)) if r["cell"] == "primary"]


@functools.lru_cache(None)
def manifest(path):
    rows = list(csv.DictReader(open(path)))
    return dict(unique=len({r["path"] for r in rows}), rows=len(rows), pos=sum(int(r["label"]) for r in rows))


@functools.lru_cache(None)
def release_ref():
    from supplement_reference import REF
    return REF


def _eer_pct(pos, neg):
    return 100 * eer(np.r_[pos, neg], np.r_[np.ones(len(pos)), np.zeros(len(neg))].astype(int))


def morph_eer(bona, morph):
    b, m = np.sort(bona), np.sort(morph)
    t = np.concatenate([b, m])
    fpr = 1 - np.searchsorted(b, t, side="left") / len(b)
    fnr = np.searchsorted(m, t, side="left") / len(m)
    i = int(np.argmin(np.abs(fnr - fpr)))
    return float((fnr[i] + fpr[i]) / 2)


def _sup_sel(method, seed, variant, pool):
    M, S, V, P, L = sup()
    return L[(M == method) & (S == seed) & (V == variant) & (P == pool)]


def ev(spec):
    k = spec[0]
    if k == "t1eer":
        _, m, s, f, form = spec
        M, S, P, L = t1()
        sel = (M == m) & (S == s)
        neg = "genuine_raw" if form == "S" else "genuine_history_" + f
        return _eer_pct(L[sel & (P == "morph_" + f)], L[sel & (P == neg)])
    if k == "t1count":
        _, m, s, p = spec
        M, S, P, L = t1()
        return float(((M == m) & (S == s) & (P == p)).sum())
    if k in ("supeer", "supauc"):
        _, m, s, v, pos, neg = spec
        a, b = _sup_sel(m, s, v, pos), _sup_sel(m, s, v, neg)
        if k == "supeer":
            return _eer_pct(a, b)
        return auc(np.r_[a, b], np.r_[np.ones(len(a)), np.zeros(len(b))].astype(int))
    if k == "suprate":
        _, which, m, s, v, pos, neg = spec
        if which == "apcer":
            return 100 * float(np.mean(_sup_sel(m, s, v, pos) <= 0))
        return 100 * float(np.mean(_sup_sel(m, s, v, neg) > 0))
    if k == "supcount":
        _, m, s, v, p = spec
        return float(len(_sup_sel(m, s, v, p)))
    if k == "mfeer":
        _, m, s, st, fam, form = spec
        M, S, P, X = mf()
        sel = (M == m) & (S == s)
        neg = f"{st}:genuine_raw" if form == "native" else f"{st}:{fam}:genuine_history"
        return 100 * morph_eer(X[sel & (P == neg)], X[sel & (P == f"{st}:{fam}:morph")])
    if k == "json":
        _, path, keys, scale = spec
        o = jload(path)
        for key in keys:
            o = o[key]
        return float(o) * scale
    if k == "tt1flag":
        _, net, fam = spec
        L = tar_scores(TT1_TAR, "__tt1.npz")[net]
        return 100 * float(np.mean([L[i] > 0 for i in tt1_ids()[fam]]))
    if k == "medsflag":
        L = tar_scores(MEDS_TAR, "__meds.npz")[spec[1]]
        return 100 * float(np.mean([L[i] > 0 for i in meds_ids()]))
    if k == "manifest":
        return float(manifest(spec[1])[spec[2]])
    if k == "lines":
        return float(sum(1 for _ in open(spec[1])))
    if k == "ref":
        return float(release_ref()[tuple(spec[1:])][0])
    if k in ("mean", "sd", "min", "max", "sum"):
        v = [ev(x) for x in spec[1]]
        return float({"mean": np.mean, "sd": lambda a: np.std(a, ddof=1), "min": np.min, "max": np.max,
                      "sum": np.sum}[k](v))
    if k == "tt1n":
        return float(len(tt1_ids()[spec[1]]))
    if k == "medsn":
        return float(sum(1 for r in csv.DictReader(open(MEDS_MANIFEST)) if r["cell"] == spec[1]))
    if k == "sub":
        return ev(spec[1]) - ev(spec[2])
    if k == "mul":
        return ev(spec[1]) * spec[2]
    raise ValueError(spec)


# --------------------------------------------------------------------------------------------------------------------
# registry of printed values
class Registry:
    def __init__(self):
        self.items = []

    def v(self, table, spec, digits, sign=False, kind=None, pct_of=None):
        """evaluate spec, register it, return the printed string (no LaTeX math)."""
        x = ev(spec)
        s = f"{x:+.{digits}f}" if sign else f"{x:.{digits}f}"
        if s in ("-0." + "0" * digits, "+0." + "0" * digits) and not sign:
            s = s.lstrip("-")
        self.items.append(dict(table=table, spec=spec, value=x, digits=digits, printed=s, kind=kind or src_kind(spec)))
        return s

    def dump(self, path):
        json.dump(self.items, open(path, "w"), indent=0)


def src_kind(spec):
    k = spec[0]
    if k in ("mean", "sd", "min", "max", "sum"):
        kinds = {src_kind(x) for x in spec[1]}
        return "record" if "record" in kinds else ("reference" if "reference" in kinds else "score")
    if k in ("sub", "mul"):
        return src_kind(spec[1])
    if k == "json":
        return "record"
    if k == "ref":
        return "reference"
    if k in ("manifest", "lines"):
        return "list"
    return "score"


def tex_minus(s):
    """typographic minus for LaTeX text mode."""
    return s.replace("-", "$-$") if s.startswith("-") or "-" in s else s
