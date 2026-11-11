# What the smiling half carries: expression or capture detail (C1c) — result

Owner run, 11 Nov 2026, DGX CPU only, zero GPU, no image written or re-encoded. Pre-registration
`prereg.md` (16:35 CET). Code `src/C1c/`: `c1c_files.py` (file and frame statistics, probe logits, pair
lists), `c1c_sep.py` (separation checks, H4), `c1c_variant_probe.py` (probe and noise on the registered
variants), `c1c_bench.py` (benchmark tables from the stored outputs of the expression cue use study (C1b)),
`c1c_eye_sample.py`. Outputs here: `c1c_files.json`, `c1c_frll_files.csv`, `c1c_sep.json`, `c1c_sep.csv`
(every score set × every check, with counts), `c1c_variant_probe.json`, `c1c_bench.md`, `c1c_bench.json`,
`c1c_feret_pairs.csv`, `c1c_frgc_pairs.csv`, `c1c_probe_logits.csv`, `c1c_eye_sample_blind.csv`,
`c1c_eye_labels.csv`. Logs in `/mnt/t7/smad_next/C1c/`.

**Abbreviations.** FRLL = Face Research Lab London set (102 persons; 03 = neutral photo, 08 = smiling
photo). FERET = colour FERET (fa = regular, fb = alternative expression, same session). FRGC = Face
Recognition Grand Challenge 2.0 stills. CLIP = the pretrained image–text model; ViT-B/16 and ViT-L/14 =
its two vision transformers. MADation = CLIP fine-tuned with low-rank adapters for morph detection; FE =
frozen-encoder variant (head only trained); FS = from-scratch variant. M3 / M3L = our retrains of the
MADation recipe on ViT-B/16 / ViT-L/14; es = early-stopped checkpoint, last = last checkpoint. M1, M2,
M4, M5, M6, M8, M8O = our CNN recipe retrains (Inception, HRNet-W48, SelfMAD-style HRNet-W18, PW-MAD
DenseNet, OrthoMAD ResNet, MixFaceNet, MixFaceNet official code). EER = equal error rate; APCER / BPCER =
share of morphs accepted / genuine photos flagged. **Share** = above / (above + below), where "above" =
pairs in which the less-smiling (FRLL: neutral) photo gets the higher morph score; ties are counted
separately and excluded. "Probe" = the FRLL-trained expression probe of the cue checks (C1); probe-clear
pair = one photo with probe logit > 0, the other < 0. Probe labels are not ground truth.

**Post hoc parts.** The reviewer's preview numbers were seen before the pre-registration (FERET
probe-clear shares of releases, M3/M3L es and last, FRGC 0.51, the ladder 0.99 / 0.78 / 0.53). H1, H3
and part (i) of H2 are therefore post hoc; new here are ties excluded, the FRGC same-session pairing,
H2 (ii), H4, the eye labels, all recipe rows the reviewer did not print, and the file statistics.

## Verdicts on the fixed falsifiers

| Hypothesis | Measured | Verdict |
|---|---|---|
| H1: last-checkpoint ViT-B/16 retrains (M3 last) do not order other-pool pairs by expression (share ≤ 0.60; falsified if ≥ 5 of 8 reach 0.65) | FERET probe-clear: 0.544, 0.524, 0.490, 0.569, 0.535, 0.555, 0.530, 0.490; 0 of 8 ≥ 0.65, 8 of 8 ≤ 0.60 (FRGC 0.44–0.60) | **not falsified; prediction met** (post hoc) |
| H2: near-pretrained CLIP features order by expression: (i) ≥ 10 of 13 es retrains ≥ 0.60 on FERET probe-clear pairs; (ii) the untrained networks of the morph-free networks experiment (AD4) ≥ 0.15 from 0.5 on FRLL | (i) 13 of 13 (lowest M3 s3 es 0.6045; range 0.60–0.76); (ii) untrained ViT-B/16 0.814 (83 above / 19 below); untrained ViT-L/14 scores not yet written | **not falsified, incomplete** ((ii) on ViT-B/16 only; (i) post hoc) |
| H3: the ViT-L/14 release does not read expression (≤ 0.60; falsified ≥ 0.80) | FERET probe-clear 0.564 [0.519, 0.611] (251 / 194 / 0 ties); FRGC 0.570 [0.516, 0.622] | **not falsified; prediction met** (post hoc). Both lower bounds are above 0.5 |
| H4: at a threshold fixed on the development genuine photos (devbona, BPCER_dev 5%) the ViT-L/14 release's flag rate changes by < 1 point, neutral-only vs all | flag rate on the 204 FRLL frames: all 3.43%, neutral-only 5.88%, smiling-only 0.98% (6 vs 1 of 102 photos); change **+2.45 points [+0.49, +4.90]**. At BPCER_dev 1%: 0 / 0. At 10%: +3.43 [+0.98, +5.88] | **falsified** |

