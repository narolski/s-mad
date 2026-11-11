"""Own-crop re-score of the audit rows (RS1), Athena pack: one uncompressed tar with code, the facenet-pytorch wheel,
the seven release weight files, the reused A46 crops, every image that needs a release crop (renamed by id), the
crop-check files and the manifest. Images are added byte-for-byte (tarfile), nothing is decoded or re-encoded.

  python3 -I athena_pack.py  -> /mnt/t7/smad_next/RS1/athena/rs1a_pack.tar (+ .sha256) and athena_manifest.csv
Weights are third-party (CC BY-NC-SA 4.0); the tar goes only to the author group's private Athena project folder.
"""
import csv
import hashlib
import io
import json
import pathlib
import tarfile

OUT = pathlib.Path("/mnt/t7/smad_next/RS1")
A46 = pathlib.Path("/mnt/t7/smad_heldout/a46_corrective_20261108")
W46 = pathlib.Path("/home/narolski/mambamorph-code-a46/smadcvpr")
SRC = pathlib.Path("/home/narolski/smad-next/src/RS1")
PAY = pathlib.Path("/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models")
M22 = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
M22INV = pathlib.Path("/home/narolski/mambamorph-code/experiments/dataaudit/marco_owncloud_20261109T103840Z/"
                      "verified_inventory.json")
C22 = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
WHEEL = pathlib.Path("/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/facenet_pytorch-2.6.0-py3-none-any.whl")
CODE46 = ("a46_corrective_crop.py", "a12_released.py", "common.py", "a36_madation.py", "archs_a12.py", "archs_v2.py",
          "mixfacenet_port.py", "a41g_score.py")
CODERS1 = ("ar1_common.py", "crop_rgb.py", "score.py", "athena_run.py")
WEIGHTS = ("ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f",
           "bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980",
           "6a4d93ba80f3c48ecb0a9d8a6ae07e0c64e8c4f49f2cc62b2588dafbffb84d92",
           "74dd7fbce8385ec4c080def2c63300243b04ca2abd8ddea6eb2a519296e054a9",
           "a7cacd4773ed3ef959e78202c7f0e0426e5fff04367418130da78e9e85e64885",
           "6071ec7b7dcb0b3f28f4c8b71c79692a322404c33893a62f5a89964fb79a9421")
MIX = pathlib.Path("/mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth")
MIXSHA = "3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c"
FAM22 = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
COLS = ["id", "set", "label", "persons", "photo", "expr", "origin", "relpath", "src_path"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def forbidden(p):
    s = str(p).lower()
    return any(x in s for x in ("fst", "a12sp", "a12-sp")) or ("valx" in s and not s.endswith("valx_a.csv"))


def pers22(name, lab):
    stem = name.rsplit(".", 1)[0]
    if lab == 0:
        return stem[:3], stem[:6], stem[4:6]
    a, b = stem.split("-vs-")
    return f"{a[:3]}|{b[:3]}", "", a[4:6] if a[4:6] == b[4:6] else "mix"


def main():
    rows = []
    man = list(csv.DictReader(open(OUT / "manifest.csv")))
    for r in man:
        if r["crop_origin"] == "a46":
            rel = "img/a46/" + str(pathlib.Path(r["crop_path"]).relative_to(A46))
            rows.append(dict(id=r["id"], set=r["set"], label=r["label"], persons=r["persons"], photo=r["photo"],
                             expr=r["expr"], origin="a46", relpath=rel, src_path=r["crop_path"]))
        else:
            ext = pathlib.Path(r["src_path"]).suffix
            rows.append(dict(id=r["id"], set=r["set"], label=r["label"], persons=r["persons"], photo=r["photo"],
                             expr=r["expr"], origin="crop", relpath=f"img/src/{r['id']}{ext}", src_path=r["src_path"]))
    # corrected MAD22: raw files (hash-checked against the committed inventory) and canonical v3 aligned frames
    inv = {e["path"]: e["sha256"] for e in json.load(open(M22INV)) if "sha256" in e}
    n = 0
    for fam in ("BonaFide",) + FAM22:
        for p in sorted((M22 / fam).iterdir()):
            key = [k for k in (f"original_sorted/{fam}/{p.name}", f"{fam}/{p.name}") if k in inv]
            assert key and sha(p) == inv[key[0]], p
            lab = 0 if fam == "BonaFide" else 1
            pp, ph, ex = pers22(p.name, lab)
            rows.append(dict(id=f"m22r{n:05d}", set="G22_raw" if lab == 0 else f"M22_{fam}", label=lab, persons=pp,
                             photo=ph, expr=ex, origin="crop", relpath=f"img/src/m22r{n:05d}{p.suffix}",
                             src_path=str(p)))
            n += 1
    sums = {}
    for ln in open(C22 / "PROCESSED_SHA256SUMS"):
        h, f = ln.strip().split(None, 1)
        sums[f.lstrip("*")] = h
    n = 0
    for sub, s in [("native/BonaFide", "G22_aln")] + [(f"e7/{f}", f"E7aln22_{f}") for f in FAM22]:
        for p in sorted((C22 / sub).iterdir()):
            assert sha(p) == sums[f"{sub}/{p.name}"], p
            pp, ph, ex = pers22(p.name, 0)
            rows.append(dict(id=f"m22a{n:05d}", set=s, label=0, persons=pp, photo=ph, expr=ex, origin="crop",
                             relpath=f"img/src/m22a{n:05d}{p.suffix}", src_path=str(p)))
            n += 1
    # crop check: the 32 raw files of the DGX crop check (already cropped by A46)
    for r in csv.DictReader(open(OUT / "lists/cropcheck.csv")):
        ext = pathlib.Path(r["path"]).suffix
        rows.append(dict(id=r["id"], set="check", label="", persons="", photo="", expr="", origin="check",
                         relpath=f"img/check/{r['id']}{ext}", src_path=r["path"]))
    ids = [r["id"] for r in rows]
    assert len(set(ids)) == len(ids)
    for r in rows:
        assert not forbidden(r["src_path"])
    (OUT / "athena").mkdir(parents=True, exist_ok=True)
    with open(OUT / "athena/athena_manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    tp = OUT / "athena/rs1a_pack.tar"
    with tarfile.open(tp, "w", format=tarfile.PAX_FORMAT) as t:
        for f in CODE46:
            t.add(W46 / f, arcname=f"code/smadcvpr/{f}")
        for f in CODERS1:
            t.add(SRC / f, arcname=f"code/rs1/{f}")
        t.add(WHEEL, arcname=f"wheels/{WHEEL.name}")
        for h in WEIGHTS:
            p = PAY / f"{h}.safetensors"
            assert sha(p) == h, p
            t.add(p, arcname=f"weights/{h}.safetensors")
        assert sha(MIX) == MIXSHA
        t.add(MIX, arcname=f"weights/{MIXSHA}.pth")
        t.add(OUT / "athena/athena_manifest.csv", arcname="manifests/athena_manifest.csv")
        for k, r in enumerate(rows):
            t.add(r["src_path"], arcname=r["relpath"])
            if k % 2000 == 0:
                print(k, len(rows), flush=True)
    h = sha(tp)
    (OUT / "athena/rs1a_pack.tar.sha256").write_text(f"{h}  rs1a_pack.tar\n")
    from collections import Counter
    print(json.dumps(dict(Counter(r["set"] for r in rows)), indent=0))
    print("pack", tp, tp.stat().st_size / 1e9, "GB", h)


if __name__ == "__main__":
    main()
