Reviewer: results-reviewer (Opus), 12 Nov 2026, read-only, development data only. Report as returned, unedited.

**Post-result review: PN1 amendment 14, the development read on FFHQ landmark_combined** (repo /home/narolski/smad-next, commit 5717375). I worked read-only, on development data only. I did not open or score any benchmark, valx, FST or A12SP file. My scripts are in /tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/a14rev/ (recompute.py, floor.py, paired.py, cues.py). They read only the PN1_A14 tar contents, the HN2 tars, pn1_a14.csv and cues/a14_lcomb.npz.

## 1. Verdict
The registered reading is right and every headline number reproduces. The gate is credible. The conclusions need qualifying in three places:
- **The paired-drop sentence is a scale artefact.** "Sb loses the least" is not true in scale-free terms. Every arm, Sb included, still relies on the surround.
- **The floor framing is too strict and too loose at once.** Too strict: Sb's ranking is almost independent of the floor statistic, so "not shown beyond simple statistics" undersells it. Too loose: the set carries a non-morph processing cue (about 0.79 outside the face), and 27 simple statistics combined reach 0.948, above every network.
- **Sb is selection-tainted.** The two seeds are the ones on which Sb was picked after H1 had been seen.

Frozen contrast 1 is still informative as a comparison between arms. The extra reads in §4 must be committed before the first fresh-seed tar is pulled. The first tar is expected around 11:50, and it was 10:33 when I checked.

## 2. Findings (most severe first)

**F1 (major): the paired complete-minus-combined table cannot rank surround reliance in logits.** Evidence: result.md:227-230; a14.json `paired_complete_minus_combined`.
- I reproduced every mean, median and share exactly.
- But the spread of genuine scores differs by arm. SD of logits on the combined history-matched genuine pool: Sb 1.23 / 1.31, B 2.52 / 1.90, C 2.35 / 1.54, A 3.02 / 2.92.
- In genuine-SD units the drops are:

| Arm | 401 | 402 |
|---|---|---|
| A | 0.29 | 0.75 |
| B | 0.95 | 2.07 |
| Bn | 0.86 | 2.29 |
| C | 1.03 | 2.49 |
| Sb | 1.31 | 1.07 |
| Bv | 0.97 | 2.26 |

- Ordinally (scale-free), the share of pairs scored higher on the complete morph is Sb 0.958 / 0.964, B 0.953 / 0.983, A 0.70 / 0.84.
- The scale-free arm difference is the AUC loss from complete to combined: Sb −0.107 / −0.085, B −0.240 / −0.279. This only restates HN8, because all complete AUCs are 0.994 to 0.999, except A (0.935 / 0.971).

Rewrite for line 230: "Every network, Sb included, ranks the whole-frame morph above the face-only splice of the same pair for 95 to 99% of pairs (A 70 / 84%). Mean logit drops are not comparable across arms (genuine SD 1.2 to 3.0). Scale-free, Sb loses 0.09 to 0.11 AUC from complete to combined, B, Bn, C and Bv 0.24 to 0.28. Surround reliance is reduced in degree, not removed." This also matches Sb's registered amendment-10 kill: read (i) failed.

**F2 (major): the floor is partly a processing cue, and a 27-cue combination beats every network.** Post hoc, development data, computed by me:
- noise_std_face reaches 0.886 with morphs lower in noise. Some of this is genuine blending: averaging two faces smooths the face.
- But noise_std_border, which is outside the blended face, separates at 0.786; noise_std reaches 0.862.
- The surround of a combined morph is a real contributor image. So this cue is processing history: the generator used an unknown resize kernel, while the genuine pool went through INTER_AREA. The ffhqm README notes exactly this kernel residual and calls the set "unfit for evaluation".
- A 5-fold cross-validated logistic regression on all 27 statistics reaches 0.948. That is above Sb (0.887 / 0.909), though it is fitted on the set itself, so it is not a fair rival.

Consequence: whatever FS1 shows, the claim is limited to "on this development set". The floor comparison should be read together with the decorrelation reads in F3.

**F3 (major, an under-claim): Sb's ranking is close to orthogonal to the floor statistic.** Post hoc, on 401 / 402:

