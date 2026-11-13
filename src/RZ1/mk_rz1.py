"""RZ1: build the cross-table manifest and the RZ1 overlay tar (code + manifest + RZ1SUMS). DGX CPU, no image is
written or changed. Inputs (pinned): the AB1 border evaluation manifest ab1x_eval.csv (AB1 amendment X), the TT1
scoring manifest tt1_score.csv (TT1 pack), the MEDS manifest (TT1-M pack, ids and paths only).
Cross-table rows (fixed before any fit):
  from ab1x_eval.csv: landmark_combined morphs 1,000 and resmatch genuine 2,000; development splices S0, S3, S4 (100
  each); development camera photos 226 and their stored-small copies 452; the MS1 FFHQ hold-out 1,480 (C2P rows);
  development camera photos with a border blanked in (R_cam_border, role dev) 1,582
  from tt1_score.csv: the camera reference R_cam 417 and every fourth row (row order) of each of the seven unseen
  source families (role tt1, rung = source)
  python3 -I mk_rz1.py [--out /mnt/t7/smad_next/RZ1]"""
import argparse
import csv
import hashlib
import io
import pathlib
import shutil
import tarfile

HERE = pathlib.Path(__file__).resolve().parent
X_EVAL = pathlib.Path("/mnt/t7/smad_next/AB1/x/manifests/ab1x_eval.csv")
X_EVAL_SHA = "5257fb63f321612c39f8da6613989976450a68cd97c0b55d51667b554995d35f"
TT1 = pathlib.Path("/mnt/t7/smad_next/TT1/pack_tree/tt1/data/manifests/tt1_score.csv")
MEDS_TAR = pathlib.Path("/mnt/t7/smad_next/TT1/meds/tt1m_meds.tar")
MEDS_TAR_SHA = "3fb917b226c6d31fab176a4d8fdd5d6e6b22b8274cc091591f444e623a87ab61"
SOURCES = ("lfw", "calfw", "agedb_30", "cfp_ff", "oulu_npu", "replay_attack", "casia_fasd", "msu_mfsd")
CODE = ("rz1_kernels.py", "rz1_patch.py", "rz1_train.py", "rz1_score.py", "rz1_guard.py")
FIELDS = ["id", "path", "label", "klass", "role", "fam", "rung", "strength", "tool", "cell", "host", "neutral", "src"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/mnt/t7/smad_next/RZ1")
    a = ap.parse_args()
    assert sha(X_EVAL) == X_EVAL_SHA
    assert sha(MEDS_TAR) == MEDS_TAR_SHA
    M = list(csv.DictReader(open(X_EVAL)))
    import importlib.util
    spec = importlib.util.spec_from_file_location("ab1_read", HERE.parent / "AB1" / "ab1_read.py")
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    P = A.pools([r for r in M if r["fam"] != "border"])
    want = set(P["lc_m"] + P["lc_g"] + P["S0"] + P["S3"] + P["S4"] + P["camera"] + P["soft"])
    want |= {r["id"] for r in M if r["fam"] == "ms1ffhq"}
    want |= {r["id"] for r in M if r["fam"] == "border" and r["rung"] == "R_cam_border" and r["role"] == "dev"}
    rows = [dict(r, src="ab1x") for r in M if r["id"] in want]
    T = list(csv.DictReader(open(TT1)))
    rows += [dict(r, src="tt1") for r in T if r["role"] == "gate" and r["rung"] == "R_cam"]
    for s in SOURCES:
        fam = [r for r in T if r["role"] == "tt1" and r["rung"] == s]
        rows += [dict(r, src="tt1") for r in fam[::4]]
    for r in rows:
        r["id"] = f'{r["src"]}:{r["id"]}'     # ids of the two manifests overlap (e.g. ar1_*); the cross id carries its source
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "cross ids collide"
    paths = {r["path"] for r in rows}
    assert len(paths) == len(rows), "cross paths repeat"
    # closed sets: every cross row is development FFHQ / FRGC / colorFERET or a TT1 unseen source; no benchmark path
    bad = [r["path"] for r in rows if any(k in r["path"].lower() for k in ("frll", "mad22", "mordiff", "dim", "h1_", "fei",
                                                                           "casia_web", "valx", "fst", "a12sp"))]
    assert not bad, bad[:5]
    out = pathlib.Path(a.out)
    tree = out / "overlay_tree" / "rz1"
    if tree.exists():
        shutil.rmtree(tree)
    (tree / "src").mkdir(parents=True)
    (tree / "manifests").mkdir()
    with open(tree / "manifests" / "rz1_cross.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    for c in CODE:
        shutil.copy2(HERE / c, tree / "src" / c)
    sums = "".join(f"{sha(p)}  {p.relative_to(tree)}\n" for p in sorted(tree.rglob("*")) if p.is_file())
    (tree / "RZ1SUMS").write_text(sums)
    tarp = out / "rz1_overlay.tar"
    with tarfile.open(tarp, "w", format=tarfile.GNU_FORMAT) as t:
        t.add(tree, arcname="rz1")
    (out / "rz1_overlay.tar.sha256").write_text(f"{sha(tarp)}  rz1_overlay.tar\n")
    from collections import Counter
    print("cross rows", len(rows), Counter((r["src"], r["fam"], r["rung"] if r["src"] == "tt1" else "") for r in rows))
    print("rz1_cross.csv", sha(tree / "manifests" / "rz1_cross.csv"))
    print(sums, end="")
    print("overlay", (out / "rz1_overlay.tar.sha256").read_text(), end="")


if __name__ == "__main__":
    main()
