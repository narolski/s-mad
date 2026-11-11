# Fixed-threshold re-read of existing scores (EV1)

Written 11 Nov 2026, 15:40 CET, before this owner read any per-image score value. Read so far: the manifests
(`eval.csv`, `gtest.csv`, `ffhqm.csv`), key names, shapes and row ids of the score and embedding files,
directory listings, and these aggregate pages: the cue checks (C1 to C4) result, the review of the MorDIFF
ladder re-read (AD1), the file-table study (A41, `a41_files.md`: per-cell separability of stored-file
attributes) and the summary page of the morph-free network study (A47, `a47_read.md`). Zero GPU; no image is
made, re-encoded or written. This page is also the separate registration that the protocol requires before
the E5 variant rows (jpeg90, jpeg70, jpeg50, blur1, resample50) are read; they are existing, scored rows.

**Partly post hoc.** Known before this page: (a) stored-file width separates every FRLL-Morphs, MorDIFF and
DiM cell at O = 1.000 (A41 file table), so the primary diagnostic-cell count of Part B is predictable;
(b) the morph-free MADation-recipe network reaches 0.00% EER on MorDIFF and 0.00 to 1.17% on DiM at its last
checkpoint (A47); (c) the released MADation ViT-L/14 flags 5.4 / 5.9 / 13.2 / 52.9% of genuine photos
(orig / JPEG 90 / 70 / 50) at an earlier threshold definition (quoted in the idea text, from the record);
(d) flag rates at per-detector EER thresholds on MorDIFF (AD1 review). Every number of this page is computed
anew under the definitions below; the parts that repeat (a) to (d) are labelled post hoc in the result.

## Question in plain words

- **Part A.** With one threshold per detector fixed on development genuine photos (5% and 10% false
  alarms, never refit): how many processed genuine FRLL photos are flagged, how many morphs are missed, and
  how many are missed once the threshold is raised to protect every gated genuine pool?
- **Part B.** In each benchmark cell, how well do morph-blind models do, and by how much does each detector
  exceed the best of them?
- **Part C.** Inside one morph family (same tool, format and history), does a detector's score rise with the
  dissimilarity of the two contributors?

## Data (all exist; paths checked by listing)

- Rows: `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` (sha256 86d055d3…, 44,666 rows).
  Used: set devbona (5,033 genuine, D-MAD probe photos of FERET/FRGC, the registered threshold pool of
  `analyze.operating_points`; 2,178 are training captures of our d1 arms, none of the releases or d0
  recipes), frllm, mordiff, dim. **Excluded: set mad22 (old 185 + 4,069 subset) and variant chip.**
- Genuine pools (204 photos of 102 FRLL persons each): frll_bona orig, jpeg90, jpeg70, jpeg50, blur1,
  resample50; dim_bona orig (byte-identical to frll_bona orig); mordiff_bona orig (another alignment of the
  same photos); the 12 resmatch pools (E7 shrink-and-enlarge history matched to each morph family: 5
  FRLL-Morphs, 6 DiM, MorDIFF).
- Morphs: FRLL-Morphs amsl 2,175, facemorpher 1,222, opencv 1,221, stylegan 1,222, webmorph 1,221 (orig);
  300 per family in each of jpeg90, jpeg70, jpeg50, blur1, resample50 (the same 300 names in every variant,
  all present in orig); MorDIFF 1,000; DiM-A, DiM-C, Fast-DiM, Greedy-DiM, Greedy-DiM-S 500, Fast-DiM-ODE 499.
- Other photo sources: FEI genuine in `gtest.csv` (sha256 5ededd6f…; 198 neutral + 187 smiling, subject id
  = file stem), FFHQ genuine in `ffhqm.csv` (sha256 732b53c8…; ffhq_bona orig 2,000 plus five FFHQ
  resmatch pools of 2,000, no identity labels; the manifest notes that its classes share people).
- Embeddings (glintr100): `/mnt/t7/smad_heldout/a46/feat/a46_feat.npz` group raw (204 FRLL photos) and
  morph groups pub_mordiff (1,000), pub_dim_c, pub_greedy_dim, pub_greedy_dim_s (500 each);
  `/mnt/t7/smad_next/AR1/frll_src_emb.npz` (204 photos, cross-check of the contributor distances);
  `/mnt/t7/smad_heldout/a41_diffae/work/glint_embeddings.npz` group dim_a_pub (100 DiM-A morphs, secondary).
