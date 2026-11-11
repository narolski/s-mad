"""AF0 heads on frozen patch tokens; writes per-patch predictions and image scores for every listed set.

Heads (prereg): (i) ridge per patch, (ii) two-layer MLP per patch (1024 -> 256 -> 1, GELU, Huber delta 0.1, AdamW
lr 1e-3 wd 1e-4, batch 4096 patches, 3 epochs, last state), seeds 401-405, (iii) image-level L2 logistic regression
(sklearn, C = 1, standardised) on mean-pooled patch tokens, uniform 0.5 (1) vs zero field (0).
Training data: AF0 training-split images (all field types + unprocessed photos, target = per-patch mean of a(x)),
all patches. Features standardised with training-patch mean / sd. Ridge lambda chosen by 3-fold CV over training
host persons (patch MSE) from a grid relative to trace(X'X)/D; validation persons are never used for any choice.
Image score = mean per-patch prediction over patches inside the face hull (>= half the footprint inside).
  python3 -I heads.py --backbone dinov3_512 --train af0_w1 --eval af0_w1,ar1 --heads ridge --tag first
Options --train-filter confounded|unconfounded (F4), see f4.py.
"""
import argparse
import json
import pathlib
import sys
import time

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import af0lib as L  # noqa: E402

RIDGE_GRID = [1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
TARGET_SCALE = {"g": 1 / 8.0, "D": 1 / 120.0, "G": 1 / 40.0}


class Source:
    """tokens + prep for one or more lists, addressed by (list index, row)."""

    def __init__(self, backbone, names, partial=False, target="alpha"):
        self.backbone, self.names = backbone, names
        self.g = L.GRID[backbone]
        self.tok, self.prep, self.rows, self.done = {}, {}, {}, {}
        gt = None
        if target != "alpha":           # wave 2: ghost energy g (scaled 1/8) or disagreement D (scaled 1/120)
            z = np.load(L.OUT / "ghost_targets.npz")
            gt = dict(zip(z["ids"], z[f"{target}{self.g}"] * TARGET_SCALE[target]))
        for n in names:
            tok, ids, done = L.load_tokens(backbone, n)
            if not partial:
                assert done == len(ids), f"{backbone}/{n}: extraction incomplete ({done}/{len(ids)})"
            p = dict(L.prep(n, self.g))
            assert (p["ids"] == ids).all()
            rr = L.rows(n)
            assert [r["id"] for r in rr] == list(ids)
            p["inner"] = L.prep_inner(n, self.g)
            if gt is not None:
                t = np.full_like(p["target"], np.nan)
                for i, r in enumerate(rr):
                    if r["set"] == "af0":
                        sid = r["id"].rsplit("_", 1)[0] if "_soft_" in r["rung"] else r["id"]
                        if r["rung"].split("_soft_")[0] in ("photo", "halfA", "halfB", "zero"):
                            t[i] = 0.0
                        elif sid in gt:
                            t[i] = gt[sid]
                        elif False:
                            t[i] = 0.0          # morph rows without a measured target stay NaN (excluded from fits)
                p["target"] = t
            self.tok[n] = tok
            self.prep[n] = {k: v[:done] for k, v in p.items()}
            self.rows[n] = rr[:done]
            self.done[n] = done
            if done < len(ids):
                print(f"NOTE {backbone}/{n}: using the first {done} of {len(ids)} rows (extraction running)", flush=True)

    def select(self, fn):
        return [(n, i) for n in self.names for i, r in enumerate(self.rows[n]) if fn(r)]

    def X(self, idx):
        out = []
        by = {}
        for k, (n, i) in enumerate(idx):
            by.setdefault(n, []).append((k, i))
        res = [None] * len(idx)
        for n, lst in by.items():
            ii = np.array([i for _, i in lst])
            o = np.argsort(ii)
            arr = np.asarray(self.tok[n][ii[o]])
            for j, oo in enumerate(o):
                res[lst[oo][0]] = arr[j]
        out = np.stack(res)
        return out

    def get(self, idx, key):
        return np.stack([self.prep[n][key][i] for n, i in idx])

    def row(self, ix):
        n, i = ix
        return self.rows[n][i]


def chunks(idx, k):
    for s in range(0, len(idx), k):
        yield idx[s:s + k]


def fit_ridge(src, tr, dev):
    import torch
    D = src.X(tr[:1]).shape[-1]
    s1 = torch.zeros(D, dtype=torch.float64, device=dev)
    s2 = torch.zeros(D, dtype=torch.float64, device=dev)
    n = 0
    for c in chunks(tr, 32):
        x = torch.from_numpy(src.X(c).reshape(-1, D)).to(dev).double()
        s1 += x.sum(0)
        s2 += (x * x).sum(0)
        n += len(x)
    mu = s1 / n
    sd = torch.sqrt(torch.clamp(s2 / n - mu * mu, min=1e-12))
    hosts = sorted({src.row(i)["p1"] for i in tr})
    fold = {h: k % 3 for k, h in enumerate(np.random.default_rng(401).permutation(hosts))}
    XtX = torch.zeros(3, D + 1, D + 1, dtype=torch.float64, device=dev)
    Xty = torch.zeros(3, D + 1, dtype=torch.float64, device=dev)
    yty = torch.zeros(3, dtype=torch.float64, device=dev)
    nn_ = torch.zeros(3, dtype=torch.float64, device=dev)
    for c in chunks(tr, 32):
        x = (torch.from_numpy(src.X(c)).to(dev).float() - mu.float()) / sd.float()
        y = torch.from_numpy(src.get(c, "target")).to(dev).float()
        f = torch.tensor([fold[src.row(i)["p1"]] for i in c], device=dev)
        for k in range(3):
            m = f == k
            if not m.any():
                continue
            xx = x[m].reshape(-1, D)
            xx = torch.cat([xx, torch.ones(len(xx), 1, device=dev)], 1).double()
            yy = y[m].reshape(-1).double()
            XtX[k] += xx.T @ xx
            Xty[k] += xx.T @ yy
            yty[k] += yy @ yy
            nn_[k] += len(yy)
    tot, toty = XtX.sum(0), Xty.sum(0)
    scale = float(torch.trace(tot[:D, :D]) / D)
    P = torch.eye(D + 1, dtype=torch.float64, device=dev)
    P[D, D] = 0
    cv = []
    for r in RIDGE_GRID:
        mse = 0.0
        for k in range(3):
            A, b = tot - XtX[k], toty - Xty[k]
            w = torch.linalg.solve(A + r * scale * P, b)
            mse += float(w @ XtX[k] @ w - 2 * w @ Xty[k] + yty[k])
        cv.append(mse / float(nn_.sum()))
    best = RIDGE_GRID[int(np.argmin(cv))]
    w = torch.linalg.solve(tot + best * scale * P, toty)
    return dict(mu=mu.float().cpu().numpy(), sd=sd.float().cpu().numpy(), w=w[:D].float().cpu().numpy(),
                b=float(w[D]), lam_rel=best, cv_mse=dict(zip(map(str, RIDGE_GRID), cv)), n_patches=int(nn_.sum()))


def predict_ridge(H, x, dev="cpu"):
    """per-patch ridge prediction; on the GPU the CPU only copies the fp16 tokens (the DGX CPU is oversubscribed)."""
    import torch
    if "_t" not in H or H["_t"][0] != dev:
        H["_t"] = (dev, torch.from_numpy(H["mu"]).to(dev), torch.from_numpy(H["sd"]).to(dev),
                   torch.from_numpy(H["w"]).to(dev))
    _, mu, sd, w = H["_t"]
    with torch.no_grad():
        xx = torch.from_numpy(np.ascontiguousarray(x)).to(dev).float()
        return (((xx - mu) / sd) @ w + H["b"]).cpu().numpy()


def fit_mlp(src, tr, seed, dev, mu, sd, epochs=3, bs=4096, kpatch=384):
    """per-patch MLP; each image contributes min(T, kpatch) patches drawn with the seed (RAM on the shared DGX)."""
    import torch
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    T = src.X(tr[:1]).shape[1]
    k = min(T, kpatch)
    Xs, Ys = [], []
    for c in chunks(tr, 64):
        x, y = src.X(c), src.get(c, "target")
        sel = np.stack([rng.choice(T, k, replace=False) for _ in range(len(c))])
        Xs.append(np.take_along_axis(x, sel[:, :, None], 1))
        Ys.append(np.take_along_axis(y, sel, 1))
    Xf = torch.from_numpy(np.concatenate(Xs).reshape(-1, x.shape[-1]))
    Yf = torch.from_numpy(np.concatenate(Ys).reshape(-1).astype(np.float32))
    D = Xf.shape[1]
    mu_t, sd_t = torch.from_numpy(mu).to(dev), torch.from_numpy(sd).to(dev)
    net = torch.nn.Sequential(torch.nn.Linear(D, 256), torch.nn.GELU(), torch.nn.Linear(256, 1)).to(dev)
    opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=1e-4)
    steps = epochs * (len(Xf) // bs)
    sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    lossf = torch.nn.HuberLoss(delta=0.1)
    net.train()
    for ep in range(epochs):
        perm = torch.from_numpy(rng.permutation(len(Xf)))
        for s in range(len(Xf) // bs):
            j = perm[s * bs:(s + 1) * bs]
            x = (Xf[j].to(dev).float() - mu_t) / sd_t
            loss = lossf(net(x).squeeze(1), Yf[j].to(dev))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sch.step()
    net.eval()
    return net, float(loss)


def predict_mlp(net, x, mu, sd, dev):
    import torch
    with torch.no_grad():
        xx = (torch.from_numpy(np.ascontiguousarray(x)).to(dev).float() - torch.from_numpy(mu).to(dev)) / \
            torch.from_numpy(sd).to(dev)
        return net(xx).squeeze(-1).cpu().numpy()


def cuda_ok(tries=10, wait=60):
    """the shared GB10 refuses allocations when system RAM is short; retry, then fall back to the CPU."""
    import torch
    for t in range(tries):
        try:
            x = torch.zeros(1 << 26, device="cuda")
            del x
            torch.cuda.empty_cache()
            return "cuda"
        except Exception as e:  # noqa: BLE001
            print(f"cuda not available now ({type(e).__name__}); retry {t + 1}/{tries} in {wait}s", flush=True)
            time.sleep(wait)
    return "cpu"


def pooled_gpu(tok, n, dev, k=64):
    import torch
    if dev == "cuda":
        dev = cuda_ok()
    out = []
    with torch.no_grad():
        for s in range(0, n, k):
            out.append(torch.from_numpy(np.ascontiguousarray(tok[s:min(s + k, n)])).to(dev).float().mean(1).cpu().numpy())
    return np.concatenate(out)


def image_scores(pp, face):
    m = face >= L.FACE_MIN
    return np.array([p[mm].mean() for p, mm in zip(pp, m)])


def region_scores(pp, face, inner):
    """wave 2: mean of the top tenth of face-hull patches; inner-face mean (inner hull >= half); periphery mean
    (patches with < half of the footprint in the face hull)."""
    m, mi = face >= L.FACE_MIN, inner >= L.FACE_MIN
    top = np.array([np.sort(p[mm])[-max(1, int(round(0.1 * mm.sum()))):].mean() for p, mm in zip(pp, m)])
    inn = np.array([p[mm].mean() for p, mm in zip(pp, mi)])
    per = np.array([p[~mm].mean() for p, mm in zip(pp, m)])
    return top, inn, per


ARMS = {
    # wave-3 five-arm ablation, uniform-0.5 morphs only as positives ("one global mixing weight")
    "a_img_photos": dict(kind="img", pos=("u50",), neg=("photo",)),
    "b_img_halves": dict(kind="img", pos=("u50",), neg=("halfA", "halfB")),
    "c_const_halves": dict(kind="dense", target="const", pos=("u50",), neg=("halfA", "halfB")),
    "d_meas_halves": dict(kind="dense", target="D", pos=("u50",), neg=("halfA", "halfB")),
    "e_meas_photos": dict(kind="dense", target="D", pos=("u50",), neg=("photo",)),
}
_SOFT = ("amsl112", "fm61")
for _k in list(ARMS):                 # wave 4: the same arms with softened copies added on both sides
    _v = ARMS[_k]
    ARMS[_k[0] + "4" + _k[1:]] = dict(_v, pos=_v["pos"] + tuple(f"{x}_soft_{s}" for x in _v["pos"] for s in _SOFT),
                                      neg=_v["neg"] + tuple(f"{x}_soft_{s}" for x in _v["neg"] for s in _SOFT))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--train", required=True, help="comma list of af0 token lists")
    ap.add_argument("--eval", required=True, help="comma list of lists to score")
    ap.add_argument("--heads", default="ridge,mlp,logreg")
    ap.add_argument("--seeds", default="401,402,403,404,405")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--train-ids", default=None, help="npy of training ids (F4 subsets)")
    ap.add_argument("--train-rungs", default=None, help="comma list: keep only these training rungs")
    ap.add_argument("--partial", action="store_true", help="score only the extracted prefix of eval lists")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--reuse-ridge", action="store_true")
    ap.add_argument("--score-only", action="store_true", help="load the saved heads of --tag and score --eval")
    ap.add_argument("--target", default="alpha", choices=("alpha", "g", "D", "G", "const", "shuffle"))
    ap.add_argument("--arm", default=None, choices=list(ARMS))
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    import torch
    dev = a.device
    if dev == "cuda":
        dev = cuda_ok()
    if dev == "cpu":
        torch.set_num_threads(4)
    t0 = time.time()
    arm = ARMS[a.arm] if a.arm else None
    if arm:
        a.target = arm.get("target", "alpha")
        a.train_rungs = ",".join(arm["pos"] + arm["neg"])
        a.heads = "logreg" if arm["kind"] == "img" else "ridge"
    trn = a.train.split(",")
    od = L.OUT / "heads" / a.backbone / a.tag
    od.mkdir(parents=True, exist_ok=True)
    heads = a.heads.split(",")
    log = dict(target=a.target, arm=a.arm, backbone=a.backbone, train=trn, eval=a.eval.split(","), heads=a.heads,
               tag=a.tag)
    H, nets, LR = None, {}, None
    if a.score_only:
        if (od / "ridge.npz").exists():
            z = np.load(od / "ridge.npz")
            H = dict(mu=z["mu"], sd=z["sd"], w=z["w"], b=float(z["b"]))
        for s in map(int, a.seeds.split(",")):
            if (od / f"mlp_s{s}.pt").exists() and "mlp" in heads:
                net = torch.nn.Sequential(torch.nn.Linear(len(H["mu"]), 256), torch.nn.GELU(), torch.nn.Linear(256, 1))
                net.load_state_dict(torch.load(od / f"mlp_s{s}.pt", map_location="cpu", weights_only=True))
                nets[s] = net.to(dev).eval()
        if (od / "logreg.npz").exists() and "logreg" in heads:
            LR = dict(np.load(od / "logreg.npz"))
        log = json.load(open(od / "log.json")) if (od / "log.json").exists() else log
    else:
        src = Source(a.backbone, trn, target=a.target if a.target not in ("const", "shuffle") else "alpha")
        tr = src.select(lambda r: r["set"] == "af0" and r["cell"] == "train")
        if a.train_ids:
            keep = set(np.load(a.train_ids).tolist())
            tr = [i for i in tr if src.row(i)["id"] in keep]
        if a.train_rungs:
            keep = set(a.train_rungs.split(","))
            tr = [i for i in tr if src.row(i)["rung"] in keep]
        tr = [(n, i) for n, i in tr if np.isfinite(src.prep[n]["target"][i]).all()]
        if a.target == "const":        # wave-3 arm (c): 0.5 inside the face hull of every positive, 0 elsewhere
            for n in src.names:
                t = src.prep[n]["target"]
                for i, r in enumerate(src.rows[n]):
                    if r["set"] == "af0":
                        t[i] = 0.5 * (src.prep[n]["face"][i] >= L.FACE_MIN) if r["rung"].split("_soft_")[0] not in (
                            "photo", "halfA", "halfB", "zero") else 0.0
        if a.target == "shuffle":      # wave-3 control: maps permuted between positive (non-zero) training images
            rng = np.random.default_rng(401)
            pos = [i for i in tr if src.row(i)["rung"] in ("u25", "u50", "grad", "bump")]
            maps = [src.prep[n]["target"][i].copy() for n, i in pos]
            perm = rng.permutation(len(pos))
            for (n, i), j in zip(pos, perm):
                src.prep[n]["target"][i] = maps[j]
        log["n_train_images"] = len(tr)
        log["train_rungs"] = dict(__import__("collections").Counter(src.row(i)["rung"] for i in tr))
        if "ridge" in heads or "mlp" in heads:
            if a.reuse_ridge and (od / "ridge.npz").exists():
                z = np.load(od / "ridge.npz")
                H = dict(mu=z["mu"], sd=z["sd"], w=z["w"], b=float(z["b"]))
            else:
                H = fit_ridge(src, tr, dev)
                log["ridge"] = dict(lam_rel=H["lam_rel"], cv_mse=H["cv_mse"], n_patches=H["n_patches"])
                np.savez(od / "ridge.npz", mu=H["mu"], sd=H["sd"], w=H["w"], b=H["b"], lam_rel=H["lam_rel"])
            print("ridge ready", log.get("ridge"), f"{time.time() - t0:.0f}s", flush=True)
        if "mlp" in heads:
            for s in map(int, a.seeds.split(",")):
                net, last = fit_mlp(src, tr, s, dev, H["mu"], H["sd"])
                torch.save(net.state_dict(), od / f"mlp_s{s}.pt")
                log[f"mlp_s{s}_last_loss"] = last
                nets[s] = net
                print(f"mlp seed {s} fitted, last loss {last:.5f}, {time.time() - t0:.0f}s", flush=True)
        if "logreg" in heads:
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import StandardScaler
            pos_r = arm["pos"] if arm else ("u50",)
            neg_r = arm["neg"] if arm else ("zero",)
            lt = [i for i in tr if src.row(i)["rung"] in pos_r + neg_r]
            Xl = np.concatenate([src.X(c).astype(np.float32).mean(1) for c in chunks(lt, 64)])
            yl = np.array([src.row(i)["rung"] in pos_r for i in lt], int)
            sc = StandardScaler().fit(Xl)
            clf = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(Xl), yl)
            LR = dict(mean=sc.mean_, scale=sc.scale_, coef=clf.coef_[0], b=clf.intercept_)
            np.savez(od / "logreg.npz", **LR)
            log["logreg"] = dict(n=len(lt), n_pos=int(yl.sum()))
        json.dump(log, open(od / "log.json", "w"), indent=1)
    for n in a.eval.split(","):
        if not (L.OUT / "feat" / a.backbone / f"{n}.done").exists():
            print(f"skip {n}: no features", flush=True)
            continue
        ev = Source(a.backbone, [n], partial=a.partial)
        N = len(ev.rows[n])
        if N == 0:
            print(f"skip {n}: 0 rows extracted", flush=True)
            continue
        ids = np.array([r["id"] for r in ev.rows[n]])
        face, inner = ev.prep[n]["face"], ev.prep[n]["inner"]
        todo = []
        if "ridge" in heads and H is not None:
            todo.append(("ridge", lambda x: predict_ridge(H, x, dev)))
        for s, net in nets.items():
            todo.append((f"mlp_s{s}", lambda x, net=net: predict_mlp(net, x, H["mu"], H["sd"], dev)))
        for h, fn in todo:
            P = np.concatenate([fn(np.asarray(ev.tok[n][c:min(c + 64, N)])).astype(np.float16) for c in range(0, N, 64)])
            Pf = P.astype(np.float32)
            top, inn, per = region_scores(Pf, face, inner)
            med = np.array([np.median(p[m]) for p, m in zip(Pf, face >= L.FACE_MIN)])
            np.savez(od / f"pred_{h}_{n}.npz", ids=ids, patch=P, score=image_scores(Pf, face), score_top10=top,
                     score_inner=inn, score_periph=per, score_median=med)
        if LR is not None:
            Xe = pooled_gpu(ev.tok[n], N, dev)
            np.savez(od / f"pred_logreg_{n}.npz", ids=ids, score=((Xe - LR["mean"]) / LR["scale"]) @ LR["coef"] + LR["b"])
        print(f"scored {n} ({N}) {time.time() - t0:.0f}s", flush=True)
    log["seconds_last"] = round(time.time() - t0, 1)
    json.dump(log, open(od / "log.json", "w"), indent=1)
    print(json.dumps(log)[:800], flush=True)


if __name__ == "__main__":
    main()
