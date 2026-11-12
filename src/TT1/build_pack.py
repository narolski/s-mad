"""Threshold transfer on unseen genuine sources (TT1): scoring list and the reusable scoring pack, plus a separate
network tar (so the fresh-seed networks of FS1 can be scored later with the same pack and a second network tar).

  list : tt1_score.csv (PN1 manifest format). fam "gate" = R_cam (417) + R_ffhq (2,000) + M_ffhq (1,000), the rows with
         stored A100 logits; fam "tt1" = all 25,241 TT1 frames, the 834 crop-geometry-matched references (rung R_cam_geo224 / R_cam_geo112), (rung = source, cell = family, host = person; 'strength'
         holds 'primary' or 'secondary') + the 4,919 border-matched references (rung R_cam_border / R_ffhq_border).
  pack : /mnt/t7/smad_next/TT1/tt1_pack.tar: tt1/data/eval/{tt1,tt1ref,tt1b}/..., tt1/data/manifests/tt1_score.csv,
         tt1/code (PN1 FS1 tree code), tt1/hf/a12 (base CLIP weights), tt1/bin/{rescore.py,gate_check.py}, tt1/SHA256SUMS.
         Asserts that no row comes from a benchmark set (paths only under TT1 aligned / border_ref and PN1 fs_tree
         eval/pn1, eval/hn2).
  nets NAME TAR... : /mnt/t7/smad_next/TT1/tt1_nets_<NAME>.tar with nets/<task>/{meta.json,last_trainable.pt} from the
         given PN1 result tars and gate_ref/<task>.npz (id, logit: stored A100 logits of the gate rows), SHA256SUMS.
  python3 -I build_pack.py list|pack|nets ...
"""
import csv
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tt1common as T  # noqa: E402

FIELDS = ["id", "path", "label", "klass", "role", "fam", "rung", "strength", "tool", "cell", "host", "neutral"]
PN1R = pathlib.Path("/mnt/t7/smad_next/PN1/results_rented/unpacked")
A14 = pathlib.Path("/mnt/t7/smad_next/PN1/results_a14/unpacked/PN1_A14")
BENCH = ("frll", "mad22", "mordiff", "dim", "h1", "fei", "casia", "valx", "fst", "a12sp", "a12-sp")


def build_list():
    rows, src = [], {}
    refs = T.ref_rows()
    for pool, rs in refs.items():
        for r in rs:
            p = f"eval/tt1ref/{r['id']}.png"
            rows.append(dict(id=r["id"], path=p, label=r["label"], klass=r["klass"], role="gate", fam="gate", rung=pool,
                             strength="", tool="", cell=pool, host=r["host"], neutral=""))
            src[p] = str(T.PN1T / "data" / r["path"])
    for r in T.tt1_rows():
        p = f"eval/tt1/{r['source']}/{r['id']}.png"
        rows.append(dict(id=r["id"], path=p, label="0", klass="genuine", role="tt1", fam="tt1", rung=r["source"],
                         strength="primary" if r["primary"] else "secondary", tool="", cell=r["family"], host=r["person"],
                         neutral=""))
        src[p] = r["aligned_path"]
    for r in csv.DictReader(open(T.OUT / "border_ref.csv")):
        p = f"eval/tt1b/{r['id']}.png"
        rows.append(dict(id=r["id"], path=p, label="0", klass="genuine", role="tt1", fam="tt1", rung=r["kind"],
                         strength=r["mask_id"], tool="", cell=r["family"], host=r["ref_host"], neutral=""))
        src[p] = r["path"]
    for r in csv.DictReader(open(T.OUT / "geo_ref.csv")):
        if r["aligned"] != "1":
            continue
        p = f"eval/tt1g/{r['id']}.png"
        rows.append(dict(id=r["id"], path=p, label="0", klass="genuine", role="tt1", fam="tt1", rung=f"R_cam_geo{r['group'][1:]}",
                         strength=r["ref_id"], tool="", cell=r["group"], host=r["ref_host"], neutral=""))
        src[p] = r["path"]
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    forbidden = ("train.rec", "train.idx", "train.lst", "cfp_fp.bin", "cplfw.bin")
    raw = {r["id"]: r for r in csv.DictReader(open(T.OUT / "raw_manifest.csv"))}
    assert not any(any(f in r["orig_file"] for f in forbidden) for r in raw.values()), "forbidden pack read"
    for p in src.values():
        s = p.lower()
        assert not any(b in s for b in BENCH) or s.startswith("/mnt/t7/smad_next/tt1/"), p
        assert s.startswith(("/mnt/t7/smad_next/tt1/", str(T.PN1T / "data" / "eval" / "pn1").lower(),
                             str(T.PN1T / "data" / "eval" / "hn2").lower())), p
    mf = T.OUT / "tt1_score.csv"
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    json.dump(src, open(T.OUT / "tt1_score_sources.json", "w"))
    shutil.copyfile(mf, T.RES / "tt1_score.csv")
    print("rows", len(rows), {k: sum(1 for r in rows if r["fam"] == k) for k in ("gate", "tt1")}, "sha256", T.sha(mf))


