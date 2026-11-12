"""AG1 scoring manifest, FR-oracle embeddings and RT check (DGX, CPU + small GPU; after the generation tars are back;
no detector score is read here).

Per result tar (stage `shard`, one tar at a time, so a local tar can be deleted after it is processed; the verified copy
stays on Athena; lead's disk rule of 11 Nov):
  check the tar against its .sha256; for every PNG of its log.csv: bytes against the log line's sha256, then
  - frame: prep_eval.align (unchanged; CPU detector as h4_prep) -> 512 PNG under data/frames/<rung>/ (cv2.imwrite);
  - oracle: prep_eval.kps on the 1024 image -> insightface norm_crop 112 -> glintr100 (a2f_common.embed_crops, the
    A43 g2 route; not the generator's w600k loss model);
  - RT check: every RT image against the R3 image of the same person and generator in the same tar (|pixel diff|);
  written to data/shards/<shard>.json (log rows, aligned flags, RT numbers, tar sha256) and <shard>_oracle.npz.
Stage `frames`: camera photos (FERET .ppm.bz2 / FRGC .jpg decoded once to lossless PNG, then prep_eval.align), MAD22
  BonaFide, E7 (R1) and published MIPGAN-I / -II rows from the admitted canonical frames (byte copies into the data root,
  hash-checked, never re-aligned), plus every processed shard -> manifests/ag1.csv (paths relative to the data root)
  and manifests/ag1_raw.csv (raw sources; generated images as 'tar://<tar>::<member>').
Stage `oracle`: glintr100 embeddings of the camera photos, merged with every shard's -> oracle_glint.npz.
Stage `rt`: merged RT numbers -> rt_check.json. Stage `pins`: AG1_data_pins.sha256.
Every DGX run: OMP_NUM_THREADS=2 (and OPENBLAS / MKL / NUMEXPR) nice -n 10; onnxruntime sessions capped at 2 threads.
Usage: ag1_manifest.py shard <tar> | frames | oracle | rt | pins
"""
import csv
import hashlib
import json
import os
import pathlib
import shutil
import sys
import tarfile

import numpy as np

B = pathlib.Path(os.environ.get("AG1_BASE", "/mnt/t7/smad_next/AG1"))   # AG1_BASE: tests only
RES = B / "results"
DATA = B / "data"
SH = DATA / "shards"
INP = pathlib.Path("/mnt/t7/smad_next/AG1/inputs/pack")
CODE = pathlib.Path("/home/narolski/mambamorph-code")
MADRAW = pathlib.Path("/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted")
MADPROC = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
LABEL = {"R0": 0, "R1": 0, "R2": 0, "R2i": 0, "R2s": 0, "R3": 1, "R3m": 1, "R4": 1, "BR": 1, "RT": 1, "AG3": 1,
         "AG3T": 1, "PUB": 1}
ATHENA_SHARDS = {"AG1_mip1_frll_00", "AG1_mip1_frll_01", "AG1_mip1_feret_00", "AG1_mip1_feret_01", "AG1_mip1_frgc_00"}
COLS = ["id", "path", "label", "rung", "gen", "db", "pa", "pb", "photo_a", "photo_b", "alpha", "source", "aligned",
        "platform"]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_inputs as BI                                       # noqa: E402  (read_bgr: FERET .ppm.bz2 decode)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def cap_threads(app, n=2):
    """DGX courtesy (lead, 11 Nov): onnxruntime ignores OMP_NUM_THREADS, so every insightface session is rebuilt with
    n intra-op threads; OpenCV is capped too. Numerics are unchanged (same model, same provider)."""
    import cv2
    import onnxruntime as ort
    cv2.setNumThreads(n)
    for m in app.models.values():
        so = ort.SessionOptions()
        so.intra_op_num_threads, so.inter_op_num_threads = n, 1
        m.session = ort.InferenceSession(m.model_file, so, providers=["CPUExecutionProvider"])
    return app


def detector():
    sys.path.insert(0, str(CODE / "smadcvpr"))
    import prep_eval                                            # unchanged
    from insightface.app import FaceAnalysis
    det = FaceAnalysis(name="buffalo_l", allowed_modules=["detection"], providers=["CPUExecutionProvider"])
    det.prepare(ctx_id=-1, det_size=(512, 512))
    prep_eval._APP = cap_threads(det)
    return prep_eval


def oracle_crop(PE, img):
    from insightface.utils import face_align
    k = PE.kps(img)
    return None if k is None else face_align.norm_crop(img, np.asarray(k, np.float32), 112)


def embed(crops):
    sys.path.insert(0, "/mnt/t7/smad_heldout/arc2face/scripts")
    import a2f_common as A2F                                    # embed_crops('glint') as A43 g2 / h3_finalise
    return A2F.l2n(A2F.embed_crops("glint", np.stack(crops))).astype(np.float32)


