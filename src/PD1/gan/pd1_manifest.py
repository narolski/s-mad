"""Signal isolation by paired differences (PD1), GAN family: item manifest, host table, byte copies.

Builds /mnt/t7/smad_next/PD1/gan/{items.csv,hosts.csv,latents.npz,templates.npz,manifest_log.json}.
Byte copies only (sha256 verified): GAN32 camera photos out of /tmp/opencode (volatile) into anchors/, H3 raw PNGs
and latents out of the H3 generation tars into h3raw/. No image is decoded or re-encoded here.

Run: /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/PD1/gan/pd1_manifest.py [--limit8]
"""
import csv, hashlib, io, json, pathlib, shutil, sys, tarfile
import numpy as np

BIG = pathlib.Path("/mnt/t7/smad_next/PD1/gan")
RS = pathlib.Path("/mnt/t7/smad_research")
G_RESULTS = {"gan32-vast-v1": [RS / "vast-gan32-v1-results/out"],
             "gan32-trainplus-v1": [RS / f"vast-gan32-trainplus-{s}-results/out" for s in ("shard0", "shard1-v2", "shard2", "shard3")]}
H3 = pathlib.Path("/mnt/t7/smad_heldout/h3_sg3")
A37 = pathlib.Path("/mnt/t7/smad_heldout/a37_sg3ctl")
MC = pathlib.Path("/home/narolski/mambamorph-code")
EVAL_ROOT = MC / "smadcvpr_data"
A47 = pathlib.Path("/mnt/t7/smad_heldout/a47/data47/i3")
MAD = pathlib.Path("/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z")
ROLE_G = {"RA0": ("x1", "a0"), "RA1": ("x1", "a1"), "RB0": ("x1", "b0"), "RB1": ("x1", "b1"),
          "SA": ("x2", None), "SB": ("x2", None), "P0": ("x3", None), "P1": ("x3", None)}
HOST_ROLES = {"a0": ("RA0", "SA", "P0"), "a1": ("RA1", "SA", "P1"), "b0": ("RB0", "SB", "P0"), "b1": ("RB1", "SB", "P1")}


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def shab(b):
    return hashlib.sha256(b).hexdigest()