| Read | Sb 401 | Sb 402 | B 401 | B 402 |
|---|---|---|---|---|
| Within-class Spearman with noise_std_face (morphs; genuine) | −0.08; −0.03 | −0.09; −0.08 | −0.08; −0.11 | 0.00; −0.03 |
| AUC inside floor deciles (pair-weighted) | 0.879 | 0.901 | 0.708 | 0.699 |
| Floor-matched pair AUC (nearest genuine within 0.1 SD of the statistic, 998 morphs) | 0.877 | 0.890 | 0.712 | 0.682 |
| Cross-validated LR, floor + logit (floor alone 0.886) | 0.954 | 0.959 | 0.904 | 0.901 |
| Cross-validated LR, 27 cues + logit (27 cues alone 0.948) | 0.975 | 0.979 | 0.955 | 0.954 |

- Sb − B inside floor strata is +0.171 / +0.202, no smaller than the raw gap.
- Sb adds about 0.07 AUC to the floor statistic and about 0.03 to all 27 cues. B adds about 0.017 / 0.009 to the floor and about 0.006 to the 27 cues.
- Sb's within-class correlation with the outside-face noise is wrong-signed for that cue (genuine +0.14 to +0.19), so Sb is not reading the kernel cue either.

So "not shown beyond simple statistics" should become: "Sb does not exceed the best single statistic's AUC, but its ranking is not that statistic."

**F4 (minor): the gate is credible, and its scope is narrow.**
- The rescored files are byte-identical: same sha256 prefixes (ab2f4b33… for A_s401, f7b033d9… for B_s402) and the same zip-member CRCs.
- numpy writes zip timestamps fixed at 1980, so byte identity is possible without copying.
- The pack holds no score file (I checked the tar listing: 0 npz). rescore.py recomputes the logits from last_trainable.pt.
- So inference is bitwise deterministic across A100 SXM4-40, SXM4-80 and PCIe-40 with this stack, and the 12 networks in the pack carry the original weights.
- It says nothing about training. Backward-pass atomics and loader order can differ between runs. HN9, the replicate A seed 401, is the only measure of that.
- For FS1, all fresh seeds run on one PCIe GPU, so the arm contrasts carry no platform confound. Comparisons with 401 / 402 mix training platform and must stay printed only.

**F5 (minor): the selection caveat is missing from the verdict line.** "HN8 supported" holds on the two seeds on which Sb was chosen after H1 was seen (BENCHMARK_EXPOSURE choice 2). Mitigation worth stating: no landmark_combined value was known when either rule was frozen. Add "(first seeds; Sb selected on these seeds after H1 was read)".

**F6 (minor): small wording errors.**
- result.md:223 "0.13 to 0.20 below the floor": those are the lower bounds. The point AUCs are 0.108 to 0.175 below 0.886.
- result.md:224 "same AUCs to the third decimal": B 401 is 0.7537 against 0.7549 aligned-only, so write "within 0.002".
- Add the point gaps Sb − floor: +0.001 (401) and +0.024 (402).

**F7 (minor): the HN2b label carries no information about magnitude.** The rule returns "calibration shift" whenever within-source AUC is at least 0.90 (hn2_read.py:28-33). Sb flags the fewest FFHQ genuine photos of all 12 networks (5.9 / 7.0%). Add: "The label does not mean Sb's threshold shifts more; Sb has the lowest own-rule flags of the 12 networks."

**F8 (minor): HN7's axis is noisy within one training regime.** Face-only AUC is Bn 401 0.905 against B 401 0.840, although Bn is a subsample of B. "Inconclusive" is right. Without Sb the correlation is −0.12, so face-only sensitivity on the OpenCV ladder does not predict the landmark_combined read.

**What reproduced exactly:**
- All 12 HN8 AUCs, misses and flags.
- Sb − B +0.1332 / +0.1938 and Sb − A +0.1088 / +0.1634.
- The floor: noise_std_face 0.8856; floor file sha 714cb73d… matches the commit.
- The gate deltas (0.0).
- All paired means, medians and shares.
- The registered rules are applied as written (a14_read.py:233-250 against prereg Text 14 and amendment 14).
- I did not re-run the bootstrap intervals.

## 3. Question 3: what contrast 1 can claim, and printed reads to register now

Contrast 1 still tells us something. Both arms are scored on the same images, so the floor and the processing cue are the same for B and Sb. Sb − B ≥ 0.05 is therefore a valid comparison between arms. What it cannot carry on its own is "reads the face splice".

On fresh seeds the most likely outcome is "replicated, floor not exceeded": the seed-401 point gap over the floor is +0.001. The registered wording is "Higher AUC than B, but not shown beyond simple statistics". It may be followed only by the printed sentence that the reads below license.

Ready-to-register text:

