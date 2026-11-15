"""Standing adversary (ADV): the registered contrasts (experiments/ADV_shortcut-floors/prereg.md section 4) as row
selections on the arms' own evaluation manifests, plus person keys for the person split.

Manifests (read only; every one is a development manifest already in the arms' packs):
  AB1X  /mnt/t7/smad_next/AB1/x/manifests/ab1x_eval.csv   (AB1's 21,277 rows + 3,582 border rows; SbFM, Sbx, GX1,
        RZ1 read on it; BB2/E3's pn1_eval rows are the same images for landmark_combined and the splice rows)
  GD    /mnt/t7/smad_next/PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv   (PR1 GD0/GD1/GD2 development families)
  TRAIN training manifests train_Sb / train_A (PN1 manifests2), train_Sbx, train_SbFM (AB1)
Person keys: the manifest host (split on '_' for FFHQ morph pairs, on '|' for MS1 pairs); a two-person row also gets
its partner (ladder_split partner_B for ladder-host rows with label 1 or a two-person rung; AF0 manifest pid_A /
pid_B for AF0 morphs and their halves). Linking more persons than strictly needed only merges groups (conservative).
Guard: no path or id containing fst, valx, a12sp, frll, mad22, mordiff, dim_, feret_h1, casia is accepted.
"""
import csv
import os
import pathlib

T7 = pathlib.Path("/mnt/t7/smad_next")
AB1X = T7 / "AB1/x/manifests/ab1x_eval.csv"
GD = T7 / "PR1/pr1_gd_tree/pr1g/data/manifests/pr1_gd.csv"
TRAIN = {"Sb": T7 / "PN1/manifests2/train_Sb.csv", "A": T7 / "PN1/manifests2/train_A.csv",
         "Sbx": T7 / "AB1/x/manifests/train_Sbx.csv", "SbFM": T7 / "AB1/fm/manifests/train_SbFM.csv",
         # amendment 3 (lead's request): the other arms' training lists for the same-data shortcut learner
         "B": T7 / "PN1/manifests2/train_B.csv", "SbZ": T7 / "AB1/manifests/train_SbZ.csv",
         "SbS": T7 / "AB1/manifests/train_SbS.csv", "Sp": T7 / "AB1/manifests/train_Sp.csv",
         "AS": T7 / "AB1/manifests/train_AS.csv", "SbH": T7 / "AB1/manifests/train_SbH.csv",
         "SbR": T7 / "AB1/b2/manifests/train_SbR.csv", "SbnS0": T7 / "AB1/b2/manifests/train_SbnS0.csv",
         "SbH61": T7 / "AB1/b2/manifests/train_SbH61.csv", "SbnS3": T7 / "AB1/b2/manifests/train_SbnS3.csv",
         "SbSp": T7 / "AB1/b2/manifests/train_SbSp.csv",
         # amendment 6: AB1 amendment 7 batch C (06a2351), hashes checked against AB1 pins.sha256 at compute time
         "SpV": T7 / "AB1/c/manifests/train_SpV.csv", "BN": T7 / "AB1/c/manifests/train_BN.csv",
         "BV": T7 / "AB1/c/manifests/train_BV.csv"}          # amendment 6 addendum (AB1 amendment 7b, 35c8a9f)
TRAIN_SHA = {"SpV": "f6521d96de7d93ff62232c4eb8236d2560cf39f2e8ca6a56d676f3c0c39af759",
             "BN": "c1b4497bb59343b7f5dd48149e300fb136533790724dfdf83aa395a703fe6af1",
             "BV": "ee4e227b2cd6648d196b5d61300a9cf483c85f05a80afae0fd6e774153baf04f"}
XF1 = T7 / "XF1/xf1_rows.csv"                                  # amendment 7
XF1_SHA = "ef4adf5ba22847f04ccf40d054fcda5b05b1546be08dde04b277dd2b5266e317"
ROOTS = [T7 / "XF1/pack_tree/xf1/data", T7 / "PN1/fs_tree/pn1/data", T7 / "AB1/overlay_tree/pn1/data", T7 / "AB1/x/img/pn1/data",
         T7 / "AB1/x/img/pn1", T7 / "AB1/fm/img/pn1/data", T7 / "AB1/fm/img/pn1", T7 / "PR1/pr1_gd_tree/pr1g/data"]
