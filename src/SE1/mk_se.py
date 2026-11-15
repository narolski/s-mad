"""Seam-shortcut training arm (SE1): training manifest train_SE.csv, evaluation manifest se_eval.csv and the overlay tar
that turns the unchanged FS1 pack (pn1_pack_fs.tar, 96c31ae2...) into the SE1 pack when unpacked over it.

train_SE.csv = the unique rows of train_Sb.csv (byte-equal FS1 copy, 5,535 unique images) plus, all as negatives
(label 0, storage history native):
  lad_R3    same-person morph (H with H's other photo), OpenCV-style engine, the 156 ladder TRAINING hosts of Sb
  lad_R3m   mirror self-morph (H with its lossless mirror), OpenCV-style engine, the same 156 hosts
  af0_selfm mirror self-morph of each of Sb's 518 AF0 training photos (src/SE1/build_selfm.py), the u50 engine
then re-balanced by the unchanged amendment-4 rule (src/PN1/mkmanifests.balanced_strata). FaceMorpher images stay out
of training (held-out engine for the development reads).

se_eval.csv = pn1_eval.csv of the FS1 pack (19,797 rows, byte-equal lines; no benchmark row, checked by its builder)
plus development rows only:
  ms1ffhq   1,480 rows of the MS1 FFHQ hold-out (copied byte-equal from the MS1 pack tree; the C2P images)
  splice    dev FaceMorpher S0, S3, S4 (native) of the same 100 development hosts as FS1's OpenCV splice rows
  af0 selfm mirror self-morphs of the 126 AF0 development photos (persons never in training)
Every added path is checked against the forbidden-name rule and against benchmark roots.
  python3 -I mk_se.py   -> /mnt/t7/smad_next/SE1/{manifests/, se1_overlay.tar(.sha256)}
"""
import collections
import csv
import hashlib
import pathlib
import shutil
import subprocess
import sys

sys.path.insert(0, "/home/narolski/smad-next/src/PN1")
import mkmanifests as MM  # noqa: E402

FS = pathlib.Path("/mnt/t7/smad_next/PN1/fs_tree/pn1")
MS1 = pathlib.Path("/mnt/t7/smad_next/MS1/pack_tree/pn1")
OUT = pathlib.Path("/mnt/t7/smad_next/SE1")
EVAL_SHA = "f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045"
SB_SHA = "2cf3fda3affc8dd3d1574857f494037ea0382c8a2d314754b615686401b7fa4a"
MS1_EVAL_SHA = "d1fab6ad4b20f0ec9dd426374ccd56e96368bf7b658b48e3ef31867e1fe470c5"
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split/ladder_split.csv")
EVCOLS = ["id", "path", "label", "klass", "role", "fam", "rung", "strength", "tool", "cell", "host", "neutral"]
BAD = ("fst", "a12sp", "a12-sp", "valx", "frll", "mad22", "mordiff", "dim", "/h1", "fei", "casia", "smad_heldout/mad",
       "smddmorph")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def clean(p):
    s = str(p).lower()
    assert not any(b in s for b in BAD), p
    return p


