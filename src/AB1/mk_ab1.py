"""Protocol ablation and replication (AB1): training manifests of the leave-one-component-out arms of Sb, made from
FS1's train_Sb.csv (2cf3fda3...) and train_A.csv / train_B.csv (af070a60..., bd53dc32...) by DROPPING row kinds (CSV only;
every image is already in the FS1 pack), the evaluation manifest ab1_eval.csv (FS1's pn1_eval.csv rows unchanged + the
1,480 MS1 FFHQ hold-out rows, fam ms1ffhq, byte-equal to the MS1 pack's rows), and one overlay tar for the FS1 pack.

Arms (unique rows of Sb = 5,535; "volume-matched" = the Bv rule of PN1 amendment 10: the dropped number of rows is
re-drawn from the arm's remaining unique rows, seeded, without replacement, as repeated rows; then the amendment-4
stratified class balance, mkmanifests.balanced_strata, unchanged):
  SbZ  Sb without the warp-only images (af0_zero, lad_R2w)                          volume-matched
  SbH  Sb without the native halves (af0_half, lad_half); af0_half61 kept (storage; removed in SbS)  volume-matched
       (pre-run review F2, 13 Nov 09:15: the first build also dropped af0_half61 and so most stored-small negatives)
  SbS  Sb without the stored-small copies (af0_photo61, af0_half61, af0_u5061)      volume-matched
  AS   A plus the stored-small copies of photos and morphs (af0_photo61, af0_u5061 rows of train_B)  natural counts
  Sp   the registered train_Sp.csv (cf386dc7..., mk_sp.py), copied unchanged       (as registered)
  python3 -I mk_ab1.py -> /mnt/t7/smad_next/AB1/{manifests/*.csv, ab1_overlay.tar, ab1_summary.json}"""
import collections
import csv
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "PN1"))
import mkmanifests as MM  # noqa: E402

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
MS1 = pathlib.Path("/mnt/t7/smad_next/MS1/pack_tree/pn1")
SP = pathlib.Path("/mnt/t7/smad_next/PN1/manifests_sp/train_Sp.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/AB1")
PIN = dict(eval="f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045",
           ms1eval="d1fab6ad4b20f0ec9dd426374ccd56e96368bf7b658b48e3ef31867e1fe470c5",
           A="af070a60529db3e8", B="bd53dc3252a76767", Sb="2cf3fda3affc8dd3", Sp="cf386dc7")
DROP = dict(SbZ=("af0_zero", "lad_R2w"), SbH=("af0_half", "lad_half"),
            SbS=("af0_photo61", "af0_half61", "af0_u5061"))
VOLSEED = dict(SbZ=20261141, SbH=20261142, SbS=20261143)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def uniq(path):
    u = {}
    for r in csv.DictReader(open(path)):
        u.setdefault(r["id"], r)
    return [dict(r) for r in u.values()]


def write(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MM.TRCOLS)
        w.writeheader()
        w.writerows(rows)


