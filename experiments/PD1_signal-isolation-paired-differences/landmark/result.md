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