Caveat on H2 (ii): FRLL is the pool where expression and detail are mixed, and an untrained network's head
is random, so its 0.81 shows that the two FRLL photos lie apart in CLIP feature space; it does not say
which property separates them.

## Step 2. What differs between the neutral and the smiling FRLL photo

Raw files (`frll_base/extracted`, 102 persons):

| Property | Neutral (03) median | Smiling (08) median | Persons with 08 > 03 | Median ratio 08/03 (range) |
|---|---|---|---|---|
| File size (bytes) | 380,968 | 554,759 | **102 of 102** | **1.43** (1.25–1.88) |
| Backdrop noise, top-left 120 × 120 px (mean squared finite difference) | 0.67 | 3.18 | **102 of 102** | **4.81** (2.74–9.77) |
| Backdrop noise, top-right | 0.69 | 3.23 | 102 of 102 | 4.65 (2.47–11.52) |
| Backdrop standard deviation, top-left | 2.88 | 3.20 | 96 of 102 | 1.09 |
| Whole-image noise | 25.8 | 32.1 | 100 of 102 | 1.29 |

Identical in all 102 pairs: pixel size (1350 × 1350), JPEG quantisation tables (one table set for all 204
files) and chroma subsampling (4:2:0).

Our aligned 512 frames, by region: backdrop noise 08/03 ratio 4.9 (top-left, 98 of 102 persons higher) and
4.6 (top-right); forehead 1.46 (98 of 102); mouth 1.49 (98 of 102); mean luminance equal (ratios
1.00–1.004); frame file size 1.19 (102 of 102).

The same statistics in the other pools, more-smiling vs less-smiling photo (probe-clear pairs):

| Pool | pairs | backdrop noise: share more-smiling higher (ratio) | forehead noise | mouth noise | file size |
|---|---|---|---|---|---|
| FRLL | 102 | 0.96–0.98 (4.6–4.9) | 0.96 (1.46) | 0.96 (1.49) | 1.00 (1.19) |
| FERET fa/fb | 445 | 0.47 / 0.56 (0.97 / 1.05) | 0.54 (1.01) | 0.84 (1.35) | 0.60 (1.01) |
| FRGC same-session | 337 | 0.56 / 0.59 (1.07 / 1.12) | 0.50 (1.00) | 0.51 (1.00) | 0.56 (1.00) |

So in FERET and FRGC the smile comes without the FRLL backdrop and forehead difference: these pools
separate expression from that capture difference. FRGC pairing check: the first photo of a consecutive
pair is smile-like in 3.7% (probe), the second in 53%, consistent with a neutral-then-smiling capture
order; this was not checked against FRGC metadata.

