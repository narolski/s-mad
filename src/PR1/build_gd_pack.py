"""PR1 GD0/GD1/GD2 scoring pack (prereg.md sections 6, 6a, "GD rows fixed"). Nothing is built: existing development
frames are linked, each checked against its source hash where one exists, and tarred (tar -h) with a manifest.
  GD0: FFHQ-Morphs stylegan_wplus, stylegan_w, diffae: orig morphs + that family's resmatch genuine (9,000 rows)
  GD1: PN1's DG1 test list /mnt/t7/smad_next/PN1/lists/dg1_test.csv (1,146 rows; hosts re-checked here)
  GD2: AG1 MIPGAN controls, FRGC/colorFERET, aligned, rungs R0 R2 R2s R3 R3m R4, persons outside PN1 training/validation
Out: /mnt/t7/smad_next/PR1/pr1_gd.tar (+ .sha256) holding pr1g/data/eval/gd/<id>.png, pr1g/data/manifests/pr1_gd.csv,
pr1g/SHA256SUMS.   python3 -I build_gd_pack.py [--limit8]"""
import csv
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

FQ = pathlib.Path("/mnt/t7/smad_heldout/ffhq_morphs")
DG1L = pathlib.Path("/mnt/t7/smad_next/PN1/lists/dg1_test.csv")
AG1 = pathlib.Path("/mnt/t7/smad_next/AG1/data")
AG1_MAN_SHA = "5892c91890c59eb0b7b47825c9f168a615b10f15dbe9eff5ac6fcd1ceb8b7246"
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split")
OUT = pathlib.Path("/mnt/t7/smad_next/PR1")
FORBID = ("fst", "valx", "a12sp", "a12-sp", "frll", "mad22", "mordiff", "/dim", "h1", "fei", "casia")
GD0_FAM = ("stylegan_wplus", "stylegan_w", "diffae")
GD2_RUNG = ("R0", "R2", "R2s", "R3", "R3m", "R4")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    lim = "--limit8" in sys.argv
    lad = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "ladder_split.csv"))}
    af = {r["pid"]: r for r in csv.DictReader(open(SPLIT / "af0_split.csv"))}

    def outside(p):                # not a PN1 training or validation person
        a, b = lad.get(p), af.get(p)
        if a and (a["role"] == "train" or a["is_val"] == "1" or a["train_genuine"] == "1" or a["train_morph"] == "1"):
            return False
        if b and (b["pn1_use"] == "train" or b["is_val"] == "1"):
            return False
        return True

    rows = []
    # GD0
    sums = {}
    for line in open(FQ / "SHA256SUMS"):
        h, p = line.rstrip("\n").split("  ", 1)
        sums[p] = h
    assert sha(FQ / "manifests" / "ffhqm.csv") == "732b53c8a8c4b875645c99f11f81b401550a4050361090dea90998d45035234c"
    meta = {r["id"]: r for r in csv.DictReader(open(FQ / "manifests" / "ffhqm_meta.csv"))}
    g0 = [r for r in csv.DictReader(open(FQ / "manifests" / "ffhqm.csv")) if r["family"] in GD0_FAM]
    bona = {pathlib.Path(r["path"]).name.split("_")[0] for r in g0 if r["label"] == "0"}
    contrib = set()
    for r in g0:
        if r["label"] == "1":
            contrib |= {meta[r["id"]]["key_x"], meta[r["id"]]["key_y"]}
    assert not (bona & contrib), "bona fide keys overlap morph contributors"
    for r in g0:
        host = pathlib.Path(r["path"]).name.split("_")[0] if r["label"] == "0" else meta[r["id"]]["key"]
        rows.append(dict(id="gd0_" + r["id"], src=FQ / r["path"], want=sums[r["path"]], label=r["label"], fam="gd0",
                         rung=f"{r['family']}_{r['variant']}", tool=r["family"], host=host))
    # GD1
    for r in csv.DictReader(open(DG1L)):
        x = lad[r["p1"]]          # host: test ladder host; every contributor outside PN1 training/validation
        assert x["role"] == "test" and x["test_read"] == "1" and x["is_val"] == "0", (r["id"], r["p1"])
        for h in {r["p1"], r["p2"]}:
            assert outside(h), (r["id"], h)
        rows.append(dict(id="gd1_" + r["id"], src=pathlib.Path(r["path"]), want=None,
                         label="1" if r["rung"] == "X" else "0", fam="gd1", rung=r["rung"], tool="diffae", host=r["p1"]))
    # GD2
    assert sha(AG1 / "manifests" / "ag1.csv") == AG1_MAN_SHA
    for r in csv.DictReader(open(AG1 / "manifests" / "ag1.csv")):
        if r["db"] not in ("feret", "frgc") or r["rung"] not in GD2_RUNG or r["aligned"] != "True":
            continue
        pa, pb = r["pa"].replace("_", ":"), r["pb"].replace("_", ":")
        if not (outside(pa) and outside(pb)):
            continue
        rows.append(dict(id="gd2_" + r["id"], src=AG1 / r["path"], want=None, label="1" if r["rung"] == "R4" else "0",
                         fam="gd2", rung=r["rung"], tool="mipgan" if r["rung"] != "R0" else "none", host=pa))
    for r in rows:
        assert not any(f in str(r["src"]).lower() for f in FORBID), r["src"]
    rows.sort(key=lambda x: x["id"])
    if lim:
        keep, seen = [], {}
        for r in rows:
            k = (r["fam"], r["rung"])
            if seen.get(k, 0) < 2:
                keep.append(r)
                seen[k] = seen.get(k, 0) + 1
        rows = keep[:8] if len(keep) < 8 else keep
    tag = "pr1_gd_limit8" if lim else "pr1_gd"
    tree = OUT / f"{tag}_tree"
    if tree.exists():
        shutil.rmtree(tree)                      # only symlinks and small files made by this script
    root = tree / "pr1g"
    (root / "data" / "eval" / "gd").mkdir(parents=True)
    (root / "data" / "manifests").mkdir(parents=True)
    ss, man = [], []
    for r in rows:
        h = sha(r["src"])
        if r["want"] is not None:
            assert h == r["want"], r["src"]
        pp = f"data/eval/gd/{r['id']}.png"
        os.symlink(r["src"], root / pp)
        ss.append((h, pp))
        man.append(dict(id=r["id"], path=f"eval/gd/{r['id']}.png", label=r["label"], fam=r["fam"], rung=r["rung"],
                        tool=r["tool"], host=r["host"], src=str(r["src"]), src_sha256=h))
    mf = root / "data" / "manifests" / "pr1_gd.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(man[0]))
        w.writeheader()
        w.writerows(man)
    ss.append((sha(mf), "data/manifests/pr1_gd.csv"))
    with open(root / "SHA256SUMS", "w") as f:
        for h, p in ss:
            f.write(f"{h}  {p}\n")
    tar = OUT / f"{tag}.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "pr1g"], check=True)
    th = sha(tar)
    (OUT / f"{tag}.tar.sha256").write_text(f"{th}  {tar.name}\n")
    from collections import Counter
    print("rows", len(man), dict(Counter((m["fam"], m["rung"]) for m in man)))
    print("list_sha256", sha(mf))
    print("pack_sha256", th)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
