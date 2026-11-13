"""Standing adversary (ADV) driver. CPU only; development rows only; no network score is read by any command here.

  python3 -I run_floors.py feats  --set ab1x|train|gd12|gd0 [--limit 8] [--workers 2]
  python3 -I run_floors.py floors --stage 1|2 [--only NAME ...]
  python3 -I run_floors.py transfer
  python3 -I run_floors.py table

feats    : feature cache /mnt/t7/smad_next/ADV/feats/<set>.npz (paths, X, names), resumable in chunks of 1,000.
floors   : for each registered contrast of the stage (prereg section 4), the cross-fitted shortcut floor (floor.py):
           experiments/ADV_shortcut-floors/floors/<name>.json and the held-out scores <name>_heldout.csv
           (id, label, component, single, logreg, gbt) that check.py uses for the paired rule.
transfer : the same-data shortcut learner: logreg and gbt fitted on an arm's unique training rows (train_Sb, train_A,
           train_Sbx, train_SbFM), applied to the evaluation rows; AUC on every registered contrast and own-rule flag
           shares (logreg decision > 0; gbt probability > 0.5) on the registered pools -> floors/transfer_<arm>.json.
table    : FLOORS.md lines from the JSON files.
"""
import argparse
import csv
import json
import os
import pathlib
import sys

for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(k, "2")
import numpy as np  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import contrasts as C  # noqa: E402
import floor as FL  # noqa: E402

OUT = pathlib.Path("/mnt/t7/smad_next/ADV")
EXP = pathlib.Path("/home/narolski/smad-next/experiments/ADV_shortcut-floors")
FDIR = EXP / "floors"

STAGE1 = ["lcomb", "test_fm_R4_vs_R2w", "test_cv_R4_vs_R2w", "test_fm_R4_vs_R3", "test_cv_R4_vs_R3", "dev_fm_R4_vs_R2w",
          "dev_fm_R4_vs_R3", "border_vs_cam", "border_ffhq_vs_ffhq", "test_S4bg_vs_S0bg", "train_lad_S4_vs_S3",
          "train_lad_S4_vs_S0", "store_photo_fm61_vs_native", "store_photo_amsl112_vs_native",
          "store_morph_vs_photo_fm61", "store_morph_vs_photo_amsl112", "gd2_R4_vs_R3", "gd2_R4_vs_R2"]
STAGE2 = ["dev_cv_R4_vs_R2w", "dev_cv_R4_vs_R2w4", "dev_cv_R4_vs_R3", "dev_cv_R4_vs_R3m", "dev_S4_vs_S3", "test_S4_vs_S3",
          "dev_S4_vs_S0", "dev_S4bg_vs_S0bg", "dev_R4face_vs_R2wface", "ms1_morph_vs_photo_native", "af0_dev_u50_vs_photo",
          "hn2_lcomplete_vs_bona", "gd1_X_vs_REC", "gd1_X_vs_SAME", "gd0_sgw_vs_resmatch", "gd0_sgwp_vs_resmatch",
          "gd0_diffae_vs_resmatch"]

