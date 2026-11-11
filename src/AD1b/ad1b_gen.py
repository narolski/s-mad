"""AD1b generation: DiffAE codes and 20-step renders of identical-input and mirror-input morphs, through the A43 generator
(mambamorph-code-a44/smadcvpr/a43_gen.py, sha fc862ec6...) unchanged in every part that touches an image: the same pinned
DiffAE repository and checkpoint, the same model loading, LitModel.encode / encode_stochastic(T=250) / render(T=20),
the A43 interp() copied verbatim (z lerp, x_T slerp, alpha 0.5), batch 16, torchvision save_image.
The only new operation is a lossless left-right flip of a loaded input tensor (torch.flip along width).

Jobs (FRLL, persons = the 102 X3 self-pair persons, A = <p>_03, A' = <p>_08, B = <next person>_03):
  codes  z_sem of A, flip(A), A', B (all persons); x_T of A and flip(A) (all persons), of A' and B (first --n-xt persons)
  PAA    render(interp(A, A), 20)          -> PAA/png256/<p>_03.png
  PAF    render(interp(A, flip A), 20)     -> PAF/png256/<p>_03.png
  D20r   render(x_T(A), z(A), 20) (the A43 D20 path, re-run here) -> D20r/png256/<p>_03.png
Pool (200 FRGC / colorFERET hosts, DiffAE-aligned H, S, B): z_sem of H, flip(H), S, B.

usage: python -I ad1b_gen.py --repo R --ckpt C --a256 DIR --pool-a256 DIR --pool-sel CSV --self-pairs CSV --out-root DIR
          [--n-xt 30] [--smoke N] [--bs 16]
"""
import argparse
import csv
import hashlib
import json
import pathlib
import sys
import time

T_ENC, T_DEC20, ALPHA = 250, 20, 0.5
CKPT_SHA = "9bd2ba9e4c22afde8f18958026a4e8e625ef67d2c3ee76bb3aa72f3e67d3b9ca"
REPO_COMMIT = "00c57d3f626f28bf9ed8aff58d90baab25de3af4"


class _InertCallbackState:
    def __init__(self, *a, **k):
        self._a, self._k = a, k