- Corrected MAD22 (null rows only; no detector score exists on it): raw
  `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/`,
  aligned `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native/`.

## Detectors (one network per row; no fusion, no seed picking)

Higher score = more morph-like, as in every earlier re-read; nothing is flipped. If a detector's native
AUCs are mostly below 0.5 this is reported, not corrected.

1. **Ten release variants** (`smadcvpr_runs/A12_scored/A12REL/<name>/scores_eval.npz`, key `score_noTTA`):
   MADation ViT-B/16, ViT-L/14, FE ViT-B/16, FE ViT-L/14, FS ViT-B/16, FS ViT-L/14, ViT-B/16 dnorm and dscale
   (diagnostic variants, eval only), SelfMAD (our pipeline), MixFaceNet-MAD (our frames; its own crop branch
   is suspended). FEI and FFHQ: `scores_gtest.npz`, `scores_ffhqm.npz` (8 releases; dnorm / dscale have none).
   Tie rule: if `logit_noTTA` orders the rows exactly as `score_noTTA` does (no inversion), it is used in
   place of `score_noTTA` so that float32 saturation does not create ties at a threshold; otherwise
   `score_noTTA`. Which key was used is printed.
2. **SelfMAD release, own preprocessing** (`mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/
   selfmad_own_eval.npz`, key `score`; 26,077 rows). It holds **no devbona row** and no jpeg90, jpeg70 or
   blur1 row. Fallback fixed now: its 5% / 10% threshold is set on frll_bona orig (a test pool, labelled
   "test-fitted"; its own false-alarm rate there is the target by construction); the other pools are read
   at that threshold; missing variants are printed as "not scored".
3. **MADation-recipe retrains, last checkpoint** (`smadcvpr_runs/A12_scored/A12BR/<run>/scores_eval_last.npz`,
   key `score`; FEI from `scores_gtest_last.npz`; no last-checkpoint FFHQ scores exist): M3 ViT-B/16 seeds
   1 to 8 and M3L ViT-L/14 seeds 1 to 5 (the primary R × d0 rows of `A36_networks.tsv`).
4. **Descriptive block**: the other 38 primary R × d0 recipe networks of `A36_networks.tsv` at the last
   checkpoint (M1 5, M2 5, M4 5, M5 8, M6 5, M8 5, M8O 5).
5. **Morph-free networks** (Part B only): the morph-free study's (A47) I-3 networks, recipes M1 and M3,
   seeds 1 to 3, `/mnt/t7/smad_heldout/a47/runs/A47I3/<run>/scores_eval_last.npz` (last checkpoint, the
   registered deciding checkpoint of that arm), key `score`.

All scores are on our 512-pixel aligned frames, not on each release's own crop (except item 2). This is
printed with every table.

## Statistics common to all parts

- Persons: FRLL genuine photo → its person (first three digits); morph → its two contributors from the name
  (`AAA_BBB` for FRLL-Morphs and DiM, `morph_AAA_EE_and_BBB_EE` for MorDIFF).
- Intervals: the two-way (pigeonhole) person bootstrap of the MorDIFF ladder re-read (AD1, `Draw` in
  `src/AD1/ad1_read.py`, copied unchanged): the 102 persons ~ Multinomial(102, 1/102); photo weight = its
  person's count; morph weight = product of its contributors' counts. B = 2,000, seed 20261111, one draw
  shared by every detector, pool and cell; percentile 95%. FEI: a separate person bootstrap over FEI
  subjects (B = 2,000, same seed). FFHQ: exact Clopper–Pearson interval (no identity labels). Development
  thresholds are fixed numbers (not resampled).
- AUC: Mann–Whitney with ties counted half (weighted version `wauc` of AD1). EER: AD1's `eer_thr`.

## Part A: false alarms and misses at one fixed threshold

- **Threshold** t_α (α = 5%, 10%): the smallest devbona score value t with share(devbona score > t) ≤ α.
  Flag = score > t. Never refit.
