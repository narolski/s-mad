"""Diffusion-autoencoder generation on Athena (DG1), amendment 2: the self-contained add-on. One process per shard of
hosts: encode every source once, SAVE the codes (semantic code z and noise map x_T per source) and the fresh-noise
draws, and render every add-on job from them.

Generator: as dg1_gen.py / a43_gen.py (pinned DiffAE commit 00c57d3f..., FFHQ256 autoencoder 9bd2ba9e...,
LitModel.encode, encode_stochastic(T=250), render(T=steps), the A43 interp() verbatim with alpha as an argument, fp16
autocast, batch 16, save_image). Job modes (column `mode`):
  rec    render(x_T(a), z(a))                                   (A43 reconstruction path)
  mix    render(interp(a, b, alpha))                           (A43 mix: z lerp + x_T slerp)
  noise  render(x of interp(a, b, alpha), z(a))                (noise-only mix: only the slerped noise map is used)
  sem    render(x_T(a), z of interp(a, b, alpha))              (semantic-only mix: only the lerped code is used)
  fresh  render(eps_k, z(a)), eps_k ~ N(0, I), CPU torch.Generator seeded with int(sha256("DG1fresh|<host>|<k>")[:15], 16)
Sources named '<stem>__flip' are the loaded tensor flipped left-right (lossless, as AD1b).
Guards (review finding 8): the mixing angle theta is computed and checked finite BEFORE rendering; a job with a
non-finite theta (or non-finite codes) is not rendered and is recorded; outputs, rows, codes and log are always
written, and the process exits non-zero at the end if anything was non-finite (the task script tars first).

Job list CSV columns: set,pool,rung,name,src_a,src_b,alpha,steps,host,partner,mode,fresh_k.
Outputs: <out-root>/<pool>/<name>, gen_rows.csv, gen_log.json, codes.npz (names, z, xT; float32), fresh.npz (keys,
seeds, eps; float32). The output folder must not exist.

usage: python -I dg1_addon.py --repo R --ckpt C --inputs DIR --jobs CSV --out-root DIR [--bs 16] [--repo-manifest F]
"""
import argparse
import csv
import hashlib
import json
import pathlib
import platform
import shutil
import subprocess
import sys
import time

T_ENC = 250
CKPT_SHA = "9bd2ba9e4c22afde8f18958026a4e8e625ef67d2c3ee76bb3aa72f3e67d3b9ca"
REPO_COMMIT = "00c57d3f626f28bf9ed8aff58d90baab25de3af4"
STEPS_OK = {20, 100}
MODES = {"rec", "mix", "noise", "sem", "fresh"}
FLIP = "__flip"
COLS = ["set", "pool", "rung", "name", "src_a", "src_b", "alpha", "steps", "host", "partner", "mode", "fresh_k"]


class _InertCallbackState:
    """Placeholder for pytorch_lightning.callbacks.model_checkpoint.ModelCheckpoint in the checkpoint's 'callbacks'
    entry (never used)."""

    def __init__(self, *a, **k):
        self._a, self._k = a, k


def fsha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def fresh_seed(host, k):
    return int(hashlib.sha256(f"DG1fresh|{host}|{k}".encode()).hexdigest()[:15], 16)


def check_repo(repo, manifest):
    info = {}
    if shutil.which("git"):
        gr = lambda *c: subprocess.run(["git", "-C", repo, *c], capture_output=True, text=True).stdout  # noqa: E731
        head, dirty = gr("rev-parse", "HEAD").strip(), gr("status", "--porcelain").strip()
        info["git_head"], info["git_dirty"] = head, bool(dirty)
        if head != REPO_COMMIT or dirty:
            sys.exit(f"DiffAE repo is not the clean pinned commit (HEAD {head!r}, dirty {bool(dirty)})")
    if manifest:
        bad = n = 0
        for ln in open(manifest):
            h, rel = ln.rstrip("\n").split("  ", 1)
            n += 1
            bad += fsha(pathlib.Path(repo) / rel) != h
        info["manifest_files"], info["manifest_bad"] = n, bad
        if bad:
            sys.exit(f"DiffAE repo: {bad} of {n} files differ from the manifest")
    if not info:
        sys.exit("no way to verify the DiffAE repo (no git, no manifest)")
    return info


