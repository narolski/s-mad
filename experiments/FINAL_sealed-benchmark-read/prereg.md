# Registration: the sealed MAD22 read of the frozen candidate (FINAL)

**Status: final text, v3.** It is registered by the commit that adds it, before any benchmark score of the frozen
networks exists. The read starts only on the lead's start word. Written 13 Nov 2026; `date` at writing: Fri Nov 13
06:58 PM CET 2026. Times are machine-clock times (NOTEBOOK, "18:46 machine clock (lead): CORRECTION OF TIMES").

- History: drafts v1 (71fa6e4) and v2 (e6003ac, 6691adc); pre-run review of v1:
  `experiments/reviews/PRERUN_FINAL_SEALED_READ_20261112.md`.
- What v3 keeps from the author's answers of 12 Nov: "Who runs the read: You!" (the lead starts it; the owner runs the
  reader; section 9), "Writing items: sure", and "only if we cannot propose SOTA" (no claim is pre-committed: the
  claim is whatever the rules below give).
- What v3 supersedes, and why, is listed in section 11.

## 1. The rulings this read rests on (verbatim)

1. **Freeze.** Author, about 18:27 by the machine clock: **"Ok, freeze the candidate and let's test it"**. The lead's
   question was: "Freeze the candidate by your own ruling, so the single sealed read on MAD22 and FRLL-Morphs can be
   prepared". The stated 18:28 is right to the minute.
2. **Scope.** Author, about 18:36 by the machine clock: **"Go with A READ NOW, improve later for MAD22, we need to know
   where we stand on this eval set."** The lead's messages gave this ruling as 19:25; NOTEBOOK records it as committed
   at 18:36:07. Option A of the lead's question was to read the frozen CLIP candidate now; the new arms are later work.
3. **Retrains.** Author, 13 Nov 08:30: "Retraining on MAD22 can IMHO be scheduled on WCSS/Athena and arrive when they
   arrive."

**Frozen, by author ruling (not by the registered freeze rule):**
- Arm Sb: protocol negatives plus face-spliced morphs with matched negatives; CLIP ViT-B/16 with LoRA; the registered
  recipe.
- The five fresh-seed networks, seeds 403-407, last checkpoints. Their tars are pinned in the C2P registration
  (2715e48) and in section 10.
- No other arm, seed or checkpoint. No ensemble. Every seed is reported.

**Scope set by the lead from ruling 2:**
- This read covers **corrected MAD22 only**, in all forms of section 3, for all five families, per family and as means.
- FRLL-Morphs, FEI gtest, MorDIFF, the six DiM families, H1 and the FRLL benign variants are **not scored and not in
  the pack**. They stay sealed for a later method.
- VAL-X, FST and A12SP are struck. They are never opened (hard rule).

## 2. Choices the lead registers under the author's go, each with its disclosure sentence