> **FS1 printed reads R1–R6 (registered at the commit that adds this section; before any fresh-seed tar is pulled; frozen contrasts v4 untouched; print only, no verdict, no seed may be dropped or chosen on them).** Disclosure: R1–R5 were computed post hoc on seeds 401/402 by the post-result review of amendment 14 (values quoted there), so the definitions were chosen knowing those values. Data: the 3,000 landmark_combined images and cues file `a14_lcomb.npz` (sha 714cb73d…), development only.
> - R1 floor-stratified AUC: strata = deciles of noise_std_face over the 3,000 images (edges computed once from the cues file and committed in this section); AUC within each stratum, weighted by morph×genuine pairs; per network; Sb − B per seed; 2,000 bootstraps of images within class with fixed edges, `default_rng(20261119)`.
> - R2 within-class Spearman of the logit with noise_std_face and with noise_std_border, morphs and genuine separately.
> - R3 incremental AUC: 5-fold stratified CV (`StratifiedKFold(5, shuffle=True, random_state=0)`), standardised logistic regression (C = 1, max_iter 2000); AUC of out-of-fold scores for (i) noise_std_face, (ii) all 27 cues, each alone and with the network logit added; print increments and Sb's increment minus B's.
> - R4 floor-matched pair AUC: each morph against the nearest genuine image on noise_std_face within 0.1 SD (with replacement).
> - R5 the processing cue: AUC of noise_std_border printed with every contrast-1 number.
> - R6 scale-free surround reliance: AUC(landmark_complete orig vs resmatch genuine) − AUC(combined vs history-matched genuine), and the share of pairs higher on the complete morph, per arm; the mean logit drop is printed with the genuine SD beside it.
> - Pre-stated wording if contrast 1 replicates and the floor is not exceeded: if R1 Sb − B ≥ +0.05 on the same seeds that meet contrast 1, R2 |ρ| ≤ 0.2 for Sb on every read seed, and R3 Sb increment over 27 cues > B's on ≥ 4 of 5 seeds, the printed sentence is: "Sb's gain over B on this development set is not explained by the best single simple statistic or by the 27 statistics combined; Sb does not exceed the best statistic's own AUC, and still reads the surround (R6)." Otherwise: "The gain is not separated from simple statistics." Never "reads the face splice"; never a benchmark or generalisation claim (the set's README calls it unfit for evaluation and it carries a processing cue, R5).

## 4. Question 5: honest status of "protocol negatives plus spliced positives" (Sb)

What it does show, on two selection-tainted seeds and development data only:
- Large gains on FFHQ landmark_combined (+0.13 / +0.19 over B), at the level of the best single statistic and nearly independent of it (F3).
- Lowest genuine flags at its own threshold: FFHQ native 5.9 / 7.0%, history-matched 6.7 / 9.6%.
- On contrast 2's read (computed by me, printed only), the share of persons whose logit rises under storage is Sb 0.160 / 0.286, against B 0.443 / 0.372 and A 0.778 / 0.720. So Sb would pass the storage mark on these seeds.

What it does not show:
- It still reads the surround (F1).
- Its registered amendment-10 kill stands.
- No clean-benchmark evidence exists.

Status: the lead candidate pending FS1. The paper may say nothing beyond development data until the sealed final read.

## 5. Question 6: remedies for threshold transfer (development only)

- **Temperature or Platt scaling: drop it.**
  - Why it cannot help: thresholds are quantiles of a genuine pool (τ_cam is the 5% point on camera photos), and a monotone map leaves the flagged set unchanged. This is a zero-GPU argument.
  - What could help instead: an *unbounded* head. The head is bounded at about ±3.87 and camera photos pile up at −3.67 (result.md:85-88). Removing the bound changes the optimum, not just the scale.
  - Novelty is low, and so is my prior that it helps.
- **Equality (consistency) term: the most novel option.**
  - What it is: a penalty pulling a genuine photo and its stored-small or warp-only copy to the same logit. It is the step the PN1 loss rule already names (§7: pass P-a and P-b, fail P-c → equality term).
  - What it needs: existing pairs only (R0 with R0_61 / R0_112, R2w), so no new image is built and no resampling code is written.
  - Expected effect: very likely to cut the storage reaction; moderately likely to cut cross-source flags.
- **Multi-source genuine training: the most likely to fix cross-source flags.** It is standard domain generalisation, so novelty is low. New genuine sources must be aligned, and alignment is a warp, so this is an author item. The development held-out source must stay FFHQ.

Development marks for any remedy, against B and Sb at the same seeds on the same GPU type:
- own-rule FFHQ native genuine flags at most half of B's;
- FFHQ flags at τ_cam below 50% (now 95 to 98%);
- the storage share at most 0.25;
- landmark_combined and landmark_complete AUC at least B − 0.02;
- the development-ladder P-c′ mark.

