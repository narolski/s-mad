# MorDIFF ladder re-read of the A43 scores (AD1, step 1): full record

Owner: hypothesis-owner agent (Opus), 11 Nov 2026. Lead: Fable. This README is the full record;
`result.md` is the short verdict. Related: the diffusion-autoencoder identical/mirror-input study (AD1b),
`/home/narolski/smad-next/experiments/AD1b/README.md`.

Terms used throughout. MorDIFF = published diffusion-morph benchmark built on FRLL (Face Research Lab
London) photos. DiffAE = diffusion autoencoder (the generator family behind MorDIFF). AUC = area under the
ROC curve (0.5 = chance). EER = equal error rate. E7 = the approved control that gives genuine photos
the morphs' shrink-and-enlarge (resolution) history. Ladder rungs (from `11_AUDIT_PLAN.md`): R0 camera
photo, R1 history-matched photo, R2 one-photo reconstruction ("pipeline only"), R3 same-person mix
("twin"), R4 two-person morph. d′ = √2·Φ⁻¹(AUC).

## 1. Question and current answer

Status: **finished** (11 Nov 2026, about 14:40 CET), reviewed the same day (independent review
`experiments/reviews/REVIEW_AD1_AG5_C_20261111.md`, verdict "accept-qualified"). Post hoc: A43's
aggregate table was read before the preregistration.

Question: for each released detector, is the MorDIFF result carried by processing steps (camera photo →
history-matched photo → reconstruction) or by morphing (reconstruction → same-person mix → two-person
morph)? Answer, in the review's corrected wording: **as scored in our pipeline, our same-pair 20-step
DiffAE morphs are not ranked above one-photo reconstructions rendered and stored identically** —
0.480 (MADation ViT-B/16 release), 0.486 (ViT-L/14 release), 0.403 (SelfMAD release, own preprocessing),
upper bounds ≤ 0.59. Our morphs are indistinguishable from the published ones (0.48–0.51). **Exception:
the released MADation FE ViT-L/14 (frozen encoder, trained head) does read the mixing step** (0.655
[0.580, 0.730] at 20 steps, 0.852 at 100 steps) without separating reconstructions from camera photos.
All cells are descriptive: the published MorDIFF error is not reproduced on our frames (gate G-a).

## 2. Timeline

- 11 Nov ~14:22: task received from the lead (AD1 step 1, AG5, C1–C4). Read `OWNER_BRIEF.md`,
  `11_AUDIT_PLAN.md`, `08_CUE_MATRIX.md`, `10_ASSET_INVENTORY.md`, `NOTEBOOK.md`, `12_STATE_AT_HANDOVER.md`.
- ~14:25: read the A43 ledger (`/home/narolski/mambamorph-code/experiments/A43_mordiff-two-by-two/README.md`)
  and `smadcvpr/results/A43/a43_read.md` (aggregate AUCs known from here on, hence "post hoc").
- ~14:28: located per-image scores (`/mnt/t7/smad_heldout/a43/a43_out/a43/*/*/scores_a43.npz`, 8 files,
  2,024 ids each) and the E7 scores (registered eval files). Located `a41_read.py` (not on main; copies in
  the worktrees `/home/narolski/mambamorph-code-a44/smadcvpr/a41_read.py`, sha 0bc7381b…) and its
  bootstrap (class `Draw`, `a36_read.wauc`).
- ~14:30: checked whether MixFaceNet-MAD could be added: the A46 RGB-only scorer is bound to its own plan,
  manifest and data pins and requires the H100 → not added.
- ~14:33: wrote `prereg.md` (before opening any per-image score).
- ~14:35: wrote `src/AD1/ad1_read.py`; smoke on 8 rows per arm (`--smoke`), then full run (49 s CPU).
  Reproduction check against A43 passed exactly.
- ~14:40: wrote `src/AD1/ad1_expr.py` (expression split, descriptive) and ran it.
- ~14:55: wrote `result.md`; handed back.
- 11 Nov afternoon: independent review (results-reviewer) → corrections listed in sections 5 and 7.
- 11 Nov ~17:30: documentation pass (this README). Added `src/AD1/ad1_flagrates.py` (CPU re-read of the
  same scores) to print the flag rates and storage-alone numbers the review asked for; output
  `ad1_flagrates.json`; added `inputs_sha256.txt`.

