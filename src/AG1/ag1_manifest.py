"""AG1 scoring manifest and FR-oracle embeddings (CPU, DGX; run after the generation tars are back; no score is read).

Inputs: the result tars of every AG1 shard (copied to /mnt/t7/smad_next/AG1/results/, sha256 checked), the inputs pack
(photos.json), the corrected MAD22 (raw files and the admitted canonical512 native frames, PROCESSED_SHA256SUMS).
Frames: every generated 1024 PNG and every FERET / FRGC camera photo -> prep_eval.align (unchanged; CPU detector as
h4_prep) -> 512 PNG (cv2.imwrite); MAD22 BonaFide and published MIPGAN-I / -II rows use the admitted native frames
(hash-checked), never re-aligned. Raw paths (for SelfMAD's own crop) are the generator PNG / camera file / MAD22 file.
Manifests (data root /mnt/t7/smad_next/AG1/data, as smadcvpr_data): manifests/ag1.csv (frames) and
manifests/ag1_raw.csv (raw files); same ids. Columns: id, path, label, rung, gen, db, pa, pb, photo_a, photo_b, alpha,
source, aligned. label is the benchmark label (1 = morph-type construction R3 / R4 / BR / AG3 / published, 0 = R0 / R2 /
R2i / RT is 1); the analysis never uses label, only rung.
Oracle (gate G-b): glintr100 (antelopev2, not the generator's w600k loss model) embeddings of every generated image and
every camera photo: prep_eval.kps -> insightface norm_crop 112 -> a2f_common.embed_crops('glint'); -> oracle.npz.
RT check: RT vs R3 pixel differences -> rt_check.json (zero GPU).
Usage: ag1_manifest.py frames | oracle | rt | pins
"""
import csv
import glob
import hashlib
import shutil
import json
import pathlib
import sys
import tarfile

import numpy as np

B = pathlib.Path("/mnt/t7/smad_next/AG1")
RES = B / "results"
DATA = B / "data"
INP = B / "inputs/pack"
CODE = pathlib.Path("/home/narolski/mambamorph-code")
MADRAW = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
MADPROC = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
LABEL = {"R0": 0, "R1": 0, "R2": 0, "R2i": 0, "R3": 1, "R3m": 1, "R4": 1, "BR": 1, "RT": 1, "AG3": 1, "AG3T": 1, "PUB": 1}
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_inputs as BI                                       # noqa: E402  (read_bgr: FERET .ppm.bz2 decode)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def detector():
    sys.path.insert(0, str(CODE / "smadcvpr"))
    import prep_eval                                            # unchanged
    from insightface.app import FaceAnalysis
    det = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"], providers=["CPUExecutionProvider"])
    det.prepare(ctx_id=-1, det_size=(512, 512))
    prep_eval._APP = det
    return prep_eval


def unpack():
    """every shard tar next to its .sha256, checked, extracted once to results/x/<shard>/."""
    out = []
    for t in sorted(RES.glob("AG1_*.tar")):
        if "smoke" in t.name:                                   # smoke shards never enter the data
            continue
        want = open(str(t) + ".sha256").read().split()[0]
        if sha(t) != want:
            sys.exit(f"{t}: sha256 mismatch")
        d = RES / "x" / t.stem
        if not d.exists():
            with tarfile.open(t) as tf:
                tf.extractall(RES / "x", filter="data")
        out.append(d)
    return out


