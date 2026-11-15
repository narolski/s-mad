"""Build the single AD4 pack (one tar) from existing, registered inputs only. No image is created or changed: every
image is a byte copy (sha256 checked against its registered list where one exists).

  python3 -I build_pack.py --out /mnt/t7/smad_next/AD4/ad4_pack.tar

Contents (top directory ad4/):
  code/smadcvpr/*.py, code/morphmamba/**  from the A47 job root jobroot_a47.tar (sha256 0ba35b33..., git archive of
                                          a47 ffcbc7f + morphmamba/data), names containing fst / valx / a12sp skipped
  src/ad4_score.py                        this directory's scorer
  hf/a12/<tag>.safetensors                CLIP ViT-B/16 and ViT-L/14 (timm hub pytorch_model.bin, loaded with
                                          weights_only=True, written as safetensors: the A12 "converted" path)
  data/manifests/train_i3.csv             the registered A47 I-3 manifest, unchanged (50,000 rows)
  data/manifests/train_perm_s<seed>.csv   the same rows, label column permuted by random.Random(2026111100 + seed)
  data/train/smdd/os25k_bf_t/*.png        the 25,000 SMDD bona fide natives the manifest names
  data/train/smdd_a47e7/**                the 25,000 registered copies (data47/i3, checked against its SHA256SUMS)
  data/eval/{dim,frllm,mordiff}/...       eval.csv rows of those sets, variants orig + resmatch (E7)
  data/eval/mad22c/{native,e7}/<fam>/*    the corrected MAD22 canonical512 inputs (checked against
                                          PROCESSED_SHA256SUMS)
  data/manifests/ad4_eval.csv             id,path,set,family,label,variant,src_id
  SHA256SUMS                              every file above (relative to ad4/)
"""
import argparse
import csv
import hashlib
import io
import json
import pathlib
import random
import re
import sys
import tarfile
import time

A47_JOBROOT = pathlib.Path("/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/"
                           "scratchpad/a47/jobroot_a47.tar")
A47_JOBROOT_SHA = "0ba35b335e39630aa291eca32f44f68d9960e0088b020348854b1036e9280ce9"
I3 = pathlib.Path("/mnt/t7/smad_heldout/a47/data47/i3")
SMAD = pathlib.Path("/home/narolski/mambamorph-code/smadcvpr_data")
MAD22C = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
HUB = pathlib.Path.home() / ".cache/huggingface/hub"
CLIP = {"vit_base_patch16_clip_224.openai": "53b401837e5baa82115d3b6db60c6fff43cfd1a6412e48ed0193d54a69d2f993",
        "vit_large_patch14_clip_224.openai": "eb70c15b117effa76315db43fcbd9f32a655292fc861798343939a02f561c6ae"}
