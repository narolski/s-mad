"""PN1 remedy arm Sp (draft): train_Sp.csv = Sb's rows minus the seam-matched negatives lad_S0 and lad_S3, re-balanced
by the amendment-4 rule (mkmanifests.balanced_strata, unchanged); then a small overlay tar for the FS1 pack:
pn1/data/manifests/train_Sp.csv and the regenerated pn1/SHA256SUMS (FS1 lines unchanged + the train_Sp line).
pn1_eval.csv of the FS1 pack is not touched (byte-equal check), so no benchmark row can enter.
  python3 -I mk_sp.py -> /mnt/t7/smad_next/PN1/manifests_sp/train_Sp.csv, /mnt/t7/smad_next/PN1/pn1_overlay_sp.tar"""
import collections
import csv
import hashlib
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import mkmanifests as MM  # noqa: E402
import pn1lib as K  # noqa: E402

FS = K.PN1 / "fs_tree" / "pn1"
OUT = K.PN1 / "manifests_sp"
EVAL_SHA = "f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045"


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert sha(FS / "data" / "manifests" / "pn1_eval.csv") == EVAL_SHA
    sb = list(csv.DictReader(open(FS / "data" / "manifests" / "train_Sb.csv")))
    uniq = {}
    for r in sb:
        uniq.setdefault(r["id"], r)
    rows = [dict(r) for r in uniq.values() if r["kind"] not in ("lad_S0", "lad_S3")]
    bal, strata = MM.balanced_strata(rows)
    mf = OUT / "train_Sp.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MM.TRCOLS)
        w.writeheader()
        w.writerows(bal)
    for r in bal:                                   # every Sp image is already in the FS1 pack
        assert (FS / "data" / r["path"]).exists(), r["path"]
    tree = K.PN1 / "sp_overlay_tree"
    if tree.exists():
        shutil.rmtree(tree)
    (tree / "pn1" / "data" / "manifests").mkdir(parents=True)
    shutil.copy2(mf, tree / "pn1" / "data" / "manifests" / "train_Sp.csv")
    sums = open(FS / "SHA256SUMS").read()
    assert "train_Sp.csv" not in sums
    (tree / "pn1" / "SHA256SUMS").write_text(sums + f"{sha(mf)}  data/manifests/train_Sp.csv\n")
    ov = K.PN1 / "pn1_overlay_sp.tar"
    subprocess.run(["tar", "-C", str(tree), "-cf", str(ov), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-12 00:00:00", "pn1/data/manifests/train_Sp.csv", "pn1/SHA256SUMS"], check=True)
    print("rows", len(bal), "unique", len(rows), dict(collections.Counter(r["kind"] for r in rows)))
    print("strata", strata)
    print("train_Sp sha256", sha(mf))
    print("overlay sha256", sha(ov), ov.stat().st_size)


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
