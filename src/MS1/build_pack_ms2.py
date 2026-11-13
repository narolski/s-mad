"""MS1 pack for the training comparison (prereg part 2): development data only, existing files only.

pn1/code/**, pn1/hf/**, pn1/src/pn1_score.py  from the FS1 tree (/mnt/t7/smad_next/PN1/fs_tree, checked against its
                                              SHA256SUMS)
pn1/data/train/**                             the images of train_Sb (FS1 tree) + the FFHQ training images of SbM3
pn1/data/manifests/train_Sb.csv               byte-equal to FS1's (2cf3fda3...)
pn1/data/manifests/train_SbM3.csv             OUT/manifests/train_SbM3.csv
pn1/data/manifests/train_SbV.csv              OUT/manifests/train_SbV.csv (data-volume control; Sb images only)
pn1/data/manifests/pn1_eval.csv               FS1's 19,797 development rows (f0f29f22...) + the MS1 FFHQ hold-out rows
                                              (fam ms1ffhq) + the TT1 aligned genuine photos (fam tt1, cell = family).
                                              No FRLL, MAD22, MorDIFF, DiM, H1, FEI or sealed row (asserted).
Out OUT/pn1_pack_ms2.tar (+ .sha256).   python3 -I build_pack_ms2.py
MS1 part 4 (WCSS H100): as build_pack.py plus train_SbM3S.csv and the CFD (fam cfd, 831) and KDEF (fam kdef, 140)
frames in the evaluation manifest, so that every score of part 4 is made in the fit job.
"""
import csv
import gzip
import os
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ms1common as C  # noqa: E402

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
FS_EVAL_SHA = "f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045"
TT1 = pathlib.Path("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/aligned_manifest.csv.gz")
TT1_SHA = "8b3c6fa932ac24c13a086984468539ba841f2facc1ac883be34c89b1c6971bef"   # of the uncompressed csv (TT1 summary)
BAD = ("frll", "mad22", "mordiff", "dim-", "h1_poisson", "/fei", "casia-webface", "casia_webface", "valx", "fst",
       "a12sp")


def holdout_rows():
    O = C.OUT / "ffhq"
    rows = []
    persons = [p for p in csv.DictReader(open(O / "persons.csv")) if p["part"] == "holdout"]
    for i, p in enumerate(persons):
        rows.append(dict(id=f"hold_ffhq_photo_{i:04d}", src=p["frame"], label="0", klass="genuine", rung="photo",
                         strength="", host=p["pid"]))
    for r in csv.DictReader(open(O / "lists/af0_pairs.csv")):
        if r["split"] == "hold":
            rows.append(dict(id=r["id"], src=r["image"], label="1" if r["field"] == "u50" else "0",
                             klass="attack" if r["field"] == "u50" else "single", rung=r["field"], strength="",
                             host=f"{r['pid_A']}|{r['pid_B']}"))
    log = {(r["src_id"], r["strength"]): r for r in csv.DictReader(open(O / "soft_log.csv"))}
    for r in csv.DictReader(open(O / "lists/soft.csv")):
        if r["split"] != "hold" or log.get((r["src_id"], r["strength"]), {}).get("aligned") == "False":
            continue
        if not pathlib.Path(r["out"]).exists():
            continue
        rows.append(dict(id=f"{r['src_id']}_{r['strength']}", src=r["out"], label="1" if r["kind"] == "u50" else "0",
                         klass="attack" if r["kind"] == "u50" else "genuine", rung=r["kind"], strength=r["strength"],
                         host=r["pid"]))
    return rows


