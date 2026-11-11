"""SM1 amendment A12 item 11 (H-new-1): pair list of the frozen arm with five RANDOM pool partners (armd5).

Exactly the dose-curve construction of pairs.py (K = 5 instead of 50 / 500): the N release first-contributor slots of
arm b (armb.csv order), second contributors = 5 partners drawn with numpy default_rng(SEED + 30 + 5) from the
replacement pool of arm b' (valid non-contributor os25k_m_t renders that are not audit keys, matched-unused or
placebo partners; = the 2,433 partners of armbp.csv, sorted), each used N / 5 times, the same swap rule against a
repeated (key, partner) pair. The reconstruction of the pool is checked by reproducing armd50.csv and armd500.csv
exactly. With K = 5 the forward swap can fail near the end of the list (a key with up to five morphs needs
distinct partners); then the row swaps with an earlier row (counts per partner unchanged; number reported).
No image is made here.

  python3 -I pairs_d5.py -> OUT/lists/armd5.csv, RES/pairs_d5.json
"""
import csv
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sm1_common as K  # noqa: E402
import pairs as P  # noqa: E402


def dose(ok, repl_pool, Kd):
    need = len(ok)
    r3 = np.random.default_rng(K.SEED + 30 + Kd)
    parts = [repl_pool[i] for i in r3.choice(len(repl_pool), size=Kd, replace=False)]
    sl = [parts[i % Kd] for i in r3.permutation(need)]
    rows, seen2, back = [], set(), 0
    mk = lambda a, x: P.row(f"D{Kd}_{a}_{x}", a, x, "src", "src", P.IMG / f"armd{Kd}" / f"{a}_{x}.png")  # noqa: E731
    for i, (a, _) in enumerate(ok):
        if (a, sl[i]) in seen2:
            j = next((j for j in range(i + 1, len(sl)) if (a, sl[j]) not in seen2 and (ok[j][0], sl[i]) not in seen2),
                     None)
            if j is not None:
                sl[i], sl[j] = sl[j], sl[i]
            else:                       # K = 5 only: no later slot fits; swap with an earlier row (counts unchanged)
                assert Kd == 5
                j = next(j for j in range(i) if (a, sl[j]) not in seen2 and (ok[j][0], sl[i]) not in seen2
                         and ok[j][0] != a)
                seen2.discard((ok[j][0], sl[j]))
                sl[i], sl[j] = sl[j], sl[i]
                seen2.add((ok[j][0], sl[j]))
                rows[j] = mk(ok[j][0], sl[j])
                back += 1
        seen2.add((a, sl[i]))
        rows.append(mk(a, sl[i]))
    assert len({r["id"] for r in rows}) == len(rows)
    return rows, parts, sl, back


def main():
    if not sys.flags.isolated:
        sys.exit("run with python3 -I")
    rd = lambda n: list(csv.DictReader(open(P.LISTS / n)))  # noqa: E731
    ok = [(r["na"], r["nb"]) for r in rd("armb.csv")]
    repl_pool = sorted({r["nb"] for r in rd("armbp.csv")})
    assert len(repl_pool) == 2433, len(repl_pool)
    for Kd in (50, 500):                              # the pool reconstruction reproduces the existing dose lists
        rows, _, _, _ = dose(ok, repl_pool, Kd)
        old = rd(f"armd{Kd}.csv")
        assert [r["id"] for r in rows] == [r["id"] for r in old], Kd
    rows, parts, sl, back = dose(ok, repl_pool, 5)
    assert not set(parts) & set(K.PARTNERS) and not set(parts) & set(K.EVAL_PARTNERS)
    audit = {r["na"] for r in rd("audit.csv")} | {x for r in rd("audit.csv") for x in r["nb"].split("|")}
    assert not set(parts) & audit
    P.write("armd5.csv", rows)
    u, c = np.unique(sl, return_counts=True)
    info = dict(n=len(rows), partners=parts, uses=dict(zip(u.tolist(), c.tolist())),
                reproduced=["armd50.csv", "armd500.csv"], keys=len({a for a, _ in ok}),
                backward_swaps=back)
    json.dump(info, open(K.RES / "pairs_d5.json", "w"), indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
