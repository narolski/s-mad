"""PRIVATE (release reproduction, 2026-11-18): write the release pool.csv (id,path,kind,label,db,hist) from the internal
manifests, in the order check_build_lists.py uses (PN1 src_B.csv rows, then Sb's splice rows in manifest order).
  python3 -I make_pool.py <release-repo> <out pool.csv>"""
import csv, sys, importlib.util
spec = importlib.util.spec_from_file_location("bl", sys.argv[1] + "/training/build_lists.py")
BL = importlib.util.module_from_spec(spec); spec.loader.exec_module(BL)
FS = "/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests"
KIND = {"af0_photo61": "photo_small", "af0_half61": "warped_half_small", "af0_u5061": "morph_small", "af0_photo": "photo",
        "lad_R0": "host_photo", "af0_u50": "morph", "lad_R4": "host_morph", "af0_zero": "warp_only", "af0_half": "warped_half",
        "lad_R2w": "host_warp_only", "lad_half": "host_warped_half", "lad_S4": "splice_two_person", "lad_S0": "seam_only",
        "lad_S3": "splice_same_person"}
HIST = {"native": "native", "s61": "stored_small"}
srcB = list(csv.DictReader(open("/mnt/t7/smad_next/PN1/manifests/src_B.csv")))
sb = BL.unique(list(csv.DictReader(open(f"{FS}/train_Sb.csv"))))
pool = [dict(id=r["id"], path=f"train/{r['kind']}/{r['id']}.png", kind=KIND[r["kind"]], label=r["label"], db=r["db"], hist=HIST[r["hist"]]) for r in srcB]
pool += [dict(id=r["id"], path=r["path"], kind=KIND[r["kind"]], label=r["label"], db=r["db"], hist=HIST[r["hist"]]) for r in sb if r["kind"] in ("lad_S4", "lad_S0", "lad_S3")]
with open(sys.argv[2], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "path", "kind", "label", "db", "hist"]); w.writeheader(); w.writerows(pool)
print(len(pool), "pool rows ->", sys.argv[2])