- **(1) False alarms**: share flagged in each FRLL genuine pool (frll_bona orig, jpeg90, jpeg70, jpeg50,
  blur1, resample50; mordiff_bona orig; each of the 12 resmatch pools), in FEI (neutral, smiling, all) and
  FFHQ (ffhq_bona orig and its five resmatch pools). Person-bootstrap intervals for FRLL and FEI.
- **(2) Misses**: share of morphs not flagged (score ≤ t), per family (12 families, orig), at t_α and at the
  **worst-pool threshold** t_wp,α = the largest of t_α and of each gated pool's own t_α(pool) (smallest t
  with false alarms ≤ α on that pool). **Gated pools**: frll_bona orig, jpeg90, jpeg70, resample50,
  dim_bona orig, mordiff_bona orig, and all 12 resmatch pools (jpeg50 and blur1 are reported, not gated).
  One t_wp per detector for all families. In the bootstrap, t_wp is recomputed in every replicate with the
  replicate's weights. Family mean = unweighted mean over the 12 families; also printed per group
  (landmark: amsl, facemorpher, opencv, webmorph; GAN: stylegan; diffusion: MorDIFF + 6 DiM).
  Secondary (descriptive): a per-family worst-pool threshold using only frll_bona {orig, jpeg90, jpeg70,
  resample50}, that family's own resmatch pool and devbona.
- **(3) Crossed table**, per FRLL-Morphs family: morph variant {orig, jpeg90, jpeg70, jpeg50, blur1,
  resample50} on the 300 morphs that exist in every variant × genuine variant {orig, jpeg90, jpeg70, jpeg50,
  blur1, resample50, resmatch of that family}. DiM and MorDIFF: morph orig only × the same genuine variants
  (MorDIFF also against mordiff_bona). Per cell: AUC with interval, and the miss rate at the threshold that
  gives ≤ 5% false alarms on that cell's genuine variant; margins: miss at t_5% per morph variant, false
  alarms at t_5% per genuine variant. Cell labels: **native** (orig, orig); **matched** (same variant on both
  sides); **E7-matched** (morph orig, genuine resmatch); **G>M, genuine more processed** (genuine variant
  processed and the morph orig, or the same operation stronger on the genuine side, e.g. morph jpeg90 vs
  genuine jpeg70); **M>G, morph more processed** (morph processed and the genuine orig or resmatch, or the
  same operation stronger on the morph side); **mixed** (different operations on the two sides).
- **(4) Ranking**: Kendall τ-b between the order of detectors by native D-EER (EER refit per cell with the
  cell's own genuine pool, family mean over 12) and by worst-pool miss rate (family mean, α = 5% primary,
  10% secondary). Rows: the 10 release variants plus M3 and M3L (seed means of the per-network metrics: a
  summary, not a fused score) = 12 rows. Also printed: 23 rows (10 releases + 13 networks separately). The
  rise native → worst-pool of the family-mean miss rate is printed for each of the 23 networks.

## Part B: null rows

Cells: the 12 cells with detector scores (FRLL-Morphs × 5 against frll_bona orig, MorDIFF against
mordiff_bona orig, DiM × 6 against dim_bona orig; all morphs of the family, orig) plus the 5 corrected MAD22
cells (FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV, Webmorph against 204 BonaFide) for null rows only.

- **Non-content nulls** (decide the diagnostic count):
  - *File attributes*: per image, native width, height, stored bytes, bytes per pixel and inter-eye distance
    from `eval.csv` (single-attribute O = max(AUC, 1 − AUC); and a 5-feature logistic regression, folds
    below); plus the A41 table's O per stored-file attribute (w, h, bpp, JPEG quality, subsampling, EXIF,
    ICC, container, IED; point values, no per-image file). Corrected MAD22: width, height, bytes, bytes per
    pixel, container and chroma subsampling read from the raw files' headers (`c_checks.header`).
  - *Colour*: the six per-channel means and standard deviations of the aligned frame (C3 features,
    recomputed per image with `c_checks.stats_job`, imported unchanged); 6-feature logistic regression.
    Stored-file colour (framing-confounded) printed as a second row.
  - *Border*: zero-border fraction of the aligned frame (`stats_job` zero_frac), single-feature O.
  - *Expression label*: genuine 03 = neutral, 08 = smiling; morphs: MorDIFF and corrected MAD22 from the
    names; DiM neutral (DiM README); FRLL-Morphs neutral (inferred by the C1 probe, 1 to 7% smile-like;
    under re-test in the expression re-read (C1b)). Score = 1 if neutral; O.