No amendment to the registration besides the deviations listed in section 7.

## 3. Data

No image was generated and nothing was rescored. Inputs (sha256 of every input file in
`/home/narolski/smad-next/experiments/AD1/inputs_sha256.txt`):

| Item | Path | n | Origin |
|---|---|---|---|
| A43 manifest | `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv` (sha ce3a264a…) | 2,024 rows | A43 build (`a43_build.py` f7b2f4a0…, 7 Nov 2026) |
| A43 per-image scores | `/mnt/t7/smad_heldout/a43/a43_out/a43/<release>/<mode>/scores_a43.npz`, releases madation_vitb16, madation_vitl14, madation_fe_vitb16, madation_fe_vitl14, madation_fs_vitb16, madation_fs_vitl14 (mode rel), selfmad_hrnet_w18 (rel and own) | 8 files × 2,024 | WCSS job 6264652 (A43 copy-back, 7 Nov) |
| Eval manifest | `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` (sha 86d055d3…) | 44,666 | registered eval set (only its MorDIFF rows are used here) |
| E7 / registered eval scores | `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/<release>/scores_eval.npz`; SelfMAD own: `/home/narolski/mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz` (sha b2e012b9…) | 44,666 / 26,077 ids | A12REL / A32 scoring |
| Identity cosines and FMR 1e-3 threshold | `/mnt/t7/smad_heldout/a43/data/a43_stats.json` (sha 31b459d1…), manifest columns `cos_stored_raw_a/b` | — | A43 build (glintr100) |

Ladder mapping (A43 arm → rung): R0 = `mordiff_bona` eval rows (204 FRLL photos, registered frames);
R1 = eval rows `set=mordiff, family=mordiff, variant=resmatch` (204, the E7 MorDIFF pool); R2 = D20
(204 reconstructions, 20 steps); R3 = C20 (102 same-person mixes of p_03 neutral + p_08 smiling);
R4 = B20 (200 same-pair morphs, 20 steps; 100 neutral pairs, 100 smiling pairs); benchmark R4 =
`A_reg` (200 sampled published MorDIFF morphs, registered frames) and arm A (the same 200 in A43
storage, identical scores). Descriptive: D (100-step reconstructions), E (204 photos through DiffAE's
aligner and A43 storage, about 141 px wide), B and C (100 steps). Images of every arm:
`/mnt/t7/smad_heldout/a43/data/a43/{frames,stored}/<arm>/`. Nothing dropped.

Outputs (experiment folder): `ad1_ladder.json` (91cc8d01…), `ad1_ladder.csv` (1eda9ec7…),
`ad1_expr_split.json` (4fb23fd4…), `ad1_flagrates.json` (35373e56…).

## 4. Code

| Script | sha256 | Job |
|---|---|---|
| `/home/narolski/smad-next/src/AD1/ad1_read.py` | 01443f0e… | ladder contrasts, d′ shares, verdicts, G-a, G-b, twin flag rates; writes `ad1_ladder.{json,csv}` |
| `/home/narolski/smad-next/src/AD1/ad1_expr.py` | cec3f87e… | expression-split contrasts (descriptive); writes `ad1_expr_split.json` |
| `/home/narolski/smad-next/src/AD1/ad1_flagrates.py` | b9378e52… | documentation check: flag rates at the EER and 1%-photo thresholds, storage-alone comparison; writes `ad1_flagrates.json` |

Run order: `ad1_read.py` (optionally `--smoke`), then `ad1_expr.py`, then `ad1_flagrates.py`. Environment:
`/home/narolski/mambamorph-code/.venv-spark/bin/python -I` (Python 3.12.3, numpy 1.26.4, scipy 1.17.1),
CPU only. Bootstrap: re-implementation of `a41_read.py`'s pigeonhole (dyadic) person bootstrap (Owen 2007):
per replicate persons ~ Multinomial(102, 1/102); a photo weighs its person's count, a morph the product of
its two contributors' counts, a same-person row its person's count; one draw shared by all arms; weighted
Mann-Whitney AUC as `a36_read.wauc`; B = 10,000; seed [20261107, 43, 1] (A43's, so A43's intervals are
reproduced). Folded AUC = 0.5 + |AUC − 0.5| with bounds from the replicates. Shares = step d′ / d′(R0 vs
published). Model weights: none loaded (score re-read only).

