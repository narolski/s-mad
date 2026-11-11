"""Builds the staging folder of the follow-up job (AD4 prereg Amendment 4 (b), (c)): symlinks to the extra images (no copy),
the extra manifest, the eleven ViT-B/16 networks' meta.json + last_trainable.pt (from the verified result tars) and the
scorer. The folder is streamed to Athena as one tar with `tar -chf -` (dereferenced), so no local copy of the images exists.

  python fu_pack.py --stage /mnt/t7/smad_next/AD4/fu/stage
"""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import random
import shutil
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
RES = pathlib.Path("/mnt/t7/smad_next/AD4/results_vast")
AR1 = pathlib.Path("/mnt/t7/smad_next/AR1/manifest.csv")
SMDD_E = pathlib.Path("/mnt/t7/Datasety/downloads/SMDD/SMDD_release_evaluation/os25k_bf_e")
H3 = (pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv"), pathlib.Path("/mnt/t7/smad_heldout/h3_sg3/data"))
H4B = (pathlib.Path("/mnt/t7/smad_heldout/h4b_mipgan1/data/manifests/h4bmipgan1.csv"),
       pathlib.Path("/mnt/t7/smad_heldout/h4b_mipgan1/data"))
FIELDS = ["id", "path", "set", "family", "label", "variant", "p1", "p2", "src"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True)
    a = ap.parse_args()
    st = pathlib.Path(a.stage)
    if st.exists():
        raise SystemExit(f"{st} exists (never overwritten)")
    (st / "fu/src").mkdir(parents=True)
    shutil.copy(HERE / "fu_rescore.py", st / "fu/src/fu_rescore.py")
    # networks
    for arm in ("mf", "perm"):
        for s in (401, 402, 403, 404, 405):
            t = f"AD4_m3{arm}_s{s}"
            tar = RES / f"{t}.tar"
            assert (RES / f"{t}.tar.sha256").read_text().split()[0] == sha(tar)
            d = st / "fu/nets" / t
            d.mkdir(parents=True)
            with tarfile.open(tar) as tf:
                for n in ("meta.json", "last_trainable.pt"):
                    (d / n).write_bytes(tf.extractfile(f"{t}/{n}").read())
    d = st / "fu/nets/AD4_m3zero_s401"
    d.mkdir(parents=True)
    json.dump({"recipe": "m3", "seed": 401}, open(d / "zero.json", "w"))
    # extra images and manifest
    rows, links = [], {}
    for r in csv.DictReader(open(AR1)):
        if r["pool"] != "frgcferet" or r["rung"] not in ("R0", "R2w", "R3", "R4"):
            continue
        rel = f"extra/ar1/{r['rung']}_{r['tool']}/{r['id']}.png"
        links[rel] = r["path"]
        rows.append({"id": f"ar1_{r['id']}", "path": rel, "set": "ar1", "family": f"{r['rung']}_{r['tool']}",
                     "label": "1" if r["rung"] in ("R3", "R4") else "0", "variant": "orig", "p1": r["p1"], "p2": r["p2"],
                     "src": r["path"]})
    names = sorted(os.listdir(SMDD_E))
    for n in random.Random(2026111104).sample(names, 1000):
        rel = f"extra/smdd_eval/{n}"
        links[rel] = str(SMDD_E / n)
        rows.append({"id": f"smdde_{pathlib.Path(n).stem}", "path": rel, "set": "smdd_eval", "family": "smdd_eval_bona",
                     "label": "0", "variant": "orig", "p1": "", "p2": "", "src": str(SMDD_E / n)})
    for (man, root), tag, fam in ((H3, "h3", "h3_bona"), (H4B, "h4b", "h4b_sg1_render")):
        for r in csv.DictReader(open(man)):
            if r["label"] != "0" or r["variant"] != "orig" or r["family"] != fam:
                continue
            rel = f"extra/{tag}/{pathlib.PurePath(r['path']).name}"
            links[rel] = str(root / r["path"])
            rows.append({"id": f"{tag}_{r['id']}", "path": rel, "set": tag, "family": fam, "label": "0", "variant": "orig",
                         "p1": "", "p2": "", "src": str(root / r["path"])})
    for rel, src in links.items():
        p = st / "fu/data" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(src, p)
    (st / "fu/data/manifests").mkdir(parents=True)
    with open(st / "fu/data/manifests/fu_extra.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    info = {"n_rows": len(rows), "by_set": {}, "fu_rescore_sha256": sha(HERE / "fu_rescore.py"),
            "fu_extra_csv_sha256": sha(st / "fu/data/manifests/fu_extra.csv")}
    for r in rows:
        info["by_set"][r["set"]] = info["by_set"].get(r["set"], 0) + 1
    json.dump(info, open(st / "fu/build_info.json", "w"), indent=1)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
