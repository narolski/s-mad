"""FZ1 P3: five SMDD-only linear heads (MADation FE head recipe) on cached frozen CLIP-L/14 features (MADation input),
seeds 401-405, last epoch; scored on A43, R1, the benchmarks and the StyleGAN3 sets.

Recipe (baselines/MADation/src: train.sh ViT-L/14 MAD_training_only_header; training/trainer.py; training/losses.py
BinaryCrossEntropyHeader; training/scheduler.py; data/loaders.py FaceDataset): Linear(768, 2) on F.normalize(feature),
BCEWithLogitsLoss on one-hot targets (class 1 = bona fide), AdamW lr 1e-2, betas (0.9, 0.999), wd 0.05, the release's
scheduler stepped per epoch, 40 epochs, global batch 256 (8 x 32), drop_last, clip_grad_norm 5, RandomHorizontalFlip
p 0.5 (cached flipped feature). Score = softmax[:, 0] (attack) = sigmoid(z0 - z1).
Run: OMP_NUM_THREADS=4 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/FZ1/fz1_heads.py [--smoke]
"""
import csv, json, pathlib, sys
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fz1_common as K
import fz1_eval as E

SEEDS = (401, 402, 403, 404, 405)
FEAT = K.BIG / "feats" / "clip_mad"


def get_scheduler(opt, num_warmup_epochs=5, T_0=5, T_mult=2, eta_min=1e-2):
    """training/scheduler.py get_scheduler('cosine', warmup=True, warmup_factor=1), verbatim in effect."""
    cos = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer=opt, T_0=T_0, T_mult=T_mult, eta_min=eta_min)
    warm = torch.optim.lr_scheduler.ConstantLR(opt, factor=1, total_iters=num_warmup_epochs)
    return torch.optim.lr_scheduler.SequentialLR(opt, schedulers=[warm, cos], milestones=[num_warmup_epochs])


