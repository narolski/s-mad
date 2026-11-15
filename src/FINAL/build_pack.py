"""Sealed MAD22 read (FINAL): build the one pack. Existing files only, plus constant-colour region blanking (an allowed
image operation) for the border-equalised form. No score is computed or read here: the networks' stored development
scores are not opened by this script (they travel inside the network tars).

Pack tree (top directory final/):
  code/**                        the PN1 code of the fresh-seed pack (pn1_pack_fs.tar pn1/code), checked against its SHA256SUMS
  hf/a12/<base>.safetensors      the CLIP ViT-B/16 base weights of the same pack (sha256 pinned in final_config.json)
  bin/rescore.py, bin/rescore_tf32.py      the pinned scorer (src/PN1/rescore.py run through src/TT1/rescore_tf32.py)
  nets/<name>.tar                the network result tars named in final_config.json (sha256 checked)
  data/eval/**                   gate rows (FS1 development frames) and MAD22 frames (byte copies, sha256 checked)
  data/eval/be/<fam>/{morph,native,e7}/*.png   border-equalised copies (only for families whose mask is not empty)
  data/masks/<fam>.png           the border mask of each family (255 = blanked)
  data/manifests/final_gate.csv  whole 64-row batches of the FS1 evaluation manifest (rule in final_config.json)
  data/manifests/final_bench.csv every MAD22 row, fam = "final", in a fixed order
  build_info.json, SHA256SUMS
Border-equalised (BE) form: for family f, mask_f = union over the family's morph frames, its E7 frames and the 204
native genuine frames of each frame's largest exactly-black (max over channels = 0) 8-connected region touching the
frame edge (TT1 build_border_ref.edge_mask definition); mask_f pixels are set to (0, 0, 0) in every image of the cell,
both classes. Lossless PNG (cv2.imwrite). Families with an empty mask get no copies (BE = standard there).
  python3 -I build_pack.py [--limit-bench N]   (N > 0: test pack with N MAD22 rows per pool; never uploaded)
Environment (tests only): FINAL_CONFIG = another config file (stand-in), FINAL_OUTD = another output folder."""
import argparse
import csv
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

