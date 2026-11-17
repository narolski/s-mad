"""cmp_npz.py REFDIR TESTDIR SUFFIX: compare logit_noTTA/score/score_noTTA on common ids (scores_rel_*SUFFIX.npz)."""
import sys, pathlib, numpy as np
ref, tst, sfx = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
worst = 0.0
for f in sorted(tst.glob(f"scores_rel_*{sfx}.npz")):
    g = ref / f.name
    if not g.exists():
        print("no ref", f.name); continue
    a, b = np.load(f), np.load(g)
    ia = {i: k for k, i in enumerate(a["id"].tolist())}; ib = {i: k for k, i in enumerate(b["id"].tolist())}
    com = [i for i in ia if i in ib]
    out = [f.name, f"n={len(com)}/{len(ia)}/{len(ib)}", str(a["det"]), str(b["det"])]
    for key in ("logit_noTTA", "score_noTTA", "score"):
        x = a[key][[ia[i] for i in com]]; y = b[key][[ib[i] for i in com]]
        d = float(np.abs(x.astype(np.float64) - y).max()); out.append(f"{key} maxabs={d:.2e}")
        if key == "logit_noTTA": worst = max(worst, d)
    print(" ".join(out))
print("WORST_LOGIT_MAXABS", f"{worst:.3e}")
