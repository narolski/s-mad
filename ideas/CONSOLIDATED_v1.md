# Ideation round 1: the lead's consolidation

11 Nov 2026, 17:15 CET. Inputs: the lead's own seeds (`SEEDS_main.md`, written first), the strategist's
16 ideas (`IDEAS_v1.md`), and 48 ideas from seven independent generators that saw neither
(`ROUND1_raw.json`; lenses: physics, invariance, data, identity, adjacent fields, evaluation,
pragmatist). Nothing here has been run unless a line says "measured".

## 1. Where independent lenses converged

Agreement between generators that could not see each other is the strongest signal in this round.

| Theme | Proposed independently by | Status |
|---|---|---|
| K1. Supervise with a map that varies inside the image; target = the measured disagreement of the two warped source images ("ghost energy"), not the nominal mixing fraction; negatives = the morph's own two unblended warped halves | lead, adjacent fields, physics, data (twice), invariance, strategist (as a critique) | probe AF0 running; upgrade below |
| K2. Rebuild the standard training set (SMDD) with pipeline-matched genuine images and crossed history, keep the MADation recipe unchanged | data, pragmatist, adjacent fields, strategist | not started |
| K3. Evaluate at one fixed threshold: false alarms on processed genuine photos, miss rate at the threshold that protects every genuine pool; morph-blind "null rows" on top of every benchmark table | evaluation (three ideas), strategist | not started; needs only existing scores |
| K4. Read identity inside the morph class: does a detector's score rise with the dissimilarity of the two contributors? Benchmark construction cannot fake this, because only morphs enter | invariance, identity | not started; needs only existing scores |
| K5. One network with separately declared outputs per kind of evidence (history, re-synthesis, mixing, second person), and a cross-talk matrix as the proof | pragmatist, evaluation, data, adjacent fields | design choice for the method |
| K6. Identity shrinkage with a predicted ceiling, fitted on genuine photos only; the honest statement of what one image can show for GAN and diffusion morphs | physics, identity (three ideas), strategist, lead | cheap triage possible tonight |
| K7. Non-degenerate one-photo rungs for landmark tools | physics, data, invariance, pragmatist, strategist | adopted at 15:40 (warp-only, mirror self-morph) |
| K8. Planted-confound stress test as a certificate for a training recipe | lead, adjacent fields, invariance | part of AF0 |

## 2. Facts found during ideation (measured or verified today)

- **SMDD's attack class uses five recurring partner faces.** Verified on the release on disk: 15,000
  training morphs, 3,853 different first contributors, 5 different second contributors (3,444 / 3,310 /
  3,260 / 2,813 / 2,173 morphs each). None of the 25,000 genuine renders is a contributor. So every
  attack image a detector trains on contains one of five faces, and the two classes have disjoint
  identity pools. Whether the SMDD paper states this is not yet checked.
- **For landmark tools, "tool on one photo" is the photo** (pixel-identical). Measured; ladder amended.
- **One released detector with a frozen encoder separates diffusion morphs from one-photo
  reconstructions** (0.66 at 20 steps, 0.85 at 100) without reacting to rendering; the adapted
  releases do not (0.40 to 0.49). Reviewer recomputation from existing scores.
- **CLIP-based MADation networks use the expression imbalance** of 11 of 17 benchmark cells (reviewer
  preview; being registered as C1b).

## 3. The method line chosen

**One frozen or lightly adapted foundation backbone with a blend-evidence map as its main output.**

1. Training images: landmark morphs whose two warped source images W_A and W_B are stored. Target per
   patch: how much the two sources actually disagree there, scaled by the mixing weights
   (4·a·(1−a)·|W_A − W_B|, patch statistic). It is exactly zero for any image made from one capture,
   whatever its history, small for same-person blends, large for two-person blends.
2. Negatives with all-zero maps: W_A and W_B themselves (same warp, same frame, same storage as the
   morph), unprocessed photos, and existing history-matched copies.
