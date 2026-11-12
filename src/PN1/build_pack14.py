"""PN1 amendment 14 (draft): one small pack for one rented lease, existing files only (nothing is built).
  pn14/code/**, pn14/hf/**          from pack 2 (each file checked against pack 2's SHA256SUMS)
  pn14/nets/PN1_<arm>_s<seed>/{meta.json,last_trainable.pt}   the 12 networks A, B, Bn, C, Sb, Bv x 401, 402, from their
                                    verified result tars (sha256 listed)
  pn14/data/eval/**                 the 4,365 splice rows of pack 2 (fam splice), the amendment-13 HN2 list (fam ffhq),
                                    FFHQ-Morphs landmark_combined orig 1,000 + resmatch 2,000 (fam ffhq_lcomb)
  pn14/data/manifests/pn1_a14.csv   one manifest (pn1_eval.csv columns)
  pn14/SHA256SUMS
Out /mnt/t7/smad_next/PN1/pn1_a14.tar (+ .sha256).   python3 -I build_pack14.py"""
import csv
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

PN1 = pathlib.Path("/mnt/t7/smad_next/PN1")
P2 = PN1 / "pack2_tree" / "pn1"
HN2 = PN1 / "hn2_tree" / "pn1h"
FQ = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs")
U = PN1 / "results_rented" / "unpacked"
NETS = [f"PN1_{a}_s{s}" for s in (401, 402) for a in ("A", "B", "Bn", "C", "Sb", "Bv")]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    p2sums = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(P2 / "SHA256SUMS"))
    fqsums = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(FQ / "SHA256SUMS"))
    tree = PN1 / "a14_tree"
    if tree.exists():
        shutil.rmtree(tree)                    # only symlinks and small files made by this script
    root = tree / "pn14"
    sums = []

    def link(pp, src, expect=None):
        dst = root / pp
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.realpath(src), dst)
        h = sha(src)
        if expect is not None:
            assert h == expect, (src, h, expect)
        sums.append((h, pp))

    for p, h in sorted(p2sums.items()):
        if p.startswith(("code/", "hf/")):
            link(p, P2 / p, h)
    for n in NETS:
        for f in ("meta.json", "last_trainable.pt"):
            link(f"nets/{n}/{f}", U / n / f)
    cols = None
    rows = []
    for r in csv.DictReader(open(P2 / "data" / "manifests" / "pn1_eval.csv")):
        cols = list(r)
        if r["fam"] == "splice":
            link("data/" + r["path"], P2 / "data" / r["path"], p2sums["data/" + r["path"]])
            rows.append(r)
    for r in csv.DictReader(open(HN2 / "data" / "manifests" / "pn1_hn2.csv")):
        link("data/" + r["path"], HN2 / "data" / r["path"])
        rows.append(r)
    for r in csv.DictReader(open(FQ / "manifests" / "ffhqm.csv")):
        if r["family"] != "landmark_combined":
            continue
        pp = f"eval/a14/{r['id']}.png"
        link("data/" + pp, FQ / r["path"], fqsums[r["path"]])
        key = pathlib.Path(r["path"]).name.split("_")[0] if r["label"] == "0" else pathlib.Path(r["path"]).stem.rsplit("_", 1)[0]
        rows.append(dict(id="lcomb_" + r["id"], path=pp, label=r["label"], klass="attack" if r["label"] == "1" else "genuine",
                         role="a14", fam="ffhq_lcomb", rung=f"landmark_combined_{r['variant']}", strength="",
                         tool="landmark_combined", cell="ffhqm", host=key, neutral=""))
    assert len({r["id"] for r in rows}) == len(rows)
    mf = root / "data" / "manifests" / "pn1_a14.csv"
    mf.parent.mkdir(parents=True, exist_ok=True)
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    sums.append((sha(mf), "data/manifests/pn1_a14.csv"))
    with open(root / "SHA256SUMS", "w") as f:
        for h, p in sums:
            f.write(f"{h}  {p}\n")
    tar = PN1 / "pn1_a14.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-12 00:00:00", "pn14"], check=True)
    th = sha(tar)
    (PN1 / "pn1_a14.tar.sha256").write_text(f"{th}  pn1_a14.tar\n")
    import collections
    print("rows", len(rows), dict(collections.Counter((r["fam"], r["label"]) for r in rows)))
    print("list_sha256", sha(mf))
    print("pack_sha256", th, tar.stat().st_size)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