- **Content null** (printed separately, not used for the count): logistic regression on a 32 × 32 grey
  thumbnail of the aligned frame (grey = mean of RGB; 16 × 16 block mean in memory, the same block-mean
  operation the C1 probe uses; nothing is written), StandardScaler + LogisticRegression(C = 0.1).
- **Morph-free networks**: the six A47 I-3 networks, AUC per cell (12 cells; none on corrected MAD22).
- **Folds** for every logistic regression: 5 folds by person, fold(person) = sha1("c3-" + person) mod 5
  (C3 rule); an item is tested in the fold of its first person and the model is trained on items with no
  person in that fold. A morph's second contributor can therefore appear in training (stated with the
  result). One out-of-fold score per item.
- **Per detector and cell**: AUC with interval; **paired excess** = detector AUC − best non-content null
  (best chosen on the point estimate; for a single attribute its direction is fixed at the point estimate),
  same bootstrap draw; if the best null is an A41 table value (no per-image file), it enters as a constant.
- **Diagnostic cell** (primary): best non-content null below AUC 0.90. Count over the 17 cells. Secondary
  counts: (i) only the nulls computed on the aligned frame (colour, border, expression), which the
  detectors see; (ii) primary rule and in addition every morph-free network below 0.90.
- **Null-conditional AUC** (for the second falsifier clause): strata = quintiles of the best per-image
  non-content null score (pooled over both classes); a stratum is usable if it holds ≥ 5 morphs and ≥ 5
  genuine photos; detector AUC per usable stratum, combined with overlap weights n_m·n_g/(n_m + n_g). A cell
  "has overlap" if at least one stratum is usable; otherwise it is marked "unable to measure morph detection".
- **Expression-balanced reading**: per cell and detector, AUC and EER with the genuine class restricted to
  the 102 neutral photos and, separately, to the 102 smiling photos; paired differences to all 204 on the
  same draw. The expression question itself is owned by the expression re-read (C1b); this is the per-cell
  table the null-row idea asks for.

## Part C: identity dose inside the morph class

- Families: the 12 (orig). Self-pair morphs (same person twice; 10 in FRLL-Morphs) are excluded here only.
- Contributor pair from the name: exposed for FRLL-Morphs (`AAA_BBB`), DiM (`AAA_BBB`) and MorDIFF
  (`morph_AAA_EE_and_BBB_EE`, with expressions). Strata: neutral–neutral and smiling–smiling, computed
  separately. MorDIFF: from the names. DiM: neutral–neutral (README). FRLL-Morphs: neutral–neutral
  (inferred; no smiling–smiling stratum exists).
- **Dose** δ = 1 − cos(A, B), glintr100 embeddings of the two contributors' photos of the stratum's
  expression (03 or 08), from a46 group raw. Cross-check: correlation of δ with the AR1 embeddings' δ.
- **Power check first** (before any detector score enters Part C): oracle = 1 − min(cos(morph, A),
  cos(morph, B)) for families with morph embeddings in a46 (MorDIFF, DiM-C, Greedy-DiM, Greedy-DiM-S;
  DiM-A on the 100 a41 morphs as a secondary check). Power if |Spearman(oracle, δ)| ≥ 0.3 (point
  estimate). Families without morph embeddings (FRLL-Morphs × 5, Fast-DiM, Fast-DiM-ODE; DiM-A in the
  primary reading) are **"no power (no oracle embeddings)"**; families with |ρ_oracle| < 0.3 are
  **"no power"**. No new embedding is computed here.
