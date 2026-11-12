"""Threshold transfer on unseen genuine sources (TT1): shared definitions (pools, families, paths). No score is read here."""
import csv
import hashlib
import pathlib

OUT = pathlib.Path("/mnt/t7/smad_next/TT1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine")
PN1T = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")          # FS1 development tree (code, hf, eval incl. hn2)
SOURCES = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw", "calfw", "cfp_ff", "agedb_30"]
ANTISPOOF = SOURCES[:4]
FAMILIES = ["replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd", "lfw_calfw", "cfp_ff", "agedb_30"]
BAND = {"antispoof": (1.2, 2.5), "pack": (2.5, 5.0)}                # plausible enlargement band of the primary pool U_p


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def tt1_rows():
    """raw + aligned manifest joined; adds 'primary' (1 if in U_p)."""
    raw = {r["id"]: r for r in csv.DictReader(open(OUT / "raw_manifest.csv"))}
    rows = []
    for a in csv.DictReader(open(OUT / "aligned_manifest.csv")):
        r = {**raw[a["id"]], **a}
        lo, hi = BAND["antispoof" if r["source"] in ANTISPOOF else "pack"]
        r["primary"] = int(r["aligned"] == "1" and lo <= float(r["enlarge"]) <= hi)
        rows.append(r)
    return rows


def ref_rows():
    """PN1 development reference rows (FS1 eval manifest): R_cam (417 native camera photos of held-out FRGC/colorFERET
    persons), R_ffhq (2,000 FFHQ bona fide orig), M_ffhq (1,000 FFHQ landmark_complete orig morphs)."""
    ev = list(csv.DictReader(open(PN1T / "data" / "manifests" / "pn1_eval.csv")))
    cam = [r for r in ev if r["label"] == "0" and r["strength"] == ""
           and ((r["fam"] == "ladder" and r["rung"] == "R0") or (r["fam"] == "af0" and r["rung"] == "photo"))]
    fq = [r for r in ev if r["fam"] == "ffhq" and r["rung"] == "ffhq_bona_orig" and r["label"] == "0"]
    fm = [r for r in ev if r["fam"] == "ffhq" and r["rung"] == "landmark_complete_orig" and r["label"] == "1"]
    assert (len(cam), len(fq), len(fm)) == (417, 2000, 1000), (len(cam), len(fq), len(fm))
    return dict(R_cam=sorted(cam, key=lambda r: r["id"]), R_ffhq=sorted(fq, key=lambda r: r["id"]),
                M_ffhq=sorted(fm, key=lambda r: r["id"]))