def fsha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    for k in ("repo", "ckpt", "a256", "pool-a256", "pool-sel", "self-pairs", "out-root"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--n-xt", type=int, default=30)
    ap.add_argument("--n-img", type=int, default=0, help="persons with x_T and renders (0 = all); z_sem for all")
    ap.add_argument("--smoke", type=int, default=0)
    ap.add_argument("--bs", type=int, default=16)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run as python -I")
    out = pathlib.Path(a.out_root)
    if out.exists():
        sys.exit(f"{out} exists")
    if fsha(a.ckpt) != CKPT_SHA:
        sys.exit("checkpoint sha mismatch")
    import subprocess
    gr = lambda *c: subprocess.run(["git", "-C", a.repo, *c], capture_output=True, text=True).stdout  # noqa: E731
    if gr("rev-parse", "HEAD").strip() != REPO_COMMIT or gr("status", "--porcelain").strip():
        sys.exit("DiffAE repo is not the clean pinned commit")
    sys.path.insert(0, a.repo)
    import numpy as np
    import torch
    import torch.nn.functional as F
    from torchvision.utils import save_image
    from templates import ffhq256_autoenc, LitModel
    from dataset import ImageDataset

    device = "cuda:0"
    conf = ffhq256_autoenc()
    model = LitModel(conf)
    torch.serialization.add_safe_globals(
        [(_InertCallbackState, "pytorch_lightning.callbacks.model_checkpoint.ModelCheckpoint")])
    state = torch.load(a.ckpt, map_location="cpu", weights_only=True)
    res = model.load_state_dict(state["state_dict"], strict=False)
    del state
    if [k for k in res.missing_keys if k.startswith("ema_model.")]:
        sys.exit("ema_model keys missing")
    model.ema_model.eval()
    model.ema_model.to(device)

    data = ImageDataset(a.a256, image_size=conf.img_size, exts=["png"], do_augment=False, sort_names=True, has_subdir=False)
    idx = {pathlib.Path(str(p)).stem: i for i, p in enumerate(data.paths)}
    pdata = ImageDataset(a.pool_a256, image_size=conf.img_size, exts=["png"], do_augment=False, sort_names=True, has_subdir=False)
    pidx = {pathlib.Path(str(p)).stem: i for i, p in enumerate(pdata.paths)}
    persons = sorted({r["person"] for r in csv.DictReader(open(a.self_pairs))})
    sel = list(csv.DictReader(open(a.pool_sel)))
    if a.smoke:
        persons, sel = persons[:a.smoke], sel[:a.smoke]
    nxt = {p: persons[(i + 1) % len(persons)] for i, p in enumerate(persons)}

    imgs = {}
    for p in persons:
        A = data[idx[f"{p}_03"]]["img"]
        imgs[f"{p}_03"] = A
        imgs[f"{p}_03_flip"] = torch.flip(A, dims=[-1])
        imgs[f"{p}_08"] = data[idx[f"{p}_08"]]["img"]
    pool_ok = []
    for r in sel:
        ks = {role: f"{r['tag']}_{role}" for role in ("H", "S", "B")}
        if all(k in pidx for k in ks.values()):
            for role, k in ks.items():
                imgs["pool_" + k] = pdata[pidx[k]]["img"]
            imgs[f"pool_{r['tag']}_H_flip"] = torch.flip(imgs[f"pool_{r['tag']}_H"], dims=[-1])
            pool_ok.append(r["tag"])
    log = {"n_persons": len(persons), "pool_hosts_aligned": len(pool_ok), "pool_hosts_selected": len(sel),
           "T_enc": T_ENC, "T_dec": T_DEC20, "alpha": ALPHA, "bs": a.bs, "script_sha256": fsha(__file__),
           "device": torch.cuda.get_device_name(0), "torch": torch.__version__}

    def sync():
        torch.cuda.synchronize()

    # ---- semantic codes for every loaded image
    cond, xT = {}, {}
    names = sorted(imgs)
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(names), a.bs):
            nm = names[i:i + a.bs]
            c = model.encode(torch.stack([imgs[s] for s in nm]).to(device))
            for k, s in enumerate(nm):
                cond[s] = c[k].float().cpu()
        sync()
    log["encode_z_s"] = time.time() - t0
    # ---- stochastic codes (the A43 call: encode_stochastic(batch, encode(batch), T=250))
    pim = persons[:a.n_img] if a.n_img else persons
    log["n_img_persons"] = len(pim)
    need_xt = [f"{p}_03" for p in pim] + [f"{p}_03_flip" for p in pim] + \
              [f"{p}_08" for p in pim[:a.n_xt]] + [f"{nxt[p]}_03" for p in pim[:a.n_xt]]
    need_xt = sorted(set(need_xt))
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(need_xt), a.bs):
            nm = need_xt[i:i + a.bs]
            batch = torch.stack([imgs[s] for s in nm]).to(device)
            c = model.encode(batch)
            x = model.encode_stochastic(batch, c, T=T_ENC)
            for k, s in enumerate(nm):
                xT[s] = x[k].float().cpu()
            print(f"x_T {i + len(nm)}/{len(need_xt)} {time.time() - t0:.0f}s", flush=True)
        sync()
    log["encode_xT_s"] = time.time() - t0
    log["n_xT"] = len(need_xt)

    def cosv(u, v):
        u = F.normalize(u.view(-1), dim=0)
        v = F.normalize(v.view(-1), dim=0)
        return (u * v).sum()

    def interp(sa, sb):   # verbatim from a43_gen.py
        c0, c1, x0, x1 = cond[sa], cond[sb], xT[sa], xT[sb]
        alpha = torch.tensor([ALPHA], dtype=torch.float32)
        intp = c0[None] * (1 - alpha[:, None]) + c1[None] * alpha[:, None]
        theta = torch.arccos(cosv(x0, x1))
        x_shape = x0.shape
        intp_x = (torch.sin((1 - alpha[:, None]) * theta) * x0.flatten(0, 2)[None] +
                  torch.sin(alpha[:, None] * theta) * x1.flatten(0, 2)[None]) / torch.sin(theta)
        return intp[0], intp_x.view(-1, *x_shape)[0], float(theta)

    jobs = []
    for p in pim:
        A = f"{p}_03"
        jobs.append(("PAA", A, A, A))
        jobs.append(("PAF", A, A, A + "_flip"))
        jobs.append(("D20r", A, A, None))
    rows = []
    mix_codes = {}
    t0 = time.time()
    with torch.no_grad():
        for pool in ("PAA", "PAF", "D20r"):
            pj = [j for j in jobs if j[0] == pool]
            (out / pool / "png256").mkdir(parents=True, exist_ok=False)
            for i in range(0, len(pj), a.bs):
                chunk = pj[i:i + a.bs]
                cs, xs, th = [], [], []
                for (_, name, sa, sb) in chunk:
                    if sb is None:
                        cs.append(cond[sa]); xs.append(xT[sa]); th.append("")
                    else:
                        c_, x_, t_ = interp(sa, sb)
                        cs.append(c_); xs.append(x_); th.append(t_)
                        mix_codes[(pool, name)] = {"z_equal_zA": bool(torch.equal(c_, cond[sa])),
                                                   "xT_finite": bool(torch.isfinite(x_).all()),
                                                   "xT_maxabs_minus_xTA": float((x_ - xT[sa]).abs().max()) if torch.isfinite(x_).all() else None}
                pred = model.render(torch.stack(xs).to(device), torch.stack(cs).to(device), T=T_DEC20)
                sync()
                for k, (_, name, sa, sb) in enumerate(chunk):
                    pth = out / pool / "png256" / f"{name}.png"
                    save_image(pred[k], str(pth))
                    mc = mix_codes.get((pool, name), {})
                    rows.append({"pool": pool, "name": name, "src_a": sa, "src_b": sb or "", "theta_xT": th[k],
                                 "finite": int(bool(torch.isfinite(pred[k]).all())), "z_equal_zA": mc.get("z_equal_zA", ""),
                                 "xT_mix_finite": mc.get("xT_finite", ""), "xT_mix_maxabs_minus_xTA": mc.get("xT_maxabs_minus_xTA", ""),
                                 "sha256": fsha(pth)})
    log["render_s"] = time.time() - t0
    with open(out / "gen_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    np.savez(out / "codes_z.npz", names=np.array(sorted(cond)), z=np.stack([cond[k].numpy() for k in sorted(cond)]))
    np.savez(out / "codes_xT.npz", names=np.array(sorted(xT)), xT=np.stack([xT[k].numpy() for k in sorted(xT)]))
    json.dump(log, open(out / "gen_log.json", "w"), indent=1)
    print(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()
