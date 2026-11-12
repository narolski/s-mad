"""PN1 amendment 10 reader: spliced LoRA arm Sb and volume control Bv against B, per seed, development ladder first,
test ladder read once.  python3 -I sb_read.py [--results /mnt/t7/smad_next/PN1/results_rented]
-> experiments/PN1_.../tier1_sb/sb_read.json"""
import argparse
import csv
import hashlib
import pathlib
import sys
import tarfile

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pn1lib as K  # noqa: E402
import reads as RD  # noqa: E402
import tier1 as T1  # noqa: E402
import posthoc2 as PH  # noqa: E402


def scores(tar, key="scores_eval.npz"):
    h = hashlib.sha256(tar.read_bytes()).hexdigest()
    assert h == (tar.parent / (tar.name + ".sha256")).read_text().split()[0], tar
    d = tar.parent / "unpacked"
    name = tar.name[:-4]
    if not (d / name).exists():
        with tarfile.open(tar) as t:
            t.extractall(d)
    z = np.load(d / name / key)
    return dict(zip([str(i) for i in z["id"]], z["logit"].astype(float)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(K.PN1 / "results_rented"))
    a = ap.parse_args()
    R_ = pathlib.Path(a.results)
    cat = {r["id"]: r for r in K.catalog()}
    rows = []
    for r in csv.DictReader(open(K.PN1 / "manifests2" / "pn1_eval.csv")):
        x = dict(r)
        x["neutral"] = r["neutral"] == "True"
        c = cat.get(r["id"])
        if r["fam"] == "splice":
            x.update(field="", persons=(r["host"],), pool="ladder")
        elif c is not None:
            x.update(field=c.get("field", ""), persons=c["persons"], pool=c["pool"])
        else:
            import re
            ids = re.findall(r"(\d{3})_\d{2}", pathlib.Path(r["path"]).name)
            x.update(field="", persons=tuple(sorted({"frll:" + i for i in ids})), pool=r["cell"])
            x["host"] = x["persons"][0] if x["persons"] else r["id"]
        rows.append(x)
    P = RD.pools([r for r in rows if r["fam"] != "splice"])
    for r in rows:
        if r["fam"] == "splice":
            P.setdefault(("T_" if r["role"] == "test" else "D_") + r["rung"], []).append(dict(r, fam="ladder"))
    fl, flinfo = PH.floor3()
    out = {"floor3": flinfo}
    for seed in (401, 402):
        S = {}
        Sb = R_ / f"PN1_B_s{seed}.tar"
        if not Sb.exists():
            continue
        S["B"] = scores(Sb)
        rs = R_ / f"PN1_Brescore_s{seed}.tar"
        if rs.exists():
            S["B"].update(scores(rs, "scores_splice.npz"))
        for arm in ("Sb", "Bv"):
            t = R_ / f"PN1_{arm}_s{seed}.tar"
            if t.exists():
                S[arm] = scores(t)
        res = {}
        for arm, s in S.items():
            r = {}
            for pre in ("D_", "T_"):
                if not P.get(pre + "R4_face") or not all(x["id"] in s for x in P[pre + "R4_face"] + P[pre + "R2w_face"]):
                    r[pre + "i_faceblanked"] = "not scored"
                    continue
                r[pre + "i_faceblanked"] = RD.paired(s, P, pre + "R4_face", pre + "R2w_face")
                pos, neg = P[pre + "S4"], P[pre + "S0"]
                ex = K.paired_auc_ci(RD.scores_of(s, pos), RD.scores_of(s, neg), [RD.unit(x) for x in pos],
                                     [RD.unit(x) for x in neg], extra={"floor3": (np.array([fl[x["id"]] for x in pos]),
                                                                                 np.array([fl[x["id"]] for x in neg]))})
                r[pre + "ii_S0_vs_S4_excess_floor3"] = ex
                r[pre + "faceonly_S0_vs_S4"] = RD.paired(s, P, pre + "S4_bg", pre + "S0_bg")
            if arm != "B" or True:
                full = RD.all_reads(s, P, 0.0)
                r["iii_storage"] = RD.storage_marks(full)
                r["H1_auc"] = full["d"].get("auc")
                r["mad22_e7_eer"] = (full["e"]["OpenCV_e7"].get("eer_eer"), full["e"]["Webmorph_e7"].get("eer_eer"))
            res[arm] = r
        for arm in ("Sb", "Bv"):
            if arm not in S:
                continue
            m = {}
            for pre in ("D_", "T_"):
                a1, b1 = res[arm].get(pre + "i_faceblanked"), res["B"].get(pre + "i_faceblanked")
                m[pre + "i"] = bool(isinstance(a1, dict) and isinstance(b1, dict) and a1["auc"] <= b1["auc"] - 0.05)
                ex = res[arm].get(pre + "ii_S0_vs_S4_excess_floor3", {})
                m[pre + "ii"] = bool(ex.get("excess_lo", -1) > 0)
            st = res[arm]["iii_storage"]
            m["iii"] = bool(st["P-c"]["pass_"] and st["P-c2"]["pass_"] and st["P-c2_kernels"]["pass_"])
            pg = T1.pg_bootstrap(S["B"], S[arm], P)
            m["iv_pg"] = pg
            m["iv"] = pg["non_inferior_3pt"]
            m["v"] = bool(res[arm]["H1_auc"] >= res["B"]["H1_auc"] - 0.02)
            m["kill_parts"] = dict(i_fails=not m["D_i"], H1_drop_gt_003=bool(res[arm]["H1_auc"] < res["B"]["H1_auc"] - 0.03),
                                   pg_hi_gt_3=bool(pg["hi"] > 0.03))
            res[arm]["marks_vs_B"] = m
        out[f"s{seed}"] = res
    d = K.RES / "tier1_sb"
    d.mkdir(parents=True, exist_ok=True)
    K.dump(out, d / "sb_read.json")
    print("DONE")


if __name__ == "__main__":
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    main()