POOLS = {  # (manifest key, selector) for the transfer flag shares
    "R_cam_border": ("AB1X", dict(fam="border", rung="R_cam_border")),
    "R_cam_border_originals": ("AB1X", "border_originals"),
    "R_ffhq_border": ("AB1X", dict(fam="border", rung="R_ffhq_border")),
    "ffhq_bona_orig": ("AB1X", dict(fam="ffhq", rung="ffhq_bona_orig")),
    "ms1_photo_native": ("AB1X", dict(fam="ms1ffhq", rung="photo", id_plain=True)),
    "ms1_photo_fm61": ("AB1X", dict(fam="ms1ffhq", rung="photo", id_suffix="_fm61")),
    "ms1_photo_amsl112": ("AB1X", dict(fam="ms1ffhq", rung="photo", id_suffix="_amsl112")),
    "ms1_u50_native": ("AB1X", dict(fam="ms1ffhq", rung="u50", id_plain=True)),
    "ms1_u50_fm61": ("AB1X", dict(fam="ms1ffhq", rung="u50", id_suffix="_fm61")),
    "ms1_u50_amsl112": ("AB1X", dict(fam="ms1ffhq", rung="u50", id_suffix="_amsl112")),
    "dev_S3": ("AB1X", dict(fam="splice", role="dev", rung="S3")),
    "dev_S0": ("AB1X", dict(fam="splice", role="dev", rung="S0")),
    "dev_S4": ("AB1X", dict(fam="splice", role="dev", rung="S4")),
    "dev_R3_cv": ("AB1X", dict(fam="ladder", role="dev", rung="R3", tool="opencv")),
    "dev_R3_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R3", tool="facemorpher")),
    "dev_R2w_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R2w", tool="facemorpher")),
    "dev_R2w4_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R2w4", tool="facemorpher")),
    "dev_R4_cv": ("AB1X", dict(fam="ladder", role="dev", rung="R4", tool="opencv")),
    "dev_R4_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R4", tool="facemorpher")),
    "dev_R0": ("AB1X", dict(fam="ladder", role="dev", rung="R0")),
    "af0_dev_photo": ("AB1X", dict(fam="af0", role="dev", rung="photo")),
    "lcomb_morph": ("AB1X", dict(fam="ffhq_lcomb", rung="landmark_combined_orig")),
    "lcomb_genuine": ("AB1X", dict(fam="ffhq_lcomb", rung="landmark_combined_resmatch")),
    "gd2_R2": ("GD", dict(fam="gd2", rung="R2")),
    "gd2_R4": ("GD", dict(fam="gd2", rung="R4")),
}


def feat_paths(setname):
    if setname == "ab1x":
        P = set()
        for n, (key, *_ ) in C.contrast_defs().items():
            if key == "AB1X":
                P |= {p for _, p, _, _ in C.build(n)}
        for k, (key, s) in POOLS.items():
            if key == "AB1X":
                P |= {p for _, p, _, _ in pool(k)}
        return sorted(P)
    if setname == "train":
        P = set()
        for a in C.TRAIN:
            P |= {C.resolve(r["path"]) for r in C.train_rows(a)}
        return sorted(P)
    fams = {"gd12": ("gd1", "gd2"), "gd0": ("gd0",)}[setname]
    return sorted({C.resolve(r["path"]) for r in C.rows(C.GD) if r["fam"] in fams})


def pool(k):
    key, s = POOLS[k]
    R = C.rows(C.manifest(key))
    if s == "border_originals":
        want = {r["id"][5:].split("__")[0] for r in C.sel(R, fam="border", rung="R_cam_border")}
        P = [r for r in R if r["id"] in want]
    else:
        P = C.sel(R, **s)
    return [(r["id"], C.resolve(r["path"]), int(r["label"]), C.persons(r)) for r in P]


def cmd_feats(a):
    import feats as F
    paths = feat_paths(a.set)
    if a.limit:
        paths = paths[: a.limit]
    OUT.joinpath("feats").mkdir(parents=True, exist_ok=True)
    out = OUT / "feats" / f"{a.set}{'_limit%d' % a.limit if a.limit else ''}.npz"
    done_p, done_X = [], []
    if out.exists():
        z = np.load(out, allow_pickle=False)
        done_p, done_X = list(z["paths"]), list(z["X"])
    have = set(done_p)
    todo = [p for p in paths if p not in have]
    print(a.set, "total", len(paths), "todo", len(todo), flush=True)
    for i in range(0, len(todo), 1000):
        chunk = todo[i:i + 1000]
        X = F.compute(chunk, workers=a.workers)
        done_p += chunk
        done_X += list(X)
        np.savez(out, paths=np.array(done_p), X=np.array(done_X), names=np.array(F.names()))
        print(a.set, len(done_p), "/", len(paths), flush=True)
    print("DONE", out, flush=True)


_FE = {}


def featmap():
    if not _FE:
        for f in sorted((OUT / "feats").glob("*.npz")):
            if "_limit" in f.name:
                continue
            z = np.load(f, allow_pickle=False)
            names = [str(n) for n in z["names"]]
            _FE.setdefault("names", names)
            assert names == _FE["names"], f
            for p, x in zip(z["paths"], z["X"]):
                _FE[str(p)] = x
    return _FE


def X_of(rowlist):
    fm = featmap()
    missing = [p for _, p, _, _ in rowlist if p not in fm]
    assert not missing, (len(missing), missing[:3])
    return np.stack([fm[p] for _, p, _, _ in rowlist]), fm["names"]


