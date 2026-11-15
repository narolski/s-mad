"""PN1 amendment 13 (HN2, FFHQ only): the scoring list and a small pack of existing aligned FFHQ-Morphs frames.
Rows (nothing is built; files of /mnt/t7/smad_heldout/ffhq_morphs, each checked against its SHA256SUMS):
  ffhq_bona orig           2,000  label 0   (FFHQ-1024 bona fide, aligned at native resolution)      -> rule
  landmark_complete orig   1,000  label 1   (FFHQ-Morphs landmark-complete morphs, native 256 px)     -> rule
  landmark_complete resmatch 2,000 label 0  (the same bona fide shrunk to the morphs' native eye distance) -> printed only
Persons: the bona fide keys are disjoint from every morph contributor (checked here), so the within-source AUC compares
disjoint persons. Out: /mnt/t7/smad_next/PN1/pn1_hn2.tar (+ .sha256) with
  pn1h/data/eval/hn2/<id>.png, pn1h/data/manifests/pn1_hn2.csv, pn1h/SHA256SUMS
  python3 -I build_hn2_pack.py"""
import csv
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

FQ = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs")
PN1 = pathlib.Path("/mnt/t7/smad_next/PN1")
SEL = (("ffhq_bona", "orig", "0"), ("landmark_complete", "orig", "1"), ("landmark_complete", "resmatch", "0"))


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    sums = {}
    for line in open(FQ / "SHA256SUMS"):
        h, p = line.rstrip("\n").split("  ", 1)
        sums[p] = h
    rows = [r for r in csv.DictReader(open(FQ / "manifests" / "ffhqm.csv")) if (r["family"], r["variant"], r["label"]) in SEL]
    meta = {r["id"]: r for r in csv.DictReader(open(FQ / "manifests" / "ffhqm_meta.csv"))}
    bona = {pathlib.Path(r["path"]).name.split("_")[0] for r in rows if r["label"] == "0"}
    contrib = set()
    for r in rows:
        if r["label"] == "1":
            m = meta[r["id"]]
            contrib |= {m["key_x"], m["key_y"]}
    assert not (bona & contrib), "bona fide keys overlap morph contributors"
    tree = PN1 / "hn2_tree"
    if tree.exists():
        shutil.rmtree(tree)                      # only symlinks and small files made by this script
    root = tree / "pn1h"
    (root / "data" / "eval" / "hn2").mkdir(parents=True)
    (root / "data" / "manifests").mkdir(parents=True)
    out, ss = [], []
    for r in sorted(rows, key=lambda x: x["id"]):
        src = FQ / r["path"]
        h = sha(src)
        assert h == sums[r["path"]], r["path"]
        pp = f"data/eval/hn2/{r['id']}.png"
        os.symlink(src, root / pp)
        ss.append((h, pp))
        kl = "attack" if r["label"] == "1" else "genuine"
        out.append(dict(id=r["id"], path=f"eval/hn2/{r['id']}.png", label=r["label"], klass=kl, role="hn2", fam="ffhq",
                        rung=f"{r['family']}_{r['variant']}", strength="", tool=r["family"], cell="ffhqm",
                        host=(pathlib.Path(r["path"]).name.split("_")[0] if r["label"] == "0" else meta[r["id"]]["key"]),
                        neutral=""))
    mf = root / "data" / "manifests" / "pn1_hn2.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    ss.append((sha(mf), "data/manifests/pn1_hn2.csv"))
    with open(root / "SHA256SUMS", "w") as f:
        for h, p in ss:
            f.write(f"{h}  {p}\n")
    tar = PN1 / "pn1_hn2.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-12 00:00:00", "pn1h"], check=True)
    th = sha(tar)
    (PN1 / "pn1_hn2.tar.sha256").write_text(f"{th}  pn1_hn2.tar\n")
    print("rows", len(out), {k: sum(1 for r in out if r["rung"] == f"{k[0]}_{k[1]}") for k in SEL})
    print("list_sha256", sha(mf))
    print("pack_sha256", th)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
