"""XF1 revision b, face-only form (lead's option (a), 13 Nov 2026): constant-colour blanking by the unchanged AR1 call
src/AR1/blank.py one() (file not edited; sha256 asserted), its output-root constant ar1_common.OUT set at run time to
/mnt/t7/smad_next/XF1, so the copies go to /mnt/t7/smad_next/XF1/blank/{bg,face}/<id>.png. Grey (128,128,128) outside
the convex hull of 0.5*tem(H) + 0.5*tem(B), the same hull for the FM(H,B) morph and its D12b warp-only image W (asserted:
the two copies' grey masks are identical outside the hull and the hull masks are equal). Only the face-only copies
('bg' variant) enter the row list; the face-blanked copies also written stay on disk, unused. Nothing of AR1's is
touched. Writes XF1/blank/xf1b_face_manifest.csv (input and output sha256 per row) and XF1/blank/SHA256SUMS, then
appends the face-only rows to xf1b_rows.csv (the previous file renamed to .bak-<stamp>).
  python3 -I build_xf1b_face.py"""
import csv, hashlib, json, pathlib, sys, time

sys.path.insert(0, "/home/narolski/smad-next/src/AR1")
BLANK_PY = pathlib.Path("/home/narolski/smad-next/src/AR1/blank.py")
BLANK_SHA = "c8d8055f9f88fb7f"
OUT = pathlib.Path("/mnt/t7/smad_next/XF1")
ROWS = OUT / "xf1b_rows.csv"
ROWS_SHA = "e4df7801b0d589c580a561f3a422ee61b10af1269b4a01e63cb97f819eeb73f8"
SRC = pathlib.Path("/mnt/t7/smad_next/MS1/ffhq/src")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main():
    import numpy as np, cv2
    assert sha(BLANK_PY).startswith(BLANK_SHA), "blank.py changed"
    assert sha(ROWS) == ROWS_SHA, "row list changed"
    import ar1_common as K
    import blank as BK
    K.OUT = OUT                               # run-time output root only (lead's option a)
    for v in ("bg", "face"):
        (OUT / "blank" / v).mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(ROWS)))
    assert all(r["form"] == "whole" for r in rows)
    by = {(r["klass"], r["host"]): r for r in rows}
    hosts = sorted({r["host"] for r in rows})
    new, man = [], []
    for h in hosts:
        p = by[("FMHB", h)]["partner"]
        tem1, tem2 = SRC / f"{h.split(':')[1]}.tem", SRC / f"{p.split(':')[1]}.tem"
        outs = {}
        for klass in ("FMHB", "WARP"):
            r = by[(klass, h)]
            assert sha(r["src"]) == r["sha256"]
            rid = f"xf1b_{klass}_face_{h.split(':')[1]}"
            _, bg, fa = BK.one(dict(id=rid, path=r["src"], tem1=str(tem1), tem2=str(tem2), w1="0.5"))
            outs[klass] = (r, rid, bg)
            man.append(dict(id=rid, klass=klass, host=h, partner=p, input=r["src"], input_sha256=r["sha256"], tem1=str(tem1),
                            tem1_sha256=sha(tem1), tem2=str(tem2), tem2_sha256=sha(tem2), w1="0.5", output=bg, output_sha256=sha(bg),
                            unused_face_blanked=fa))
        ia = cv2.imread(outs["FMHB"][2]); ib = cv2.imread(outs["WARP"][2])
        ga, gb = (ia == 128).all(2), (ib == 128).all(2)
        m = BK.hull_mask(dict(tem1=str(tem1), tem2=str(tem2), w1="0.5"), ia.shape)
        assert ga[~m].all() and gb[~m].all(), h          # both copies grey everywhere outside the same hull
        for klass, (r, rid, bg) in outs.items():
            q = dict(r); q.update(id=rid, path=f"eval/xf1b/{klass}/face/{h.split(':')[1]}.png", form="face", sha256=sha(bg), src=bg)
            new.append(q)
    mp = OUT / "blank" / "xf1b_face_manifest.csv"
    with open(mp, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(man[0])); w.writeheader(); w.writerows(man)
    files = sorted((OUT / "blank").rglob("*.png"))
    (OUT / "blank" / "SHA256SUMS").write_text("".join(f"{sha(f)}  {f.relative_to(OUT / 'blank')}\n" for f in files) + f"{sha(mp)}  {mp.name}\n")
    ROWS.rename(ROWS.with_name(ROWS.name + f".bak-{time.strftime('%Y%m%d%H%M%S')}"))
    with open(ROWS, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows + new)
    print(json.dumps(dict(face_rows=len(new), all_rows=len(rows) + len(new), manifest_sha256=sha(mp), rows_sha256=sha(ROWS),
                          png_files=len(files))))


if __name__ == "__main__":
    main()
