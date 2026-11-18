"""PRIVATE check: the release training/build_lists.py, run on a pool rebuilt from the internal manifests (src order:
PN1 src_B.csv rows, then Sb's splice rows in their manifest order), must give exactly the internal training lists
A, B, Sb (FS1 pack), Sp (manifests_sp) and SpV, BN, BV (AB1 batch C), row by row (path, label, id, kind, db, hist).
  python3 -I check_build_lists.py <release-repo>"""
import csv, sys, importlib.util
spec = importlib.util.spec_from_file_location("bl", sys.argv[1] + "/training/build_lists.py")
BL = importlib.util.module_from_spec(spec); spec.loader.exec_module(BL)
FS = "/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests"
INTERNAL = {"A": f"{FS}/train_A.csv", "B": f"{FS}/train_B.csv", "Sb": f"{FS}/train_Sb.csv",
            "Sp": "/mnt/t7/smad_next/PN1/manifests_sp/train_Sp.csv",
            **{k: f"/mnt/t7/smad_next/AB1/c/manifests/train_{k}.csv" for k in ("SpV", "BN", "BV")}}
KIND = {"af0_photo61": "photo_small", "af0_half61": "warped_half_small", "af0_u5061": "morph_small", "af0_photo": "photo",
        "lad_R0": "host_photo", "af0_u50": "morph", "lad_R4": "host_morph", "af0_zero": "warp_only", "af0_half": "warped_half",
        "lad_R2w": "host_warp_only", "lad_half": "host_warped_half", "lad_S4": "splice_two_person", "lad_S0": "seam_only",
        "lad_S3": "splice_same_person"}                    # internal kind name -> release kind name
HIST = {"native": "native", "s61": "stored_small"}
srcB = list(csv.DictReader(open("/mnt/t7/smad_next/PN1/manifests/src_B.csv")))
sb = BL.unique(list(csv.DictReader(open(INTERNAL["Sb"]))))
pool = [dict(id=r["id"], path=f"train/{r['kind']}/{r['id']}.png", kind=KIND[r["kind"]], label=r["label"], db=r["db"], hist=HIST[r["hist"]]) for r in srcB]
pool += [dict(id=r["id"], path=r["path"], kind=KIND[r["kind"]], label=r["label"], db=r["db"], hist=HIST[r["hist"]]) for r in sb if r["kind"] in ("lad_S4", "lad_S0", "lad_S3")]
ok = True
for name, rows in BL.arms(pool).items():
    ref = list(csv.DictReader(open(INTERNAL[name])))
    a = [tuple(r[c] for c in BL.COLS) for r in rows]
    b = [tuple(dict(r, kind=KIND[r["kind"]], hist=HIST[r["hist"]])[c] for c in BL.COLS) for r in ref]
    same = a == b
    ok &= same
    print(f"{name:4s} rows {len(a)} internal {len(b)} identical {same}")
sys.exit(0 if ok else 1)