def main():
    fs_sums = dict(reversed(line.rstrip("\n").split("  ", 1)) for line in open(FS / "SHA256SUMS"))
    assert C.sha(FS / "data/manifests/pn1_eval.csv") == FS_EVAL_SHA
    tree = C.OUT / "pack_tree_ms2"
    if tree.exists():
        shutil.rmtree(tree)                     # only symlinks and small files made by this script
    root = tree / "pn1"
    sums = []

    def link(pp, src, expect=None):
        dst = root / pp
        dst.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(os.path.realpath(src), dst)
        h = C.sha(src)
        assert expect is None or h == expect, src
        sums.append((h, pp))

    for p, h in sorted(fs_sums.items()):
        if p.startswith(("code/", "hf/", "src/")) or p == "data/manifests/train_Sb.csv":
            link(p, FS / p, h)
    for r in csv.DictReader(open(FS / "data/manifests/train_Sb.csv")):
        pp = "data/" + r["path"]
        if not (root / pp).exists():
            link(pp, FS / pp, fs_sums[pp])
    for r in csv.DictReader(open(C.OUT / "manifests/SbM3_files.csv")):
        pp = "data/" + r["pack_path"]
        assert not (root / pp).exists(), pp
        link(pp, r["source"], r["sha256"])
    link("data/manifests/train_SbM3.csv", C.OUT / "manifests/train_SbM3.csv")
    link("data/manifests/train_SbV.csv", C.OUT / "manifests/train_SbV.csv")
    link("data/manifests/train_SbM3S.csv", C.OUT / "manifests/train_SbM3S.csv")
    ev = list(csv.DictReader(open(FS / "data/manifests/pn1_eval.csv")))
    cols = list(ev[0])
    for r in ev:
        link("data/" + r["path"], FS / "data" / r["path"], fs_sums["data/" + r["path"]])
    n_fs = len(ev)
    for h in holdout_rows():
        pp = f"eval/ms1/{h['id']}.png"
        link("data/" + pp, h["src"])
        ev.append(dict({k: "" for k in cols}, id=h["id"], path=pp, label=h["label"], klass=h["klass"], role="dev",
                       fam="ms1ffhq", rung=h["rung"], strength=h["strength"], tool="af0engine", host=h["host"]))
    raw = gzip.open(TT1).read()
    assert __import__("hashlib").sha256(raw).hexdigest() == TT1_SHA
    import io
    ntt = 0
    for r in csv.DictReader(io.StringIO(raw.decode())):
        if r["aligned"] != "1":
            continue
        pp = f"eval/tt1/{r['id']}.png"
        link("data/" + pp, r["aligned_path"], r["aligned_sha256"])
        ev.append(dict({k: "" for k in cols}, id=r["id"], path=pp, label="0", klass="genuine", role="dev", fam="tt1",
                       rung="photo", cell=r["family"], host=r["person"]))
        ntt += 1
    for fam, ph in (("cfd", "d6ef6793b588fa981ccb27a575ead4b91ffad0f3fe2b2345973c8ec9866b75a9"),
                    ("kdef", "e54be768a2b1ab8cb6fc9e9812d6baf1e2009ca06ef35268bbbecd497589d8c3")):
        pool = C.OUT / fam / "pool.csv"
        assert C.sha(pool) == ph
        for r in csv.DictReader(open(pool)):
            if r["aligned"] != "1":
                continue
            pp = f"eval/{fam}/{r['id']}.png"
            link("data/" + pp, r["frame"], r["frame_sha256"])
            ev.append(dict({k: "" for k in cols}, id=r["id"], path=pp, label="0", klass="genuine", role="dev", fam=fam,
                           rung="photo", cell=fam, host=r["person"]))
    for r in ev:
        src = os.path.realpath(root / "data" / r["path"]).lower()
        assert not any(b in src for b in BAD), src
        assert ("/ffhq_morphs/" in src) or ("/smad_next/" in src), src
    mf = root / "data/manifests/pn1_eval.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(ev)
    sums.append((C.sha(mf), "data/manifests/pn1_eval.csv"))
    with open(root / "SHA256SUMS", "w") as f:
        for h, p in sums:
            f.write(f"{h}  {p}\n")
    tar = C.OUT / "pn1_pack_ms2.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "pn1"], check=True)
    th = C.sha(tar)
    (C.OUT / "pn1_pack_ms2.tar.sha256").write_text(f"{th}  pn1_pack_ms2.tar\n")
    import collections
    print("eval rows", len(ev), "fs", n_fs, "tt1", ntt, dict(collections.Counter((r["fam"], r["label"]) for r in ev)))
    print("eval_sha256", C.sha(mf))
    print("pack_sha256", th, tar.stat().st_size, "files", len(sums))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
