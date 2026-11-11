"""PN1 tier 0: logistic heads on frozen mean patch tokens (prereg section 3), arms A0 (photos against morphs) and B0
(protocol), CLIP ViT-L/14 224 and DINOv3 ViT-L/16 512, seeds 401 to 405 (401 named), then reads (reads.py).
  python3 -I tier0.py [--backbones clip224,dinov3_512] [--seeds 401,402,403,404,405] [--smoke]
Outputs: /mnt/t7/smad_next/PN1/tier0/<bb>/<arm>_s<seed>.npz (id, logit) and
         experiments/PN1_protocol-network-first-tests/tier0/<bb>_<arm>_s<seed>.json (reads), tier0_summary.json.
"""
import argparse
import json
import os
import pathlib
import sys
import time

os.environ.setdefault("OMP_NUM_THREADS", "2")
import numpy as np  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402


def soft_cat_rows(cat_ids):
    """AF0 softened training copies (AF0's soft_soft_src.csv) as catalogue rows (role train if the source is)."""
    import mkmanifests as MM
    by_id = {r["id"]: r for r in K.catalog() if r["fam"] == "af0"}
    out = []
    for r in MM.soft_rows():
        src = by_id.get(r["id"].rsplit("_", 1)[0])
        if src is None or r["id"] in cat_ids:
            continue
        x = dict(src)
        x.update(id=r["id"], path=r["path"], src="soft", strength=K._strength(r["rung"]))
        out.append(x)
    return out


def train_sets(cat):
    """A0, B0 (prereg section 3) and Bn0 (amendment 4 item 10), unique rows; balance is applied by balance_rows."""
    tr = [r for r in cat if r["fam"] == "af0" and r["role"] == "train"]
    A = [r for r in tr if r["strength"] == "" and r["rung"] in ("photo", "u50")]
    B = A + [r for r in tr if r["strength"] == "" and (r["rung"] == "zero" or
                                                      (r["rung"] in ("halfA", "halfB") and r["field"] == "u50"))]
    B += [r for r in tr if r["strength"] == "61" and r["rung"] in ("photo", "u50", "halfA", "halfB")]
    import mkmanifests as MM
    kind = lambda r: f"{'half' if r['rung'].startswith('half') else r['rung']}{r['strength']}"  # noqa: E731
    lab = lambda r: "1" if r["klass"] == "attack" else "0"  # noqa: E731
    rowsB = [dict(r, kind=kind(r), label=lab(r)) for r in B]
    Bn = MM.draw_bn(rowsB, sum(lab(r) == "0" for r in A), sum(lab(r) == "1" for r in A))
    return {"A0": A, "B0": B, "Bn0": Bn}


def balance_rows(rows):
    """amendment 4 item 1: class balance inside each stratum of database x storage history (seeded repetition)."""
    import mkmanifests as MM
    rs = [dict(r, label="1" if r["klass"] == "attack" else "0", db=r["pool"].split("_")[1],
               hist="s61" if r["strength"] == "61" else "native") for r in rows]
    out, strata = MM.balanced_strata(rs)
    return out, strata


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbones", default="clip224,dinov3_512")
    ap.add_argument("--seeds", default="401,402,403,404,405")
    ap.add_argument("--smoke", action="store_true", help="8 rows per class, 1 seed, 2 folds: a code test only")
    a = ap.parse_args()
    cat = K.catalog()
    cat += soft_cat_rows({r["id"] for r in cat})
    sets = train_sets(cat)
    z = np.load(K.AF0 / "cues" / "ar1.npz")
    cues = {str(i): c for i, c in zip(z["ids"], z["cues"])}
    names = [str(n) for n in z["names"]]
    for f in sorted((K.PN1 / "cues").glob("*.npz")) if (K.PN1 / "cues").exists() else []:
        if f.name.startswith("cert_") or "_limit" in f.name:
            continue
        z2 = np.load(f)
        assert [str(n) for n in z2["names"]] == names
        cues.update({str(i): c for i, c in zip(z2["ids"], z2["cues"])})
    # amendment 4 item 6 (F8): the floor also over the 12 certificate cues at 224 px
    import cert as CE
    c224 = CE.load_cues("c224")
    cues = {i: np.r_[v, c224[i]] for i, v in cues.items() if i in c224}
    names = names + [n + "@224" for n in CE.PIX]
    out_dir = K.RES / "tier0"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for bb in a.backbones.split(","):
        idx, X, rep = K.load_features(bb)
        have = [r for r in cat if r["id"] in idx]
        P = RD.pools(have)
        summary[bb] = dict(n_features=len(idx), dupe_checks=rep,
                           missing_train={k: sum(1 for r in v if r["id"] not in idx) for k, v in sets.items()},
                           pools={k: len(v) for k, v in sorted(P.items())})
        for arm, rows in sets.items():
            rows = [r for r in rows if r["id"] in idx]
            rows, strata = balance_rows(rows)
            y = np.array([1 if r["klass"] == "attack" else 0 for r in rows])
            if a.smoke:
                rng = np.random.default_rng(0)
                pick = np.r_[rng.choice(np.where(y == 0)[0], 8, replace=False), rng.choice(np.where(y == 1)[0], 8,
                                                                                            replace=False)]
                rows, y = [rows[i] for i in pick], y[pick]
            Xtr = X[[idx[r["id"]] for r in rows]]
            for seed in [int(s) for s in a.seeds.split(",")][: 1 if a.smoke else None]:
                tag = f"{bb}_{arm}_s{seed}" + ("_smoke" if a.smoke else "")
                t0 = time.time()
                h = K.fit_head(Xtr, y, [r["persons"] for r in rows], seed, folds=2 if a.smoke else 5)
                ids = list(idx)
                s = K.head_score(h, X[[idx[i] for i in ids]])
                S = dict(zip(ids, s.tolist()))
                (K.PN1 / "tier0" / bb).mkdir(parents=True, exist_ok=True)
                np.savez(K.PN1 / "tier0" / bb / f"{arm}_s{seed}{'_smoke' if a.smoke else ''}.npz", id=np.array(ids),
                         logit=s.astype(np.float32))
                np.savez(K.PN1 / "tier0" / bb / f"{arm}_s{seed}{'_smoke' if a.smoke else ''}_head.npz",
                         coef=h["model"].coef_.ravel(), intercept=h["model"].intercept_, mean=h["scaler"].mean_,
                         scale=h["scaler"].scale_, C=h["C"])
                R = RD.all_reads(S, P, 0.0, (cues, names))
                R["strata"] = strata
                R["marks"] = RD.marks_tier0(R)
                R["head"] = dict(C=h["C"], cv=h["cv"], inner_dropped_rows=h["inner_dropped_rows"], n_train=len(rows),
                                 n_unique=len({r["id"] for r in rows}), n_attack=int(y.sum()),
                                 n_negative=int((y == 0).sum()), seconds=round(time.time() - t0, 1),
                                 train_kinds={k: sum(1 for r in rows if f"{r['rung']}{r['strength']}" == k)
                                              for k in sorted({f"{r['rung']}{r['strength']}" for r in rows})})
                K.dump(R, out_dir / f"{tag}.json")
                print("DONE", tag, f"{time.time() - t0:.0f} s", flush=True)
    K.dump(summary, out_dir / ("tier0_summary_smoke.json" if a.smoke else "tier0_summary.json"))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
