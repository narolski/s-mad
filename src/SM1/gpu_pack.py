"""SM1: build the self-contained GPU feature pack (amendment A7) from the feature lists in OUT/flists.

  python3 -I gpu_pack.py code                  -> OUT/gpupack/sm1gpu_code.tar (+ .sha256): MANIFEST.json, code, weights,
                                                  lists/<name>.csv (id, rel) for every flist present
  python3 -I gpu_pack.py images SET name,...   -> OUT/gpupack/sm1gpu_img_<SET>.tar (+ .sha256): the images of those lists
                                                  under images/<absolute path without the leading slash>
On the GPU machine: mkdir pack; tar -C pack -xf sm1gpu_code.tar; for each image tar: tar -C pack/images -xf ...
(the image tars hold paths without "images/"), then python feats_gpu.py --pack pack --out out.
"""
import csv
import hashlib
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
FL = K.OUT / "flists"
GP = K.OUT / "gpupack"
WEIGHTS = pathlib.Path("/home/narolski/.cache/huggingface/hub/models--timm--vit_large_patch14_clip_224.openai/blobs/"
                       "eb70c15b117effa76315db43fcbd9f32a655292fc861798343939a02f561c6ae")
CODE = {"code/feats_gpu.py": HERE / "feats_gpu.py", "code/common.py": K.W46 / "smadcvpr/common.py",
        "code/a12_released.py": K.W46 / "smadcvpr/a12_released.py"}
SKIP = ("tab", "tab_sub", "tab_smoke8", "smoke_audit", "train_arma")   # arma = subset of train_m15k


def write_sha(p):
    h = K.sha(p)
    (p.parent / (p.name + ".sha256")).write_text(f"{h}  {p.name}\n")
    return h


def lists():
    out = {}
    for f in sorted(FL.glob("*.csv")):
        if f.stem in SKIP or f.stem.startswith("smoke_"):
            continue
        rows = list(csv.DictReader(open(f)))
        out[f.stem] = [dict(id=r["id"], rel=r["path"].lstrip("/")) for r in rows]
    return out


def code():
    GP.mkdir(parents=True, exist_ok=True)
    src = GP / "code_src"
    if src.exists():
        shutil.rmtree(src)
    (src / "code").mkdir(parents=True)
    (src / "weights").mkdir()
    (src / "lists").mkdir()
    man = {"code_and_weights": {}, "lists": {}}
    for rel, p in CODE.items():
        shutil.copy2(p, src / rel)
        man["code_and_weights"][rel] = K.sha(src / rel)
    wrel = "weights/vit_large_patch14_clip_224.openai.bin"
    shutil.copy2(WEIGHTS, src / wrel)
    man["code_and_weights"][wrel] = K.sha(src / wrel)
    for name, rows in lists().items():
        with open(src / "lists" / f"{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "rel"])
            w.writeheader()
            w.writerows(rows)
        man["lists"][name] = dict(n=len(rows), sha256=K.sha(src / "lists" / f"{name}.csv"))
    json.dump(man, open(src / "MANIFEST.json", "w"), indent=1)
    t = GP / "sm1gpu_code.tar"
    with tarfile.open(t, "w") as tf:
        tf.add(src, arcname=".")
    print(json.dumps(dict(tar=str(t), sha256=write_sha(t), lists={k: v["n"] for k, v in man["lists"].items()}), indent=1))


def images(setname, names):
    GP.mkdir(parents=True, exist_ok=True)
    L = lists()
    files = sorted({"/" + r["rel"] for n in names for r in L[n]})
    missing = [p for p in files if not pathlib.Path(p).exists()]
    if missing:
        sys.exit(f"{len(missing)} files missing, e.g. {missing[:3]}")
    fl = GP / f"filelist_{setname}.txt"
    fl.write_text("\n".join(files) + "\n")
    t = GP / f"sm1gpu_img_{setname}.tar"
    r = subprocess.run(["tar", "-cf", str(t), "-T", str(fl)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr[-2000:])
    print(json.dumps(dict(tar=str(t), n_files=len(files), bytes=t.stat().st_size, sha256=write_sha(t), lists=names)))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    if sys.argv[1] == "code":
        code()
    else:
        images(sys.argv[2], sys.argv[3].split(","))
