# Landmark-morph ladder (AR1, with AR2 dose, AR3 baselines, AR4 blanking): result, first round, revised after review

Status 11 Nov 2026, about 22:45 CET: finished for the four released detectors and the retrain block (M3 seeds 1-8,
M3L seeds 1-5). Revised after the independent review (`experiments/reviews/REVIEW_AR1_20261111.md`, "needs
qualification"). The post hoc addendum, amendment 7/7b (spliced inner-face morph) and amendment 8 (softened copies)
were registered in `prereg.md` before they ran. The previous version is at
`/mnt/t7/smad_next/AR1/result_v1_before_review.md`. Facts only; the lead draws conclusions.

**Standing caveats, repeated in every summary.** The registered negative control is degenerate: both tools are
symmetric at 50%, so tool(S, H) is pixel-identical to tool(H, S), and the guard it was meant to provide is missing. The
registered falsifier reads "supported on the primary pool; secondary pool descriptive". All ladder numbers come from
our pipeline (aligned 512-pixel frames, one DGX).

## Summary in corrected wording (the review's sentences, with this round's numbers)

1. On landmark morphs built without benchmark cues, the released detectors separate a two-person morph from a warp-only
   photo with the same geometry (R2w4 vs R4: 0.89-0.99). Warp size alone does nothing (R2w vs R2w4: 0.49-0.52). This
   shows that they detect blend traces. It does not show that benchmark cues play no role on the benchmark. On the
   published FRLL files, the step from raw photo to history-matched photo (E7) is SelfMAD 0.95 / 0.92, ViT-B/16
   0.75 / 0.73, MixFaceNet 0.70 / 0.67, and reversed for ViT-L/14 (0.38). Raw file bytes and width separate published
   morphs from photos perfectly.
2. Most of the separation appears as soon as two captures are blended: a same-person morph is flagged almost as
   readily as a two-person one (warp-only vs same-person morph 0.81-0.96, "blend reading"). Replacing the second
   capture with a second, dissimilar person adds 0.60-0.75. This is an upper bound on identity reading, because the
   two-person pairs also look more different. The R4 score falls as pair similarity rises (Spearman with cos(H, B)
   -0.14 to -0.39). On the most similar decile of pairs, R3 vs R4 stays within 0.03 of the full value in 5 of 8 cells
   (n = 55 hosts, wide intervals). The identity excess over the best simple baseline survives Bonferroni-at-8 only
   for ViT-L/14 (+0.12 [0.04, 0.20], +0.11 [0.04, 0.20]). SelfMAD OpenCV is marginal and not replicated with
   FaceMorpher. Per database, SelfMAD's R3 vs R4 is 0.735 / 0.701 on FRGC and 0.534 / 0.511 on colorFERET.
3. Detail loss: matching R2w and R4 on Laplacian variance and band shares leaves the separation unchanged (CLIP
   0.99-1.00, SelfMAD 0.97 / 0.98, MixFaceNet 0.85 / 0.88), so H-new-1 is falsified on these two global statistics.
   With the author-approved softened copies (amendment 8), softened warp-only vs native two-person morph gives:
   - MixFaceNet 0.58 / 0.78: "detail loss explains" at the 61-pixel strength.
   - ViT-B/16 0.79 at 61 px, 0.96 at 113 px: "mixed".
   - SelfMAD 0.98 / 0.90 and ViT-L/14 0.97 / 0.99: "more than detail loss".
4. Part of the trace lies outside the inner-face hull. With the face blanked, R2w vs R4 is 0.73-0.97, and this holds on
   FRGC, which has no padded borders. The spliced inner-face morph (amendment 7b) confines the second capture to the
   face: there, R2w4 vs spliced morph is ViT-B/16 0.66 / 0.64, ViT-L/14 0.71 / 0.75, MixFaceNet 0.60 / 0.61 (none
   above the best simple baseline) and SelfMAD 0.91 / 0.95 (+0.15 to +0.26 above it). So for the CLIP detectors and
   MixFaceNet, most of the unspliced 0.89-0.99 comes from what whole-frame tools blend outside the face. SelfMAD
   separates the inner-face splice too (above the band baseline, but not shown to exceed the 3-statistic seam floor;
   amendment 9). No released detector is shown to read more than one simple statistic, interior sharpness, on spliced
   morph vs swap-splice: inside-hull Laplacian variance alone gives 0.926 against SelfMAD's 0.888 (amendments 10, 11). This part is specific to tools that blend the whole frame.
5. For regular morphs the audit finds both: blend-trace detection that works without benchmark cues, and, on the
   published FRLL files, sensitivity to photo history (SelfMAD strongly; ViT-B/16 and MixFaceNet moderately; not
   ViT-L/14). Neither a second identity nor face-only blending is shown to be what the CLIP detectors and MixFaceNet
   read.
6. Within-ladder contrasts do not depend on platform. Absolute levels and transfer to the published files do:
   reproduction held for 2 of 4 detectors, the A46 platform check passed on AUC only (Kendall 0.97), and the bridge
   failed in 4 of 8 cells.

Rungs, in words (512 x 512 PNG, the tools' own aligned frame; tools run unchanged):
- R0: camera photo (host H, neutral).
- R1: photo with matched history. Not built on our pools (it is the identity there); measured on the FRLL benchmark
  side with the record's E7 frames.
- R2: tool run on one photo. Identical to R0 for OpenCV, within 1 grey level for FaceMorpher.
- R2w: warp-only, H warped to the mean shape of H and the same person's other photo.
- R2wm: warp-only toward H's own mirrored shape.
- R2w4: warp-only toward the mean shape of H and the two-person partner B (the same geometry as R4).
- R3: same-person morph (H with the same person's photo from another session).
- R3m: mirror self-morph. A trace control only; never evidence about a second person.
- R4: two-person morph.
- S4: spliced morph, R4 inside the hull and R2w4 outside.
- S3: spliced twin, R3 inside the hull and R2w outside.
- S0: the R2w face pasted onto R2w4 through the same hull. With OpenCV its seam matches S4 in size but not in kind (see amendment 9). With FaceMorpher it has almost no seam: those reads are "seam not matched".
Pools: primary FRGC + colorFERET, 536 hosts (FRGC 427, FERET 109); secondary FRLL, 102 persons.

## Gates

- **G-a (reproduction, from the A46 RGB-only result, prereg):** MADation ViT-B/16 (FRLL OpenCV / FaceMorpher EER 1.47 /
  0.86 vs published 2.97 / 1.35) and MixFaceNet-MAD (4.42 / 2.98 vs 4.39 / 3.87) reproduced. MADation ViT-L/14 and
  SelfMAD: no published landmark anchor in the record -> "not reproduced, descriptive". Platform check of my scoring
  adapter (rescoring the 2,647 A46 FRLL crops on the DGX and comparing with the A46 H100 score files,
  `a46_platform_check.json`): AUCs agree within 0.0004 (|dAUC| <= 0.005 passes), but per-image logits differ (median
  0.05-0.17, max 4.6 / 7.0 / 1.2 logits for ViT-B/16 / ViT-L/14 / MixFaceNet; Kendall tau 0.969 / 0.966 / 0.973, below
  A46's 0.99 bar). So my scores reproduce A46 at the AUC level only, not image by image; the cause (GB10 vs H100
  numerics, JPEG decoder version of the A46 .jpg crops) is not identified.
- **G-b (twin validity, glintr100):** passed in all four cells. Primary pool: oracle AUC morph vs twin 0.998
  [0.996, 1.000] (OpenCV) and 0.998 [0.996, 0.999] (FaceMorpher); morphs verify against both contributors at false-match
  rate 1/1,000 (tau 0.283) in 99.2% / 99.1%; twins verify against the host in 100%. The registered negative control is
  **degenerate**: both tools are symmetric at 50%, so tool(S, H) is pixel-identical to tool(H, S) (40 of 40 checked);
  its 0.500 carries no information. FRLL: 1.000 everywhere, but with the source photo as reference (no independent
  photo) and the smiling confound.
- **G-c (probe on each network's frozen features, R4 vs R3, strict person folds):** readable (>= 0.65) for every
  network and cell. Primary pool OpenCV / FaceMorpher: SelfMAD 0.906 / 0.926, ViT-B/16 0.875 / 0.865, ViT-L/14 0.901 /
  0.906, MixFaceNet 0.693 / 0.676, M3 seeds 1-8 0.871-0.908. R4 vs R3m is 0.99-1.00 for the CLIP networks (mirror twins
  are trivially separable). Note: the first G-c run used folds by host only, which leaked the shared photo S_q between
  morph(H_p, S_q) and twin(H_q, S_q); it was discarded and rerun with folds over the cycles of the host -> B assignment
  (`src/AR1/folds.py`). M3 seed 8 scores were read in one analysis pass about 10 minutes before its G-c was computed
  (0.899 / 0.903); `analyse.py` now refuses to read a network without G-c.
- Rung validity: R2w, R2wm, R2w4 all differ from H (median mean |difference| 1.2-4.1 grey levels) with glintr100 cosine
  to H 0.966-0.990; R3m cosine to H 0.954 / 0.942 >= R3 0.946 / 0.938 (registered gate passed; against the
  independent photo R3m is lower, 0.849 vs 0.894). Warp check: R2w4 (and R2w) averaged with the matching partner-side
  warp reproduce the tool's R4 (R3) within 0.5 grey level over the whole frame (OpenCV, all 536 hosts) and exactly
  inside the face mask (FaceMorpher).

## Main table, primary pool, released detectors (ladder R0 -> R2w -> R3 -> R4)

AUC with 95% two-way person-bootstrap interval (B = 2,000); share = step d' / d'(R0 vs R4). Main verdict on R2w vs R4
(R2w replaces R2, amendment 1). OC = OpenCV, FM = FaceMorpher.

| Detector | Tool | R0 -> R2w (warp) | R2w -> R3 (blend two photos of one person) | R3 -> R4 (second identity) | R2w vs R4 (main) | Main verdict | R3 vs R4 side | R2w vs R3 side (renamed "blend reading") |
|---|---|---|---|---|---|---|---|---|
| SelfMAD | OC | 0.710 [0.69, 0.73] (0.25) | 0.922 [0.91, 0.94] (0.65) | 0.689 [0.65, 0.73] (0.23) | 0.966 [0.95, 0.98] | mixed (R0 -> R2w share 0.25 > 0.2) | mixed | blend reading (twins flagged) |
| SelfMAD | FM | 0.650 [0.64, 0.66] (0.16) | 0.959 [0.95, 0.97] (0.72) | 0.663 [0.63, 0.70] (0.17) | 0.984 [0.98, 0.99] | reads morphing | mixed | blend reading |
| MADation ViT-B/16 | OC | 0.566 [0.55, 0.58] (0.07) | 0.948 [0.94, 0.96] (0.70) | 0.695 [0.65, 0.73] (0.22) | 0.986 [0.98, 0.99] | reads morphing | mixed | blend reading |
| MADation ViT-B/16 | FM | 0.511 [0.50, 0.52] (0.01) | 0.948 [0.94, 0.96] (0.73) | 0.672 [0.63, 0.71] (0.20) | 0.984 [0.97, 0.99] | reads morphing | mixed | blend reading |
| MADation ViT-L/14 | OC | 0.427 [0.41, 0.44] (-0.08) | 0.896 [0.88, 0.91] (0.53) | 0.749 [0.71, 0.79] (0.28) | 0.992 [0.98, 1.00] | reads morphing | mixed | blend reading |
| MADation ViT-L/14 | FM | 0.463 [0.45, 0.48] (-0.04) | 0.926 [0.91, 0.94] (0.58) | 0.737 [0.70, 0.77] (0.26) | 0.994 [0.99, 1.00] | reads morphing | mixed | blend reading |
| MixFaceNet-MAD | OC | 0.587 [0.58, 0.60] (0.15) | 0.813 [0.80, 0.83] (0.61) | 0.619 [0.58, 0.65] (0.21) | 0.890 [0.86, 0.91] | reads morphing | mixed | blend reading |
| MixFaceNet-MAD | FM | 0.528 [0.52, 0.54] (0.05) | 0.841 [0.83, 0.86] (0.73) | 0.598 [0.56, 0.63] (0.18) | 0.901 [0.88, 0.92] | reads morphing | no identity reading | blend reading |

"Blend reading" (renamed from "identity reading", presentation change disclosed in prereg) on R2w vs R3 means the
rule's AUC >= 0.75 with lower bound > 0.65 between the warp-only image and the same-person morph: same-person morphs
are flagged. No second identity is involved. Multiplicity: for all four OpenCV primary cells the one-sided
bootstrap p of "AUC(R2w vs R4) <= 0.65" is < 1/2,000 and the Bonferroni-at-12 interval stays above 0.85 (SelfMAD
[0.948, 0.982], ViT-B/16 [0.970, 0.994], ViT-L/14 [0.970, 0.998], MixFaceNet [0.853, 0.923]).

Original R2 (tool on one photo; kept, labelled identical to R0 for OpenCV): R0 -> R2 AUC 0.479-0.503 for every
detector; R2 vs R4 0.912-0.993 (same as R0 vs R4).

Other one-photo controls, primary pool (`result_tables.md`, ladders C-E):
- R2w vs R2w4 (warp toward the same person's shape vs toward the partner's shape): 0.489-0.515 for every release;
  warp size alone does not move the scores.
- R2w4 vs R4 (identical geometry; only the blended second photograph differs): SelfMAD 0.959 / 0.981, ViT-B/16 0.986 /
  0.984, ViT-L/14 0.992 / 0.994, MixFaceNet 0.889 / 0.903.
- R2wm -> R3m (blending H with its own mirror, one photograph): 0.92-0.98 (SelfMAD, CLIP), 0.77-0.81 (MixFaceNet);
  R3m -> R4: 0.59-0.66. By amendment 5, R3m is read for trace contrasts only (a 32-pixel thumbnail separates R4 from R3m
  at 0.93 / 0.92), never for a statement about a second person.
- R3m vs R3: 0.47-0.64.

## Secondary pool, FRLL

Every FRLL rung that uses a smiling file (R2w, R3, R4 with a smiling partner, NC) is "confounded by capture detail and
expression"; no verdict. The clean FRLL ladder uses neutral files only: R0 neutral photo -> R2wm -> R3m -> R4nn (our
neutral + neutral two-person morphs of the 1,221 / 1,222 published pairs). R2wm vs R4nn: SelfMAD 0.994 / 0.998, ViT-B/16
0.996 / 0.997, ViT-L/14 0.997 / 0.996, MixFaceNet 0.986 / 0.988; R3m -> R4nn 0.53-0.75; R0 -> R2wm: SelfMAD 0.879 /
0.766, ViT-B/16 0.680 / 0.568, ViT-L/14 0.370 / 0.392, MixFaceNet 0.647 / 0.547 (verdicts printed in
`result_tables.md` are descriptive; secondary pool).

FRLL benchmark side (genuine class neutral-only; all-photo number in `result_tables.md`):

| Detector | Tool | Published morphs vs raw photos (AUC) | E7 step R1f vs R0f | E7 share of R4f vs R0f | Bench EER % | Bridge: published vs our same-pair morphs | Detection at bench threshold, published / ours |
|---|---|---|---|---|---|---|---|
| SelfMAD | OC | 0.999 | 0.949 [0.92, 0.97] | 0.63 | 0.08 | 0.519 [0.47, 0.57] | 1.00 / 1.00 |
| SelfMAD | FM | 0.999 | 0.920 [0.89, 0.95] | 0.54 | 0.12 | 0.239 [0.19, 0.28] | 1.00 / 1.00 |
| ViT-B/16 | OC | 0.998 | 0.753 [0.72, 0.80] | 0.27 | 1.72 | 0.333 [0.29, 0.36] | 0.99 / 0.99 |
| ViT-B/16 | FM | 0.999 | 0.725 [0.69, 0.77] | 0.23 | 0.98 | 0.448 [0.39, 0.50] | 0.99 / 0.99 |
| ViT-L/14 | OC | 0.991 | 0.376 [0.34, 0.40] | -0.12 | 2.78 | 0.417 [0.38, 0.45] | 0.97 / 0.99 |
| ViT-L/14 | FM | 0.998 | 0.381 [0.35, 0.40] | -0.12 | 0.98 | 0.382 [0.33, 0.43] | 0.99 / 0.99 |
| MixFaceNet | OC | 0.989 | 0.697 [0.67, 0.74] | 0.22 | 4.01 | 0.244 [0.21, 0.28] | 0.96 / 0.98 |
| MixFaceNet | FM | 0.993 | 0.670 [0.64, 0.71] | 0.19 | 2.94 | 0.563 [0.53, 0.60] | 0.97 / 0.97 |

Bridge criterion (AUC within 0.40-0.60 and detection within 10 points): detection rates agree in every cell; the AUC
criterion holds only for SelfMAD OpenCV, ViT-B/16 FaceMorpher, ViT-L/14 OpenCV and MixFaceNet FaceMorpher. Below 0.5
means our tool-size morphs score more morph-like than the published files.

Flag rates at each detector's FRLL benchmark EER threshold, primary pool (exact 95% intervals in `result_tables.md`):
R0 genuine photos SelfMAD 25.4% / 46.6%, ViT-B/16 3.7% / 3.0%, ViT-L/14 1.1% / 1.1%, MixFaceNet 15.1% / 12.5%;
twins (R3) 99.6% / 100%, 78.7% / 72.8%, 66.8% / 72.0%, 69.8% / 64.0%; morphs (R4) 100% / 100%, 93.8% / 91.8%,
93.8% / 96.1%, 85.4% / 75.9%.

## AR3 baselines (strict person folds) and excess over them

Best simple baseline on R2w vs R4: Laplacian variance (folded 0.774, OpenCV) or band power (0.756, FaceMorpher); best
non-content baseline: PNG bytes (0.685 / 0.687); 32-pixel thumbnail 0.566; border mask 0.521; background-only 0.565.
Detector excess over the best simple baseline, R2w vs R4 (paired interval): SelfMAD +0.192 [0.16, 0.23] / +0.228
[0.19, 0.26]; ViT-B/16 +0.212 [0.18, 0.24] / +0.229 [0.19, 0.26]; ViT-L/14 +0.218 [0.19, 0.25] / +0.238 [0.20, 0.27];
MixFaceNet +0.116 [0.08, 0.15] / +0.145 [0.11, 0.19]. Same for R2w4 vs R4 (+0.12 to +0.23). On R3 -> R4 (second
identity) the excess over the best simple baseline (band power 0.631 / 0.622, thumbnail 0.646) is: SelfMAD +0.059
[0.01, 0.11] / +0.041 [-0.01, 0.10]; ViT-B/16 +0.064 [-0.00, 0.13] / +0.049 [-0.01, 0.12]; ViT-L/14 +0.119 [0.06, 0.18]
/ +0.114 [0.05, 0.18]; MixFaceNet -0.012 [-0.07, 0.05] / -0.025 [-0.09, 0.04]. On R0 -> R2w a band-power probe
separates warped from unwarped photos at 0.858 / 0.719, above every detector.
FRLL benchmark files: raw bytes and width separate published morphs from raw photos perfectly (folded AUC 1.000).

## AR2 dose (300 hosts, FaceMorpher library, mixing 0-0.5)

Monotone for every network (Page trend test p < 1e-250). AUC of mixing m vs m = 0 at m = 0.1 / 0.3 / 0.5: SelfMAD
0.801 / 0.978 / 0.989; ViT-B/16 0.619 / 0.928 / 0.984; ViT-L/14 0.511 / 0.927 / 0.992; MixFaceNet 0.666 / 0.862 / 0.917;
M3 seeds 0.67-0.81 / 0.96-1.00 / 0.995-1.000. Mean logits flatten above m = 0.3 for SelfMAD and MixFaceNet.

## AR4 blanking (primary pool; constant grey; crop boxes and landmarks from the unblanked image)

R2w vs R4 with the background blanked / with the face blanked: SelfMAD 0.901 / 0.888 (OC), 0.913 / 0.924 (FM);
ViT-B/16 0.814 / 0.912, 0.820 / 0.909; ViT-L/14 0.813 / 0.860, 0.825 / 0.869; MixFaceNet 0.791 / 0.761, 0.821 / 0.802.
With the face blanked, R3 vs R4 is 0.50-0.62; R0 vs R2w 0.49-0.59. Every cell meets the registered "works" bar
(>= 0.75, lower bound > 0.65), including face-blanked: the separation of R2w from R4 survives removal of the inner face
(the 106-point hull, jaw to brows), so part of it is carried by the region outside the hull (hair, forehead, ears,
background, where the second photograph's outline is blended in).

## Our-retrain block (M3 = MADation recipe ViT-B/16, M3L = ViT-L/14; R x d0; last checkpoint)

This is a separate block: the retrains did not reproduce the published FRLL numbers (A12-BR). Results on the primary
pool, ladder R0 -> R2w -> R3 -> R4, OpenCV / FaceMorpher:

| Recipe | Seeds | G-c | R0 -> R2w | R2w -> R3 | R3 -> R4 | R2w vs R4 |
|---|---|---|---|---|---|---|
| M3 | 8 | 0.87-0.91 | 0.57-0.69 | 0.94-1.00 | 0.71-0.78 | 0.994-1.000 |
| M3L | 5 | 0.90-0.92 | 0.46-0.52 | 0.98-1.00 | 0.81-0.83 | 0.999-1.000 |

Verdict counts:
- M3L: main "reads morphing" 10 of 10; R3 vs R4 side "identity reading" 10 of 10.
- M3: main "reads morphing" 16 of 16. R3 vs R4 sits at 0.71-0.78; the side counts are in `result_tables.md`.

M3 seed 8 was read about 10 minutes before its G-c existed (disclosed). The same pair-dissimilarity caveat applies to
the identity step.

## Sensitivity: without the 8 validation-reserved FERET hosts

No change beyond the third decimal (e.g. R2w vs R4: SelfMAD OC 0.966 -> 0.967, MixFaceNet OC 0.890 -> 0.889).

## Post hoc addendum (registered before running; zero GPU), `posthoc.json`

- **P1, per database, R2w vs R4.** FRGC / colorFERET, OpenCV:
  - SelfMAD 0.993 / 0.890
  - ViT-B/16 0.995 / 0.988
  - ViT-L/14 0.995 / 0.989
  - MixFaceNet 0.886 / 0.904

  Face-blanked, FRGC / colorFERET, OpenCV:
  - SelfMAD 0.900 / 0.867
  - ViT-B/16 0.960 / 0.914
  - ViT-L/14 0.891 / 0.828
  - MixFaceNet 0.730 / 0.868

  R3 vs R4, FRGC / colorFERET:
  - SelfMAD 0.735 / 0.534 (OpenCV), 0.701 / 0.511 (FaceMorpher)
  - ViT-B/16 0.700 / 0.747
  - ViT-L/14 0.762 / 0.757
  - MixFaceNet 0.618 / 0.628

  All cells with intervals are in `posthoc.json`; colorFERET has n = 109 hosts.
- **P2 (H-new-2), pair dissimilarity.**
  - Spearman of the R4 logit with cos(H, B): SelfMAD -0.28 / -0.23, ViT-B/16 -0.23 / -0.31, ViT-L/14 -0.30 / -0.39,
    MixFaceNet -0.14 / -0.15.
  - Spearman with the 32-pixel thumbnail distance between H and B: -0.04 to +0.25.
  - R3 vs R4 on the most similar decile (55 hosts), full -> decile: SelfMAD 0.689 -> 0.652 and 0.663 -> 0.676;
    ViT-B/16 0.695 -> 0.689 and 0.672 -> 0.647; ViT-L/14 0.749 -> 0.721 and 0.737 -> 0.732; MixFaceNet 0.619 -> 0.575
    and 0.598 -> 0.559.
  - H-new-2's falsifier ("within 0.03") holds in 5 of 8 cells, so the prediction is not supported there.
- **P3 (H-new-1), strata matched on sharpness.** Matched AUC vs unmatched: SelfMAD 0.968 / 0.981 (0.966 / 0.984);
  ViT-B/16 0.993 / 0.992; ViT-L/14 0.997 / 0.996; MixFaceNet 0.851 / 0.881 (0.890 / 0.901). This uses 427 / 544 of
  1,072 images in usable cells. All four stay >= 0.85: falsified on these statistics.
- **P4, three checks.**
  - Bonferroni-at-8 excess over the best simple baseline (band power) on R3 -> R4:
    - SelfMAD +0.06 [-0.01, 0.13], +0.04 [-0.03, 0.12]
    - ViT-B/16 +0.06 [-0.02, 0.15], +0.05 [-0.04, 0.14]
    - ViT-L/14 +0.12 [0.04, 0.20], +0.11 [0.04, 0.20]
    - MixFaceNet -0.01 [-0.09, 0.08], -0.03 [-0.11, 0.07]
  - H-new-5, R0 vs R2wm: SelfMAD 0.705 / 0.646 (prediction "about 0.7 or more": met with OpenCV); ViT-B/16 0.557 /
    0.510 and ViT-L/14 0.408 / 0.442 (prediction "at or below 0.6": met); MixFaceNet 0.587 / 0.520.
  - H-new-4, on colorFERET, Spearman of the R4 score with the padding area that differs between H and B (median
    5.5% of the frame):
    - MixFaceNet -0.18 / -0.18: opposite sign; H-new-4 not supported.
    - SelfMAD +0.44 / +0.47; with the face blanked, +0.39 / +0.37.
    - ViT-B/16 -0.05 / -0.09; ViT-L/14 +0.18 / +0.13.

## Amendment 8: softened copies (author-approved shrink-and-enlarge path, AF0 images), `soft_splice.json`

200 hosts, OpenCV. Strengths are 61.2 px / 112.7 px inter-eye distance. The same-host native reference
(R2w vs R4) is SelfMAD 0.965, ViT-B/16 0.990, ViT-L/14 0.995, MixFaceNet 0.911.

| Detector | Softened R2w vs native R4 | Native R2w vs softened R4 | Softened R2w vs softened R4 | Native R0 vs softened R0 | Verdict (registered) |
|---|---|---|---|---|---|
| SelfMAD | 0.976 / 0.901 | 0.954 / 0.974 | 0.964 / 0.935 | 0.850 / 0.861 | more than detail loss |
| ViT-B/16 | 0.785 [0.72, 0.85] / 0.964 | 1.000 / 1.000 | 0.986 / 0.998 | 0.966 / 0.715 | mixed |
| ViT-L/14 | 0.966 / 0.991 | 1.000 / 0.999 | 0.995 / 0.998 | 0.603 / 0.429 | more than detail loss |
| MixFaceNet | 0.584 [0.52, 0.64] / 0.780 | 0.987 / 0.961 | 0.833 / 0.879 | 0.857 / 0.703 | detail loss explains (61 px) |

FaceMorpher, softened R2w vs native R4: SelfMAD 0.990 / 0.949, ViT-B/16 0.805 / 0.965, ViT-L/14 0.981 / 0.995,
MixFaceNet 0.568 / 0.782; verdicts as for OpenCV.

## Amendments 7 / 7b: spliced inner-face morph (one hull per host, pixel copy only), `soft_splice.json`

Seam (corrected wording, review of the spliced reads): pixel counts do not measure the seam. Counting pixels that
differ in the 3-pixel band only gives the inner half of the band. With OpenCV the seam has the same size in both
classes but not the same kind. The step size matches (mean absolute step 12.25 vs 12.17 grey levels, reviewer), but S4
carries a signed colour step of half the partner's skin tone, and one such number separates S4 from S0 at about 0.71.
With FaceMorpher the negative has almost no seam (step 1.06 vs 15.83). **Every FaceMorpher spliced read below is "seam
not matched"** and is not used for conclusions.

| Detector | R2w4 vs S4 (OC / FM) | S0 vs S4 | S3 vs S4 | R2w4 vs S0 | Unspliced R2w4 vs R4 | Excess of R2w4 vs S4 over best simple baseline (band 0.72) |
|---|---|---|---|---|---|---|
| SelfMAD | 0.906 / 0.945 | 0.889 / 0.951 | 0.579 / 0.667 | 0.539 / 0.485 | 0.959 / 0.981 | [0.15, 0.22] / [0.18, 0.26] |
| ViT-B/16 | 0.660 / 0.643 | 0.686 / 0.637 | 0.473 / 0.475 | 0.463 / 0.510 | 0.986 / 0.984 | [-0.11, -0.01] / [-0.13, -0.03] |
| ViT-L/14 | 0.708 / 0.746 | 0.725 / 0.740 | 0.519 / 0.531 | 0.470 / 0.516 | 0.992 / 0.994 | [-0.07, 0.04] / [-0.04, 0.08] |
| MixFaceNet | 0.600 / 0.610 | 0.630 / 0.603 | 0.511 / 0.517 | 0.470 / 0.508 | 0.889 / 0.903 | [-0.17, -0.07] / [-0.16, -0.07] |

The inside/outside sharpness-ratio baseline reaches 0.65-0.72.

Controls:
- Face-blanked with the same hull: R2w4 vs S4 is 0.49-0.52 for every detector (the images are identical outside the
  hull, as required).
- Background-blanked R2w4 vs S4 is 0.78-0.89.

Reviewer's marks:
- "CLIP >= 0.85": not met (0.64-0.75).
- MixFaceNet falls by 0.29.
- The falsifier "all within 0.02 of unspliced, or all below 0.75" is not met, because SelfMAD stays at 0.91 / 0.95.

S3 vs S4 (the second identity, inner face only) is 0.47-0.67.

Transfer read on the existing Poisson-blended set (H1, A27/A36, not rescored): the record has ViT-B/16 0.770 and
ViT-L/14 0.718 above a file-size floor of 0.620 (via the dossier); no SelfMAD or MixFaceNet H1 number is quoted here.

## Amendment 9 (after the review of the spliced reads; OpenCV-style tool only; POST HOC: registration and computation were committed together in 9f1f810, order not verifiable), `sp_floor.json`

- Evaluation set: the 3-statistic floor (seam tone luma and R-G, sharpness ratio, band5 at 224 px), fitted on the 100
  PN1 development hosts. On the 436 other non-validation hosts it gives S0 vs S4 0.861 [0.834, 0.886].
- Excess of S0 vs S4 over the floor, same images, paired:

  | Detector | S0 vs S4 | Excess over floor |
  |---|---|---|
  | SelfMAD | 0.882 | +0.021 [-0.013, 0.057] |
  | ViT-B/16 | 0.677 | -0.185 [-0.23, -0.14] |
  | ViT-L/14 | 0.723 | -0.138 [-0.19, -0.09] |
  | MixFaceNet | 0.631 | -0.231 [-0.27, -0.18] |

- Inside tone-matched fifths, S0 vs S4 changes by at most 0.015: SelfMAD 0.886, ViT-B/16 0.681, ViT-L/14 0.708,
  MixFaceNet 0.641. H-new-1's predicted drop of 0.05 is not seen. Its falsifier (drop <= 0.02 AND floor < 0.75) is not
  met, because the floor is 0.86.
- Swap-splice SW: the partner's warped half pasted, unblended, through the same hull onto R2w4. Median absolute seam
  statistics (luma tone / R-G tone / step): S4 9.3 / 5.4 / 7.8, S0 4.9 / 3.1 / 4.3, SW 15.6 / 9.1 / 15.2
  (`swap_seam.csv`).
- S4 (positive) vs SW, all 536 hosts:

  | Detector | S4 vs SW |
  |---|---|
  | SelfMAD | 0.888 [0.849, 0.922] |
  | ViT-B/16 | 0.723 [0.691, 0.759] |
  | ViT-L/14 | 0.616 [0.581, 0.652] |
  | MixFaceNet | 0.688 [0.665, 0.718] |

  The registered prediction (SelfMAD AUC <= 0.5, i.e. it reads a patch boundary) is falsified (>= 0.75). SelfMAD
  scores the spliced blend above the unblended patch, even though the patch has 1.7 to 2.0 times the colour step
  (luma 15.6 vs 9.3, R-G 9.1 vs 5.4, step 15.2 vs 7.8). SelfMAD does not read only the patch boundary; its S4 vs SW
  is below the simple-statistic floor of amendment 10 (excess -0.071). SelfMAD is not shown to exceed the 3-statistic floor on S0 vs S4 (+0.021
  [-0.013, 0.057]).

## Amendment 10 (registered in git 81864bd at 12 Nov 03:14:54 before this ran; post hoc in substance), `floors10.json`

Measurement only, no image written; OpenCV-style tool for (a); paired two-way person bootstrap.

(a) Simple-statistic floor for spliced morph S4 vs swap-splice SW (536 hosts):

| Statistic | AUC (folded) |
|---|---|
| Inside Laplacian variance | 0.926 [0.898, 0.951] |
| Inside/outside sharpness ratio | 0.774 |
| Band shares | 0.72-0.78 |
| Absolute seam step | 0.693 |
| Seam tone luma / R-G | 0.506 / 0.503 |
| Combined logistic, strict person folds (the floor) | 0.959 [0.938, 0.975] |

| Detector | S4 vs SW | Excess over floor |
|---|---|---|
| SelfMAD | 0.888 | -0.071 [-0.110, -0.036] |
| ViT-B/16 | 0.723 | -0.236 |
| ViT-L/14 | 0.616 | -0.342 |
| MixFaceNet | 0.688 | -0.270 |

So SelfMAD's separation of the spliced blend from an unblended patch is below what interior sharpness alone gives. The
wording stays "SelfMAD does not read only the patch boundary"; it is not shown to read the blend beyond simple
statistics.

(b) Noise-residual floor for warp-only vs morph, qualified after REVIEW_FZ2_AR1A10 F9 (reviewer's wording):
- On warp-only vs morph, both MADation networks exceed a 12-number noise-residual floor by 5 to 8 points, and a
  combined 22-number floor by 4 to 7.
- SelfMAD exceeds the residual floor by 3 to 7 points, but on OpenCV R2w it is not shown to exceed the combined floor.
- MixFaceNet exceeds neither.
- Detectors sit at 0.96 to 0.99 against floors of 0.92 to 0.95, so the excess is most of the remaining headroom.
- The residual feature family was chosen after the detector scores were known. Post hoc in substance.

Floors:

| Contrast | 12-number residual floor | Combined 22-number floor (10 simple statistics + 12 residuals, strict person folds) |
|---|---|---|
| OpenCV R2w vs R4 | 0.935 | 0.949 |
| FaceMorpher R2w vs R4 | 0.917 | 0.920 |
| OpenCV R2w4 vs R4 | 0.935 | 0.933 (the residual floor remains the best) |
| FaceMorpher R2w4 vs R4 | 0.917 | 0.921 |

Excess over the combined floor, OpenCV / FaceMorpher R2w vs R4 (my recomputation, `floors11.json`):

| Detector | Excess (OC) | Excess (FM) |
|---|---|---|
| SelfMAD | +0.017 [-0.002, 0.037] | +0.064 [0.041, 0.091] |
| ViT-B/16 | +0.037 [0.021, 0.054] | +0.064 [0.043, 0.090] |
| ViT-L/14 | +0.043 [0.026, 0.061] | +0.074 [0.051, 0.100] |
| MixFaceNet | -0.059 [-0.088, -0.031] | -0.019 [-0.050, 0.012] |

Excess over the residual floor alone (amendment 10 as first computed):

| Detector | Excess (OC) | Excess (FM) |
|---|---|---|
| SelfMAD | +0.031 [0.011, 0.053] | +0.067 [0.043, 0.095] |
| ViT-B/16 | +0.051 | +0.067 |
| ViT-L/14 | +0.057 | +0.077 |
| MixFaceNet | -0.045 [-0.073, -0.018] | -0.016 [-0.047, 0.016] |

## Amendment 11 (registered in git a265476 at 12 Nov 03:36:37 before this ran; post hoc in substance), `floors11.json`

(a) Spliced morph vs swap-splice. Paired excess over the single statistic inside-hull Laplacian variance (0.926),
my computation:

| Detector | Excess over 0.926 |
|---|---|
| SelfMAD | -0.038 [-0.076, -0.004] (equal to the reviewer's value) |
| ViT-B/16 | -0.203 |
| ViT-L/14 | -0.309 |
| MixFaceNet | -0.237 |

No released detector is shown to read more than one simple statistic, interior sharpness, on spliced morph vs
swap-splice: inside-hull Laplacian variance alone gives 0.926 against SelfMAD's 0.888.

(b) H-D on the FRLL secondary pool, R2w vs R4 (confounded rungs; descriptive):
- The combined 22-number floor is 1.000 with both tools: the smiling-file confound makes the contrast separable by
  simple statistics.
- Detectors 0.96-1.00. Excess: ViT-L/14 -0.000 [-0.001, 0.000] / 0.000 [0.000, 0.000]; SelfMAD OpenCV -0.000
  [-0.002, 0.000]; ViT-B/16 -0.003 / -0.001; MixFaceNet -0.040 / -0.033.
- H-D untestable on FRLL: the combined floor is 1.000 (smiling-file confound, stated in the registration), so the falsifier fires mechanically; no information on whether AR1(b) replicates. (Review F7, commit 88f6016.)

## Gaps and what was not done

- R1 not built on the primary or FRLL tool-frame pools (history identical by construction); measured on the FRLL
  benchmark side only.
- OpenCV graded mixing not built (78 / 68_hires_morph hard-code 0.5); AR2 is FaceMorpher only.
- The approved h1_build.py warp path (third tool) was not built in round 1.
- SelfMAD and ViT-L/14 have no published landmark anchor (G-a descriptive).
- Negative control degenerate (symmetric tools).
- The 8 validation-reserved FERET hosts were in the pool (pool.py did not apply prep_train.is_val); sensitivity above.
- FRLL secondary pool: smiling confound; clean ladder only.
- Not run in this round: the third tool (h1_build), graded OpenCV, look-alike pairs, genuine photos passed through
  the benchmark's resize and format (author item).
- GPU: all new scoring (about 1.3 GPU-hours in jobs of 2-15 minutes each) ran on the DGX with thread caps, not on
  Athena. No single job exceeded half an hour. The lead's Athena instruction is noted, and the container is not set
  up.
- The first splice build (one hull per arm) and its scores are superseded and unread (amendment 7b).
- Scoring platform: AUC-level agreement with A46 only (Kendall 0.97, see G-a).
- Build speed (DGX CPU, shared, load 30-190): OpenCV 2,000-3,200 images/min (12 processes), FaceMorpher 330-1,030/min,
  warp-only driver 940-6,900/min, FaceMorpher library graded 430/min. The binding cost was GPU-side (RGB-MTCNN crops
  about 250-300/min batched; scoring 4.7-14 images/s per network on the shared GB10).
