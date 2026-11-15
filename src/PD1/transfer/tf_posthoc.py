"""Signal isolation by paired differences (PD1), cross-family transfer: post hoc additions (prereg amendment 2).

(a) pairwise single-family transfer: heads trained on one family A (purged of the held-out family's persons; C by the
    in-family inner 3-fold grouped CV), scored on another family T
(b) threat probes of the mean-direction heads of the registered leave-one-family-out runs

  tf_posthoc.py --feat clip_pool [--B 2000]
Writes /mnt/t7/smad_next/PD1/transfer/res/<feat>_posthoc.json
"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import tf_lib as K  # noqa: E402
import tf_analysis as A  # noqa: E402


def groups_of(f, hosts):
    return A.folds_for(f, hosts)[1]


def evaluate(head, F, R, H, T, ts, fl_stat, fl_rep):
    s = {}
    for rr in ts.ids:
        s.update(A.score_ids(head, F, ts.ids[rr]))
    pt, rep = ts.auc(s, "x3", "x1")
    fl = A.flags_for(T, head, F, R, H)
    e = dict(auc_x1_x3=pt, ci=K.ci(rep), excess=pt - fl_stat["auc"], excess_ci=K.ci(rep - fl_rep),
             share_x3_gt_x1=ts.share(s, "x3", "x1")[0], primary_flag=A.primary_flag(T, fl),
             flags={k: v["rate"] for k, v in fl.items()})
    e["reading_posthoc"] = A.read_transfer(pt, e["excess"], e["primary_flag"])
    return e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--feat", required=True, choices=list(K.FKEY.values()))
    ap.add_argument("--B", type=int, default=2000)
    a = ap.parse_args()
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    feat = [k for k, v in K.FKEY.items() if v == a.feat][0]
    F = K.load_features(*feat)
    H = K.all_hosts()
    R = K.refs()
    S = A.load_stats()
    out = dict(feature=K.FNAME[feat], label="post hoc (prereg amendment 2), descriptive", pairwise={}, meandir_probes={})
    for T in K.FAMS:
        ts = A.TestSet(F, H[T], a.B)
        fl_stat, fl_rep = A.floor(ts, S)
        Tp = {p for h in H[T] for p in (h["person"], h["partner"])}
        for Af in K.FAMS:
            if Af == T:
                continue
            tr = [h for h in H[Af] if not ({h["person"], h["partner"]} & Tp)]
            g = groups_of(Af, tr)
            r = dict(train_hosts=len(tr))
            for hn, pos in (("O", A.POS_O[Af]), ("T2", ("x3",))):
                C = A.choose_C_inner(F, Af, tr, pos, g)
                head, mdir = K.fit_multi(F, {Af: tr}, {Af: pos}, C)
                r[hn] = dict(C=C, **evaluate(head, F, R, H, T, ts, fl_stat, fl_rep))
                r[hn + "_meandir"] = evaluate(mdir, F, R, H, T, ts, fl_stat, fl_rep)
            out["pairwise"][f"{Af}->{T}"] = r
            A.log(f"{a.feat} {Af}->{T}: O {r['O']['auc_x1_x3']:.3f} (C {r['O']['C']}), O mean dir "
                  f"{r['O_meandir']['auc_x1_x3']:.3f}, T2 {r['T2']['auc_x1_x3']:.3f}, floor {fl_stat['auc']:.3f}")
        # (b) mean-direction heads of the registered LOFO
        tr_f = [f for f in K.FAMS if f != T]
        train = {f: [h for h in H[f] if not ({h["person"], h["partner"]} & Tp)] for f in tr_f}
        pos_o = {f: A.POS_O[f] for f in tr_f}
        _, mdir = K.fit_multi(F, train, pos_o, 1.0)        # the mean direction does not depend on C
        pr = A.probes(T, mdir, F, R, ts)
        if T == "D" and feat[0] == "clip":
            pr.update({"blanked " + k: v for k, v in A.blank_probe_D(mdir, feat[1], ts).items()})
        out["meandir_probes"][T] = pr
        A.log(f"{a.feat} mean-direction probes {T}:", {k: round(v["auc"], 3) for k, v in pr.items() if "auc" in v})
    p = K.OUT / "res" / f"{a.feat}_posthoc.json"
    json.dump(out, open(p, "w"), indent=1, default=float)
    A.log("wrote", p)


if __name__ == "__main__":
    main()
