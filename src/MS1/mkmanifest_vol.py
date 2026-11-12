"""MS1 data-volume control arm SbV (lead ruling M2, 12 Nov): train_Sb oversampled to SbM3's 13,414 rows.

Rule: per Sb stratum s (feret|native, feret|s61, frgc|native, frgc|s61; balanced, n_s rows per label), the per-label
target t_s = n_s * 6707 / 4193 rounded by largest remainder so that sum_s t_s = 6707 (13,414 rows, labels equal in every
stratum). Within each stratum and label, every row of train_Sb (repeats included, so Sb's relative weights are kept)
is repeated floor(k) or ceil(k) times, k = t_s / n_s, the ceil rows chosen by numpy.random.default_rng(20261131 + 10 *
stratum index + label). No new image.
  python3 -I mkmanifest_vol.py -> OUT/manifests/train_SbV.csv, experiments/MS1.../manifest_SbV_summary.json
"""
import collections
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402

import ms1common as C  # noqa: E402
import mkmanifest as MK  # noqa: E402

TARGET = 13414


def main():
    assert C.sha(MK.SB) == MK.SB_SHA
    sb = list(csv.DictReader(open(MK.SB)))
    strata = sorted({(r["db"], r["hist"]) for r in sb})
    n = {st: sum(1 for r in sb if (r["db"], r["hist"]) == st and r["label"] == "0") for st in strata}
    for st in strata:
        assert n[st] == sum(1 for r in sb if (r["db"], r["hist"]) == st and r["label"] == "1")
    half = TARGET // 2
    tot = sum(n.values())
    q = {st: n[st] * half / tot for st in strata}
    t = {st: int(np.floor(v)) for st, v in q.items()}
    for st in sorted(strata, key=lambda s: -(q[s] - t[s]))[: half - sum(t.values())]:
        t[st] += 1
    out, rep = [], {}
    for i, st in enumerate(strata):
        for lab in ("0", "1"):
            rs = [r for r in sb if (r["db"], r["hist"]) == st and r["label"] == lab]
            base, rem = divmod(t[st], len(rs))
            extra = set(np.random.default_rng(20261131 + 10 * i + int(lab)).permutation(len(rs))[:rem].tolist())
            for j, r in enumerate(rs):
                out += [r] * (base + (1 if j in extra else 0))
        rep["|".join(st)] = dict(sb_rows_per_label=n[st], target_per_label=t[st])
    assert len(out) == TARGET
    mf = C.OUT / "manifests/train_SbV.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MK.TRCOLS)
        w.writeheader()
        w.writerows(out)
    att = [r for r in out if r["label"] == "1"]
    summ = dict(rows=len(out), unique=len({r["id"] for r in out}), strata=rep, sha256=C.sha(mf),
                splice_share_of_attack_rows=sum(r["kind"] == "lad_S4" for r in att) / len(att),
                by_kind=dict(collections.Counter(r["kind"] for r in out)))
    json.dump(summ, open(C.RES / "manifest_SbV_summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "by_kind"}, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