Registered variants of the 204 FRLL photos (`c1c_variant_probe.json`): the probe orders the smiling
photo above the neutral one in **102 of 102 persons in every variant** (JPEG 50, blur, half-resolution,
every resolution-matched set, MorDIFF crop). The backdrop-noise difference shrinks with resolution
(ratio 4.9 at full resolution, 2.5 at half resolution, 1.85 at the 256-px DiM-matched set; not measurable
on MorDIFF's crop, whose corners are zero border), and the forehead difference disappears at the DiM and
MorDIFF resolutions (share 0.36 / 0.43, ratio 0.97 / 0.98). JPEG 50 reverses the backdrop ordering
(share 0.24, ratio 0.63).

## Step 3. Separation checks (all 111 score sets plus the untrained ViT-B/16; full table `c1c_sep.csv`)

Releases and the untrained network: share (above / below / tied) on the FRLL variants:

| Detector | FRLL frames | JPEG 50 | blur | half res. | FaceMorpher-matched (≈138 px eye distance) | AMSL-matched (≈113) | DiM-matched (256-px file, ≈63) | MorDIFF crop, full res. | MorDIFF-matched (152-px file, ≈65) |
|---|---|---|---|---|---|---|---|---|---|
| MADation ViT-L/14 release | **0.99** (101/1/0) | 0.89 | 0.96 | 0.95 | 0.97 | 0.93 | **0.78** (80/22/0) | 0.79 (81/21/0) | **0.53** (54/48/0) |
| MADation ViT-B/16 release | 0.58 (59/43/0) | 0.48 | 0.49 | 0.41 | 0.43 | 0.50 | 0.25 | 0.53 | 0.34 |
| MADation FE ViT-B/16 release | 0.09 (9/93/0) | 0.04 | 0.08 | 0.08 | 0.07 | 0.08 | 0.08 | 0.10 | 0.16 |
| MADation FE ViT-L/14 release | 0.34 (35/67/0) | 0.33 | 0.32 | 0.35 | 0.35 | 0.36 | 0.39 | 0.21 | 0.28 |
| MADation FS ViT-B/16 release | 0.54 | 0.56 | 0.57 | 0.63 | 0.60 | 0.61 | 0.62 | 0.66 | 0.70 |
| MADation FS ViT-L/14 release | 0.50 | 0.51 | 0.50 | 0.51 | 0.51 | 0.49 | 0.53 | 0.52 | 0.44 |
| SelfMAD release, own preprocessing | 0.48 (49/53/0) | 0.44 | – | 0.41 | 0.33 | 0.39 | 0.46 | 0.42 | 0.46 |
| SelfMAD release, our pipeline | 0.31 | 0.38 | 0.16 | 0.16 | 0.19 | 0.15 | 0.29 | 0.41 | 0.36 |
| MixFaceNet-MAD release, our frames | 0.47 | 0.40 | 0.45 | 0.42 | 0.43 | 0.43 | 0.47 | 0.53 | 0.56 |
| Untrained ViT-B/16 (AD4, zero-step) | 0.81 (83/19/0) | – | – | – | 0.83 | 0.81 | 0.75 | 0.67 | 0.65 |

Correction to the reviewer's ladder wording: the "about 150 px" value (0.53) is on MorDIFF's crop, whose
own full-resolution value is 0.79. Same-crop resolution drops are 0.99 → 0.78 (FRLL crop) and
0.79 → 0.53 (MorDIFF crop).

Other pools, releases: share [95% subject bootstrap] (above / below / tied):

| Detector | FERET probe-clear (445 pairs) | FRGC probe-clear (337) | FERET all pairs (1,268) | FRGC all (677) | FERET by tertile of probe difference |
|---|---|---|---|---|---|
| MADation ViT-L/14 release | 0.564 [0.519, 0.611] (251/194/0) | 0.570 [0.516, 0.622] (192/145/0) | 0.545 [0.517, 0.573] | 0.597 [0.559, 0.632] | 0.51 / 0.56 / 0.57 |
| MADation ViT-B/16 release | 0.485 [0.439, 0.532] | 0.472 [0.419, 0.523] | 0.499 | 0.483 | 0.53 / 0.50 / 0.46 |
| MADation FE ViT-B/16 release | **0.321** [0.279, 0.364] | 0.463 [0.407, 0.521] | 0.388 | 0.428 | 0.49 / 0.40 / 0.27 |
| MADation FE ViT-L/14 release | **0.382** [0.336, 0.429] | **0.193** [0.150, 0.239] | 0.421 | 0.257 | 0.45 / 0.44 / 0.37 |
| MADation FS ViT-B/16 release | 0.501 | 0.457 | 0.507 | 0.476 | 0.53 / 0.50 / 0.48 |
| MADation FS ViT-L/14 release | 0.476 | 0.582 [0.528, 0.635] | 0.506 | 0.555 | 0.51 / 0.51 / 0.50 |
| SelfMAD release, our pipeline | 0.555 [0.507, 0.602] | 0.561 [0.507, 0.615] | 0.543 | 0.533 | 0.51 / 0.55 / 0.57 |
| MixFaceNet-MAD release, our frames | 0.593 [0.546, 0.640] | 0.558 [0.504, 0.611] | 0.543 | 0.542 | 0.52 / 0.54 / 0.57 |

SelfMAD with its own preprocessing has no FERET or FRGC scores (its own-crop file covers the benchmark
rows only). No ties in any release row.

Recipes (per seed; FERET and FRGC on probe-clear pairs; "saturated" = ties above 10% of pairs):

| Recipe, ckpt | FRLL frames | DiM-matched (mean) | MorDIFF-matched (mean) | FERET | FRGC |
|---|---|---|---|---|---|
| M3 es | 0.84–0.99 | 0.88 | 0.34 | 0.60–0.76 (all 8 lower bounds > 0.5) | 0.55–0.93 |
| M3L es | 0.81–0.96 | 0.88 | 0.22 | 0.63–0.74 (all 5 > 0.5) | 0.83–0.88 |
| **M3 last** | 0.67–0.97 | **0.33** | 0.57 | **0.49–0.57** | 0.44–0.60 |
| **M3L last** | 1.00 (all 5) | **0.99** | **0.86** | **0.45–0.54** | 0.43–0.58 |
| M1 last / es | 0.45–0.54 / 0.44–0.63 | 0.54 / 0.46 | 0.57 / 0.55 | 0.49–0.59 / 0.52–0.55 | 0.47–0.61 / 0.49–0.60 (es s2 saturated, 103 ties) |
| M2 last / es | 0.48–0.63 / 0.43–0.63 | 0.54 / 0.52 | 0.60 / 0.64 | 0.54–0.57 / 0.53–0.58 | 0.48–0.62 / 0.49–0.66 |
| M4 last / es | **0.00** (saturated: 70–94 of 102 tied) / 0.00 (0–70 tied) | 0.11 / 0.11 | 0.16 / 0.15 | 0.50–0.55 / 0.48–0.54 | 0.43–0.48 / 0.45–0.53 |
| M5 last / es | 0.25–0.61 / 0.28–0.67 | 0.56 / 0.70 | 0.45 / 0.46 | 0.31–0.55 / 0.35–0.51 | 0.33–0.58 / 0.47–0.59 |
| M6 last / es | 0.48–0.65 / 0.48–0.58 | 0.58 / 0.57 | 0.59 / 0.59 | 0.51–0.61 / 0.52–0.56 | 0.47–0.58 / 0.55–0.62 |
| M8 last / es | 0.44–0.62 / 0.43–0.63 | 0.60 / 0.57 | 0.59 / 0.58 | 0.51–0.64 / 0.43–0.63 | 0.53–0.70 / 0.51–0.64 |
| M8O last / es | 0.43–0.61 / 0.45–0.58 | 0.47 / 0.49 | 0.50 / 0.59 | 0.46–0.54 / 0.55–0.63 | 0.49–0.62 / 0.53–0.65 |

The SelfMAD-style retrains (M4) rank the smiling FRLL photo higher in every untied pair (this was hidden
when ties counted as half), and still do so at low resolution (0.11–0.16), but not in FERET or FRGC
(0.43–0.55). M4 is reversed on the benchmarks overall (mean EER 89 in C1b), so it is descriptive.

**Eye labels** (the owner, an AI agent, viewing the two aligned frames of each pair without the probe
values; not ground truth): 29 of the 40 sampled FERET probe-clear pairs could be viewed (an image request
limit stopped the rest; the 20 FRGC sample pairs were not viewed). Probe direction agrees with the eye in
**25 of 25** pairs with a visible difference; 4 of 29 show no visible difference (`c1c_eye_labels.csv`).
The full pair lists with paths and probe logits are `c1c_feret_pairs.csv` and `c1c_frgc_pairs.csv`;
`c1c_eye_sample_blind.csv` is the 60-pair sample without probe values, for the author.

## Step 4. Benchmark tables, neutral-only genuine photos as the headline

Imbalanced cells: 12 (DiM ×6, FRLL-Morphs ×5, corrected MAD22 Webmorph); 11 scored (no detector score on
the corrected MAD22). Mean EER over the 11 cells, 95% two-way person bootstrap (C1b replicates, B = 2,000):

| Release | **EER, neutral-only genuine** [95%] | rank | EER, all genuine [95%] | rank | EER, smiling-only | change neutral-only − all [95%] |
|---|---|---|---|---|---|---|
| SelfMAD release, own preprocessing | **3.9** [2.4, 5.5] | 1 | 5.3 [3.5, 7.3] | 1 | 6.6 | −1.43 [−2.48, −0.52] |
| SelfMAD release, our pipeline | **11.6** [9.1, 13.9] | 2 | 13.9 [11.4, 16.7] | 2 | 16.7 | −2.22 [−3.67, −1.41] |
| MADation FE ViT-L/14 release | **13.7** [10.7, 16.7] | 3 | 14.6 [11.7, 17.5] | 3 | 15.6 | −0.88 [−2.31, +0.29] |
| MADation ViT-B/16 release | **16.8** [14.1, 19.3] | 4 | 16.2 [13.8, 18.2] | 5 | 15.2 | +0.57 [−0.21, +1.71] |
| MADation FE ViT-B/16 release | **18.3** [14.6, 21.8] | 5 | 27.7 [24.0, 31.0] | 7 | 35.4 | −9.42 [−11.51, −7.35] |
| MADation FS ViT-B/16 release | **19.3** [15.6, 23.2] | 6 | 20.1 [16.2, 23.3] | 6 | 20.6 | −0.78 [−2.12, +1.07] |
| MADation ViT-L/14 release | **20.2** [17.2, 23.5] | 7 | 15.6 [13.1, 18.4] | 4 | 8.7 | **+4.55 [+3.42, +5.81]** |
| MADation FS ViT-L/14 release | **40.7** [35.9, 45.0] | 8 | 41.1 [37.2, 45.0] | 8 | 41.5 | −0.37 [−3.32, +2.16] |
| MixFaceNet-MAD release, our frames | **57.1** [53.2, 61.0] | 9 | 57.4 [53.5, 61.5] | 9 | 57.7 | −0.26 [−1.20, +0.46] |

Per-cell EER (neutral-only / all / smiling-only), per-cell ranks, BPCER at APCER 5% and the recipe
seed means are in `c1c_bench.md`. Examples, ViT-L/14 release: AMSL 24.5 / 17.7 / 7.9; FRLL-Morphs StyleGAN
65.7 / 52.4 / 34.3; DiM-A 27.4 / 22.0 / 10.8. FE ViT-B/16 release: AMSL 17.6 / 26.0 / 35.3. Recipes:
M3L last 21.5 / 14.6 / 1.3 (mean neutral-only / all / smiling-only), M3 last 9.9 / 8.9 / 7.6, M3L es
11.5 / 9.8 / 7.1, M3 es 10.8 / 8.4 / 5.2.

Rank moves under the neutral-only headline: the ViT-L/14 release falls from 4th to 7th of 9, the FE
ViT-B/16 release rises from 7th to 5th, and the ViT-B/16 release rises from 5th to 4th. The first three
(SelfMAD own preprocessing, SelfMAD our pipeline, FE ViT-L/14) and the last three are unchanged.

## What moved, and the evidence per detector group

| Group | FRLL ordering | With resolution removed (smile still visible to the probe in 102 of 102) | Other pools (expression without the FRLL capture difference) | Reading by the pre-registered rule |
|---|---|---|---|---|
| MADation ViT-L/14 release | 0.99 | 0.78 (FRLL crop), 0.53 (MorDIFF crop, from 0.79) | 0.56 FERET, 0.57 FRGC (both lower bounds > 0.5, both < 0.60) | **capture detail** for most of the FRLL ordering (falls toward 0.5 with resolution; other pools 0.40–0.60); a small expression-direction ordering remains elsewhere |
| M3 last (8) | 0.67–0.97 | 0.33 (DiM-matched, reversed), 0.57 | 0.49–0.57 / 0.44–0.60 | **capture detail** |
| M3L last (5) | 1.00 | 0.99, 0.86 | 0.45–0.54 / 0.43–0.58 | **neither**: not expression (other pools at 0.5), but it does not fade with resolution either; something FRLL-specific that survives downsampling (the backdrop-noise ratio is still 1.85 at 256 px) |
| M3 es, M3L es (13) | 0.81–0.99 | 0.88 (DiM-matched); reversed on MorDIFF's crop (0.22–0.34) | 0.60–0.76 / 0.55–0.93, all FERET lower bounds > 0.5 | **expression** (with an unexplained reversal on MorDIFF's crop) |
| MADation FE ViT-B/16, FE ViT-L/14 releases | 0.09, 0.34 | stable (0.07–0.16; 0.21–0.39) | 0.32 / 0.46 and 0.38 / 0.19 | **expression, reversed** (smiling looks more morph-like); FE ViT-B/16 in FERET only |
| MADation ViT-B/16, FS ViT-B/16, FS ViT-L/14 releases | 0.50–0.58 | 0.25–0.70, no pattern | 0.46–0.58 | no consistent reading |
| SelfMAD release | own 0.48; our pipeline 0.31 | 0.33–0.46; 0.15–0.41 | our pipeline 0.555 / 0.561 | undetermined (FRLL direction opposite to other pools) |
| CNN recipes | 0.25–0.65 (M4: 0.00, saturated) | mostly 0.45–0.60; M4 0.11–0.16 | mostly 0.45–0.65 | no consistent reading; M4 reads something FRLL-specific, not expression |

