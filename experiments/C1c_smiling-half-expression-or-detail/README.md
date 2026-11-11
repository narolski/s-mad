# What the smiling half carries: expression or capture detail (C1c) — full record

Owner: hypothesis-owner agent (Claude), for Paweł Narolski. Written 11 Nov 2026, 17:55 CET (documentation
pass asked by the author at 17:20). Short verdict: `result.md`. Predecessor: "Is the expression imbalance
of the benchmarks used by detectors" (C1b), `../C1b/README.md`.

**Abbreviations.** FRLL = Face Research Lab London set (102 persons; 03 = neutral frontal photo, 08 = smiling
frontal photo, 1350 × 1350 JPEG). FERET = colour FERET (fa = regular expression, fb = alternative
expression, same session). FRGC = Face Recognition Grand Challenge 2.0 controlled stills. FEI = the FEI face
database (not used here, see section 9). CLIP = OpenAI's image–text model; ViT-B/16 and ViT-L/14 = its two
vision transformers. MADation = CLIP fine-tuned with low-rank adapters for morph detection (released
weights); FE = frozen-encoder variant (head only), FS = from-scratch variant. M3 / M3L = our retrains of the
MADation recipe on ViT-B/16 / ViT-L/14; M1, M2, M4, M5, M6, M8, M8O = our CNN recipe retrains (Inception,
HRNet-W48, SelfMAD-style HRNet-W18, PW-MAD DenseNet-121, OrthoMAD ResNet-18, MixFaceNet, MixFaceNet official
code); es = early-stopped, last = last checkpoint. AD4 = the morph-free networks experiment, whose
untrained ("zero-step") networks are used here. EER = equal error rate (%); APCER / BPCER = share of morphs
accepted / genuine photos flagged; BPCER_dev = flag rate on the development genuine photos. **Probe** = the
expression probe of the cue checks (C1): logistic regression (C = 0.1, standardised) on a 22 × 36 grey
thumbnail of the lower face of the eye-aligned frame, fit on the 204 FRLL frames, label 08. **Probe-clear
pair** = one photo with probe logit > 0, the other < 0. **Share** = above / (above + below), "above" = the
less-smiling photo (FRLL: the neutral one) gets the higher morph score; ties counted and excluded.

## 1. Question and current answer

Question (lead, 11 Nov ~16:28, after the independent review of C1b): the smiling FRLL photos differ from the
neutral ones not only in expression but also in file size and backdrop noise; which of the two do detectors
read? Status: **finished 11 Nov 17:00 CET; not yet independently reviewed.** Answer: the file facts hold
(smiling files 1.43 times larger and backdrop 4.8 times noisier in 102 of 102 persons, with identical pixel
size, JPEG tables and subsampling); in FERET and FRGC same-session pairs the smile comes without that
capture difference. The released MADation ViT-L/14 orders the FRLL photos almost perfectly (0.99) but
FERET and FRGC pairs only weakly (0.56, 0.57), and its FRLL ordering falls when resolution is removed while
the smile stays visible to the probe: mainly capture detail. Last-checkpoint retrains do not order
other-pool pairs by expression (0.43–0.60); early-stopped retrains (0.60–0.93) and both frozen-encoder
releases (reversed) do. Falsifiers: H1, H2, H3 not falsified (H2 incomplete), H4 falsified. With
neutral-only genuine photos as the headline, the ViT-L/14 release falls from 4th to 7th of 9 releases.

## 2. Timeline (11 Nov 2026, CET)

- ~16:26 Lead's message received. Read `experiments/reviews/REVIEW_C1b_20261111.md` and the reviewer's
  scripts and output in `experiments/reviews/rev_scripts_c1b_20261111/` (`main_out.txt` read in full;
  scripts not run by this owner).
