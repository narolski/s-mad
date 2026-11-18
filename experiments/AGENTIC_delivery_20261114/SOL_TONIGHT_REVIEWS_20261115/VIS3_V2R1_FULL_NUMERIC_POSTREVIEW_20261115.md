# VIS3 v2r1 FULL numeric post-review — 2026-11-15

Decision: **GO_VIS3_FULL_NUMERIC** (79 checks PASS, 0 FAIL).

Reviewer: continuation-agent MAIN (Vibe session, single-agent review). **Limitation:** this review was written and executed by the same agent lineage that continued tonight's delivery, not by a fresh external reviewer. All checks are mechanical recomputations from released artifacts with pinned SHAs (checker script alongside this file), which bounds but does not eliminate the common-mode risk. The review is written standalone; my own runs/loops and other miscellaneous repo changes were NOT made by executing or altering numeric inference.

## What was reviewed
- Full numeric inference outputs `/mnt/t7/smad_next/VIS3/20261115/v2r1/numeric/full/{A,B,selfmad_hrnet_w18}/` (selfmad's terminal files identical layout), 3 models × 512 responses = 1536 registered rows, plus 4 anchor controls and 4 derived baselines per model.
- Checker: `VIS3_V2R1_FULL_NUMERIC_CHECKER_20261115.py` (fresh code; does not import `numeric_worker.py`; recomputes every aggregate from per-row data).

## Checks (all PASS)
1. Grants and provenance: `ROOT_NUMERIC_FULL_RELEASE.json` sha == external pin `342a1715…`; independent source delta review sha matches `c0234ae…`; construction receipt `27fb7fb…`; input admission `a83ed75…`; roster `ef50ff6…`; smoke post-review `84ecb02…`; generated regional indexing gate in smoke post-review verified TRUE.
2. Constructed inputs: all four PNGs and `actual_used_alpha.npy` hashes match `SHA256.json` and roster; roster host/donor logic consistent (samephoto: donor==host; crossphoto: donor 42/56 swapped).
3. Per model: `RESULT.json` status COMPLETE; 512 responses with complete, duplicated-free (input × fill {0,128} × cell 0–63) grid; geometry (row/col 8×8, 64 px cells, area 4096) consistent; `delta_logit == occluded − baseline` on all rows within 1e-6; all values finite; single constant baseline logit per input matching `baseline_logits`.
4. Reported regional means recomputed from raw per-cell deltas — byte-level agreement within 1e-6 for all 8 regions × 3 models; fixed registered boundary [3,4,10,13] and surround [0,7,56,63] cells, no post-hoc cell selection (`threshold=null`, `decision_flips=null`).
5. Controls: anchors reproduce reference z exactly (z==repeat==literal==reference); derived baselines z==repeat==literal and equal per-input baseline constants.
6. Scope flags in every RESULT: `maps_rendered=false`, `source_pixels_exported=false`, `publication_allowed=false`.
7. Smoke: all three smoke RESULT SHA256 match the admitted smoke post-review (`beb98f03…`, `f9b19254…`, `4bf3107a…`).

## Descriptive summary of measured regional contrasts (boundary − surround, z-logit sum-of-RGB; means of four separate 4096-px interventions, NOT simultaneous removal)
| model | 42_same fill0/128 | 42_cross fill0/128 | 56_same fill0/128 | 56_cross fill0/128 | baselines z (same/cross per pair) |
|---|---|---|---|---|---|
| A | 0.18 / 0.36 | 2.24 / 3.76 | 0.88 / 4.35 | 0.31 / 0.43 | -3.30/-2.36; -3.23/+2.80 |
| B | 0.25 / 0.50 | 0.06 / 0.22 | 1.15 / 3.62 | 0.13 / 0.25 | -3.06/+2.61; -3.33/+3.02 |
| selfmad_hrnet_w18 | -0.35 / -0.26 | -0.36 / -0.32 | -0.18 / -0.17 | -0.19 / -0.28 | +10.06/+7.03; +9.83/+6.68 |

Readings (descriptive only, single host per direction): A shows seam-over-surround sensitivity on crossphoto recombination, especially at fill 128; B shows it mainly for the 56 host; SelfMAD reacts strongly to the constructed morphs overall but its baseline response to surround occlusion exceeds seam response on these two hosts. Two host photos only; positions/content spatially confounded; no identity, anatomy, or benchmark claim is licensed by this read.

## Qualifications that must survive into any figure/prose
- Same two source photos (00042, 00056, CC BY-NC 2.0); private research only; publication of images still HOLD pending rights clearance.
- Regional means are separate-patch intervention means; the 16384-px simultaneous case is not measured.
- Fallback-ellipse transition mask is the actual mixing mask used but is not anatomically verified seam geometry.
- Same-photo construction is processed content, not a noop; literal copy is the noop realization.
- Post-review GO covers rendering under a NEW separate root grant (private render, print layout from VIS2 accepted constraints — 180 mm figure, ≥8 pt fonts), reusing the VIS2 layout; public dissemination remains HOLD.