def stage_frames():
    import cv2
    PE = detector()
    photos = json.load(open(INP / "photos.json"))
    proc = dict(l.split()[::-1] for l in open(MADPROC / "PROCESSED_SHA256SUMS"))
    (DATA / "manifests").mkdir(parents=True, exist_ok=True)
    rows = []

    flags_p = DATA / "frames/aligned_flags.json"
    flags = json.load(open(flags_p)) if flags_p.exists() else {}

    def frame(src, dst):
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or str(dst) not in flags:
            img, ok, _ = PE.align(cv2.imread(str(src), cv2.IMREAD_COLOR))
            cv2.imwrite(str(dst), img)
            flags[str(dst)] = bool(ok)
        return flags[str(dst)]

    def mad_frame(fam, name):
        rel = f"native/{fam}/{pathlib.Path(name).stem}.png"
        p = MADPROC / rel
        key = next((k for k in (rel, "./" + rel) if k in proc), None)
        if key is None or sha(p) != proc[key]:
            sys.exit(f"{p}: not the admitted processed frame")
        return admitted_copy(rel)

    def admitted_copy(rel):
        """byte copy of an admitted MAD22 frame into the AG1 data root (portable manifests), hash re-checked."""
        dst = DATA / "frames/mad22" / rel
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(MADPROC / rel, dst)
        if sha(dst) != proc[rel]:
            sys.exit(f"{dst}: copy differs from the admitted frame")
        return dst
    # R0: camera photos
    for ph, m in sorted(photos.items()):
        if m["slot"] == "s1m":                                 # mirrored crops are generator inputs, not R0
            continue
        if m["db"] == "frll":
            fp, ok = mad_frame("BonaFide", pathlib.Path(m["src"]).name), True
            raw = m["src"]
        else:                                                  # FERET .ppm.bz2 / FRGC .jpg: decoded once (lossless
            raw = DATA / "camera_png" / f"{ph}.png"            # PNG of the decoded pixels; no resampling)
            if not raw.exists():
                raw.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(raw), BI.read_bgr(m["src"]))
            fp = DATA / "frames/R0" / f"{ph}.png"
            ok = frame(raw, fp)
            raw = str(raw)
        rows.append({"id": f"R0__{ph}", "path": str(fp), "raw": raw, "rung": "R0", "gen": "camera",
                     "db": m["db"], "pa": m["person"], "pb": m["person"], "photo_a": ph, "photo_b": ph, "alpha": "",
                     "source": "camera", "aligned": ok})
    # R1: the existing, approved E7 outputs of the FRLL photos for the MIPGAN-I / -II cells (no new code)
    for fam, gen in (("MIPGAN_I", "mip1"), ("MIPGAN_II", "mip2")):
        for ph, m in sorted(photos.items()):
            if m["db"] != "frll" or m["slot"] == "s1m":
                continue
            stem = pathlib.Path(m["src"]).stem
            rel = f"e7/{fam}/{stem}.png"
            if rel not in proc or sha(MADPROC / rel) != proc[rel]:
                sys.exit(f"{rel}: not the admitted E7 frame")
            e7 = admitted_copy(rel)
            rows.append({"id": f"R1__{gen}__{ph}", "path": str(e7), "raw": str(e7), "rung": "R1",
                         "gen": gen, "db": "frll", "pa": m["person"], "pb": m["person"], "photo_a": ph,
                         "photo_b": ph, "alpha": "", "source": "e7", "aligned": True})
    # published MIPGAN morphs of the FRLL persons (benchmark side and bridge partners)
    for fam, gen in (("MIPGAN_I", "mip1"), ("MIPGAN_II", "mip2")):
        for f in sorted((MADRAW / fam).glob("*.png")):
            a, b = f.stem.split("-vs-")
            rows.append({"id": f"PUB__{gen}__{f.stem}", "path": str(mad_frame(fam, f.name)), "raw": str(f),
                         "rung": "PUB", "gen": gen, "db": "frll", "pa": f"frll_{a[:3]}", "pb": f"frll_{b[:3]}",
                         "photo_a": a, "photo_b": b, "alpha": 0.5, "source": "published", "aligned": True})
    # ours
    for d in unpack():
        for r in csv.DictReader(open(d / "log.csv")):
            src = d / "png" / f"{r['stem']}.png"
            if sha(src) != r["png_sha256"]:
                sys.exit(f"{src}: sha256 differs from its log line")
            fp = DATA / "frames" / r["rung"] / f"{r['stem']}.png"
            ok = frame(src, fp)
            pa, pb = r["a"].split("__")[0], r["b"].split("__")[0]
            rows.append({"id": r["stem"], "path": str(fp), "raw": str(src), "rung": r["rung"], "gen": r["gen"],
                         "db": pa.split("_")[0], "pa": pa, "pb": pb, "photo_a": r["a"], "photo_b": r["b"],
                         "alpha": r["alpha"], "source": "ours", "aligned": ok})
    json.dump(flags, open(flags_p, "w"))
    for r in rows:
        r["label"] = LABEL[r["rung"]]
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        sys.exit("duplicate ids")
    cols = ["id", "path", "label", "rung", "gen", "db", "pa", "pb", "photo_a", "photo_b", "alpha", "source", "aligned"]
    for name, key in (("ag1.csv", "path"), ("ag1_raw.csv", "raw")):
        with open(DATA / "manifests" / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in rows:                                     # ag1.csv: paths relative to the data root
                pth = r[key]
                if name == "ag1.csv":
                    pth = str(pathlib.Path(pth).relative_to(DATA))
                w.writerow({**{c: r[c] for c in cols}, "path": pth})
    print(f"MANIFEST {len(rows)} rows; aligned-flag rate {np.mean([bool(r['aligned']) for r in rows]):.3f}")


def stage_oracle():
    import cv2
    from insightface.utils import face_align
    PE = detector()
    sys.path.insert(0, "/mnt/t7/smad_heldout/arc2face/scripts")
    import a2f_common as A2F                                      # embed_crops('glint') as A43 g2 / h3_finalise
    rows = list(csv.DictReader(open(DATA / "manifests/ag1_raw.csv")))
    ids, crops, fail = [], [], []
    for r in rows:
        img = cv2.imread(r["path"], cv2.IMREAD_COLOR)
        k = PE.kps(img)
        if k is None:
            fail.append(r["id"])
            continue
        crops.append(face_align.norm_crop(img, np.asarray(k, np.float32), 112))
        ids.append(r["id"])
    E = A2F.l2n(A2F.embed_crops("glint", np.stack(crops)))
    np.savez(DATA / "oracle_glint.npz", id=np.array(ids), emb=E.astype(np.float32), fail=np.array(fail))
    print(f"ORACLE {len(ids)} embedded, {len(fail)} without a face")


def stage_rt():
    """RT (order-reversed twin) vs R3 of the same person and generator: max and mean |pixel difference| (1024 PNG)."""
    import cv2
    rows = {r["id"]: r for r in csv.DictReader(open(DATA / "manifests/ag1_raw.csv"))}
    out = []
    for i, r in rows.items():
        if r["rung"] != "RT":
            continue
        twin = i.replace("_RT_", "_R3_")
        a = cv2.imread(r["path"]).astype(int)
        b = cv2.imread(rows[twin]["path"]).astype(int)
        d = np.abs(a - b)
        out.append({"id": i, "twin": twin, "gen": r["gen"], "db": r["db"], "max": int(d.max()), "mean": float(d.mean())})
    json.dump(out, open(DATA / "rt_check.json", "w"), indent=0)
    print("RT", len(out), "max of max", max((o["max"] for o in out), default=None))


def stage_pins():
    lines = [f"{sha(DATA / 'manifests' / n)}  manifests/{n}" for n in ("ag1.csv", "ag1_raw.csv")]
    (DATA / "AG1_data_pins.sha256").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    {"frames": stage_frames, "oracle": stage_oracle, "rt": stage_rt, "pins": stage_pins}[sys.argv[1]]()
