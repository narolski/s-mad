"""PN1 fresh seeds (registration FS1): development-only pack, existing files only (nothing is built).
  pn1/code/**, pn1/hf/**, pn1/src/pn1_score.py   from pack 2 (checked against pack 2's SHA256SUMS)
  pn1/data/train/**                              the images of train_A, train_B, train_Sb (pack 2)
  pn1/data/manifests/train_{A,B,Sb}.csv          byte-equal to pack 2
  pn1/data/manifests/pn1_eval.csv                DEVELOPMENT rows only: pack 2's af0, ladder and splice rows (our own
                                                 FRGC / colorFERET constructions) + the FFHQ development rows of the
                                                 amendment-14 list (HN2 list: ffhq_bona orig, landmark_complete orig and
                                                 resmatch; landmark_combined orig and resmatch). No FRLL, MAD22,
                                                 MorDIFF, DiM, H1, FEI or sealed row or image is in the pack (asserted).
Out /mnt/t7/smad_next/PN1/pn1_pack_fs.tar (+ .sha256).   python3 -I build_pack_fs.py"""
import csv
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

PN1 = pathlib.Path("/mnt/t7/smad_next/PN1")
P2 = PN1 / "pack2_tree" / "pn1"
A14 = PN1 / "a14_tree" / "pn14"
BAD = ("frllm", "mad22", "h1", "mordiff", "dim", "fei", "gtest", "valx", "fst", "a12sp", "casia")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    p2 = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(P2 / "SHA256SUMS"))
    a14 = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(A14 / "SHA256SUMS"))
    tree = PN1 / "fs_tree"
    if tree.exists():
        shutil.rmtree(tree)                     # only symlinks and small files made by this script
    root = tree / "pn1"
    sums = []

    def link(pp, src, expect):
        dst = root / pp
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.realpath(src), dst)
        assert sha(src) == expect, src
        sums.append((expect, pp))

    for p, h in sorted(p2.items()):
        if p.startswith(("code/", "hf/", "src/")):
            link(p, P2 / p, h)
    (root / "data" / "manifests").mkdir(parents=True)
    for arm in ("A", "B", "Sb"):
        m = f"data/manifests/train_{arm}.csv"
        for r in csv.DictReader(open(P2 / m)):
            pp = "data/" + r["path"]
            if not (root / pp).exists():
                link(pp, P2 / pp, p2[pp])
        link(m, P2 / m, p2[m])
    rows, cols = [], None
    for r in csv.DictReader(open(P2 / "data" / "manifests" / "pn1_eval.csv")):
        cols = list(r)
        if r["fam"] in ("af0", "ladder", "splice"):
            assert r["host"].split(":")[0] in ("frgc", "feret"), r
            link("data/" + r["path"], P2 / "data" / r["path"], p2["data/" + r["path"]])
            rows.append(r)
    for r in csv.DictReader(open(A14 / "data" / "manifests" / "pn1_a14.csv")):
        if r["fam"] in ("ffhq", "ffhq_lcomb"):
            link("data/" + r["path"], A14 / "data" / r["path"], a14["data/" + r["path"]])
            rows.append(r)
    for r in rows:
        src = os.path.realpath(root / "data" / r["path"]).lower()
        assert not any(b in r["id"].lower() or b in r["cell"].lower() for b in BAD), r["id"]
        assert ("/ffhq_morphs/" in src) or ("/smad_next/" in src), src
        assert not any(f"/{b}" in src for b in ("frll", "mad22", "h1_poisson", "mordiff", "dim-", "fei")), src
    mf = root / "data" / "manifests" / "pn1_eval.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    sums.append((sha(mf), "data/manifests/pn1_eval.csv"))
    with open(root / "SHA256SUMS", "w") as f:
        for h, p in sums:
            f.write(f"{h}  {p}\n")
    tar = PN1 / "pn1_pack_fs.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-12 00:00:00", "pn1"], check=True)
    th = sha(tar)
    (PN1 / "pn1_pack_fs.tar.sha256").write_text(f"{th}  pn1_pack_fs.tar\n")
    import collections
    print("eval rows", len(rows), dict(collections.Counter((r["fam"], r["label"]) for r in rows)))
    print("eval_sha256", sha(mf))
    print("pack_sha256", th, tar.stat().st_size, "files", len(sums))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
