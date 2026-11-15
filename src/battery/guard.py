"""Shared test battery (BATTERY), deny-list guard. Development data only.

Two layers:
1. check_path(p) / check_rows(rows): every image path and every manifest the battery reads is tested against an explicit
   deny-list of closed benchmarks and sealed sets before anything is opened or scored. A hit raises DeniedPath.
2. install(): a CPython audit hook on the "open" event (and os.listdir / os.scandir / glob) for the whole process, so that
   no imported reader, library or later code path can open a denied path either. Audit hooks cannot be removed.

Deny-list (BATTERY brief, 13 Nov): FRLL (and FRLL-Morphs), MAD22, MorDIFF, DiM (DiM-A/C, Fast-DiM, Greedy-DiM), H1, FEI,
CASIA-WebFace, manifests/valx.csv (any valx file except the allowed valx_a.csv), FST, A12SP / A12-SP.
Matching is on path tokens (split at every non-alphanumeric character, lower case), so that development sources whose
names merely contain the letters (CASIA-FASD, colorFERET, tt1, ...) pass, plus substring rules for names that are never
part of a development path."""
import os
import re
import sys

# whole tokens (path split at non-alphanumerics, lower case)
DENY_TOKENS = {"frll", "frllm", "mad22", "mordiff", "dim", "fastdim", "greedydim", "h1", "fei", "webface", "fst",
               "a12sp", "valx", "gtest"}
# substrings anywhere in the lower-case path
DENY_SUB = ("frll", "mad22", "mordiff", "casia-webface", "casia_webface", "casiawebface", "webface", "a12sp", "a12-sp",
            "a12_sp", "fast-dim", "fast_dim", "greedy-dim", "greedy_dim", "/dim_", "/dim-", "/dim/", "fst")
# token pairs
DENY_PAIRS = (("casia", "webface"), ("dim", "a"), ("dim", "c"))
ALLOW_EXACT_NAMES = {"valx_a.csv"}          # the one allowed valx file (OWNER_BRIEF hard rules)
_TOK = re.compile(r"[^a-z0-9]+")
_installed = False


class DeniedPath(PermissionError):
    pass


def _reason_str(s):
    """the rules on one lower-case path string (allow check included)."""
    if os.path.basename(s) in ALLOW_EXACT_NAMES:
        return None
    toks = [t for t in _TOK.split(s) if t]
    for t in toks:
        if t in DENY_TOKENS:
            return f"token '{t}'"
    for x in DENY_SUB:
        if x in s:
            return f"substring '{x}'"
    for a, b in DENY_PAIRS:
        for i in range(len(toks) - 1):
            if toks[i] == a and toks[i + 1] == b:
                return f"token pair '{a} {b}'"
    return None


def reason(p):
    """None if the path is allowed, else the rule that denies it. The path string AND its resolved real path (symlinks
    followed) are both checked (pre-run review F5); realpath raises no "open" audit event, so the hook cannot recurse."""
    if isinstance(p, int):
        return None
    s = os.fspath(p)
    s = s.decode(errors="replace") if isinstance(s, bytes) else s
    if not s:
        return None
    r = _reason_str(s.lower())
    if r:
        return r
    try:
        rp = os.path.realpath(s)
    except (OSError, ValueError):
        return None
    if rp != s:
        r = _reason_str(rp.lower())
        if r:
            return f"resolved {rp!r}: {r}"
    return None


def check_path(p, what="path"):
    r = reason(p)
    if r:
        raise DeniedPath(f"BATTERY DENY-LIST: refusing to open {what} {os.fspath(p)!r} ({r}): closed benchmark or sealed set")
    return p


def check_rows(rows, key="path", what="manifest row"):
    """every row's path; raises on the first denied row (no row of a denied manifest is ever scored)."""
    for r in rows:
        check_path(r[key], what)
        check_path(r.get("id", ""), what + " id")
    return rows


_LIB = tuple(sorted({os.path.realpath(x).rstrip("/") + "/" for x in (sys.prefix, sys.base_prefix, sys.exec_prefix)}))


def _is_library(p):
    """files under the Python installation roots (sys.prefix, base_prefix, exec_prefix) only: library code, not data."""
    try:
        rp = os.path.realpath(p)
    except (TypeError, ValueError):
        return False
    return rp.startswith(_LIB)


def _hook(event, args):
    if event == "open":
        p = args[0]
        if isinstance(p, (str, bytes, os.PathLike)):
            if isinstance(p, bytes):
                p = p.decode(errors="replace")
            if _is_library(p):
                return
            r = reason(p)
            if r:
                raise DeniedPath(f"BATTERY DENY-LIST (audit hook): open {p!r} refused ({r})")
    elif event in ("os.listdir", "os.scandir", "glob.glob"):
        p = args[0] if args else None
        if isinstance(p, (str, os.PathLike)) and reason(p):
            raise DeniedPath(f"BATTERY DENY-LIST (audit hook): {event} {p!r} refused ({reason(p)})")


def install():
    """process-wide; idempotent; cannot be undone."""
    global _installed
    if not _installed:
        sys.addaudithook(_hook)
        _installed = True
    return True


def self_test():
    """the deny-list must deny every named closed set and pass the development sources the battery reads."""
    deny = ["/x/FRLL/img.png", "/data/frll_morphs/a.png", "eval/mad22/x.png", "/d/MorDIFF/1.png", "/d/DiM-A/1.png",
            "/d/Greedy-DiM/1.png", "/d/fast_dim/x", "/d/H1/x.png", "lists/h1.csv", "/d/FEI/1.jpg", "/d/CASIA-WebFace/0/1.jpg",
            "manifests/valx.csv", "/d/fst_pack.tar", "/d/A12SP/x", "/d/a12-sp/x", "/d/A12_SP/x"]
    allow = ["eval/pn1/val_frgc_zero_0000.png", "eval/tt1/casia_fasd_0001.png", "eval/ms1/hold_ffhq_photo_0000.png",
             "eval/tt1ref/ar1_000000.png", "/mnt/t7/smad_next/AF0/cues/ar1.npz", "manifests/valx_a.csv",
             "/mnt/t7/smad_next/TT1/meds/meds_manifest.csv", "eval/gd/x.png", "feret:00002", "eval/tt1g/bgeo_g112_val.png",
             "/mnt/t7/smad_next/BD1/d_values.csv"]
    deny += ["/d/smadcvpr/prep_gtest.py", "/d/gtest/x.png"]
    bad = [p for p in deny if reason(p) is None] + [p for p in allow if reason(p) is not None]
    # symlink case: an innocent name pointing into a denied folder must be denied (review F5)
    import tempfile
    with tempfile.TemporaryDirectory(prefix="battery_guard_") as td:
        link = os.path.join(td, "ok.png")
        os.symlink("/x/FRLL/img.png", link)
        if reason(link) is None:
            bad.append("symlink ok.png -> /x/FRLL/img.png")
        link2 = os.path.join(td, "valx_a.csv")
        os.symlink("/x/manifests/valx.csv", link2)
        if reason(link2) is None:
            bad.append("symlink valx_a.csv -> valx.csv")
    assert not bad, f"deny-list self-test failed on {bad}"
    return dict(denied=len(deny) + 2, allowed=len(allow))
