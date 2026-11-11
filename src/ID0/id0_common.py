"""ID0 shared paths and helpers (identity-shrinkage triage). Reuses AR1 code unchanged by import."""
import csv
import hashlib
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path("/home/narolski/smad-next")
AR1_SRC = ROOT / "src/AR1"
AR1_POOL = ROOT / "experiments/AR1/pool.csv"
AR1_OUT = pathlib.Path("/mnt/t7/smad_next/AR1")
OUT = pathlib.Path("/mnt/t7/smad_next/ID0")
RES = ROOT / "experiments/ID0_identity-shrinkage-triage"
MC = pathlib.Path("/home/narolski/mambamorph-code")
EVAL_CSV = MC / "smadcvpr_data/manifests/eval.csv"
A43 = pathlib.Path("/mnt/t7/smad_heldout/a43")
A41X3 = pathlib.Path("/mnt/t7/smad_heldout/a41_diffae/data/a41diffae")
A46_FEAT = pathlib.Path("/mnt/t7/smad_heldout/a46/feat/a46_feat.npz")
H3_MAN = pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv")
H3_DATA = pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/data")
H3_INPUTS = pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/work/h3_inputs.npz")
A37_MAN = pathlib.Path("/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/a37spread.csv")
A37_DATA = pathlib.Path("/mnt/t7/smad_heldout/a37_sg3ctl/data")
MAD22_RAW = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
FRLLM_RAW = pathlib.Path("/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london")
PY_SPARK = "/home/narolski/mambamorph-code/.venv-spark/bin/python"
E7_PRIMARY = (("frllm", "opencv"), ("frllm", "facemorpher"), ("frllm", "stylegan"), ("mordiff", "mordiff"))
E7_DESC = (("dim", "dim_c"), ("dim", "greedy_dim"), ("dim", "greedy_dim_s"), ("frllm", "amsl"), ("frllm", "webmorph"))


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def is_val(subject):
    """prep_train.is_val, the existing val10 rule (copied expression; key verified against train.csv)."""
    return int(hashlib.sha1(f"smadcvpr:{subject}".encode()).hexdigest(), 16) % 10 == 0


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ar1_pool_module():
    if str(AR1_SRC) not in sys.path:
        sys.path.insert(0, str(AR1_SRC))
    spec = importlib.util.spec_from_file_location("ar1pool", AR1_SRC / "pool.py")
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    return P


def read_tem(path):
    import numpy as np
    lines = open(path).read().splitlines()
    n = int(lines[0].strip())
    return np.array([list(map(float, lines[i].split()[:2])) for i in range(1, n + 1)], np.float64)


def rows(path):
    return list(csv.DictReader(open(path)))


def tier(key, arm):
    """processing priority (1 first). Tier 1 = everything the fixed reads need; 2 = second tool and controls of the
    primary pool; 3 = descriptive sets. DiffAE-native frames only for the DiffAE arm (else 9 = skipped)."""
    t = key.split("|")
    if t[0] == "dae":
        if arm != "diffae":
            return 9
        return 1 if t[1] in ("a256", "D20", "C20", "B20") else 2
    if t[0] in ("fit", "sg3", "ar1g"):
        return 1
    if t[0] == "ar1src" and t[1] == "frgcferet":
        return 1 if t[3] in ("H", "S") else 2
    if t[0] == "ar1" and t[1] == "frgcferet":
        if t[3] in ("R2w", "R3", "R3m", "R4"):
            return 1 if t[2] == "opencv" else 2
        return 2
    if t[0] == "a43":
        return 1 if t[1] in ("E", "D20", "C20", "B20", "A") else 2
    if t[0] == "e7":
        return 1 if t[1] in ("native", "opencv", "facemorpher", "stylegan", "mordiff") else 3
    return 3


def glint_rank(key):
    """finer order for the CPU-bound glint detector: fit, A43 tier-1 sets, AR1 OpenCV R2w/R3m, StyleGAN3, primary E7,
    graded set, then the remaining tiers."""
    t = key.split("|")
    if t[0] == "fit":
        return 0
    if t[0] == "a43" and t[1] in ("E", "D20", "C20", "B20", "A"):
        return 1
    if t[0] == "ar1" and t[1] == "frgcferet" and t[2] == "opencv" and t[3] in ("R2w", "R3m"):
        return 2
    if t[0] == "sg3":
        return 3
    if t[0] == "e7" and t[1] in ("opencv", "facemorpher", "stylegan"):
        return 4
    if t[0] == "ar1g":
        return 5
    return 5 + tier(key, "spark")


def ordered(items, arm, max_tier=3):
    """items [(key, path)] -> sorted by tier (stable), tiers above max_tier dropped."""
    ts = [(tier(k, arm), i) for i, (k, _) in enumerate(items)]
    return [items[i] for t, i in sorted(ts) if t <= max_tier]


def existing_glint():
    """item key -> existing glintr100 embedding (unit) from the same registered route (prep_eval.kps -> norm_crop ->
    a2f_common 'glint'): AR1 pool_src_emb / frll_src_emb / fr_emb_built (matched by path) and a46_feat (native and
    diffusion E7 frames, matched by photo). Only found faces are used."""
    import numpy as np
    it = rows(OUT / "items.csv")
    bypath = {}
    for f in ("pool_src_emb.npz", "fr_emb_built.npz"):
        z = np.load(AR1_OUT / f)
        for p, e, ok in zip(z["path"], z["emb"], z["found"]):
            if ok:
                bypath[str(p)] = e
    z = np.load(AR1_OUT / "frll_src_emb.npz")
    for s, e, ok in zip(z["stem"], z["emb"], z["found"]):
        if ok:
            bypath[str(AR1_OUT / "frll_src" / f"{s}.png")] = e
    z = np.load(A46_FEAT)
    a46 = {}
    for k, e, ok in zip(z["keys"], z["emb"], z["found"]):
        g, n = str(k).split("|", 1)
        if ok and (g == "native" or g.startswith("e7_")):
            a46[f"e7|{'native' if g == 'native' else g[3:]}|{n}"] = e
    out = {}
    for r in it:
        e = bypath.get(r["path"])
        if e is None:
            e = a46.get(r["key"])
        if e is not None:
            out[r["key"]] = e / np.linalg.norm(e)
    return out