| # | Choice | Disclosure sentence (paper) |
|---|---|---|
| C1 | **Freeze.** No method met the registered freeze rule (FINAL section 1 as amended at 6691adc). The storage-test re-run (C2P-R) was not approved and was not run. The MS1 clause of that rule no longer applies: the author froze Sb himself. | "No method met the registered freeze rule. Its storage test on seeds 403-407 was first scored on a different GPU model and precision setting than training, which removed every plain-training control; a re-scoring on the training platform was not run. On two further independent seed blocks the test was 'inconclusive' for the candidate (3 of 5 and 2 of 4 seeds at the untrained size), each time because its genuine scores moved toward genuine, while its flag-rate rise stayed at most +4.5 points against +27 to +39 for plain training. The authors froze the candidate by their own decision on 13 Nov 2026, before any benchmark score of these networks existed. Its recipe had been chosen after benchmark scores of earlier seeds (401/402) were seen." |
| C2 | **Deciding measure.** EER per history-matched cell; AUC printed beside it. Printed as secondary: own-rule APCER and BPCER, and APCER and BPCER at a development threshold from FFHQ genuine photos, a pool never used in training. The training-source threshold τ_dev(i) is withdrawn as the decider and is not printed (reviewer finding F10: it flags 96-98% of unseen genuine photos). | "Before any benchmark score, the deciding measure was changed from error rates at a development threshold to EER on history-matched cells, because that threshold flagged 96-98% of genuine photos from an unseen source for every network." |
| C3 | **Labels.** MAD22 is labelled "seen during development": the 401/402 networks of the same recipe were scored on every MAD22 cell, and its genuine side is the 204 FRLL photos. It is reported in standard, history-matched and border-equalised forms. The history-matched column is labelled "aligned-frame history (our aligner plus history)" (CB1 review). | "MAD22 was scored with networks of the same recipe during development; its genuine side is the 204 FRLL photos; it is reported as seen during development. This read is a 'where we stand' read of the candidate frozen on 13 Nov 2026." |
| C4 | **Shortcut and specificity labels.** MAD22 FaceMorpher is "shortcut-saturated": AD4's morph-free ViT-B/16 reaches 0.0% EER in both its native and E7 cells, and ViT-L/14 reaches 0.0% native. No state-of-the-art sentence rests on it. The MIPGAN-I and MIPGAN-II cells carry "not shown to be morph-specific: the network flags one-photo GAN renders" (REVIEW_PR1_PART2). Their E7 pool equals the native genuine photos by construction. | as the labels |
| C5 | **Border-equalised form** (section 3.3). Constant-colour blanking is an approved image operation. | "A border-equalised form blanks the same black region into every image of both classes of a cell." |
| C6 | **Reference detector.** The best development statistic, noise_std_face. Its direction was fixed on development data (morphs lower; FFHQ landmark_combined AUC 0.886). It is printed beside the networks and is never the "best comparison". | as the label |
| C7 | **Retrains.** The 14 Nov 18:00 retrain cut-off (v2 section 4) is replaced by the author's rulings: retrains "arrive when they arrive". Retrain rows (AD5) and CB1 baselines are not part of this read. Any that arrive later are added in a separate table labelled "late addition, read by the same reader rules". They never change a registered verdict of this read. Other methods' rows are "as reported, not verified" (CB1 labels). | "Released detectors are scored by us; other methods' numbers are as reported, not verified." |
| C8 | **Second backbone (BB2).** It is not part of this read ("no other arm"). The v2 robustness-row clause is struck. | none |

## 3. Cells, forms and inputs

### 3.1 Cells
- **Morph families of corrected MAD22**: FaceMorpher (1,000 morphs), MIPGAN-I (1,000), MIPGAN-II (999), OpenCV (984)
  and Webmorph (500), 4,483 in total. Path: `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z`,
  checked against its PROCESSED_SHA256SUMS. These are the files the 401/402 networks and AD4 read.
- **Genuine pools**:
  - native: the 204 FRLL photos of 102 persons, codes _03 (neutral) and _08 (smiling);
  - E7: per family, the same photos shrunk to the family's median inter-eye distance and enlarged again
    (`resmatch`), 204 each.
- **Neutral-only variant** of every genuine pool (the 102 _03 photos, cue C1): EER printed beside every cell.
- **Means**:
  - `mean4`: the mean of the per-family EERs over the four families that are not shortcut-saturated (OpenCV,
    Webmorph, MIPGAN-I, MIPGAN-II);
  - `mean5`: the mean over all five families;
  - `mean2`: the mean over the two landmark families (OpenCV, Webmorph), secondary (section 4).

### 3.2 Forms
| Form | Our networks and the reference statistic (our 512-px aligned frames) | Released detectors (their own crop path, RS1) |
|---|---|---|
| S, standard | morphs against native genuine | raw morphs against raw genuine photos (`G22_raw`); aligned native (`G22_aln`) printed |
| H, history-matched: "aligned-frame history (our aligner plus history)" | morphs against the family's E7 pool | raw morphs against our aligned E7 frames through their crop (`E7aln22_<fam>`); for the best comparison also raw morphs against raw genuine photos (section 4, pre-run finding B1) |
| BE_S and BE_H, border-equalised | as S and H on the border-equalised copies (3.3) | MADation ViT-B/16 and ViT-L/14, MixFaceNet-MAD: identical to S and H. Their own crop of every MAD22 pool has under 0.01% black pixels: `rs1_border.csv` lines 2-6, 27-28, 35-39 give a mean black fraction of 0.0000 and a maximum of 0.0001. Black pixels occur in 26.5% of MIPGAN-I morph crops against 1% of genuine crops, at a maximum fraction of 0.0000. SelfMAD: "not available" (the border on its own preprocessing path is not measured) |

