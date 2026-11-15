"""SM1 shared paths and helpers (SMDD five-partner audit and rebuild of the standard training set)."""
import hashlib
import pathlib
import re

import numpy as np

SMDD = pathlib.Path("/mnt/t7/Datasety/downloads/SMDD")
BF_T = SMDD / "SMDD_release_train/os25k_bf_t"          # 25,000 genuine renders (training release)
M_T = SMDD / "SMDD_release_train/m15k_t"               # 15,000 release morphs
SRC_T = SMDD / "os25k_m_t"                             # 25,000 morph-source renders (3,858 contributors)
SRC_E = SMDD / "os25k_m_e"                             # evaluation split's morph-source renders
M_E = SMDD / "SMDD_release_evaluation/m15k_e"
EVAL_PARTNERS = ("img279570", "img226436", "img141280", "img042475", "img005071")   # Part 1, by morph count
IF106 = SMDD / "smdd_bona_landmarks_if106.npz"
LOOK = SMDD / "smdd_bona_lookalikes.npz"
OUT = pathlib.Path("/mnt/t7/smad_next/SM1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/SM1_smdd-partner-audit-and-rebuild")
MC = pathlib.Path("/home/narolski/mambamorph-code")
W46 = pathlib.Path("/home/narolski/mambamorph-code-a46")
PY = "/home/narolski/mambamorph-code/.venv-spark/bin/python"
FACENET_PY = "/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv/bin/python"
S78 = MC / "scripts/78_tool_morph.py"
S68 = MC / "scripts/68_hires_morph.py"
PAT = re.compile(r"^morphed_(img\d+)_(img\d+)\.png$")
PARTNERS = ("img054553", "img282038", "img496816", "img337488", "img099545")   # by morph count, Part 1
SEED = 20261111
SEEDS = (401, 402, 403, 404, 405)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def release_pairs():
    """[(first, second)] of the 15,000 training-release morphs, file order."""
    out = []
    for f in sorted(x.name for x in M_T.iterdir()):
        m = PAT.match(f)
        if m:
            out.append(m.groups())
    return out


def write_tem(path, pts):
    """73_delin_align.write_tem's format (as src/AR1/variants.py): N, then x<TAB>y rows, then 0."""
    with open(path, "w") as fo:
        fo.write(f"{len(pts)}\n")
        for x, y in pts:
            fo.write(f"{float(x):.4f}\t{float(y):.4f}\n")
        fo.write("0\n")


def load_if106():
    z = np.load(IF106, allow_pickle=False)
    names, lms = z["names"], z["lms"]            # read once (each z[...] access re-reads the npz member)
    return {str(n)[:-4]: lms[i] for i, n in enumerate(names)}