SPLIT = pathlib.Path("/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/split/ladder_split.csv")
AF0MAN = T7 / "AF0/manifest.csv"
AG1MAN = T7 / "AG1/data/manifests/ag1.csv"
FORBID = ("fst", "valx", "a12sp", "a12-sp", "frll", "mad22", "mordiff", "/dim", "h1_", "casia_web", "fei")


def _ok(s):
    s = s.lower()
    return not any(f in s for f in FORBID)


def resolve(rel):
    for r in ROOTS:
        p = r / rel
        if p.exists():
            return str(p)
    raise FileNotFoundError(rel)


_P = {}


def partner():
    if not _P:
        _P["lad"] = {r["pid"]: r["partner_B"] for r in csv.DictReader(open(SPLIT))}
        _P["af0"] = {r["id"]: (r["pid_A"], r["pid_B"]) for r in csv.DictReader(open(AF0MAN)) if r["kind"] == "morph"}
        _P["ag1"] = {pathlib.Path(r["path"]).name: tuple(x.replace("_", ":", 1) for x in (r["pa"], r["pb"]))
                     for r in csv.DictReader(open(AG1MAN))}
    return _P


TWO = ("R4", "S4", "R2w4", "R2w4_bg", "R2w4_face", "R4_face", "R4_bg", "S4_face", "S4_bg", "X", "u50", "zero", "halfA", "halfB")


def persons(r):
    h = r.get("host", "")
    fam = r.get("fam", "")
    if fam in ("ffhq_lcomb", "ffhq", "gd0") or (fam == "border" and r.get("role") == "hn2"):
        ps = ["ffhq:" + x for x in h.split("_") if x]
    elif "|" in h:
        ps = h.split("|")
    else:
        ps = [h] if h else [r["id"]]
    P = partner()
    if fam == "xf1":                               # amendment 7: host, plus the partner for the two-person morph
        ps = [h] + ([r["partner"]] if r.get("rung") == "FMHB" and r.get("partner") else [])
        return tuple(sorted(set(ps)))
    if fam == "gd2":                               # pre-run check F2: true contributors from the AG1 manifest
        return tuple(sorted(set(P["ag1"][pathlib.Path(r["src"]).name])))
    if fam == "af0" or r["id"].startswith(("train_", "val_")):
        mid = r["id"].split("_half")[0].split("_fm61")[0].split("_amsl112")[0].split("_s61")[0]
        if mid in P["af0"]:
            ps += list(P["af0"][mid])
    if h in P["lad"] and (r.get("label") == "1" or r.get("rung") in TWO):
        ps.append(P["lad"][h])
    return tuple(sorted(set(ps)))


def rows(manifest):
    R = list(csv.DictReader(open(manifest)))
    for r in R:
        assert _ok(r["path"]) and _ok(r["id"]), r["id"]
    return R


def train_rows(arm):
    """Unique training images of an arm's manifest (first occurrence), with person keys from the id."""
    R = rows(TRAIN[arm])
    seen, out = set(), []
    for r in R:
        if r["path"] in seen:
            continue
        seen.add(r["path"])
        r = dict(r)
        r["host"] = ""
        out.append(r)
    return out