**Disclosure for the releases' path (pre-run finding B1).**
- For the releases, the history-matched form pairs raw JPEG morphs with our aligned PNG E7 genuine frames.
- Our aligner step alone moves a release's EER by −3.9 to +5.4 points on some cells (CB1 result, lines 230 and 236).
- Our E7 pool equals the native photos for MIPGAN-I and MIPGAN-II (204 of 204), and for 108 and 104 of 204 photos
  of OpenCV and Webmorph.
- Therefore, in every form, each release enters the best comparison twice: once with its registered genuine pool, and
  once with its raw genuine photos (G22_raw). The lower point EER is taken. This choice is conservative for us.
- The aligned-native rows (G22_aln) are printed beside them, with the aligner step.
- Paper sentence: "For the released detectors, morphs are the raw benchmark files and the history-matched genuine
  photos pass through our aligner; each release is compared at the better of its raw-genuine and aligned-history
  forms."

### 3.3 Border-equalised copies
For family f:
- **Mask.** mask_f is the union, over every image of the cell (f's morphs, f's E7 frames and the 204 native genuine
  frames), of each frame's largest exactly-black region (maximum over channels = 0, 8-connected) that touches the frame
  edge. This is the TT1 `build_border_ref.edge_mask` definition.
- **Blanking.** mask_f pixels are set to (0,0,0) in every image of the cell, both classes. Images are written as
  lossless PNG, and each is read back and checked.
- **Measured from pixels only, no score:**

  | Family | Mask share | Mask share in the central face box |
  |---|---|---|
  | FaceMorpher | 0.301 | 0.000 |
  | MIPGAN-I | 0.133 | 0.000 |
  | MIPGAN-II | 0.119 | 0.000 |
  | OpenCV | 0.000 | 0.000 |
  | Webmorph | 0.000 | 0.000 |

  The genuine frames carry no edge-black region. The central face box is rows 150-400, columns 128-384.
- **Empty masks.** For OpenCV and Webmorph the border-equalised form equals the unblanked form. It is printed with the
  label "no border in either class".

### 3.4 Thresholds (fixed now from development scores; `final_thresholds.json`, section 10)
- **Own rule:** logit > 0 for our networks; probability of morph > 0.5 for the releases (logit > 0 of their stored
  key).
- **τ_FFHQ:** the smallest score c with share(FFHQ genuine score > c) ≤ 5%.
  - Pool: the 2,000 FFHQ genuine development photos (pn1_eval.csv, fam ffhq, rung ffhq_bona_orig), never a training
    source.
  - Our networks use their stored fit-time scores: s403 −0.9736, s404 −0.1601, s405 −0.1863, s406 +0.0613,
    s407 −0.8872.
  - The releases use their existing RS1 own-crop scores of the same photos (FF_orig). In variant 1, 66 FFHQ photos are
    dropped by crop failures (n = 1,934). Variant 2 is printed. This affects secondary results only.
  - SelfMAD uses RS1's DGX own-preprocessing scores (n = 2,000).
- No threshold is taken from any benchmark.

## 4. Statistics

- **One metrics function**, `src/FINAL/final_metrics.py` (pinned), for every detector:
  - ROC at every distinct score;
  - ties counted half, through linear segments;
  - EER at FPR = FNR by linear interpolation;
  - BPCER@APCER 1/5/10/20% by interpolation;
  - AUC by Mann-Whitney with ties half;
  - flagged means score > threshold;
  - exact Clopper-Pearson 95% intervals for every rate.
- **Per cell, our networks**: every seed's value, the mean, the SD, the minimum and the maximum.
- **Intervals: a two-level bootstrap**, 2,000 replicates, `numpy.random.default_rng(20261121)`:
  - **Person level.** The persons are the 102 FRLL persons. In each replicate they are drawn as multinomial counts,
    the pigeonhole bootstrap of AD4/RS1. A genuine photo weighs its person's count. A morph weighs the product of its
    two contributors' counts.
  - **Seed level.** Each replicate also draws 5 seed indices with replacement, and our value is the mean over the
    drawn seeds.
  - **Pairing.** The same draws serve every detector, form and cell.