def train_head(X, Xf, bona, seed, epochs=40, bs=256, lr=1e-2, wd=0.05, max_norm=5.0):
    torch.manual_seed(seed)
    head = nn.Linear(X.shape[1], 2)
    opt = torch.optim.AdamW([{"params": head.parameters()}], betas=(0.9, 0.999), lr=lr, weight_decay=wd)
    sch = get_scheduler(opt, eta_min=lr)
    lossf = nn.BCEWithLogitsLoss()
    g = torch.Generator().manual_seed(seed)
    n = len(X)
    tgt = F.one_hot(torch.from_numpy(bona).long(), 2).float()
    Xt, Xft = F.normalize(torch.from_numpy(X), dim=-1), F.normalize(torch.from_numpy(Xf), dim=-1)
    lrs, losses = [], []
    for ep in range(epochs):
        perm = torch.randperm(n, generator=g)
        flip = torch.rand(n, generator=g) < 0.5
        tot = 0.0
        for k in range(n // bs):
            ii = perm[k * bs:(k + 1) * bs]
            x = torch.where(flip[ii, None], Xft[ii], Xt[ii])
            loss = lossf(head(x), tgt[ii])
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(head.parameters(), max_norm=max_norm, norm_type=2)
            opt.step()
            tot += loss.item()
        lrs.append(opt.param_groups[0]["lr"])
        sch.step()
        losses.append(tot / (n // bs))
    return head, lrs, losses


def score(head, X):
    with torch.no_grad():
        z = head(F.normalize(torch.from_numpy(X), dim=-1))
        return torch.sigmoid(z[:, 0] - z[:, 1]).numpy().astype(np.float64)


def load(name):
    z = np.load(FEAT / f"{name}.npz", allow_pickle=False)
    return z["id"].tolist(), z["feat"].astype(np.float32)


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    smoke = "--smoke" in sys.argv
    torch.set_num_threads(4)
    ids, X = load("smdd")
    idsf, Xf = load("smdd_flip")
    assert ids == idsf
    lab = {r["path"]: int(r["label"]) for r in csv.DictReader(open(K.TRAIN)) if r["source"] == "smdd"}
    morph = np.array([lab[i] for i in ids])
    assert len(ids) == 40000 and morph.sum() == 15000 and all(i.startswith("train/smdd/") for i in ids)
    bona = 1 - morph                       # MADation: 'bonafide' -> 1, attack -> 0
    ctx = E.Ctx(smoke=smoke)
    i43, X43 = load("a43")
    iev, Xev = load("eval")
    isg, Xsg = load("sg3")
    assert i43 == [r["id"] for r in ctx.rows]
    rel = np.load(K.A43 / "a43_out/a43/madation_fe_vitl14/rel/scores_a43.npz", allow_pickle=False)["score_noTTA"].astype(float)
    res, scores = {}, {}
    # end-to-end check: the released FE ViT-L/14 head on our fp32 features vs the stored release scores (P1)
    from safetensors.torch import load_file
    import fz1_feats as FF
    rh = load_file(str(FF.FE_REL))
    relhead = nn.Linear(768, 2)
    relhead.load_state_dict({"weight": rh["head.weight"].float(), "bias": rh["head.bias"].float()})
    r43 = score(relhead, X43)
    rchk = E.evaluate(ctx, r43, dict(zip(iev, score(relhead, Xev))), dict(zip(isg, score(relhead, Xsg))))
    p1 = json.load(open(K.OUT / "p1_release_reread.json"))["FE ViT-L/14"]
    dauc = {k: rchk["a43"][k]["auc"] - p1["a43"][k]["auc"] for k in rchk["a43"]}
    dauc.update({f"SG3 {k}": rchk["sg3"][k]["auc"] - p1["sg3"][k]["auc"] for k in rchk["sg3"]})
    res["_release_head_on_our_features"] = {"score_max_abs_a43": float(np.abs(r43 - rel).max()), "score_mean_abs_a43": float(np.abs(r43 - rel).mean()),
                                            "auc_minus_stored": dauc, "max_abs_auc_diff": float(max(abs(v) for v in dauc.values())),
                                            "bench_eer_minus_stored": {c: [rchk["bench"][c]["native"]["eer"] - p1["bench"][c]["native"]["eer"],
                                                                           rchk["bench"][c]["E7"]["eer"] - p1["bench"][c]["E7"]["eer"]] for c in rchk["bench"]}}
    print("release head on our features:", json.dumps(res["_release_head_on_our_features"])[:600])
    hdir = K.BIG / "heads"
    hdir.mkdir(parents=True, exist_ok=True)
    for seed in (SEEDS[:1] if smoke else SEEDS):
        head, lrs, losses = train_head(X, Xf, bona, seed, epochs=2 if smoke else 40)
        s43, sev, ssg = score(head, X43), dict(zip(iev, score(head, Xev))), dict(zip(isg, score(head, Xsg)))
        str_ = score(head, X)
        out = E.evaluate(ctx, s43, sev, ssg)
        out["train"] = {"lr_per_epoch_unique": sorted(set(round(x, 8) for x in lrs)), "loss_first": losses[0], "loss_last": losses[-1],
                        "train_auc_morph_vs_bona": K.auc(str_[morph == 1], str_[morph == 0])}
        out["spearman_vs_release_FE_L14_a43"] = spearman(s43, rel)
        res[str(seed)] = out
        scores[f"s{seed}_a43"] = s43
        if not smoke:
            torch.save(head.state_dict(), hdir / f"head_s{seed}.pt")
        a = out["a43"]
        print(f"seed {seed}: train AUC {out['train']['train_auc_morph_vs_bona']:.3f} loss {losses[0]:.4f}->{losses[-1]:.4f} lr {out['train']['lr_per_epoch_unique']}")
        print("   " + " | ".join(f"{k} {E.fmt(v)}" for k, v in a.items()))
        print("   SG3: " + " | ".join(f"{k} {E.fmt(v)}" for k, v in out["sg3"].items()))
        print("   bench: " + " | ".join(f"{c} nat {v['native']['eer']:.1f} E7 {v['E7']['eer']:.1f}" for c, v in out["bench"].items()))
        f = out["flag_R0_R1"]["thr_full_mordiff"]
        print(f"   flag R0->R1 {100*f['flag_R0']:.1f}% -> {100*f['flag_R1']:.1f}% ({f['change_pts']:+.1f}); neutral>smiling "
              f"{out['neutral_above_smiling']['frll_bona']['value']:.3f}; spearman vs release {out['spearman_vs_release_FE_L14_a43']:.3f}")
    bd = {s: r["a43"]["B vs D"]["auc"] for s, r in res.items()}
    dr = {s: r["a43"]["D vs R0"]["auc"] for s, r in res.items()}
    n_pred = sum(bd[s] >= 0.75 and dr[s] <= 0.60 for s in bd)
    n_070 = sum(bd[s] >= 0.70 for s in bd)
    verdict = "supported" if n_pred >= 4 else ("falsified" if n_070 < 3 else "neither supported nor falsified")
    res["_prediction"] = {"B_vs_D": bd, "D_vs_R0": dr, "seeds_meeting_prediction": n_pred, "seeds_B_vs_D_ge_0.70": n_070,
                          "verdict": verdict}
    print(res["_prediction"])
    if not smoke:
        json.dump(res, open(K.OUT / "p3_heads.json", "w"), indent=1)
        np.savez(K.BIG / "heads" / "scores_a43.npz", id=np.array(i43), **scores)


if __name__ == "__main__":
    main()
