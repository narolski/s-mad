<!-- Independent results review by the results-reviewer agent (on Opus), 11 Nov 2026 about 23:40 CET; saved verbatim by the lead. -->

# Review: does the detector read the blend inside the face, or the surround and softness? Landmark ladder follow-ups [AR1, addendum, amendments 7b and 8] and spliced and bracketing frozen heads [PN1, amendments 8 and 9], 11 Nov 2026

## Verdict: needs qualification

The direction holds. The CLIP-based releases and MixFaceNet-MAD do not show a face-confined blend reading. SelfMAD does. Spliced positives move our frozen heads partly toward the face. Four claims go further than the evidence:
- **"The seam is equal in both classes."** For OpenCV the seam has the same size in both classes but not the same kind. For FaceMorpher the negative has almost no seam at all.
- **"More than detail loss"** for ViT-L/14. This cannot be told apart from surround ghosting.
- **The seed-stability claim.** The seeds change only the inner folds.
- **The DINOv3 MAD22 result (2.0 / 3.0%).** It is the best of 8 heads read on first-test data, from a head that still reads the surround (face-blanked 0.999).

One finding cuts against the remedy: the spliced-trained heads are not better on real face-spliced morphs (the approved Poisson set, H1).

## Q1. Released detectors

Is the spliced contrast fair? I ran three single-thread CPU checks on 150 random hosts per tool, comparing each image with its own surround in a ring 3 or 6 px inside the hull. Scripts are in `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/splice/`.
- **Pixel counts do not measure the seam.** `splice_seam_pixels.csv` counts pixels that differ in the 3-px band. For S4, S3 and OpenCV S0 that is 0.497 to 0.498 of the band, which is simply the inner half of the band. It says nothing about how strong the step is.
- **OpenCV: step size is matched, tone is not.** The mean absolute step is 12.25 grey levels for S4 and 12.17 for S0 (AUC 0.53). But the signed colour offset differs: S4 carries half of B's skin tone at the hull (median 13.8 to 14.7), while S0 has a geometric seam (7.4 to 6.7). That one number separates S4 from S0 at AUC 0.71 to 0.73. This is about what the CLIP releases reach on S0 vs S4 (ViT-B/16 0.686, ViT-L/14 0.725) and above MixFaceNet (0.630).
- **FaceMorpher: S0 is not a seam-matched negative.** The step is 1.06 for S0 against 15.83 for S4 (AUC 0.999); the median band count is 159 px. Every FaceMorpher S0-vs-S4 read should be dropped or labelled "seam not matched". SelfMAD gains 0.06 there (0.951 against OpenCV 0.889), which looks like a seam bonus.
- **S0 is otherwise a usable negative.** No release flags it: R2w4 vs S0 is 0.46 to 0.54. Its different warp does not matter, because warp size moves nothing (R2w vs R2w4 0.49 to 0.52). The face-only S0 copy is byte-identical to the face-only R2w copy.
- **Face-blanked S0 vs S4 at 0.50 is a construction check, not evidence.** The two images are identical once the face is blanked.
- **Rule disclosure.** One variant of my check ran a Gaussian low-pass on a difference map (analysis only, nothing written). Under rule 3 that number should not be used, and I have not quoted it.

What each release reads (OpenCV, our 512 frames, AUC-level platform agreement only):
- **SelfMAD reads a blend confined to the face.** Seam-matched S0 vs S4 is 0.889, far above the tone statistic (0.71) and the band baseline (excess +0.15 to +0.22). SelfMAD is trained on self-blends, so it may be reading the boundary of a blended patch rather than the blend itself. A swap-splice would decide (H-new-2).
- **MADation ViT-B/16 and ViT-L/14 read mostly the surround ghosting.** They drop from 0.98–0.99 unspliced to 0.64–0.75 spliced. The excess's upper bound is at most 0.08 (ViT-B/16's interval lies entirely below 0), and the residual is within reach of the seam tone (0.71) and the sharpness ratio (0.65–0.72). There is no evidence they read the face blend at all.
- **MixFaceNet-MAD reads mostly detail loss.** Softened warp-only vs morph is 0.58 and the spliced contrast 0.60.
- **ViT-B/16 also reads detail loss in part** (0.79 at 61 px).
- **ViT-L/14's "more than detail loss" (0.97 / 0.99) is not shown.** The softened warp-only image has no ghosting, but the native morph does. So that cell crosses softness with surround ghosting. The decisive cell is softened S0 or R2w4 against S4, which is an author item.