- **Best comparison** per cell, form and mean: the lowest point EER among the release candidates.
  - The releases are MADation ViT-B/16, MADation ViT-L/14 and MixFaceNet-MAD (RS1 crop variant 1), and SelfMAD (DGX own
    preprocessing) if its rows exist at the read.
  - Each release is a candidate twice: with its registered genuine pool, and with its raw genuine photos (3.2, B1).
  - The choice is made once, by point estimate, and is then held fixed in the replicates. This is disclosed: choosing
    the minimum separately in each replicate would favour the release further. Conversely, taking the minimum of up to
    8 candidates by point estimate and holding it fixed can inflate a "lost" verdict (winner's curse on the release
    side).
  - Printed only, never the best comparison: the morph-free networks (AD4 seed-mean EERs from its registered readings, ad4_reading_m3.md lines 48-57 and ad4_reading_m3l.md lines 51-60; not rescored), the reference statistic, crop variant 2 and the aligned-native release rows.
  - Each replicate's difference uses the same release with its own person-weighted EER.
- **Tests** on d = ours − best, in EER points. Each is one-sided at 0.025, with bootstrap p-values (1 + count)/(R + 1):
  - exceeded: p(d ≥ 0) ≤ 0.025 AND at least 4 of 5 seeds individually below the best's point EER;
  - lost: p(d ≤ 0) ≤ 0.025;
  - matched (non-inferior): p(d ≥ +1.0 point) ≤ 0.025;
  - otherwise: "comparable, not separated".
  - The order of precedence is exceeded, then lost (printed "within the 1-point margin" when non-inferiority also
    holds), then matched, then comparable.
- **Absolute intervals.**
  - Every detector's EER in every cell carries a person-bootstrap 95% percentile interval.
  - Our seed mean carries the two-level interval.
- **Expected precision.** With 102 persons, the paired interval of d is expected to be about ±2-3 points. So
  "matched" needs a point advantage of roughly 1.5-2 points, and "comparable, not separated" is the expected verdict
  when the detectors are close. This is stated before the read so that a "comparable" verdict is read as expected
  precision, not as a failure.
- **Landmark-only mean** (`mean2`: OpenCV and Webmorph), pre-run finding M4.
  - It is secondary, with its own verdict.
  - If its H-form verdict differs from the primary verdict, the primary sentence says so. Half of `mean4` is the two
    MIPGAN cells, which are labelled "not shown to be morph-specific".
- **Multiplicity:**
  - One primary endpoint: **the H form, mean4**. It has no adjustment.
  - Per-family verdicts in every form are computed with Holm's step-down across the five families, separately for
    each test.
  - Everything other than the primary endpoint is secondary or descriptive. The 95% percentile interval of d is
    printed everywhere.

## 5. Predictions, stated before the read (lead and strategist)

- **F1.** "It trails MADation ViT-B/16 on the standard form for landmark cells."
  - Tested on FaceMorpher, OpenCV and Webmorph, form S, against MADation ViT-B/16 (variant 1).
  - "Trails" on a cell means p(d ≤ 0) ≤ 0.025.
  - F1 holds if it trails on at least 2 of the 3 cells; otherwise it is falsified.
- **F2.** "The GAN cells look good by render response."
  - F2 holds if our seed-mean EER is ≤ 10% on both MIPGAN cells (form S); otherwise it is falsified.
  - Either way, the cells carry the label of C4.
- **F3 (strategist).** The border-equalised form raises our EER by ≤ 2 points.
  - Δ = BE_H − H, seed mean, two-level interval, per family with a non-empty mask.
  - F3 holds if Δ ≤ +2.0 points on all three such families; otherwise it is falsified.
  - If Δ > 3 points on a family, that family's rows carry a **border caveat**.

## 6. What the paper says under each outcome (primary endpoint; the labels of C3 and C4 always attached)

| Outcome | Sentence |
|---|---|
| exceeded | "On corrected MAD22 (seen during development; genuine side the 204 FRLL photos), against genuine photos with aligned-frame history (our aligner plus history), the frozen network's mean EER over OpenCV, Webmorph, MIPGAN-I and MIPGAN-II (FaceMorpher is solvable without morphs and excluded) is lower than that of the best released detector (X) by D points [lo, hi], with k of 5 seeds individually lower." |
| matched | "... is within one point of the best released detector (X): difference D points [lo, hi] (non-inferiority margin +1.0 point)." |
| comparable | "... is not separated from the best released detector (X): difference D points [lo, hi]." |
| lost | "... trails the best released detector (X) by D points [lo, hi]" (plus ", within the one-point margin" where it applies). |
| gate failed or job not finished | "No read: the platform gate failed or the job did not finish; no benchmark row was scored or read." It is reported to the lead. There is no second platform and no changed tolerance. |

