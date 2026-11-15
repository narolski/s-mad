# FRLL READ V1 — INDEPENDENT REVIEW (2026-11-15T20:13Z, GB10)

Reviewer: continuation agent (Vibe), eyeballs-off numeric audit per SOL_TONIGHT procedure.

## What was reviewed
`/mnt/t7/smad_next/FRLL_READ_V1/read/` produced by `src/FINAL/frll_read_v1_read.py`
run v2 (reader SHA256 **40586644124682eb879236d7cfba1074cd27c36445380b66113bd3a39e1c4550**),
freeze `FREEZE.json` manifest SHA **6af62341cf4936831af46ccf7ec966204512ee007b0ad3a4cf35f20cc0a3bb0b**
(re-verified inside the reader before metrics).

Receipts:
- FRLL_READ_RESULTS.json SHA256 **bcd7e82049e0fdb8c786d7a91096a84b842710d2d4ae5ff561e86375165846e2**
- FRLL_READ_TABLES.md  SHA256 **a1e91ed80e5467a5f4492561e4844191c0c374e1e361f6512cdcbd6d6e8adedb**
- Reader hard-pin checks all passed pre-metrics (manifest SHA, npz SHAs ×7 (5 Sb tars→npz + selfmad + a46),
  script pins ×3, weight pins ×4 via FREEZE, pre-amend2 manifest pin a3a10e25…, τ_FFHQ file).

## Independent recomputation (different code path, same inputs)
Brute-force FAR/FRR sweep EER + average-rank (tie-corrected) AUC, rebuilding cells directly from
the raw score npz files and the roster manifest — NOT through final_metrics.py:
- Sb s403–s407 × 5 families = 25 cells
- SelfMAD (release, fresh GB10 own) × 5 families = 5 cells
- madation_vitb16/v1, madation_vitl14/v1, mixfacenet/v1 × 5 families + mixfacenet/v2 facemorpher = 13 cells
**Result: 43/43 cells PASS** (EER |Δ| ≤ 0.06 pp, AUC |Δ| ≤ 0.0015). Counts per cell match:
morphs 2175/1222/1221/1222/1221 + 204 genuine; FaceMorpher and 10 OpenCV rows absent from v1 npz
(release crop-script fails) — exactly per RS1 amendment 7; v2 pools complete.

## Scale incident (resolved, quarantined)
Run v1 (JSON e45cc023a023…) stored `eer_pct` as a **fraction** while labelling it percent;
v2 multiplies by 100 (also seed-summary). Quarantined, not deleted, at
`/mnt/t7/smad_next/FRLL_READ_V1/read_quarantined_fraction_scale_20261115/`
its values ÷ aggregation agree with v2 under factor 100 (spot-verified). The tables above come
from v2 only.

## Headline cells (EER %, point [boot 95%]; descriptive read — no verdict tests; exact from v2 JSON)
| family | Sb mean ± sd (5 seeds) | SelfMAD own | MADation B/16 | MADation L/14 | MixFaceNet |
|---|---|---|---|---|---|
| amsl       | 11.85 ± 3.68 | 2.94 | 3.92 (v1) | 7.95 (v1) | 15.13 (v1) |
| facemorpher| 2.35 ± 1.78  | 0.90 | 0.57 (v2) | 0.98 (v2) | 2.95 (v2) |
| opencv     | 1.37 ± 0.56  | 0.16 | 1.96 (v1) | 2.73 (v1) | 4.90 (v1) |
| stylegan   | 10.87 ± 3.96 | 16.67 | 18.58 (v1) | 39.20 (v1) | 9.08 (v1) |
| webmorph   | 11.69 ± 2.93 | 10.78 | 2.21 (v1) | 5.32 (v1) | 12.25 (v1) |

All released-detector cells use variant 1 except FaceMorpher (variant 2; crop-script failures in v1).

## Flag-threshold observation (kept as caveat in the manuscript)
- Sb at the own rule (logit>0) flags 66.9–82.9% of aMSL morphs while τ_FFHQ flip rates are shown
  for released/selfmad detectors only — Sb-NETS have NO registered tau_FFHQ row in
  final_thresholds.json (`nets.PN1_Sb_s40x.tau_ffhq` does NOT exist there) → flag_tau stays "—"
  for Sb in the tables. CORRECT on purpose: the reader reads only committed keys.
- MADation B/16 v1 flag_tau on aMSL = 0.0/27.0% (morph/genuine at dev-frozen tau) —
  strongly discordant flag rates vs own rule; keep the "processing mismatch" narrative.

## Side record kept, not promoted
`side_record`: a46 corrective npz vs RS1 prod_v2 xr_ rows (madation_vitb16):
7,265 shared rows, max|Δlogit| **14.57** — a46 is a different crop-path corrective run and is NOT
used in any table cell; registered as consistency telemetry only.

## Verdict
PASS for Tabela 5 / results.tex integration (descriptive cells only, no SOTA sentences,
FaceMorpher v2-only note, crop-fail counts kept, "development-exposed" FRLL qualifier kept).