def train_persons(r):
    """Person keys of a training row: AF0 ids through the AF0 manifest; ladder ids through the AR1 list."""
    P = partner()
    i = r["id"]
    mid = i.split("_half")[0].split("_fm61")[0].split("_amsl112")[0].split("_s61")[0]
    if mid in P["af0"]:
        return tuple(sorted(set(P["af0"][mid])))
    lad = _ar1()
    if i.startswith("sm1h_"):                      # ladder native halves sm1h_<db>_<num>_h[AB]: host and partner
        _, db, num = i.split("_")[:3]
        h = f"{db}:{num}"
        return tuple(sorted({h, P["lad"].get(h, h)}))
    base = i.split("__")[0]
    if base != i:
        return train_persons(dict(r, id=base))
    for k in (i, base, i.rsplit("_", 1)[0]):
        if k in lad:
            h = lad[k]
            ps = [h]
            if r.get("label") == "1" or r.get("kind", "") in ("lad_R4", "lad_S4", "lad_R4fm"):
                ps.append(P["lad"].get(h, h))
            return tuple(sorted(set(ps)))
    return (i,)


_A = {}


def _ar1():
    if not _A:
        for n in ("AF0/lists/ar1.csv", "PN1/lists/r2w4.csv"):
            p = T7 / n
            if p.exists():
                for r in csv.DictReader(open(p)):
                    _A[r["id"]] = r["p1"]
        for n in ("af0_w1", "af0_w2", "af0_h"):
            p = T7 / "AF0" / "lists" / f"{n}.csv"
            if p.exists():
                for r in csv.DictReader(open(p)):
                    _A.setdefault(r["id"], r["p1"])
        sp = T7 / "PN1/lists"
        for f in sorted(sp.glob("splice*.csv")):
            for r in csv.DictReader(open(f)):
                if "p1" in r:
                    _A[r["id"]] = r["p1"]
    return _A


def sel(R, **kw):
    out = []
    for r in R:
        ok = True
        for k, v in kw.items():
            if k == "id_suffix":
                ok = ok and r["id"].endswith(v)
            elif k == "bd1_hosts":
                ok = ok and r.get("host") in v
            elif k == "id_plain":
                ok = ok and not r["id"].endswith(("_fm61", "_amsl112"))
            elif isinstance(v, (tuple, list)):
                ok = ok and r.get(k) in v
            else:
                ok = ok and r.get(k) == v
        if ok:
            out.append(r)
    return out


_B = {}


def bd1_hosts():
    """The 291 BD1 hosts (development + test splice hosts of the AB1 evaluation rows)."""
    if "bd1" not in _B:
        _B["bd1"] = frozenset(r["host"] for r in csv.DictReader(open(AB1X))
                              if r["fam"] == "splice" and r["role"] in ("dev", "test"))
    return _B["bd1"]


