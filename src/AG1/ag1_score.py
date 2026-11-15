"""AG1 scoring adapter: score the AG1 frames (manifests/ag1.csv, built by src/AG1/ag1_manifest.py and pinned in
plans/AG1/AG1_data_pins.sha256 by the AG1 data registration, before any AG1 score) with the released detectors, on WCSS
(H100, the registered container). A mechanical copy of the registered A43 adapter smadcvpr/a43_score.py (branch a43
c669666, sha256 339533c4d6611a59c7e6f181e0fbcc59bdbe60264fcc7b24ce47d11e44c7b6b0) with every 'a43' / 'A43' replaced by 'ag1' / 'AG1'; nothing else changed. It imports amendment G's
scorer a41g_score.py unchanged (pinned BASE_SHA) and therefore runs from a job root built from c669666's smadcvpr/
(src/AG1/make_score_root.sh) with this file and plans/AG1/AG1_data_pins.sha256 added.

  python3 -I smadcvpr/ag1_score.py --item ag1 --mode rel|own --ckpt FILE --list LIST --manifest ag1.csv
          --out a41g_out/ag1/<release>/<mode>/scores_ag1.npz [--pylib D ...] [--pylib-front D ...] [--predictor P]
          [--bs 32] [--workers 14] [--check-only]
  python3 -I smadcvpr/ag1_score.py --selftest [--tmp DIR]

Releases: rel = MADation ViT-B/16, ViT-L/14 (+ FE / FS variants, descriptive) and the SelfMAD release through our
pipeline; own = the SelfMAD release with its own preprocessing. MixFaceNet-MAD (RGB path) is not covered by this
adapter (its scorer a46_rgb_score.py is bound to the A46 plan); see experiments/AG1/prereg.md.
"""
import argparse
import hashlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import a41g_score as S  # noqa: E402  (amendment G's scorer, unchanged; pinned below)

BASE_SHA = "f53612cb146e72ca5598d9b01962dcf3fb2f9d4aa8c9d616d80bd99e273c6113"          # smadcvpr/a41g_score.py
DATA_PINS43 = HERE / "plans" / "AG1" / "AG1_data_pins.sha256"                         # the AG1 data registration
MANIFEST = "ag1.csv"
RELS_REL = ("madation_vitb16", "madation_vitl14", "madation_fe_vitb16", "madation_fe_vitl14", "madation_fs_vitb16",
            "madation_fs_vitl14", "selfmad_hrnet_w18")
ITEMS43 = {"ag1": {"modes": {"rel": RELS_REL, "own": ("selfmad_hrnet_w18",)}, "manifests": {}}}
REG_BS43 = {"rel": 32, "own": 32}
KEYS = {"rel": {"score", "score_noTTA", "logit_noTTA"}, "own": {"score", "logit_noTTA", "cropped"}}
SELFTEST = False


def refuse(msg):
    sys.exit(f"ag1_score: refused: {msg}")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def data_pin(pins=DATA_PINS43):
    """the ag1.csv sha256 from the data registration's pin file (one line '<sha256>  manifests/ag1.csv')."""
    if not pathlib.Path(pins).is_file():
        refuse(f"no {pins}: the AG1 data registration writes it before any AG1 score")
    hit = [ln.split()[0] for ln in open(pins) if len(ln.split()) == 2 and ln.split()[1] == f"manifests/{MANIFEST}"]
    if len(hit) != 1 or len(hit[0]) != 64:
        refuse(f"{pins}: no single sha256 line for manifests/{MANIFEST}")
    return hit[0]


def configure(pin=None):
    """amendment G's scorer at its pin, run with this file's item table (its file is not changed)."""
    if sha(S.__file__) != BASE_SHA:
        refuse(f"{S.__file__} is not amendment G's a41g_score.py ({BASE_SHA})")
    ITEMS43["ag1"]["manifests"] = {MANIFEST: pin or data_pin()}
    S.ITEMS, S.SELFTEST = ITEMS43, SELFTEST


