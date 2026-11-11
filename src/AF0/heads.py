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


class Source:
    """tokens + prep for one or more lists, addressed by (list index, row)."""

    def __init__(self, backbone, names, partial=False):
        self.backbone, self.names = backbone, names
        self.g = L.GRID[backbone]
        self.tok, self.prep, self.rows, self.done = {}, {}, {}, {}
        for n in names:
            tok, ids, done = L.load_tokens(backbone, n)
            if not partial:
                assert done == len(ids), f"{backbone}/{n}: extraction incomplete ({done}/{len(ids)})"
            p = L.prep(n, self.g)
            assert (p["ids"] == ids).all()
            rr = L.rows(n)
            assert [r["id"] for r in rr] == list(ids)
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


def predict_ridge(H, x):
    return ((x.astype(np.float32) - H["mu"]) / H["sd"]) @ H["w"] + H["b"]


def fit_mlp(src, tr, seed, dev, mu, sd, epochs=3, bs=4096):
    import torch
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    X = torch.from_numpy(np.concatenate([src.X(c) for c in chunks(tr, 64)]))      # (N, T, D) fp16, CPU
    Y = torch.from_numpy(src.get(tr, "target").astype(np.float32))
    N, T, D = X.shape
    Xf, Yf = X.reshape(-1, D), Y.reshape(-1)
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
            y = Yf[j].to(dev)
            loss = lossf(net(x).squeeze(1), y)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sch.step()
    net.eval()
    return net, float(loss)


def predict_mlp(net, x, mu, sd, dev):
    import torch
    with torch.no_grad():
        xx = (torch.from_numpy(x.astype(np.float32)).to(dev) - torch.from_numpy(mu).to(dev)) / torch.from_numpy(sd).to(dev)
        return net(xx).squeeze(-1).cpu().numpy()


def image_scores(pp, face):
    m = face >= L.FACE_MIN
    return np.array([p[mm].mean() for p, mm in zip(pp, m)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backbone", required=True)
    ap.add_argument("--train", required=True, help="comma list of af0 token lists")
    ap.add_argument("--eval", required=True, help="comma list of lists to score")
    ap.add_argument("--heads", default="ridge,mlp,logreg")
    ap.add_argument("--seeds", default="401,402,403,404,405")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--train-ids", default=None, help="npy of training ids (F4 subsets)")
    ap.add_argument("--partial", action="store_true", help="score only the extracted prefix of eval lists")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    import torch
    dev = "cuda"
    t0 = time.time()
    trn = a.train.split(",")
    src = Source(a.backbone, trn)
    tr = src.select(lambda r: r["set"] == "af0" and r["cell"] == "train")
    if a.train_ids:
        keep = set(np.load(a.train_ids).tolist())
        tr = [i for i in tr if src.row(i)["id"] in keep]
    evn = [n for n in a.eval.split(",")]
    ev = Source(a.backbone, evn, partial=a.partial)
    od = L.OUT / "heads" / a.backbone / a.tag
    od.mkdir(parents=True, exist_ok=True)
    log = dict(backbone=a.backbone, train=trn, n_train_images=len(tr), eval=evn, heads=a.heads, tag=a.tag)
    heads = a.heads.split(",")
    preds = {}          # head -> list name -> (N, T) float16 per-patch predictions or (N,) image scores
    H = None
    if "ridge" in heads or "mlp" in heads:
        H = fit_ridge(src, tr, dev)
        log["ridge"] = dict(lam_rel=H["lam_rel"], cv_mse=H["cv_mse"], n_patches=H["n_patches"])
        np.savez(od / "ridge.npz", **{k: v for k, v in H.items() if isinstance(v, np.ndarray)}, b=H["b"])
        print("ridge fitted", log["ridge"], f"{time.time() - t0:.0f}s", flush=True)
    if "ridge" in heads:
        for n in evn:
            P = []
            for c in chunks(list(range(len(ev.rows[n]))), 64):
                x = np.asarray(ev.tok[n][c[0]:c[-1] + 1])
                P.append(predict_ridge(H, x).astype(np.float16))
            preds.setdefault("ridge", {})[n] = np.concatenate(P)
    if "mlp" in heads:
        for s in map(int, a.seeds.split(",")):
            net, last = fit_mlp(src, tr, s, dev, H["mu"], H["sd"])
            torch.save(net.state_dict(), od / f"mlp_s{s}.pt")
            log[f"mlp_s{s}_last_loss"] = last
            for n in evn:
                P = []
                for c in chunks(list(range(len(ev.rows[n]))), 64):
                    x = np.asarray(ev.tok[n][c[0]:c[-1] + 1])
                    P.append(predict_mlp(net, x, H["mu"], H["sd"], dev).astype(np.float16))
                preds.setdefault(f"mlp_s{s}", {})[n] = np.concatenate(P)
            print(f"mlp seed {s} done, last loss {last:.5f}, {time.time() - t0:.0f}s", flush=True)
    if "logreg" in heads:
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler

        def pooled(S, idx):
            return np.concatenate([S.X(c).astype(np.float32).mean(1) for c in chunks(idx, 64)])

        lt = [i for i in tr if src.row(i)["rung"] in ("u50", "zero")]
        Xl = pooled(src, lt)
        yl = np.array([src.row(i)["rung"] == "u50" for i in lt], int)
        sc = StandardScaler().fit(Xl)
        clf = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(Xl), yl)
        log["logreg"] = dict(n=len(lt), n_pos=int(yl.sum()))
        for n in evn:
            Xe = np.concatenate([np.asarray(ev.tok[n][s:s + 64]).astype(np.float32).mean(1)
                                 for s in range(0, len(ev.rows[n]), 64)])
            preds.setdefault("logreg", {})[n] = clf.decision_function(sc.transform(Xe))
        print("logreg done", f"{time.time() - t0:.0f}s", flush=True)
    for h, d in preds.items():
        for n, P in d.items():
            ids = np.array([r["id"] for r in ev.rows[n]])
            if P.ndim == 2:
                np.savez(od / f"pred_{h}_{n}.npz", ids=ids, patch=P, score=image_scores(P.astype(np.float32),
                                                                                         ev.prep[n]["face"]))
            else:
                np.savez(od / f"pred_{h}_{n}.npz", ids=ids, score=P)
    log["seconds"] = round(time.time() - t0, 1)
    json.dump(log, open(od / "log.json", "w"), indent=1)
    print(json.dumps(log), flush=True)


if __name__ == "__main__":
    main()