## 5. Results

All AUCs with 95% two-way person-bootstrap intervals; n per arm as in section 3. Source:
`ad1_ladder.json` / `.csv` unless stated.

### 5.1 Ladder, primary rows

| Step | ViT-B/16 release | ViT-L/14 release | SelfMAD own prep. | SelfMAD our pipeline (desc.) |
|---|---|---|---|---|
| Benchmark R0 vs published | 0.986 [0.970, 0.997] | 0.825 [0.746, 0.896] | 0.994 [0.983, 1.000] | 0.977 [0.954, 0.993] |
| Bridge published vs B20 | 0.505 [0.473, 0.539] | 0.486 [0.458, 0.509] | 0.481 [0.448, 0.513] | 0.478 [0.449, 0.499] |
| R0 → R1 (E7) | 0.894 [0.863, 0.924] | 0.645 [0.616, 0.681] | 0.997 [0.992, 1.000] | 0.985 [0.973, 0.995] |
| R1 → R2 | 0.917 [0.891, 0.942] | 0.743 [0.719, 0.772] | 0.426 [0.391, 0.459] | 0.414 [0.381, 0.443] |
| R0 → R2 | 0.992 [0.982, 0.999] | 0.877 [0.848, 0.907] | 0.996 [0.990, 1.000] | 0.982 [0.966, 0.994] |
| R2 → R3 | 0.266 [0.216, 0.315] | 0.444 [0.396, 0.492] | 0.678 [0.629, 0.727] | 0.683 [0.637, 0.730] |
| R3 → R4 | 0.706 [0.625, 0.785] | 0.541 [0.422, 0.652] | 0.252 [0.186, 0.323] | 0.290 [0.213, 0.371] |
| **Main R2 vs R4 (B20 vs D20)** | **0.480 [0.382, 0.578]** | **0.486 [0.384, 0.588]** | **0.403 [0.324, 0.487]** | 0.460 [0.372, 0.549] |
| R2 vs published (A vs D20) | 0.487 [0.381, 0.594] | 0.471 [0.369, 0.573] | 0.379 [0.305, 0.457] | 0.436 [0.355, 0.518] |
| R4 ours vs R0 (B20 vs R0) | 0.988 [0.974, 0.997] | 0.836 [0.759, 0.904] | 0.994 [0.984, 1.000] | 0.978 [0.956, 0.993] |
| E vs R0 (desc.) | 0.856 [0.823, 0.889] | 0.625 [0.601, 0.652] | 1.000 [0.999, 1.000] | 0.995 [0.990, 0.999] |
| D (100 steps) vs R0 (desc.) | 0.896 | 0.742 | 0.996 | 0.990 |
| C20 vs R0 (desc.) | 0.934 | 0.841 | 0.998 | 0.991 |

