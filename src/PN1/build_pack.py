"""PN1 tier-1 pack: one tar `pn1_pack.tar` with
  pn1/code/**            the AD4 pack's code (smadcvpr/*.py, morphmamba/**), each file checked against ad4/SHA256SUMS
  pn1/hf/a12/vit_base_patch16_clip_224.openai.safetensors   (the AD4 pack's converted ViT-B/16 weights, hash-checked)
  pn1/src/pn1_score.py   the PN1 scorer
  pn1/data/{train,eval}/...  images (pack_files.csv: pack path -> source file)
  pn1/data/manifests/{train_A,train_B,train_C,pn1_eval}.csv
  pn1/SHA256SUMS         sha256 of every file above (relative to pn1/)
Built from a symlink tree (/mnt/t7/smad_next/PN1/pack_tree) with `tar -h` (no image is copied on the T7 drive), fixed
order, owner and time. Writes /mnt/t7/smad_next/PN1/pn1_pack.tar and .sha256.
  python3 -I build_pack.py [--limit 8]     (--limit: a test pack of 8 training rows per manifest and 8 eval rows)
"""
import argparse
import csv
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

PN1 = pathlib.Path("/mnt/t7/smad_next/PN1")
AD4X = pathlib.Path("/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/ad4")
SRC = pathlib.Path("/home/narolski/smad-next/src/PN1")
FORBID = ("fst", "valx", "a12sp", "a12-sp")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    tag = f"_limit{a.limit}" if a.limit else ""
    tree = PN1 / f"pack_tree{tag}"
    if tree.exists():
        shutil.rmtree(tree)                       # only symlinks and small copies made by this script
    root = tree / "pn1"
    ad4sums = {}
    for line in open(AD4X / "SHA256SUMS"):
        h, p = line.rstrip("\n").split("  ", 1)
        ad4sums[p] = h
    sums = []

    def link(pack_path, src, expect=None):
        dst = root / pack_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(src, dst)
        h = sha(src)
        if expect is not None:
            assert h == expect, (src, h, expect)
        sums.append((h, pack_path))

    for p, h in sorted(ad4sums.items()):
        if p.startswith("code/"):
            assert not any(f in p.lower() for f in FORBID)
            link(p, str(AD4X / p), h)
    w = "hf/a12/vit_base_patch16_clip_224.openai.safetensors"
    link(w, str(AD4X / w), ad4sums[w])
    link("src/pn1_score.py", str(SRC / "pn1_score.py"))
    M = PN1 / "manifests"
    keep = None
    mans = {}
    for n in ("train_A", "train_B", "train_Bn", "train_C", "pn1_eval"):
        f = M / f"{n}.csv"
        if not f.exists():
            print("missing manifest", f)
            continue
        rows = list(csv.DictReader(open(f)))
        if a.limit:                # test pack: limit/2 unique rows per class, repeated to 512 rows (2 batches of 256)
            if n == "pn1_eval":
                rows = rows[:: max(1, len(rows) // a.limit)][:a.limit]
            else:
                u = [r for r in rows if r["label"] == "0"][:a.limit // 2] + [r for r in rows if r["label"] == "1"][:a.limit // 2]
                rows = (u * (512 // len(u) + 1))[:512]
        mans[n] = rows
    files = {r["pack_path"]: r["source"] for r in csv.DictReader(open(M / "pack_files.csv"))}
    need = sorted({r["path"] for rows in mans.values() for r in rows})
    for p in need:
        link("data/" + p, files[p])
    for n, rows in mans.items():
        dst = root / "data" / "manifests" / f"{n}.csv"
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, "w", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            wr.writeheader()
            wr.writerows(rows)
        sums.append((sha(dst), f"data/manifests/{n}.csv"))
    with open(root / "SHA256SUMS", "w") as fh:
        for h, p in sorted(sums, key=lambda x: x[1]):
            fh.write(f"{h}  {p}\n")
    out = PN1 / f"pn1_pack{tag}.tar"
    subprocess.run(["tar", "-chf", str(out), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-11 00:00:00", "-C", str(tree), "pn1"], check=True)
    h = sha(out)
    (PN1 / f"pn1_pack{tag}.tar.sha256").write_text(f"{h}  pn1_pack.tar\n")
    print("PACK", out, os.path.getsize(out), h, "files", len(sums))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
