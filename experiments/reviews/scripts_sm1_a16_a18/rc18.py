import sys, hashlib, tarfile, io, json, numpy as np
sys.path.insert(0, "/home/narolski/smad-next/src/SM1")
import hn2_incr as I, sm1_common as K
D = K.OUT / "results_rented/hn2"
scores = {}
for s in (401, 402, 403):
    f = D / f"HN2_RS_s{s}.tar"
    h = hashlib.sha256(open(f, "rb").read()).hexdigest()
    assert h == open(str(f)+".sha256").read().split()[0]
    with tarfile.open(f) as t:
        m = [x for x in t.getmembers() if x.name.endswith("hn2test/scores_eval.npz")][0]
        z = np.load(io.BytesIO(t.extractfile(m).read()))
        z2 = np.load(D / f"HN2_RS_s{s}/hn2test/scores_eval.npz")
        assert (z["score_noTTA"] == z2["score_noTTA"]).all()
        mm = [x for x in t.getmembers() if x.name.endswith("metrics.json")][0]
        met = json.load(t.extractfile(mm))
    p = np.clip(z["score_noTTA"].astype(float), 1e-7, 1-1e-7)
    scores[s] = dict(zip([str(i) for i in z["id"]], np.log(p/(1-p))))
    print(s, h[:12], "train auc", met["train"]["auc_vs_training_labels"], "finite", np.isfinite(z["score_noTTA"]).all(), "n", len(p), "clipped", (p<=1e-7).sum()+(p>=1-1e-7).sum())
for drop in (False, True):
    rows = I.test_rows(drop_flagged=drop)
    per = {s: I.incremental(rows, scores[s]) for s in scores}
    for s, o in per.items():
        print(drop, s, {k: round(o[k][0], 4) for k in ("F","F_plus","Fimg","Fimg_plus","score_raw_auc","dAUC_over_F","dAUC_over_Fimg","score_only")})
    sm = I.summarise([per[401], per[402]])
    print("2seed", drop, sm["dAUC_over_F"], sm["dAUC_over_Fimg"], I.verdict(sm["dAUC_over_F"]))
    print("3seed", drop, I.summarise(list(per.values()))["dAUC_over_F"])
    print(o["_n"])
