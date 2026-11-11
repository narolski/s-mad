"""AG1 / AG2 / AG3 generation for one shard (GPU; WCSS H100 slot task or DGX GB10 smoke). Our own code, run as python -I.

Generator code = branch gan1 24cc974 files, vendored unchanged in vendor/ (sha256 in vendor/VENDOR.sha256, the hashes
registered in A33 / A34): mip1 = generate_mip1 (StyleGAN v1 FFHQ-1024, contributor latents by W+ inversion
generate_mip1.invert: w_avg init, 500 Adam steps lr 0.02, LPIPS + MSE + 0.1 ID), then generate.mipgan (150 Adam steps,
lr 0.03 x 0.95 / 6, 0.0002 Perc + 10 ID + 1 MS-SSIM + 1 ID-Diff); mip2 = generate.Models (e4e + StyleGAN2 FFHQ
config-f), init from the e4e codes, then the same generate.mipgan. Fixed iteration counts for every rung.
Rungs: R2 = mipgan(x, x, init w_x); R3 = mipgan(s1, s2); R4 = mipgan(s1(p), s2(q)); R3m = mipgan(s1, mirror(s1));
BR = bridge pair; RT = reversed twin; R2i = G(w_inv) render (mip1 only, descriptive); AG3 = mipgan_alpha (below) at alpha in 0.1..0.4.
mipgan_alpha: generate.mipgan with contributor weights (1 - alpha, alpha): Perc and MS-SSIM terms weighted, ID =
(1-a) dA + a dB, ID-Diff = 2 |(1-a) dA - a dB|, init (1-a) wA + a wB, identity crop at the weighted 5 points; at
alpha = 0.5 it equals generate.mipgan term by term (checked by --selfcheck); alpha = 0.5 jobs call generate.mipgan.
Logged per image (log.csv): final loss terms evaluated at the final latent, generator-side w600k cosines, latent
distance from the generator's mean latent (mean over the 18 layers of ||w_l - w_avg||_2, and Frobenius), seconds.
Output dir: png/<stem>.png (1024 RGB PNG, as the published MAD22 MIPGAN files), lat/<stem>.npz, lat/inv_<photo>.npz,
log.csv, inv.csv, meta.json. Exit 0 only if every job of the shard produced its PNG.
Usage: python -I ag1_gen.py --shard S.json --inputs DIR --weights DIR --sg1 FILE --out DIR [--latents DIR]
       [--max-jobs N] [--selfcheck]
"""
import argparse
import csv
import functools
import hashlib
import json
import os
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", required=True)
    ap.add_argument("--inputs", required=True)
    ap.add_argument("--weights", required=True)
    ap.add_argument("--sg1", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--latents", default=None)
    ap.add_argument("--max-jobs", type=int, default=None)
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("refused: run with python -I")
    # vendored code must be the registered one
    for line in open(HERE / "vendor/VENDOR.sha256"):
        h, f = line.split()
        if sha(HERE / "vendor" / f) != h:
            sys.exit(f"refused: vendor/{f} is not the registered file")
    os.environ["GAN_WEIGHTS"] = a.weights
    os.environ["SG1_WEIGHTS"] = a.sg1
    os.environ["TORCH_HOME"] = str(pathlib.Path(a.weights) / "torch")
    sys.path.insert(0, str(pathlib.Path(a.weights) / "py"))      # pytorch_msssim 1.0.0 from the pack
    sys.path.insert(0, str(HERE / "vendor"))
    import numpy as np
    import torch
    import torch.nn.functional as F
    _load = torch.load

    @functools.wraps(_load)
    def load_weights_only(*args, **kw):                              # every checkpoint loads as weights only,
        kw["weights_only"] = True                                    # also where vendored code asks otherwise
        return _load(*args, **kw)
    torch.load = load_weights_only
    import arcface as AF
    import generate as GEN
    import generate_mip1 as G1
    from PIL import Image

    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.deterministic = True                       # pre-run review finding 8 (repeatable runs
    torch.backends.cudnn.benchmark = False                          # on one platform and stack)
    torch.manual_seed(0)
    dev = "cuda"
    S = json.load(open(a.shard))
    inp = pathlib.Path(a.inputs)
    photos = json.load(open(inp / "photos.json"))
    out = pathlib.Path(a.out)
    for d in ("png", "lat"):
        (out / d).mkdir(parents=True, exist_ok=True)
    gen = S["gen"]
    t0 = time.time()
    if gen == "mip1":
        m = G1.Models1(dev)
        w_avg = m.G.w_avg.view(1, 1, -1).detach()
    else:
        m = GEN.Models(dev)
        w_avg = m.net.latent_avg.view(1, -1, 512).detach()
    print(f"models loaded in {time.time() - t0:.1f} s on {torch.cuda.get_device_name()} torch {torch.__version__}",
          flush=True)

    def latdist(w):
        d = (w - w_avg).float()
        return float(d.norm(dim=-1).mean()), float(d.norm())

    X, MM, KP, WI = {}, {}, {}, {}

    def load(ph):
        if ph not in X:
            X[ph] = GEN.load_png(inp / photos[ph]["crop"]).to(dev)
            KP[ph] = np.array(photos[ph]["kps256"])
            MM[ph] = AF.estimate_norm(KP[ph])

    inv_rows = []

    def latent(ph):
        load(ph)
        if ph in WI:
            return WI[ph]
        f = out / "lat" / f"inv_{ph}.npz"
        src = pathlib.Path(a.latents) / f"inv_{ph}.npz" if a.latents else None
        if f.exists() or (src is not None and src.exists()):
            WI[ph] = torch.from_numpy(np.load(f if f.exists() else src)["w"]).to(dev)
            return WI[ph]
        if S.get("needs"):
            sys.exit(f"missing inversion latent of {ph} (needs {S['needs']}): the core shard tar must be extracted")
        t = time.time()
        if gen == "mip1":
            w, loss, cos = G1.invert(m, X[ph], MM[ph])
            if not torch.isfinite(w).all() or not np.isfinite(loss):
                sys.exit(f"inversion of {ph}: non-finite latent or loss")
        else:
            w, loss, cos = m.encode(X[ph]), float("nan"), float("nan")
        torch.cuda.synchronize()
        np.savez_compressed(f, w=w.cpu().numpy().astype(np.float32))
        ld = latdist(w)
        inv_rows.append({"photo": ph, "gen": gen, "inv_loss": loss, "inv_cos_w600k": cos, "latdist": ld[0],
                         "latdist_fro": ld[1], "seconds": time.time() - t})
        WI[ph] = w
        return w

    def terms_at(w, xa, xb, Ma, Mb, Mm, al):
        """the mipgan_alpha objective at a fixed latent (no step); al = 0.5 is generate.mipgan's objective."""
        with torch.no_grad():
            ea, eb = m.emb(xa, Ma), m.emb(xb, Mb)
            fa, fb = m.vgg_feats(xa), m.vgg_feats(xb)
            y = GEN.down(m.synth(w))
            fy = m.vgg_feats(y)
            perc = (1 - al) * sum(F.mse_loss(f, g) for f, g in zip(fy, fa)) + al * sum(
                F.mse_loss(f, g) for f, g in zip(fy, fb))
            e = m.emb(y, Mm)
            da, db = 1 - (e * ea).sum(), 1 - (e * eb).sum()
            ident = (1 - al) * da + al * db
            iddiff = 2 * ((1 - al) * da - al * db).abs()
            y01 = (y + 1) / 2
            mss = (1 - al) * (1 - m.ms_ssim(y01, (xa + 1) / 2, data_range=1.0)) + al * (
                1 - m.ms_ssim(y01, (xb + 1) / 2, data_range=1.0))
            loss = GEN.MIP["l1"] * perc + GEN.MIP["l2"] * ident + GEN.MIP["l3"] * mss + GEN.MIP["l4"] * iddiff
        return {"loss": float(loss), "perc_x_l1": float(GEN.MIP["l1"] * perc), "id": float(ident),
                "msssim": float(mss), "iddiff": float(iddiff), "cos_a": float(1 - da), "cos_b": float(1 - db)}

    def mipgan_alpha(xa, xb, Ma, Mb, Mm, w0, al):
        P = GEN.MIP
        w = w0.clone().requires_grad_(True)
        opt = torch.optim.Adam([w], lr=P["lr"], betas=(0.9, 0.999), eps=1e-8)
        sched = torch.optim.lr_scheduler.StepLR(opt, step_size=P["every"], gamma=P["decay"])
        with torch.no_grad():
            ea, eb = m.emb(xa, Ma), m.emb(xb, Mb)
            fa, fb = m.vgg_feats(xa), m.vgg_feats(xb)
            ya01, yb01 = (xa + 1) / 2, (xb + 1) / 2
        for it in range(P["iters"]):
            y = GEN.down(m.synth(w))
            fy = m.vgg_feats(y)
            perc = (1 - al) * sum(F.mse_loss(f, g) for f, g in zip(fy, fa)) + al * sum(
                F.mse_loss(f, g) for f, g in zip(fy, fb))
            e = m.emb(y, Mm)
            da, db = 1 - (e * ea).sum(), 1 - (e * eb).sum()
            ident = (1 - al) * da + al * db
            iddiff = 2 * ((1 - al) * da - al * db).abs()
            y01 = (y + 1) / 2
            mss = (1 - al) * (1 - m.ms_ssim(y01, ya01, data_range=1.0)) + al * (1 - m.ms_ssim(y01, yb01, data_range=1.0))
            loss = P["l1"] * perc + P["l2"] * ident + P["l3"] * mss + P["l4"] * iddiff
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            sched.step()
        return w.detach()

    if a.selfcheck:          # mipgan_alpha(0.5) == generate.mipgan on the shard's first two photos
        p1, p2 = S["jobs"][0]["a"], S["jobs"][0]["b"] if S["jobs"][0]["b"] != S["jobs"][0]["a"] else S["jobs"][2]["b"]
        wa, wb = latent(p1), latent(p2)
        Mm = AF.estimate_norm((KP[p1] + KP[p2]) / 2)
        w_ref, _ = GEN.mipgan(m, X[p1], X[p2], MM[p1], MM[p2], Mm, (wa + wb) / 2)
        w_al = mipgan_alpha(X[p1], X[p2], MM[p1], MM[p2], Mm, 0.5 * wa + 0.5 * wb, 0.5)
        d = float((w_ref - w_al).abs().max())
        print(f"SELFCHECK max|w_ref - w_alpha0.5| = {d:.3e}", flush=True)
        json.dump({"selfcheck_maxabs": d}, open(out / "selfcheck.json", "w"))

    fields = ["stem", "rung", "gen", "a", "b", "alpha", "seconds", "loss", "perc_x_l1", "id", "msssim", "iddiff",
              "cos_a", "cos_b", "w600k_cos_a_img", "w600k_cos_b_img", "latdist", "latdist_fro", "init_latdist",
              "png_sha256"]
    logp = out / "log.csv"
    done = set()
    if logp.exists():
        done = {r["stem"] for r in csv.DictReader(open(logp))}
    fh = open(logp, "a", newline="")
    wr = csv.DictWriter(fh, fieldnames=fields)
    if not done:
        wr.writeheader()
    jobs = S["jobs"][:a.max_jobs] if a.max_jobs else S["jobs"]
    for j in jobs:
        png = out / "png" / f"{j['stem']}.png"
        if j["stem"] in done and png.exists():
            continue
        torch.cuda.synchronize()
        t = time.time()
        pa, pb, al = j["a"], j["b"], float(j["alpha"])
        wa, wb = latent(pa), latent(pb)
        w0 = (1 - al) * wa + al * wb if pa != pb else wa
        if j["rung"] == "R2i":
            w, terms = wa, {k: float("nan") for k in ("loss", "perc_x_l1", "id", "msssim", "iddiff", "cos_a", "cos_b")}
        else:
            Mm = AF.estimate_norm((1 - al) * KP[pa] + al * KP[pb]) if pa != pb else MM[pa]
            if al == 0.5:
                w, _ = GEN.mipgan(m, X[pa], X[pb], MM[pa], MM[pb], Mm, w0)
            else:
                w = mipgan_alpha(X[pa], X[pb], MM[pa], MM[pb], Mm, w0, al)
            terms = terms_at(w, X[pa], X[pb], MM[pa], MM[pb], Mm, al)
        if not torch.isfinite(w).all() or (j["rung"] != "R2i" and not np.isfinite(terms["loss"])):
            sys.exit(f"{j['stem']}: non-finite latent or loss; shard stopped (no PNG written)")
        with torch.no_grad():
            img = m.synth(w)
            y = GEN.down(img)
            ca = float((m.emb(y, MM[pa]) * m.emb(X[pa], MM[pa])).sum())
            cb = float((m.emb(y, MM[pb]) * m.emb(X[pb], MM[pb])).sum())
        arr = ((img[0].clamp(-1, 1) + 1) * 127.5).round().byte().permute(1, 2, 0).cpu().numpy()
        torch.cuda.synchronize()
        Image.fromarray(arr).save(png, compress_level=1)
        np.savez_compressed(out / "lat" / f"{j['stem']}.npz", w=w.cpu().numpy().astype(np.float32))
        ld, ld0 = latdist(w), latdist(w0)
        row = {"stem": j["stem"], "rung": j["rung"], "gen": gen, "a": pa, "b": pb, "alpha": al,
               "seconds": round(time.time() - t, 3), **terms, "w600k_cos_a_img": ca, "w600k_cos_b_img": cb,
               "latdist": ld[0], "latdist_fro": ld[1], "init_latdist": ld0[0], "png_sha256": sha(png)}
        wr.writerow(row)
        fh.flush()
        print(f"{j['stem']} {row['seconds']:.1f}s loss={terms['loss']:.3f} cosA={ca:.3f} cosB={cb:.3f} "
              f"latdist={ld[0]:.2f}", flush=True)
    fh.close()
    if inv_rows:
        new = not (out / "inv.csv").exists()
        with open(out / "inv.csv", "a", newline="") as fi:
            wi = csv.DictWriter(fi, fieldnames=list(inv_rows[0]))
            if new:
                wi.writeheader()
            wi.writerows(inv_rows)
    n_png = sum((out / "png" / f"{j['stem']}.png").exists() for j in jobs)
    json.dump({"shard": S["shard"], "gen": gen, "jobs": len(jobs), "png": n_png, "seconds": time.time() - t0,
               "device": torch.cuda.get_device_name(), "torch": torch.__version__,
               "peak_gpu_mem_mib": torch.cuda.max_memory_allocated() / 2 ** 20,
               "peak_gpu_reserved_mib": torch.cuda.max_memory_reserved() / 2 ** 20,
               "shard_sha256": sha(a.shard), "script_sha256": sha(__file__)}, open(out / "meta.json", "w"), indent=1)
    print(f"GEN_DONE {S['shard']} {n_png}/{len(jobs)} in {time.time() - t0:.0f} s", flush=True)
    sys.exit(0 if n_png == len(jobs) else 1)


if __name__ == "__main__":
    main()
