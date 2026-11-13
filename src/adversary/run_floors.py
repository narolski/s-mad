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
          "store_morph_vs_photo_fm61", "store_morph_vs_photo_amsl112", "gd2_R4_vs_R3", "gd2_R4_vs_R2", "gd2_R4_vs_R2s1"]
CEILING = ("border_vs_cam", "border_ffhq_vs_ffhq", "store_photo_fm61_vs_native", "store_photo_amsl112_vs_native",
           "ri_R0s61_vs_R0", "ri_S0_vs_R0", "ri_R2w4_vs_R0")
FILE_SIZE = ("F27:png_bytes", "STORE:png_bytes_per_px", "STORE:png_n_idat", "STORE:png_idat_mean_bytes",
             "STORE:png_zlib_level", "STORE:png_ancillary", "STORE:png_colour_type",
             "STORE:png_filter0_share", "STORE:png_filter1_share", "STORE:png_filter2_share",
             "STORE:png_filter3_share", "STORE:png_filter4_share")
NUISANCE = ("BORDER:", "RES:", "STORE:", "RENDER:")            # amendment 2 F4: no F27, no BLEND
STAGE1A = ["lcomb", "test_fm_R4_vs_R2w", "test_cv_R4_vs_R2w", "test_fm_R4_vs_R3", "test_cv_R4_vs_R3"]
AFTER_READ = ("dev_cv_R4_vs_R2w", "dev_cv_R4_vs_R2w4", "dev_cv_R4_vs_R3", "dev_cv_R4_vs_R3m", "dev_S4_vs_S3", "test_S4_vs_S3",
              "dev_S4_vs_S0", "dev_S4bg_vs_S0bg", "dev_R4face_vs_R2wface", "ms1_morph_vs_photo_native",
              "af0_dev_u50_vs_photo", "hn2_lcomplete_vs_bona", "gd1_X_vs_REC", "gd1_X_vs_SAME", "gd0_sgw_vs_resmatch",
              "gd0_sgwp_vs_resmatch", "gd0_diffae_vs_resmatch")
AMEND1 = ["ri_R4_vs_R3", "ri_R4_vs_R0", "ri_S4_vs_S3", "ri_R0s61_vs_R0", "ri_S0_vs_R0", "ri_R2w4_vs_R0"]
WITHIN_D = ("ri_S4_vs_S3", "dev_S4_vs_S3", "test_S4_vs_S3")
DFEATS = pathlib.Path("/mnt/t7/smad_next/BD1/d_values.csv")   # BD1 prereg line 30: D (lead, amendment 2)


def within_d(ids, y, scores, col="D"):
    """BD1's primary rule on held-out floor scores: quintile edges of log D over the pooled rows, AUC within each
    stratum, mean weighted by n_pos x n_neg over strata with >= 10 rows of each class."""
    D = {r["id"]: float(r[col]) for r in csv.DictReader(open(DFEATS))}
    keep = np.array([i in D for i in ids])
    if keep.sum() < 20:
        return None
    ld = np.log(np.array([D[i] for i in np.array(ids)[keep]]))
    yy = y[keep]
    edges = np.quantile(ld, [0.2, 0.4, 0.6, 0.8])
    q = np.searchsorted(edges, ld, side="right")
    out = dict(n_rows=int(keep.sum()), D=col)
    for m, s in scores.items():
        ss = s[keep]
        num = den = 0.0
        cov = 0
        for k in range(5):
            w = q == k
            p, n = int(yy[w].sum()), int(w.sum() - yy[w].sum())
            if p >= 10 and n >= 10:
                num += FL.auc(ss[w], yy[w]) * p * n
                den += p * n
                cov += int(w.sum())
        out[m] = float(num / den) if den else None
        out["coverage"] = cov / int(keep.sum())
    pure = np.where(np.isfinite(ld), ld, 0)
    num = den = 0.0
    for k in range(5):
        w = q == k
        p, n = int(yy[w].sum()), int(w.sum() - yy[w].sum())
        if p >= 10 and n >= 10:
            a = FL.auc(pure[w], yy[w])
            num += max(a, 1 - a) * p * n
            den += p * n
    out["pure_D_reference"] = float(num / den) if den else None
    return out


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
    "dev_R3_cv": ("AB1X", dict(fam="ladder", role="dev", rung="R3", tool="opencv", strength="")),
    "dev_R3_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R3", tool="facemorpher", strength="")),
    "dev_R2w_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R2w", tool="facemorpher", strength="")),
    "dev_R2w4_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R2w4", tool="facemorpher", strength="")),
    "dev_R4_cv": ("AB1X", dict(fam="ladder", role="dev", rung="R4", tool="opencv", strength="")),
    "dev_R4_fm": ("AB1X", dict(fam="ladder", role="dev", rung="R4", tool="facemorpher", strength="")),
    "dev_R0": ("AB1X", dict(fam="ladder", role="dev", rung="R0", strength="")),
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
            if "_limit" in f.name or f.name == "pngmeta.npz":
                continue
            z = np.load(f, allow_pickle=False)
            names = [str(n) for n in z["names"]]
            _FE.setdefault("names", names)
            assert names == _FE["names"], f
            for p, x in zip(z["paths"], z["X"]):
                _FE[str(p)] = x
    return _FE


_PM = {}