def main():
    ap = argparse.ArgumentParser()
    for k in ("repo", "ckpt", "inputs", "jobs", "out-root"):
        ap.add_argument("--" + k, required=True)
    ap.add_argument("--repo-manifest", default="")
    ap.add_argument("--bs", type=int, default=16)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run as python -I (third-party code and checkpoint)")
    out = pathlib.Path(a.out_root)
    if out.exists():
        sys.exit(f"{out} exists (a new output folder; nothing is replaced)")
    t_all = time.time()
    jobs = list(csv.DictReader(open(a.jobs)))
    if not jobs or list(jobs[0].keys()) != COLS:
        sys.exit(f"job list columns {list(jobs[0].keys()) if jobs else None} != {COLS}")
    keys = [(j["pool"], j["name"]) for j in jobs]
    if len(set(keys)) != len(keys):
        sys.exit("two jobs share an output name")
    for j in jobs:
        if int(j["steps"]) not in STEPS_OK or j["mode"] not in MODES:
            sys.exit(f"job {j['pool']}/{j['name']}: steps {j['steps']} mode {j['mode']}")
        if j["mode"] in ("mix", "noise", "sem") and not j["src_b"]:
            sys.exit(f"job {j['pool']}/{j['name']}: mode {j['mode']} needs src_b")
        if j["mode"] in ("rec", "fresh") and j["src_b"]:
            sys.exit(f"job {j['pool']}/{j['name']}: mode {j['mode']} takes one source")
        if j["mode"] == "fresh" and j["fresh_k"] not in ("1", "2"):
            sys.exit(f"job {j['pool']}/{j['name']}: fresh_k {j['fresh_k']}")
    got = fsha(a.ckpt)
    if got != CKPT_SHA:
        sys.exit(f"checkpoint sha256 {got} != {CKPT_SHA}")
    repo_info = check_repo(a.repo, a.repo_manifest)
    sys.path.insert(0, a.repo)
    import numpy as np
    import torch
    import torch.nn.functional as F
    import torchvision
    import PIL
    from torchvision.utils import save_image
    from templates import ffhq256_autoenc, LitModel  # noqa: E402  (pinned DiffAE repository)
    from dataset import ImageDataset  # noqa: E402

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

    data = ImageDataset(a.inputs, image_size=conf.img_size, exts=["png"], do_augment=False, sort_names=True,
                        has_subdir=False)
    idx = {pathlib.Path(str(p)).stem: i for i, p in enumerate(data.paths)}

    def base(s):
        return s[:-len(FLIP)] if s.endswith(FLIP) else s

    need = sorted({s for j in jobs for s in (j["src_a"], j["src_b"]) if s})
    missing = sorted({base(s) for s in need if base(s) not in idx})
    if missing:
        sys.exit(f"inputs missing: {missing[:10]} ({len(missing)})")

    def load(s):
        t = data[idx[base(s)]]["img"]
        return torch.flip(t, dims=[-1]) if s.endswith(FLIP) else t

    def sync():
        torch.cuda.synchronize()

    log = {"generator": "A43 path (a43_gen.py fc862ec6...) via dg1_addon.py (amendment 2)", "T_enc": T_ENC,
           "bs": a.bs, "fp16_autocast": conf.fp16, "seed": conf.seed, "ckpt_sha256": got, "repo": repo_info,
           "torch": torch.__version__, "cuda": torch.version.cuda, "cudnn": torch.backends.cudnn.version(),
           "torchvision": torchvision.__version__, "numpy": np.__version__, "pillow": PIL.__version__,
           "python": platform.python_version(), "node": platform.node(), "device": torch.cuda.get_device_name(0),
           "jobs_file": a.jobs, "jobs_sha256": fsha(a.jobs), "script_sha256": fsha(__file__), "n_jobs": len(jobs)}
    out.mkdir(parents=True)

    # ---- codes: one encoding per source in this process (the A43 calls), saved
    cond, xT = {}, {}
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(need), a.bs):
            names = need[i:i + a.bs]
            batch = torch.stack([load(s) for s in names]).to(device)
            c = model.encode(batch)
            x = model.encode_stochastic(batch, c, T=T_ENC)
            for k, s in enumerate(names):
                cond[s], xT[s] = c[k].float().cpu(), x[k].float().cpu()
            print(f"encode {i + len(names)}/{len(need)} {time.time() - t0:.0f}s", flush=True)
        sync()
    log["n_encode"] = len(need)
    log["encode_s"] = time.time() - t0
    log["encode_s_per_image"] = log["encode_s"] / max(1, len(need))
    np.savez(out / "codes.npz", names=np.array(need), z=np.stack([cond[s].numpy() for s in need]),
             xT=np.stack([xT[s].numpy() for s in need]))
    bad_codes = sorted(s for s in need if not (torch.isfinite(cond[s]).all() and torch.isfinite(xT[s]).all()))
    log["nonfinite_codes"] = bad_codes

    # ---- fresh-noise draws (seeded on the CPU), saved
    fresh = {}
    for j in jobs:
        if j["mode"] == "fresh":
            key = (j["host"], int(j["fresh_k"]))
            if key not in fresh:
                g = torch.Generator(device="cpu").manual_seed(fresh_seed(*key))
                fresh[key] = torch.randn(xT[j["src_a"]].shape, generator=g, dtype=torch.float32)
    fk = sorted(fresh)
    if fk:
        np.savez(out / "fresh.npz", keys=np.array([f"{h}|{k}" for h, k in fk]),
                 seeds=np.array([str(fresh_seed(h, k)) for h, k in fk]), eps=np.stack([fresh[k].numpy() for k in fk]))
    log["n_fresh"] = len(fk)

    def cosv(u, v):
        u = F.normalize(u.view(-1), dim=0)
        v = F.normalize(v.view(-1), dim=0)
        return (u * v).sum()

    def interp(sa, sb, ALPHA):   # the A43 interp(), verbatim but for ALPHA as an argument
        c0, c1, x0, x1 = cond[sa], cond[sb], xT[sa], xT[sb]
        alpha = torch.tensor([ALPHA], dtype=torch.float32)
        intp = c0[None] * (1 - alpha[:, None]) + c1[None] * alpha[:, None]
        theta = torch.arccos(cosv(x0, x1))
        x_shape = x0.shape
        intp_x = (torch.sin((1 - alpha[:, None]) * theta) * x0.flatten(0, 2)[None] +
                  torch.sin(alpha[:, None] * theta) * x1.flatten(0, 2)[None]) / torch.sin(theta)
        return intp[0], intp_x.view(-1, *x_shape)[0], float(theta)

    def codes_for(j):
        """(z, x, theta) of a job, or None with a reason if not finite (checked before rendering)."""
        sa, sb, m = j["src_a"], j["src_b"], j["mode"]
        if sa in bad_codes or (sb and sb in bad_codes):
            return None, "nonfinite source code"
        if m == "rec":
            return (cond[sa], xT[sa], ""), ""
        if m == "fresh":
            return (cond[sa], fresh[(j["host"], int(j["fresh_k"]))], ""), ""
        theta = float(torch.arccos(cosv(xT[sa], xT[sb])))
        if not np.isfinite(theta) or abs(np.sin(theta)) < 1e-6:
            return None, f"mixing angle {theta}"
        c_, x_, t_ = interp(sa, sb, float(j["alpha"]))
        if not (torch.isfinite(c_).all() and torch.isfinite(x_).all()):
            return None, "nonfinite mix"
        if m == "mix":
            return (c_, x_, round(t_, 6)), ""
        if m == "noise":
            return (cond[sa], x_, round(t_, 6)), ""
        return (c_, xT[sa], round(t_, 6)), ""       # sem

    rows, per, skipped = [], {}, []
    pools = list(dict.fromkeys(j["pool"] for j in jobs))
    with torch.no_grad():
        for pool in pools:
            pj = [j for j in jobs if j["pool"] == pool]
            steps = {int(j["steps"]) for j in pj}
            if len(steps) != 1:
                sys.exit(f"pool {pool} mixes step counts {steps}")
            steps = steps.pop()
            (out / pool).mkdir(parents=True, exist_ok=False)
            per[pool] = [0, 0.0, steps]
            ok = []
            for j in pj:
                cd, why = codes_for(j)
                if cd is None:
                    skipped.append({"pool": pool, "name": j["name"], "reason": why})
                    rows.append({**{c: j[c] for c in COLS}, "theta_xT": "", "finite": 0, "std01": "", "fresh_seed": "",
                                 "sha256": "", "note": why})
                else:
                    ok.append((j, cd))
            for i in range(0, len(ok), a.bs):
                chunk = ok[i:i + a.bs]
                t1 = time.time()
                pred = model.render(torch.stack([cd[1] for _, cd in chunk]).to(device),
                                    torch.stack([cd[0] for _, cd in chunk]).to(device), T=steps)
                sync()
                per[pool][0] += len(chunk)
                per[pool][1] += time.time() - t1
                for k, (j, cd) in enumerate(chunk):
                    p = pred[k]
                    fin = bool(torch.isfinite(p).all())
                    f = out / pool / j["name"]
                    if f.exists():
                        sys.exit(f"refusing to overwrite {f}")
                    save_image(p, str(f))
                    rows.append({**{c: j[c] for c in COLS}, "theta_xT": cd[2], "finite": int(fin),
                                 "std01": round(float(p.float().std()), 5),
                                 "fresh_seed": fresh_seed(j["host"], int(j["fresh_k"])) if j["mode"] == "fresh" else "",
                                 "sha256": fsha(f), "note": ""})
            print(f"pool {pool}: {per[pool][0]} images, {per[pool][1]:.0f}s", flush=True)
    log["decode"] = {p: {"images": v[0], "seconds": v[1], "steps": v[2], "s_per_image": v[1] / max(1, v[0])}
                     for p, v in per.items()}
    log["skipped"] = skipped
    log["all_finite"] = bool(all(r["finite"] for r in rows)) and not bad_codes
    log["elapsed_s"] = time.time() - t_all
    with open(out / "gen_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    json.dump(log, open(out / "gen_log.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in log.items() if k != "decode"}, indent=1))
    if not log["all_finite"]:
        sys.exit("non-finite codes, mixing angle or image (outputs written; see gen_log.json)")


if __name__ == "__main__":
    main()