## Q2. Our heads

**Spliced positives move the reading toward the face, but not past one band-power number.**
- Spliced-only S-a: face-blanked drops from 0.99 to 0.759 (CLIP) and 0.884 (DINOv3); face-only rises by 0.08 to 0.09.
- Protocol plus spliced S-b: still reads the surround (face-blanked 0.939 / 0.999); face-only rises by 0.06 to 0.07.
- Every face-only excess is significantly negative. Best cases: S-a DINOv3 [-0.090, -0.019], S-b DINOv3 [-0.093, -0.024].
- Answer to the registered amendment-8 question: **no** for every head.

**What the baseline is.** "band5@224" is one high-frequency band-power number on the 224 px face-only copy, which is a detail-loss measure. It is the maximum of about 40 statistics, each with its sign chosen on the test hosts themselves (`pn1lib.py:300-318`). So it is optimistic, which makes "below it" a conservative bar.

**Is it the right bar?** It is right for "more than detail loss inside the face". It is the wrong bar for "reads the face":
- Full-frame heads scored on copies with 60% of the frame grey are scored outside their training distribution.
- PD1 shows the frozen features carry more. Heads refitted on face-only images reach 0.95 to 0.98 (post hoc).
- For location, use the fall when the face is blanked plus the absolute face-only AUC. For content, use the excess over a floor of seam tone, sharpness ratio and band5 together.

**S-a's native 0.946 is held-out accuracy on its own training task.** Some of it is reachable by the seam-tone cue, which is not in the 40 statistics (H-new-1).

**Transfer goes the wrong way.**
- Poisson set (H1, real face-spliced morphs): S-a and S-b CLIP 0.821 / 0.843 against plain A0 0.877 and protocol B0 0.888. DINOv3 0.775 / 0.854 against 0.850 / 0.842.
- Diffusion-autoencoder set: S-a two-person morph against reconstruction is 0.468 (CLIP) and 0.302 (DINOv3), below chance.
- Mirror-mix contrast is below 0.5 for every head: the heads read "two captures blended", not a second person.

## Q3. Bracketing

The test is uninformative. Native warp-only vs two-person morph and the 61 px warp-only copy vs morph are already at 0.998 to 0.999, so a share of 1.000 just restates those AUCs. The floor (0.911) was chosen on the test hosts. The 61.2 px copy is milder than blending for about 91% of hosts. Harder versions:
- (a) **Face-only bracket:** S4's face above S0's face and above its softened copy.
- (b) **Inverted subset:** only hosts where the softened warp-only image is softer than the morph by band5. About 17 hosts now, so it needs stronger softening (author).
- (c) **Margin:** the morph must beat max(R2w, R2w_61) by more than the host's own R0 to R0_61 shift.
- (d) **Fixed threshold:** the morph above τ_cam and both negatives below it.

## Q4. MAD22, protocol plus spliced on DINOv3 (2.0 / 3.0%)

Treat it as a lead, not a method:
- It is threshold-free on our frames.
- With 204 genuine photos, one photo is 0.49 points, so 2.0% is about 4 errors.
- It is the best of 8 heads × 2 cells, read on data that amendment 4 item 6 calls first-test.
- The head still reads the surround (face-blanked 0.999). The face-relocated S-a is worse (13.8%), so the gain is not face reading.
- H1 is unchanged (0.854 vs 0.842).