def write_frame(PE, img, dst):
    import cv2
    dst.parent.mkdir(parents=True, exist_ok=True)
    fr, ok, _ = PE.align(img)
    cv2.imwrite(str(dst), fr)
    return bool(ok)


# ------------------------------------------------------------------------------------------------ one tar
def stage_shard(tar):
    import cv2
    t = pathlib.Path(tar).resolve()
    root = t.stem
    if "smoke" in root:
        sys.exit("smoke shards never enter the data")
    want = open(str(t) + ".sha256").read().split()[0]
    th = sha(t)
    if th != want:
        sys.exit(f"{t}: sha256 mismatch")
    PE = detector()
    SH.mkdir(parents=True, exist_ok=True)
    rows, crops, cids, fail, imgs_r3, rts = [], [], [], [], {}, []
    with tarfile.open(t) as tf:
        log = list(csv.DictReader(tf.extractfile(f"{root}/log.csv").read().decode().splitlines()))
        meta = json.loads(tf.extractfile(f"{root}/meta.json").read().decode())
        # amendments 4 / 6: platform per shard. Both platforms report "NVIDIA A100-SXM4-40GB", so the label is set
        # by where the shard was made: the five Athena core shards are listed; every other shard ran on the rented A100
        platform = ("athena_" if root in ATHENA_SHARDS else "rented_") + meta.get("device", "unknown").replace(" ", "_")
        for r in log:
            mem = f"{root}/png/{r['stem']}.png"
            buf = tf.extractfile(mem).read()
            if hashlib.sha256(buf).hexdigest() != r["png_sha256"]:
                sys.exit(f"{t}::{mem}: sha256 differs from its log line")
            img = cv2.imdecode(np.frombuffer(buf, np.uint8), cv2.IMREAD_COLOR)
            fp = DATA / "frames" / r["rung"] / f"{r['stem']}.png"
            ok = write_frame(PE, img, fp)
            c = oracle_crop(PE, img)
            if c is None:
                fail.append(r["stem"])
            else:
                crops.append(c)
                cids.append(r["stem"])
            if r["rung"] == "R3":
                imgs_r3[r["stem"]] = img
            pa, pb = r["a"].split("__")[0], r["b"].split("__")[0]
            rows.append({"id": r["stem"], "path": str(fp.relative_to(DATA)), "raw": f"tar://{t}::{mem}",
                         "rung": r["rung"], "gen": r["gen"], "db": pa.split("_")[0], "pa": pa, "pb": pb,
                         "photo_a": r["a"], "photo_b": r["b"], "alpha": r["alpha"], "source": "ours", "aligned": ok,
                         "platform": platform})
        for r in log:                                           # RT check within the tar
            if r["rung"] == "RT":
                twin = r["stem"].replace("_RT_", "_R3_")
                a = cv2.imdecode(np.frombuffer(tf.extractfile(f"{root}/png/{r['stem']}.png").read(), np.uint8),
                                 cv2.IMREAD_COLOR).astype(int)
                if twin in imgs_r3:
                    d = np.abs(a - imgs_r3[twin].astype(int))
                    rts.append({"id": r["stem"], "twin": twin, "gen": r["gen"], "db": r["a"].split("_")[0],
                                "max": int(d.max()), "mean": float(d.mean())})
    E = embed(crops) if crops else np.zeros((0, 512), np.float32)
    np.savez(SH / f"{root}_oracle.npz", id=np.array(cids), emb=E, fail=np.array(fail))
    json.dump({"tar": str(t), "tar_sha256": th, "platform": platform, "rows": rows, "rt": rts, "oracle_fail": fail},
              open(SH / f"{root}.json", "w"))
    print(f"SHARD {root}: {len(rows)} images, aligned {np.mean([r['aligned'] for r in rows]):.3f}, oracle "
          f"{len(cids)} / fail {len(fail)}, RT {len(rts)}; the local tar may now be removed (copy on Athena)")


