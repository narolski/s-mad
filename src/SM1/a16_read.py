"""SM1 amendment A16 reader (H-n1, registered aafd46b; platform D1): saved ViT-B/16 a, e, f on DG1 rungs.

Input: OUT/results_rented/dev16/SM1E_<arm>_s<seed>.tar (sha256 checked, extracted): <T>/scores_audit.npz (ids of
dev_a16/sm1_dev16_eval.csv; logit of the no-TTA score), <T>/check.json (reproduction check, must pass).
Host bootstrap (536 hosts), B = 10,000, seed 20261111; 2-seed means.
Readings: AUC FRESH1_20 over REC20, NOISES20 over REC20, NOISEX20 over NOISES20, SEMX20 over SEMS20; MIR20 over REC20
descriptive. H-n1 (arm a): supported if FRESH1 and NOISES over REC ≥ 0.70 and NOISEX over NOISES and SEMX over SEMS
≤ 0.60; falsified if FRESH1 and NOISES over REC ≤ 0.55 and SEMX over SEMS ≥ 0.70; otherwise undecided. e about 0.5
throughout is reported.

  python3 -I a16_read.py -> RES/a16_read.json
"""
import csv
import hashlib
import json
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import sm1_stats as S  # noqa: E402

D = K.OUT / "results_rented/dev16"
CONTRASTS = (("FRESH1_20", "REC20"), ("NOISES20", "REC20"), ("NOISEX20", "NOISES20"), ("SEMX20", "SEMS20"),
             ("MIR20", "REC20"))


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    rows = list(csv.DictReader(open(K.OUT / "dev_a16/sm1_dev16_eval.csv")))
    fam, host = {}, {}
    for r in rows:
        fam.setdefault(r["family"], []).append(r["id"])
        host[r["id"]] = r["variant"]
    hosts = sorted(set(host.values()))
    hp = {h: i for i, h in enumerate(hosts)}
    C = np.random.default_rng(K.SEED).multinomial(len(hosts), np.full(len(hosts), 1 / len(hosts)), size=10000).astype(float)
    W = lambda ids: C[:, [hp[host[i]] for i in ids]]  # noqa: E731
    per, checks = {}, {}
    for f in sorted(D.glob("SM1E_*.tar")):
        assert hashlib.sha256(open(f, "rb").read()).hexdigest() == open(str(f) + ".sha256").read().split()[0], f
        T = f.stem
        if not (D / T).exists():
            with tarfile.open(f) as t:
                t.extractall(D)
        chk = json.load(open(D / T / "check.json"))
        assert chk["passed"], T
        checks[T] = chk["max_abs_score_diff"]
        z = np.load(D / T / "scores_audit.npz")
        p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1 - 1e-7)
        zi = dict(zip([str(i) for i in z["id"]], np.log(p / (1 - p))))
        g = lambda ids: np.array([zi[i] for i in ids])  # noqa: E731
        m = {}
        for a, b in CONTRASTS:
            pos, neg = fam[a], fam[b]
            m[f"{a}_over_{b}"] = (float(S.wauc(g(pos), g(neg), np.ones((1, len(pos))), np.ones((1, len(neg))))[0]),
                                  S.wauc(g(pos), g(neg), W(pos), W(neg)))
        per.setdefault(T.split("_")[1], []).append(m)
    out = dict(check_max_abs=checks)
    for arm, lst in per.items():
        out[arm] = {k: dict(mean=round(float(np.mean([m[k][0] for m in lst])), 4), seeds=[round(m[k][0], 4) for m in lst],
                            ci=[round(x, 4) for x in S.ci(np.mean([m[k][1] for m in lst], 0))]) for k in lst[0]}
    a = out["a"]
    fr, no = a["FRESH1_20_over_REC20"]["mean"], a["NOISES20_over_REC20"]["mean"]
    nx, sx = a["NOISEX20_over_NOISES20"]["mean"], a["SEMX20_over_SEMS20"]["mean"]
    v = ("supported" if fr >= 0.70 and no >= 0.70 and nx <= 0.60 and sx <= 0.60 else
         "falsified" if fr <= 0.55 and no <= 0.55 and sx >= 0.70 else "undecided")
    out["H-n1"] = dict(a=dict(FRESH1_over_REC=fr, NOISES_over_REC=no, NOISEX_over_NOISES=nx, SEMX_over_SEMS=sx), verdict=v)
    json.dump(out, open(K.RES / "a16_read.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