- **Slope**: Spearman(detector score, δ) per detector, family and stratum. Interval: two-way person bootstrap
  (same Draw restricted to the family's persons; weighted midranks, weighted Pearson of the ranks).

## Falsifiers, verbatim from `ideas/ROUND1_raw.json`, and how each is applied

1. **evaluation → ideas[0]:** "The metric is dropped if, over the 10 release variants plus M3 and M3L, the
   ranking by worst-pool miss rate agrees with the ranking by native D-EER at Kendall tau 0.8 or more and no
   network's family-mean miss rate rises by 20 points or more when the threshold moves from native to
   worst-pool. For our own detector: not shortcut-free if the false-alarm rate exceeds 10% on any gated pool
   at the native 5% threshold."
   Applied: τ on the 12-row ranking at α = 5%; "rises" over the 23 networks (10 releases + 13 recipe
   networks). Both conditions met → "metric dropped"; otherwise "metric kept". The second sentence concerns
   a detector that does not exist yet: not applicable; the existing networks that would fail that bar are
   listed for information.
2. **evaluation → ideas[1]:** "Dropped if 10 or more of the 17 cells are diagnostic, or if on every cell with
   overlap each release's null-conditional AUC is within 0.03 of its raw AUC. The expression row of the cue
   table is crossed out if neutral-only and smiling-only genuine pools give EERs within 2 points for every
   release. Prediction from the record: the morph-free M3 network already reaches 0.0 to 2.6% EER on 11 to
   12 of 17 cells, so at most 5 or 6 cells can be diagnostic."
   Applied: primary diagnostic count over 17 cells; second clause over the release variants (10 plus
   SelfMAD own preprocessing) on cells with overlap (vacuous, and printed as such, if no cell has overlap);
   expression clause over the release variants and the 12 cells. The prediction is checked against the six
   morph-free networks (EER ≤ 2.6% counted per network).
3. **invariance → ideas[0]:** "Audit: with oracle power shown, rho at most 0.10 with upper bound below 0.20
   for the MADation ViT-L/14 release and for M3L on all four FRLL landmark families means even the rows that
   hold under E7 do not read identity distance. Training: within-class Spearman on held-out persons and the
   left-out tool with lower bound at or below 0, or a slope drop above 0.05 under the tool swap, kills the
   idea."
   Applied: the audit sentence, to the ViT-L/14 release and to each of the 5 M3L networks, in the
   neutral–neutral stratum of amsl, facemorpher, opencv and webmorph. If oracle power is not shown for those
   families (expected: no morph embeddings exist), the result is "not applicable: power not shown", and the
   slopes are printed. The training sentence is outside this re-read (no training).
4. **identity → ideas[1]:** "For a detector's identity reading: correlation upper bound at or below +0.10 in
   every generator family means no identity reading there. For the tool itself: if the reference-based
   oracle's own correlation is below 0.3 in a family, the similarity range there is too narrow and the audit
   is void for that family."
   Applied per detector over the generator families (FRLL-Morphs stylegan, MorDIFF, the 6 DiM), both
   strata where present: "no identity reading there" for each family whose upper bound is ≤ +0.10; the
   sentence is stated for a detector when it holds in every generator family with power. Families without
   power are void.

## Guards and caveats fixed now

- Scores are on our 512-pixel frames (reproduction gap: ViT-B/16 MorDIFF 4.9% here against 1.10% published).
- SelfMAD own preprocessing has no development pool; its thresholds are test-fitted (above).
- FRLL has 204 photos: 5% = 10 photos; intervals are wide. Everything here is descriptive, no multiplicity
  correction, no paper-level verdict.
- FRLL-Morphs morph expression is inferred, not documented. dim_bona = frll_bona bytes.
- The E5 variants were made by the earlier registered `prep_eval.py` path; nothing is regenerated here.
- Never read: any file whose name contains fst, valx (except `valx_a.csv`), A12SP or A12-SP; train90 /
  val10 scores; set mad22 of `eval.csv`.

## Stop rule, budget, commands

CPU only on the DGX (≤ 8 worker processes; the machine is shared), about 1 to 2 hours, zero GPU.
Python: `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`. Each script has `--smoke` (8 images per
pool / cell, B = 50) and is run that way first.

- `src/EV1/ev1_feat.py [--smoke]`: per-image colour, border and thumbnail features of the aligned frames and
  raw-file headers of corrected MAD22 → `/mnt/t7/smad_next/EV1/feat.npz`.
- `src/EV1/ev1_partA.py [--smoke]`, `src/EV1/ev1_partB.py [--smoke]`, `src/EV1/ev1_partC.py [--smoke]`
  (Part C runs its oracle power check before loading any detector score).
- Outputs: `experiments/EV1_fixed-threshold-reread/*.csv|json`, `result.md`.

- **Pre-run review:** not run (zero-compute re-read of existing scores; lead to decide, as for the MorDIFF
  ladder re-read (AD1) and the expression re-read (C1b)).
- **Result:** `experiments/EV1_fixed-threshold-reread/result.md`.

---

## Amendment 1, 11 Nov 2026, 16:38 CET (lead's requirements after the second ideation round and the review of the expression re-read (C1b))

(Time corrected at 16:47 to the file's actual save time, 16:38:52; the header first said 16:45 by mistake.
The first amendment outputs were written at 16:43. No other change was made to this amendment.)

Written before any of the items below was computed. **Already seen by this owner at this time:** all
Part A outputs (false alarms on all 204 photos, misses, crossed table, ranking) and all Part C outputs
(oracle check and detector slopes). Part B (as registered above) is running; only its progress lines for
five FRLL-Morphs cells were seen (best non-content null = stored-file width, O = 1.000, as predicted).
Sources read for this amendment: `ideas/CONSOLIDATED_v2.md`, `experiments/reviews/REVIEW_C1b_20261111.md`.
Abbreviations: FA = false-alarm rate (share of genuine images flagged); miss = share of morphs not
flagged; CP = exact Clopper–Pearson 95% interval; E7 = the shrink-and-enlarge history-matched copies
(resmatch); devbona = the development genuine photos of `eval.csv`.

**Scope statement printed on every table:** scores are on our 512-pixel aligned frames (SelfMAD own
preprocessing excepted), where the releases' published numbers are not reproduced (released MADation
ViT-L/14 on FRLL-Morphs AMSL: 17.7% EER here against 7.26% published); the own-crop re-score of the
audit rows (RS1) is redoing the key rows through each release's own preprocessing.

