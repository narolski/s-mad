# Protocol network, first tests (PN1): result (short page)

Status 11 Nov 2026, 21:00 CET: tier 0 done (CLIP and DINOv3, recomputed under amendment 4), certificate and
matched-subsample test done; tier 1 (eight ViT-B/16 LoRA fits) and the reference row submitted on Athena, pending
(Slurm forecast 12 Nov 16:56 for the fits). Full record: `README.md`. Registration: `prereg.md` (amendments 1 to 5,
pack pin). No conclusion is drawn here; the lead draws conclusions.

## Tier 0 (frozen heads; tier 0 decides nothing in favour, prereg section 7)

Test ladder 191 hosts (OpenCV-style engine), seed 401, arms photos-against-morphs (A0) / protocol (B0) / equal-size
protocol (Bn0). Intervals over partner cycles. τ_cam = 5% false alarms on development camera photos.

| Read | CLIP A0 | CLIP B0 | CLIP Bn0 | DINOv3 A0 | DINOv3 B0 | DINOv3 Bn0 |
|---|---|---|---|---|---|---|
| R2w vs R4 (excess over best of 39 statistics, 0.888) | 1.000 (+0.11) | 0.998 (+0.11) | 0.999 (+0.11) | 0.999 (+0.11) | 0.999 (+0.11) | 0.999 (+0.11) |
| R0_61 vs R4 | 0.999 | 0.998 | 0.999 | 0.999 | 0.999 | 0.998 |
| shift R0 -> R0_61 (SD) | +0.30 | +0.17 | +0.14 | +0.75 | +0.43 | +0.40 |
| shift R0 -> R0_112 (SD) | +0.15 | +0.08 | +0.04 | +0.45 | +0.24 | +0.18 |
| τ_cam: R0_61 flagged | 20.4% | 8.4% | 5.2% | 23.6% | 10.5% | 10.5% |
| τ_cam: FRLL jpeg50 flagged | 3.9% | 2.0% | 0.0% | 0.0% | 0.0% | 0.0% |
| τ_cam: gating-family mean miss | 16.0% | 16.4% | 22.8% | 37.6% | 37.1% | 40.1% |
| own rule: gating-family mean miss | 48.5% | 46.6% | 49.7% | 61.9% | 61.1% | 60.9% |
| H1 AUC | 0.877 | 0.888 | 0.879 | 0.850 | 0.842 | 0.839 |
| MAD22 E7 EER OpenCV / Webmorph | 4.9 / 6.2% | 4.4 / 4.9% | 3.9 / 6.8% | 5.4 / 12.8% | 5.2 / 11.4% | 4.9 / 10.8% |
| P-c / P-c2 | fail / fail | pass / pass | pass / pass | fail / fail | fail / pass | fail / pass |
| K0; 2 x 2 control | no; pass | no; pass | no; pass | no; pass | no; pass | no; pass |

Seed spread (CLIP): A0 seeds 402 to 404 chose a stronger regularisation (C = 0.1) and flag 7.3% of R0_61 at τ_cam.

Certificate (nuisance-only; `cert/`): manifest A 1.00 (engine), B 0.84, Bn 0.83, C 0.84. Matched-subsample test: no
kill rule met (48.5% kept; nuisance AUC 0.47; R0 -> R0_61 flag change +4.7 points matched, +8.9 random, +4.7 full).

## Provisional tier-0 version (kept, superseded)

The first tier-0 tables (CLIP heads A0 and B0, computed 19:35 to 19:53, read by the owner and reported to the lead at
about 19:53) were made with class balance over the whole manifest. The independent pre-run review (manifest counts
only, no score opened) showed that this balance made "stored at 61.2 px" a cue for "morph" in B0 and left a database
cue in A0. Those tables are kept under `tier0_v1_provisional/`, `tier0_v1_provisional_tables.md` and
`tier0_v1_provisional_key.csv` and are superseded. They are not results of PN1.

## Spliced reads (amendments 8 to 11), wording as corrected by the splice review

- "Spliced morphs (blend only inside the face): with OpenCV the seam is equal in size but not in kind. A spliced morph
  carries a colour step that one simple number separates from the negative at about 0.71. With FaceMorpher the
  negative has almost no seam, and those reads are not seam-matched."
- "Spliced positives move frozen heads partly toward the face (face-blanked 0.99 to 0.76 / 0.88 for spliced-only). No
  full-frame head reads more inside the face than one band-power statistic (0.906, chosen on test, optimistic). Spliced
  heads do not improve on real face-spliced morphs (H1)." Post hoc: heads trained on face-only copies do exceed band5
  on face-only test copies (CLIP 0.950, DINOv3 0.992) but transfer to nothing else (MAD22 E7 EER 33-36%, H1 0.53-0.56).
- "The bracketing share is saturated (1.000) and does not discriminate between heads."
- "Protocol plus spliced on DINOv3, corrected MAD22 2.0 / 3.0%: best of 8 heads on first-test data. The head still reads
  the surround. A lead to re-test, not a method result. Seeds vary only the inner folds." Post hoc training-person
  resampling: OpenCV E7 EER 1.0 to 8.8% (median 2.75%).

## Tier 1

Not yet run (pending on Athena).

## Compute

- DGX GB10 (shared), one process: about 37 minutes of GPU wall time (allowance 30 minutes).
- Athena (account plgmultivision-gpu-a100, A100-SXM4-40GB, container image `fedeff10…`):

| Job | Purpose | State | Elapsed | GPU-hours |
|---|---|---|---|---|
| 3545947 | smoke 1 (arm Bn) + DINOv3 extraction | FAILED (path bug in the smoke job file; DINOv3 part done) | 0:04:14 | 0.07 |
| 3545968 | smoke 2 (arm Bn, 200 steps, 64 rows) | COMPLETED, rc 0, 1.24 it/s, peak 30,833 MiB | 0:05:21 | 0.09 |
| 3545976_[0-7] | eight fits A, B, Bn, C x seeds 401, 402 (limit 2 h 15 min) | pending, forecast 12 Nov 16:56 | | |
| 3545977 | reference row (amendment 5; limit 1 h) | pending, forecast 13 Nov 12:01 | | |