- **Always attached:**
  - "Frozen by the authors' decision on 13 Nov 2026; the registered freeze rule did not freeze any method."
  - The release-path sentence of section 3.2: "For the released detectors, morphs are the raw benchmark files and the
    history-matched genuine photos pass through our aligner; each release is compared at the better of its
    raw-genuine and aligned-history forms."
  - The MIPGAN label and the FaceMorpher label.
- **Secondary sentences** (S, BE_S, BE_H; mean4), each with its verdict, labelled descriptive.
- **The landmark-only sentence** (`mean2`, H form). If its verdict differs from the primary verdict, the primary
  sentence must say so.
- **The border sentence**, with the caveat families.
- **F1-F3** reported as held or falsified.
- **No sentence may say** "state of the art", "generalises", "shortcut-free" or "detects morphing", whatever the
  outcome.
- The best wording available is "matches / is lower than the released detectors on corrected MAD22 (seen during
  development)".

## 7. Exposure statement (part of this registration, with `PN1_protocol-network-first-tests/BENCHMARK_EXPOSURE.md`)

- **MAD22 was seen in development.** Every corrected-MAD22 cell was scored for the 401/402 networks of this recipe,
  and choices 1, 7 and 8 of BENCHMARK_EXPOSURE rest on it.
- **The frozen networks are clean; the recipe is not.** The networks 403-407 have never been scored on MAD22 or any
  benchmark.
- **The lead is not blind.** He endorsed the Sb refit after H1 was seen. The owner who prepared this package has seen
  no benchmark score of these networks.
- **Unavoidable exposure created by this read.** MAD22's genuine side is the 204 FRLL photos, so after the read the
  frozen networks' scores on those photos exist. The FRLL-Morphs morphs stay unscored. After this read, any later
  method's MAD22 numbers are "seen during development" (they already carry that label through 401/402).
- **Released detectors.** Every MAD22 cell was read for them in the RS1/CB1 audits. Their rows here are those
  existing scores (section 8), except SelfMAD.

## 8. Comparison rows

- **Existing rows.** MADation ViT-B/16, MADation ViT-L/14 and MixFaceNet-MAD use their existing RS1 score files: the
  rented RTX 3090 production runs, own crop, variants 1 and 2. They are copied unchanged into
  `release_scores_existing.npz` by `src/FINAL/extract_release_scores.py`. Every row and form those files hold is
  used; nothing is rescored.
- **SelfMAD.** RS1 scored SelfMAD on FRLL only, so its MAD22 rows are missing. They are scored after this commit, once,
  on SelfMAD's RS1 platform: the DGX, RS1 `score.py --mode own`, beside the running IDistill job, with GPU memory
  checked first.
  - Inputs: the same 5,911 files the other releases read.
  - Output: sealed until the read. Its sha256 is recorded in the README and in a short pin commit before the start.
  - If it cannot run before the start, SelfMAD's cells are printed "pending" and SelfMAD is not in the comparison set
    of this read.
- **Reference statistic.** The best development statistic is computed the same way: after this commit, on the DGX
  CPU, output sealed, pinned before the start. Absent means "pending".
- **Platforms.** No release is rescored on the A100 lease. Their own-crop path is not reproducible across GPU models
  (RS1: boxes differ on about 1 image in 10). Each cell takes all its rows from one run.

## 9. The one read: platform, gate, order, failure handling

- **Machine.** One fresh A100-PCIE-40GB lease, rented by the lead.
  - The model must be exactly the stored run's device, A100-PCIE-40GB. The job checks it.
  - **Why this platform, and the alternative not used.** The lead reported to the FINAL owner on 13 Nov (message received about 20:02 by the machine
    clock) that Athena's A100-SXM4 (container smad_torch221_cu121_v1.sif, plgrid-now) reproduced the TT1-FS gate
    scores of all five frozen networks byte for byte (NE1, Athena job 3550470, registration 9ef5884). This read
    nevertheless uses the rented A100-PCIE-40GB path, because it is the path that was built, mock-tested end to end
    and pre-run checked.
  - Athena may become the platform only by a dated amendment before the start. The amendment needs its own runner
    (container, Slurm, IO in $TMPDIR), its own stand-in test, and the same byte-identity gate inside the same job.
  - Image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, with its own venv on the system site packages.
  - Pins asserted before scoring: torch 2.2.1, CUDA 12.1, cuDNN 8902, timm 1.0.27, huggingface_hub 0.36.2,
    safetensors 0.8.0, numpy 1.26.4, pyyaml 6.0.3, Pillow 10.2.0.
  - Recorded: GPU UUID, driver, the TF32 and SDP flags, pip freeze.
  - A busy or second GPU aborts the job.