SEEDS = (401, 402, 403, 404, 405)
PERM_BASE = 2026111100
EVAL_SETS = ("dim", "frllm", "mordiff")
EVAL_VARIANTS = ("orig", "resmatch")
MAD22_FAMS = ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph")
SKIP = re.compile(r"fst|valx|a12sp|a12-sp", re.I)
HERE = pathlib.Path(__file__).resolve().parent


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", required=True, help="scratch dir for the converted weights")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    if out.exists():
        sys.exit(f"{out} exists; never overwritten")
    work = pathlib.Path(a.work)
    sums = []          # (sha, relpath)
    t0 = time.time()
    tf = tarfile.open(str(out) + ".part", "w", format=tarfile.GNU_FORMAT)

    def add_bytes(rel, data):
        ti = tarfile.TarInfo("ad4/" + rel)
        ti.size, ti.mtime, ti.mode = len(data), 1762819200, 0o644
        tf.addfile(ti, io.BytesIO(data))
        sums.append((sha_bytes(data), rel))

    def add_file(rel, src, want=None):
        data = pathlib.Path(src).read_bytes()
        h = sha_bytes(data)
        if want is not None and h != want:
            sys.exit(f"{src}: sha256 {h} != registered {want}")
        ti = tarfile.TarInfo("ad4/" + rel)
        ti.size, ti.mtime, ti.mode = len(data), 1762819200, 0o644
        tf.addfile(ti, io.BytesIO(data))
        sums.append((h, rel))
        return h

    # code
    if sha_file(A47_JOBROOT) != A47_JOBROOT_SHA:
        sys.exit("jobroot_a47.tar is not the registered A47 job root")
    n_code = 0
    with tarfile.open(A47_JOBROOT) as jr:
        for m in jr.getmembers():
            if not m.isfile():
                continue
            p = m.name.split("/", 1)[1] if "/" in m.name else m.name
            top = p.split("/")[0]
            if SKIP.search(p):
                continue
            if top == "smadcvpr" and p.count("/") == 1 and p.endswith(".py") or top == "morphmamba":
                add_bytes("code/" + p, jr.extractfile(m).read())
                n_code += 1
    add_bytes("src/ad4_score.py", (HERE / "ad4_score.py").read_bytes())
    print(f"code: {n_code} files", flush=True)

    # weights: hub pytorch_model.bin (blob sha256 = its file name) -> safetensors
    import torch
    from safetensors.torch import save_file
    work.mkdir(parents=True, exist_ok=True)
    wsha = {}
    for tag, blob in CLIP.items():
        src = HUB / f"models--timm--{tag}" / "blobs" / blob
        if sha_file(src) != blob:
            sys.exit(f"{src}: content differs from its blob name")
        sd = torch.load(src, map_location="cpu", weights_only=True)
        sd = {k: v.contiguous() for k, v in sd.items()}
        dst = work / f"{tag}.safetensors"
        save_file(sd, str(dst))
        wsha[tag] = add_file(f"hf/a12/{tag}.safetensors", dst)
        print(f"weights {tag}: {len(sd)} tensors, sha256 {wsha[tag]}", flush=True)

    # training data
    i3sums = {}
    for ln in open(I3 / "SHA256SUMS"):
        h, p = ln.rstrip("\n").split(None, 1)
        i3sums[p.lstrip("*").removeprefix("./")] = h
    man = (I3 / "manifests" / "train.csv").read_bytes()
    man_sha = sha_bytes(man)
    if man_sha != i3sums["manifests/train.csv"]:
        sys.exit("data47/i3 manifests/train.csv is off its SHA256SUMS line")
    add_bytes("data/manifests/train_i3.csv", man)
    rows = list(csv.DictReader(io.StringIO(man.decode())))
    hdr = list(rows[0].keys())
    assert len(rows) == 50000 and sum(r["label"] == "1" for r in rows) == 25000
    wsize = {}
    for ln in open(work.parent / "wcss_data_train_os25k.content"):
        t, s, p = ln.rstrip("\n").split("\t")[:3]
        wsize[p.removeprefix("data/")] = int(s)
    n_nat = n_cp = 0
    for r in rows:
        p = r["path"]
        if r["label"] == "0":
            src = SMAD / p
            if src.stat().st_size != wsize.get(p, -1):
                sys.exit(f"{p}: local size {src.stat().st_size} != WCSS data_train size {wsize.get(p)}")
            add_file("data/" + p, src)
            n_nat += 1
        else:
            k = p
            want = i3sums.get(k) or i3sums.get(k.removeprefix("train/"))
            if want is None:
                sys.exit(f"{p}: not in data47/i3/SHA256SUMS")
            add_file("data/" + p, I3 / p, want)
            n_cp += 1
    print(f"train: {n_nat} natives, {n_cp} copies; manifest sha256 {man_sha}", flush=True)
    perms = {}
    for s in SEEDS:
        lab = [r["label"] for r in rows]
        random.Random(PERM_BASE + s).shuffle(lab)
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=hdr, lineterminator="\n")
        w.writeheader()
        for r, l in zip(rows, lab):
            w.writerow(dict(r, label=l))
        b = buf.getvalue().encode()
        add_bytes(f"data/manifests/train_perm_s{s}.csv", b)
        perms[s] = {"sha256": sha_bytes(b), "changed": sum(l != r["label"] for r, l in zip(rows, lab)),
                    "n1": lab.count("1")}
    print(f"permutations: {perms}", flush=True)

    # evaluation data
    ev = []
    for r in csv.DictReader(open(SMAD / "manifests" / "eval.csv")):
        if r["set"] in EVAL_SETS and r["variant"] in EVAL_VARIANTS:
            add_file("data/" + r["path"], SMAD / r["path"])
            ev.append({"id": r["id"], "path": r["path"], "set": r["set"], "family": r["family"],
                       "label": r["label"], "variant": r["variant"], "src_id": r["id"]})
    psums = {}
    for ln in open(MAD22C / "PROCESSED_SHA256SUMS"):
        h, p = ln.rstrip("\n").split(None, 1)
        psums[p.lstrip("*")] = h
    n_m = 0
    for d in sorted((MAD22C / "native").iterdir()):
        for f in sorted(d.iterdir()):
            rel = f"native/{d.name}/{f.name}"
            add_file(f"data/eval/mad22c/{rel}", f, psums[rel])
            bona = d.name == "BonaFide"
            ev.append({"id": f"mad22c/{rel}", "path": f"eval/mad22c/{rel}", "set": "mad22c",
                       "family": "mad22c_bona" if bona else d.name, "label": "0" if bona else "1",
                       "variant": "orig", "src_id": rel})
            n_m += 1
    for fam in MAD22_FAMS:
        for f in sorted((MAD22C / "e7" / fam).iterdir()):
            rel = f"e7/{fam}/{f.name}"
            add_file(f"data/eval/mad22c/{rel}", f, psums[rel])
            ev.append({"id": f"mad22c/{rel}", "path": f"eval/mad22c/{rel}", "set": "mad22c", "family": fam,
                       "label": "0", "variant": "resmatch", "src_id": rel})
            n_m += 1
    if n_m != 5707:
        sys.exit(f"corrected MAD22: {n_m} files, 5707 expected")
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(ev[0].keys()), lineterminator="\n")
    w.writeheader()
    w.writerows(ev)
    evb = buf.getvalue().encode()
    add_bytes("data/manifests/ad4_eval.csv", evb)
    print(f"eval: {len(ev)} rows (mad22c {n_m}); ad4_eval.csv sha256 {sha_bytes(evb)}", flush=True)

    info = {"jobroot_a47_sha256": A47_JOBROOT_SHA, "i3_manifest_sha256": man_sha, "weights_safetensors": wsha,
            "weights_source_blobs": CLIP, "perm_base": PERM_BASE, "perms": perms, "eval_rows": len(ev),
            "eval_manifest_sha256": sha_bytes(evb), "n_files": len(sums) + 1}
    add_bytes("build_info.json", json.dumps(info, indent=1).encode())
    sb = "".join(f"{h}  {p}\n" for h, p in sums).encode()
    ti = tarfile.TarInfo("ad4/SHA256SUMS")
    ti.size, ti.mtime, ti.mode = len(sb), 1762819200, 0o644
    tf.addfile(ti, io.BytesIO(sb))
    tf.close()
    pathlib.Path(str(out) + ".part").rename(out)
    tsha = sha_file(out)
    pathlib.Path(str(out) + ".sha256").write_text(f"{tsha}  {out.name}\n")
    print(f"PACK {out} sha256 {tsha} files {len(sums) + 1} in {time.time() - t0:.0f} s", flush=True)
    print(json.dumps(info), flush=True)


if __name__ == "__main__":
    main()
