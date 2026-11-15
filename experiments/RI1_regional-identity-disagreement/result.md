# RI1 regional identity disagreement: result (single read, Fri Nov 13 21:44 CET)

Read once at a585cb3 (`ri1_read.json`) against the adversary's pinned stage-3 floors. Reviewed in `experiments/reviews/REVIEW_TB1S_ME1_RI1_20261113.md` (ACCEPT). Development data only.

Registered reading: **"inconclusive: P1 invalid (projection carries scale)"**.
- The controls are in band: R0_61 vs R0 0.452, R2w4 vs R0 0.493, S0 vs R2w4 0.536, R2w4 vs R2w 0.499.
- The validity gate gave 0.934 and 0.873, against the required [0.40, 0.60]. The projection direction alone separates genuine photos better than P1 separates morphs (P1 0.702 [0.660, 0.741]). P1 is not a pass.
- Post hoc (reviewer): the two-person morph shows less occlusion spread than its own camera photo along the same direction (0.057).
- The single-image occlusion dispersion does not separate two-person from same-person splices at equal D (S4 vs S3 within D 0.522; pure-D reference 0.524). R4 vs R3 within D is 0.580.
- It adds nothing over the hand cues (−0.0002) or over Sb (−0.003 to −0.004 across seeds; test hosts −0.008 to −0.011), as expected for an uninformative feature. The seeds share the feature, so they are not replications.
- Adversary floors (all / nuisance / within-D logistic), exceeds no in every case:
  - S4 vs S3: 0.540 vs 0.773 / 0.719 / 0.757;
  - R4 vs R3: 0.595 vs 0.793 / 0.705 / 0.785;
  - R4 vs R0: 0.537 vs 1.000 / 1.000.
- M1 is not closed by this read.

What the paper may say: "Occluded face-recognition embeddings did not reveal a second identity in single images."

## Closing (lead's ruling, 13 Nov 2026: RI1 is closed for the sprint)

**Established (development data).**
- **The premise is invalid by its own validity check.** The check gave 0.934 and 0.873 against the required [0.40, 0.60]; P1 is 0.702 and is not a pass.
- **Single-image contrasts are 0.54-0.60, against floors of 0.77-0.79.** S4 vs S3 is 0.540 and R4 vs R3 is 0.595. Neither exceeds any floor.
- **The shortcut gain is −0.0002**, and the Sb increment is −0.003 to −0.004.

**May not be written.** "Regional identity disagreement exists" or "P1 passes". M1 is not closed.

**Not run, available after the deadline.**
1. A projection direction that is scale-free by construction (one that passes the validity check on genuine photos), registered fresh.
2. The same read on the look-alike set (LA1) once it exists.

**Saved embeddings, kept for reuse.** `/mnt/t7/smad_next/RI1/emb_rows_{0,1}of2.npz` and `emb_sources_{0,1}of2.npz`.
