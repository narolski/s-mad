# Draft test design: regional identity disagreement [RI1]

Draft by the ideas and literature role (IDEAS), 13 Nov 2026, about 19:05 CET (machine clock; committed in 6db5154 at 19:07). **Not registered; nothing run.** A hypothesis
owner who takes it writes `prereg.md` from the template, gets the pre-run check and the lead's go. Ledger entry M1.

## Question

Does a two-person morph carry identity evidence that differs between face regions, in a way that a genuine photo, a
same-person morph or splice, a stored-small photo and a seam-only image do not? Measured with a frozen face-recognition
network, no training.

## Data (development only)

- The landmark ladder (AR1) hosts of FRGC and colorFERET that are already development or test hosts of the protocol
  tests: 291 hosts (191 test, 100 development, as in BD1), OpenCV-style engine (FaceMorpher rungs where they exist,
  reported separately). Rungs: camera photo R0, stored small R0_61, warp-only R2w4, same-person morph R3, two-person
  morph R4, seam-only S0, same-person splice S3, two-person splice S4. Sources and an independent host photo R from
  `experiments/AR1/pool.csv` (columns H, S, B, R).
- FFHQ development genuine photos (2,000) for the genuine reference distribution, and the border-blanked camera photos
  of the TT1 follow-up (Z3 rows) for the border control.
- Closed: everything listed in OWNER_BRIEF and LA1 section 1. No `valx`, FST, A12SP file.

## Measurement

- Route: the registered glintr100 route `src/AR1/fr.py` (prep_eval.kps unchanged, insightface norm_crop,
  `a2f_common.embed_crops('glint')`). Keypoints are found on the **unblanked** image; blanking is applied afterwards,
  in memory, to the 112 x 112 crop, so detection never fails because of an occlusion. No image is written.
- Eight occlusion patterns, constant colour (crop mean grey, fixed value), defined on the crop's five keypoints and
  fixed before any number: left-eye box, right-eye box, nose box, mouth box, upper half, lower half, left half, right
  half. Plus the unoccluded crop (e_0).
- Per image: embeddings e_0, e_1..e_8 (L2-normalised).

## Gate G0 (before any contrast): are occluded embeddings still identity-bearing?

On R0 against R of the same host (two genuine sessions) and against other hosts: verification AUC per pattern. A
pattern with AUC < 0.90 is dropped (fixed rule); if fewer than five patterns remain, RI1 stops with "face-recognition
regions too weak to test", and only a trained region encoder (ICT-style, about 6 H100-hours) could test M1.
Optional inner/outer branch for splices: embed outer-only (inside the landmark hull blanked) and test the same gate;
expected to fail (glintr100 needs the eyes), in which case the branch is dropped and stated as such.

## P1: oracle premise (uses the known sources; not a detector)

- For R4: leaning per pattern L_k = cos(e_k, emb(H_src)) − cos(e_k, emb(B_src)); for R3: L_k = cos(e_k, emb(H_src))
  − cos(e_k, emb(S_src)) (two sessions of one person).
- Statistic: spread V = SD over k = 1..8 of (L_k − L_0), divided by the mean of the two source cosines' distance
  (1 − cos(e_0, src)), so that a morph further from both sources does not get a larger spread by scale alone. The
  divisor is fixed here; the owner prints V also without it.
- Read: AUC(V_R4 > V_R3), host bootstrap B = 2,000, overall and within quintiles of the geometry gap G and of cos_HS.
- Kill: AUC ≤ 0.60. Then the regions of a full-frame morph do not lean to different contributors measurably, and M1
  holds for splices at most.
- Pass: AUC ≥ 0.70 with the lower bound > 0.62.

## S1: the single-image statistic

- Dispersion Δ = mean over pattern pairs of (1 − cos(e_j, e_k)), z-scored against the FFHQ development genuine
  distribution (fitted on FFHQ only, fixed before the ladder is read).
- Contrasts (AUC, host bootstrap; S-rungs also within the five BD1 D quintiles using `/mnt/t7/smad_next/BD1/d_values.csv`):
  - signal: R4 vs R3; S4 vs S3; R4 vs R0;
  - controls that must stay near 0.5 (≤ 0.60): R0_61 vs R0 (storage), border-blanked vs plain camera photo (border),
    R2w4 vs R0 (warp to two-person geometry, one identity), S0 vs R0 (seam), R3 vs R0 (two captures of one person;
    printed, no bar: a softness effect would show here).
- Floor (ADVERSARY convention): the best single statistic of the 27-statistic set on the same rows, cross-fitted by
  host halves, and Sb's logit. Incremental value: cross-fitted logistic on [Sb logit, Δ] against [Sb logit] for S4 vs
  S3, per Sb seed 403-407 (existing development scores only; no new network score).

## Outcome table (fixed before reading)

| P1 | S1 signal | S1 controls | Reading | Next |
|---|---|---|---|---|
| ≥ 0.70 | R4/R3 and S4/S3-within-D ≥ 0.65 | all ≤ 0.60 | regional identity disagreement exists and is readable in one image | if incremental gain ≥ +0.03 on ≥ 4 of 5 seeds: register an identity-consistency arm (ledger M1 f) |
| ≥ 0.70 | < 0.65 | — | the premise holds but glintr100 occlusions are too coarse to read it | trained region encoder only if the paper needs it; otherwise stop |
| ≤ 0.60 | S4/S3 ≥ 0.65, R4/R3 < 0.60 | all ≤ 0.60 | splice-only mechanism (inner blend against outer host) | arm limited to spliced attacks; state coverage |
| ≤ 0.60 | < 0.60 | — | no regional identity disagreement measurable | M1 closed; the paper may say "no regional identity signal with an off-the-shelf FR network" |
| any | any | any control > 0.60 | the statistic reads the nuisance | report which control; closed unless the control can be stratified away |

## Cost

About 291 hosts x 8 rungs x 9 crops ≈ 21,000 crops, plus 2,000 x 9 FFHQ and about 2,000 x 9 border rows: about 40,000
glintr100 forwards, under 0.3 GB10 GPU-hours; CPU reads about 2 hours. Machine: DGX (with the OMP / nice settings of
OWNER_BRIEF); test the command on 8 images first.

## Risks the reviewer should check

- Using B_src (the very photo blended into the morph) as a reference favours R4's leaning towards B; R3 has the same
  bias with S_src, so the contrast is balanced, but the owner should also print the leaning with the independent host
  photo R in place of H_src.
- The occlusion boxes come from five keypoints of the unblanked crop; for morphs those keypoints sit at the mean
  geometry. The same holds for R2w4, which is the control.
- FR networks are trained to be robust to occlusion: a small Δ on morphs may reflect that robustness, not the absence
  of regional identity differences. G0 bounds this only partly.
