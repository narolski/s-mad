"""PRIVATE helper: copies the 20 morph-free networks (LoRA tensors + head) into the release repo with a sanitised
meta.json (configuration keys only; no paths, hosts or job ids) and a SHA256SUMS file.
  python3 -I copy_morph_free_weights.py <release-repo>/weights/morph_free"""
import hashlib, json, pathlib, shutil, sys
SRC = pathlib.Path("/home/narolski/smad-next/weights")
OUT = pathlib.Path(sys.argv[1])
KEEP = ["seed", "res", "steps", "bs", "accum", "lr", "head_lr", "wd", "clip_grad", "aug", "sched", "final", "lora_r",
        "lora_alpha", "lora_dropout", "lora_rs", "lora_targets", "lora_train_norms", "pos_weight", "n_items", "label_smoothing", "opt"]
sums = []
for d, bb in (("morph_free_b16", "vitb16"), ("morph_free_l14", "vitl14")):
    for src in sorted((SRC / d).glob("AD4_*")):
        arm = "perm" if "perm" in src.name else "mf"
        s = src.name.rsplit("_s", 1)[1]
        name = f"{bb}_{'label_permuted_' if arm == 'perm' else ''}s{s}"
        dst = OUT / name; dst.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / "last_trainable.pt", dst / "last_trainable.pt")
        m = json.load(open(src / "meta.json"))
        meta = {"backbone": bb, "training_list": "train_morph_free_perm_s%s.csv" % s if arm == "perm" else "train_morph_free.csv"}
        meta.update({k: m[k] for k in KEEP})
        json.dump(meta, open(dst / "meta.json", "w"), indent=1)
        sums.append(f"{hashlib.sha256((dst / 'last_trainable.pt').read_bytes()).hexdigest()}  {name}/last_trainable.pt")
(OUT / "SHA256SUMS").write_text("\n".join(sums) + "\n")
print(len(sums), "networks")