3. Image score: mean of the highest tenth of predicted patches inside the face.
4. A second, separately declared output for re-synthesis evidence on GAN and diffusion images, if the
   author wants generator morphs covered; it is reported as its own capability and never mixed into
   the morph-evidence score.
5. Two training-set variants: SMDD renders only (the field's protocol; the comparison with MADation
   then changes nothing but data and supervision) and real photo pools.

Why this line: the target cannot be predicted by any property that is constant over an image, which
covers cues nobody has listed; soft but agreeing regions have target zero, so the head is not taught
that softness means mixing; and it gives checks a file cue cannot pass (map correlation on an unseen
tool, collapse when the face is blanked, dose curves).

What it cannot do, stated in advance: GAN and diffusion morphs have no pixel superposition, so the
blend map is expected to stay silent on them. For those families the paper reports (a) what the
re-synthesis output does, labelled as generated-image detection, and (b) the identity-shrinkage ceiling.

## 4. What "state of the art and shortcut-free" will mean (adopted from the evaluation lens, shortened)

- **S1, landmark morphs against history-matched genuine photos**: published FRLL-Morphs families and
  our FRGC/colorFERET ladder with one tool never trained on. Bar to beat: released MADation ViT-L/14 at
  1.0 / 1.0 / 14.7 / 4.4 % EER (FaceMorpher / OpenCV / AMSL / WebMorph). Metric: miss rate at the
  threshold that keeps false alarms at or below 5% on every genuine pool; EER and AUC beside it.
- **S2, processed genuine photos**: at the threshold giving 5% false alarms on untouched development
  photos, at most 10% on each benign variant and on two unseen photo sources.
- **S3, native benchmark cells**: non-inferiority only, and only on cells where a morph-blind model
  cannot already solve the task. Non-diagnostic cells are printed in grey under the null rows.
- **Generator cells**: no state-of-the-art claim unless morph against one-identity render reaches
  0.75 on a generator not used in training; otherwise the measured limit is reported.
- **Shortcut-free** is a list of measured bounds, never a universal statement: score shift of genuine
  photos under each benign variant; morph-free network at least 10 points worse on every claimed
  cell; score rises with dose; chance with the face blanked; expression-balanced re-read.

## 5. Order of work

Tonight (no queue):

| ID | Work | Compute |
|---|---|---|
| EV1 | Fixed-threshold, history-crossed re-read of existing scores; null rows; identity-dose slope inside each morph family | CPU |
| SM1 | SMDD partner audit (do released detectors score morphs with the five training partners higher than with unused partners); SMDD rebuild arms on frozen features | CPU, light GPU |
| AF0 wave 2 | Ghost-energy target, both halves as negatives, top-tenth pooling | as AF0 |
| ID0 | Identity-shrinkage triage on existing embeddings and landmark files | CPU |
| running | AR1, AD4, AG1, AD1b, C1b, FZ1 | — |

Thursday: LoRA fits of the chosen line (five seeds; SMDD-only and real-photo variants) on rented or
WCSS GPUs; corrected MAD22 scoring. Friday: unseen tool and source, guards, tables. Saturday: reviews,
figures, text.

## 6. Dropped to make room

Two-identity embedding head; stand-alone mixing-fraction regression; SelfMAD retrains; morph-free GAN
network; DiM ladder; pipeline-count ablation; generator twin training sets at 10,000 pairs; MADMamba
and MambaVision arms until one landmark gate is positive; d-prime shares as decision quantities
(they are not additive).

## 7. Questions only the author can answer

1. Class definitions (literature check running): one-photo reconstructions, same-person and mirror
   morphs, warp-only images.
2. May one network have two declared outputs (blend evidence; re-synthesis evidence) under the
   "one network, no fusion" rule?
3. May the existing shrink-and-enlarge path be run unchanged on training photos and on our own morphs,
   so that training contains history negatives and history-matched morphs?
4. Does "SMDD-only" allow morphs rebuilt from SMDD's own renders, or must the published morph files be
   the positives?
5. Is a landmark-only state-of-the-art claim plus a measured limit for GAN and diffusion morphs an
   acceptable headline?
