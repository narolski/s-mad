"""AB1 follow-up arms (SbFM, Sbx): ADVERSARY stage-1a floors printed beside the registered reads (printed only; the
registered verdicts are unchanged). Contrasts covered by stage 1a (bffacb5): lcomb, test_cv_R4_vs_R2w, test_cv_R4_vs_R3,
test_fm_R4_vs_R2w, test_fm_R4_vs_R3. For each network (arm and its AB1 comparators Sb, A, B at the same seed):
src/adversary/check.exceeds against the all-cue ADV floor and against the nuisance floor; for arm against Sb,
diff_within_floor_quintiles of the nuisance floor's held-out score. Scores: the networks' fit-job scores (the readers'
loaders, provenance-checked).
  python3 -I ab1_advfloor.py --arm SbFM|Sbx --out OUT.json
  python3 -I ab1_advfloor.py --selftest --out TEST.json   (random scores for every floor row; code path only)"""
import argparse
import importlib.util
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ADV = HERE.parent / "adversary"
sys.path.insert(0, str(ADV))
import check  # noqa: E402

CONTRASTS = ("lcomb", "test_cv_R4_vs_R2w", "test_cv_R4_vs_R3", "test_fm_R4_vs_R2w", "test_fm_R4_vs_R3")
SEEDS = (408, 409, 410, 411, 412)


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("SbFM", "Sbx"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    R = dict(arm=a.arm, selftest=a.selftest, contrasts=CONTRASTS, networks={}, arm_vs_Sb_quintiles={})
    if a.selftest:
        import csv
        ids = set()
        for c in CONTRASTS:
            ids |= {r["id"] for r in csv.DictReader(open(check.FDIR / f"{c}_heldout.csv"))}
        rng = np.random.default_rng(0)
        nets = {(arm, s): {i: float(rng.normal()) for i in ids} for arm in ("ARM", "Sb") for s in SEEDS[:1]}
        armname = "ARM"
    else:
        A = _mod("ab1_read", HERE / "ab1_read.py")
        if a.arm == "SbFM":
            F = _mod("ab1fm_read", HERE / "ab1fm_read.py")
            load_arm = lambda s: F.load_fm(pathlib.Path("/mnt/t7/smad_next/AB1/fm/results") / f"AB1FM_SbFM_s{s}.tar")[0]
        else:
            X = _mod("ab1x_read", HERE / "ab1x_read.py")
            load_arm = lambda s: X.load_x(pathlib.Path("/mnt/t7/smad_next/AB1/x/results") / f"AB1X_Sbx_s{s}.tar")[0]
        nets = {}
        for s in SEEDS:
            x = load_arm(s)
            if x is not None:
                nets[(a.arm, s)] = x
            for arm in ("Sb", "A", "B"):
                y = A.load(pathlib.Path("/mnt/t7/smad_next/AB1/results") / f"AB1_{arm}_s{s}.tar", "AB1", arm)[0]
                if y is not None:
                    nets[(arm, s)] = y
        armname = a.arm
    for (arm, s), sc in nets.items():
        R["networks"][f"{arm}_s{s}"] = {c: dict(all=check.exceeds(c, sc), nuisance=check.exceeds(c, sc, floor="nuisance"))
                                         for c in CONTRASTS}
    for s in SEEDS:
        if (armname, s) in nets and ("Sb", s) in nets:
            R["arm_vs_Sb_quintiles"][str(s)] = {c: check.diff_within_floor_quintiles(c, nets[(armname, s)], nets[("Sb", s)],
                                                                                    floor="nuisance") for c in CONTRASTS}
    json.dump(R, open(a.out, "w"), indent=1, default=lambda o: o.item() if isinstance(o, np.generic) else str(o))
    print("networks:", sorted(R["networks"]), "| quintile seeds:", sorted(R["arm_vs_Sb_quintiles"]))


if __name__ == "__main__":
    main()
