"""ID0: contributor similarity actually present in benchmark pairs (glintr100 cosine of the two contributors' photos).
FRLL photos: the a46 'raw' gallery (existing glintr100, registered route). Pairs from file names: FRLL-Morphs (aaa_bbb,
neutral photos), MorDIFF (morph_a_e_and_b_e), DiM families (aaa_bbb, a46 keys; neutral assumed), corrected MAD22
(directory listing, aaa_ee-vs-bbb_ee), AR1 pool (cos_HB), H3 (h3crops_glint.npz, if present).
  python3 -I bench_sim.py   -> experiments/ID0.../bench_similarity.json
"""
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import id0_common as C  # noqa: E402


def q(v):
    v = np.asarray(v, float)
    return dict(n=int(len(v)), q10=round(float(np.quantile(v, .1)), 3), median=round(float(np.median(v)), 3),
                q90=round(float(np.quantile(v, .9)), 3), min=round(float(v.min()), 3), max=round(float(v.max()), 3))


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    z = np.load(C.A46_FEAT)
    raw = {str(k).split("|", 1)[1]: e / np.linalg.norm(e) for k, e in zip(z["keys"], z["emb"]) if str(k).startswith("raw|")}
    cs = lambda a, b: float(raw[a] @ raw[b])  # noqa: E731
    out = {}
    for fam in ("opencv", "facemorpher", "amsl", "webmorph", "stylegan"):
        v = []
        for p in sorted((C.FRLLM_RAW / f"morph_{fam}").glob("*.jpg")):
            a, b = p.stem.split("_")[:2]
            if f"{a}_03" in raw and f"{b}_03" in raw:
                v.append(cs(f"{a}_03", f"{b}_03"))
        out[f"FRLL-Morphs {fam}"] = q(v)
    for fam in ("FaceMorpher", "MIPGAN_I", "MIPGAN_II", "OpenCV", "Webmorph"):
        v = []
        for p in sorted((C.MAD22_RAW / fam).iterdir()):
            t = p.stem.split("-vs-")
            if len(t) == 2 and t[0] in raw and t[1] in raw:
                v.append(cs(t[0], t[1]))
        out[f"MAD22 corrected {fam}"] = q(v)
    keys = [str(k) for k in z["keys"]]
    v = []
    for k in keys:
        if k.startswith("pub_mordiff|"):
            t = k.split("|")[1].split("_")
            v.append(cs(f"{t[1]}_{t[2]}", f"{t[4]}_{t[5]}"))
    out["MorDIFF published"] = q(v)
    for fam in ("pub_dim_c", "pub_greedy_dim", "pub_greedy_dim_s"):
        v = []
        for k in keys:
            if k.startswith(fam + "|"):
                a, b = k.split("|")[1].split("_")[:2]
                v.append(cs(f"{a}_03", f"{b}_03"))
        out[f"DiM {fam[4:]} (neutral photos assumed)"] = q(v)
    out["AR1 FRGC+colorFERET pool (cos_HB)"] = q([float(r["cos_HB"]) for r in C.rows(C.AR1_POOL)])
    out["AR1 FRGC+colorFERET same-person (cos_HS)"] = q([float(r["cos_HS"]) for r in C.rows(C.AR1_POOL)])
    p = C.OUT / "feat" / "h3crops_glint.npz"
    if p.exists():
        h = np.load(p)
        E = {str(f): e / np.linalg.norm(e) for f, e in zip(h["folder"], h["emb"])}
        v = []
        for r in C.rows(C.H3_MAN):
            if r["family"] == "h3_sg3" and r["variant"] == "orig" and r["contrib_a"] in E and r["contrib_b"] in E:
                v.append(float(E[r["contrib_a"]] @ E[r["contrib_b"]]))
        out["H3 StyleGAN3 pairs (CASIA source crops)"] = q(v)
    json.dump(out, open(C.RES / "bench_similarity.json", "w"), indent=1)
    for k, v in out.items():
        print(f"{k:50s} {v}")


if __name__ == "__main__":
    main()