- ~16:28 Listings and manifests only: `eval.csv` genuine variants; `devbona` composition (2,606 FERET
  fa/fb-named, 2,427 FRGC); FRGC naming (`nd1_<season>_<subject>d<n>`); 677 consecutive-number pairs; FERET
  1,268 pairs / 936 subjects; AD4 untrained scores present for ViT-B/16 only (`zero_step/m3l/` empty;
  AD4 result said the ViT-L/14 scorer would finish about 17:30); provenance of `devbona`
  (`smadcvpr/prep_eval.py` l.234–246: `mambamorph-code/dmad/data/probes/{feret,frgc}`) and its overlap with
  our FERET/FRGC-trained arms (PROTOCOL l.9257: 2,178 of 5,033 are training captures).
- 16:30 `prereg.md` written (file time 16:30; its header says 16:35). H1–H4 as fixed by the lead; pair
  definitions, statistics, eye-label plan and reading rule fixed.
- 16:31 `src/C1c/c1c_files.py` smoke (8 persons, 8 pairs per pool) passed; full run 16:31–16:35 in the
  background (log `/mnt/t7/smad_next/C1c/c1c_files.log`).
- 16:33 `src/C1c/c1c_bench.py` (step 4, from C1b outputs) run → `c1c_bench.md`, `c1c_bench.json`.
- 16:35 `src/C1c/c1c_sep.py` written; a syntax slip in its smoke filter fixed (section 7); smoke (3 score sets
  + untrained, B = 50) passed; full run 16:36–16:39 (log `/mnt/t7/smad_next/C1c/c1c_sep.log`).
- 16:36 `src/C1c/c1c_eye_sample.py`: 40 FERET + 20 FRGC probe-clear pairs drawn (seed 20261111), blind list
  written (no probe values).
- 16:37–16:54 Eye labelling of the sample by viewing the aligned frames: an image request limit blocked most
  reads; 29 FERET pairs were viewed and labelled (section 5). The FRGC sample and 11 FERET pairs could not be
  viewed.
- 16:55 `c1c_eye_labels.csv` written; compared with the probe.
- 16:56–16:57 `src/C1c/c1c_variant_probe.py` (probe and region noise on every registered variant) added because
  the pre-registered "capture detail" reading needs "the probe still separates the photos" → 
  `c1c_variant_probe.json`.
- 16:58–17:00 `result.md` written; two fixes in it (recipe means M3L last smiling-only 1.3, M3 last 7.6;
  rank-move sentence). Report sent.
- 17:20–17:55 Documentation pass: reviewer's feature file copied out of the scratchpad, hashes, this README.
  No new statistic. Noted at 17:3x that `zero_step/m3l/scores_eval.npz` now exists; it was not read.

Amendments to the registration: none. Additions after the registration, labelled as such: the variant probe /
noise check (supports the pre-registered reading rule), and the stratification of FERET pairs by tertile of
the probe difference (descriptive).

## 3. Data