- **Scorer.** `src/PN1/rescore.py` runs unchanged through `src/TT1/rescore_tf32.py`. TF32 is on for matmul and cuDNN,
  as `pn1_score.py` did for the stored scores and thresholds. It runs float32, in eval mode, batch 64, in the pinned
  manifest order. This path reproduced every fresh-seed network bit for bit on pn1fs (TT1-FS, 15 of 15 on 19,797
  rows). The same rescore.py path, with TF32 off, was bit-identical on se1d (TT1-M).
- **Gate dry run, before the start** (pre-run improvement 2).
  - On the rented lease, `drive_final.sh dryrun` runs the same job with FINAL_DRYRUN=1. It runs steps 1-4 only:
    checks, venv and the gate on development rows. The benchmark manifest is never read.
  - It runs once per host (marker STARTED_DRYRUN). Its result is fetched and verified (`pulldry`).
  - The read can be started only after DRYRUN_PASSED on that lease.
  - If the dry run fails, the read is not started, and the result is reported to the lead. Any further dry run, on the
    same machine type, is the lead's decision and is recorded. No benchmark row is involved in any dry run.
  - The tolerance stays byte identity. A tolerance fallback is an author decision and is not adopted here.
- **The one-start marker** (pre-run finding M2). It is created on the host after every check that scores nothing
  (pins, GPU model, venv, versions, extraction) and immediately before the first gate score.
  - A failure before it (no score made) uses up nothing.
  - On the driver side, the local lock is taken at `start`. A start that fails before any score keeps the lock; the
    lead's written word, recorded in the README, is needed to remove it.
- **Gate, before any benchmark row.**
  - All five networks score the gate rows. The rows are every 3rd whole 64-row batch (batch index ≡ 0 mod 3) of the
    FS1 development evaluation manifest `pn1_eval.csv` (sha256 f0f29f22…): 104 batches, the last partial batch
    (21 rows) included, 6,613 rows in total. Batch composition and order equal the stored scoring run's.
  - Coverage, genuine and attack rows of every development family:

    | Family | Genuine | Attack |
    |---|---|---|
    | af0 | 393 | 55 |
    | ffhq | 1,344 | 320 |
    | ffhq_lcomb | 661 | 320 |
    | ladder | 1,695 | 353 |
    | splice | 985 | 487 |

  - **Criterion:** byte identity (float32) with each network's stored fit-time `scores_eval.npz` on every row, for
    every network.
  - **On failure:** if any network fails, the job stops and no benchmark row is scored. The result is reported to the
    lead. There is no second platform and no changed tolerance. A further attempt needs a new dated amendment and the
    author's word.
  - **Batch-subset check.** On the DGX GB10, scoring 10 whole batches out of a 30-batch stretch reproduced the full
    run's logits byte for byte (640 FFHQ development rows, Sb s403). This tests the method only.
- **Benchmark rows.** Then, in the same job, all 9,930 rows of `final_bench.csv`, per network in config order:
  - 5,707 MAD22 frames;
  - 4,223 border-equalised copies.
- **One start.**
  - The remote job refuses to run if `STARTED` exists on the host (created with noclobber).
  - The driver creates the local lock `/mnt/t7/smad_next/FINAL/START_LOCK_FINAL_mad22` (atomic mkdir) before the
    start. No script removes it.
  - A second start is refused by both.
- **Crash after the gate.** The result tar is fetched and verified, and only `rc`, `gate.txt` and `calls.log` are read
  (they hold no score). The lead decides.
  - A re-run is the same pack and config on a fresh A100 PCIe lease, once.
  - It needs the lead's written word, recorded in the README, to remove the lock by hand.
  - No partial score is opened.
- **After the job.**
  - The driver fetches the result tar and logs, verifies sha256, and makes a second copy.
  - The owner runs `final_read.py` once. Its marker directory makes a second read impossible.
  - The reader first verifies every pin and parses every input, then takes the marker (pre-run finding M1).
  - A reader crash that writes no output may be re-run once, unchanged, with the lead's word. The traceback is kept.
  - Non-finite scores mean "no read", never re-run.
  - The result review follows (results-reviewer).
  - No network is trained, and no recipe, threshold or label changes, because of this read. Later work is labelled
    post-read.
