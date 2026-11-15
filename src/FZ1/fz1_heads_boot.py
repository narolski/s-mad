"""FZ1 post hoc addendum A1 (c): five MADation-FE-recipe heads, each trained on a bootstrap resample of the 40,000 SMDD
images (resample seeds 401-405; initialisation / batching seed 401), on the cached frozen CLIP-L/14 features; same
evaluation as P3. Registered in experiments/FZ1/prereg.md ("Post hoc addendum A1").
Run: OMP_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/FZ1/fz1_heads_boot.py [--smoke]
"""
import csv, json, pathlib, sys
import numpy as np
import torch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fz1_common as K
import fz1_eval as E
import fz1_heads as HD


def main():
    smoke = "--smoke" in sys.argv
    torch.set_num_threads(2)
    ids, X = HD.load("smdd")
    idsf, Xf = HD.load("smdd_flip")
    assert ids == idsf
    lab = {r["path"]: int(r["label"]) for r in csv.DictReader(open(K.TRAIN)) if r["source"] == "smdd"}
    bona = 1 - np.array([lab[i] for i in ids])
    ctx = E.Ctx(smoke=smoke)
    i43, X43 = HD.load("a43")
    iev, Xev = HD.load("eval")
    isg, Xsg = HD.load("sg3")
    rel = np.load(K.A43 / "a43_out/a43/madation_fe_vitl14/rel/scores_a43.npz", allow_pickle=False)["score_noTTA"].astype(float)
    res, scores = {}, {}
    for rs in ((401,) if smoke else (401, 402, 403, 404, 405)):
        idx = np.random.default_rng(rs).integers(0, len(ids), len(ids))
        head, lrs, losses = HD.train_head(X[idx], Xf[idx], bona[idx], 401, epochs=2 if smoke else 40)
        s43 = HD.score(head, X43)
        out = E.evaluate(ctx, s43, dict(zip(iev, HD.score(head, Xev))), dict(zip(isg, HD.score(head, Xsg))))
        out["train"] = {"resample_seed": rs, "unique_images": int(len(np.unique(idx))), "morph_share": float(1 - bona[idx].mean()),
                        "loss_first": losses[0], "loss_last": losses[-1]}
        out["spearman_vs_release_FE_L14_a43"] = HD.spearman(s43, rel)
        res[f"boot{rs}"] = out
        scores[f"boot{rs}_a43"] = s43
        a = out["a43"]
        print(f"boot {rs}: " + " | ".join(f"{k} {E.fmt(v)}" for k, v in a.items() if k in ("B vs D", "B20 vs D20", "B20 vs C20", "C20 vs D20", "D vs R0")), flush=True)
    bd = {s: r["a43"]["B vs D"]["auc"] for s, r in res.items()}
    dr = {s: r["a43"]["D vs R0"]["auc"] for s, r in res.items()}
    res["_rule_descriptive"] = {"B_vs_D": bd, "D_vs_R0": dr, "meeting_prediction": sum(bd[s] >= 0.75 and dr[s] <= 0.60 for s in bd),
                                "B_vs_D_ge_0.70": sum(bd[s] >= 0.70 for s in bd)}
    print(res["_rule_descriptive"])
    if not smoke:
        json.dump(res, open(K.OUT / "addendum_heads_boot.json", "w"), indent=1)
        np.savez(K.BIG / "heads" / "scores_a43_boot.npz", id=np.array(i43), **scores)


if __name__ == "__main__":
    main()
