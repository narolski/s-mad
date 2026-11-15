# Draft test design: nuisance directions in the candidate's own features [NE1]

Draft by the ideas and literature role (IDEAS), 13 Nov 2026, about 19:05 CET (machine clock; committed in 6db5154 at 19:07). **Not registered; nothing run.** Ledger entries
M7 (group DRO), M9 (paired invariance), M10 (adversarial debiasing and erasure).

## Question

Two of the candidate's known failures, the reaction to a blanked-in border and the flags on same-person splices, are
either (i) directions in its penultimate features that a last-layer change can remove without losing detection, or (ii)
entangled with the detection direction. (i) licenses cheap training remedies (nuisance head with gradient reversal,
erasure layer, group-balanced loss). (ii) says those remedies will move along the known trade-off and that a new signal
(ledger M1 or M2) is needed instead.

## Networks and data (development only)

- The five frozen candidate networks, arm Sb seeds 403-407, last checkpoints, tars pinned in the C2P registration
  (2715e48). Only development rows are scored; no benchmark row.
- Fitting rows: Sb's own training manifest (features of training images; the network has seen them, which is the
  point of a last-layer refit, as in Kirichenko et al. 2023).
- Reading rows: the development and test hosts of the landmark ladder (R0, R2w4, R3, R4, S0, S3, S4), FFHQ
  landmark_combined (genuine and morphs), the MS1 FFHQ hold-out with its 61.2 px and 112.7 px stored copies (C2P
  rows), and the TT1 border reference rows: training-source camera photos with and without a CFP-shaped blanked
  border, plus the MSU-MFSD and Oulu-NPU border rows (Z3).

## Platform

Features are extracted on one machine and GPU model. Gate: the original head applied to the extracted features must
reproduce the stored development logits of the same platform within the PLATFORM_PINS tolerance; if no stored logits of
that platform exist, every comparison is made only between heads on the same extracted features (H0 against H1-H4),
and no number is compared with stored logits.

## Heads (all on the same frozen penultimate features)

- H0: the original head (reference).
- H1: plain logistic refit on the training features, class-balanced (refit control: shows what refitting alone does).
- H2: group-balanced refit (equal weight per group: camera photos, stored copies, warp-only, warped halves, S0, S3, S4,
  R4 and their stored copies), DFR-style, L2 chosen by cross-validation on training hosts only.
- H3: border erasure. A linear eraser (LEACE or the mean-difference projection, the owner fixes one) fitted on
  development camera photos of half the persons with and without the blanked border; applied to all features; then H1
  refit. Read on the other half of the persons and on MSU-MFSD / Oulu-NPU border rows.
- H4: storage erasure, the same with native against stored genuine pairs of the MS1 hold-out (half the persons for
  fitting).

Every head's threshold is set so that its flag rate on training-source camera photos equals H0's own-rule rate
(fixed rule, so that a head cannot gain by moving the operating point; the MS1 lesson).

## Reads

1. Border: flag rate on border-blanked camera photos (held-out persons, and MSU / Oulu), per head and seed.
2. Same-person splices: S3 flag rate at the threshold where S4 recall equals H0's, and the full front (S3 flags
   against S4 recall).
3. Detection: FFHQ landmark_combined AUC.
4. Storage: own-rule flag increase on stored genuine photos at 61.2 px and 112.7 px.
5. Linear decodability (printed): AUC of a probe for border presence and for storage on genuine rows, before and after
   erasure.

## Outcome table (fixed before reading)

| Result on ≥ 4 of 5 seeds | Reading | Next |
|---|---|---|
| H3 removes ≥ 70% of H0's border flags, landmark AUC within −0.01 | the border reaction is a separable direction | register a border nuisance head (gradient reversal) or an erasure layer as an arm, read beside the queued border-crossed data arm (Sbx); the cheaper one that passes wins |
| H3 removes < 50%, or costs > 0.02 AUC | border and detection share features | only data (Sbx) or a new input treatment can help; no adversarial arm |
| H2's front lies ≥ 0.05 below H0's (fewer S3 flags at equal S4 recall) | reweighting can move the trade-off | register a group-DRO arm with strong L2 (Sagawa et al.) |
| H2 within 0.03 of H0 and of H1 | the same-person-splice flags are not a weighting problem | group DRO / JTT closed for this backbone; the second-identity route needs a new signal (RI1, TB1) |
| H4 changes storage Δf by ≥ 0.02 with AUC within −0.01 | residual storage reaction is a separable direction | note for the next version; not a claim about the frozen network |

## Cost

Five ViT-B/16 networks x about 30,000-40,000 rows (training manifest plus reading rows) ≈ 0.5 H100-hours or about
1.5 GB10 GPU-hours; heads and erasers on CPU, about 2 hours. Belongs on WCSS or the DGX GPU under the dispatcher; no
new image is built.

## Risks the reviewer should check

- Features of the training rows are in-sample for the backbone; H1 is the control for that.
- The border rows used to fit the eraser and those used to read it must be person-disjoint.
- An erasure fitted on genuine rows can remove a direction that morphs use differently; read 3 guards this.
- These are statements about heads on frozen features. They cannot change the frozen candidate and do not count as a
  new method; any arm they license is post-freeze and goes through the method-selection rule (NEXT).
