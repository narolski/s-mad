# RELEASE sanity — MixFaceNet zeroshot re-score determinism check (closes qualifier pkt 2/6)

Written 2026-11-16T07:20 CET (06:20Z) by the continuity agent (autonomy mode, operator priority 3: "re-score
sanity MixFaceNet if GB10 has a free window"). CPU-only analysis; NO training, NO GPU job, nothing new dispatched.

## What was found
The released MixFaceNet (mixfacenet_mad_smdd) RSX re-scores on the GB10-regenerated RS1 crops were ALREADY
computed 2026-11-16 03:50/03:55 CET (`scores_rel_mixfacenet_mad_smdd__ad5v{1,2}.npz`, log "28253 images,
feat dim 128, 256.2 s; scores written") but had NOT been folded into the aggregate (last aggregate rerun was
03:46, before these landed) — hence the qualifier "MixFaceNet sanity not re-scored" in
RETRAIN_COHORT_EER_TABLE_20261116.md. This report closes that open item.

## Verification performed (independent, values recomputed from npz)
- Rerun `retrain_eer_aggregate_20261116.py` (python -I, spark venv) 2026-11-16T06:20Z:
  RSX mixfacenet_mad_smdd v1 sha256 4a895f4da4c182c8668dd15e8e2996eb632eb03cf6f1147fbfdc0fcd24d4c121
  RSX mixfacenet_mad_smdd v2 sha256 b01ef171b57104c8d5251c7055c6eab1e07a68e26e73e0a48f233fd6ed3cbbf2
  both missing_ids 0; S/H table values re-checked vs fresh aggregate.csv — bit-identical
  (spot-check FRLL/amsl B 4.93±2.36, facemorpher B 2.16±0.67, amsl L 9.65±5.60, amsl X 13.95±3.98).
- Independent delta script /tmp/rsx_delta_20261116.py (re-joined per id to the 17 registered families,
  RWS prod vs RSX regen):

| det | v | n families | mean |dEER| | max |dEER| | worst cell (prod -> regen) |
|---|---|---|---|---|
| mixfacenet_mad_smdd | v1 | 17 | 0.257 pp | 0.980 pp | MAD22/DiM-LM2-ODE(fast_dim_ode): 42.65 -> 43.63 |
| mixfacenet_mad_smdd | v2 | 17 | 0.245 pp | 0.490 pp | FRLL/amsl: 17.16 -> 16.67 |

- Cross-check of the B/L rows in the same independent run (must equal MONITOR_20261116T0240Z): B v1 0.134/0.490,
  B v2 0.235/1.400, L v1 0.099/0.379, L v2 0.238/0.735 — MATCH exactly (reproduced, not copied).

## Verdict
Determinism of the GB10 scoring pipeline now CONFIRMED for all three released detectors (B, L, MixFaceNet)
on both variants: mean|dEER| 0.099–0.257 pp, max 1.40 pp over 17/17 families, missing ids 0. Consistent with
crop byte-identity (v1 80.2%, v2 74.4%).
RETRAIN_COHORT_EER_TABLE_20261116.md qualifier (6) upgraded: "mixfacenet sanity not re-scored" REMOVED,
replaced by the full three-detector range. MixFaceNet H rows no longer carry the no-sanity caveat.

## Files touched
- RETRAIN_COHORT_EER_RECEIPTS_20261116.txt + 2 RSX mixfacenet lines (above SHAs).
- RETRAIN_COHORT_EER_TABLE_20261116.md: receipts block + qualifiers (2)/(6).
- Nothing else. Values on /mnt/t7 aggregate.csv regenerated (deterministic recompute, unchanged).