def cmd_floors(a):
    FDIR.mkdir(parents=True, exist_ok=True)
    names = a.only or (STAGE1 if a.stage == 1 else STAGE2)
    for n in names:
        rl = C.build_train(n) if n in C.TRAIN_CONTRASTS else C.build(n)
        X, nm = X_of(rl)
        y = np.array([l for _, _, l, _ in rl])
        rep, sc, groups = FL.fit_contrast(X, y, [p for *_, p in rl], nm)
        rep["contrast"] = n
        rep["definition"] = (C.TRAIN_CONTRASTS[n] if n in C.TRAIN_CONTRASTS else
                             {k: v for k, v in zip(("manifest", "positive", "negative", "note"), C.contrast_defs()[n])})
        (FDIR / f"{n}.json").write_text(json.dumps(rep, indent=1, default=str))
        with open(FDIR / f"{n}_heldout.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "label", "component", "single", "logreg", "gbt"])
            for k, (i, _, l, _) in enumerate(rl):
                w.writerow([i, l, int(groups[k])] + [f"{sc[m][k]:.6g}" for m in ("single", "logreg", "gbt")])
        fl = rep["floor"]
        print(f"{n}: floor {fl['auc']:.3f} [{fl['ci'][0]:.3f}, {fl['ci'][1]:.3f}] ({fl['model']}); "
              f"carried by {rep.get('carrying_family')}; in-sample best single {rep['insample_best_single']:.3f} "
              f"({rep['insample_best_single_stat']})", flush=True)


def cmd_transfer(a):
    FDIR.mkdir(parents=True, exist_ok=True)
    defs = C.contrast_defs()
    for arm in C.TRAIN:
        T = C.train_rows(arm)
        rl = [(r["id"], C.resolve(r["path"]), int(r["label"]), C.train_persons(r)) for r in T]
        X, nm = X_of(rl)
        y = np.array([l for _, _, l, _ in rl])
        Xc, _, keep = FL._clean(X, X[:1])
        med = np.nanmedian(np.where(np.isfinite(X), X, np.nan), 0)
        models = {k: FL._model(k).fit(Xc, y) for k in ("logreg", "gbt")}

        def score(rows_):
            Z, _ = X_of(rows_)
            Z = np.where(np.isfinite(Z), Z, med)[:, keep]
            return {"logreg": models["logreg"].decision_function(Z), "gbt": models["gbt"].predict_proba(Z)[:, 1]}
        rep = dict(arm=arm, n_train=len(y), n_train_pos=int(y.sum()), contrasts={}, pools={})
        for n in list(defs):
            if defs[n][0] == "GD" and not all(p in featmap() for _, p, _, _ in C.build(n)):
                continue
            rows_ = C.build(n)
            s = score(rows_)
            yy = np.array([l for _, _, l, _ in rows_])
            rep["contrasts"][n] = {k: FL.auc(v, yy) for k, v in s.items()}
        for k in POOLS:
            rows_ = pool(k)
            if not all(p in featmap() for _, p, _, _ in rows_):
                continue
            s = score(rows_)
            rep["pools"][k] = dict(n=len(rows_), flag_logreg=float(np.mean(s["logreg"] > 0)),
                                   flag_gbt=float(np.mean(s["gbt"] > 0.5)))
        (FDIR / f"transfer_{arm}.json").write_text(json.dumps(rep, indent=1))
        print(arm, json.dumps({k: round(v["logreg"], 3) for k, v in rep["contrasts"].items()}), flush=True)


def cmd_table(a):
    lines = []
    for f in sorted(FDIR.glob("*.json")):
        if f.name.startswith("transfer_"):
            continue
        r = json.loads(f.read_text())
        fl = r["floor"]
        lines.append(f"| {r['contrast']} | {r['n_pos']} / {r['n_neg']} | {fl['auc']:.3f} [{fl['ci'][0]:.3f}, "
                     f"{fl['ci'][1]:.3f}] | {fl['model']} | {r['carrying_family']} | {r['insample_best_single']:.3f} "
                     f"({r['insample_best_single_stat']}) | {r['logreg_f27']['auc']:.3f} | {fl['ci'][1]:.3f} |")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("feats", "floors", "transfer", "table"))
    ap.add_argument("--set", default="ab1x")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--stage", type=int, default=1)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    {"feats": cmd_feats, "floors": cmd_floors, "transfer": cmd_transfer, "table": cmd_table}[a.cmd](a)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
