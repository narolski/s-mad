"""AB1 border-crossed arm (Sbx): training manifest = Sb's unique rows + border-blanked copies of 25% of the unique rows of
EVERY row kind (both classes at the same rate), and an evaluation manifest = ab1_eval.csv + the TT1 border references of
development persons. Image operation: constant-colour region blanking only (an approved operation): the pixels under a
border mask are set to (0,0,0), exactly as src/TT1/build_border_ref.py (its edge_mask function is imported unchanged).

Masks for training come from TT1 primary unseen-source frames (U_p) that are NOT the mask of any TT1 border reference,
so every evaluation border shape is unseen in training. Mask choice and row choice: numpy default_rng(20261161).
Bordered rows get kind "<kind>_border", hist "<hist>_border" (their own database x history strata, so the amendment-4
balance makes the bordered rows exactly class-balanced) and id "<id>__bd". Not volume-matched (the border copies are new
images).
Evaluation rows added (fam "border", label 0, klass genuine): TT1 R_cam_border rows whose camera photo is a development
person (development ladder R0, AF0 development photo; 226 photos x 7 families = 1,582) and R_ffhq_border (2,000 FFHQ
HN2 photos, development set). Test-ladder references are not added. Images copied unchanged from /mnt/t7/smad_next/TT1.
  python3 -I mk_ab1x.py [--limit 8]  -> /mnt/t7/smad_next/AB1/x/{manifests, img, ab1x_overlay.tar, ab1x_summary.json}"""
import argparse
import collections
import csv
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

import cv2
import numpy as np