### A1. Both class policies for diffusion and GAN controls (rates only, no verdict words)

- Sets: (i) the MorDIFF control images of the earlier MorDIFF ladder study (A43 manifest
  `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`, scores `/mnt/t7/smad_heldout/a43/a43_out/a43/<release>/<mode>/scores_a43.npz`):
  arm E (204 FRLL photos only stored at the published MorDIFF crop size, "stored-small"), D20 and D (one-photo
  DiffAE reconstructions, 20 and 100 steps), C20 and C (same-person mixes of the neutral and smiling photo),
  A (200 published MorDIFF morphs), B20 and B (200 of our same-pair morphs); scored by the six MADation
  releases and SelfMAD (own preprocessing and our pipeline). (ii) StyleGAN3: the H3 set
  (`/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv`, 423 morphs `h3_sg3` and 423 one-identity renders
  `h3_bona`, variant orig) and the spread-matched renders of the StyleGAN3 ladder (AG5) (`a37spread`, orig);
  scores `A12REL/<release>/scores_h3sg3.npz`, `smadcvpr_runs/A36/selfmad_own/own_h3sg3.npz`,
  `/mnt/t7/smad_heldout/a41g/a41g_out/x4/<release>/<mode>/scores_a37spread.npz` (and the a46x4 path for
  MixFaceNet-MAD). Recipe networks have no last-checkpoint scores on these sets and are left out.
- Thresholds: the Part A devbona thresholds at 5% and 10% (same score key; for A43 the consistency of the
  re-scored registered MorDIFF genuine frames with the eval file is checked, max |Δ| printed). SelfMAD own
  preprocessing: the Part A test-fitted fallback.
- Policy G (counted as genuine): reconstructions (D20, D) and one-identity renders (h3_bona, a37spread)
  are genuine pools: their FA is printed and they are added to the gated pools of the worst-pool threshold.
  Policy X (inadmissible): they are left out; worst-pool threshold from the Part A gated pools plus arm E.
  Printed per detector and policy: FA per pool (CP), miss on each morph set at the native threshold and at
  the policy's worst-pool threshold. Same-person mixes (C20, C) are printed as their own row (flag rate),
  under neither policy (they are morphs by the author's ruling of 11 Nov and inherit the smiling-half file
  difference).