def main():
    limit = "--limit8" in sys.argv
    out = BIG / ("smoke8" if limit else "")
    out.mkdir(parents=True, exist_ok=True)
    items, hosts, log = [], [], {}
    lat, tmpl = {}, {}

    def add(iid, set_, role, cluster, frame, path, **kw):
        items.append(dict(id=iid, set=set_, role=role, cluster=cluster, frame=frame, path=str(path), **kw))

    # ---------------- set G (GAN32) ----------------
    (BIG / "anchors").mkdir(exist_ok=True)
    nG = 0
    for payload, outs in G_RESULTS.items():
        src = json.load(open(RS / payload / "payload/inputs/SOURCES.json"))
        plan = json.load(open(RS / payload / "payload/inputs/PLAN.json"))
        with np.load(RS / payload / "payload/inputs/data.npz", allow_pickle=False) as z:
            for n, t in zip(z["folder"].tolist(), z["tmpl"]):
                tmpl[n] = t.astype(np.float32)
        srcby = {r["name"]: r for r in src}
        rows = []
        for o in outs:
            rows += json.load(open(o / "OUTPUTS.json"))
        byname = {}
        for r in rows:
            rawname = pathlib.Path(r["raw_path"]).name
            hit = [o / "raw1024" / rawname for o in outs if (o / "raw1024" / rawname).exists()]
            assert len(hit) == 1, (rawname, hit)
            byname[(r["block"], r["role"])] = (r, hit[0])
        blocks = plan[:2] if limit else plan
        for b in blocks:
            bid = b["id"]
            for role in ROLE_G:
                r, p = byname[(bid, role)]
                if sha(p) != r["raw_sha256"]:
                    raise SystemExit(f"raw sha mismatch {p}")
                add(f"G|{bid}|{role}", "G", ROLE_G[role][0], bid, "stylegan_raw1024", p, db=b["db"], partition=b["partition"],
                    payload=payload, src=";".join(r["source_names"]))
            for slot, name in b["slots"].items():
                s = srcby[name]
                dst = BIG / "anchors" / f"{name}.png"
                if not dst.exists():
                    if sha(s["source_path"]) != s["source_sha256"]:
                        raise SystemExit(f"anchor sha mismatch {name}")
                    shutil.copyfile(s["source_path"], dst)
                if sha(dst) != s["source_sha256"]:
                    raise SystemExit(f"anchor copy sha mismatch {dst}")
                add(f"G|{bid}|X0{slot}", "G", "x0", bid, "shared512_photo", dst, db=b["db"], partition=b["partition"],
                    payload=payload, src=name, subject=s["subject"], capture=s["capture"])
                lp = [o / "latents" / f"{name}.npz" for o in outs if (o / "latents" / f"{name}.npz").exists()]
                assert len(lp) == 1, (name, lp)
                with np.load(lp[0], allow_pickle=False) as z:
                    lat[f"G|{name}"] = z["w"].astype(np.float32)
                r1, r2, r3 = HOST_ROLES[slot]
                hosts.append(dict(host=f"G|{name}", set="G", cluster=bid, db=b["db"], slot=slot,
                                  x0=f"G|{bid}|X0{slot}", x1=f"G|{bid}|{r1}", x2=f"G|{bid}|{r2}", x3=f"G|{bid}|{r3}", x1s="",
                                  person=f"{bid}|{slot[0].upper()}",
                                  partner_tmpl=b["slots"]["b0" if slot[0] == "a" else "a0"],
                                  own_tmpl=name, same_tmpl=b["slots"][slot[0] + ("1" if slot[1] == "0" else "0")],
                                  partner_lat=b["slots"][("b" if slot[0] == "a" else "a") + slot[1]],
                                  same_lat=b["slots"][slot[0] + ("1" if slot[1] == "0" else "0")]))
            nG += 1
    log["G_blocks"] = nG

    # ---------------- set H (H3 + A37 spread), raw and aligned ----------------
    h3 = [r for r in csv.DictReader(open(H3 / "data/manifests/h3sg3.csv")) if r["variant"] == "orig"]
    a37 = [r for r in csv.DictReader(open(A37 / "data/manifests/a37spread.csv")) if r["variant"] == "orig"]
    morph = {r["pair"]: r for r in h3 if r["label"] == "1"}
    bona = {r["pair"]: r for r in h3 if r["label"] == "0"}
    spread = {r["pair"]: r for r in a37}
    pairs = sorted(morph, key=int)
    if limit:
        pairs = pairs[:2]
    assert set(pairs) <= set(bona) and set(pairs) <= set(spread)
    want = {}
    for p in pairs:
        want[pathlib.Path(morph[p]["path"]).stem] = ("morph", p)
        want[pathlib.Path(bona[p]["path"]).stem] = ("bona", p)
    (BIG / "h3raw/morph").mkdir(parents=True, exist_ok=True)
    (BIG / "h3raw/bona").mkdir(parents=True, exist_ok=True)
    got, hlat = {}, {}
    for tp in sorted((H3 / "work/gen_tars").glob("h3_out_t*.tar")):
        ref = open(str(tp) + ".sha256").read().split()[0]
        if sha(tp) != ref:
            raise SystemExit(f"tar sha mismatch {tp}")
        with tarfile.open(tp) as tf:
            for m in tf.getmembers():
                nm = pathlib.Path(m.name)
                if m.isfile() and nm.parent.name in ("morph", "bona") and nm.parent.parent.name == "raw" and nm.stem in want:
                    data = tf.extractfile(m).read()
                    dst = BIG / "h3raw" / nm.parent.name / nm.name
                    if not dst.exists():
                        dst.write_bytes(data)
                    assert sha(dst) == shab(data)
                    got[nm.stem] = (dst, shab(data), tp.name)
                elif m.isfile() and nm.parent.name == "latents" and nm.stem.endswith("_w") and nm.stem[:-2] in want:
                    with np.load(io.BytesIO(tf.extractfile(m).read()), allow_pickle=False) as z:
                        hlat[nm.stem[:-2]] = z["w"].astype(np.float32).reshape(16, 512)
    miss = sorted(set(want) - set(got))
    if miss:
        raise SystemExit(f"H3 raw missing {len(miss)}: {miss[:5]}")
    with np.load(A37 / "work/latents/a37spread.npz", allow_pickle=False) as z:
        slat = {str(n): w.astype(np.float32) for n, w in zip(z["name"], z["w"])}
    sp_log = {json.loads(l)["name"]: json.loads(l)["png_sha256"] for l in open(A37 / "work/gen/a37spread/gen_log.jsonl")}
    for p in pairs:
        m, b, s = morph[p], bona[p], spread[p]
        assert s["h3_twin"] == b["id"], (p, s["h3_twin"], b["id"])
        mst, bst, sst = pathlib.Path(m["path"]).stem, pathlib.Path(b["path"]).stem, pathlib.Path(s["path"]).stem
        sraw = A37 / "work/gen/a37spread/raw/bona" / f"{sst}.png"
        if sha(sraw) != sp_log[sst]:
            raise SystemExit(f"A37 raw sha mismatch {sraw}")
        cl = f"H{int(p):04d}"
        shown = b["contrib_a"]
        other = m["contrib_b"] if shown == m["contrib_a"] else m["contrib_a"]
        assert shown in (m["contrib_a"], m["contrib_b"])
        kw = dict(pair=p, shown=shown, other=other, pair_cos=m["pair_cos_a2f_template"])
        add(f"Hr|{p}|x3", "Hr", "x3", cl, "stylegan_raw1024", got[mst][0], **kw)
        add(f"Hr|{p}|x1", "Hr", "x1", cl, "stylegan_raw1024", got[bst][0], **kw)
        add(f"Hr|{p}|x1s", "Hr", "x1s", cl, "stylegan_raw1024", sraw, **kw)
        add(f"Ha|{p}|x3", "Ha", "x3", cl, "eval512_aligned", H3 / "data" / m["path"], fz1_id=m["id"], **kw)
        add(f"Ha|{p}|x1", "Ha", "x1", cl, "eval512_aligned", H3 / "data" / b["path"], fz1_id=b["id"], **kw)
        add(f"Ha|{p}|x1s", "Ha", "x1s", cl, "eval512_aligned", A37 / "data" / s["path"], fz1_id=s["id"], **kw)
        for fs in ("Hr", "Ha"):
            hosts.append(dict(host=f"{fs}|{p}", set=fs, cluster=cl, x1=f"{fs}|{p}|x1", x3=f"{fs}|{p}|x3", x1s=f"{fs}|{p}|x1s",
                              pair_cos=m["pair_cos_a2f_template"]))
        lat[f"H|{p}|x3"] = hlat[mst]
        lat[f"H|{p}|x1"] = hlat[bst]
        lat[f"H|{p}|x1s"] = slat[sst]
    log["H_pairs"] = len(pairs)

    # ---------------- set S (SMDD softening pairs) ----------------
    rows = list(csv.DictReader(open(A47 / "manifests/train.csv")))
    orig = sorted(r["path"] for r in rows if r["path"].startswith("train/smdd/os25k_bf_t/"))
    soft = {r["path"] for r in rows if r["path"].startswith("train/smdd_a47e7/os25k_bf_t/")}
    assert len(orig) == 25000 and len(soft) == 25000
    pick = np.random.default_rng(401).permutation(len(orig))[: (8 if limit else 2000)]
    for k, i in enumerate(pick):
        po = orig[i]
        ps = po.replace("train/smdd/", "train/smdd_a47e7/")
        assert ps in soft
        part = "S_fit" if k < len(pick) // 2 else "S_test"
        nm = pathlib.Path(po).stem
        add(f"S|{nm}|orig", "S", "s0", f"S{nm}", "smdd256", EVAL_ROOT / po, part=part)
        add(f"S|{nm}|e7", "S", "s1", f"S{nm}", "smdd256", A47 / ps, part=part)
        hosts.append(dict(host=f"S|{nm}", set="S", cluster=f"S{nm}", s0=f"S|{nm}|orig", s1=f"S|{nm}|e7", part=part))
    log["S_pairs"] = int(len(pick))

    # ---------------- set F and benchmark cells (scoring only) ----------------
    ev = list(csv.DictReader(open(EVAL_ROOT / "manifests/eval.csv")))
    bona_fr = {pathlib.Path(r["path"]).name.replace("_orig.png", ""): r for r in ev
               if r["set"] == "frllm" and r["family"] == "frll_bona" and r["variant"] == "orig"}
    names = sorted(bona_fr)[: (4 if limit else None)]
    ident = {}
    for n in names:
        add(f"Fe|{n}|native", "Fe", "native", n[:3], "eval_frllm", EVAL_ROOT / bona_fr[n]["path"], photo=n)
    for fam in ("amsl", "facemorpher", "opencv", "webmorph", "stylegan"):
        rm = {pathlib.Path(r["path"]).name.split("_resmatch")[0]: r for r in ev
              if r["set"] == "frllm" and r["family"] == fam and r["variant"] == "resmatch"}
        same = 0
        for n in names:
            p = EVAL_ROOT / rm[n]["path"]
            if sha(p) == sha(EVAL_ROOT / bona_fr[n]["path"]):
                same += 1
            elif fam != "stylegan":
                add(f"Fe|{n}|e7_{fam}", "Fe", f"e7_{fam}", n[:3], "eval_frllm", p, photo=n)
        ident[f"frllm_resmatch_{fam}"] = f"{same} of {len(names)} byte-identical to native"
    mb = sorted(p.name for p in (MAD / "native/BonaFide").glob("*.png"))[: (4 if limit else None)]
    for n in mb:
        add(f"Fm|{n[:-4]}|native", "Fm", "native", n[:3], "mad22_canonical512", MAD / "native/BonaFide" / n, photo=n[:-4])
    for fam in ("FaceMorpher", "OpenCV", "Webmorph", "MIPGAN_I", "MIPGAN_II"):
        same = 0
        for n in mb:
            p = MAD / "e7" / fam / n
            if sha(p) == sha(MAD / "native/BonaFide" / n):
                same += 1
            elif fam not in ("MIPGAN_I", "MIPGAN_II"):
                add(f"Fm|{n[:-4]}|e7_{fam}", "Fm", f"e7_{fam}", n[:3], "mad22_canonical512", p, photo=n[:-4])
        ident[f"mad22_e7_{fam}"] = f"{same} of {len(mb)} byte-identical to native"
    sg = [r for r in ev if r["set"] == "frllm" and r["family"] == "stylegan" and r["variant"] == "orig"][: (4 if limit else None)]
    for r in sg:
        stem = pathlib.Path(r["path"]).name.replace("_orig.png", "")
        a, b = stem.split("_")[:2]
        add(f"Be|{stem}|stylegan", "Be", "morph_stylegan", f"{a}|{b}", "eval_frllm", EVAL_ROOT / r["path"], pa=a, pb=b)
    for fam in ("MIPGAN_I", "MIPGAN_II"):
        fs = sorted((MAD / "native" / fam).glob("*.png"))[: (4 if limit else None)]
        for p in fs:
            a, b = p.stem.split("-vs-")
            add(f"Bm|{p.stem}|{fam}", "Bm", f"morph_{fam}", f"{a[:3]}|{b[:3]}", "mad22_canonical512", p, pa=a, pb=b)
    log["byte_identity"] = ident

    # ---------------- write ----------------
    keys = sorted({k for r in items for k in r})
    front = ["id", "set", "role", "cluster", "frame", "path"]
    keys = front + [k for k in keys if k not in front]
    with open(out / "items.csv", "w", newline="") as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(items)
    hk = sorted({k for r in hosts for k in r})
    with open(out / "hosts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, ["host", "set", "cluster"] + [k for k in hk if k not in ("host", "set", "cluster")])
        w.writeheader()
        w.writerows(hosts)
    np.savez(out / "latents.npz", key=np.array(list(lat)), w=np.stack(list(lat.values())))
    np.savez(out / "templates.npz", key=np.array(list(tmpl)), t=np.stack(list(tmpl.values())))
    ids = [r["id"] for r in items]
    assert len(ids) == len(set(ids))
    from collections import Counter
    log["items_by_set_role"] = {f"{k[0]}|{k[1]}": v for k, v in sorted(Counter((r["set"], r["role"]) for r in items).items())}
    log["n_items"] = len(items)
    log["n_hosts"] = len(hosts)
    json.dump(log, open(out / "manifest_log.json", "w"), indent=1)
    print(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()
