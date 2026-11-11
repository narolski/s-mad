"""SM1 Part 3 heads on frozen CLIP ViT-L/14 features (feats.py) and their scores on every test / audit image.

Arms (genuine class + morph class; N = release pairs with landmarks, equal for a, b, b', c, c', d):
  a     os25k_bf_t (25,000) + release morph files (N)           a256  as a, morph files 256 x 256 only (A1.8)
  b     os25k_bf_t + release pairs re-made by our engine        bp    (b'): release first contributors, random
                                                                        unused partners, cap 2 (A1.3)
  c     os25k_bf_t + balanced look-alike pairs on os25k_bf_t    cr    (c'): balanced random pairs (A1.3)
  d     12,500 renders + 12,500 halves (both halves of 6,250 c pairs, drawn per seed) + c morphs
  dplus 25,000 renders + 12,500 halves + c morphs (descriptive, unequal count, A1.10)
Head: standardise (train mean / std), Linear(768, 1), class-balanced BCE, AdamW lr 1e-3, wd 1e-4, batch 256,
20 epochs, last epoch; seed -> init, shuffle, d draws. --boot: training images resampled with replacement
(genuine by image, morphs by pair; A1.7, descriptive). Reference: the FE ViT-L/14 release header on the same features.
--smoke: 500 morph pairs (lists/smoke_*.csv) + 834 genuine (seeded), seed 401 only.

  python3 -I heads.py --arms a,b,bp,c,cr,d,a256,dplus --seeds 401,402,403,404,405 [--boot] [--smoke]
  python3 -I heads.py --fe-ref
-> OUT/heads[/smoke]/<arm>_s<seed>[_boot].npz (id, logit over all test + audit images), heads_log.json
"""
import argparse
import csv
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

FEAT = K.OUT / "feat"
TESTS = ("test_eval", "test_mad22", "test_ar1", "test_ar1h", "audit")


def load(name):
    z = np.load(FEAT / f"{name}.npz", allow_pickle=False)
    return np.array([str(i) for i in z["id"]]), z["feat"]


def subset(name, ids):
    i, f = load(name)
    pos = {x: j for j, x in enumerate(i)}
    sel = [pos[x] for x in ids]
    return f[sel]


def smoke_ids(arm):
    rows = list(csv.DictReader(open(K.OUT / "lists" / f"smoke_{arm}.csv")))
    return [r["id"] for r in rows]