def contrast_defs():
    """name -> (manifest key, positive selector, negative selector, note). Selectors are dicts for sel()."""
    L = dict(fam="ladder", strength="")              # native rows; stored copies carry strength 61 / 112
    S = dict(fam="splice")
    D = {
        # ---- shared: FFHQ landmark_combined (SbFM H-fm1, Sbx guard, GX1 guard, RZ1 detection, BB2/E3 contrast 1, SA1 row 18)
        "lcomb": ("AB1X", dict(fam="ffhq_lcomb", rung="landmark_combined_orig"),
                  dict(fam="ffhq_lcomb", rung="landmark_combined_resmatch"), "1,000 morphs vs 2,000 resmatch genuine"),
        # ---- SbFM (AB1 second engine)
        "test_fm_R4_vs_R2w": ("AB1X", dict(L, role="test", rung="R4", tool="facemorpher"),
                              dict(L, role="test", rung="R2w", tool="facemorpher"), "H-fm2"),
        "test_cv_R4_vs_R2w": ("AB1X", dict(L, role="test", rung="R4", tool="opencv"),
                              dict(L, role="test", rung="R2w", tool="opencv"), "H-fm3"),
        "test_fm_R4_vs_R3": ("AB1X", dict(L, role="test", rung="R4", tool="facemorpher"),
                             dict(L, role="test", rung="R3", tool="facemorpher"), "SbFM printed"),
        "test_cv_R4_vs_R3": ("AB1X", dict(L, role="test", rung="R4", tool="opencv"),
                             dict(L, role="test", rung="R3", tool="opencv"), "SbFM printed"),
        "dev_fm_R4_vs_R2w": ("AB1X", dict(L, role="dev", rung="R4", tool="facemorpher"),
                             dict(L, role="dev", rung="R2w", tool="facemorpher"), "SbFM printed"),
        "dev_cv_R4_vs_R2w": ("AB1X", dict(L, role="dev", rung="R4", tool="opencv"),
                             dict(L, role="dev", rung="R2w", tool="opencv"), "SbFM printed; SA1 row 6"),
        "dev_fm_R4_vs_R3": ("AB1X", dict(L, role="dev", rung="R4", tool="facemorpher"),
                            dict(L, role="dev", rung="R3", tool="facemorpher"), "SbFM printed"),
        "dev_cv_R4_vs_R3": ("AB1X", dict(L, role="dev", rung="R4", tool="opencv"),
                            dict(L, role="dev", rung="R3", tool="opencv"), "SbFM printed; SA1 row 7"),
        "dev_cv_R4_vs_R2w4": ("AB1X", dict(L, role="dev", rung="R4", tool="opencv"),
                              dict(L, role="dev", rung="R2w4", tool="opencv"), "SA1 row 6 (two-person geometry)"),
        "dev_cv_R4_vs_R3m": ("AB1X", dict(L, role="dev", rung="R4", tool="opencv"),
                             dict(L, role="dev", rung="R3m", tool="opencv"), "SA1 row 7 (mirror same-person)"),
        # ---- Sbx (border): separability of the bordered photos from photos (no network can do worse than chance)
        "border_vs_cam": ("AB1X", dict(fam="border", rung="R_cam_border"),
                          dict(border_originals=True), "H-x1 context; SA1 row 5 (226 unbordered originals)"),
        "border_ffhq_vs_ffhq": ("AB1X", dict(fam="border", rung="R_ffhq_border"),
                                dict(fam="ffhq", rung="ffhq_bona_orig"), "Sbx printed; SA1 row 5"),
        # ---- BB2/E3 contrast 3 and splice rows (SA1 rows 8, 9, 12)
        "test_S4bg_vs_S0bg": ("AB1X", dict(S, role="test", rung="S4_bg"), dict(S, role="test", rung="S0_bg"),
                              "E3 contrast 3 (face only)"),
        "dev_S4_vs_S3": ("AB1X", dict(S, role="dev", rung="S4"), dict(S, role="dev", rung="S3"), "SA1 row 8"),
        "dev_S4_vs_S0": ("AB1X", dict(S, role="dev", rung="S4"), dict(S, role="dev", rung="S0"), "SA1 row 9"),
        "test_S4_vs_S3": ("AB1X", dict(S, role="test", rung="S4"), dict(S, role="test", rung="S3"), "SA1 row 8 (test)"),
        "dev_S4bg_vs_S0bg": ("AB1X", dict(S, role="dev", rung="S4_bg"), dict(S, role="dev", rung="S0_bg"),
                             "SA1 row 12 (face only)"),
        "dev_R4face_vs_R2wface": ("AB1X", dict(S, role="dev", rung="R4_face"), dict(S, role="dev", rung="R2w_face"),
                                  "SA1 row 12 (surround only: face blanked)"),
        # ---- storage (SA1 rows 1, 2; RZ1 wave 1, C2P rows)
        "store_photo_fm61_vs_native": ("AB1X", dict(fam="ms1ffhq", rung="photo", id_suffix="_fm61"),
                                       dict(fam="ms1ffhq", rung="photo", id_plain=True), "SA1 row 1"),
        "store_photo_amsl112_vs_native": ("AB1X", dict(fam="ms1ffhq", rung="photo", id_suffix="_amsl112"),
                                          dict(fam="ms1ffhq", rung="photo", id_plain=True), "SA1 row 1"),
        "store_morph_vs_photo_fm61": ("AB1X", dict(fam="ms1ffhq", rung="u50", id_suffix="_fm61"),
                                      dict(fam="ms1ffhq", rung="photo", id_suffix="_fm61"), "SA1 row 2"),
        "store_morph_vs_photo_amsl112": ("AB1X", dict(fam="ms1ffhq", rung="u50", id_suffix="_amsl112"),
                                         dict(fam="ms1ffhq", rung="photo", id_suffix="_amsl112"), "SA1 row 2"),
        "ms1_morph_vs_photo_native": ("AB1X", dict(fam="ms1ffhq", rung="u50", id_plain=True),
                                      dict(fam="ms1ffhq", rung="photo", id_plain=True), "SA1 row 2 (native)"),
        "af0_dev_u50_vs_photo": ("AB1X", dict(fam="af0", role="dev", rung="u50"), dict(fam="af0", role="dev", rung="photo"),
                                 "AF0 development"),
        "hn2_lcomplete_vs_bona": ("AB1X", dict(fam="ffhq", rung="landmark_complete_orig"),
                                  dict(fam="ffhq", rung="landmark_complete_resmatch"), "FFHQ landmark_complete"),
        # ---- GAN / diffusion development families (SA1 rows 13, 14; GX1 transfer reads)
        "gd1_X_vs_REC": ("GD", dict(fam="gd1", rung="X"), dict(fam="gd1", rung="REC"), "SA1 row 13"),
        "gd1_X_vs_SAME": ("GD", dict(fam="gd1", rung="X"), dict(fam="gd1", rung="SAME"), "SA1 row 13"),
        "gd2_R4_vs_R2": ("GD", dict(fam="gd2", rung="R4"), dict(fam="gd2", rung="R2"), "SA1 row 14 (R2 on s1 and s2)"),
        "gd2_R4_vs_R2s1": ("GD", dict(fam="gd2", rung="R4"), dict(fam="gd2", rung="R2", id_suffix="__s1"),
                           "GX1 secondary analogue (R2 on s1)"),
        "gd2_R4_vs_R3": ("GD", dict(fam="gd2", rung="R4"), dict(fam="gd2", rung="R3"), "SA1 row 14; GX1 primary analogue"),
        "gd0_sgw_vs_resmatch": ("GD", dict(fam="gd0", rung="stylegan_w_orig"), dict(fam="gd0", rung="stylegan_w_resmatch"),
                                "GX1 transfer read"),
        "gd0_sgwp_vs_resmatch": ("GD", dict(fam="gd0", rung="stylegan_wplus_orig"),
                                 dict(fam="gd0", rung="stylegan_wplus_resmatch"), "GX1 transfer read"),
        "gd0_diffae_vs_resmatch": ("GD", dict(fam="gd0", rung="diffae_orig"), dict(fam="gd0", rung="diffae_resmatch"),
                                   "SA1 row 13 context"),
        # ---- amendment 7: XF1 matched FaceMorpher render on FFHQ hold-out hosts
        "xf1_FMHB_vs_FMHH": ("XF1", dict(fam="xf1", rung="FMHB"), dict(fam="xf1", rung="FMHH"),
                             "XF1: two-person FaceMorpher morph vs one-photo FaceMorpher render"),
        "xf1_FMHH_vs_H": ("XF1", dict(fam="xf1", rung="FMHH"), dict(fam="xf1", rung="H"),
                          "XF1: one-photo FaceMorpher render vs the plain photo"),
        # ---- amendment 3: history-balanced landmark_combined (row list built by balance.py, committed)
        "lcomb_bal": ("AB1X", dict(rowfile="/home/narolski/smad-next/experiments/ADV_shortcut-floors/floors/lcomb_bal_rows.csv"),
                      dict(), "lcomb matched on the surround score and pre_ied (amendment 3)"),
        # ---- amendment 1: regional identity (RI1) and texture band profile (TB1), the 291 BD1 hosts (test + dev)
        "ri_R4_vs_R3": ("AB1X", dict(L, role=("test", "dev"), rung="R4", tool="opencv", bd1_hosts=bd1_hosts()),
                        dict(L, role=("test", "dev"), rung="R3", tool="opencv", bd1_hosts=bd1_hosts()), "RI1 S1 signal"),
        "ri_R4_vs_R0": ("AB1X", dict(L, role=("test", "dev"), rung="R4", tool="opencv", bd1_hosts=bd1_hosts()),
                        dict(L, role=("test", "dev"), rung="R0", bd1_hosts=bd1_hosts()), "RI1 S1 signal"),
        "ri_R0s61_vs_R0": ("AB1X", dict(fam="ladder", role=("test", "dev"), rung="R0", strength="61", bd1_hosts=bd1_hosts()),
                           dict(L, role=("test", "dev"), rung="R0", bd1_hosts=bd1_hosts()), "RI1/TB1 storage control (ceiling)"),
        "ri_S0_vs_R0": ("AB1X", dict(S, role=("test", "dev"), rung="S0"),
                        dict(L, role=("test", "dev"), rung="R0", bd1_hosts=bd1_hosts()), "RI1/TB1 seam control"),
        "ri_R2w4_vs_R0": ("AB1X", dict(L, role=("test", "dev"), rung="R2w4", tool="opencv", bd1_hosts=bd1_hosts()),
                          dict(L, role=("test", "dev"), rung="R0", bd1_hosts=bd1_hosts()), "RI1/TB1 warp control"),
        "ri_S4_vs_S3": ("AB1X", dict(S, role=("test", "dev"), rung="S4"), dict(S, role=("test", "dev"), rung="S3"),
                        "RI1 S1 and TB1 S (within BD1 D quintiles printed)"),
    }
    return D


