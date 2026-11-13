"""Shared test battery (BATTERY) reader: prints the audit rows per arm with seed ranges, from battery.json outputs.

  cd src && python -m battery.read DIR [DIR ...] [--json OUT.json] [--arms A Sb ...] [--expect-seeds 408 409 ...]

Statistics only. The battery registers no rule, so this reader prints no verdict, no "supported", "removes",
"passes" or similar word: a decision belongs to the registration of the arm that is read, applied by that arm's owner to
these numbers. Outputs that are TEST runs, that failed or skipped the platform gate, or whose logits changed since
scoring are listed and left out. When the networks of one arm come from more than one platform, the line says so
(seed and platform then change together). Records built from stored logits (battery.stored) are shown only with
--include-stored and are labelled "[stored logits]"; they are never pooled with battery-scored networks.
Never pooled either (rc2, pre-run review F1, F4): records of different battery code (battery_code_sha256; an arm whose
records carry more than one hash is refused) and tolerance-gated with byte-gated records (separate entries). NOTEs:
platforms differ between the arms of one print; stored and battery records in one print (TF32 off vs on: rows 4, 5, 10,
17, 19); training sources not checked against the battery sets (in-source). --expect-seeds refuses a print with a
missing seed or a duplicate (arm, seed)."""
import argparse
import json
import math
import pathlib
import sys

from . import rows as RW
from .legacy import sha


def load(dirs, include_stored=False):
    good, skipped = [], []
    for d in dirs:
        d = pathlib.Path(d)
        f = d / "battery.json"
        if not f.exists():
            skipped.append((str(d), "no battery.json"))
            continue
        r = json.load(open(f))
        why = None
        if r.get("source") == "stored":
            if include_stored:
                good.append((d, r))
            else:
                skipped.append((str(d), "stored logits (use --include-stored)"))
            continue
        if r.get("test_mode"):
            why = "TEST run"
        elif not r.get("gate", {}).get("passed"):
            why = "platform gate not passed"
        elif r.get("netcheck", {}).get("passed") is False:
            why = "network check (--expect-eval) failed"
        elif "rows" not in r:
            why = f"statistics not computed ({r.get('status')})"
        else:
            for s, v in r["sets"].items():
                if not (d / v["logits_file"]).exists() or sha(d / v["logits_file"]) != v["logits_sha256"]:
                    why = f"logits of set {s} missing or changed"
        if why:
            skipped.append((str(d), why))
            continue
        good.append((d, r))
    return good, skipped


def fmt(x):
    if x is None:
        return "-"
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, (int, float)):
        if isinstance(x, float) and math.isnan(x):
            return "nan"
        return f"{x:.3f}"
    return str(x)


def rng(vals):
    v = [x for x in vals if isinstance(x, (int, float)) and not isinstance(x, bool) and not math.isnan(x)]
    if not v:
        return "-"
    lo, hi = min(v), max(v)
    return fmt(lo) if lo == hi else f"{fmt(lo)} to {fmt(hi)}"


