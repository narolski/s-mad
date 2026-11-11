# Protocol network, first tests (PN1)

Registration written 11 Nov 2026, 18:50 to 19:06 CET (machine clock), by the PN1 owner (Claude agent), before any score or
statistic of this experiment was computed. Before writing it the owner ran only: the person split (`src/PN1/split.py`,
lists only), list writing (`src/PN1/lists.py`), an 8-image test of the extraction script, and the start of the
softened development-photo build (`src/PN1/soften_dev.py`, an image build, no statistic). Sources of every rule: the
lead's task message (11 Nov, about 18:45), `ideas/CONSOLIDATED_v3.md` sections 3, 4 and 6, the vetted cards
(`ideas/round3/sota_vetting.md` 2.6 to 2.8; `ideas/round3/nuisance_vetting.md` "NU1r"; `ideas/round3/paired_vetting.md`
2.3, 2.7, 2.8; `literature/crossfield/diffusion_check.md` proposal 4) and the coordinator's addition of 19:00 (items
1 to 5 below, section 9). Pass and kill numbers are the cards' numbers; where this page changes one, it is tighter,
and the change is marked "tighter".

## 0. Terms

- Rungs of the landmark ladder (AR1), per host H: **R0** camera photo; **R0_61 / R0_112** the same photo stored small
  (shrunk to 61.2 or 112.7 px between the eyes and enlarged back by the registered path); **R2w** warp-only image
  toward the mean shape of H and H's other photo; **R2w4** warp-only image toward the two-person mean shape (the
  geometry-matched negative of the two-person morph, new rung, coordinator 19:00); **R2w_61 / R2w_112** stored copies
  of R2w; **R3** same-person morph; **R3m** mirror self-morph; **R4** two-person morph (H with another person's photo);
  **R4_61 / R4_112, R3_61 / R3_112** stored copies of the morphs (to be built by the alpha-field probe owner, AF0).
  Engines: **OpenCV-style** (`scripts/78_tool_morph.py`; decides every read) and **FaceMorpher** (descriptive, never
  in training).
- Alpha-field probe (AF0) images: **photo**; **zero** = warp-only image toward the two-person mean shape of a pair
  (equal to the engine's warped host); **u50** = the engine's two-person morph at 0.5 (equal to the unchanged engine,
  verified by AF0); **halfA / halfB** = the morph's own two warped halves; **_61** = stored copy at 61.2 px.
- Classes (`14_CLASS_DEFINITIONS.md`, lead's working rule): **genuine** = camera photo and its stored copies
  (admissible processing); **attack** = two-person morph and its stored copies; **single-subject** = warp-only images,
  halves, same-person and mirror morphs and their stored copies. In training, single-subject images are
  **negatives** (label 0), never "genuine"; in reporting they go into the single-subject table and never into a
  genuine flag rate or into a threshold.
- Flag rate = share of genuine images above the threshold; miss = share of attacks at or below it; placement = share of
  single-subject images above it. AUC is signed, the attack (or the single-subject image, where so stated) positive.

## 1. Hypothesis (plain words)

A network trained by the registered MADation recipe (CLIP with LoRA), with manifest B, whose negatives contain
everything a morph has been through except the mixing (camera photos, warp-only images, the morph's own warped
halves, and 61.2 px stored copies of photos and halves) and whose attacks are two-person morphs and their 61.2 px
copies, keeps the morph signal (two-person morph against warp-only image; border-free benchmark cells) and does not
react to storage history and softness at one fixed threshold, while the same recipe with manifest A (camera photos
against two-person morphs) does react.

## 2. Persons (fixed by `src/PN1/split.py`, run 18:58; outputs `split/ladder_split.csv`, `split/af0_split.csv`,
`split/split_summary.json` with sha256)

- V (validation-reserved persons) = `smadcvpr/prep_train.is_val(subject)` (imported unchanged). V persons are in no
  PN1 training set, no development pool and no test read: 8 ladder hosts, 67 AF0 persons.
- Test ladder T: `random.Random(401).sample(sorted 536 hosts, 200)`; identical to the AF0 softened-host list
  (`/mnt/t7/smad_next/AF0/lists/ar1soft_src.csv`, checked by the script). Test reads use the 191 hosts h of T with h and
  its partner B(h) outside V (`test_read = 1`).
- Development ladder D: `random.Random(402).sample(...)`, 100 hosts drawn among the partners of test hosts that are not
  in T or V and whose own partner is not in V. Reason: fewer persons are then lost to training. Consequence (stated):
  each development host's other photo appears in one test host's two-person morph; the development ladder is used for
  thresholds and descriptive rows only.
- X = T ∪ B(T) ∪ D ∪ B(D) ∪ V (everyone who appears in a test or development ladder image). Ladder training hosts L:
  the 156 hosts outside X (130 FRGC, 26 colorFERET). Their R0 and R2w (OpenCV) may be negatives; their R4 (OpenCV) and its
  two warped halves are used only for the 124 hosts whose partner is also outside X.
- AF0 persons (disjoint from all 536 ladder persons, checked): 481 training-split persons and 115 validation-split
  persons outside V. AF0 training images are used only if every person in them is a kept training person; AF0
  validation images only as development pools.
- FRLL, FFHQ, FEI persons never enter training (FRLL and CASIA/H1 are evaluation pools here; FFHQ and FEI unused).

## 3. Tier 0 (tonight, DGX CPU, frozen features)

- Features: mean of the patch tokens (final norm, prefix tokens dropped) of CLIP ViT-L/14 at 224 and DINOv3 ViT-L/16
  at 512, from the AF0 caches `/mnt/t7/smad_next/AF0/feat/{clip224,dinov3_512}/` (float16 tokens, mean in float32);
  missing sets extracted by `src/PN1/featmean.py` (AF0's `feat.py` imported unchanged; same statistic). GPU: at most
  0.5 hours on the DGX in one process; DINOv3 sets that do not fit go into the Athena smoke job with an equivalence
  check on 64 images (head score difference at most 0.01 on every one, else those reads are marked "platform-mixed").
- Head: StandardScaler + LogisticRegression (L2, lbfgs, class_weight balanced, max_iter 5,000); C from {0.001, 0.01,
  0.1, 1, 10} by 5-fold inner cross-validation grouped by the first person of each image (AUC); refit on all
  training rows. Seeds 401 to 405 set the inner folds; seed 401 is the named head, the others are printed as spread.
- Arm A0 (photos against morphs): genuine = AF0 training photos; attack = AF0 training u50 morphs.
- Arm B0 (protocol): negatives = AF0 training photos, zero images, both halves of every u50 pair, and the 61.2 px copies
  of photos and halves that exist in the AF0 softened training list (`/mnt/t7/smad_next/AF0/img/soft/fm61/`,
  alternating strengths, built by AF0); attack = AF0 training u50 morphs and their existing 61.2 px copies.
- 0.5 rule for a head: predicted probability above 0.5.

## 4. Tier 1 (Athena, decisive)

- Four networks: manifests A and B, seeds 401 (named) and 402. The training script is the unchanged `train.py` of the
  AD4 pack (sha256 `cbb2cbd1…`, `common.py` `b5d42a99…`) with the morph-free networks (AD4) ViT-B/16 call:
  `--arch a12_clip_vitb16_madation --regime d0 --split train90 --lofo none --lr 3.33e-06 --seed S --res 224 --workers 7
  --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps=6250 --ft=lora --lora-targets=qv
  --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw --wd=0.05 --head-lr=3.33e-05
  --bs=256 --aug=flip --sched=const --clip-grad=5 --pos-weight=1`. Last checkpoint, no selection. Manifest rows carry
  `source=smdd` so that regime d0 keeps every row once (the convention of A47 I-3 and AD4; it changes no code path
  other than row selection).
- Manifest A: genuine = AF0 training photos + R0 of the 156 ladder training hosts; attack = AF0 training u50 + R4
  (OpenCV) of the 124 hosts.
- Manifest B: A, plus negatives = AF0 training zero images, both halves of every AF0 training u50 pair, R2w (OpenCV) of
  the 156 hosts, the two warped halves of R4 of the 124 hosts (`/mnt/t7/smad_next/SM1/img/ar1h/*_hA.png`, `*_hB.png`,
  built by the SMDD rebuild owner with the unchanged engine; the morphs there equal AR1's R4 pixel for pixel), and the
  existing 61.2 px copies of AF0 training photos and halves; attack = A's attacks plus the existing 61.2 px copies of
  AF0 training u50.
- Not in any training manifest: 112.7 px copies; any ladder stored copy (the genuine-side ladder copies do not exist
  for training hosts, and adding only the morph copies would make "stored small" a morph cue in that subset);
  FaceMorpher images; R2w4, R3, R3m; AF0 u25, grad, bump fields; anything of T, D, V, FRLL, CASIA.
- Class balance: in each manifest the smaller class's rows are repeated by a seeded rule (each row ⌊r⌋ or ⌈r⌉ times,
  r = n_large / n_small, `numpy.random.default_rng(20261111)`) so that both labels have equal row counts; within a class
  the natural counts are kept. (The recipe fixes `--pos-weight=1` and the prior sampler; balance keeps the 0.5 rule
  comparable between A and B.)
- Scores: no flip averaging (`score_noTTA`, the card's rule); the flip average is stored and printed only.
- Pack: one tar (code and ViT-B/16 weights from the AD4 pack, hash-checked; images; manifests; `SHA256SUMS`), sha256
  beside it. Exact image counts per class and source go to `manifests_summary.json` when the pack is built; the rules
  above bind, the counts do not.

## 5. Thresholds (every head and network; both printed in every fixed-threshold table)

- τ_0.5: the network's own rule, P(morph) above 0.5.
- τ_dev: the lowest t at which every protected development genuine pool has at most 5% of its images above t
  (t = max over pools of each pool's threshold; per pool: the smallest score t with share(score > t) ≤ 0.05, the
  fixed-threshold re-read's rule, EV1). Protected pools (all with 60 px or more between the eyes): development-ladder
  R0 (100), R0_61, R0_112; AF0 validation photos (126 of persons outside V), their 61.2 and 112.7 px copies. Stored
  copies of development photos are built by PN1 with the AF0 path unchanged (`src/PN1/soften_dev.py`). Single-subject
  pools never set a threshold. Printed beside it, descriptive: τ_dev,native (R0 and AF0 validation photos only) and the
  pool that binds τ_dev.
- Every table prints, at the same threshold, flag rate (genuine pools), placement (single-subject pools) and miss
  (attack pools), with exact Clopper-Pearson 95% intervals.

## 6. Reads (test ladder T_read, 191 hosts; OpenCV-style engine decides, FaceMorpher printed)

Intervals: person bootstrap over test hosts (B = 2,000, seed 20261111), paired by host when both sides come from the
same hosts; benchmark cells: CP intervals for rates, stratified image bootstrap (B = 1,000) for EER.

- (a) Identity step: AUC(R2w vs R4) (card) and AUC(R2w4 vs R4) (geometry-matched, coordinator). Excess = head AUC minus
  the best of the 27 simple statistics (the 26 `cue_floor` statistics plus PNG bytes; folded AUC on the same images;
  the maximum is re-taken in every bootstrap draw, tighter than choosing it once).
- (b) Crossed softness: AUC(R0_61 vs R4) (lead's wording) and AUC(R2w_61 vs R4) (card's wording), same hosts.
- (c) Storage shift: mean paired logit shift R0 → R0_61 in units of the standard deviation of the R0 logits of the test
  hosts; share of R0_61 flagged at τ_0.5 and at τ_dev. The same for R0_112 (printed separately) and for R2w → R2w_61
  (single-subject, printed).
- (d) Poisson set (H1, 598 morphs against 598 photos, CASIA source): AUC.
- (e) Corrected MAD22 OpenCV and Webmorph: AUC and EER native (against the 204 genuine photos) and history-matched
  (against that family's E7 pool), miss at both thresholds. FaceMorpher, MIPGAN-I and MIPGAN-II printed (FaceMorpher
  is no evidence of morph detection without blanking, `CONSOLIDATED_v3.md` 3.8). Tier 0 reads AF0's subsample
  `bench_s`; tier 1 the full cells.
- (f) Fixed-rule table (NU1r adapted): at τ_0.5 and τ_dev, flag rate on FRLL genuine photos (all; neutral-only printed),
  the FRLL-Morphs E7 pools (AMSL, FaceMorpher, OpenCV, Webmorph), the corrected MAD22 E7 pools, the FRLL benign
  variants blur1 and resample50 (left-out kernels) and jpeg90 / jpeg70 / jpeg50 (printed as uncontrolled: no JPEG may be
  trained on), test-ladder R0, R0_61, R0_112; miss on test R4 (both engines), R4_61, R4_112 (when built), the
  FRLL-Morphs landmark cells (printed, never gating: our aligner leaves a border there), the MAD22 cells, H1.
- (g) 2 × 2 softness by blend (paired card): (g1) R2w vs R4, (g2) R2w_61 vs R4, (g3) R2w vs R4_61, (g4) R2w_112 vs
  R4_112 and R2w_61 vs R4_61.
- (h) Single-subject table: placement of R2w, R2w4, R2w_61, R2w_112, R3, R3m (both engines), R3_61 / R3_112 (when
  built), AF0 validation zero images and halves, at both thresholds; AUC(R4 vs R3).
- (i) Certificate and (j) matched-subsample test: section 9.
- Every read is also printed on the development ladder where its images exist (descriptive).

## 7. Pass, kill, comparison

Tier 0 decides nothing in favour (card 2.8). Printed for A0 and B0, both feature sets, seed 401 and spread:
- K0 (card): B0 with (b) AUC(R2w_61 vs R4) below 0.60 on CLIP: "the frozen features hold no softness-free signal";
  tier 1 then runs labelled "low expectation". Also read with R0_61.
- 2 × 2 marks (paired card) for B0: pass min(g1, g2, g3) ≥ 0.85 with every lower bound above 0.75 and g4 ≥ 0.70; kill
  min(g1, g2, g3) < 0.75 on both feature sets (label "frozen protocol head reads softness"; no stop).
- NU1r marks: NU-a A0 flags more than 10% of some left-out genuine pool (non-JPEG) at τ_0.5 or τ_dev (a violation
  exists); NU-b B0 flags at most 5% (point) with CP upper bound at most 10% of every left-out non-JPEG genuine pool of
  150 images or more (tighter: the card's size limit was 200); NU-d B0 misses at most 20% of R4_61 at both thresholds.

Tier 1, each manifest-B network (seeds 401 and 402); "B passes" needs every mark on both seeds:
- P-a: AUC(R2w vs R4) ≥ 0.95 and AUC(R2w4 vs R4) ≥ 0.95 (tighter: R2w4 added), each with excess ≥ 0.03 and bootstrap
  lower bound of the excess above 0.
- P-b: AUC(R0_61 vs R4) ≥ 0.90 and AUC(R2w_61 vs R4) ≥ 0.90 (tighter: both).
- P-c: shift R0 → R0_61 at most 0.3 standard deviations, and at most 10% of R0_61 flagged at τ_0.5 and at τ_dev
  (tighter: both thresholds).
- P-d: H1 AUC ≥ 0.85 (measured bar 0.833).
- P-e (tighter, added for the claim "keeps the signal on border-free cells"): history-matched EER on corrected MAD22
  OpenCV and on Webmorph at most 3.0 points above the manifest-A network of the same seed.
- P-f (tighter, from NU1r d, the softness-window confound): at most 20% of R4_61 missed at τ_0.5 and at τ_dev. If the
  copies are not built by the time the networks are scored, P-f is "not read" and B can at most "pass P-a to P-e".
- Kill (card, tighter): on both B seeds, AUC(R2w_61 vs R4) < 0.75, or the lower bound of the excess in P-a is at or
  below 0 for R2w or for R2w4. Then the network reads softness at 224 and the landmark claim stops.
- Comparison ("where A does not"): A has a violation if, on both A seeds, the shift R0 → R0_61 exceeds 0.3 standard
  deviations, or more than 10% of R0_61 or of a left-out non-JPEG genuine pool is flagged at τ_0.5. Without an A
  violation the result reads "the protocol is not shown to be needed for this recipe on these data" (NU1r rule a), and
  no "removes" sentence is written. Headline row, printed: family-mean miss at τ_dev over the gating attack cells (test
  R4 OpenCV, MAD22 OpenCV, MAD22 Webmorph, H1), A against B per seed.
- Loss rule (card): if B passes P-a and P-b and fails P-c, the equality term is the next step (outside PN1).

## 8. Gating and non-gating cells

Gate only on: the test ladder, corrected MAD22 OpenCV and Webmorph, the Poisson set (H1). FRLL-Morphs cells on our
aligned frames are printed and never gate a decision. JPEG rows are uncontrolled.

## 9. Coordinator's addition (19:00): certificate and matched-subsample test

- (i) Certificate. Named cues per image, measured on the image as the network sees it (the training loader's own
  step `common.ImageItems.load` of the AD4 pack: whole frame, PIL bilinear to 224; for DINOv3 at 512, descriptive):
  Laplacian variance of the luma at kernel sizes 1, 3 and 5 (`cv2.Laplacian`); mean log power in eight equal-width
  radial bands of the Hann-windowed luma spectrum (1/224 to 0.5 cycles per pixel); border fraction (share of pixels
  with every channel ≤ 2, the `cue_floor` definition); history flag (native, 112.7, 61.2 px); engine (none,
  OpenCV-style, FaceMorpher, other benchmark tool); photo pool (AF0 colorFERET, AF0 FRGC, ladder colorFERET, ladder
  FRGC, or the benchmark source); partner reuse (number of attack images in the set sharing that partner; the partner
  identity itself cannot transfer across person-disjoint folds). Classifiers: logistic regression on standardised
  cues with one-hot categories, and a histogram gradient-boosted tree model (scikit-learn defaults, seed 401); the
  certificate is the larger of the two out-of-fold AUCs (tighter than either). Folds: 5, person-disjoint, built on
  the connected components of the person graph (both persons of a morph and of its halves always in the same fold).
  Printed for manifest A, manifest B, tier-0 arms A0 and B0, and for every evaluation cell read (within-cell
  cross-validation; with and without the categorical cues; on benchmark cells a file or construction attribute is
  expected to give values near 1.0, and that line is the audit, not a property of the method).
- (j) Matched-subsample test (tier 0, CLIP features, logistic heads as section 3). Pool: the B0 training pool.
  Balanced (nuisance) cues: history flag, engine, photo pool, border fraction (two bins: 0, above 0). Reported only,
  never balanced: the three Laplacian variances and the eight bands (softness is caused by blending; balancing it
  inside the label would remove true evidence), and partner reuse. Matching: coarsened exact matching on the strata of
  the balanced cues; in each stratum both classes are cut to the smaller count by a seeded draw (rng 20261111); strata
  with one class only are dropped. The nuisance-cue classifier of (i), fitted on the balanced cues only, is then refit
  on the matched pool. Random control: a seeded random subsample of the full pool with the same class counts.
  Thresholds: each head's own 5% false alarms on unprocessed development camera photos (development-ladder R0 and AF0
  validation photos). Reads: nuisance-cue AUC and full-cue AUC before and after matching; share kept; change in flag
  rate from test R0 to R0_61 (and to R0_112) at that threshold; AUC(R4 vs R3); EER(R4 vs R0), OpenCV-style engine.
  Kill (card): (k1) the nuisance-cue AUC cannot be brought to 0.60 or below while keeping at least 30% of the pool;
  (k2) the matched head's flag-rate change is not below the random head's by at least half of the full-pool change;
  (k3) EER(R4 vs R0) of the matched head exceeds the random head's by more than 2 points. If the full-pool change is
  at or below 0, k2 reads "no flag-rate change to remove".
- Not done (stated): the card's second certificate by a strong reader (a probe on frozen patch features of the
  matched pool, and a morph-free network refitted on it).

## 10. Guards

Simple-statistic floor in (a); history pools on both sides (stored copies of genuine photos and of morphs); identity
disjointness by section 2; label balance by section 4; the A-violation requirement of section 7; the certificate and
the random-subsample control of section 9; FaceMorpher and FRLL-Morphs never gate; no ensembles, no score fusion, one
network per result, last checkpoint, no seed picking.

## 11. Stop rule and budget

- DGX: at most 2 processes at nice 10 plus at most 0.5 GPU-hours of extraction in one process.
- Athena (account plgrestorearc-gpu-a100, `-C memfs`, `--mem=120G`, 1 A100): one smoke job of at most 1 GPU-hour after
  an 8-image DGX test; the four fits only after the lead's GO, estimated 1.0 to 1.5 GPU-hours each with scoring; cap 150
  GPU-hours. A failed task is rerun once, unchanged, never because of its values.
- No image operation outside the allowed list; no JPEG, blur or resample branch on training images.

## 12. Command (tested on 8 images)

To be filled per step with the exact command line and its 8-image test (README section 11).

## 13. Pre-run review

The lead's independent review of this page before the four fits. Date and verdict: pending.

## 14. Result

Pending. Numbers go to `result.md` and the README; the lead draws conclusions.

## Amendment 1 (11 Nov 19:20 CET, before any score or statistic of PN1): JPEG arm, manifest C

Source: author's decision of 19:13 (`07_DECISIONS_NEEDED.md`), relayed by the coordinator. The JPEG branch of the
registered function `degrade` in `/home/narolski/mambamorph-code/smadcvpr/prep_eval.py` (sha256 `374408ab…`,
operations jpeg90 and jpeg70) may be run unchanged on training images (imported and called, never copied or edited).
blur1, resample50 and chip stay forbidden on training images.

1. Verification before use (`src/PN1/jpeg_c.py verify`): the registered evaluation branch (raw FRLL photo →
   `degrade(img, "jpeg70")` → `align` → PNG) must reproduce the existing evaluation file
   `smadcvpr_data/eval/frllm/frll_bona/<id>_jpeg70.png` pixel for pixel and byte for byte (both printed) on 4 files.
   If it does not, manifest C is not built and the lead is told.
2. Manifest C = manifest B plus JPEG copies. Copies are made on the training image itself (the 512 frame that B trains
   on): `degrade(frame, "jpeg90")` or `degrade(frame, "jpeg70")`, stored as lossless PNG; no re-alignment. Selection:
   within every source kind of B (AF0 photos, zero images, halves, ladder R0, R2w, ladder halves, 61.2 px copies of
   each kind, AF0 u50, ladder R4, 61.2 px u50), 50% of the unique images are drawn (`numpy.random.default_rng(20261119)`,
   the same rate in every kind and in both classes); half of the drawn images (seeded) get a jpeg90 copy, the other
   half a jpeg70 copy. A copy keeps the label of its source. Class balance then by the rule of section 4.
   jpeg50 is never in training (held-out test condition).
3. Tier 1 becomes six networks: A, B, C at seeds 401 (named) and 402, if the lead's pre-run review agrees; GO before
   any fit as before.
4. Reads added for every network and head (A, B, C; A0, B0 at tier 0, which have no JPEG arm): flag rate of FRLL genuine
   photos under jpeg90, jpeg70 and jpeg50 (existing evaluation files, `frll_e5` list), at τ_0.5 and τ_dev, each with the
   miss rate of the gating attack cells at the same threshold. Corrected-MAD22 genuine photos under JPEG: no such
   evaluation files exist (`/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/` holds `native` and
   `e7` only, checked 19:18); they are built only if the lead says so, with the registered evaluation branch (raw file →
   `degrade` → `align`), and are otherwise reported as "not available".
5. Marks for C (descriptive comparison; no new pass mark is invented): C is read with every tier-1 mark of section 7
   (P-a to P-f) exactly as B; in addition printed: jpeg50 and jpeg70 flag rates of FRLL photos for A, B, C at both
   thresholds with the misses beside them. The JPEG rows stop being "uncontrolled" for C only (C trains on jpeg90 and
   jpeg70; jpeg50 is its left-out quality); for A and B they stay uncontrolled.
6. Certificate (section 9 (i)) for manifest C as well; history flag extended with jpeg90 / jpeg70.