TRAIN_CONTRASTS = {
    # BB2/E3 splice-fit gate and E2 linear probe, on train_Sb's unique rows
    "train_lad_S4_vs_S3": ("lad_S4", "lad_S3"),
    "train_lad_S4_vs_S0": ("lad_S4", "lad_S0"),
}


def manifest(key):
    if key == "XF1":
        import hashlib
        assert hashlib.sha256(open(XF1, "rb").read()).hexdigest() == XF1_SHA, "xf1_rows.csv changed"
    return {"AB1X": AB1X, "GD": GD, "XF1": XF1}[key]


def build(name):
    """-> list of (id, abs path, label, persons) for a registered contrast."""
    D = contrast_defs()
    key, pos, neg, _ = D[name]
    R = rows(manifest(key))
    if pos.get("rowfile"):                         # amendment 3: a committed row list (lcomb_bal)
        want = {r["id"]: int(r["label"]) for r in csv.DictReader(open(pos["rowfile"]))}
        X = [r for r in R if r["id"] in want]
        assert len(X) == len(want), name
        return [(r["id"], resolve(r["path"]), want[r["id"]], persons(r)) for r in X if want[r["id"]] == 1] + \
               [(r["id"], resolve(r["path"]), want[r["id"]], persons(r)) for r in X if want[r["id"]] == 0]
    P = sel(R, **pos)
    if neg.get("border_originals"):
        want = {r["id"][5:].split("__")[0] for r in P}
        N = [r for r in R if r["id"] in want]
    else:
        N = sel(R, **neg)
    assert P and N, name
    return [(r["id"], resolve(r["path"]), 1, persons(r)) for r in P] + \
           [(r["id"], resolve(r["path"]), 0, persons(r)) for r in N]


def build_train(name, arm="Sb"):
    a, b = TRAIN_CONTRASTS[name]
    R = train_rows(arm)
    out = []
    for r in R:
        if r["kind"] in (a, b):
            out.append((r["id"], resolve(r["path"]), 1 if r["kind"] == a else 0, train_persons(r)))
    return out


if __name__ == "__main__":
    import collections
    for n in contrast_defs():
        if n == "lcomb_bal" and not os.path.exists(contrast_defs()[n][1]["rowfile"]):
            continue
        x = build(n)
        c = collections.Counter(l for _, _, l, _ in x)
        print(n, c[1], c[0], os.path.basename(x[0][1]))
    for n in TRAIN_CONTRASTS:
        x = build_train(n)
        c = collections.Counter(l for _, _, l, _ in x)
        print(n, c[1], c[0], sum(len(p) == 1 and p[0].startswith(("lad", "ar1")) for *_, p in x))
