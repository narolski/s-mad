"""Threshold transfer on unseen genuine sources (TT1), step 2a: extract the genuine pools.

Copies the encoded image bytes VERBATIM (no decode/re-encode, no resize) into /mnt/t7/smad_next/TT1/raw/<source>/ and
writes the raw manifest /mnt/t7/smad_next/TT1/raw_manifest.csv (copy in the experiment folder).

Sources (genuine only; none is a benchmark of this sprint, none was used in training):
  anti-spoofing sets, genuine ("live") frames only, 224x224 JPEG, /mnt/t7/Datasety/datasets_processed/<set>/:
    replay_attack, msu_mfsd, oulu_npu, casia_fasd. Genuine = metadata.json label "Bona fide"; the script asserts that
    this agrees with each set's documented file-name convention on EVERY row (genuine and spoof), see GENUINE_RULE.
  face-verification validation packs, 112x112 JPEG, /mnt/t7/Datasety/downloads/CASIA-Webface/:
    lfw.bin, calfw.bin (one family "lfw_calfw": CALFW is built from LFW people), cfp_ff.bin, agedb_30.bin.
    NOT used: train.rec (CASIA-WebFace, closed: source of the H1 benchmark), cplfw.bin, cfp_fp.bin.
    The .bin files are Python pickles (list of encoded images, list of same/different flags; pair i = slots 2i, 2i+1).
    They are loaded ONLY with RestrictedUnpickler (numpy _reconstruct / ndarray / dtype; every other global refused);
    run this script with python -I.
Distinct images: by sha256 of the encoded bytes (first slot kept; n_slots counts repeats).
Pseudo-identities (packs have no identity labels): connected components (union-find) over the "same" pairs, per family;
LFW and CALFW are joined into one graph (shared byte-identical images link them). An image in no "same" pair is its
own component. Anti-spoofing sets: the person id of the file name (CASIA-FASD subject numbers restart between train and
test, so its person id is "<split>_<number>").
Measurements on the raw decoded image (measurement only, no image is written from them):
  lap_var     variance of cv2.Laplacian(grey, CV_64F) with grey = cv2.cvtColor(BGR, COLOR_BGR2GRAY) (cv2.imread decode)
  chroma_mean mean over pixels of (|R-G| + |G-B|)/2 on the decoded 8-bit image
  greyscale   1 if the JPEG is single-channel (PIL mode "L") or chroma_mean < 1.0
  python3 -I extract.py [--limit 8]
"""
import argparse
import collections
import csv
import hashlib
import io
import json
import pathlib
import pickle
import re
import shutil

import cv2
import numpy as np
from PIL import Image

AS = pathlib.Path("/mnt/t7/Datasety/datasets_processed")
CW = pathlib.Path("/mnt/t7/Datasety/downloads/CASIA-Webface")
OUT = pathlib.Path("/mnt/t7/smad_next/TT1")
RES = pathlib.Path("/home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine")
ANTISPOOF = ("replay_attack", "msu_mfsd", "oulu_npu", "casia_fasd")
PACKS = (("lfw", "lfw_calfw"), ("calfw", "lfw_calfw"), ("cfp_ff", "cfp_ff"), ("agedb_30", "agedb_30"))
FORBIDDEN = ("train.rec", "train.idx", "train.lst", "cplfw.bin", "cfp_fp.bin")


def _stem(m):
    return m["origin_id"].split("/")[-1].rsplit(".", 1)[0]


# documented genuine conventions (dataset documentation): Replay-Attack keeps live videos under "real/"; MSU-MFSD names
# live videos "real_client..."; OULU-NPU names videos Phone_Session_User_File, File 1 = real access; CASIA-FASD videos
# 1, 2 (low, normal quality) and HR_1 (high quality) are genuine, 3-8 and HR_2-HR_4 attacks.
GENUINE_RULE = {
    "replay_attack": lambda m: "/real/" in m["origin_id"],
    "msu_mfsd": lambda m: m["origin_id"].startswith("real_"),
    "oulu_npu": lambda m: _stem(m).split("_")[-1] == "1",
    "casia_fasd": lambda m: re.fullmatch(r"(train|test)_release_\d+_(1|2|HR_1)", m["origin_id"]) is not None,
}


def person_of(src, m):
    o = m["origin_id"]
    if src in ("replay_attack", "msu_mfsd"):
        return re.search(r"client(\d+)", o).group(1)
    if src == "oulu_npu":
        return _stem(m).split("_")[2]
    if src == "casia_fasd":
        g = re.fullmatch(r"(train|test)_release_(\d+)_.*", o)
        return f"{g.group(1)}_{int(g.group(2))}"
    raise KeyError(src)


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        ok = {("numpy.core.multiarray", "_reconstruct"): np.core.multiarray._reconstruct,
              ("numpy", "ndarray"): np.ndarray, ("numpy", "dtype"): np.dtype}
        if (module, name) in ok:
            return ok[(module, name)]
        raise pickle.UnpicklingError(f"refused global {module}.{name}")


def load_pack(p):
    assert p.name not in FORBIDDEN
    with open(p, "rb") as f:
        bins, issame = RestrictedUnpickler(f, encoding="bytes").load()
    bins = [b.tobytes() if hasattr(b, "tobytes") else bytes(b) for b in bins]
    issame = [bool(x) for x in issame]
    assert len(bins) == 2 * len(issame), (p, len(bins), len(issame))
    return bins, issame