os.environ.setdefault("OMP_NUM_THREADS", "2")
import cv2  # noqa: E402
import numpy as np  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
CFG_PATH = pathlib.Path(os.environ.get("FINAL_CONFIG", HERE / "final_config.json"))
CFG = json.load(open(CFG_PATH))
OUTD = pathlib.Path(os.environ.get("FINAL_OUTD", "/mnt/t7/smad_next/FINAL"))
SEALED = re.compile(r"fst|valx|a12sp|a12-sp", re.I)
BAD = re.compile(r"fst|valx|a12sp|a12-sp|frllm|mordiff|dim_|gtest|fei|h1poisson|casia", re.I)   # data rows only
RX_BONA = re.compile(r"^(\d{3})_(\d{2})\.png$")
RX_MORPH = re.compile(r"^(\d{3})_(\d{2})-vs-(\d{3})_(\d{2})\.png$")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def edge_mask(frame):
    z = (frame.max(2) == 0).astype(np.uint8)
    n, lab = cv2.connectedComponents(z, connectivity=8)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    edge = [k for k in edge if k != 0]
    if not edge:
        return np.zeros(z.shape, bool)
    sizes = [(int((lab == k).sum()), k) for k in edge]
    return lab == max(sizes)[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit-bench", type=int, default=0)
    a = ap.parse_args()
    lim = a.limit_bench
    tag = CFG["read_id"] + (f"_test{lim}" if lim else "")
    tree = OUTD / f"tree_{tag}"
    root = tree / "final"
    if tree.exists():
        shutil.rmtree(tree)
    for d in ("code", "hf/a12", "bin", "nets", "data/eval", "data/masks", "data/manifests"):
        (root / d).mkdir(parents=True, exist_ok=True)
    info = {"config_sha256": sha(CFG_PATH), "limit_bench": lim}

    # ---- code, base weights (fresh-seed pack, checked against its SHA256SUMS)
    G = CFG["gate"]
    src = pathlib.Path(G["source_tree"])
    sums = dict(reversed(ln.rstrip("\n").split("  ", 1)) for ln in open(src / "SHA256SUMS"))
    n_code = 0
    for p in sorted((src / "code").rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            rel = p.relative_to(src).as_posix()
            if SEALED.search(rel):
                sys.exit(f"forbidden name in code: {rel}")
            assert sums[rel] == sha(p), rel
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(p, root / rel)
            n_code += 1
    wname = "vit_base_patch16_clip_224.openai.safetensors"
    wp = src / "hf/a12" / wname
    assert sha(wp) == CFG["scorer"]["base_weights_" + wname] == sums[f"hf/a12/{wname}"]
    os.symlink(wp, root / "hf/a12" / wname)
    info["n_code_files"] = n_code

    # ---- scorer
    for f, d in (("rescore.py", "/home/narolski/smad-next/src/PN1/rescore.py"),
                 ("rescore_tf32.py", "/home/narolski/smad-next/src/TT1/rescore_tf32.py")):
        assert sha(d) == CFG["scorer"][f], f
        shutil.copy(d, root / "bin" / f)

    # ---- networks (tars by pin; their stored scores are not opened here)
    for n in CFG["networks"]:
        assert sha(n["tar"]) == n["sha256"], n["name"]
        os.symlink(n["tar"], root / "nets" / f"{n['name']}.tar")

    # ---- gate rows: whole 64-row batches of the FS1 evaluation manifest, order kept
    man = src / G["source_manifest"]
    assert sha(man) == G["source_manifest_sha256"]
    rows = list(csv.DictReader(open(man)))
    B, K = G["batch"], G["keep_every_kth_batch"]
    keep = [r for i, r in enumerate(rows) if (i // B) % K == 0]
    groups = {(r["fam"], r["label"]) for r in rows}
    kept = {(r["fam"], r["label"]) for r in keep}
    assert groups == kept, ("gate subset misses a development family/class", groups - kept)
    last_batch = (len(rows) - 1) // B
    for r in keep:
        if BAD.search(r["path"]) or BAD.search(r["id"]):
            sys.exit(f"forbidden row in gate list: {r['id']}")
        p = src / "data" / r["path"]
        assert sums["data/" + r["path"]] == sha(p), r["path"]
        (root / "data" / r["path"]).parent.mkdir(parents=True, exist_ok=True)
        if not (root / "data" / r["path"]).exists():
            os.symlink(p, root / "data" / r["path"])
    gr = [dict(r, fam="gate") for r in keep]
    with open(root / "data/manifests/final_gate.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(gr[0])); w.writeheader(); w.writerows(gr)
    info["gate"] = dict(rows=len(gr), batches=len({i // B for i, _ in enumerate(rows) if (i // B) % K == 0}),
                        of_rows=len(rows), last_partial_batch_included=(last_batch % K == 0),
                        groups={f"{k[0]}|{k[1]}": sum((r["fam"], r["label"]) == k for r in keep) for k in sorted(groups)})

    # ---- MAD22 frames (byte copies, checked against PROCESSED_SHA256SUMS)
    M = CFG["mad22"]
    mroot = pathlib.Path(M["root"])
    psums = {}
    for ln in open(mroot / M["sums"]):
        h, p = ln.rstrip("\n").split(None, 1)
        psums[p.lstrip("*")] = h
    assert len(psums) == M["n_files"]
    bench = []

    def add_row(rel_data, src_p, label, family, pool, form, persons, expr):
        dst = root / "data" / rel_data
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src_p is not None:
            os.symlink(src_p, dst)
        bench.append(dict(id=rel_data, path=rel_data, label=str(label), fam="final", family=family, pool=pool,
                          form=form, pa=persons[0], pb=persons[-1], expr=expr))

    def take(files):
        return files[:lim] if lim else files

    bona = take(sorted((mroot / "native/BonaFide").glob("*.png")))
    fams = M["families"]
    per = {}
    for f in bona:
        m = RX_BONA.match(f.name); assert m, f.name
        assert sha(f) == psums[f"native/BonaFide/{f.name}"]
        add_row(f"eval/mad22c/native/BonaFide/{f.name}", f, 0, "bona", "native", "std", (m.group(1),), m.group(2))
    for fam in fams:
        mf = take(sorted((mroot / "native" / fam).glob("*.png")))
        ef = take(sorted((mroot / "e7" / fam).glob("*.png")))
        per[fam] = (mf, ef)
        for f in mf:
            m = RX_MORPH.match(f.name); assert m, f.name
            assert sha(f) == psums[f"native/{fam}/{f.name}"]
            add_row(f"eval/mad22c/native/{fam}/{f.name}", f, 1, fam, "morph", "std", (m.group(1), m.group(3)),
                    f"{m.group(2)}|{m.group(4)}")
        for f in ef:
            m = RX_BONA.match(f.name); assert m, f.name
            assert sha(f) == psums[f"e7/{fam}/{f.name}"]
            add_row(f"eval/mad22c/e7/{fam}/{f.name}", f, 0, fam, "e7", "std", (m.group(1),), m.group(2))

    # ---- border-equalised copies
    be = {}
    for fam in fams:
        mf, ef = per[fam]
        U = np.zeros((512, 512), bool)
        for f in list(mf) + list(ef) + list(bona):
            im = cv2.imread(str(f), cv2.IMREAD_COLOR)
            assert im.shape == (512, 512, 3)
            U |= edge_mask(im)
        cv2.imwrite(str(root / "data/masks" / f"{fam}.png"), (U * 255).astype(np.uint8))
        be[fam] = dict(mask_share=float(U.mean()), mask_pixels=int(U.sum()),
                       mask_central_share=float(U[150:400, 128:384].mean()))
        if not U.any():
            be[fam]["copies"] = 0
            continue
        n = 0
        for pool, files, lab in (("morph", mf, 1), ("native", bona, 0), ("e7", ef, 0)):
            for f in files:
                im = cv2.imread(str(f), cv2.IMREAD_COLOR)
                im[U] = 0
                rel = f"eval/be/{fam}/{pool}/{f.name}"
                dst = root / "data" / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                assert cv2.imwrite(str(dst), im)
                back = cv2.imread(str(dst), cv2.IMREAD_COLOR)
                assert np.array_equal(back, im)                 # lossless
                if lab == 1:
                    m = RX_MORPH.match(f.name); pp, ex = (m.group(1), m.group(3)), f"{m.group(2)}|{m.group(4)}"
                else:
                    m = RX_BONA.match(f.name); pp, ex = (m.group(1),), m.group(2)
                add_row(rel, None, lab, fam if pool != "native" else "bona", pool, "be:" + fam, pp, ex)
                n += 1
        be[fam]["copies"] = n
    info["be"] = be
    with open(root / "data/manifests/final_bench.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(bench[0])); w.writeheader(); w.writerows(bench)
    info["bench_rows"] = len(bench)
    ids = [r["id"] for r in bench]
    assert len(ids) == len(set(ids))
    for r in bench:
        assert not BAD.search(r["path"]), r["path"]

    # ---- sums, tar
    json.dump(info, open(root / "build_info.json", "w"), indent=1)
    lines = []
    for p in sorted(root.rglob("*")):
        if p.is_file() or p.is_symlink():
            rel = p.relative_to(root).as_posix()
            if rel != "SHA256SUMS":
                lines.append(f"{sha(p)}  {rel}")
    (root / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    out = OUTD / f"{tag}_pack.tar"
    subprocess.run(["tar", "-C", str(tree), "--dereference", "--sort=name", "--owner=0", "--group=0",
                    "--mtime=2026-11-13 00:00Z", "-cf", str(out), "final"], check=True)
    h = sha(out)
    (OUTD / f"{tag}_pack.tar.sha256").write_text(f"{h}  {out.name}\n")
    print(json.dumps(dict(pack=str(out), sha256=h, bytes=out.stat().st_size, **{k: info[k] for k in ("gate", "be", "bench_rows")}), indent=1))


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