- **Order of work.** This commit; then the SelfMAD and reference-statistic runs, sealed, with their pin commit; then
  the lead's start word; then the job; then the read.

## 10. Pins (sha256)

The machine-readable copy is `src/FINAL/final_pins.json`. The table below is generated by `src/FINAL/make_pins.py`
at registration.

<!-- PINS_BEGIN -->
| Item | Path | sha256 |
|---|---|---|
| pack | `/mnt/t7/smad_next/FINAL/FINAL_mad22_pack.tar` | `5ec63472d9c489aea93bfdcdd0929b4651ef9c5a27e9c90801d7c54c3eee43c1` |
| pack SHA256SUMS (inside the pack) | `final/SHA256SUMS` | `bf48c489e99f35bde4f765db75a0744f15178d7312325c1a643d9593f609323f` |
| gate manifest (inside the pack) | `final/data/manifests/final_gate.csv` | `2799d2f99dcd8b122a92f110c38954932f6c1d1989bc3aece0b92aa34dce6663` |
| benchmark manifest (inside the pack) | `final/data/manifests/final_bench.csv` | `48335f869046d23251c46d000d4a35bd5b7e6d18cc8d858bd8d7eac56cdccbd0` |
| FS1 evaluation manifest (gate source) | `data/manifests/pn1_eval.csv` | `f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045` |
| fresh-seed pack (gate source) | `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar` | `96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004` |
| MAD22 PROCESSED_SHA256SUMS | `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/PROCESSED_SHA256SUMS` | `73ff92fd29a49a9d4b7d1a1bc7aa8b0e43919100ab7ca5873f3f66f228c493c2` |
| network PN1_Sb_s403 | `/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s403.tar` | `8dec83b880b7bac28db4b6217bc10b58eb78dc65d699734614cf57ae6b444fde` |
| network PN1_Sb_s404 | `/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s404.tar` | `de67068959bc277b3850c6d8e13f0e88d8fa1e273dccad53665abcfa4827752c` |
| network PN1_Sb_s405 | `/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s405.tar` | `3a3a53fd98bdd09eab9a15ec14fdd1ed46b2fc8f95f520e6bd4e4bab1e4265ea` |
| network PN1_Sb_s406 | `/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s406.tar` | `d2cf5faa31330ce82dc9734760f08513640c0a908072fae02447109abc039291` |
| network PN1_Sb_s407 | `/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s407.tar` | `865c04552df4367b3311dda007405ecb7dc8ee0f98d390d1b1baff51b24da595` |
| scorer rescore.py | `rescore.py` | `6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e` |
| scorer rescore_tf32.py | `rescore_tf32.py` | `0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5` |
| scorer base_weights_vit_base_patch16_clip_224.openai.safetensors | `base_weights_vit_base_patch16_clip_224.openai.safetensors` | `4b8699299b1e8997753c64b052ba32031449d5d853f55a039148560ee02b820f` |
| src/FINAL/final_config.json | `/home/narolski/smad-next/src/FINAL/final_config.json` | `79bd4e3e446232133a4265254b519d1430a3774e6b8aca266202c7ac406817af` |
| src/FINAL/build_pack.py | `/home/narolski/smad-next/src/FINAL/build_pack.py` | `b80b4fcdec7bc1368561b5f74c5cf2bb175c2fd9879a01578025e66b78e1fcec` |
| src/FINAL/remote_final.sh | `/home/narolski/smad-next/src/FINAL/remote_final.sh` | `54925f22f8856fd7e5101d5487b69bd8480becdde1b809afef97045dc506384d` |
| src/FINAL/drive_final.sh | `/home/narolski/smad-next/src/FINAL/drive_final.sh` | `8fb39b8a085e1464927c5e2996554f184b7a9a644da0bf88894892fb4b4f432f` |
| src/FINAL/gate_check_final.py | `/home/narolski/smad-next/src/FINAL/gate_check_final.py` | `ac2e5f578faf9622b784558b0a280856c2c8d3654c2e3c2d661707731ec7ef24` |
| src/FINAL/final_metrics.py | `/home/narolski/smad-next/src/FINAL/final_metrics.py` | `9c202f9749e5c1d5f7b7fa856d6cb589511f1415ee1a554044bba39b537a5370` |
| src/FINAL/final_read.py | `/home/narolski/smad-next/src/FINAL/final_read.py` | `f8ab8e55217a400396a7611bfe1432fdaa4408c6d51d60808ae3fa408a049df2` |
| src/FINAL/mock_test.py | `/home/narolski/smad-next/src/FINAL/mock_test.py` | `7648a3632e8f6f89441b256dcc5cf67c2482f57ed86af9448cd9926cf1026a6e` |
| src/FINAL/make_standin.py | `/home/narolski/smad-next/src/FINAL/make_standin.py` | `f91e7503974fbb9cc7038320e61e85443fd0185f840e5f15ef85a15eb87baf24` |
| src/FINAL/thresholds.py | `/home/narolski/smad-next/src/FINAL/thresholds.py` | `36d0474ca3512e26f860c92e729f06c747b11e1d67d98d35b8f0fa34260470d6` |
| src/FINAL/extract_release_scores.py | `/home/narolski/smad-next/src/FINAL/extract_release_scores.py` | `9e2c9de985e722357fb8ce113ca0be2e6085371b4aa976bea25b413881862c99` |
| src/FINAL/selfmad_mad22.py | `/home/narolski/smad-next/src/FINAL/selfmad_mad22.py` | `696d1a7aaf92dea0f20084d86e94b208963db62e721e861bc3f8084c749477c2` |
| src/FINAL/beststat_mad22.py | `/home/narolski/smad-next/src/FINAL/beststat_mad22.py` | `094eed87e478cff7440294ae5397aabbab35ad5ecba14104251286d0632b015d` |
| src/FINAL/make_pins.py | `/home/narolski/smad-next/src/FINAL/make_pins.py` | `fca462b1c41c6f99a923b89cf0c372fbc7d44a9f65dcd1c7f9432862a940e556` |
| thresholds (committed) | `/home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read/final_thresholds.json` | `0293c3adad2487114fded4555fd235a6ad9946c993381ea1e3f702e6851983d4` |
| released detectors, existing rows | `/mnt/t7/smad_next/FINAL/release_scores_existing.npz` | `dba3acdad6cea543fde2b323a2118a2eb6a32b6d15cc2f0de1d0f304749e963b` |
| AF0 cues_all.py (reference statistic) | `/home/narolski/smad-next/src/AF0/cues_all.py` | `1ab50f3098e9eac6fcdfeb7a08cb6b02613d728f87aa24a4a396509f41cdcc9f` |
| RS1 score.py (SelfMAD scorer) | `/home/narolski/smad-next/src/RS1/score.py` | `56bb124444980f630d676758d25aaefe5b3485874c8aea174e0bd74d3c597cc8` |
| RS1 athena_manifest.csv (SelfMAD inputs) | `/mnt/t7/smad_next/RS1/athena/athena_manifest.csv` | `11cef1c5b285fba6d50f7828a2d2fb8fe11e0b653facbbe631409572949f1b7e` |
| rs1_border.csv (release crop border) | `/home/narolski/smad-next/experiments/RS1_own-crop-rescore/rs1_border.csv` | `0b3bad62e83a04515ab9fe6a315e706b72f58734c0da666edebd328710905fa5` |

