"""Signal isolation by paired differences (PD1), GAN family: first small end-to-end pass.

CLIP pooled, set G, fold 0 of the registered 5-fold split by block (seed 401) held out: Q1 shares and projection
AUCs on the held-out hosts; Q3 one-person head (x2 vs x1 of the same host) and two-person head (x3 vs x1) trained on
the other four folds, scored on the held-out fold. Point estimates only (intervals come with the full run).
Run: nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/gan/pd1_first.py
"""
import json, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pd1_lib as L


def main():
    F = L.load_feats("clip", "pool", ["G"])
    H = [h for h in L.hosts() if h["set"] == "G"]
    fo = L.folds([h["cluster"] for h in H], 5, 401)
    tr = [h for h in H if fo[h["cluster"]] != 0]
    te = [h for h in H if fo[h["cluster"]] == 0]
    res = dict(n_train_hosts=len(tr), n_test_hosts=len(te), n_test_blocks=len({h["cluster"] for h in te}))
    steps = {"pipeline x0->x1": ("x0", "x1"), "same-person mixing x1->x2": ("x1", "x2"),
             "second identity x2->x3": ("x2", "x3"), "whole morph x1->x3": ("x1", "x3"), "camera to morph x0->x3": ("x0", "x3")}
    for nm, (a, b) in steps.items():
        u = L.unit(np.mean([F[h[b]] - F[h[a]] for h in tr], 0))
        p = np.array([(F[h[b]] - F[h[a]]) @ u for h in te])
        ia, ib = sorted({h[a] for h in te}), sorted({h[b] for h in te})
        res[f"Q1 {nm}"] = dict(share=float(np.mean(p > 0)), proj_auc=L.auc([F[i] @ u for i in ib], [F[i] @ u for i in ia]))
    for head, pos in (("one-person head (x2 vs x1)", "x2"), ("two-person head (x3 vs x1)", "x3")):
        pairs = [(h[pos], h["x1"]) for h in tr]
        groups = [h["cluster"] for h in tr]
        imgs = sorted({i for pr in pairs for i in pr})
        hd, C = L.fit_head(F, pairs, groups, imgs, 401)
        s = {r: {i: float(hd.score(F[i][None])[0]) for i in sorted({h[r] for h in te})} for r in ("x0", "x1", "x2", "x3")}
        A = lambda p, n: L.auc(list(s[p].values()), list(s[n].values()))
        res[f"Q3 {head}"] = dict(C=C, auc_x3_vs_x1=A("x3", "x1"), auc_x3_vs_x0=A("x3", "x0"), auc_x3_vs_x2=A("x3", "x2"),
                                 auc_x2_vs_x1=A("x2", "x1"), auc_x1_vs_x0=A("x1", "x0"),
                                 paired_win_x3_over_x1=float(np.mean([s["x3"][h["x3"]] > s["x1"][h["x1"]] for h in te])))
    print(json.dumps(res, indent=1))
    L.dump(res, "first_pass_clip_pool_fold0.json")


if __name__ == "__main__":
    main()