| Input | Path | Items | Origin / hash |
|---|---|---|---|
| Raw FRLL photos | `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral,smiling}_front/NNN_0{3,8}.jpg` | 102 + 102 | sha256 list `../C1b/c1b_frll_raw_sha256.csv` |
| Evaluation manifest | `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` | — | sha256 `86d055d3…6c9` (asserted) |
| FRLL aligned frames and registered variants | `smadcvpr_data/eval/frllm/frll_bona/NNN_0{3,8}_{orig,jpeg90,jpeg70,jpeg50,chip,blur1,resample50}.png`; resolution-matched photos `eval/{frllm,dim,mordiff}/<family>/NNN_0x_resmatch_<family>.png`; MorDIFF crop `eval/mordiff/mordiff_bona/…` | 204 per variant (20 variants) | built by `smadcvpr/prep_eval.py`; all stored as 512 × 512 PNG. Resolution matches the family's median morph eye distance: FaceMorpher ≈ 138 px, OpenCV ≈ 130, AMSL ≈ 113, WebMorph ≈ 112, DiM ≈ 63 (256-px morph files), MorDIFF ≈ 65 (152-px files); StyleGAN resmatch = orig |
| FERET pairs | `eval.csv` set `devbona`, files `SSSSS_YYMMDD_fa[_x]_orig.png` / `_fb[_x]_orig.png` | 1,268 pairs, 936 subjects, 445 probe-clear | source `/home/narolski/mambamorph-code/dmad/data/probes/feret/` (2,606 files) |
| FRGC pairs | `devbona` files `nd1_<season>_<subject>d<n>_orig.png`; pair = same subject, same season folder, recording numbers n and n + 1 (non-overlapping, in order) | 677 pairs, 386 subjects, 337 probe-clear | source `/home/narolski/mambamorph-code/dmad/data/probes/frgc/` (2,427 files) |
| Development genuine photos (H4 threshold) | all `devbona` rows, variant orig | 5,033 | as above; 2,178 are training captures of our FERET/FRGC-trained (d1) arms, none of the networks scored here |
| Score files | same 112 files as C1b (`../C1b/c1b_input_scores_sha256.csv`) plus `/mnt/t7/smad_next/AD4/zero_step/m3/scores_eval.npz` (untrained ViT-B/16, key `score`, 19,827 rows of the AD4 manifest) | 113 | sha256 of the AD4 file `a846fbdf5c3f44e338609716dfdf8b7dea53cbcf54cebe54084a47a549853d4b` |
| C1b outputs (step 4) | `../C1b/c1b_read.json`, `/mnt/t7/smad_next/C1b/c1b_eer_bootstrap_reps.npz` | — | sha256 64c6e36e…, 4ca97263… |

