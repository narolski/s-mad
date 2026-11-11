"""SM1 amendment A12 item 5 (post hoc, H-new-4): every arm refitted with the release (FZ1) head recipe.

Recipe as src/FZ1/fz1_heads.py (MADation FE header): Linear(768, 2) on F.normalize(feature), BCEWithLogitsLoss on
one-hot targets (class 1 = bona fide), AdamW lr 1e-2, betas (0.9, 0.999), wd 0.05, the release's scheduler
(ConstantLR warm-up 5 epochs, then CosineAnnealingWarmRestarts T_0 5, T_mult 2, eta_min = lr) stepped per epoch,
40 epochs, batch 256, drop_last, clip_grad_norm 5. Deviation (registered): no horizontal flip, because flipped
features of our arms do not exist (the flip draw is still made, so the shuffles match the FZ1 code). No class
balancing (the release has none). Same compositions and seeds as Part 3 (compose.py, 401 to 405).
Logit = z_attack - z_bona (so >= 0 is the own rule, as for the Part 3 heads).

CPU, 2 threads (DGX rule).
  python3 -I heads_fz1.py [--arms ...] [--seeds ...] -> OUT/heads_fz1/<arm>_s<seed>.npz (id, logit, W (2, 768), b)
"""
import argparse
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import heads as H  # noqa: E402


def sched(opt, lr):
    import torch
    cos = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer=opt, T_0=5, T_mult=2, eta_min=lr)
    warm = torch.optim.lr_scheduler.ConstantLR(opt, factor=1, total_iters=5)
    return torch.optim.lr_scheduler.SequentialLR(opt, schedulers=[warm, cos], milestones=[5])


def train(gen, mor, seed, epochs=40, bs=256, lr=1e-2, wd=0.05, max_norm=5.0):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    torch.manual_seed(seed)
    X = np.concatenate([gen, mor]).astype(np.float32)
    bona = np.concatenate([np.ones(len(gen)), np.zeros(len(mor))]).astype(np.int64)
    head = nn.Linear(X.shape[1], 2)
    opt = torch.optim.AdamW([{"params": head.parameters()}], betas=(0.9, 0.999), lr=lr, weight_decay=wd)
    sch = sched(opt, lr)
    lossf = nn.BCEWithLogitsLoss()
    g = torch.Generator().manual_seed(seed)
    n = len(X)
    tgt = F.one_hot(torch.from_numpy(bona), 2).float()
    Xt = F.normalize(torch.from_numpy(X), dim=-1)
    for _ in range(epochs):
        perm = torch.randperm(n, generator=g)
        _flip = torch.rand(n, generator=g) < 0.5          # drawn, not used (no flipped features)
        for k in range(n // bs):
            ii = perm[k * bs:(k + 1) * bs]
            loss = lossf(head(Xt[ii]), tgt[ii])
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(head.parameters(), max_norm=max_norm, norm_type=2)
            opt.step()
        sch.step()
    W = head.weight.detach().numpy().astype(np.float32)
    b = head.bias.detach().numpy().astype(np.float32)
    with torch.no_grad():
        z = head(Xt)
        acc = float((((z[:, 0] - z[:, 1]) > 0).numpy().astype(int) == (1 - bona)).mean())
    return W, b, dict(n_gen=len(gen), n_morph=len(mor), train_acc=round(acc, 4))


def logit(F_, W, b):
    Fn = F_ / np.maximum(np.linalg.norm(F_, axis=1, keepdims=True), 1e-12)
    z = Fn @ W.T + b
    return (z[:, 0] - z[:, 1]).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(H.ARMS))
    ap.add_argument("--seeds", default="401,402,403,404,405")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    import torch
    torch.set_num_threads(2)
    test = H.Bank(H.TESTS)
    ids = np.array(sorted(test.pos, key=test.pos.get))
    bank = H.Bank(H.TRAIN)
    od = K.OUT / "heads_fz1"
    od.mkdir(parents=True, exist_ok=True)
    log = {}
    for arm in a.arms.split(","):
        for s in map(int, a.seeds.split(",")):
            c = json.load(open(K.OUT / f"compose/{arm}_s{s}.json"))
            t0 = time.time()
            W, b, info = train(bank.get(c["genuine"]), bank.get(c["morph"]), s)
            np.savez(od / f"{arm}_s{s}.npz", id=ids, logit=logit(test.F, W, b), W=W, b=b)
            info["seconds"] = round(time.time() - t0, 1)
            log[f"{arm}_s{s}"] = info
            print(arm, s, json.dumps(info), flush=True)
    lp = od / "heads_log.json"
    old = json.load(open(lp)) if lp.exists() else {}
    old.update(log)
    json.dump(old, open(lp, "w"), indent=1)


if __name__ == "__main__":
    main()
