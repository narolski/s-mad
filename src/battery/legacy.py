"""Shared test battery (BATTERY): the reviewed readers, imported unchanged by file path after a sha256 check.

The battery never re-implements a statistic. Every number it writes comes from a function of one of these files, at the
pin below (the version that produced the reviewed numbers of the shortcut audit table, SA1). A file off its pin stops the
battery. smadcvpr/prep_eval.py and prep_gtest.py are never edited or imported here.

Optional path remapping (--side): the readers hard-code absolute paths under /mnt/t7/smad_next and
/home/narolski/smad-next. With remap(prefix_map) every module-level str / pathlib.Path constant of the loaded readers that
starts with one of those prefixes is rebound to the same relative path under another root (a copy of the side files on a
cluster's local disk). Function bodies are not touched; the regression test runs without remapping."""
import hashlib
import importlib.util
import pathlib
import sys

SRC = pathlib.Path(__file__).resolve().parents[1]

# module name -> (path relative to src/, sha256 at the reviewed version)
PINS = {
    "pn1lib": ("PN1/pn1lib.py", "136f78543af3747811919fcaf06cfc0abaeb0d64692f2c196c9320bfe4841482"),
    "reads": ("PN1/reads.py", "5169ac4267507e6d1a1ee1e75d13cdf805e100f9e9f211a5da1052b667c4fd69"),
    "fs_read": ("PN1/fs_read.py", "c0d8dc19cbf375aa2daf9dd434b7ab6cc1d7e5810c3da781730fe0cb159dcf21"),
    "c2p_read": ("PN1/c2p_read.py", "45e72914d960214131a5b4a11aefd2e301a2236e908d77d20d94136c1d7d5840"),
    "pr1_read": ("PR1/pr1_read.py", "1970e8f2e1dce43f70ab3c214c77584e2fae34e47399ba5517e17fa501d98124"),
    "gd_read": ("PR1/gd_read.py", "8ff4e3b77a79ca7b0b086939b42e791f61e5adf5f048dcbc10a9efe34b8fea7e"),
    "tt1common": ("TT1/tt1common.py", "1053022792e99ade577abc11490d169e0bec15c6a6dd761fc5aac3b92c52a1a3"),
    "tt1_read": ("TT1/tt1_read.py", "4546f520f63b48c33e6d313673314b6c0f778ddc81da02b22d356f8c6a87fb8f"),
    "tt1_read_fs": ("TT1/tt1_read_fs.py", "87356fd74746b08f621e3e0c4e38554c80f475fae7d0d1f5e7f8634cb144f227"),
    "tt1_read_meds": ("TT1/meds/tt1_read_meds.py", "0b5d86b154c2455f3279ded63ee9a606196140fa65b707d6a173212d0cb84b11"),
    "ab1_read": ("AB1/ab1_read.py", "74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b"),
    "bd1_read": ("BD1/bd1_read.py", "8f3ad9e1f31b334f2d1f17c8b12bcadca3457ab8cc2c108678f4283c44fbe9bb"),
}
# scoring references (not imported; their loop is what score.py follows, and their hashes are recorded)
SCORER_PINS = {
    "PN1/pn1_score.py": "737d6e35e4da3af3e2587e8ee2f5cf19c98d305d3c00f445046046be44bdee79",
    "PN1/rescore.py": "6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e",
}
_MODS = {}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def get(name):
    """the reviewed module `name`, loaded once from its pinned file. Its own directory goes on sys.path (as the reader
    does when run), so its sibling imports resolve to the same pinned files (asserted below)."""
    if name in _MODS:
        return _MODS[name]
    rel, want = PINS[name]
    p = SRC / rel
    got = sha(p)
    if got != want:
        raise RuntimeError(f"BATTERY: {rel} is off its pin ({got[:16]} != {want[:16]}); the battery reads only the reviewed version")
    d = str(p.parent)
    if d not in sys.path:
        sys.path.insert(0, d)
    if name in sys.modules and getattr(sys.modules[name], "__file__", None) and \
            pathlib.Path(sys.modules[name].__file__).resolve() == p:
        m = sys.modules[name]
    else:
        spec = importlib.util.spec_from_file_location(name, p)
        m = importlib.util.module_from_spec(spec)
        sys.modules[name] = m                       # sibling "import pn1lib" etc. then reuse this pinned module
        spec.loader.exec_module(m)
    _MODS[name] = m
    return m


def loaded_files():
    """every reader file imported so far with its sha256 (for the output record)."""
    out = {}
    for n, m in sys.modules.items():
        f = getattr(m, "__file__", None)
        if not f or not pathlib.Path(f).is_absolute() or not pathlib.Path(f).exists():
            continue
        f = pathlib.Path(f).resolve()
        if f.is_relative_to(SRC) and not f.is_relative_to(SRC / "battery"):
            out[str(f.relative_to(SRC))] = sha(f)
    return dict(sorted(out.items()))


def check_siblings():
    """the sibling modules the readers import by name must be the pinned files."""
    for n, (rel, want) in PINS.items():
        m = sys.modules.get(n)
        if m is not None and getattr(m, "__file__", None):
            f = pathlib.Path(m.__file__).resolve()
            assert f == (SRC / rel).resolve() and sha(f) == want, f"module {n} resolved to {f}, not the pinned {rel}"


def remap(prefix_map):
    """rebind module-level path constants of every loaded reader (see module docstring). Returns the list of rebinds."""
    done = []
    for n in list(_MODS):
        m = _MODS[n]
        for k, v in list(vars(m).items()):
            if isinstance(v, (str, pathlib.PurePath)):
                s = str(v)
                for a, b in prefix_map.items():
                    if s == a or s.startswith(a.rstrip("/") + "/"):
                        new = b.rstrip("/") + s[len(a.rstrip("/")):]
                        setattr(m, k, type(v)(new) if isinstance(v, pathlib.PurePath) else new)
                        done.append((n, k, s, new))
                        break
    return done