FEI pairs: **not used** (not in the task's pool list; see section 9). SelfMAD with its own preprocessing has no
`devbona` scores, so it has no FERET/FRGC rows. No `valx`, `fst` or `A12SP` file opened.

Outputs (experiment folder; sha256 first 12 hex): `prereg.md` (33501d234ae1), `result.md` (d7c68761de41),
`c1c_files.json` (644e1d6e4e27; step 2 tables), `c1c_frll_files.csv` (2974e44d5104; per person raw and frame
statistics and probe logits), `c1c_probe_logits.csv` (f9ff5c9b1e42; probe logit of all 4,094 frames read),
`c1c_feret_pairs.csv` (05c2cafcabb5) and `c1c_frgc_pairs.csv` (1df357985637): every pair with ids, paths,
probe logits, probe-clear flag and probe direction (for the author's labelling), `c1c_sep.json` (46c4b38a8fa0)
and `c1c_sep.csv` (73cc4e96d047; every score set × check with counts and intervals), `c1c_variant_probe.json`
(1dcb52b3ef6b), `c1c_bench.md` (1be8e4539a5c), `c1c_bench.json` (f3b7a386f9a7), `c1c_eye_sample_blind.csv`
(31b6a116080a), `c1c_eye_labels.csv` (26c267add5c8). Large / logs in `/mnt/t7/smad_next/C1c/`:
`c1c_files.log`, `c1c_sep.log`, and the reviewer's covariate file copied out of the scratchpad
(`reviewer_c1b_feats.npz`, 11.2 MB, ce81fd970649; its script `reviewer_c1b_feats.py`). Copies: DGX and the T7
drive only.

## 4. Code

Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I` (Python 3.12.3, numpy 1.26.4, scipy
1.17.1, scikit-learn 1.9.0, Pillow 12.2.0). No model weights loaded. Seed 20261111 everywhere.

1. `src/C1c/c1c_files.py [--smoke]` (sha256 9877e904…) — step 2: raw FRLL headers (bytes, size, JPEG
   quantisation tables, subsampling) and backdrop noise (mean squared finite difference of the grey image in
   120 × 120 boxes 20 px from the top corners); frame region statistics (background 5:90 × 5:40 and
   5:90 × 472:507, forehead 90:150 × 200:310, mouth 300:432 × 150:366); probe logits for all frames (imports
   `src/C_cue_checks/c_checks.py` `stats_job`, sha256 00d6e627…); FERET and FRGC pair lists. 8 workers.
2. `src/C1c/c1c_bench.py` (7683d74d…) — step 4 tables from the C1b outputs.
3. `src/C1c/c1c_sep.py [--smoke]` (c377c8f3…) — step 3 and H4; reuses `src/C1b/c1b_read.py` `detectors()`;
   subject or person cluster bootstrap B = 10,000; H4 thresholds as in `smadcvpr/analyze.py`
   `operating_points` (threshold = quantile of the devbona scores at 1 − target; flag = score > threshold).
4. `src/C1c/c1c_eye_sample.py` (f83df994…) — draws the 60-pair blind sample.
5. `src/C1c/c1c_variant_probe.py` (8356415e…) — probe ordering and region noise on 9 variants (imports
   `c1c_files.frame_job`).

## 5. Results

### Falsifiers

| Hypothesis (fixed by the lead) | Measured | Verdict |
|---|---|---|
| H1: M3 last orders by detail, not expression: share ≤ 0.60 on other-pool pairs; falsified if ≥ 5 of 8 reach 0.65 | FERET probe-clear per seed 0.544, 0.524, 0.490, 0.569, 0.535, 0.555, 0.530, 0.490 (0 of 8 ≥ 0.65); FRGC 0.44–0.60 | not falsified, prediction met (post hoc) |
| H2: (i) ≥ 10 of 13 es retrains ≥ 0.60 on those pairs; (ii) AD4 untrained networks ≥ 0.15 from 0.5 (FRLL) | (i) 13 of 13: M3 es 0.719, 0.755, 0.6045, 0.688, 0.618, 0.640, 0.647, 0.667; M3L es 0.629, 0.688, 0.737, 0.708, 0.640. (ii) untrained ViT-B/16 0.814 (83 / 19 / 0) | not falsified, incomplete (ViT-L/14 untrained missing at analysis) |
| H3: ViT-L/14 release ≤ 0.60; falsified ≥ 0.80 | FERET 0.564 [0.519, 0.611] (251 / 194 / 0); FRGC 0.570 [0.516, 0.622] (192 / 145 / 0) | not falsified, prediction met (post hoc); both lower bounds > 0.5 |
| H4: flag-rate change < 1 point at BPCER_dev 5% (ViT-L/14 release) | all 3.43%, neutral-only 5.88%, smiling-only 0.98% (6 vs 1 of 102); +2.45 [+0.49, +4.90]; at 1%: 0; at 10%: +3.43 [+0.98, +5.88] | falsified |

H4 for the other releases at BPCER_dev 5% (neutral-only minus all, points): ViT-B/16 +0.98 [0, +2.45]; FE ViT-B/16
−0.98 [−2.45, 0]; FE ViT-L/14 0.00 [−1.96, +1.96]; FS ViT-B/16 +0.49; FS ViT-L/14 +0.98 [0, +2.45]; SelfMAD (our
pipeline) 0; MixFaceNet 0 (`c1c_sep.json` → `h4`).

### Step 2: file and frame facts (102 persons; `c1c_files.json`, `c1c_frll_files.csv`)

| Property | Neutral median | Smiling median | Persons smiling > neutral | Median ratio (range) |
|---|---|---|---|---|
| Raw file size | 380,968 B | 554,759 B | 102 | 1.43 (1.25–1.88) |
| Raw backdrop noise, top-left | 0.67 | 3.18 | 102 | 4.81 (2.74–9.77) |
| Raw backdrop noise, top-right | 0.69 | 3.23 | 102 | 4.65 (2.47–11.52) |
| Raw backdrop standard deviation, top-left / top-right | 2.88 / 2.87 | 3.20 / 3.09 | 96 / 89 | 1.09 / 1.11 |
| Raw whole-image noise | 25.8 | 32.1 | 100 | 1.29 |
| Frame backdrop noise, top-left / top-right | 0.49 / 0.54 | 2.47 / 2.55 | 98 / 100 | 4.86 / 4.60 |
| Frame forehead noise | 23.9 | 36.0 | 98 | 1.46 |
| Frame mouth noise | 47.1 | 71.8 | 98 | 1.49 |
| Frame luminance (backdrop, forehead, mouth) | 209 / 165 / 136 | 210 / 166 / 134 | 70 / 57 / 53 | 1.00 |
| Frame file size | 317,513 B | 380,866 B | 102 | 1.19 |

Identical in 102 of 102 pairs: pixel size 1350 × 1350, the JPEG quantisation tables (one table set for all
204 files), chroma subsampling 4:2:0. In-sample probe: smiling above neutral in 102 of 102.

Other pools (probe-clear pairs; share = more-smiling photo has the larger value; median ratio more/less):
FERET (445 pairs): backdrop noise 0.47 / 0.56 (0.97 / 1.05), forehead 0.54 (1.01), mouth 0.84 (1.35), file
size 0.60 (1.01), luminance 0.39–0.47. FRGC (337): backdrop 0.56 / 0.59 (1.07 / 1.12), forehead 0.50 (1.00),
mouth 0.51 (1.00), file size 0.56 (1.00), mouth luminance 0.06 (0.92: the smiling mouth region is darker).
Probe smile-like rates: FERET fa 0.397, fb 0.569; FRGC first photo of a pair 0.037, second 0.532.

Variants of the 204 FRLL photos (`c1c_variant_probe.json`; probe = share of persons with smiling probe logit
above neutral; noise = share smiling > neutral, median ratio):

| Variant | Probe | Backdrop noise TL / TR | Forehead | Mouth |
|---|---|---|---|---|
| orig | 1.00 | 0.96 ×4.86 / 0.98 ×4.60 | 0.96 ×1.46 | 0.96 ×1.49 |
| JPEG 50 | 1.00 | 0.24 ×0.63 / 0.22 ×0.59 | 0.44 ×0.97 | 0.74 ×1.16 |
| blur | 1.00 | 0.95 ×3.01 / 0.97 ×3.01 | 0.82 ×1.09 | 0.91 ×1.37 |
| half resolution | 1.00 | 0.96 ×2.54 / 0.97 ×2.52 | 0.66 ×1.04 | 0.86 ×1.36 |
| FaceMorpher-matched | 1.00 | 0.95 ×3.34 / 0.98 ×3.14 | 0.89 ×1.15 | 0.95 ×1.37 |
| AMSL-matched | 1.00 | 0.95 ×2.92 / 0.97 ×2.69 | 0.81 ×1.10 | 0.93 ×1.38 |
| DiM-matched | 1.00 | 0.95 ×1.85 / 0.97 ×1.70 | 0.36 ×0.97 | 0.87 ×1.37 |
| MorDIFF-matched | 1.00 | not measurable (zero-border corners) | 0.43 ×0.98 | 0.90 ×1.36 |
| MorDIFF crop, full resolution | 1.00 | not measurable | 0.94 ×1.47 | 0.97 ×1.50 |

### Step 3: separation checks (every score set; `c1c_sep.csv` has all rows with counts and intervals)

Releases and the untrained network, FRLL variants, share (above / below / tied in brackets for the first):
see `result.md` table; key rows: ViT-L/14 release orig 0.99 (101/1/0), JPEG 50 0.89, blur 0.96, half
resolution 0.95, FaceMorpher-matched 0.97, AMSL-matched 0.93, DiM-matched 0.78 (80/22/0), MorDIFF crop 0.79
(81/21/0), MorDIFF-matched 0.53 (54/48/0). ViT-B/16 release 0.58 → 0.25 (DiM-matched). FE ViT-B/16 0.04–0.16
throughout; FE ViT-L/14 0.21–0.39; FS ViT-B/16 0.54–0.70; FS ViT-L/14 0.44–0.53; SelfMAD own 0.33–0.48; SelfMAD
our pipeline 0.15–0.41; MixFaceNet 0.40–0.56; untrained ViT-B/16 0.81 (orig), 0.75 (DiM-matched), 0.65
(MorDIFF-matched).

Releases on other pools, share [95% subject bootstrap] (above / below / tied):

| Release | FERET probe-clear | FRGC probe-clear | FERET all | FRGC all | FERET tertiles of probe difference |
|---|---|---|---|---|---|
| ViT-L/14 | 0.564 [0.519, 0.611] (251/194/0) | 0.570 [0.516, 0.622] (192/145/0) | 0.545 [0.517, 0.573] | 0.597 [0.559, 0.632] | 0.51 / 0.56 / 0.57 |
| ViT-B/16 | 0.485 [0.439, 0.532] (216/229/0) | 0.472 [0.419, 0.523] | 0.499 | 0.483 | 0.53 / 0.50 / 0.46 |
| FE ViT-B/16 | 0.321 [0.279, 0.364] (143/302/0) | 0.463 [0.407, 0.521] | 0.388 | 0.428 | 0.49 / 0.40 / 0.27 |
| FE ViT-L/14 | 0.382 [0.336, 0.429] (170/275/0) | 0.193 [0.150, 0.239] (65/272/0) | 0.421 | 0.257 | 0.45 / 0.44 / 0.37 |
| FS ViT-B/16 | 0.501 [0.454, 0.549] | 0.457 [0.403, 0.512] | 0.507 | 0.476 | 0.53 / 0.50 / 0.48 |
| FS ViT-L/14 | 0.476 [0.430, 0.524] | 0.582 [0.528, 0.635] | 0.506 | 0.555 | 0.51 / 0.51 / 0.50 |
| SelfMAD, our pipeline | 0.555 [0.507, 0.602] | 0.561 [0.507, 0.615] | 0.543 | 0.533 | 0.51 / 0.55 / 0.57 |
| MixFaceNet, our frames | 0.593 [0.546, 0.640] | 0.558 [0.504, 0.611] | 0.543 | 0.542 | 0.52 / 0.54 / 0.57 |

Recipes, per seed (ranges): M3 es FRLL 0.84–0.99, DiM-matched mean 0.88, MorDIFF-matched 0.34, FERET
0.60–0.76, FRGC 0.55–0.93; M3L es 0.81–0.96, 0.88, 0.22, 0.63–0.74, 0.83–0.88; M3 last 0.67–0.97, 0.33,
0.57, 0.49–0.57, 0.44–0.60; M3L last 1.00, 0.99, 0.86, 0.45–0.54, 0.43–0.58; M4 last FRLL 0.00 with 70–94 of
102 persons tied (saturated), DiM-matched 0.11, MorDIFF-matched 0.16, FERET 0.50–0.55, FRGC 0.43–0.48; other
CNN recipes FRLL 0.25–0.65, FERET 0.31–0.64, FRGC 0.33–0.70 (M8 last up to 0.64 / 0.70). Saturation (ties >
10% of pairs): M4 on FRLL; M1 s2 es on FRGC (103 of 337); M8O s2/s5 es on FRGC (19 each) below the 10% mark.

Eye labels (`c1c_eye_labels.csv`): 29 FERET probe-clear pairs viewed (00170_931230 to 01006_960627 in the
sample order); the eye's "more smiling" photo agrees with the probe in 25 of 25 pairs with a visible
difference; 4 pairs show no visible difference (00612_940928, 00729_941205, 00732_960530, 00936_960627;
probe logits 0.43 / −1.35, 1.86 / −0.01, −0.27 / 0.01, −2.62 / 0.19). Labeller: this AI owner, blind to probe
values; not ground truth.

### Step 4: benchmark tables, neutral-only genuine photos as headline (`c1c_bench.md`)

Mean EER over the 11 scored imbalanced cells (12th, corrected MAD22 Webmorph, has no scores), 95% two-way
person bootstrap:

| Release | neutral-only [95%] | rank | all [95%] | rank | smiling-only | change [95%] |
|---|---|---|---|---|---|---|
| SelfMAD own preprocessing | 3.9 [2.4, 5.5] | 1 | 5.3 [3.5, 7.3] | 1 | 6.6 | −1.43 [−2.48, −0.52] |
| SelfMAD our pipeline | 11.6 [9.1, 13.9] | 2 | 13.9 [11.4, 16.7] | 2 | 16.7 | −2.22 [−3.67, −1.41] |
| FE ViT-L/14 | 13.7 [10.7, 16.7] | 3 | 14.6 [11.7, 17.5] | 3 | 15.6 | −0.88 [−2.31, +0.29] |
| ViT-B/16 | 16.8 [14.1, 19.3] | 4 | 16.2 [13.8, 18.2] | 5 | 15.2 | +0.57 [−0.21, +1.71] |
| FE ViT-B/16 | 18.3 [14.6, 21.8] | 5 | 27.7 [24.0, 31.0] | 7 | 35.4 | −9.42 [−11.51, −7.35] |
| FS ViT-B/16 | 19.3 [15.6, 23.2] | 6 | 20.1 [16.2, 23.3] | 6 | 20.6 | −0.78 [−2.12, +1.07] |
| ViT-L/14 | 20.2 [17.2, 23.5] | 7 | 15.6 [13.1, 18.4] | 4 | 8.7 | +4.55 [+3.42, +5.81] |
| FS ViT-L/14 | 40.7 [35.9, 45.0] | 8 | 41.1 [37.2, 45.0] | 8 | 41.5 | −0.37 [−3.32, +2.16] |
| MixFaceNet, our frames | 57.1 [53.2, 61.0] | 9 | 57.4 [53.5, 61.5] | 9 | 57.7 | −0.26 [−1.20, +0.46] |

Recipes (seed means, neutral-only / all / smiling-only): M3L last 21.5 / 14.6 / 1.3; M3L es 11.5 / 9.8 / 7.1;
M3 last 9.9 / 8.9 / 7.6; M3 es 10.8 / 8.4 / 5.2; the rest in `c1c_bench.md`. Per-cell EER and per-cell ranks
of the releases, and BPCER at APCER 5% (neutral-only / all / smiling-only): `c1c_bench.md`.

### Reading per detector group (pre-registered rule)

ViT-L/14 release: mainly capture detail (falls with resolution while the probe still separates the photos;
other pools 0.56–0.57, within 0.40–0.60). M3 last: capture detail. M3L last: neither (no other-pool reading,
no fading with resolution). M3 / M3L es: expression. FE releases: expression, reversed. ViT-B/16 and FS
releases, SelfMAD, MixFaceNet, CNN recipes: no consistent reading.

## 6. Checks

Verified: smoke runs of every script; manifest hash asserted for every score file; the FRLL file facts
reproduce the reviewer's (1.43, about five times); the release shares reproduce the reviewer's preview on
the same pairs where ties are absent (ViT-L/14 0.564; FE ViT-B/16 0.321); the step 4 interval for the
ViT-L/14 change [3.42, 5.81] equals the reviewer's 3.4 to 5.8; the probe direction agrees with blind eye
labels in 25 of 25 viewed pairs with a visible difference; the FRGC pairing is consistent with a
neutral-then-smiling capture order (3.7% vs 53% smile-like).

Not verified: FRGC pairing against FRGC metadata; eye labels for the FRGC sample and 11 FERET pairs (not
viewable); H2 (ii) for ViT-L/14; which capture property the ViT-L/14 release reads (JPEG 50 reverses the
backdrop ordering, yet the release keeps 0.89, so backdrop noise alone does not explain it); no independent
review of C1c yet.

## 7. Dead ends, failures, corrected and withdrawn statements

- **Correction of the reviewer's ladder wording** (made in `result.md`): "0.53 at about 150 px" is on
  MorDIFF's crop, whose own full-resolution value is 0.79; the same-crop drops are 0.99 → 0.78 (FRLL crop,
  256-px files) and 0.79 → 0.53 (MorDIFF crop).
- **Ties were counted as half in C1b**; here they are counted and excluded. This exposed that M4 ranks the
  smiling FRLL photo higher in every untied pair (its earlier 0.34–0.46 came from 70–94 ties).
- **Eye labelling only partly done:** repeated image reads returned "request limit" for the first 11 FERET
  pairs and all 20 FRGC pairs of the sample; only 29 of 60 were labelled. The blind sample file is kept for the
  author.
- **Bug fixed before the full run:** the smoke filter of `c1c_sep.py` contained `d[2 if False else 4]`; replaced
  by `d[4]` (it selects the untrained networks; the full run never used the filter).
- **Missing values, expected:** backdrop noise on MorDIFF-crop variants is not measurable (corners are zero
  border; numpy "mean of empty slice" warnings in the variant run).
- **H2 incomplete:** the untrained ViT-L/14 scores did not exist at analysis time (`zero_step/m3l/` empty);
  they exist now and were not read (no new experiments in this pass).
- **Pre-registration header time** says 16:35 while the file was written at 16:30; it was written before any
  C1c computation (first smoke at 16:31).
- From C1b, withdrawn in light of this study: "the expression cue is used" and "only the expression
  differs" (see `../C1b/README.md`, section 7).

## 8. Observations and ideas

- The untrained ViT-B/16 network (frozen CLIP, random head) already orders the FRLL photos at 0.81: the two
  photo types lie apart in pretrained CLIP feature space before any morph training.
- M3L last keeps 0.99 at the DiM-matched resolution and 0.86 at the MorDIFF-matched one while reading nothing
  in FERET / FRGC: an FRLL-specific property that survives downsampling (the backdrop-noise ratio is still
  1.85 at 256 px).
- JPEG 50 reverses the backdrop-noise ordering (0.24) but the ViT-L/14 release still orders the photos at
  0.89.
- FRGC smiling mouths are darker (mouth luminance lower in 94% of probe-clear pairs), FERET's not as much;
  luminance is a possible confound for probe labels in FRGC.
- FE ViT-L/14 reads smiles in reverse much more strongly in FRGC (0.19) than FERET (0.38).
- In 4 of 29 viewed FERET probe-clear pairs the expressions look the same: the probe's logits there are near
  0 for one photo, so a stricter margin (|logit| > 0.5) would clean the pair set.

## 9. Open items and next steps

- Read the untrained ViT-L/14 scores (`/mnt/t7/smad_next/AD4/zero_step/m3l/scores_eval.npz`) to complete H2 (ii).
- Author labels for `c1c_eye_sample_blind.csv` (60 pairs) or more pairs from `c1c_feret_pairs.csv` /
  `c1c_frgc_pairs.csv`.
- A third same-session two-expression pool: FEI frontal neutral / smiling photos (in `gtest.csv`: 198 neutral,
  187 smiling per `10_ASSET_INVENTORY.md`; `scores_gtest*.npz` exist for releases and recipes). Not used here.
- The half-exchange test (upper part of one photo with the lower part of the other) to separate expression
  from capture detail; needs the author's ruling on pixel copies.
- Corrected MAD22 Webmorph once scored (WCSS job 6299123).
- Independent review of C1c.

## 10. Handover state

Nothing running; nothing queued; no file in progress. Compute: CPU only on the DGX, about 10 minutes of
wall time over 8 processes; 0 GPU-hours; 0 USD. Scratchpad-only files copied in this pass:
`/mnt/t7/smad_next/C1c/reviewer_c1b_feats.npz` and `reviewer_c1b_feats.py` (the reviewer's covariates for its
C1b preview).

## 11. Reproduce from scratch

```bash
cd /home/narolski/smad-next
PY="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
# needs the C1b outputs (../C1b/README.md, section 11)
$PY src/C1c/c1c_files.py --smoke && $PY src/C1c/c1c_files.py      # step 2, pair lists, probe logits (~4 min)
$PY src/C1c/c1c_bench.py                                           # step 4
$PY src/C1c/c1c_sep.py --smoke && $PY src/C1c/c1c_sep.py          # step 3 and H4 (~3 min)
$PY src/C1c/c1c_variant_probe.py                                   # probe and noise on the variants
$PY src/C1c/c1c_eye_sample.py                                      # blind 60-pair sample
```
