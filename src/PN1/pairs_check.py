"""PN1 pair-term inertness check (note in prereg.md, commit fb818c4): training images only.
B and Sb at seeds 401, 402 (result tars of pn1a / pn1b, unpacked); pairs from train_Sb.csv of the FS1 tree.
Prints median |dz| and |dcos| (1 - cos on the L2-normalised head input) per pair type, eval mode and train mode
(LoRA dropout on), and the null pairs (a, a).
  SMAD_DATA=/mnt/t7/smad_next/PN1/fs_tree/pn1/data HF_HOME=/mnt/t7/smad_next/PN1/fs_tree/pn1/hf HF_HUB_OFFLINE=1 \
  python pairs_check.py -> experiments/PN1_.../tier1/pairs_check.json"""
import csv
import json
import pathlib
import sys

import numpy as np

T = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
U = pathlib.Path("/mnt/t7/smad_next/PN1/results_rented/unpacked")
OUT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/tier1/pairs_check.json")


def main():
    sys.path.insert(0, str(T / "code" / "smadcvpr"))
    sys.path.insert(0, "/home/narolski/smad-next/src/PN1")
    import torch
    import torch.nn.functional as F
    from torch.utils.data import DataLoader
    import common as C
    import pn1lib as K
    torch.set_num_threads(4)
    rows = {r["id"]: r for r in csv.DictReader(open(T / "data" / "manifests" / "train_Sb.csv"))}
    host = {r["id"]: r["host"] for r in K.catalog() if r["fam"] == "ladder"}
    pairs = {"genuine_photo_61": [], "genuine_half_61": [], "genuine_R0_R2w": [], "morph_u50_61": [], "null": []}
    for i, r in rows.items():
        if i.endswith("_fm61"):
            b = i[: -len("_fm61")]
            if b in rows:
                k = {"af0_photo61": "genuine_photo_61", "af0_half61": "genuine_half_61", "af0_u5061": "morph_u50_61"}[r["kind"]]
                pairs[k].append((b, i))
    r0 = {host[i]: i for i, r in rows.items() if r["kind"] == "lad_R0"}
    for i, r in rows.items():
        if r["kind"] == "lad_R2w" and host.get(i) in r0:
            pairs["genuine_R0_R2w"].append((r0[host[i]], i))
    photos = sorted(i for i, r in rows.items() if r["kind"] == "af0_photo")[:50]
    pairs["null"] = [(i, i) for i in photos]
    ids = sorted({x for v in pairs.values() for p in v for x in p})
    out = {"n_pairs": {k: len(v) for k, v in pairs.items()}}
    dev = "cuda"
    for arm in ("B", "Sb"):
        for seed in (401, 402):
            d = U / f"PN1_{arm}_s{seed}"
            meta = json.load(open(d / "meta.json"))
            meta["arch_extra"] = dict(meta.get("arch_extra") or {}, weights="file:" + str(T / "hf" / "a12" / "vit_base_patch16_clip_224.openai.safetensors"))
            model, _ = C.build_run_model(meta)
            tr = torch.load(d / "last_trainable.pt", map_location="cpu", weights_only=True)
            model.load_state_dict(tr, strict=False)
            model.to(dev)
            res = {}
            for mode in ("eval", "train"):
                model.train(mode == "train")
                torch.manual_seed(0)
                dl = DataLoader(C.ImageItems([(rows[i]["path"], 0) for i in ids], meta["res"]), batch_size=64, num_workers=4)
                Z, Fs = [], []
                with torch.no_grad():
                    for x, _ in dl:
                        x = x.to(dev)
                        f = F.normalize(model.net((x - model.mean) / model.std), dim=-1)
                        Z.append(model.head.cls(f).squeeze(-1).float().cpu()); Fs.append(f.float().cpu())
                Z = torch.cat(Z).numpy(); Fs = torch.cat(Fs).numpy()
                ix = {i: k for k, i in enumerate(ids)}
                if mode == "train":      # null pairs in train mode: a second independent pass over the null images
                    dl2 = DataLoader(C.ImageItems([(rows[i]["path"], 0) for i in photos], meta["res"]), batch_size=64, num_workers=2)
                    with torch.no_grad():
                        x = next(iter(dl2))[0].to(dev)
                        f2 = F.normalize(model.net((x - model.mean) / model.std), dim=-1)
                        z2 = model.head.cls(f2).squeeze(-1).float().cpu().numpy(); f2 = f2.float().cpu().numpy()
                rr = {}
                for k, v in pairs.items():
                    a = np.array([ix[p] for p, _ in v]); b = np.array([ix[q] for _, q in v])
                    if k == "null" and mode == "train":
                        dz = np.abs(Z[a] - z2); dc = 1 - (Fs[a] * f2).sum(1)
                    else:
                        dz = np.abs(Z[a] - Z[b]); dc = 1 - (Fs[a] * Fs[b]).sum(1)
                    rr[k] = dict(median_abs_dz=float(np.median(dz)), median_dcos=float(np.median(dc)), mean_z_a=float(Z[a].mean()))
                res[mode] = rr
            res["head_w_norm"] = float(model.head.cls.weight.norm())
            out[f"{arm}_s{seed}"] = res
            print(arm, seed, {m: {k: (round(v["median_abs_dz"], 4), round(v["median_dcos"], 5)) for k, v in res[m].items()} for m in ("eval", "train")}, flush=True)
            del model
            torch.cuda.empty_cache()
    g = [out[f"{a}_s{s}"]["eval"][k]["median_abs_dz"] for a in ("B", "Sb") for s in (401, 402)
         for k in ("genuine_photo_61", "genuine_half_61", "genuine_R0_R2w")]
    out["prestated"] = dict(rule="logit term inert if median |dz| of genuine pairs (eval) < 0.05",
                            genuine_pair_medians=g, inert=bool(max(g) < 0.05))
    OUT.write_text(json.dumps(out, indent=1))
    print("prestated", out["prestated"])


if __name__ == "__main__":
    main()
