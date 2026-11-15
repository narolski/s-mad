"""Shared test battery (BATTERY): check of the H100 smoke result tar (CPU, after fetch). For each smoke network, the
battery's dev logits must equal the network's stored fit-job logits (scores_eval.npz of its AB1 tar) on all 21,277 rows,
byte for byte; prints the gate record and the other sets' counts and finiteness. Decides nothing beyond "identical or not".
  cd src && python -m battery.smoke_check SMOKE_TAR OUT.json"""
import io
import json
import sys
import tarfile

import numpy as np

from .regress import T7, npz


def main():
    tar, out = sys.argv[1], sys.argv[2]
    R = {}
    with tarfile.open(tar) as t:
        names = t.getnames()
        root = names[0].split("/")[0]
        for n in ("AB1_Sb_s408", "AB1_A_s408"):
            rec = dict()
            try:
                b = json.loads(t.extractfile(f"{root}/{n}/battery.json").read())
            except KeyError:
                R[n] = dict(error="no battery.json")
                continue
            rec["status"] = b.get("status")
            rec["platform_key"] = b["platform"]["key"]
            rec["gate"] = {k: b.get("gate", {}).get(k) for k in ("n", "n_differ", "max_abs", "byte_identical")}
            rec["sets"] = {s: {k: v.get(k) for k in ("n", "n_scored", "finite", "seconds")} for s, v in b["sets"].items()}
            if f"{root}/{n}/logits_dev.npz" in names:
                z = np.load(io.BytesIO(t.extractfile(f"{root}/{n}/logits_dev.npz").read()))
                s = npz(T7 / "AB1/results" / f"{n}.tar", f"{n}/scores_eval.npz")
                a, c = z["logit"].astype(np.float32), s["logit"].astype(np.float32)
                same_ids = z["id"].tolist() == s["id"].tolist()
                rec["dev_vs_stored"] = dict(same_ids_and_order=same_ids, n=len(a), n_differ=int((a != c).sum()) if same_ids else None,
                                            max_abs=float(np.abs(a.astype(float) - c.astype(float)).max()) if same_ids else None,
                                            byte_identical=bool(same_ids and (a == c).all()))
            R[n] = rec
    json.dump(R, open(out, "w"), indent=1)
    print(json.dumps(R, indent=1))


if __name__ == "__main__":
    main()