TF32_ROWS = ("4", "5", "10", "17", "19")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--arms", nargs="*")
    ap.add_argument("--json")
    ap.add_argument("--include-stored", action="store_true", help="also records built from stored logits (battery.stored), labelled")
    ap.add_argument("--expect-seeds", nargs="*", type=int, help="every arm printed must have exactly these seeds, once each")
    a = ap.parse_args()
    good, skipped = load(a.dirs, a.include_stored)
    by = {}
    for d, r in good:
        if a.arms and r["arm"] not in a.arms:
            continue
        if r.get("source") == "stored":
            lab = r["arm"] + f" [stored logits, {r['block_set']}]"
        else:
            gc = r.get("gate", {}).get("gate_class", "byte-gated")
            lab = r["arm"] + ("" if gc == "byte-gated" else f" [{gc}]")
        by.setdefault(lab, []).append((d, r))
    out = dict(note="statistics only; no verdict (the battery registers no rule)", skipped=skipped, arms={}, refused={}, notes=[])
    print("BATTERY reader: statistics only; no verdict. Ranges are min to max over the seeds listed.")
    for d, why in skipped:
        print(f"  left out: {d} ({why})")
    if a.expect_seeds:
        bad = {}
        for lab, nets in by.items():
            ss = [r["seed"] for _, r in nets]
            if sorted(ss) != sorted(set(a.expect_seeds)) or len(ss) != len(set(ss)):
                bad[lab] = sorted(ss)
        if bad:
            print(f"REFUSED (--expect-seeds {a.expect_seeds}): arms with missing or duplicate seeds: {bad}")
            out["refused"]["expect_seeds"] = bad
            if a.json:
                pathlib.Path(a.json).write_text(json.dumps(out, indent=1))
            return 7
    kinds = {("stored" if r.get("source") == "stored" else "battery") for v in by.values() for _, r in v}
    keys = {lab: sorted({(f"stored logits ({r['block_set']})" if r.get("source") == "stored" else r["platform"]["key"])
                         for _, r in nets}) for lab, nets in by.items()}
    allkeys = sorted({k for v in keys.values() for k in v})
    if len(allkeys) > 1:
        n = f"NOTE: the arms in this print come from different platforms or sources ({'; '.join(allkeys)}); compare arms only within one platform"
        print(n)
        out["notes"].append(n)
    mixed = kinds == {"stored", "battery"}
    if mixed:
        n = ("NOTE: stored records (TT1/MEDS rescored with TF32 off) and battery records (TF32 on) in one print: rows "
             "4, 5, 10, 17, 19 are not comparable between them")
        print(n)
        out["notes"].append(n)
    for arm in sorted(by):
        nets = sorted(by[arm], key=lambda x: x[1]["seed"])
        hashes = sorted({r.get("battery_code_sha256") or r.get("stats_code_sha256") or "none" for _, r in nets})
        if len(hashes) > 1:
            print(f"\n=== arm {arm}: REFUSED: its records carry {len(hashes)} battery code hashes {[h[:12] for h in hashes]}; not pooled")
            out["refused"][arm] = dict(code_hashes=hashes, dirs=[str(d) for d, _ in nets])
            continue
        seeds = [r["seed"] for _, r in nets]
        plats = keys[arm]
        vers = sorted({r["battery_version"] for _, r in nets})
        gcs = sorted({r.get("gate", {}).get("gate_class", "stored" if r.get("source") == "stored" else "byte-gated") for _, r in nets})
        print(f"\n=== arm {arm}: seeds {seeds}; platform {'; '.join(plats)}; gate {', '.join(gcs)}; battery {', '.join(vers)} "
              f"code {hashes[0][:12]}")
        if len(plats) > 1:
            print("    NOTE: more than one platform in this arm; seed and platform change together")
        ins = sorted({r.get("in_source_note") for _, r in nets if r.get("in_source_note")})
        for n in ins:
            print(f"    NOTE: {n}")
        A = dict(seeds=seeds, platforms=plats, gate=gcs, versions=vers, code_sha256=hashes[0], in_source_notes=ins, rows={})
        for rid in sorted(RW.ROWS, key=int):
            spec = RW.ROWS[rid]
            print(f"  row {rid}. {spec['name']}")
            if mixed and str(rid) in TF32_ROWS:
                print("      NOTE: TF32 differs between stored (off) and battery (on) records for this row's TT1/MEDS statistics")
            R = A["rows"].setdefault(str(rid), dict(name=spec["name"], stats=[]))
            if spec.get("missing"):
                print(f"      not measured by the battery: {spec['missing']}")
                R["missing"] = spec["missing"]
            for k, (label, blk, paths) in enumerate(spec["stats"]):
                ps = paths if isinstance(paths, list) else [paths]
                per = []
                nc = []
                for _, r in nets:
                    st = r["rows"][str(rid)]["stats"][k]
                    if st.get("not_computed"):
                        nc.append((r["seed"], st["not_computed"]))
                        per.append([None] * len(ps))
                    else:
                        per.append(st["values"])
                cols = [rng([p[j] for p in per]) for j in range(len(ps))]
                n_ok = sum(1 for p in per if any(v is not None for v in p))
                line = " / ".join(cols)
                print(f"      {label}: {line}  (n = {n_ok} of {len(nets)} seeds)")
                for s, why in nc:
                    print(f"          seed {s}: not computed ({why})")
                R["stats"].append(dict(label=label, block=blk, paths=ps, per_seed={str(r['seed']): p for (_, r), p in zip(nets, per)},
                                       range=cols, n=n_ok))
        out["arms"][arm] = A
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