# ------------------------------------------------------------------------------------------------ whole manifest
def stage_frames():
    import cv2
    PE = detector()
    photos = json.load(open(INP / "photos.json"))
    proc = dict(l.split()[::-1] for l in open(MADPROC / "PROCESSED_SHA256SUMS"))
    (DATA / "manifests").mkdir(parents=True, exist_ok=True)
    flags_p = DATA / "frames/aligned_flags_camera.json"
    flags = json.load(open(flags_p)) if flags_p.exists() else {}
    rows = []

    def admitted_copy(rel):
        """byte copy of an admitted MAD22 frame into the AG1 data root (portable manifests), hash re-checked."""
        if rel not in proc or sha(MADPROC / rel) != proc[rel]:
            sys.exit(f"{rel}: not the admitted processed frame")
        dst = DATA / "frames/mad22" / rel
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(MADPROC / rel, dst)
        if sha(dst) != proc[rel]:
            sys.exit(f"{dst}: copy differs from the admitted frame")
        return str(dst.relative_to(DATA))
    for ph, m in sorted(photos.items()):                         # R0: camera photos
        if m["slot"] == "s1m":                                   # mirrored crops are generator inputs, not R0
            continue
        if m["db"] == "frll":
            fp, ok, raw = admitted_copy(f"native/BonaFide/{pathlib.Path(m['src']).stem}.png"), True, m["src"]
        else:
            raw = DATA / "camera_png" / f"{ph}.png"                # decoded pixels, lossless; no resampling
            if not raw.exists():
                raw.parent.mkdir(parents=True, exist_ok=True)
                cv2.imwrite(str(raw), BI.read_bgr(m["src"]))
            fpp = DATA / "frames/R0" / f"{ph}.png"
            if not fpp.exists() or str(fpp) not in flags:
                flags[str(fpp)] = write_frame(PE, cv2.imread(str(raw), cv2.IMREAD_COLOR), fpp)
            fp, ok, raw = str(fpp.relative_to(DATA)), flags[str(fpp)], str(raw)
        rows.append({"id": f"R0__{ph}", "path": fp, "raw": raw, "rung": "R0", "gen": "camera", "db": m["db"],
                     "pa": m["person"], "pb": m["person"], "photo_a": ph, "photo_b": ph, "alpha": "",
                     "source": "camera", "aligned": ok})
    json.dump(flags, open(flags_p, "w"))
    for fam, gen in (("MIPGAN_I", "mip1"), ("MIPGAN_II", "mip2")):
        for ph, m in sorted(photos.items()):                     # R1: existing approved E7 frames
            if m["db"] != "frll" or m["slot"] == "s1m":
                continue
            e7 = admitted_copy(f"e7/{fam}/{pathlib.Path(m['src']).stem}.png")
            rows.append({"id": f"R1__{gen}__{ph}", "path": e7, "raw": str(DATA / e7), "rung": "R1", "gen": gen,
                         "db": "frll", "pa": m["person"], "pb": m["person"], "photo_a": ph, "photo_b": ph,
                         "alpha": "", "source": "e7", "aligned": True})
        for f in sorted((MADRAW / fam).glob("*.png")):            # published MIPGAN morphs
            a, b = f.stem.split("-vs-")
            rows.append({"id": f"PUB__{gen}__{f.stem}", "path": admitted_copy(f"native/{fam}/{f.stem}.png"),
                         "raw": str(f), "rung": "PUB", "gen": gen, "db": "frll", "pa": f"frll_{a[:3]}",
                         "pb": f"frll_{b[:3]}", "photo_a": a, "photo_b": b, "alpha": 0.5, "source": "published",
                         "aligned": True})
    shards = sorted(SH.glob("AG1_*.json"))
    for j in shards:
        rows += json.load(open(j))["rows"]
    for r in rows:
        r["label"] = LABEL[r["rung"]]
        r.setdefault("platform", r["source"])                    # camera / e7 / published rows
    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        sys.exit("duplicate ids")
    for name, key in (("ag1.csv", "path"), ("ag1_raw.csv", "raw")):
        with open(DATA / "manifests" / name, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS)
            w.writeheader()
            for r in rows:
                w.writerow({**{c: r[c] for c in COLS}, "path": r[key]})
    print(f"MANIFEST {len(rows)} rows from {len(shards)} processed shards; aligned-flag rate "
          f"{np.mean([bool(r['aligned']) for r in rows]):.3f}")


def stage_oracle():
    import cv2
    PE = detector()
    rows = [r for r in csv.DictReader(open(DATA / "manifests/ag1_raw.csv")) if r["rung"] == "R0"]
    ids, crops, fail = [], [], []
    for r in rows:
        c = oracle_crop(PE, cv2.imread(r["path"], cv2.IMREAD_COLOR))
        if c is None:
            fail.append(r["id"])
        else:
            crops.append(c)
            ids.append(r["id"])
    E = [embed(crops)]
    for z in sorted(SH.glob("AG1_*_oracle.npz")):
        d = np.load(z)
        ids += d["id"].tolist()
        fail += d["fail"].tolist()
        E.append(d["emb"])
    np.savez(DATA / "oracle_glint.npz", id=np.array(ids), emb=np.concatenate(E), fail=np.array(fail))
    print(f"ORACLE {len(ids)} embedded, {len(fail)} without a face")


def stage_rt():
    out = []
    for j in sorted(SH.glob("AG1_*.json")):
        out += json.load(open(j))["rt"]
    json.dump(out, open(DATA / "rt_check.json", "w"), indent=0)
    print("RT", len(out), "max of max", max((o["max"] for o in out), default=None))


def stage_pins():
    lines = [f"{sha(DATA / 'manifests' / n)}  manifests/{n}" for n in ("ag1.csv", "ag1_raw.csv")]
    (DATA / "AG1_data_pins.sha256").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "shard":
        stage_shard(sys.argv[2])
    else:
        {"frames": stage_frames, "oracle": stage_oracle, "rt": stage_rt, "pins": stage_pins}[st]()
