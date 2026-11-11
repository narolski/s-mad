"""FZ1 P1: post hoc re-read of the released MADation FE / FS (and full, reference) scores on A43, R1, benchmarks and
StyleGAN3 sets. No image is read; only existing per-image score files.
Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/FZ1/fz1_p1.py [--smoke]
"""
import json, sys, pathlib
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fz1_common as K
import fz1_eval as E

SMOKE = "--smoke" in sys.argv
A12 = K.MC / "smadcvpr_runs/A12_scored/A12REL"
NETS = [("FE ViT-L/14", "madation_fe_vitl14", "subject"), ("FE ViT-B/16", "madation_fe_vitb16", "descriptive"),
        ("FS ViT-L/14", "madation_fs_vitl14", "descriptive"), ("FS ViT-B/16", "madation_fs_vitb16", "descriptive"),
        ("full ViT-L/14 (reference)", "madation_vitl14", "reference"), ("full ViT-B/16 (reference)", "madation_vitb16", "reference")]
PREVIEW = {"B20 vs D20": 0.655, "B vs D": 0.852, "C vs D": 0.721, "D vs R0": 0.459, "D20 vs R0": 0.561, "morph vs render": 0.505}


def main():
    ctx = E.Ctx(smoke=SMOKE)
    res = {}
    for lab, net, role in NETS:
        z = np.load(K.A43 / "a43_out/a43" / net / "rel/scores_a43.npz", allow_pickle=False)
        assert str(z["manifest_sha256"]) == K.MAN_SHA and list(z["id"]) == [r["id"] for r in ctx.rows]
        s43 = z["score_noTTA"].astype(float)
        ze = np.load(A12 / net / "scores_eval.npz", allow_pickle=False)
        assert str(ze["manifest_sha256"]) == K.EVAL_SHA
        sev = dict(zip(ze["id"].tolist(), ze["score_noTTA"].astype(float)))
        cons = float(np.max(np.abs(s43[ctx.g["R0"]] - np.array([sev[ctx.rows[i]["id"]] for i in ctx.g["R0"]]))))
        zh = np.load(A12 / net / "scores_h3sg3.npz", allow_pickle=False)
        ssg = dict(zip(zh["id"].tolist(), zh["score_noTTA"].astype(float)))
        zx = np.load(f"/mnt/t7/smad_heldout/a41g/a41g_out/x4/{net}/rel/scores_a37spread.npz", allow_pickle=False)
        ssg.update(dict(zip(zx["id"].tolist(), zx["score_noTTA"].astype(float))))
        out = E.evaluate(ctx, s43, sev, ssg)
        out["role"], out["R0_consistency_maxabs"] = role, cons
        res[lab] = out
        a = out["a43"]
        print(f"== {lab} ({role}); R0 a43 vs eval max|d| {cons:.2e}")
        print("   " + " | ".join(f"{k} {E.fmt(v)}" for k, v in a.items()))
        print("   SG3: " + " | ".join(f"{k} {E.fmt(v)}" for k, v in out["sg3"].items()))
        f = out["flag_R0_R1"]["thr_full_mordiff"]
        print(f"   flag R0->R1 (full MorDIFF EER thr): {100*f['flag_R0']:.1f}% -> {100*f['flag_R1']:.1f}% "
              f"({f['change_pts']:+.1f} [{f['change_ci_pts'][0]:+.1f}, {f['change_ci_pts'][1]:+.1f}])")
        print(f"   neutral>smiling frll_bona {out['neutral_above_smiling']['frll_bona']}")
        print("   bench: " + " | ".join(f"{c} nat {v['native']['eer']:.1f} E7 {v['E7']['eer']:.1f}" for c, v in out["bench"].items()))
    fe = res["FE ViT-L/14"]
    rep = {k: (round(fe["a43"][k]["auc"], 3) if k in fe["a43"] else round(fe["sg3"][k]["auc"], 3)) for k in PREVIEW}
    res["_preview_check"] = {"preview": PREVIEW, "recomputed": rep, "all_equal_3dp": all(abs(rep[k] - v) < 5e-4 + 1e-9 for k, v in PREVIEW.items())}
    print("preview check", res["_preview_check"])
    if not SMOKE:
        json.dump(res, open(K.OUT / "p1_release_reread.json", "w"), indent=1)


if __name__ == "__main__":
    main()