### A2. Per-pool false-alarm block (style of NIST's morph evaluation)

- One threshold per detector (devbona 5% and 10%, Part A). Per genuine pool: FA with CP interval. Pools:
  the stored-small arm E first (MorDIFF cell), then FRLL orig, jpeg90, jpeg70, jpeg50, blur1, resample50,
  MorDIFF alignment, the 12 E7 pools, FEI neutral / smiling, FFHQ orig and its five E7 pools.
- Paired per photo against FRLL orig (same person, same capture): number of photos that change side
  (flagged in the variant but not in orig; flagged in orig but not in the variant), exact two-sided
  McNemar p (binomial on the discordant photos), and the number of persons with at least one photo that
  changes side. Neutral-only (102) and all (204) both printed.

### A3. Smiling half (not called "expression")

- The neutral and smiling FRLL photos differ in capture detail as well as expression; the effect is named
  "smiling half of the FRLL genuine class". In every imbalanced cell (FRLL-Morphs × 5, DiM × 6; corrected
  MAD22 Webmorph for null rows) the **neutral-only genuine class is the headline**, all 204 photos beside it:
  Part B detector AUC, EER, paired excess and the null rows (logistic nulls refit with the neutral-only
  genuine class), the diagnostic count, Part A crossed-table AUCs, and the worst-pool threshold (gated
  FRLL pools restricted to their neutral photos). The Part B null formerly named "expression label" is
  renamed "smiling-half label".
- Within-person neutral-above-smiling share (s(03) > s(08), ties half; mean over persons, person bootstrap
  B = 2,000) for every primary detector on: FRLL orig, each E5 variant (jpeg90 … resample50), each of the
  12 E7 copies of the same 204 photos, the MorDIFF alignment, arm E, and FEI (subjects with both a neutral
  and a smiling frontal photo).
- FEI backdrop check, done before the FEI share is read: corner statistic on the stored captures
  (`/mnt/t7/Datasety/downloads/FEI/extracted/<subj>-11.jpg` neutral, `-12.jpg` smiling; FRLL raw files for
  comparison): grey image; four corner squares of side 10% of the shorter image side; noise = standard
  deviation of horizontal first differences / √2 within each square; per image the median of the four.
  Paired per person: median smiling / neutral ratio and share of persons with smiling > neutral.
  "Equal backdrop noise" = median ratio within [0.8, 1.25] and share within [0.3, 0.7]. If FEI fails this,
  its share is printed with that label.

### A4. Controls for the identity-dose slope

- The identical Part C computation (same strata, same δ, same bootstrap) for (a) the six morph-free
  networks of the morph-free study (A47 I-3) and (b) the stored file size of each morph (`eval.csv`
  file_bytes). A control "has a slope" in a family and stratum if its 95% interval excludes 0. Where either
  control has a slope, the reading for that family states that the dose test can be produced by
  construction there.
- MorDIFF stratified by expression subset (neutral–neutral, smiling–smiling) and by gender, taken from the
  release's folder names (`MorDIFF_crop/{neutral,smiling}_front_{female,male}_aligned`); the eval file names
  do not carry gender. Detectors and both controls are read in the four MorDIFF strata.

### A5. Split-half choice of the best null

- Persons split into two halves by sha1("ev1-half-" + person) mod 2. An item belongs to a half if all its
  persons are in it (morphs with contributors in different halves are dropped from this analysis). The
  best non-content null (per-image nulls only; the A41 point values cannot be split) is chosen on half 1
  and its AUC / O reported on half 2, and the reverse. Diagnostic count (< 0.90) under both splits, all
  genuine and neutral-only; the count is "unstable" if the two splits disagree on any cell.

### Stop rule

CPU only, as above. Scripts: `src/EV1/ev1_amend.py [--smoke]` (A1, A2, A3 shares, FEI check),
`src/EV1/ev1_partB.py` gains an amendment pass (A3 neutral-only headline, A5), `src/EV1/ev1_partC.py`
gains the A4 controls and MorDIFF gender strata. Smoke on 8 items first.
