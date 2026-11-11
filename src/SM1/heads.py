"""SM1 Part 3 heads on frozen CLIP ViT-L/14 features and their scores on every test / audit image.

Features: OUT/feat_athena/<list>.npz (id, feat), merged from the Athena shards (amendment A7: one platform).
Compositions: OUT/compose[/smoke]/<arm>_s<seed>.json (compose.py; the LoRA fits use the same lists).
Head: standardise (train mean / std), Linear(768, 1), class-balanced BCE, AdamW lr 1e-3, wd 1e-4, batch 256,
20 epochs, last epoch; seed -> init and shuffle (compose.py draws the d / e subsets with the same seed). --boot:
training images resampled with replacement (A1.7, descriptive).
Reference: the FE ViT-L/14 release header (Linear(768, 2) on the same normalised features; `--fe-ref`).

  python3 -I heads.py [--arms a,b,...] [--seeds 401,...] [--boot] [--smoke] [--feat-dir D]
  python3 -I heads.py --fe-ref [--feat-dir D]
-> OUT/heads[/smoke]/<arm>_s<seed>[_boot].npz (id, logit over all test + audit images, W, b), heads_log.json
Training runs on the GPU by default (--device cpu for the CPU); the seeded initialisation and shuffles are the same.
"""
import argparse
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

TESTS = ("test_eval", "test_mad22", "test_ar1", "test_ar1h", "audit", "test_eval_jpeg")
TRAIN = ("train_bf", "train_m15k", "train_armb", "train_armbp", "train_armc", "train_armc_halves", "train_armcr",
         "train_armd50", "train_armd500", "train_arme_bfS", "train_arme_cS", "train_arme_hS", "train_armf_jpeg")
ARMS = ("a", "b", "bp", "c", "cr", "d", "e", "f", "d50", "d500", "a256", "dplus")
FEAT = K.OUT / "feat_athena"


def load(name):
    z = np.load(FEAT / f"{name}.npz", allow_pickle=False)
    return np.array([str(i) for i in z["id"]]), z["feat"]


class Bank:
    def __init__(self, names):
        F, self.pos = [], {}
        n0 = 0
        for n in names:
            if not (FEAT / f"{n}.npz").exists():
                continue
            i, f = load(n)
            F.append(f)
            for j, x in enumerate(i):
                assert x not in self.pos, x
                self.pos[x] = n0 + j
            n0 += len(i)
        self.F = np.concatenate(F) if F else np.zeros((0, 768), np.float32)

    def get(self, ids):
        return self.F[[self.pos[x] for x in ids]]


DEV = "cpu"


def train(gen, mor, seed, boot):
    import torch
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed + 1000)
    if boot:
        gen = gen[rng.integers(0, len(gen), len(gen))]
        mor = mor[rng.integers(0, len(mor), len(mor))]
    X = np.concatenate([gen, mor]).astype(np.float32)
    y = np.concatenate([np.zeros(len(gen)), np.ones(len(mor))]).astype(np.float32)
    mu, sd = X.mean(0), X.std(0) + 1e-6
    Xt = torch.from_numpy((X - mu) / sd).to(DEV)
    yt = torch.from_numpy(y).to(DEV)
    w = torch.where(yt == 1, len(y) / (2 * len(mor)), len(y) / (2 * len(gen)))
    lin = torch.nn.Linear(X.shape[1], 1).to(DEV)
    opt = torch.optim.AdamW(lin.parameters(), lr=1e-3, weight_decay=1e-4)
    g = torch.Generator().manual_seed(seed)
    for _ in range(20):
        perm = torch.randperm(len(y), generator=g).to(DEV)
        for i in range(0, len(y), 256):
            b = perm[i:i + 256]
            loss = (torch.nn.functional.binary_cross_entropy_with_logits(lin(Xt[b]).squeeze(1), yt[b],
                                                                          reduction="none") * w[b]).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
    Wr = lin.weight.detach().cpu().numpy()[0]
    W = Wr / sd
    b0 = float(lin.bias.detach().cpu()) - float((mu / sd) @ Wr)
    with torch.no_grad():
        acc = float(((lin(Xt).squeeze(1) > 0).float() == yt).float().mean())
    return W.astype(np.float32), np.float32(b0), dict(n_gen=len(gen), n_morph=len(mor), train_acc=round(acc, 4))


def fe_ref(test):
    from safetensors.torch import load_file
    sd = load_file("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/"
                   "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9.safetensors", device="cpu")
    Wh, bh = sd["head.weight"].float().numpy(), sd["head.bias"].float().numpy()   # Linear(768, 2), class 0 = attack
    z = test.F @ Wh.T + bh
    ids = np.array(sorted(test.pos, key=test.pos.get))
    (K.OUT / "heads").mkdir(parents=True, exist_ok=True)
    np.savez(K.OUT / "heads/feref.npz", id=ids, logit=(z[:, 0] - z[:, 1]).astype(np.float32))
    print("feref", len(ids))


def main():
    global FEAT
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--seeds", default="401,402,403,404,405")
    ap.add_argument("--boot", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--fe-ref", action="store_true")
    ap.add_argument("--feat-dir", default=str(FEAT))
    ap.add_argument("--device", default="cuda", help="cuda (default; the DGX CPU is saturated) or cpu")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    FEAT = pathlib.Path(a.feat_dir)
    global DEV
    import torch
    torch.set_num_threads(1)
    DEV = a.device if (a.device == "cpu" or torch.cuda.is_available()) else "cpu"
    test = Bank(TESTS)
    if a.fe_ref:
        return fe_ref(test)
    bank = Bank(TRAIN)
    ids = np.array(sorted(test.pos, key=test.pos.get))
    od = K.OUT / ("heads/smoke" if a.smoke else "heads")
    od.mkdir(parents=True, exist_ok=True)
    cd = K.OUT / ("compose/smoke" if a.smoke else "compose")
    log = {}
    for arm in a.arms.split(","):
        for s in map(int, a.seeds.split(",")):
            f = cd / f"{arm}_s{s}.json"
            if not f.exists():
                continue
            t0 = time.time()
            c = json.load(open(f))
            if any(x not in bank.pos for x in c["genuine"] + c["morph"]):
                print(f"{arm}_s{s}: features missing for some training images; skipped", flush=True)
                continue
            W, b0, info = train(bank.get(c["genuine"]), bank.get(c["morph"]), s, a.boot)
            z = test.F @ W + b0
            tag = f"{arm}_s{s}" + ("_boot" if a.boot else "")
            np.savez(od / f"{tag}.npz", id=ids, logit=z.astype(np.float32), W=W, b=b0)
            info["seconds"] = round(time.time() - t0, 1)
            log[tag] = info
            print(tag, json.dumps(info), flush=True)
    lp = od / "heads_log.json"
    old = json.load(open(lp)) if lp.exists() else {}
    old.update(log)
    json.dump(old, open(lp, "w"), indent=1)


if __name__ == "__main__":
    main()