The more interesting number is the fixed-threshold gating miss: 7.8% against 37.1% for protocol B0. Storage is borderline (shift 0.28 SD against the 0.3 mark; 8.9% flagged at 61 px against the 10% mark). The 112.7 px and kernel marks are unread. Earlier reviews add that our frames may favour the landmark cells.

## Q5. Selection and multiplicity

- **Seeds are not replication.** Seeds 401 to 405 only set the inner folds. Four of the five S-b DINOv3 seeds give an identical 0.848. "Stable over seeds" means only that the chosen regularisation strength is stable. Data spread needs a resampling of training persons.
- **Many reads, picked on test data.** About 8 heads × 2 backbones × about 15 reads × 2 tools were read on the 191 test hosts and MAD22. If S-b or DINOv3 is now picked for LoRA because of MAD22 or the test ladder, the choice was guided by test data. State that, and decide on the development ladder (100 hosts) and the AF0 validation set.
- **Notebook 22:17** says "seam in both classes". Correct this (see below).
- The spliced arm itself was designed after reading the ladder (disclosed as a remedy experiment; acceptable).

## Q6. Spliced-positive LoRA arm (ViT-B/16, registered before any tier-1 score is opened)

- **Arms:**
  - S-b LoRA = manifest B + S4 (OpenCV) of the 124 training hosts as attacks, with S0 and S3 as negatives. This keeps the definition of the frozen S-b head.
  - Plus a volume control: B plus the same number of extra B rows.
  - Seeds 401 (named) and 402, on the same machine as B; stratified balance as in amendment 4.
- **Deciding reads (OpenCV only), development ladder first, test ladder read once:**
  - (i) Face-blanked R2w vs R4 lower than B's by at least 0.05.
  - (ii) Native S0 vs S4, with a lower bound of excess above 0 over a floor fitted on development hosts (seam tone + sharpness ratio + band5).
  - (iii) P-c, P-c2 and kernel marks.
  - (iv) P-g non-inferiority against B.
  - (v) H1 AUC not below B by more than 0.02.
- **Pass:** all of (i) to (v) on both seeds.
- **Kill:** (i) fails on both seeds, or H1 falls below B by more than 0.03, or the P-g upper bound is above +3 points.
- **Otherwise:** "inconclusive, no claim".
- **Cost:** about 3.5 A100-hours (0.87 each × 4).

## Corrected wording for the notebook

1. "Spliced morphs (blend only inside the face): with OpenCV the seam is equal in size but not in kind. A spliced morph carries a colour step that one simple number separates from the negative at about 0.71. With FaceMorpher the negative has almost no seam, and those reads are not seam-matched."
2. "Only SelfMAD reads a face-confined blend beyond simple cues (0.889 seam-matched), possibly as a blend boundary. The MADation CLIP releases read mainly surround ghosting; their spliced 0.64–0.75 is within reach of seam and sharpness cues. MixFaceNet-MAD reads mainly detail loss. ViT-L/14's 'more than detail loss' is not separated from ghosting."
3. "Spliced positives move frozen heads partly toward the face (face-blanked 0.99 to 0.76 / 0.88 for spliced-only). No head reads more inside the face than one band-power statistic (0.906, chosen on test, optimistic). Spliced heads do not improve on real face-spliced morphs (H1)."
4. "The bracketing share is saturated (1.000) and does not discriminate between heads."
5. "Protocol plus spliced on DINOv3, corrected MAD22 2.0 / 3.0%: best of 8 heads on first-test data. The head still reads the surround. A lead to re-test, not a method result. Seeds vary only the inner folds."

## New hypotheses

- **H-new-1, seam tone.**
  - Statement: part of the S0-vs-S4 separation is the colour step at the hull.
  - Prediction: a 3-statistic floor (tone, sharpness ratio, band5) reaches at least 0.80; inside tone-matched quintiles, S-a and the CLIP releases fall by at least 0.05.
  - Falsified if the drop is at most 0.02 and the floor is below 0.75.
  - Cost: 0 GPU, now.
