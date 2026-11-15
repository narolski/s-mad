"""PN1: tar for the DINOv3 tier-0 features that the DGX GPU allowance (0.5 GPU-hours) could not cover, extracted inside
the Athena smoke job (prereg section 3). Contents (featx/):
  feat.py (AF0's extractor, byte copy, sha256 4529c523...), featmean.py (PN1), featx_run.py (job list),
  hf/hub/models--timm--vit_large_patch16_dinov3.lvd1689m/ (the local timm cache, safetensors weights),
  lists/<name>.csv with relative image paths img/<name>/<id>.png, img/ (dereferenced), SHA256SUMS.
Lists: eq64 (64 images whose DGX DINOv3 means exist: the platform check), and the sets named on the command line.
  python3 -I build_featx.py r2w4_td=/mnt/t7/smad_next/PN1/lists/r2w4_td.csv soft=/mnt/t7/smad_next/AF0/lists/soft.csv ...
"""
import csv
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

PN1 = pathlib.Path("/mnt/t7/smad_next/PN1")
SRC = pathlib.Path("/home/narolski/smad-next/src/PN1")
AF0FEAT = pathlib.Path("/home/narolski/smad-next/src/AF0/feat.py")
HUB = pathlib.Path("/home/narolski/.cache/huggingface/hub/models--timm--vit_large_patch16_dinov3.lvd1689m")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    tree = PN1 / "featx_tree"
    if tree.exists():
        shutil.rmtree(tree)
    root = tree / "featx"
    (root / "lists").mkdir(parents=True)
    jobs = [a.split("=", 1) for a in sys.argv[1:]]
    # platform check set: 32 ladder rows + 32 AF0 rows that already have DGX DINOv3 means (AF0 caches via PD1)
    eq = []
    ar1 = list(csv.DictReader(open("/mnt/t7/smad_next/AF0/lists/ar1.csv")))
    w1 = list(csv.DictReader(open("/mnt/t7/smad_next/AF0/lists/af0_w1.csv")))
    eq = ar1[:: len(ar1) // 32][:32] + w1[:: len(w1) // 32][:32]
    lists = {"eq64": eq}
    for name, lst in jobs:
        lists[name] = list(csv.DictReader(open(lst)))
    names = []
    for name, rows in lists.items():
        out = []
        for r in rows:
            rel = f"img/{name}/{r['id']}.png"
            d = root / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(r["path"], d)
            out.append(dict(id=r["id"], path=rel))
        with open(root / "lists" / f"{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["id", "path"])
            w.writeheader()
            w.writerows(out)
        names.append(name)
    shutil.copy2(AF0FEAT, root / "feat.py")
    shutil.copy2(SRC / "featmean.py", root / "featmean.py")
    run = ["import os, subprocess, sys",
           "os.environ['PN1_AF0FEAT'] = os.path.abspath('feat.py')",
           "os.environ.setdefault('PN1_FEAT_OUT', os.path.abspath('out'))",
           "args = [sys.executable, '-I', 'featmean.py', '--backbone', 'dinov3_512', '--bs', '32', '--workers', '6']",
           f"for n in {names!r}:",
           "    args += ['--job', f'{n}=lists/{n}.csv']",
           "sys.exit(subprocess.call(args))"]
    (root / "featx_run.py").write_text("\n".join(run) + "\n")
    hub = root / "hf" / "hub" / HUB.name
    shutil.copytree(HUB, hub, symlinks=True)        # blobs + snapshot symlinks; tar -h dereferences
    sums = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            sums.append(f"{sha(p)}  {p.relative_to(root)}")
    (root / "SHA256SUMS").write_text("\n".join(sums) + "\n")
    out = PN1 / "featx.tar"
    subprocess.run(["tar", "-chf", str(out), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-11 00:00:00", "-C", str(tree), "featx"], check=True)
    (PN1 / "featx.tar.sha256").write_text(f"{sha(out)}  featx.tar\n")
    print("FEATX", out, os.path.getsize(out), {k: len(v) for k, v in lists.items()})


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
