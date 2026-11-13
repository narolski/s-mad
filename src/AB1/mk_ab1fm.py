"""AB1 second-engine arm (SbFM): train_SbFM.csv = Sb's 5,535 unique rows + FaceMorpher-engine ladder rows of TRAINING
hosts, selected exactly like Sb's OpenCV ladder rows (PN1 mkmanifests.final rules, catalog role "train"):
  lad_R4fm   FaceMorpher two-person morph R4 (attack)           hosts with train_morph = 1 (partner also a training host)
  lad_R2wfm  FaceMorpher warp-only image toward the host's own mean shape (negative)   hosts with train_genuine = 1
  lad_R2w4fm FaceMorpher warp-only image toward the two-person mean shape (negative; the engine's warped host, i.e. the
             host-side half of R4)                              hosts with train_morph = 1
No FaceMorpher splices (their seam-only negatives carry almost no seam: REVIEW_SPLICE_20261111 step 1.06 against 15.83,
AUC 0.999); no FaceMorpher partner-side half (it does not exist and building it would be a new engine run); no
stored-small ladder copies (Sb has none for either engine). Images: unchanged AR1 FaceMorpher outputs, copied.
Evaluation manifest: ab1x_eval.csv (ab1_eval.csv + the 3,582 border rows) unchanged, with the border images.
Rows: train_Sb.csv's 8,386 rows unchanged + the FaceMorpher block balanced on its own by the amendment-4 rule
(pre-run check F2). Not volume-matched (adds 7.3% unique images; disclosed).
  python3 -I mk_ab1fm.py -> /mnt/t7/smad_next/AB1/fm/{manifests, img, ab1fm_overlay.tar, ab1fm_summary.json}"""
import collections
import csv
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

SRC = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC / "PN1"))
import mkmanifests as MM  # noqa: E402
import pn1lib as K  # noqa: E402

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
X = pathlib.Path("/mnt/t7/smad_next/AB1/x")
OUT = pathlib.Path("/mnt/t7/smad_next/AB1/fm")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    man = OUT / "manifests"; man.mkdir(parents=True, exist_ok=True)
    M = FS / "data" / "manifests"
    assert sha(M / "train_Sb.csv").startswith("2cf3fda3affc8dd3")
    assert sha(X / "manifests" / "ab1x_eval.csv") == "5257fb63f321612c39f8da6613989976450a68cd97c0b55d51667b554995d35f"
    u = {}
    for r in csv.DictReader(open(M / "train_Sb.csv")):
        u.setdefault(r["id"], r)
    sb = [dict(r) for r in u.values()]
    assert len(sb) == 5535
    lad, _ = K.split_tables()
    cat = K.catalog()
    ev_ids = {r["id"] for r in csv.DictReader(open(X / "manifests" / "ab1x_eval.csv"))}
    img = OUT / "img"
    add = []
    for r in cat:
        if r["role"] != "train" or r["fam"] != "ladder" or r["strength"] != "" or r["tool"] != "facemorpher":
            continue
        h = lad[r["host"]]
        kind = None
        if r["rung"] == "R4" and h["train_morph"] == "1":
            kind, label = "lad_R4fm", "1"
        elif r["rung"] == "R2w" and h["train_genuine"] == "1":
            kind, label = "lad_R2wfm", "0"
        elif r["rung"] == "R2w4" and h["train_morph"] == "1":
            kind, label = "lad_R2w4fm", "0"
        if kind is None:
            continue
        assert r["id"] not in ev_ids, r["id"]
        pp = f"train/{kind}/{r['id']}.png"
        dst = img / "pn1" / "data" / pp
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(r["path"], dst)
        add.append(dict(path=pp, label=label, source="smdd", tool="smdd", arm="smdd", val="0", mixed="0", id=r["id"],
                        kind=kind, db=r["host"].split(":")[0], hist="native"))
    have = {r["id"] for r in sb}
    assert not have & {r["id"] for r in add}
    # pre-run check F2: Sb's 8,386 rows unchanged (same rows, same order) + a FaceMorpher block balanced on its own within
    # each database (attacks repeated to equal the FaceMorpher negatives), so no engine-identity attack prior is added
    sb_rows = list(csv.DictReader(open(M / "train_Sb.csv")))
    fm_bal, fm_strata = MM.balanced_strata(add)
    bal = sb_rows + fm_bal
    strata = dict(fm_block=fm_strata)
    with open(man / "train_SbFM.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MM.TRCOLS)
        w.writeheader()
        w.writerows(bal)
    # evaluation manifest and border images (unchanged from the Sbx build)
    (img / "pn1" / "data" / "manifests").mkdir(parents=True, exist_ok=True)
    shutil.copy2(man / "train_SbFM.csv", img / "pn1" / "data" / "manifests" / "train_SbFM.csv")
    shutil.copy2(X / "manifests" / "ab1x_eval.csv", img / "pn1" / "data" / "manifests" / "ab1x_eval.csv")
    bsrc = X / "img" / "pn1" / "data" / "eval" / "border"
    bdst = img / "pn1" / "data" / "eval" / "border"
    if bdst.exists():
        shutil.rmtree(bdst)
    shutil.copytree(bsrc, bdst)
    files = sorted(str(p.relative_to(img / "pn1")) for p in (img / "pn1").rglob("*") if p.is_file() and p.name != "AB1FMSUMS")
    fs_sums = open(FS / "SHA256SUMS").read()
    for f in files:
        assert f"  {f}\n" not in fs_sums, f
    with open(img / "pn1" / "AB1FMSUMS", "w") as fh:
        for f in files:
            fh.write(f"{sha(img / 'pn1' / f)}  {f}\n")
    ov = OUT / "ab1fm_overlay.tar"
    subprocess.run(["tar", "-C", str(img), "-cf", str(ov), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "pn1"], check=True)
    (OUT / "ab1fm_overlay.tar.sha256").write_text(f"{sha(ov)}  ab1fm_overlay.tar\n")
    n = len(bal)
    cnt = collections.Counter(r["kind"] for r in bal)
    summ = dict(sb_unique=len(sb), added=len(add), added_by_kind=dict(collections.Counter(r["kind"] for r in add)),
                unique=len(sb) + len(add), rows_after_balance=n, row_share_pct={k: round(100 * v / n, 2) for k, v in sorted(cnt.items())},
                strata=strata, train_SbFM_sha256=sha(man / "train_SbFM.csv"), overlay_sha256=sha(ov), overlay_bytes=ov.stat().st_size,
                overlay_files=len(files))
    (OUT / "ab1fm_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "strata"}, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