def arm_data(arm, seed, smoke):
    rng = np.random.default_rng(seed)
    bid, bf = load("train_bf")
    n_gen = 834 if smoke else len(bid)
    if smoke:
        bf = bf[np.sort(np.random.default_rng(K.SEED + 17).choice(len(bid), size=n_gen, replace=False))]
    src = {"a": "arma", "a256": "arma", "b": "armb", "bp": "armbp", "c": "armc", "cr": "armcr", "d": "armc",
           "dplus": "armc", "d50": "armd50", "d500": "armd500", "e": "armc"}[arm]
    pre = "smoke_" if smoke else ""         # smoke builds have their own feature files
    if src == "arma":                      # features of all 15,000 release files; arm = the N pairs of train_arma.csv
        want = [r["id"] for r in csv.DictReader(open(K.OUT / "flists/train_arma.csv"))]
        mid, mf = np.array(want), subset("train_m15k", want)
    else:
        mid, mf = load(f"{pre}train_{src}")
    if smoke:
        keep = set(smoke_ids(src))
        sel = [j for j, x in enumerate(mid) if x in keep]
        mid, mf = mid[sel], mf[sel]
    if arm == "a256":
        sz = {r["id"]: r["size"] for r in csv.DictReader(open(K.OUT / "flists/train_arma.csv"))}
        sel = [j for j, x in enumerate(mid) if sz[x] == "256x256"]
        mid, mf = mid[sel], mf[sel]
    gen = bf
    if arm == "e":                         # A4: history crossing, quarters of the genuine class, halves of the morphs
        assert not smoke
        sid, sf = load("train_arme_bfS")
        assert [x[4:] for x in sid] == [x[3:] for x in bid]
        hid, hf = load("train_armc_halves")
        hsid, hsf = load("train_arme_hS")
        assert [x[:-2] for x in hsid] == list(hid)
        csid, csf = load("train_arme_cS")
        assert [x[:-2] for x in csid] == list(mid)
        q = len(bid) // 4
        pb = rng.permutation(len(bid))
        ph = rng.permutation(len(hid))
        gen = np.concatenate([bf[pb[:q]], sf[pb[q:2 * q]], hf[ph[:q]], hsf[ph[q:2 * q]]])
        pm = rng.permutation(len(mid))
        h2 = len(mid) // 2
        return gen, np.concatenate([mf[pm[:h2]], csf[pm[h2:]]])
    if arm in ("d", "dplus"):
        hid, hf = load(f"{pre}train_armc_halves")
        pair = np.array([x.rsplit("_h", 1)[0] for x in hid])
        pairs = np.array(sorted(set(mid.tolist())))
        n_h = (len(bf) // 2) if arm == "d" else len(bf) // 2
        pick = set(rng.choice(pairs, size=n_h // 2, replace=False).tolist())
        hsel = np.array([p in pick for p in pair])
        if arm == "d":
            g = bf[rng.choice(len(bf), size=len(bf) - hsel.sum(), replace=False)]
            gen = np.concatenate([g, hf[hsel]])
        else:
            gen = np.concatenate([bf, hf[hsel]])
    return gen, mf


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
    Xt = torch.from_numpy((X - mu) / sd)
    yt = torch.from_numpy(y)
    w = torch.where(yt == 1, len(y) / (2 * len(mor)), len(y) / (2 * len(gen)))
    lin = torch.nn.Linear(X.shape[1], 1)
    opt = torch.optim.AdamW(lin.parameters(), lr=1e-3, weight_decay=1e-4)
    g = torch.Generator().manual_seed(seed)
    for _ in range(20):
        perm = torch.randperm(len(y), generator=g)
        for i in range(0, len(y), 256):
            b = perm[i:i + 256]
            loss = (torch.nn.functional.binary_cross_entropy_with_logits(lin(Xt[b]).squeeze(1), yt[b],
                                                                          reduction="none") * w[b]).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
    W = lin.weight.detach().numpy()[0] / sd
    b0 = float(lin.bias.detach()) - float((mu / sd) @ lin.weight.detach().numpy()[0])
    with torch.no_grad():
        acc = float(((lin(Xt).squeeze(1) > 0).float() == yt).float().mean())
    return W.astype(np.float32), np.float32(b0), dict(n_gen=len(gen), n_morph=len(mor), train_acc=round(acc, 4))


def test_feats():
    ids, fs = [], []
    for t in TESTS:
        if (FEAT / f"{t}.npz").exists():
            i, f = load(t)
            ids.append(i)
            fs.append(f)
    return np.concatenate(ids), np.concatenate(fs)


def fe_ref():
    for p in (K.MC, K.W46 / "smadcvpr"):
        sys.path.insert(0, str(p))
    import torch
    import common as C
    import a12_released as R
    R.np, R.torch, R.C = np, torch, C
    spec = R.RELEASES["madation_fe_vitl14"]
    fe = R.build_release(spec)
    fe.load_state_dict(R.extract_state(R.load_release(
        pathlib.Path("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/"
                     "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9.safetensors")), spec), strict=True)
    ids, F = test_feats()
    with torch.no_grad():
        z = R.head_logit(fe.head(torch.from_numpy(F)), 2, 0).numpy()
    (K.OUT / "heads").mkdir(parents=True, exist_ok=True)
    np.savez(K.OUT / "heads/feref.npz", id=ids, logit=z.astype(np.float32))
    print("feref", len(ids))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="a,b,bp,c,cr,d,e,d50,d500,a256,dplus")
    ap.add_argument("--seeds", default="401,402,403,404,405")
    ap.add_argument("--boot", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--fe-ref", action="store_true")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    import torch
    torch.set_num_threads(1)
    if a.fe_ref:
        return fe_ref()
    od = K.OUT / ("heads/smoke" if a.smoke else "heads")
    od.mkdir(parents=True, exist_ok=True)
    ids, F = test_feats()
    log = {}
    for arm in a.arms.split(","):
        for s in map(int, a.seeds.split(",")):
            t0 = time.time()
            gen, mor = arm_data(arm, s, a.smoke)
            W, b0, info = train(gen, mor, s, a.boot)
            z = F @ W + b0
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