Pack size 5,756,416,000 bytes. `final_pins.json` itself is pinned by the commit.
<!-- PINS_END -->

## 11. Superseded parts of v2 (kept in git history)

- Section 1, the freeze rule and its MS1 clause: the author froze Sb by ruling (C1).
- Section 2, the confirmatory sets (FEI gtest, VAL-X, FST, A12SP, MorDIFF and DiM morphs) and the reported sets
  FRLL-Morphs and H1: ruling 2 limits this read to MAD22. The rest stay sealed. VAL-X, FST and A12SP are struck.
- Section 3, the τ_dev(i) endpoint (M2, M4) and its combined (mean APCER + BPCER)/2: replaced by C2.
- Section 4, the cut-off of 14 Nov 18:00 and the AD5/CB1 rows: replaced by C7.
- Section 7, "Reuse: no existing RS1 or AD5 benchmark score is reused": replaced by section 8. The releases' own-crop
  path cannot be re-run on the A100 with matching boxes.
- Section 7, the platform gate (M7): replaced by the byte-identity gate of section 9. The H100/MS1 parts no longer
  apply.
- Section 7, "a failed gate may be repeated once": replaced by section 9 (no second platform).
- Section 8, the outcome table: replaced by section 6.
- Section 10 item 9 (proposal F10): adopted as C2 by the lead under the author's go.
