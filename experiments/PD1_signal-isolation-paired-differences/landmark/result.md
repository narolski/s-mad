# Signal isolation by paired differences (PD1), landmark family: result

Owner's page. Facts only; the lead draws conclusions. Pre-registration: `prereg.md` beside this file (written
11 Nov 17:05 CET, before any number). Status: first pass pending.

## Inventory (11 Nov, 17:00 CET)

| Item | Where | Count | State |
|---|---|---|---|
| Landmark ladder (AR1) rungs, primary pool | `/mnt/t7/smad_next/AR1/img/frgcferet/{opencv,facemorpher}/{R2w,R2wm,R3m,R3,R4}`, R0 = `AR1/src` frames | 536 hosts x 2 engines x 5 rungs + 536 photos | all built by the AR1 owner (warp-only and mirror rungs included), nothing built here |
| Graded mixing set (landmark dose curve, AR2) | `AR1/img/frgcferet/fm_graded/m000..m050` | 300 hosts x 6 levels | built (FaceMorpher library) |
| FRLL ladder pool | `AR1/img/frll/...` | 102 persons | built; diagnostic only (smiling photo in every rung beyond x0) |
| Alpha-field probe images (AF0) | `/mnt/t7/smad_next/AF0/img` | photos 715, zero field 1,000, uniform 0.25 1,000, uniform 0.5 1,000 (and gradient / bump fields, not used) | built; warped halves of the pairs were still being built (10 files at 17:00), not used |
| SMDD renders and stored-small copies | `smadcvpr_data/train/smdd/os25k_bf_t` (256 px), `a47/data47/i3/train/smdd_a47e7` (80 px) | 25,000 pairs; 1,500 drawn | existing |
| FRLL-Morphs and corrected MAD22 landmark cells | AF0's `lists/bench_s.csv` | 600 morphs per cell (MAD22 Webmorph 500), genuine 204 native + 204 E7 per family | existing |
| Approved Poisson set (H1) | `/mnt/t7/smad_heldout/h1_poisson` | 598 + 598 | existing |
| DINOv3 ViT-L/16 512 patch tokens (AF0 cache) | `AF0/feat/dinov3_512/{ar1,af0_w1,af0_w2}` | ar1 8,294 complete; af0_w2 2,400 of 4,200; bench_s, h1, ar1g queued | reused (mean patch token) |
| CLIP ViT-L/14 224 patch tokens (AF0 cache) | `AF0/feat/clip224/{ar1,af0_w1}` | complete at 16:55 | patch tokens only, no class token: CLIP is re-run here for the class token (one pass gives both features) |
| CLIP class token / DINOv3 pooled (identity-shrinkage triage, ID0) | `ID0/feat/part_cd_*` | being extracted (DINOv3 at 256 px, fp16 weights) | not used (incomplete, other resolution and precision) |
| Simple statistics (AF0) | `AF0/cues/` | ar1, h1, bench_s, af0_w1 being computed | reused where present |

Images of the warp-only toward the mirror shape (x1m) and the SMDD pairs are in no DINOv3 cache and are extracted
here.

## First small pass (11 Nov, 17:47 CET): DINOv3 mean patch token, OpenCV-style engine, fold 0 only

Written as soon as the numbers existed. Fold 0: 107 held-out hosts; one-person head trained on 426 hosts
(pairs same-person morph vs warp-only and mirror self-morph vs warp-only; C = 0.01 by inner CV), two-person head on
423 hosts (two-person morph vs warp-only; C = 1). AUC on the 107 held-out hosts, later rung positive, 95% pigeonhole
person bootstrap. Floor = best folded AUC among the 27 simple statistics on the same 107 hosts' images (AF0's cached
statistics). Source: `first_pass_dino_opencv_fold0.json`.

| Contrast (held-out hosts) | One-person head | Two-person head |
|---|---|---|
| warp-only x1 vs two-person morph x3 (main) | 0.933 [0.885, 0.973] | 0.980 [0.963, 0.994] |
| simple-statistic floor, same images (band power 0.125 to 0.25 cycles/px) | 0.912 [0.870, 0.952] | same |
| excess over the floor | 0.021 [-0.037, 0.081] | 0.068 [0.026, 0.114] |
| Laplacian variance alone (folded) | 0.80 (whole frame), 0.87 (face box) | same |
| photo x0 vs x3 | 0.944 [0.898, 0.980] | 0.986 [0.972, 0.997] |
| floor for x0 vs x3 (Haar LH/HL energy) / excess | 0.955 / -0.010 [-0.066, 0.048] | 0.955 / 0.031 [-0.003, 0.077] |
| same-person morph x2 vs x3 | 0.652 [0.562, 0.740] | 0.759 [0.683, 0.838] |
| mirror self-morph xm vs x3 | 0.486 [0.391, 0.584] | 0.694 [0.605, 0.780] |
| photo x0 vs warp-only x1 | 0.543 [0.538, 0.557] | 0.564 [0.554, 0.584] |
| x1 vs x2 (training contrast, held out) | 0.873 [0.841, 0.907] | 0.915 [0.885, 0.946] |
| x1 vs xm (training contrast, held out) | 0.945 [0.920, 0.968] | 0.936 [0.908, 0.963] |

On this one fold and feature, the one-person head ranks two-person morphs above warp-only images at 0.93, but a
single band-power statistic reaches 0.91 on the same images; the excess (0.02) is below the registered 0.05 and above
0. The flag rate on softened genuine photos was not yet computed (benchmark features not yet extracted). Not a
verdict: four folds, two features, the flag rates and the projections are missing.

## Second step (11 Nov, 18:35 CET): both CLIP features complete, all five folds, registered sets

Out-of-fold over all 536 hosts, OpenCV-style engine, one-person head (pairs x2 vs x1 and xm vs x1; C by inner CV).
Fixed reading of the pre-registration (point estimates decide). Sources: `readings_clip_*.json`,
`q3q4_contrasts_clip_*.json`, `external_clip_*.json`. The DINOv3 run waits for its SMDD and x1m features; the
amendment-1 sets (softened hosts, AF0 halves) are not in these numbers yet.

| Feature | AUC x1 vs x3 [95%] | Floor (band power 0.125 to 0.25) | Excess [95%] | Flag rate FRLL E7 OpenCV | Flag rate MAD22 E7 OpenCV | Reading |
|---|---|---|---|---|---|---|
| CLIP class token | 0.998 [0.995, 1.000] | 0.886 | 0.112 [0.092, 0.136] | 5.4% (11/204) | 5.4% (11/204) | works |
| CLIP mean patch token | 0.987 [0.979, 0.993] | 0.886 | 0.101 [0.080, 0.125] | 3.9% | 4.9% | works |

The threshold flags 5.4% (11 of 204) of the untouched photos by construction (ties at the 11th highest score), so
flag rates near 5% mean the E7 photos are not flagged more often than untouched ones.
