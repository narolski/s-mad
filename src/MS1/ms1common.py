"""MS1 shared paths and helpers. Every image operation is imported unchanged from existing, approved code."""
import csv
import hashlib
import importlib.util
import pathlib
import sys

MC = pathlib.Path("/home/narolski/mambamorph-code")
SRC = pathlib.Path("/home/narolski/smad-next/src")
OUT = pathlib.Path("/mnt/t7/smad_next/MS1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/MS1_multi-source-training-set")
FFHQ = pathlib.Path("/mnt/t7/Datasety/downloads/FFHQ-1024")
FFHQM_DOCS = pathlib.Path("/mnt/t7/Datasety/downloads/FFHQ_Morphs/_docs/FFHQ-Morphs")
FFHQM = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs")
PE_SHA = "374408ab3a886e6df25b563bc2344d190efe2ab7b3163efbb17c9b6ca9100628"
UNCHANGED = [MC / "scripts/73_delin_align.py", MC / "scripts/78_tool_morph.py", MC / "scripts/68_hires_morph.py",
             MC / "smadcvpr/prep_eval.py", SRC / "AF0/af_morph.py", SRC / "AF0/soften.py", SRC / "AF0/ghost.py",
             SRC / "AR1/variants.py", SRC / "AR1/splice.py", SRC / "AR1/fr.py", SRC / "AR1/ar1_common.py",
             SRC / "PN1/mkmanifests.py"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def raw_ffhq(key):
    k = int(key)
    return FFHQ / f"Part{k // 10000 + 1}" / f"{k:05d}.png"


def excluded_keys():
    """the whole FFHQ-Morphs universe + every key named by ffhqm (must be inside it)."""
    ex = set()
    for r in csv.DictReader(open(FFHQM_DOCS / "pairs.csv")):
        ex |= {f"{int(r['key_x']):05d}", f"{int(r['key_y']):05d}"}
    for r in csv.DictReader(open(FFHQM_DOCS / "bonafide_only.csv")):
        ex.add(f"{int(r['key']):05d}")
    named = set()
    for ln in open(FFHQM / "protocol/bona_keys.txt"):
        if ln.strip():
            named.add(f"{int(ln.strip()):05d}")
    for f in ("morph_pair_keys.txt", "ds_touched_pair_keys.txt"):
        for ln in open(FFHQM / "protocol" / f):
            if ln.strip():
                x, y = ln.strip().split("_")
                named |= {f"{int(x):05d}", f"{int(y):05d}"}
    for r in csv.DictReader(open(FFHQM / "manifests/ffhqm_meta.csv")):
        for c in ("key_x", "key_y"):
            if r.get(c):
                named.add(f"{int(r[c]):05d}")
        if r.get("key") and "_" not in r["key"]:
            named.add(f"{int(r['key']):05d}")
    return ex, named


def write_csv(path, rows, cols=None):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cols = cols or list(rows[0])
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def add_paths(*ps):
    for p in ps:
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