def parser():
    """amendment G's arguments (a41g_score.main, --predictor and --pylib-front included) plus --check-only."""
    ap = argparse.ArgumentParser(prog="ag1_score.py")
    ap.add_argument("--item")
    ap.add_argument("--mode", choices=("rel", "own"))
    ap.add_argument("--ckpt")
    ap.add_argument("--run", default=None)
    ap.add_argument("--list")
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--predictor", default=None)
    ap.add_argument("--pylib", action="append", default=[], help="appended to sys.path (a12_released's --pylib)")
    ap.add_argument("--pylib-front", action="append", default=[],
                    help="inserted before site-packages in the given order (rsx_selfmad_own's PYTHONPATH, mode own)")
    ap.add_argument("--bs", type=int, default=None, help="32 (REG_BS43); another value is refused")
    ap.add_argument("--workers", type=int, default=14)
    ap.add_argument("--check-only", action="store_true", help="parse, pins and check_scope; SCOPE_OK; no network")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--tmp", default=None)
    return ap


def score(a, data_root, run_rel=None, run_own=None):
    """check_scope, then amendment G's run_rel / run_own (unless a selftest stub is passed), then the write-once file."""
    hm, hc, rel = S.check_scope(a, data_root)
    a.release = rel
    if a.check_only:
        print(f"SCOPE_OK item {a.item} mode {a.mode} release {rel} ckpt {hc} manifest {a.manifest} {hm} out {a.out}",
              flush=True)
        return None
    import numpy as np
    import torch
    import common as C
    import a12_released as R
    R.np, R.torch, R.C = np, torch, C     # a12_released binds these globals inside its main(); same objects here
    if a.mode in S.TF32_MODES:            # mode rel as a12_released.py; own keeps torch's defaults (rsx_selfmad_own)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
    numerics = dict(bs=a.bs, tf32_matmul=bool(torch.backends.cuda.matmul.allow_tf32),
                    tf32_cudnn=bool(torch.backends.cudnn.allow_tf32))
    rows = C.read_manifest(a.manifest)
    ids = np.array([r["id"] for r in rows])
    if len(set(ids.tolist())) != len(ids):
        refuse(f"{a.manifest}: duplicate ids")
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if a.mode == "rel":
        res = (run_rel or S.run_rel)(a, rows, R, C, torch, np)
    else:
        res = (run_own or S.run_own)(a, rows, R, C, torch, np, data_root)
    if set(res) != KEYS[a.mode] or any(len(v) != len(ids) for v in res.values()):
        refuse(f"the score arrays {sorted(res)} do not cover the manifest as mode {a.mode} must")
    tmp = pathlib.Path(str(out) + ".tmp.npz")
    np.savez(tmp, id=ids, manifest_sha256=hm, ckpt_sha256=hc, item=a.item, mode=a.mode, release=rel or "",
             run=a.run or "", script_sha256=sha(__file__), base_scorer_sha256=sha(S.__file__), **numerics, **res)
    if out.exists():
        refuse(f"{out} appeared while scoring")
    tmp.replace(out)
    print(f"scored {len(rows)} -> {out} (item {a.item}, mode {a.mode}, {rel}, ckpt {hc}, manifest {hm}; bs {numerics['bs']}, "
          f"tf32 matmul {numerics['tf32_matmul']} / cudnn {numerics['tf32_cudnn']})", flush=True)
    print(f"WRITTEN {sha(out)}  {out}", flush=True)
    return out


def main(argv=None, run_rel=None, run_own=None, pin=None):
    global SELFTEST
    if not sys.flags.isolated:
        refuse("run as python3 -I smadcvpr/ag1_score.py (third-party checkpoints)")
    ap = parser()
    a = ap.parse_args(argv)
    for d in a.pylib + a.pylib_front:
        if not pathlib.Path(d).is_absolute() or not pathlib.Path(d).is_dir():
            refuse(f"--pylib / --pylib-front {d} is not an absolute directory")
    for i, d in enumerate(a.pylib_front):
        if d not in sys.path:
            sys.path.insert(1 + i, d)
    for d in a.pylib:
        if d not in sys.path:
            sys.path.append(d)
    if a.selftest:
        SELFTEST = True
        configure(pin="0" * 64)
        return selftest(a.tmp)
    configure(pin)
    if not all((a.item, a.mode, a.ckpt, a.list, a.manifest, a.out)):
        ap.error("--item, --mode, --ckpt, --list, --manifest and --out are required (or --selftest)")
    if a.item not in ITEMS43:
        refuse(f"--item {a.item}: one of {', '.join(ITEMS43)}")
    if a.bs is None:
        a.bs = REG_BS43[a.mode]
    if a.bs != REG_BS43[a.mode]:
        refuse(f"--bs {a.bs}: --mode {a.mode} scores in batches of {REG_BS43[a.mode]}")
    return score(a, pathlib.Path(os.environ.get("SMAD_DATA", str(ROOT / "smadcvpr_data"))), run_rel, run_own)