def measure(data):
    arr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    assert img is not None
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lap = float(cv2.Laplacian(grey, cv2.CV_64F).var())
    b, g, r = (img[..., i].astype(np.int16) for i in range(3))
    chroma = float(((np.abs(r - g) + np.abs(g - b)) / 2.0).mean())
    pim = Image.open(io.BytesIO(data))
    return dict(width=img.shape[1], height=img.shape[0], format=pim.format, pil_mode=pim.mode,
                lap_var=round(lap, 4), chroma_mean=round(chroma, 4),
                greyscale=int(pim.mode == "L" or chroma < 1.0))


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="test: first N images per source")
    a = ap.parse_args()
    raw = OUT / ("raw_test" if a.limit else "raw")
    rows, report = [], dict(antispoof={}, packs={}, shared_between_packs={})
    # ---- anti-spoofing sets
    for src in ANTISPOOF:
        meta = json.load(open(AS / src / "metadata.json"))
        lab = [m["label"] == "Bona fide" for m in meta]
        conv = [GENUINE_RULE[src](m) for m in meta]
        agree = sum(x == y for x, y in zip(lab, conv))
        assert agree == len(meta), (src, agree, len(meta))
        report["antispoof"][src] = dict(rows=len(meta), labels=dict(collections.Counter(m["label"] for m in meta)),
                                        genuine_by_label=sum(lab), genuine_by_name=sum(conv), agree=agree)
        gen = sorted((m for m in meta if m["label"] == "Bona fide"), key=lambda m: m["processed_filename"])
        if a.limit:
            gen = gen[:a.limit]
        (raw / src).mkdir(parents=True, exist_ok=True)
        seen = {}
        for m in gen:
            sp = AS / src / m["processed_filename"]
            data = sp.read_bytes()
            h = hashlib.sha256(data).hexdigest()
            if h in seen:
                seen[h]["n_slots"] += 1
                continue
            dst = raw / src / m["processed_filename"]
            shutil.copyfile(sp, dst)
            r = dict(source=src, family=src, person=f"{src}:{person_of(src, m)}", person_kind="label",
                     orig_file=str(sp), pack_index="", origin_id=m["origin_id"], origin_set=m["origin_set"],
                     raw_path=str(dst), sha256=h, bytes=len(data), n_slots=1, **measure(data))
            seen[h] = r
            rows.append(r)
    # ---- verification packs
    packdata = {name: load_pack(CW / f"{name}.bin") for name, _ in PACKS}
    hashes = {name: [hashlib.sha256(b).hexdigest() for b in bins] for name, (bins, _) in packdata.items()}
    names = [n for n, _ in PACKS]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            o = len(set(hashes[names[i]]) & set(hashes[names[j]]))
            report["shared_between_packs"][f"{names[i]}&{names[j]}"] = o
    fam_of = dict(PACKS)
    uf = {f: UF() for f in set(fam_of.values())}
    for name, (bins, issame) in packdata.items():
        u = uf[fam_of[name]]
        hs = hashes[name]
        for h in hs:
            u.find(h)
        for k, same in enumerate(issame):
            if same:
                u.union(hs[2 * k], hs[2 * k + 1])
    comp_id = {}
    for fam, u in uf.items():
        roots = sorted({u.find(x) for x in u.p})
        idx = {r: n for n, r in enumerate(roots)}
        comp_id[fam] = {x: f"{fam}:c{idx[u.find(x)]:05d}" for x in u.p}
    taken = set()          # family-level: an image shared by LFW and CALFW is kept once (under the first pack)
    for name, (bins, issame) in packdata.items():
        fam = fam_of[name]
        hs = hashes[name]
        report["packs"][name] = dict(slots=len(bins), pairs=len(issame), same_pairs=sum(issame), distinct=len(set(hs)))
        (raw / name).mkdir(parents=True, exist_ok=True)
        first = {}
        for k, h in enumerate(hs):
            if h in first:
                first[h]["n_slots"] += 1
                continue
            if (fam, h) in taken:
                first[h] = dict(n_slots=0)   # counted, not kept again
                continue
            if a.limit and len([1 for r in rows if r["source"] == name]) >= a.limit:
                first[h] = dict(n_slots=0)
                continue
            data = bins[k]
            assert data[:2] == b"\xff\xd8", (name, k)
            dst = raw / name / f"{name}_{k:05d}.jpg"
            dst.write_bytes(data)
            r = dict(source=name, family=fam, person=comp_id[fam][h], person_kind="pseudo_cc_same_pairs",
                     orig_file=str(CW / f"{name}.bin"), pack_index=k, origin_id="", origin_set="",
                     raw_path=str(dst), sha256=h, bytes=len(data), n_slots=1, **measure(data))
            first[h] = r
            taken.add((fam, h))
            rows.append(r)
        report["packs"][name]["kept"] = sum(1 for r in rows if r["source"] == name)
    for i, r in enumerate(rows):
        r["id"] = f"tt1_{i:06d}"
    fields = ["id", "source", "family", "person", "person_kind", "orig_file", "pack_index", "origin_id", "origin_set",
              "raw_path", "sha256", "bytes", "n_slots", "width", "height", "format", "pil_mode", "lap_var",
              "chroma_mean", "greyscale"]
    mf = OUT / ("raw_manifest_test.csv" if a.limit else "raw_manifest.csv")
    with open(mf, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})
    report["kept_per_source"] = dict(collections.Counter(r["source"] for r in rows))
    report["persons_per_source"] = {s: len({r["person"] for r in rows if r["source"] == s}) for s in report["kept_per_source"]}
    report["manifest"] = str(mf)
    report["manifest_sha256"] = hashlib.sha256(mf.read_bytes()).hexdigest()
    rp = (OUT if a.limit else RES) / ("extract_report_test.json" if a.limit else "extract_report.json")
    rp.write_text(json.dumps(report, indent=1))
    if not a.limit:
        shutil.copyfile(mf, RES / "raw_manifest.csv")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
