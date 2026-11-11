"""Code test of ag1_read.py on the real AG1 design with synthetic scores (DGX, CPU). Builds a manifest with the
rows ag1_manifest.py would write (R0 per camera photo, R1 per FRLL photo and generator, PUB per published MIPGAN file,
one row per generation job of every non-smoke shard), then runs the reader in --synthetic mode.
Usage: python -I test_reader_synthetic.py OUT_DIR  (then: ag1_read.py --data OUT_DIR/data --photos .../photos.json
       --out OUT_DIR/out --boot 300 --synthetic)
"""
import csv
import glob
import json
import pathlib
import sys

I = pathlib.Path("/mnt/t7/smad_next/AG1/inputs")
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")


def main():
    out = pathlib.Path(sys.argv[1])
    (out / "data/manifests").mkdir(parents=True, exist_ok=True)
    photos = json.load(open(I / "pack/photos.json"))
    rows = []
    for ph, m in photos.items():
        if m["slot"] == "s1m":
            continue
        rows.append(dict(id=f"R0__{ph}", path="x", label=0, rung="R0", gen="camera", db=m["db"], pa=m["person"],
                         pb=m["person"], photo_a=ph, photo_b=ph, alpha="", source="camera", aligned=True))
        if m["db"] == "frll":
            for g in ("mip1", "mip2"):
                rows.append(dict(id=f"R1__{g}__{ph}", path="x", label=0, rung="R1", gen=g, db="frll", pa=m["person"],
                                 pb=m["person"], photo_a=ph, photo_b=ph, alpha="", source="e7", aligned=True))
    for fam, g in (("MIPGAN_I", "mip1"), ("MIPGAN_II", "mip2")):
        for f in sorted((MAD / fam).glob("*.png")):
            a, b = f.stem.split("-vs-")
            rows.append(dict(id=f"PUB__{g}__{f.stem}", path="x", label=1, rung="PUB", gen=g, db="frll",
                             pa=f"frll_{a[:3]}", pb=f"frll_{b[:3]}", photo_a=a, photo_b=b, alpha=0.5,
                             source="published", aligned=True))
    for s in sorted(glob.glob(str(I / "shards/*.json"))):
        S = json.load(open(s))
        if S.get("smoke"):
            continue
        for j in S["jobs"]:
            pa, pb = j["a"].split("__")[0], j["b"].split("__")[0]
            rows.append(dict(id=j["stem"], path="x", label=1, rung=j["rung"], gen=j["gen"], db=pa.split("_")[0],
                             pa=pa, pb=pb, photo_a=j["a"], photo_b=j["b"], alpha=j["alpha"], source="ours",
                             aligned=True))
    for ph, m in photos.items():                         # R2s rows (spread-matched renders), as ag1_spread.py names them
        if m["slot"] != "s1":
            continue
        for g in (("mip1", "mip2") if m["db"] == "frll" else ("mip1",)):
            rows.append(dict(id=f"{g}_R2s_{m['person']}", path="x", label=0, rung="R2s", gen=g, db=m["db"],
                             pa=m["person"], pb=m["person"], photo_a=ph, photo_b=ph, alpha=0.0, source="ours",
                             aligned=True))
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids"
    with open(out / "data/manifests/ag1.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