def main():
    man = OUT / "manifests"
    man.mkdir(parents=True, exist_ok=True)
    M = FS / "data" / "manifests"
    assert sha(M / "pn1_eval.csv") == PIN["eval"]
    for k in ("A", "B", "Sb"):
        assert sha(M / f"train_{k}.csv").startswith(PIN[k]), k
    assert sha(SP).startswith(PIN["Sp"])
    sb, a, b = uniq(M / "train_Sb.csv"), uniq(M / "train_A.csv"), uniq(M / "train_B.csv")
    assert len(sb) == 5535 and len(a) == 1526 and len(b) == 5099, (len(sb), len(a), len(b))
    summ = {}
    arms = {}
    for name, drop in DROP.items():
        keep = [r for r in sb if r["kind"] not in drop]
        n_drop = len(sb) - len(keep)
        rng = np.random.default_rng(VOLSEED[name])
        pick = rng.choice(len(keep), size=n_drop, replace=False)
        arms[name] = (keep, keep + [dict(keep[i]) for i in sorted(pick)])
    have = {r["id"] for r in a}
    add = [r for r in b if r["kind"] in ("af0_photo61", "af0_u5061") and r["id"] not in have]
    arms["AS"] = (a + add, a + add)
    fs_train = {r["id"] for k in ("A", "B", "Sb") for r in uniq(M / f"train_{k}.csv")}
    closed_tr = ("frll", "mad22", "mordiff", "dim", "h1", "fei", "casia", "ffhq", "valx", "fst", "a12sp")
    for name, (u, rows) in arms.items():
        for r in u:
            assert (FS / "data" / r["path"]).exists(), r["path"]
            assert r["id"] in fs_train, r["id"]                      # review F9: every training row is an FS1 row
            assert r["db"] in ("frgc", "feret") and not any(c in (r["path"] + r["id"]).lower() for c in closed_tr), r["id"]
        bal, strata = MM.balanced_strata(rows)
        write(bal, man / f"train_{name}.csv")
        summ[name] = dict(unique=len(u), rows_before_balance=len(rows), rows=len(bal),
                          repeated_for_volume=len(rows) - len(u),
                          unique_by_kind=dict(sorted(collections.Counter(r["kind"] for r in u).items())),
                          rows_by_kind=dict(sorted(collections.Counter(r["kind"] for r in bal).items())),
                          strata=strata, sha256=sha(man / f"train_{name}.csv"))
    shutil.copy2(SP, man / "train_Sp.csv")
    summ["Sp"] = dict(copied_from=str(SP), sha256=sha(man / "train_Sp.csv"))
    # evaluation manifest: FS1 rows unchanged (order kept) + MS1 hold-out rows
    ev = list(csv.DictReader(open(M / "pn1_eval.csv")))
    keys = list(ev[0].keys())
    assert sha(MS1 / "data" / "manifests" / "pn1_eval.csv") == PIN["ms1eval"]
    ho = [r for r in csv.DictReader(open(MS1 / "data" / "manifests" / "pn1_eval.csv")) if r["fam"] == "ms1ffhq"]
    assert len(ho) == 1480 and list(ho[0].keys()) == keys
    ids = {r["id"] for r in ev}
    assert not ids & {r["id"] for r in ho}
    closed = ("frll", "mad22", "mordiff", "dim", "h1", "fei", "casia", "valx", "fst", "a12sp")
    for r in ev + ho:
        assert r["fam"] in ("af0", "ladder", "splice", "ffhq", "ffhq_lcomb", "ms1ffhq"), r["fam"]
        low = (r["path"] + r["cell"] + r["id"]).lower()
        assert not any(c in low for c in closed), r["id"]
    with open(man / "ab1_eval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(ev + ho)
    summ["eval"] = dict(rows=len(ev) + len(ho), fs1_rows=len(ev), ms1ffhq_rows=len(ho),
                        by_fam=dict(collections.Counter(r["fam"] for r in ev + ho)), sha256=sha(man / "ab1_eval.csv"))
    # overlay tree: manifests + hold-out images + AB1SUMS (no FS1 file replaced)
    tree = OUT / "overlay_tree"
    if tree.exists():
        shutil.rmtree(tree)
    (tree / "pn1" / "data" / "manifests").mkdir(parents=True)
    files = []
    for n in ("SbZ", "SbH", "SbS", "AS", "Sp"):
        shutil.copy2(man / f"train_{n}.csv", tree / "pn1" / "data" / "manifests" / f"train_{n}.csv")
        files.append(f"data/manifests/train_{n}.csv")
    shutil.copy2(man / "ab1_eval.csv", tree / "pn1" / "data" / "manifests" / "ab1_eval.csv")
    files.append("data/manifests/ab1_eval.csv")
    for r in ho:
        dst = tree / "pn1" / "data" / r["path"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        assert not (FS / "data" / r["path"]).exists()
        shutil.copy2(MS1 / "data" / r["path"], dst)
        files.append("data/" + r["path"])
    fs_sums = open(FS / "SHA256SUMS").read()
    for f in files:
        assert f"  {f}\n" not in fs_sums, f
    with open(tree / "pn1" / "AB1SUMS", "w") as f:
        for p in sorted(files):
            f.write(f"{sha(tree / 'pn1' / p)}  {p}\n")
    ov = OUT / "ab1_overlay.tar"
    subprocess.run(["tar", "-C", str(tree), "-cf", str(ov), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "pn1"], check=True)
    (OUT / "ab1_overlay.tar.sha256").write_text(f"{sha(ov)}  ab1_overlay.tar\n")
    summ["overlay"] = dict(sha256=sha(ov), bytes=ov.stat().st_size, files=len(files))
    (OUT / "ab1_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("strata",)} for k, v in summ.items()}, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