Cost: about 1.3 A100-hours per fit (69 min on SXM4, PCIe a little slower), so 3 seeds ≈ 4 A100-hours ≈ 1.8 USD.

## 6. New hypotheses

- **H-new-1: Sb's gain is a face-interior signal complementary to the floor.**
  - Prediction: on 403–407, R1 Sb − B ≥ +0.05 on ≥ 4 of 5 seeds, R2 |ρ| ≤ 0.2, and R3 Sb's increment over the 27 cues ≥ +0.02 and above B's.
  - Falsified if: R1 Sb − B < 0.05 on ≥ 2 seeds, or |ρ| > 0.3.
  - Cost: 0 GPU. Timing: register now.
- **H-new-2: spliced positives remove the storage reaction beyond the protocol alone.**
  - Prediction: the contrast-2 share for Sb is at most B's − 0.05 on ≥ 4 of 5 seeds (printed).
  - Falsified if: this holds on ≤ 1 seed.
  - Cost: 0 GPU.
- **H-new-3: the remaining surround reliance comes from the whole-frame morph positives.**
  - Prediction: an arm with spliced positives plus protocol negatives but no whole-frame morphs moves the complete-higher share toward ≤ 0.75 and keeps landmark_combined AUC ≥ Sb − 0.03.
  - Falsified if: the share stays ≥ 0.9.
  - Cost: about 4 A100-hours. Timing: 13 to 14 Nov, after registration and pre-run review.
- **H-new-4: the equality term fixes threshold transfer.**
  - Prediction: it halves the own-rule FFHQ genuine flags against B (≥ 2 of 3 seeds) at landmark_combined AUC ≥ B − 0.02.
  - Falsified if: flags stay within ±20% of B's.
  - Cost: about 4 A100-hours. Timing: 13 to 14 Nov.

## 7. Next experiments (ranked by information per GPU-hour)

| # | Experiment | A100-h | When | What it decides | Approval needed |
|---|---|---|---|---|---|
| 1 | Register R1–R6 (§3) | 0 | before the first fresh tar (~11:50) | interpretability of contrast 1 | owner and lead; amendment commit |
| 2 | Commit the post hoc 401/402 table (F1–F3, storage shares) | 0 | now | text corrections | none (label it post hoc) |
| 3 | Simple-statistic baseline trained like the networks: 27-cue LR fitted on the training ladder, scored on landmark_combined (CPU, cues27.py) | 0 | today | whether "beyond simple statistics" holds under fair training | registration |
| 4 | Equality-term arm, seeds 403–405, on the FS1 GPU type | ~4 (≈1.8 USD) | 13 Nov | H-new-4; method candidate | author (budget, new arm), pre-run review |
| 5 | Splice-only-positives arm | ~4 | 13 to 14 Nov | H-new-3 | author, pre-run review |
| 6 | Unbounded head | ~4 | only if #4 cannot run | saturation story | author |
| 7 | Multi-source genuine training | ~4 plus author preparation | after 14 Nov, unless images already exist | cross-source flags | author (alignment) |

## 8. Risks to the story
- **Contrast 1 versus the floor:** it will very likely replicate with the floor not exceeded. Without R1–R6, the strongest result of FS1 reads as "not beyond simple statistics".
- **Limits of the set:** a processing cue (0.786) and its own README make it unusable for any generalisation claim.
- **Contrast 2:** A must still fail as the positive control, and Sb could make the mark trivially easy.
- **Platform:** 401/402 against fresh seeds mixes training platform. Keep the two printed separately.
- **Benchmarks:** none until the sealed final read. The only clean sets left are MorDIFF, DiM, FEI and the sealed sets.

## 9. Text corrections to result.md
- **Line 205:** "byte-identical (scorer bitwise deterministic across A100 SXM4-40/80 and PCIe-40 with this stack; says nothing about training determinism, see HN9)".
- **Lines 221-223:** "…lower bound −0.017 / +0.006 (point gaps +0.001 / +0.024)…; other networks' point AUCs are 0.11–0.17 below the floor. Post hoc: noise_std_border separates at 0.786 (a processing cue outside the blended face); 27 cues combined (cross-validated) 0.948."
- **Line 224:** "within 0.002".
- **Line 218:** "supported (first seeds; Sb selected on them after H1 was read)".
- **Line 230:** replace with the F1 rewrite.
- **Line 237:** append the F7 sentence.

