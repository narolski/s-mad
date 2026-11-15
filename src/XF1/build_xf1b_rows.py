"""XF1 revision (b): row list for FM(H,B) (DATA D12a, R4) against the matched FaceMorpher warp-only image W (DATA D12b,
R2w4: H warped toward the H-and-B mean shape, no blending), whole-frame form; H kept only for the own-rule flag prints
(klass H, never in a contrast). Every image sha256-checked against the DATA manifests. Per host: pairing component
(permutation cycle), cycle block (runs of 5 along each cycle, F3), exactly-one-black share and |IED gap| with
terciles (D12b pair_measures.csv, F2), glintr100 cosine H-B from the existing MS1 embeddings (F4). Host ids stay on
/mnt/t7. No file is deleted: an existing output is renamed to .bak-<stamp> (F7).
  python3 -I build_xf1b_rows.py   -> /mnt/t7/smad_next/XF1/xf1b_rows.csv"""
import csv, hashlib, json, pathlib, time
import numpy as np

DATA = pathlib.Path("/mnt/t7/smad_next/DATA")
OUT = pathlib.Path("/mnt/t7/smad_next/XF1")
PINS = {"D12a/manifest.csv": "9df020e1c5fa7a3bcc21d038c154405707780a05a90df579baad0f59eb7f7f4c",
        "D12b/manifest.csv": "152a492b1d938b9a0c3852cc5531e6529d230e02f93c996592263c9ed4491455",
        "D12b/pair_measures.csv": "29d4655a9bc347408a113ed46070247e683a20df671a4f633efeb22568d7dcc5"}
EMB = pathlib.Path("/mnt/t7/smad_next/MS1/ffhq/emb_kept.npz")
BL = 5
HEAD = ["id", "path", "label", "klass", "form", "host", "partner", "component", "block", "excl_border", "excl_border_t",
        "ied_gap", "ied_gap_t", "cos_HB", "sha256", "src"]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def terc(vals):
    q = np.quantile(list(vals.values()), [1 / 3, 2 / 3])
    return {k: int(np.searchsorted(q, v, side="right")) for k, v in vals.items()}


def main():
    for rel, want in PINS.items():
        assert sha(DATA / rel) == want, rel
    a = {r["host"]: r for r in csv.DictReader(open(DATA / "D12a/manifest.csv"))}
    b = {r["host"]: r for r in csv.DictReader(open(DATA / "D12b/manifest.csv"))}
    pm = {"ffhq:" + r["host"]: r for r in csv.DictReader(open(DATA / "D12b/pair_measures.csv"))}
    assert set(a) == set(b) == set(pm) and len(a) == 299
    hosts = sorted(a)
    nxt = {h: a[h]["partner"] for h in hosts}
    for h in hosts:
        assert b[h]["partner"] == nxt[h] and b[h]["d12a_morph"] == a[h]["out"] and b[h]["d12a_morph_sha256"] == a[h]["out_sha256"]
        assert b[h]["rung"] == "R2w4" and b[h]["engine"] == "facemorpher" and b[h]["frame_host_sha256"] == a[h]["frame_host_sha256"]
    comp, block, seen, k, nb = {}, {}, set(), 0, 0
    for h0 in hosts:                     # cycles in sorted-host order; blocks of 5 consecutive hosts along each cycle
        if h0 in seen:
            continue
        cyc, x = [], h0
        while x not in seen:
            cyc.append(x); seen.add(x); x = nxt[x]
        for i, h in enumerate(cyc):
            comp[h] = k; block[h] = nb + i // BL
        nb += (len(cyc) + BL - 1) // BL; k += 1
    z = np.load(EMB); E = {key: v / np.linalg.norm(v) for key, v in zip(z["key"].tolist(), z["emb"])}
    cos = {h: float(E[h.split(":")[1]] @ E[nxt[h].split(":")[1]]) for h in hosts}
    eb = {h: float(pm[h]["exactly_one_black_share"]) for h in hosts}
    ig = {h: float(pm[h]["abs_ied_gap"]) for h in hosts}
    ebt, igt = terc(eb), terc(ig)
    rows = []
    for h in hosts:
        key = h.split(":")[1]
        for klass, src, hh, label in (("FMHB", a[h]["out"], a[h]["out_sha256"], 1), ("WARP", b[h]["out"], b[h]["out_sha256"], 0),
                                      ("H", a[h]["frame_host"], a[h]["frame_host_sha256"], 0)):
            assert sha(src) == hh, src
            rows.append(dict(id=f"xf1b_{klass}_whole_{key}", path=f"eval/xf1b/{klass}/whole/{key}.png", label=label, klass=klass,
                             form="whole", host=h, partner=nxt[h], component=comp[h], block=block[h], excl_border=eb[h],
                             excl_border_t=ebt[h], ied_gap=ig[h], ied_gap_t=igt[h], cos_HB=cos[h], sha256=hh, src=src))
    p = OUT / "xf1b_rows.csv"
    if p.exists():
        p.rename(p.with_name(p.name + f".bak-{time.strftime('%Y%m%d%H%M%S')}"))
    with open(p, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEAD); w.writeheader(); w.writerows(rows)
    c = np.array(list(cos.values()))
    print(json.dumps(dict(rows=len(rows), components=k, blocks=nb, cos_HB=dict(min=float(c.min()), median=float(np.median(c)), max=float(c.max())),
                          sha256=sha(p))))


if __name__ == "__main__":
    main()