def build_pack():
    src = json.load(open(T.OUT / "tt1_score_sources.json"))
    tree = T.OUT / "pack_tree"
    if tree.exists():
        shutil.rmtree(tree)                       # symlinks made by this script only
    root = tree / "tt1"
    for p, s in src.items():
        d = root / "data" / p
        d.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(s, d)
    (root / "data" / "manifests").mkdir(parents=True)
    os.symlink(T.OUT / "tt1_score.csv", root / "data" / "manifests" / "tt1_score.csv")
    os.symlink(T.PN1T / "code", root / "code")
    (root / "hf" / "a12").mkdir(parents=True)
    for f in (T.PN1T / "hf" / "a12").iterdir():
        os.symlink(f.resolve(), root / "hf" / "a12" / f.name)
    (root / "bin").mkdir()
    here = pathlib.Path(__file__).resolve().parent
    os.symlink(here.parent / "PN1" / "rescore.py", root / "bin" / "rescore.py")
    os.symlink(here / "gate_check.py", root / "bin" / "gate_check.py")
    ss = subprocess.run(f"cd {root} && find -L . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum",
                        shell=True, check=True, capture_output=True, text=True).stdout
    (root / "SHA256SUMS").write_text(ss)
    tar = T.OUT / "tt1_pack.tar"
    subprocess.run(["tar", "-C", str(tree), "-chf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "tt1"], check=True)
    h = T.sha(tar)
    (T.OUT / "tt1_pack.tar.sha256").write_text(f"{h}  tt1_pack.tar\n")
    print("pack", tar, tar.stat().st_size, h, "files", len(ss.splitlines()))


def stored_gate(task):
    """stored A100 logits of the gate rows for one PN1 result (R_cam from scores_eval.npz; FFHQ from HN2 or A14)."""
    arm, seed = task[len("PN1_"):].rsplit("_s", 1)
    z = np.load(PN1R / task / "scores_eval.npz")
    m = dict(zip(z["id"].tolist(), z["logit"].tolist()))
    fq = PN1R / f"PN1_HN2_s{seed}" / f"scores_hn2_{arm}.npz"
    if not fq.exists():
        fq = A14 / f"{task}__ffhq.npz"
    z2 = np.load(fq)
    m.update(zip(z2["id"].tolist(), z2["logit"].tolist()))
    refs = T.ref_rows()
    ids = [r["id"] for k in ("R_cam", "R_ffhq", "M_ffhq") for r in refs[k]]
    return np.array(ids), np.array([m[i] for i in ids], np.float32), str(fq)


def build_nets(name, tars):
    tree = T.OUT / f"nets_tree_{name}"
    if tree.exists():
        shutil.rmtree(tree)
    root = tree / "tt1nets"
    (root / "gate_ref").mkdir(parents=True)
    info = {}
    for t in tars:
        t = pathlib.Path(t)
        task = t.name[:-len(".tar")]
        want = (t.parent / f"{task}.tar.sha256").read_text().split()[0]
        assert T.sha(t) == want, t
        d = root / "nets" / task
        d.mkdir(parents=True)
        with tarfile.open(t) as tf:
            for n in ("meta.json", "last_trainable.pt"):
                m = tf.getmember(f"{task}/{n}")
                assert m.isfile()
                (d / n).write_bytes(tf.extractfile(m).read())
        if name == "s401402":
            ids, lg, fq = stored_gate(task)
            np.savez(root / "gate_ref" / f"{task}.npz", id=ids, logit=lg)
            info[task] = dict(tar=str(t), tar_sha256=want, ffhq_ref=fq)
        else:
            info[task] = dict(tar=str(t), tar_sha256=want, ffhq_ref=None)
    (root / "nets.json").write_text(json.dumps(info, indent=1))
    ss = subprocess.run(f"cd {root} && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum",
                        shell=True, check=True, capture_output=True, text=True).stdout
    (root / "SHA256SUMS").write_text(ss)
    tar = T.OUT / f"tt1_nets_{name}.tar"
    subprocess.run(["tar", "-C", str(tree), "-cf", str(tar), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=2026-11-13 00:00:00", "tt1nets"], check=True)
    h = T.sha(tar)
    (T.OUT / f"tt1_nets_{name}.tar.sha256").write_text(f"{h}  {tar.name}\n")
    print("nets", tar, h, list(info))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "list":
        build_list()
    elif cmd == "pack":
        build_pack()
    elif cmd == "nets":
        build_nets(sys.argv[2], sys.argv[3:])