What moved the benchmark numbers: removing the smiling half raises the ViT-L/14 release's mean EER by
4.5 points and lowers the FE ViT-B/16 release's by 9.4; for the release whose number moves most (ViT-L/14),
the evidence points mainly to the capture difference that rides with the smiling photos, not to the smile.
At a threshold fixed on independent development photos the same release flags 6 of 102 neutral and 1 of
102 smiling FRLL photos (H4 falsified: +2.45 points, not < 1).

## Proposed cue-table wording (`08_CUE_MATRIX.md`, row 15; not applied)

Replace the C1b proposal for row 15a with:

- **Name:** "Smiling half of the FRLL genuine class: expression together with a capture difference (the
  smiling files are 1.43 times larger and their backdrop 4.8 times noisier in 102 of 102 persons; same
  pixel size, JPEG tables and subsampling)".
- **In the files?** "Yes in 12 of 17 cells (DiM ×6, FRLL-Morphs ×5, corrected MAD22 Webmorph): the morphs
  are built from the neutral photos only, half the genuine class is the smiling photos (C1, C1b)".
- **Does a detector use it?** "The smiling half moves benchmark numbers (matched comparison: neutral-only
  vs all genuine photos, 11 scored cells): MADation ViT-L/14 release +4.5 EER points (20.2 vs 15.6), FE
  ViT-B/16 release −9.4 (18.3 vs 27.7), others within ±2.2 (C1b, C1c). Which property is read differs by
  network: the ViT-L/14 release and last-checkpoint retrains order the two FRLL photos almost perfectly
  but other pools weakly or not at all (FERET / FRGC 0.56 / 0.57 for the release, 0.43–0.60 for the
  retrains), and the release's ordering falls with resolution while the smile stays visible (0.99 → 0.78;
  0.79 → 0.53 on MorDIFF's crop): mainly the capture difference. Early-stopped retrains (FERET 0.60–0.76,
  FRGC 0.55–0.93) and the frozen-encoder releases (reversed, FERET 0.32 / 0.38) order expression in other
  pools too. No intervention isolates expression from the capture difference (half-exchange test pending
  the author's ruling)."
- **Status:** "PRESENT, USE UNTESTED (expression as such)"; evidence column: "benchmark numbers depend on
  the smiling half (matched comparison, C1b/C1c); use headline EER with neutral-only genuine photos".
- Row 15b (balanced cells) unchanged from the C1b proposal (ABSENT).

## What could not be verified

- Probe labels are not ground truth. Eye labels cover 29 of 60 sampled pairs (FERET only), by an AI owner.
- The FRGC same-session pairing is an operational rule (consecutive recording numbers in one season
  folder), not checked against FRGC metadata.
- H2 (ii) is incomplete: the untrained ViT-L/14 network's scores were not written at analysis time; the
  untrained networks were not scored on FERET or FRGC.
- SelfMAD with its own preprocessing has no FERET / FRGC scores.
- `devbona` (the development photos used for H4 and as the FERET / FRGC pairs) contains 2,178 captures that
  are training data of our FERET / FRGC-trained arms; none of the scored networks used them (all are
  SMDD-trained), but the H4 threshold is not from a sealed set.
- Which capture property (backdrop noise, sharpness, file history) the ViT-L/14 release and M3L last read
  is not isolated; JPEG 50 reverses the backdrop ordering yet the release keeps 0.89, so backdrop noise
  alone does not explain it.
- The corrected MAD22 Webmorph cell has no detector scores.