100-step versions (from A43's table, `smadcvpr/results/A43/a43_read.md`): main B vs D 0.366 (ViT-B/16),
0.515 (ViT-L/14), 0.293 (SelfMAD own).

d′ shares of the benchmark separation (point [95%]) — **the review asks to drop these from prose** (they
exceed 1 and do not add up); kept here for the record:

| Share | ViT-B/16 | ViT-L/14 | SelfMAD own | SelfMAD pipe |
|---|---|---|---|---|
| R0 → R1 | 0.57 [0.49, 0.65] | 0.40 [0.29, 0.57] | 1.04 [1.00, 1.16] | 1.09 [1.00, 1.19] |
| R1 → R2 | 0.63 [0.55, 0.71] | 0.70 [0.52, 0.98] | −0.07 [−0.12, −0.04] | −0.11 [−0.16, −0.07] |
| R0 → R2 | 1.10 [0.99, 1.23] | 1.24 [0.94, 1.73] | 1.04 [1.00, 1.13] | 1.05 [0.97, 1.15] |
| R2 → R4 (main) | −0.02 [−0.15, 0.08] | −0.04 [−0.43, 0.19] | −0.10 [−0.20, −0.01] | −0.05 [−0.18, 0.06] |

### 5.2 Descriptive release variants (FE = frozen encoder, FS = full fine-tune)

| Step | FE ViT-B/16 | **FE ViT-L/14** | FS ViT-B/16 | FS ViT-L/14 |
|---|---|---|---|---|
| Benchmark | 0.640 [0.542, 0.733] | 0.703 [0.632, 0.772] | 0.249 [0.174, 0.333] (reversed) | 0.617 [0.537, 0.696] |
| R0 → R2 | 0.607 | **0.561 [0.528, 0.597]** | 0.310 | 0.484 |
| Main R2 vs R4 | 0.532 [0.432, 0.626] | **0.655 [0.580, 0.730]** | 0.502 | 0.584 [0.499, 0.670] |
| R3 → R4 | 0.544 | 0.653 [0.562, 0.741] | 0.514 | 0.541 |
| R2 → R3 | 0.493 | 0.498 | 0.489 | 0.546 |
| Main at 100 steps (A43 table) | 0.572 | **0.852** | 0.531 | 0.569 |

**Correction (review, 11 Nov):** my `result.md` summarised these variants only as "none separates the
benchmark above 0.71". That omitted the one release that reads the mixing step: FE ViT-L/14 separates
morphs from reconstructions (0.655 at 20 steps, 0.852 at 100 steps) without separating reconstructions
from camera photos (0.561; 0.459 at 100 steps). The sentence "no released detector reads the morph step"
is false and must not be used. The review also reports that FE ViT-L/14 separates same-person mixes
from reconstructions at 0.721 and does not transfer to StyleGAN3 (0.505); both are the reviewer's
numbers (`experiments/reviews/rev_scripts_20261111/ad1_fe.py`, `ag5_fe.py`), not recomputed by me.

### 5.3 Verdicts under the fixed rules (all cells descriptive by G-a)

| Detector | Main (R2 vs R4) | Side R3 vs R4 | Side R2 vs R3 |
|---|---|---|---|
| ViT-B/16 release | reads the benchmark (rule fired on both arms: share lower bound 0.99; folded 0.52, UB 0.62) | mixed (0.71) | ~~twin artefact, cell invalid~~ → **renamed (review): "non-monotone rung; same-person mix confounded by expression"** (0.27, UB 0.32: reconstructions above same-person mixes) |
| ViT-L/14 release | reads the benchmark (share LB 0.94; folded 0.51, UB 0.62) | mixed (0.54; folded UB 0.653) | no identity reading (0.44) |
| SelfMAD own | reads the benchmark (share LB 1.00 only; folded UB 0.676 misses the folded arm) | twin artefact, cell invalid (0.252, UB 0.32; = A43) | mixed (0.68) |
| SelfMAD pipe (desc.) | reads the benchmark | twin artefact, cell invalid (0.290) | mixed (0.68) |
| FE ViT-L/14 (desc.) | mixed (0.655; share 0.29 [0.15, 0.44]) | mixed (0.653) | no identity reading |

**Correction (review):** the "reads the benchmark" label rests partly on d′ shares that exceed 1; the
review's wording to use instead is the AUC statement in section 1 plus the flag rates in 5.4.

### 5.4 Flag rates at fixed thresholds (`ad1_flagrates.json`, added 11 Nov 17:30)

Threshold = each detector's EER threshold on R0 vs the 200 published morphs (EER 5.4% / 26.0% / 2.0%);
second threshold = the score flagging about 1% of untouched photos (99th percentile of R0, strict >;
3 of 204 = 1.5% because of ties).

| Share flagged | ViT-B/16 EER-thr / 1%-thr | ViT-L/14 | SelfMAD own | SelfMAD pipe |
|---|---|---|---|---|
| R0 photos | 0.054 / 0.015 | 0.260 / 0.015 | 0.020 / 0.015 | 0.064 / 0.015 |
| R1 E7 photos | **0.539 / 0.132** | **0.510 / 0.123** | **0.980 / 0.877** | 0.966 / 0.652 |
| E (photo stored at published size) | 0.417 / 0.088 | 0.431 / 0.074 | **0.995 / 0.985** | 0.995 / 0.863 |
| D20 reconstructions | 0.995 / 0.779 | 0.824 / 0.368 | 0.985 / 0.873 | 0.956 / 0.515 |
| C20 same-person mixes | 0.745 / 0.480 | 0.765 / 0.343 | 0.990 / 0.941 | 0.980 / 0.775 |
| B20 our morphs | 0.935 / 0.725 | 0.745 / 0.400 | 0.980 / 0.775 | 0.930 / 0.465 |
| Published morphs | 0.945 / 0.730 | 0.740 / 0.390 | 0.980 / 0.750 | 0.935 / 0.455 |

**Correction (review):** the earlier summary sentence "51 to 98 percent [of history-matched photos] are
flagged" is withdrawn because it omitted the baseline; corrected: E7 raises the share flagged from 5% to
54% (ViT-B/16), 26% to 51% (ViT-L/14), 2% to 98% (SelfMAD); at the 1%-photo threshold 13%, 12%, 88%.
Twins (C20) at the EER threshold, exact 95%: ViT-B/16 76/102 = 0.75 [0.65, 0.83]; ViT-L/14 78/102 = 0.76
[0.67, 0.84]; SelfMAD own 101/102 = 0.99 [0.95, 1.00].

**Storage alone (review point, my recomputation):** for SelfMAD own preprocessing a genuine photo merely
stored at the published size (arm E) outranks a published MorDIFF morph in 90.5% of pairs (review: 89%;
small difference in definition not resolved), and 203 of 204 such photos are flagged at the EER threshold.

### 5.5 Gates

- G-a (reproduction): EER on R0 vs the 200 sampled published morphs: ViT-B/16 5.4% (A41 on all 1,000:
  4.9%) vs 1.10% published; ViT-L/14 26.0% (A41: 28.9%) vs 19.3%; SelfMAD own 2.0%, no published MorDIFF
  number in the record → every cell "not reproduced, descriptive".
- G-b (twin validity, glint cosines from the A43 manifest, computed before scores): oracle AUC morph vs
  twin (lower minimum cosine to the two source photos = morph) 1.000; B20 verifies against both
  contributors at FMR 1e-3 (threshold 0.2394) in 99.5%; C20 verifies against A in 100% → pass. The
  negative control twin(A, A′) vs twin(A′, A) does not exist (one twin per person).
- G-c (probe readability): not done (assigned to FZ1).

### 5.6 Expression split (descriptive, `ad1_expr_split.json`)

| Contrast | ViT-B/16 | ViT-L/14 | SelfMAD own | SelfMAD pipe |
|---|---|---|---|---|
| Main, neutral only | 0.444 [0.312, 0.580] | 0.475 [0.343, 0.606] | 0.408 [0.307, 0.519] | 0.462 |
| Main, smiling only | 0.510 [0.394, 0.625] | 0.495 [0.378, 0.612] | 0.398 [0.295, 0.505] | 0.459 |
| R3 → R4, neutral B20 | 0.646 [0.536, 0.756] | 0.523 | 0.259 [0.181, 0.340] | 0.273 |
| R3 → R4, smiling B20 | 0.765 [0.674, 0.844] | 0.558 | 0.246 [0.163, 0.337] | 0.306 |
| R2 → R3, D20 neutral / smiling | 0.299 / 0.233 | 0.451 / 0.437 | 0.677 / 0.678 | 0.700 / 0.666 |

## 6. Checks

Verified: (i) my bootstrap reproduces A43's printed numbers exactly (ViT-B/16 R3m 0.480 [0.382, 0.578],
R2m 0.706 [0.625, 0.785], R1m 0.505 [0.473, 0.539], R0m 0.487 [0.381, 0.594]; SelfMAD own R2m 0.252;
SelfMAD pipe 0.290); (ii) manifest sha256 inside every score file equals the manifest's; score ids equal
manifest ids in order; (iii) R0 scores in the A43 file vs the eval file for the same 204 frames: max
|Δ| 0 (ViT-B/16, FE/FS), 3e-12 (ViT-L/14), 4.2e-4 (SelfMAD own), 2.8e-4 (SelfMAD pipe), so R1 from the eval
files is combinable; (iv) the independent reviewer recomputed every number from the per-image files and
found them matching; (v) flag rates in 5.4 match the review's figures.
Not verified: the SelfMAD release's published MorDIFF EER; the meaning of MorDIFF's real generation
settings (the 20-step match is relative to 20 vs 100 steps); G-c; any detector other than the eight
release rows; MixFaceNet-MAD on these images.