# ------------------------------------------------------------------------------------------------ selftest (CPU, stubbed)
def selftest(tmp):
    """the adapter's own parts: the pins, the item table through amendment G's check_scope (refusals), the real argv path
    (this file's parser and main, in process and as python3 -I subprocesses with --check-only), the write path with
    stubbed run_rel / run_own (the scoring paths themselves are amendment G's, unchanged)."""
    import csv
    import subprocess
    import tempfile
    import numpy as np
    n = [0]

    def ok_(cond, msg):
        if not cond:
            refuse(f"selftest: {msg}")
        n[0] += 1

    ok_(sha(S.__file__) == BASE_SHA and S.ITEMS is ITEMS43, "a41g_score.py pinned and run with ITEMS43")
    ok_(set(ITEMS43) == {"ag1"} and ITEMS43["ag1"]["modes"] == {"rel": RELS_REL, "own": ("selfmad_hrnet_w18",)},
        "one item, modes rel (7 releases) and own (SelfMAD)")
    acts = {x.dest for x in parser()._actions}
    ok_({"predictor", "pylib_front", "check_only", "pylib", "bs", "workers", "run"} <= acts, "parser has --predictor etc.")
    with tempfile.TemporaryDirectory(dir=tmp) as d:
        d = pathlib.Path(d)
        data = d / "data"
        (data / "manifests").mkdir(parents=True)
        (data / "ag1" / "frames" / "A").mkdir(parents=True)
        man = data / "manifests" / MANIFEST
        with open(man, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "path", "label"], lineterminator="\n")
            w.writeheader()
            w.writerows([{"id": f"ag1{i:06d}", "path": f"ag1/frames/A/{i}.png", "label": i % 2} for i in range(5)])
        pins = d / "AG1_data_pins.sha256"
        pins.write_text(f"{sha(man)}  manifests/{MANIFEST}\n")
        ok_(data_pin(pins) == sha(man), "the data pin is read from its pin file")
        ck = {}
        for rel in ("madation_vitb16", "selfmad_hrnet_w18"):
            (d / "A12REL" / rel).mkdir(parents=True)
            ck[rel] = d / "A12REL" / rel / "model.safetensors"
            ck[rel].write_bytes(f"not a checkpoint {rel}".encode())
        lst = d / "rel.tsv"
        lst.write_text("".join(f"/x/A12REL/{r}\tmodel.safetensors\t{sha(c)}\n" for r, c in ck.items()))
        pred = d / "pred.dat"
        pred.write_bytes(b"not a predictor")
        os.environ["SMAD_DATA"] = str(data)

        def argv(mode="rel", rel="madation_vitb16", out=None, extra=()):
            o = out or str(d / "a41g_out" / "ag1" / rel / mode / "scores_ag1.npz")
            return ["--item", "ag1", "--mode", mode, "--ckpt", str(ck[rel]), "--list", str(lst), "--manifest", MANIFEST,
                    "--out", o, "--workers", "0", "--bs", "32", *extra]

        def sub(av, pin=None):
            code = ("import sys; sys.path.insert(0, %r); import ag1_score as A, a41g_score as S; "
                    "S.A36_RELEASE_LIST_SHA256 = %r; A.main(sys.argv[1:], pin=%r)") % (str(HERE), sha(lst), pin or sha(man))
            return subprocess.run([sys.executable, "-I", "-c", code, *av], capture_output=True, text=True,
                                  env=dict(os.environ, SMAD_DATA=str(data)))

        def refused(av, text="refused", pin=None):
            r = sub(av, pin)
            return r.returncode != 0 and text in (r.stdout + r.stderr) and "Traceback" not in r.stderr

        r = sub(argv(extra=("--check-only",)))
        ok_(r.returncode == 0 and "SCOPE_OK item ag1 mode rel release madation_vitb16" in r.stdout,
            f"the real argv passes check_scope with --check-only ({r.stdout[-200:]} {r.stderr[-300:]})")
        r = sub(argv("own", "selfmad_hrnet_w18", extra=("--check-only", "--predictor", str(pred))))
        ok_(r.returncode == 0 and "SCOPE_OK item ag1 mode own release selfmad_hrnet_w18" in r.stdout,
            f"mode own with --predictor passes check_scope ({r.stderr[-300:]})")
        r = sub(argv("own", "selfmad_hrnet_w18", extra=("--check-only",)))
        ok_(r.returncode == 0 and "SCOPE_OK" in r.stdout, "mode own without --predictor passes check_scope (refused by run_own)")
        ok_(refused(argv(extra=("--item", "x3", "--check-only"))), "another item refused")
        ok_(refused(argv(extra=("--manifest", "eval.csv", "--check-only"))), "another manifest refused")
        ok_(refused(argv(out=str(d / "elsewhere" / "scores_ag1.npz"), extra=("--check-only",))), "an output outside a41g_out refused")
        ok_(refused(argv(out=str(d / "a41g_out" / "ag1" / "x" / "scores_other.npz"), extra=("--check-only",))),
            "an output not named after the manifest refused")
        ok_(refused(argv(extra=("--check-only",)), pin="0" * 64), "a manifest off its data pin refused")
        ok_(refused(argv("own", "madation_vitb16", extra=("--check-only",))), "mode own for a MADation release refused")
        ok_(refused(argv(extra=("--bs", "64", "--check-only")), "--bs 64"), "--bs 64 refused")
        ok_(refused(argv(extra=("--predictor", str(d / "fst_probe" / "p.dat"), "--check-only")), "fst_probe"),
            "an fst path part refused (--predictor)")
        r = subprocess.run([sys.executable, str(HERE / "ag1_score.py"), *argv(extra=("--check-only",))], capture_output=True,
                           text=True)
        ok_(r.returncode != 0 and "run as python3 -I" in (r.stdout + r.stderr), "not -I refused")

        def stub_rel(a, rows, R, C, torch, np_):
            z = np_.linspace(-1, 1, len(rows)).astype(np_.float32)
            p = (1 / (1 + np_.exp(-z))).astype(np_.float32)
            return {"score": p, "score_noTTA": p, "logit_noTTA": z}

        def stub_own(a, rows, R, C, torch, np_, data_root):
            z = np_.linspace(-2, 2, len(rows)).astype(np_.float32)
            return {"score": (1 / (1 + np_.exp(-z))).astype(np_.float32), "logit_noTTA": z, "cropped": np_.ones(len(rows), bool)}
        try:
            import a12_released  # noqa: F401
            import torch
            have_r = True
        except Exception:
            have_r = False
        if have_r:
            global SELFTEST
            old = S.A36_RELEASE_LIST_SHA256
            S.A36_RELEASE_LIST_SHA256 = sha(lst)      # the stand-in list; check_scope then runs its REAL list check
            SELFTEST = False
            tf32_default = (torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32)
            for mode, rel in (("rel", "madation_vitb16"), ("own", "selfmad_hrnet_w18")):
                # one process here; each job line is its own process: torch's TF32 defaults before each mode
                torch.backends.cuda.matmul.allow_tf32, torch.backends.cudnn.allow_tf32 = tf32_default
                o = main(argv(mode, rel, extra=("--predictor", str(pred))), run_rel=stub_rel, run_own=stub_own, pin=sha(man))
                with np.load(o, allow_pickle=False) as z:
                    ok_(set(z.files) == {"id", "manifest_sha256", "ckpt_sha256", "item", "mode", "release", "run",
                                         "script_sha256", "base_scorer_sha256", "bs", "tf32_matmul", "tf32_cudnn"} | KEYS[mode],
                        f"{mode}: written keys {sorted(z.files)}")
                    ok_(str(z["script_sha256"]) == sha(__file__) and str(z["base_scorer_sha256"]) == BASE_SHA
                        and str(z["manifest_sha256"]) == sha(man) and str(z["item"]) == "ag1" and str(z["mode"]) == mode
                        and str(z["release"]) == rel and z["id"].tolist() == [f"ag1{i:06d}" for i in range(5)]
                        and int(z["bs"]) == 32 and bool(z["tf32_matmul"]) == (mode == "rel" or tf32_default[0]),
                        f"{mode}: provenance fields and numerics")
                ok_(refused(argv(mode, rel, extra=("--predictor", str(pred), "--check-only")), "exists"),
                    f"{mode}: an existing output refused (written once)")
            S.A36_RELEASE_LIST_SHA256 = old
            SELFTEST = True
    print(f"ag1_score selftest: {n[0]} checks passed")


if __name__ == "__main__":
    main()