SRC = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SRC / "PN1"))
sys.path.insert(0, str(SRC / "TT1"))
import mkmanifests as MM  # noqa: E402
import tt1common as T  # noqa: E402
from build_border_ref import edge_mask  # noqa: E402

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
AB1EVAL = pathlib.Path("/mnt/t7/smad_next/AB1/manifests/ab1_eval.csv")
BREF = pathlib.Path("/mnt/t7/smad_next/TT1/border_ref.csv")
OUT = pathlib.Path("/mnt/t7/smad_next/AB1/x")
RATE = 0.25


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    out = OUT if not a.limit else OUT.parent / "x_limit"
    man = out / "manifests"; man.mkdir(parents=True, exist_ok=True)
    M = FS / "data" / "manifests"
    assert sha(M / "train_Sb.csv").startswith("2cf3fda3affc8dd3")
    assert sha(AB1EVAL) == "93a5ba234f91e57951829c5536fabbe0f792ee4ad0a293f074aaca72f7465bd5"
    u = {}
    for r in csv.DictReader(open(M / "train_Sb.csv")):
        u.setdefault(r["id"], r)
    sb = [dict(r) for r in u.values()]
    assert len(sb) == 5535
    bref = list(csv.DictReader(open(BREF)))
    used = {r["mask_id"] for r in bref}
    pool = sorted((r for r in T.tt1_rows() if r["primary"] and r["id"] not in used), key=lambda r: r["id"])
    rng = np.random.default_rng(20261161)
    bykind = collections.defaultdict(list)
    for r in sb:
        bykind[r["kind"]].append(r)
    plan = []
    for k in sorted(bykind):
        rows = sorted(bykind[k], key=lambda r: r["id"])
        n = int(round(RATE * len(rows)))
        for i in sorted(rng.permutation(len(rows))[:n].tolist()):
            plan.append((rows[i], pool[int(rng.integers(len(pool)))]))
    if a.limit:
        plan = plan[::max(1, len(plan) // (4 * a.limit))][:4 * a.limit]   # spread over kinds so both classes appear
    img = out / "img"
    new, log = [], []
    for r, m in plan:
        src = cv2.imread(str(FS / "data" / r["path"]))
        msk = cv2.imread(m["aligned_path"])
        assert src is not None and msk is not None and src.shape == msk.shape == (512, 512, 3), (r["path"], m["id"])
        black = edge_mask(msk)
        im = src.copy()
        im[black] = 0
        pp = f"train/{r['kind']}_border/{r['id']}__bd.png"
        dst = img / "pn1" / "data" / pp
        dst.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(dst), im)
        new.append(dict(r, path=pp, id=f"{r['id']}__bd", kind=f"{r['kind']}_border", hist=f"{r['hist']}_border"))
        log.append(dict(id=f"{r['id']}__bd", src_id=r["id"], kind=r["kind"], label=r["label"], mask_id=m["id"],
                        mask_family=m["family"], masked_frac=round(float(black.mean()), 6), sha256=sha(dst)))
    bal, strata = MM.balanced_strata(sb + new)
    with open(man / "train_Sbx.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MM.TRCOLS)
        w.writeheader()
        w.writerows(bal)
    with open(out / "border_train_log.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(log[0]))
        w.writeheader()
        w.writerows(log)
    # evaluation rows
    ev = list(csv.DictReader(open(AB1EVAL)))
    keys = list(ev[0].keys())
    evid = {r["id"]: r for r in ev}
    add = []
    for b in bref:
        ref = evid.get(b["ref_id"])
        if ref is None:
            continue
        dev = (b["kind"] == "R_cam_border" and ref["role"] == "dev") or b["kind"] == "R_ffhq_border"
        if not dev:
            continue
        pp = f"eval/border/{b['id']}.png"
        dst = img / "pn1" / "data" / pp
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(b["path"], dst)
        assert sha(dst) == b["sha256"]
        add.append(dict({k: "" for k in keys}, id=b["id"], path=pp, label="0", klass="genuine",
                        role=ref["role"], fam="border", rung=b["kind"], strength=b["family"], tool="",
                        cell=b["mask_id"], host=b["ref_host"], neutral=""))
        if a.limit and len(add) >= a.limit:
            break
    with open(man / "ab1x_eval.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(ev + add)
    # overlay
    tree = img
    (tree / "pn1" / "data" / "manifests").mkdir(parents=True, exist_ok=True)
    for n in ("train_Sbx.csv", "ab1x_eval.csv"):
        shutil.copy2(man / n, tree / "pn1" / "data" / "manifests" / n)
    files = sorted(str(p.relative_to(tree / "pn1")) for p in (tree / "pn1").rglob("*") if p.is_file() and p.name != "AB1XSUMS")
    fs_sums = open(FS / "SHA256SUMS").read()
    for f in files:
        assert f"  {f}\n" not in fs_sums, f
    with open(tree / "pn1" / "AB1XSUMS", "w") as fh:
        for f in files:
            fh.write(f"{sha(tree / 'pn1' / f)}  {f}\n")
    ov = out / "ab1x_overlay.tar"
    subprocess.run(["tar", "-C", str(tree), "-cf", str(ov), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "pn1"], check=True)
    (out / "ab1x_overlay.tar.sha256").write_text(f"{sha(ov)}  ab1x_overlay.tar\n")
    summ = dict(sb_unique=len(sb), bordered=len(new), bordered_by_kind=dict(collections.Counter(x["kind"] for x in log)),
                bordered_by_label=dict(collections.Counter(x["label"] for x in log)), rows_after_balance=len(bal),
                rows_by_kind=dict(sorted(collections.Counter(r["kind"] for r in bal).items())), strata=strata,
                mask_pool=len(pool), mask_families_train=dict(collections.Counter(x["mask_family"] for x in log)),
                eval_rows=len(ev) + len(add), border_eval_rows=len(add),
                border_eval_by=dict(collections.Counter((x["rung"], x["role"]) for x in add).items()) if False else
                {f"{k[0]}|{k[1]}": v for k, v in collections.Counter((x["rung"], x["role"]) for x in add).items()},
                train_Sbx_sha256=sha(man / "train_Sbx.csv"), ab1x_eval_sha256=sha(man / "ab1x_eval.csv"),
                overlay_sha256=sha(ov), overlay_bytes=ov.stat().st_size, overlay_files=len(files))
    (out / "ab1x_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k: v for k, v in summ.items() if k != "strata"}, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