## 7. Dead ends and failures

- MixFaceNet-MAD could not be added: `smadcvpr/a46_rgb_score.py` requires its own plan, manifest
  `a46_rgb_only.csv`, data pins (`verify_data(..., require_complete=True)`) and the registered H100;
  no MixFaceNet per-image scores of the A43 arms exist.
- `a41_read.py` is not on the main checkout; I re-implemented its `Draw` + `wauc` (identical code) in
  `ad1_read.py` rather than importing it (its import pulls in registration guards); equivalence shown by
  reproducing A43 exactly.
- Statements corrected or withdrawn by the independent review (11 Nov), each with the corrected wording:
  1. "None of the FE/FS variants separates the benchmark above 0.71" (true but incomplete) → add that
     FE ViT-L/14 reads the mixing step (0.655 / 0.852); "no released detector reads the morph step" is
     false. Reason: the summary looked only at benchmark separation, not at the main contrast.
  2. ViT-B/16 R2 vs R3 label "twin artefact, cell invalid" → "non-monotone rung; same-person mix
     confounded by expression". Reason: the rule targets R3 vs R4; R2 vs R3 is confounded by the
     neutral+smiling mix.
  3. Verdict wording based on d′ shares (shares 1.04–1.24) → drop shares from prose; use the AUCs against
     the camera photo and flag rates at fixed thresholds. Reason: shares exceed 1 and do not add.
  4. "51 to 98 percent of history-matched photos are flagged" → withdrawn; corrected rates with the R0
     baseline in 5.4.
