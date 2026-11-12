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

## Amendment 2 (11 Nov 19:26 CET, before any score or statistic): encoding of "partner identity" in the certificate

Section 9 (i) said "partner reuse = number of attack images in the set sharing that partner". Written that way the cue
is 0 for every negative and at least 1 for every attack, i.e. the label itself. Replaced by **person frequency**: for
every image, the largest number of images in the same set that contain one of its persons (this is the cue that would
expose SMDD's five recurring partners, and it applies to both classes). Nothing else changes.

## Amendment 3 (11 Nov 19:52 CET, operational, before any Athena job of PN1)

- Software on Athena (coordinator 19:28, `ATHENA.md` "Container image"): every PN1 job runs `python` inside
  `/net/pr2/projects/plgrid/plggrestoration/smad-next/containers/smad_torch221_cu121_v1.sif` (sha256
  `fedeff10a26d14edad624fffc048fc197509618ba5012519c47699dd6419649f`; python 3.10.13, torch 2.2.1 + CUDA 12.1,
  timm 1.0.27, numpy 1.26.4, pillow 10.2.0, safetensors 0.8.0) through `apptainer exec --nv`. The training script and
  recipe are unchanged; the 8-image DGX test ran the same `run.sh` with the host Python (the image is x86).
- Account (author 19:48): `-A plgmultivision-gpu-a100` for the smoke job and the fits (section 11 named
  plgrestorearc-gpu-a100); one A100, `-C memfs`, `--mem=120G`, 8 CPUs, as before.
- JPEG call verified (amendment 1, item 1): 4 of 4 FRLL jpeg70 evaluation files reproduced pixel for pixel and byte for
  byte (`jpeg_verify.json`).

## Amendment 4 (11 Nov 20:05 CET; the lead's "amendment 3"): fixes from the independent pre-run review

Disclosure. The tier-0 tables (CLIP heads A0 and B0) were computed by the owner at 19:42 to 19:53, read by the owner and
reported to the lead at about 19:53, before the pre-run review arrived. The review
(`experiments/reviews/PRERUN_PN1_20261111.md`, verdict GO WITH FIXES) was written by a reviewer who had not opened any
score file or tier-0 result; its fixes come from counting manifest rows. Those first tier-0 tables are provisional:
they are kept under new names (`tier0_v1_provisional/`, `tier0_v1_provisional_tables.md`, `tier0_v1_provisional_key.csv`)
and are recomputed after the fixes. The ladder hosts were also read by the landmark ladder (AR1) and the alpha-field
probe (AF0) while PN1 was designed. Pack building had started and was stopped at 20:00 before completion; no pack of
the old manifests exists. Below, decisions of the lead (numbers F1 to F11 refer to the review).

1. F1, F2 (stratified balance). In A, B, Bn and C, and in the tier-0 arms, the class balance of section 4 is applied
   inside each stratum of database (FRGC, colorFERET) by storage history (native, 61.2 px; for C also jpeg90 and jpeg70,
   crossed with size), by seeded repetition of the smaller class (each row ⌊r⌋ or ⌈r⌉ times, rng 20261111 + stratum
   index). No new image.
2. F3 (storage marks). The primary fixed threshold for every mark is now τ_cam = 5% false alarms on development camera
   photos only (development-ladder R0 and AF0 validation photos; the larger of the two pool thresholds), beside τ_0.5.
   τ_dev of section 5 (camera photos plus their stored copies) is printed only. Sensitivity row: τ_V from AF0
   validation photos only (F11). P-c becomes: shift R0 → R0_61 ≤ 0.3 SD and ≤ 10% of R0_61 flagged at τ_0.5 and at
   τ_cam. New mark P-c2 (sizes and kernels never trained): shift R0 → R0_112 ≤ 0.3 SD and ≤ 10% of R0_112 flagged at
   τ_0.5 and τ_cam; at most 10% flagged at both thresholds on FRLL blur1, FRLL resample50 and the E7 pools whose strength
   is not 61.2 px (FRLL-Morphs AMSL, FaceMorpher, OpenCV, Webmorph E7; corrected MAD22 OpenCV and Webmorph E7).
   Registered reading: B flat at 61.2 px but shifting at 112.7 px = "the trained size was memorised"; if A does not
   shift at 112.7 px either, that read is "uninformative".
3. F4 (data volume). New arm Bn: a seeded draw from B (rng 20261121), within kinds in proportion to B's kind counts, of
   A's unique counts (674 negatives, 852 attacks), then the stratified balance; seeds 401 and 402. Reading: Bn close to
   B = the protocol; Bn close to A = data volume. Printed for every network: mean logit of training rows minus mean logit
   of held-out images of the same kind (AF0 validation photo, zero, halves, u50; development-ladder R0, R2w, R4; their
   61.2 px copies where held-out copies exist).
4. F5 (manifest C). C is labelled a small-data check; the decisive JPEG test is the SMDD rebuild's (SM1) arm with JPEG
   crossing against the one without. A has a JPEG violation if more than 10% of FRLL jpeg50 photos are flagged at τ_0.5
   or τ_cam on both A seeds. C passes the JPEG mark if at most 10% of FRLL jpeg50 are flagged at both thresholds on both
   seeds with the gating-family miss at τ_cam not worse than B's by more than 3 points. Reading: C low on jpeg70 but high
   on jpeg50 = the trained qualities were memorised. Pipeline difference, stated: training JPEG copies are compressed on
   the aligned 512 frame and stored as PNG; the FRLL evaluation copies were compressed on the raw photo and then aligned.
5. F6 (headline and middle outcomes). Registered mark P-g: family-mean miss over the gating attack cells (test R4 OpenCV,
   MAD22 OpenCV, MAD22 Webmorph, H1) at τ_cam, B (and Bn, C) against A of the same seed, paired bootstrap (B = 2,000;
   resampling partner cycles of the test ladder, FRLL persons for MAD22, CASIA persons for H1 and development camera
   pools with τ_cam refitted in each draw). Non-inferiority: upper bound of (B − A) ≤ +3 points; "B lowers the miss" only
   if the upper bound is below 0. Fixed sentence "inconclusive, no claim" for every middle outcome: P-b between 0.75 and
   0.90, one seed passing and one failing any mark, P-f unread. The label "passes P-a to P-e" is dropped. P-e uses point
   EERs (interval about ±2 points with 204 photos), stated with it.
6. F7, F8, F9, F11. Certificate folds: persons dealt to 5 folds at random (seed 401); an image is tested in fold k only
   if all its persons are in fold k and trained on only if none is; images that straddle folds are dropped and their
   share printed. THE certificate is the nuisance-only classifier (history, engine, pool, border, person frequency); the
   classifier with softness cues is printed beside it. The simple-statistic floor of read (a) is the maximum over the 27
   statistics on the 512 frame and the 12 certificate cues at 224 px. Bootstrap unit on the ladder: partner cycles
   (the host -> partner permutation's cycles, as `src/AR1/folds.py`). Tier-0 inner folds partner-safe (same fold rule).
   The choice between B and C and any later configuration choice use development-ladder and AF0-validation reads only;
   PN1's test-ladder, corrected-MAD22 and Poisson numbers are "first-test data, read once".
7. F10. Manifest C is built before the pack (done: 2,549 JPEG copies). The pack's sha256 is pinned in this file (line
   added below, before any submission) and checked by the job file before `run.sh` runs. The test-ladder stored copies
   of the morphs (AF0, 19:42) are in the evaluation manifest (764 test attack rows), so no rescoring job is needed for
   them. The job time limit is checked against the smoke job's step rate. Infrastructure failures are rerun unchanged
   once; a run with non-finite loss or weights is never rerun. Tier 1 = eight fits: A, B, Bn, C at seeds 401 and 402.
8. Improvement 4 (reference row from the existing ViT-B/16 recipe retrains on SMDD): no scores of these networks exist
   on PN1's pools (stored ladder copies, development copies, corrected MAD22); cost reported to the lead, not run.
9. Not done (author): JPEG genuine pools from raw corrected-MAD22 files; a stronger shrink than 61.2 px.
10. Split unchanged. Tier-0 arms recomputed: A0, B0 and Bn0 (a seeded draw from B0 of A0's unique counts, same rule).

## Amendment 5 (11 Nov 20:12 CET, before any score of these networks): reference row "standard recipe on released SMDD"

Approved by the lead (improvement 4 of the review). The eight existing ViT-B/16 MADation-recipe retrains on SMDD (the
A12-BR "R" rows, `a12_clip_vitb16_madation_r224_d0_train90_none_lr3.33e-06_s{1..8}_r`, last checkpoint
`/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/<run>/last.pt`, meta from
`/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12BR/<run>/meta.json`; sha256 recorded in the README) are
scored on PN1's 23,640 evaluation images on Athena (`-A plgmultivision-gpu-a100`, container image `fedeff10…`) with
`pn1_score.py`, the scorer of PN1's own networks (logit without flip averaging; flip average stored), from the same pack.
All eight are reported, none is selected. Question fixed in advance: does the standard recipe flag more than 10% of
any history-matched genuine pool (test-ladder R0_61 and R0_112, FRLL-Morphs and corrected-MAD22 E7 pools, FRLL
blur1 / resample50) or JPEG genuine pool (FRLL jpeg90 / 70 / 50) at its own 0.5 rule or at τ_cam, and what does it miss
on the gating attack cells at the same threshold? Reported per network and as the range over the eight; no pass mark.

## Pack pin (11 Nov 20:15 CET, before any Athena job)

`/mnt/t7/smad_next/PN1/pn1_pack.tar`: sha256 `5c6427907d92514ed284881fcf859f92a4294da74e03ada46226fdd7b0dd2676` (10,159,360,000 bytes, 31,398 files in its SHA256SUMS: code and
ViT-B/16 weights of the AD4 pack, `pn1_score.py`, manifests train_A (`af070a60529db3e8…`),
train_B (`bd53dc3252a76767…`), train_Bn (`21b5a2ca91fb672e…`),
train_C (`a9f8fae62382648f…`), pn1_eval (`44f049d11a6c9dee…`)). The job files refuse any other pack.

## Amendment 6 (11 Nov 21:06 CET, before any fit result exists): one platform for all tier-1 networks

The author approved a rented A100 (Docker image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, the base of the
Athena container image, with the same pinned packages: timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0, numpy
1.26.4, pyyaml 6.0.3, pillow 10.2.0) as a fallback while Athena's queue forecasts a start on 12 Nov 16:56. Rule: all
eight fits and the reference row come from ONE platform. If the rented machine is used, its set is the registered one:
the owner cancels Athena array 3545976 and job 3545977 as soon as the rented 200-step smoke fit has passed, before
any rented fit result exists (no duplicates). If the rental does not happen, Athena stays the platform. A fit from one
platform is never compared with a fit from the other. On the rented machine the same pinned pack (`5c642790…`) and the
unchanged `run.sh` (`42b335b6…`) run with the host Python (`PN1_LOCAL=1`), 7 loader workers, one task after another;
the reference row runs the same scorer (`pn1_score.py`) with a copy of `score_ref.sh` whose only change is the host
Python instead of `apptainer` and local paths (`src/PN1/rented/score_ref_local.sh`).

## Amendment 7 (11 Nov 21:21 CET, before any fit result): two rented machines, split by seed

The rental goes ahead with two A100-SXM4 machines (lead): pn1a (40 GB) runs the four seed-401 fits (A, B, Bn, C) and
then the reference row; pn1b (80 GB) runs the four seed-402 fits. Arms are therefore always compared within one seed
on one machine (P-g and every A-against-X comparison is within seed). Across seeds the card differs (40 GB against 80 GB
memory, same family); seed spread is reported with that stated. The Athena array 3545976 is cancelled and the Athena
reference result 3545977 is discarded once the pn1a smoke fit has passed (amendment 6).

## Amendment 8 (11 Nov 22:35 CET, before any computation on these images): spliced-positive frozen heads

Lead's request (author-approved remedy experiment against cue learning; not a dataset extension, not a benchmark).
Images: the landmark-ladder owner's pixel-copy splices with one hull per host, `/mnt/t7/smad_next/AR1/img/frgcferet/
{opencv,facemorpher}/{S4,S3,S0}/` (S4 = two-person morph inside the face on the geometry-matched warp-only image; S3 =
same-person morph inside; S0 = seam-matched negative), manifest `/mnt/t7/smad_next/AR1/manifest_splice2.csv`, with
their face-blanked (`face_R4hull`) and background-blanked (`bg_R4hull`, only the face visible) copies; R4 and R2w
blanked copies from AR1's `blank/` (own hull) and `blank_splice2/` (R4 hull). Split and thresholds as registered (test
191 hosts read; τ_0.5, τ_cam). Features: frozen CLIP ViT-L/14 224 and DINOv3 512 mean tokens (DGX extraction).
Heads as section 3 (logistic, partner-safe inner folds, seeds 401 to 405, 401 named), stratified balance as amendment 4.
- Arm S-a: S4 (attack) against S0 (negative) only, OpenCV-style engine, ladder training hosts (S4 of the 124 hosts
  with a usable partner, S0 of the 156).
- Arm S-b: the B0 protocol rows plus the same S4 (attack) and S0, S3 (negatives).
- A0 and B0 are read beside them on the same images.
Reads (test hosts, OpenCV-style engine; FaceMorpher printed): S0 vs S4; R2w vs R4 and R2w4 vs R4; each as excess over
the simple baselines (39 statistics of amendment 4 plus the inside-against-outside sharpness ratio = Laplacian
variance inside the R4 hull over that outside it, hull taken from the background-blanked copy); the same AUCs on the
face-blanked copies and on the face-only copies (for R4 vs R2w: R4 blanked with its own hull, R2w with the R4 hull);
the fixed-threshold storage reads of section 6 (c), (f); transfer to H1 and corrected MAD22 OpenCV and Webmorph.
Question fixed in advance: does a head trained with spliced positives read the face blend, i.e. face-only AUC
(S0 vs S4 and R2w vs R4 on face-only copies) at least 0.80 and above the best baseline on the same copies, where the
protocol head B0 reads mostly the surround (face-blanked AUC above its face-only AUC)? Reported as numbers; no pass mark
beyond the stated 0.80.

## Amendment 9 (11 Nov 23:15 CET, before computing): seed stability of the spliced arms, bracketing test, DiffAE transfer

Lead's request. (1) The spliced arms S-a, S-b at seeds 402 to 405 (already fitted by `splice.py` in the same run as seed
401; their reads were not opened before this amendment) are reported with partner-cycle intervals beside seed 401.
(2) Bracketing test (ideation round 3) as an evaluation row for every frozen head (A0, B0, Bn0, S-a, S-b; CLIP and
DINOv3; seeds 401 to 405): share of the 191 test hosts whose two-person morph (R4, OpenCV-style) scores above BOTH its
native warp-only image (R2w) and the 61.2 px copy of that warp-only image (R2w_61); beside it the same share for the
best simple statistic, taken as the maximum over the 39 statistics (27 at 512 px, 12 at 224 px) and the sharpness
ratio, each oriented by its sign on R4 vs R2w, maximum taken on the test hosts themselves (an optimistic floor, stated);
host bootstrap over partner cycles. Also printed with the geometry-matched warp-only image R2w4 in place of R2w.
(3) Transfer, no fitting: the same heads scored on the diffusion-autoencoder set B (`/mnt/t7/smad_next/DG1/gen/setB_s*`,
manifest `/mnt/t7/smad_next/DG1/validity/setB/manifest_full.csv`, rows with test_read = 1: photos G, reconstruction
REC, same-person mix SAME, mirror mix MIR, two-person morph X, all 20 steps, 256 px). These images are 256 px, so the
features use each backbone's own timm transform (CLIP: resize to 224; DINOv3: resize to 512) without AF0's 512-px
assertion (`src/PN1/featmean_any.py`). Reads: AUC X vs REC, X vs G, X vs SAME, X vs MIR, each beside the best of 24
simple statistics (the 12 certificate cues at 224 px and at 256 px, folded) on the same images.

## Amendment 10 (11 Nov 23:50 CET, before any tier-1 fit result is opened): spliced-positive LoRA arm

Wording of the splice review (`experiments/reviews/REVIEW_SPLICE_20261111.md`, section Q6), registered as written.
Disclosure: the frozen spliced reads (amendments 8, 9) were computed and seen on the test hosts and MAD22 before this
registration; two tier-1 tars (PN1_A_s401, PN1_A_s402) have been copied back and hash-checked but not opened.
- Arms (ViT-B/16, the AD4 recipe, unchanged train.py): **S-b LoRA** = manifest B + S4 (OpenCV-style) of the 124
  training hosts with a usable partner as attacks, with S0 and S3 (OpenCV-style) of the 156 ladder training hosts as
  negatives; **volume control Bv** = manifest B + the same number of extra unique rows, drawn seeded from B's kinds
  (repeated B images, since no new image exists; stated). Seeds 401 (named) and 402, each on the same machine as that
  seed's B fit; stratified balance as amendment 4.
- Deciding reads (OpenCV only), development ladder first, test ladder read once:
  (i) face-blanked R2w vs R4 lower than B's by at least 0.05;
  (ii) native S0 vs S4 with a bootstrap lower bound of the excess above 0 over a floor fitted on development hosts
  (seam tone + sharpness ratio + band5);
  (iii) P-c, P-c2 and kernel marks;
  (iv) P-g non-inferiority against B;
  (v) H1 AUC not below B by more than 0.02.
- Pass: all of (i) to (v) on both seeds. Kill: (i) fails on both seeds, or H1 falls below B by more than 0.03, or the
  P-g upper bound is above +3 points. Otherwise: "inconclusive, no claim".
- Rule: any choice of arm or backbone for later fits is made on the development ladder and the AF0 validation set
  only; PN1's test-ladder, MAD22 and Poisson numbers stay "first-test data, read once".
- Cost: about 3.5 A100-hours (four fits).

## Amendment 11 (written by 23:38 (git 1c52cbe); header times of amendments 10, 11 and the pack 2 pin were not machine-clock times; approved by the lead): face-only heads, face-blanked benchmark reads, post hoc items

- H-new-3: frozen heads (CLIP, DINOv3; section 3 rules) trained on face-only copies (background blanked with the R4
  hull, AR1 `blank_splice2/bg`; R4 with its own hull, AR1 `blank/bg`) of the ladder training hosts: attacks S4_bg and
  R4_bg (hosts with a usable partner), negatives S0_bg, S3_bg, R2w_bg, R2w4_bg; read on test face-only S0 vs S4 (= R2w
  vs R4 face-only) and R2w4_bg vs R4_bg, with the excess over band5@224 and over the 3-statistic floor below.
- H-new-5: corrected-MAD22 (bench_s subsample) and H1 images with the face blanked: constant grey 128 inside the convex
  hull of AF0's fixed canonical landmarks (`/mnt/t7/smad_next/AF0/canonical_lm.npy`, the fixed hull AF0 uses for
  benchmark frames); EER of the S-b DINOv3 head (and every frozen head) blanked against native.
- Post hoc, labelled as such (no pass marks): the 3-statistic floor for S0 vs S4 (seam tone = mean luma and mean R-G
  difference between 3-px rings inside and outside the R4 hull, sharpness ratio, band5@224; logistic, fitted on
  development hosts, applied to test hosts); FaceMorpher spliced reads are not used ("seam not matched"); training-person
  resampling of the frozen heads (10 resamples of the training persons with replacement, seed 20261124; MAD22 E7 EER
  and τ_cam gating miss); harder brackets (c) margin over the host's own R0 -> R0_61 shift and (d) fixed threshold τ_cam
  (bracket (a) on face-only copies without the softened face copy, which does not exist).

## Pack 2 pin (12 Nov 00:05 CET, amendment 10 fits)

`/mnt/t7/smad_next/PN1/pn1_pack2.tar`: sha256 `266ce5c352f1a04220d2025092ef92f973f0c8ecdc5872671a228819b189fce6` (11,289,876,480 bytes, 36,201 files): the content of pack 1 plus
manifests train_Sb (`2cf3fda3affc8dd3…`, 8,648 rows) and train_Bv
(`4057e9935a4e813e…`, 8,400 rows), the spliced training images, and
pn1_eval.csv extended by 4,365 spliced and blanked ladder rows of development and test hosts
(`22d1c23e9eccca75…`). Manifests A, B, Bn, C byte-equal to pack 1.
run.sh changed only in its arm list (A|B|Bn|C|Sb|Bv; sha256 `a208fcf8d17e0b8a…`).

## Amendment 12 (registered at git 1ab1256 (03:19:01); PN1_Sb_s401.tar was already local (03:08:28) but not read (sb_read.json at 1ab1256 has B only)): rescoring B on the spliced rows

Read (i) of amendment 10 compares the face-blanked R2w vs R4 AUC of Sb with B's, but B was scored with pack 1, which
has no spliced or blanked rows. B (seed 401 on pn1a, seed 402 on pn1b) is rescored on the same machine after its second
queue, from its result tar (meta.json + last_trainable.pt on the pack-2 base weights; `src/PN1/rescore.py`, logit
without flip), on the 4,365 spliced and blanked rows of pack 2 (one platform per seed kept). Tested on 8 rows on the DGX.

## Note on times (12 Nov, review REVIEW_PN1_TIER1_20261112.md)

Header times of amendments 10, 11 and the pack 2 pin were typed, not machine-clock times (commit 1c52cbe at 23:38:52
already contains them; pn1_pack2.tar was written 23:31:05). From here on registrations cite git hashes and `date`
output.

## Amendment 13 (registered at the git commit that adds this section; no HN2 score exists at that commit): HN2, genuine-source shortcut on FFHQ

Lead decision on the pre-run review `experiments/reviews/PRERUN_PN1_FRESH_SEEDS_20261112.md` (commit 7d90384), items F1,
F4, F5. FFHQ only (no FEI, no SMDD).

- Networks: the eight tier-1 networks (A, B, Bn, C x seeds 401, 402), unchanged (trained with run.sh `42b335b6…`,
  amendment 6). Each seed is scored on its own rented machine (seed 401 pn1a, seed 402 pn1b; one platform per seed),
  after that machine's third queue (amendment 12), from its result tars: `src/PN1/rescore.py` (sha256 `6f6eede7…`;
  meta.json + last_trainable.pt on the pack-2 code and base weights; logit without flip), driven by
  `src/PN1/rented/remote_hn2.sh` (`2cc83d14…`). run.sh (pack 2, `a208fcf8…`) is not used for scoring.
- Scoring list `pn1_hn2.csv` (sha256 `4c0caa89ab25406854b6865c17943ef5e9532b0e5cc8bed58ad8e73d53b15871`, 5,000 rows,
  built by `src/PN1/build_hn2_pack.py` `4986c42d…` from existing aligned files of `/mnt/t7/smad_heldout/ffhq_morphs`, each
  checked against its SHA256SUMS; nothing built): ffhq_bona orig 2,000 (label 0), landmark_complete orig 1,000 (label
  1), landmark_complete resmatch 2,000 (label 0, printed only). Pack `/mnt/t7/smad_next/PN1/pn1_hn2.tar` sha256
  `7648b15ac67798e7601e24b790e62ef86687949f9af0ac440065c2fcb6ac42a7`. The bona fide persons are disjoint from every
  morph contributor (dataset design, checked by the builder), so the within-source read compares disjoint persons.
- Reads per network (`src/PN1/hn2_read.py` `caf027b2…`): (a) share of FFHQ bona fide with logit > 0 (own rule τ_0.5);
  (b) AUC of landmark_complete orig morphs against ffhq_bona orig.
- Rule (F5, fixed now): "shortcut supported" if (a) ≥ 0.30 AND (b) ≤ 0.75; "calibration shift (not a shortcut)" if
  (b) ≥ 0.90; otherwise "inconclusive". An arm sentence needs both seeds with the same verdict, else "mixed".
- Printed only, no mark: 95% bootstrap intervals (2,000 draws, rng 20261113, images resampled within class); (a) at the
  network's tier-1 τ_cam; the morphs against the history-matched bona fide (resmatch) and that pool's flag share.
- Caveat (F4), stated before scoring: the FFHQ bona fide are 1024x1024 PNG, native eye distance median 259 px (shrunk
  about 0.51x into the 512 frame); the landmark_complete morphs are 256x256 PNG, median 65 px (enlarged about 2.0x).
  Reading (b) on orig therefore mixes morph signal with an enlargement/resolution history difference that favours a
  high AUC for a network that reacts to softness; the resmatch read shows the size of that part. The 512 frames of FFHQ
  are PNG like every other PN1 pool; no JPEG history on either side.
- Release: drive.sh waits for `PN1_HN2_s<seed>` before RELEASE (task folder created on upload); caps and stop times of
  the leases are unchanged. If a machine cannot finish it inside its cap, the task is dropped there and reported, not
  moved to another platform.
- Native history table (lead item A; post hoc, descriptive, no GPU, no new score): `tier1/native_history.json`
  (`src/PN1/native_history.py`).

## Benchmark ruling and development designation (12 Nov 2026; `date`: Thu Nov 12 08:11:57 AM CET 2026)

- Author ruling, his words: "We can't use the set for development we're using to benchmark methods, that is a grave
  error. We are aiming for CVPR." Follow-up: "Just use another dataset to compare them, unless we do not plan to use
  FFHQ in benchmarks."
- Lead designation under that ruling: the FFHQ set (genuine and every morph family under
  `/mnt/t7/smad_heldout/ffhq_morphs`) is the development comparison set of this sprint and is not reported as a
  benchmark in the paper.
- FRLL, MAD22, MorDIFF, DiM, H1, FEI and the sealed sets stay sealed for every candidate network until the method is
  frozen. No PN1 network, existing or fresh, is scored on them from now on.
- What PN1 has already read on those sets: `BENCHMARK_EXPOSURE.md`. H1, MAD22 and FRLL exposure is unchanged by the
  designation.
- Suspended: the frozen fresh-seed contrasts v3 (git e4a4590; primary contrast on H1). They are replaced by
  registration FS1 below. The two amendment-14 drafts (full, reduced) as written on H1 are cancelled. Amendment 14 is
  revived only as a development read (separate section, committed after FS1).

## Registration FS1: fresh seeds on development data only (registered at the git commit that adds this section; no fresh-seed fit, no FFHQ landmark_combined score or statistic exists at that commit)

- Author's answers (12 Nov, his words: "2. Yes", "3 go"): the killed Sb arm may be refitted on the stated grounds;
  budget approved for arms A, B, Sb at seeds 403 to 407 plus the replicate fit of A seed 401, 16 fits, about 11.6 USD,
  two leases of one type, each seed whole on one machine. C decided: not run.
- Contrasts, margins, seed rules, deadline and claims: `prereg_fresh_seeds_v4_frozen.md` (committed with this section;
  development data only).
- Recipe: unchanged train.py and flags (README section 4), last checkpoint, manifests train_A (`af070a60…`), train_B
  (`bd53dc32…`), train_Sb (`2cf3fda3…`), byte-equal to pack 2; training images are our own AF0 and ladder images from
  FRGC / colorFERET (no FFHQ, FRLL, MAD22, CASIA, FEI image in any training manifest).
- Pack (development only): `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar`, sha256
  `96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004` (8,752,445,440 bytes; builder
  `src/PN1/build_pack_fs.py` `613398bb…`, which asserts that no benchmark row or image is included); evaluation
  manifest `pn1_eval.csv` `f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045` (19,797 rows: af0 1,339,
  ladder 6,093, splice 4,365, FFHQ HN2 list 5,000, FFHQ landmark_combined 3,000). The driver cannot score a benchmark
  row: none is in the pack.
- Scorer `pn1_score.py` `737d6e35…` (inside the pack); run.sh `74a49b0baaeb99108664bf8243d079b708c94f4f87c154ff5840796288e48bb0`
  (pack-2 run.sh plus seeds 406, 407 in its seed list and the GPU UUID written into each result tar; training and
  scoring commands unchanged); `src/PN1/rented/remote_fs.sh` and `src/PN1/rented/drive_fs.sh` (sha256 at this commit).
- Platform: two leases of A100-SXM4 40 GB; GPU UUID recorded per lease (setup log) and per fit (gpu.txt in the tar).
  Machine 1: seeds 403, 405, 407 (A, B, Sb each), 9 fits. Machine 2: seeds 404, 406 (A, B, Sb each), then the
  replicate A seed 401, 7 fits. Replacement of a lost lease: same type only, disclosed; the unfinished seed restarts.
- Reader `src/PN1/fs_read.py`: committed before the first fresh-seed tar is pulled; it implements exactly the frozen
  rules.

## Amendment 14 (development read; registered at the git commit that adds this section, after the FS1 freeze ac585b7; no amendment-14 score and no landmark_combined statistic exists at that commit)

Text 14 of `prereg_amendment14_draft.md` (pre-run fixes F1 to F6 of `PRERUN_PN1_A14_AND_SEEDS_V3_20261112.md`, commit
3f2bd14) is registered with these changes under the 12 Nov ruling and designation:
- HN7's transfer axis is the FFHQ landmark_combined AUC (development set), not H1; H1 is sealed and is not read.
  Prediction and falsifier unchanged (Spearman ≥ 0.6 and A's face-only AUC > B's on both seeds; falsified ≤ 0.2);
  label "associational, between arms"; bootstrap over test partner cycles and landmark_combined images (rng 20261117).
  Disclosure: the 12 H1 values that motivated HN7 were known; no landmark_combined value is known.
- Text 14R is not used.
- Pack contents checked: `pn1_a14.tar` (`bda5fd3d…`) holds the 4,365 splice rows (our own OpenCV-style splices of
  FRGC / colorFERET ladder hosts, files under `/mnt/t7/smad_next/AR1`), the HN2 list and landmark_combined (FFHQ,
  development); no FRLL, MAD22, MorDIFF, DiM, H1, FEI or sealed image or row.
- Reader `src/PN1/a14_read.py` sha256 `c2e81363fd53844795272255dfa84819a72c1d37fb7b2017ef290a30a8964cc7`. Unchanged:
  rescore.py `6f6eede7…`, remote_a14.sh `adc0b84d…`, drive14.sh `e079e4b5…`, build_pack14.py `1f08b98d…`, list
  `9f199c3a…`, floor list `e1df77a5…`, cues27.py `2338780c…`.
- Platform: run first on fresh-seed machine 2 (A100-SXM4 40 GB), before its fit queue (the queue waits for A14_DONE);
  the driver's lease folder for this step is a sub-folder (`LEASE/a14`), so its RELEASE marker does not release the
  machine. Gate, guard values (1.5 USD of the machine-2 cap, 2.5 h) and failure rules as in Text 14.
- Order: the floor cues on landmark_combined (`cues27.py`) are computed and their sha256 committed
  (`tier1_a14/a14_lcomb_floor.sha256`) before the lease starts; they serve both amendment 14 and FS1 contrast 1.

## Deviation FS1-D1 (`date`: Thu Nov 12 08:19:22 AM CET 2026; committed before any fit starts; frozen contrasts v4 untouched): GPU type and one-host layout

Reason: no single A100-SXM4 40 GB is on offer (lead, 12 Nov morning).
- GPU type rule: A100 40 GB of either form factor (SXM4 or PCIe; same GA100 chip, sm_80). GPU index, name and UUID are
  recorded in every result tar (`gpu.txt`, the GPU named by CUDA_VISIBLE_DEVICES). All arms of one seed run on one
  GPU; results are printed per GPU. The replicate A seed 401 is then read as "platform plus nondeterminism" against
  an SXM4 original (pn1a), which mixes form factor, host and run-to-run nondeterminism; it separates none of them.
- Preferred layout: ONE 2-GPU A100 PCIe 40 GB host, queue m1 (seeds 403, 405, 407) on GPU 0 and queue m2 (amendment
  14 first, then seeds 404, 406 and the replicate A 401) on GPU 1, via CUDA_VISIBLE_DEVICES; separate work folders per
  task, task-named result tars, per-queue markers; one guard, cap 11.6 USD total, deadline 13.5 h; disk 120 GB.
  RELEASE (+ FAILED) only when both queues are fetched and verified (`PN1_FS_ONEHOST=1`).
- Fallback: two single A100 40 GB leases of whichever form factors are on offer (same queues, one per lease); if the
  two differ, the mixed-type layout is disclosed in the result and every read is printed per GPU.
- Scripts re-pinned (training and scoring commands unchanged): run.sh
  `04998a7c274229b861b840e2b5a793854a712a7fb031fb572e34e1c791a4c87e` (only the gpu.txt line: the visible GPU and
  CUDA_VISIBLE_DEVICES); remote_fs.sh `010f1f621392916f2281d448b756da70916c17ce404d2f5df8c1bd1c8e5ae7e1`; drive_fs.sh
  (sha256 at this commit; pins run.sh `04998a7c…` and the pack `96c31ae2…`); amendment 14's remote_a14.sh
  `fadc2c79174d48b6dbdca678356da8bd445c215743b473f02e66f97be190f58a` (only the gpu.txt line) and drive14.sh
  `f0c99f172a55ba8c5dab5369cd03339120bec7a7740be70b76d3455236259d1d` (CUDA_VISIBLE_DEVICES for its scoring).
- Reader `src/PN1/fs_read.py` `ff363aa4abc2fc13d500e274b4d2bc2fd9a65348f3b3652cc383b716de6f879a`, committed here,
  before any fresh-seed tar exists (tested on random mock scores only).
- Wording fix: the 4,365 splice rows in the FS1 pack and in amendment 14 are all OpenCV-style splices of FRGC /
  colorFERET ladder hosts (tool column "opencv" for all 4,365).
- Local checks: the 20-step smoke of run.sh on the development pack passed (rc 0, full tar); the two-queue path
  (both queues, A14_DONE wait, per-queue markers, joint RELEASE and FAILED on a partial queue) passed a mock test with a
  stand-in task script.