def pngmeta(p):
    import feats as F
    if not _PM:
        f = OUT / "feats" / "pngmeta.npz"
        if f.exists():
            z = np.load(f)
            _PM.update({str(a): b for a, b in zip(z["paths"], z["X"])})
        _PM["_dirty"] = False
    if p not in _PM:
        _PM[p] = np.array(F.pngmeta(p), float)
        _PM["_dirty"] = True
    return _PM[p]


def save_pngmeta():
    if _PM.get("_dirty"):
        ks = [k for k in _PM if not k.startswith("_")]
        np.savez(OUT / "feats" / "pngmeta.npz", paths=np.array(ks), X=np.stack([_PM[k] for k in ks]))
        _PM["_dirty"] = False


def X_of(rowlist):
    import feats as F
    fm = featmap()
    missing = [p for _, p, _, _ in rowlist if p not in fm]
    assert not missing, (len(missing), missing[:3])
    X = np.stack([np.r_[fm[p], pngmeta(p)] for _, p, _, _ in rowlist])
    save_pngmeta()
    return X, fm["names"] + F.PNGMETA


def cmd_floors(a):
    FDIR.mkdir(parents=True, exist_ok=True)
    names = a.only or {0: STAGE1A, 1: [n for n in STAGE1 if n not in STAGE1A], 2: STAGE2, 3: AMEND1}[a.stage]
    for n in names:
        rl = C.build_train(n) if n in C.TRAIN_CONTRASTS else C.build(n)
        X, nm = X_of(rl)
        y = np.array([l for _, _, l, _ in rl])
        rep, sc, groups = FL.fit_contrast(X, y, [p for *_, p in rl], nm)
        rep["contrast"] = n
        rep["kind"] = "separability ceiling (both sides genuine; no exceeds rule)" if n in CEILING else "floor"
        if n in AFTER_READ:
            rep["label"] = "after the frozen candidate's read; features designed with Sb's landmark_combined value known"
        if n in C.TRAIN_CONTRASTS:
            rep["note"] = ("binds only for E2's out-of-fold probe; the E3 gate is an in-sample training AUC, so an "
                           "in-sample gbt AUC is printed as context")
            from sklearn.base import clone  # noqa: F401
            Xc, _, _ = FL._clean(X, X[:1])
            m = FL._model("gbt").fit(Xc, y)
            rep["insample_gbt_auc"] = FL.auc(m.predict_proba(Xc)[:, 1], y)
        pix = [k for k, v in enumerate(nm) if v not in FILE_SIZE]
        rp, _, _ = FL.fit_contrast(X[:, pix], y, [p for *_, p in rl], [nm[k] for k in pix], detail=False)
        rep["pixel_only_floor"] = rp["floor"]
        nu = [k for k, v in enumerate(nm) if v.startswith(NUISANCE)]
        rn, scn, _ = FL.fit_contrast(X[:, nu], y, [p for *_, p in rl], [nm[k] for k in nu], detail=False)
        rep["nuisance_floor"] = rn["floor"]
        rep["nuisance_floor"]["families"] = list(NUISANCE)
        if n == "lcomb":                                           # amendment 2 F3: regression gate
            f27 = rep["insample_best_single_f27"]
            rep["regression_gate"] = dict(value=f27, stat=rep["insample_best_single_f27_stat"],
                                          passed=bool(round(f27, 3) == 0.886))
            assert rep["regression_gate"]["passed"], ("regression gate failed", f27)
        if n in WITHIN_D:
            rep["within_D_quintiles"] = within_d([i for i, *_ in rl], y, sc)
        rep["definition"] = (C.TRAIN_CONTRASTS[n] if n in C.TRAIN_CONTRASTS else
                             {k: v for k, v in zip(("manifest", "positive", "negative", "note"), C.contrast_defs()[n])})
        (FDIR / f"{n}.json").write_text(json.dumps(rep, indent=1, default=str))
        with open(FDIR / f"{n}_heldout.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "label", "component", "single", "logreg", "gbt", "nu_single", "nu_logreg", "nu_gbt"])
            for k, (i, _, l, _) in enumerate(rl):
                w.writerow([i, l, int(groups[k])] + [repr(float(sc[m][k])) for m in ("single", "logreg", "gbt")]
                           + [repr(float(scn[m][k])) for m in ("single", "logreg", "gbt")])
        fl = rep["floor"]
        print(f"{n}: nuisance floor {rep['nuisance_floor']['auc']:.3f}; ADV floor {fl['auc']:.3f} [{fl['ci'][0]:.3f}, {fl['ci'][1]:.3f}] ({fl['model']}); "
              f"carried by {rep.get('carrying_family')}; in-sample best single {rep['insample_best_single']:.3f} "
              f"({rep['insample_best_single_stat']})", flush=True)


def cmd_pins(a):
    import hashlib
    fs = sorted(p for p in FDIR.glob("*") if p.suffix in (".json", ".csv") and not p.name.startswith("transfer_"))
    lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in fs if p.stem.replace("_heldout", "")
             in set(a.only or [])]
    (FDIR / f"pins_stage{a.stage}.sha256").write_text("\n".join(lines) + "\n")
    print(len(lines), "files pinned in", f"pins_stage{a.stage}.sha256")


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
    ap.add_argument("cmd", choices=("feats", "floors", "transfer", "table", "pins"))
    ap.add_argument("--set", default="ab1x")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--stage", type=int, default=1)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    {"feats": cmd_feats, "floors": cmd_floors, "transfer": cmd_transfer, "table": cmd_table, "pins": cmd_pins}[a.cmd](a)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