- **H-new-2, boundary vs blend.**
  - Statement: SelfMAD reads the boundary of a blended patch, not the blend.
  - Test: a swap-splice made by pixel copy only: B's warped half inside the same hull, R2w4 outside. No blend, and twice S4's tone step. Diagnostic only, never trained on.
  - Prediction: SelfMAD scores the swap-splice at least as high as S4 (AUC S4 vs swap-splice at most 0.5).
  - Falsified if S4 vs swap-splice is at least 0.75 for SelfMAD. A head that reads the blend should give at least 0.75.
  - Cost: CPU minutes and about 0.3 GPU-hours. Needs a lead amendment. The halves exist for all 536 hosts.
- **H-new-3, under-use of features.**
  - Statement: the features carry a face blend signal beyond band power, but full-frame training spends the weight on the surround.
  - Prediction: a head trained on face-only copies of training hosts beats band5 on test face-only images with lower bound above 0; S-b does not.
  - Cost: CPU, plus at most 15 GPU-minutes of feature extraction.
- **H-new-4, ghosting inside "more than detail loss".**
  - Prediction: softened S0 or R2w4 vs S4 is at most 0.75 for the CLIP releases and at least 0.85 for SelfMAD.
  - Cost: author item (shrink path), then 0.3 GPU-hours.
- **H-new-5, the MAD22 gain reads the surround.**
  - Prediction: with the face blanked, S-b DINOv3's corrected-MAD22 EER stays within 2 points of native.
  - Second check: under training-person resampling, the EER interval overlaps B0's.
  - Blanking is a pixel replacement; about 0.2 GPU-hours.

## Next steps, ranked by information per GPU-hour

| # | Step | GPU-h | Decides | Approval |
|---|---|---|---|---|
| 1 | Seam-tone plus 3-statistic floor for S0 vs S4 (releases and heads); drop the FaceMorpher S0 reads [AR1, PN1] | 0 | H-new-1; wording items 1-2 | none, post hoc |
| 2 | Training-person resampling of the frozen heads, including MAD22 EER and τ_cam miss [PN1] | 0 | real spread; Q4 | none |
| 3 | Harder brackets (a), (c), (d) on existing images [PN1] | 0 | whether bracketing can discriminate | none |
| 4 | Face-only-trained heads [PN1] | at most 0.25 | H-new-3 | lead amendment |
| 5 | Register the spliced LoRA arm before tonight's eight fits are read [PN1] | 0 now | keeps the design free of test data | lead |
| 6 | Swap-splice diagnostic [AR1 / PN1] | 0.3 | H-new-2 | lead amendment |
| 7 | Face-blanked MAD22 and H1 reads [PN1] | 0.2 | H-new-5 | lead amendment |
| 8 | Spliced LoRA arm plus volume control, 2 seeds [PN1] | about 3.5 A100-h | whether the remedy holds under fine-tuning | lead |
| 9 | Softened splices and a stronger shrink | author | H-new-4; bracket (b) | author only |

## Risks to the story

Whether the network reads the face is still open. The face-relocated head transfers worse to real spliced morphs (H1) and to diffusion morphs. The best MAD22 number comes from a surround reader on our frames. Hedge in the paper: "reads that two captures were averaged, mostly where whole-frame tools ghost the surround".

## Files

- `/home/narolski/smad-next/experiments/AR1/splice_seam_pixels.csv`, `/home/narolski/smad-next/experiments/AR1/result.md`
- `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/README.md`, `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/splice/splice_summary.json`, `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/bracket/bracket.json`, `/home/narolski/smad-next/src/PN1/pn1lib.py`
- My check scripts: `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/splice/seam_mag.py`, `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/splice/s3_seam.py`, `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/splice/tone_step.py` (its low-pass line is the one disclosed under Q1).