- No bugs found in the code after the smoke run.

## 8. Observations and ideas

- Arm E (photo only passed through DiffAE's aligner and stored at the published file size, about 141 px)
  already scores far above R0 for every primary detector (ViT-B/16 0.856, SelfMAD own 1.000): storage at
  the published size alone moves them, before any diffusion step.
- SelfMAD's R1 → R2 step is negative (reconstructions score slightly below E7 photos): for SelfMAD the
  whole separation sits in the resolution history.
- The step count acts on every arm the same way (A43: D20 vs D 0.87, B20 vs B 0.90, C20 vs C 0.79 for
  ViT-B/16), so a detector's MorDIFF number depends on how many decoding steps the generator used.
- FE ViT-L/14 is the only release whose ranking follows the morphing step and not the processing step; it
  is the natural candidate for the frozen-feature probe (FZ1) and for a positive control in later ladders.

## 9. Open items and next steps

- Expression-matched twins (R2x, never built in A43): the planned second AD1 step (about 2 GPU-h).
- Re-score the MorDIFF ladder with the own-crop RGB scorer so that the benchmark number reproduces
  (review follow-up; WCSS slot task not yet staged).
- Second photo pool (AD3). MixFaceNet-MAD on these images needs a registered scoring path.
- Identical and mirror inputs to the DiffAE morph: AD1b (separate README).

## 10. Handover state

No process running for AD1. Compute: CPU only, under 2 minutes in total; 0 GPU-hours; 0 USD. Nothing
in /tmp or a scratchpad is needed (all code in `src/AD1/`, all outputs in this folder).

## 11. Reproduce from scratch

```bash
cd /home/narolski/smad-next
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
sha256sum -c <(sed 's/ /  /' experiments/AD1/inputs_sha256.txt)        # inputs unchanged
$PY -I src/AD1/ad1_read.py --smoke                                     # 8 rows per arm, prints only
$PY -I src/AD1/ad1_read.py                                             # -> experiments/AD1/ad1_ladder.{json,csv}
$PY -I src/AD1/ad1_expr.py                                             # -> experiments/AD1/ad1_expr_split.json
CUDA_VISIBLE_DEVICES= $PY -I src/AD1/ad1_flagrates.py                  # -> experiments/AD1/ad1_flagrates.json
```
