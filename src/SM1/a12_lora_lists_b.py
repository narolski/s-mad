"""SM1 amendment A12 item 12: manifests for the ViT-B/16 LoRA fits of arms b and b' (seeds 401, 402), in the format of
lora_lists.py (the composition of compose.py), plus the unchanged evaluation manifests (copied from the v2 folder,
sha256 checked against OUT/lora/lists.json). Every training path must be inside sm1gpu_img_base.tar or
sm1gpu_img_armsb.tar (checked against their file lists).

  python3 -I a12_lora_lists_b.py -> OUT/lora/manifests_b/*.csv, OUT/gpupack/sm1lora_manifests_b.tar (+ .sha256)
"""
import csv
import hashlib
import json
import pathlib
import shutil
import sys
import tarfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import lora_lists as LL  # noqa: E402

ARMS = ("b", "bp")
SEEDS = (401, 402)


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    path = {}
    for n in ("train_bf", "train_armb", "train_armbp"):
        for r in csv.DictReader(open(LL.FL / f"{n}.csv")):
            path[r["id"]] = "x/" + r["path"].lstrip("/")
    packed = set()
    for s in ("base", "armsb"):
        packed |= {ln.strip().lstrip("/") for ln in open(K.OUT / f"gpupack/filelist_{s}.txt")}
    od = K.OUT / "lora/manifests_b"
    od.mkdir(parents=True, exist_ok=True)
    info = {}
    for arm in ARMS:
        for s in SEEDS:
            c = json.load(open(K.OUT / "compose" / f"{arm}_s{s}.json"))
            rows = [dict(path=path[i], label=0, source="smdd", tool="smdd", arm=f"sm1{arm}", val=0, mixed=0)
                    for i in c["genuine"]] + \
                   [dict(path=path[i], label=1, source="smdd", tool=f"sm1{arm}", arm=f"sm1{arm}", val=0, mixed=0)
                    for i in c["morph"]]
            miss = [r["path"] for r in rows if r["path"][2:] not in packed]
            assert not miss, (arm, s, len(miss), miss[:3])
            f = od / f"train_sm1{arm}_s{s}.csv"
            with open(f, "w", newline="") as fo:
                w = csv.DictWriter(fo, fieldnames=LL.COLS, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
            info[f.name] = dict(n=len(rows), n_morph=len(c["morph"]), sha256=K.sha(f))
    old = json.load(open(K.OUT / "lora/lists.json"))
    for n in ("sm1_ar1_eval.csv", "sm1_jpeg_eval.csv"):
        shutil.copy2(K.OUT / "lora/manifests" / n, od / n)
        assert K.sha(od / n) == old[n]["sha256"], n
        info[n] = old[n]
    tp = K.OUT / "gpupack/sm1lora_manifests_b.tar"
    with tarfile.open(tp, "w") as t:
        for f in sorted(od.glob("*.csv")):
            t.add(f, arcname=f.name)
    sha = hashlib.sha256(open(tp, "rb").read()).hexdigest()
    (tp.parent / (tp.name + ".sha256")).write_text(f"{sha}  {tp.name}\n")
    info["tar"] = dict(path=str(tp), sha256=sha)
    json.dump(info, open(K.OUT / "lora/lists_b.json", "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