def main():
    assert sha(FS / "data/manifests/pn1_eval.csv") == EVAL_SHA
    assert sha(FS / "data/manifests/train_Sb.csv") == SB_SHA
    assert sha(MS1 / "data/manifests/pn1_eval.csv") == MS1_EVAL_SHA
    split = {r["pid"]: r for r in csv.DictReader(open(SPLIT))}
    files = {}                                              # overlay path (under pn1/) -> source file

    # ---------------- training manifest
    sb = list(csv.DictReader(open(FS / "data/manifests/train_Sb.csv")))
    uniq = {}
    for r in sb:
        uniq.setdefault(r["id"], r)
    rows = [dict(r) for r in uniq.values()]
    ar1 = {r["id"]: r for r in csv.DictReader(open("/mnt/t7/smad_next/AF0/lists/ar1.csv"))}
    hosts = sorted({ar1[r["id"]]["p1"] for r in rows if r["kind"] == "lad_R0"})
    assert len(hosts) == 156
    for h in hosts:
        assert split[h]["role"] == "train" and split[h]["is_val"] == "0", h
    add = []
    for rung in ("R3", "R3m"):
        got = [r for r in ar1.values() if r["rung"] == rung and r["tool"] == "opencv" and r["p1"] in hosts]
        assert len(got) == 156 and all(r["p2"] == r["p1"] for r in got), (rung, len(got))
        for r in got:
            p = f"train/lad_{rung}/{r['id']}.png"
            files[f"data/{p}"] = clean(r["path"])
            add.append(dict(path=p, label="0", source="smdd", tool="smdd", arm="smdd", val="0", mixed="0", id=r["id"],
                            kind=f"lad_{rung}", db=r["p1"].split(":")[0], hist="native"))
    sm = list(csv.DictReader(open(OUT / "selfm_build.csv")))
    for r in sm:
        if r["split"] != "train":
            continue
        assert sha(r["path"]) == r["sha256"]
        p = f"train/af0_selfm/{r['id']}_selfm.png"
        files[f"data/{p}"] = clean(r["path"])
        add.append(dict(path=p, label="0", source="smdd", tool="smdd", arm="smdd", val="0", mixed="0",
                        id=f"{r['id']}_selfm", kind="af0_selfm", db=r["db"], hist="native"))
    assert sum(a["kind"] == "af0_selfm" for a in add) == 518
    ids = [r["id"] for r in rows] + [a["id"] for a in add]
    assert len(ids) == len(set(ids))
    allrows = rows + add
    bal, strata = MM.balanced_strata(allrows)
    (OUT / "manifests").mkdir(parents=True, exist_ok=True)
    mt = OUT / "manifests" / "train_SE.csv"
    with open(mt, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MM.TRCOLS)
        w.writeheader()
        w.writerows(bal)

    # ---------------- evaluation manifest
    ev_lines = open(FS / "data/manifests/pn1_eval.csv").read().splitlines()
    assert ev_lines[0].split(",") == EVCOLS
    fs_ev = list(csv.DictReader(open(FS / "data/manifests/pn1_eval.csv")))
    extra = []
    for r in csv.DictReader(open(MS1 / "data/manifests/pn1_eval.csv")):
        if r["fam"] == "ms1ffhq":
            files[f"data/{r['path']}"] = MS1 / "data" / r["path"]
            extra.append({k: r[k] for k in EVCOLS})
    assert len(extra) == 1480
    dev_hosts = {g: sorted({r["host"] for r in fs_ev if r["fam"] == "splice" and r["role"] == "dev" and r["rung"] == g})
                 for g in ("S0", "S3", "S4")}
    assert all(len(v) == 100 for v in dev_hosts.values())
    sp2 = list(csv.DictReader(open("/mnt/t7/smad_next/AR1/manifest_splice2.csv")))
    for g, klass in (("S0", "single"), ("S3", "single"), ("S4", "attack")):
        got = [r for r in sp2 if r["tool"] == "facemorpher" and r["variant"] == "native" and r["rung"] == g
               and r["p1"] in dev_hosts[g]]
        assert len(got) == 100, (g, len(got))
        for r in got:
            assert split[r["p1"]]["role"] == "dev"
            p = f"eval/se1/{r['id']}.png"
            files[f"data/{p}"] = clean(r["path"])
            extra.append(dict(id=r["id"], path=p, label="1" if klass == "attack" else "0", klass=klass, role="dev",
                              fam="splice", rung=g, strength="", tool="facemorpher", cell="", host=r["p1"], neutral=""))
    for r in sm:
        if r["split"] != "dev":
            continue
        p = f"eval/se1/{r['id']}_selfm.png"
        files[f"data/{p}"] = clean(r["path"])
        extra.append(dict(id=f"{r['id']}_selfm", path=p, label="0", klass="single", role="dev", fam="af0",
                          rung="selfm", strength="", tool="af0engine", cell="", host=r["person"], neutral=""))
    assert sum(e["rung"] == "selfm" for e in extra) == 126
    eids = [r["id"] for r in fs_ev] + [e["id"] for e in extra]
    assert len(eids) == len(set(eids))
    me = OUT / "manifests" / "se_eval.csv"
    with open(me, "w", newline="") as f:
        f.write("\n".join(ev_lines) + "\n")
        w = csv.DictWriter(f, fieldnames=EVCOLS, lineterminator="\n")
        w.writerows(extra)
    files["data/manifests/train_SE.csv"] = mt
    files["data/manifests/se_eval.csv"] = me

    # ---------------- overlay tree + tar
    tree = OUT / "overlay_tree"
    if tree.exists():
        shutil.rmtree(tree)
    for rel, src in files.items():
        d = tree / "pn1" / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, d)
    fs_names = {ln.split("  ", 1)[1] for ln in open(FS / "SHA256SUMS").read().splitlines()}
    clash = sorted(set(files) & fs_names)
    assert not clash, clash[:5]                              # the overlay never replaces an FS1 file
    rels = sorted(files)
    (tree / "pn1" / "SE1SUMS").write_text("".join(f"{sha(tree / 'pn1' / r)}  {r}\n" for r in rels))
    ov = OUT / "se1_overlay.tar"
    subprocess.run(["tar", "-C", str(tree), "-cf", str(ov), "--sort=name", "--owner=0", "--group=0", "--numeric-owner",
                    "--mtime=@0", "pn1/SE1SUMS"] + [f"pn1/{r}" for r in rels], check=True)
    (OUT / "se1_overlay.tar.sha256").write_text(f"{sha(ov)}  se1_overlay.tar\n")
    kinds = collections.Counter(r["kind"] for r in allrows)
    summ = dict(train_SE=dict(unique=len(allrows), rows=len(bal), by_kind=dict(kinds), strata=strata, sha256=sha(mt),
                              unique_by_label=dict(collections.Counter(r["label"] for r in allrows)),
                              draws_per_row_6250x256=round(6250 * 256 / len(bal), 1)),
                se_eval=dict(rows=len(eids), added=len(extra), sha256=sha(me),
                             added_by=dict(collections.Counter((e["fam"], e["rung"], e["strength"], e["tool"])
                                                               .__str__() for e in extra))),
                overlay=dict(files=len(rels), sha256=sha(ov), bytes=ov.stat().st_size))
    import json
    json.dump(summ, open(OUT / "manifests" / "se1_summary.json", "w"), indent=1)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
