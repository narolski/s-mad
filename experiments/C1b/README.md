# Is the expression imbalance of the benchmarks used by detectors? (C1b) — full record

Owner: hypothesis-owner agent (Claude), for Paweł Narolski. Written 11 Nov 2026, 17:45 CET, as the
documentation pass the author asked for at 17:20. Short verdict: `result.md` (with a correction line at
its top). Follow-up study: "What the smiling half carries: expression or capture detail" (C1c),
`../C1c_smiling-half-expression-or-detail/README.md`.

**Abbreviations.** FRLL = Face Research Lab London set: 102 persons, photo type 03 = neutral frontal, 08 =
smiling frontal, 1350 × 1350 JPEG. MAD = morphing attack detection. CLIP = OpenAI's pretrained image–text
model; ViT-B/16 and ViT-L/14 = its two vision transformers. MADation = CLIP fine-tuned with low-rank
adapters (LoRA) for morph detection (released weights); FE = its frozen-encoder variant (only the head is
trained), FS = its from-scratch variant. SelfMAD and MixFaceNet-MAD = two other released detectors. M1 …
M8O = our re-implementations ("recipes") of published detectors trained on the synthetic SMDD set: M1
Inception-MAD, M2 MorphHRNet-style (HRNet-W48), M3 MADation ViT-B/16, M3L MADation ViT-L/14, M4
SelfMAD-style (HRNet-W18), M5 PW-MAD (DenseNet-121), M6 OrthoMAD (ResNet-18), M8 MixFaceNet-MAD, M8O
MixFaceNet-MAD with the official code. es = early-stopped checkpoint, last = last checkpoint. EER = equal
error rate (%); APCER = share of morphs accepted as genuine; BPCER = share of genuine photos flagged as
morphs; AUC = area under the ROC curve (0.5 = chance). AUC_wp = within-person neutral-above-smiling AUC
(defined in section 5). Corrected MAD22 = the author's re-uploaded complete SYN-MAD 2022 set (4,687
images), as opposed to the old 185 + 4,069 subset that must not be used.

## 1. Question and current answer

Question (11 Nov, from the lead): in 12 of 17 benchmark cells the genuine class is half smiling FRLL photos
while the morphs are built from neutral photos only; do detectors use that imbalance? Status:
**finished 11 Nov 15:45 CET; its causal reading was corrected by the independent review (16:25) and by C1c
(17:00).** What stands: removing the smiling half of the genuine class changes benchmark numbers by
detector-specific amounts: the released MADation ViT-L/14's mean EER over 11 scored cells rises by 4.5
points (15.6 → 20.2), the released frozen-encoder ViT-B/16's falls by 9.4 (27.7 → 18.3), and rankings
move. The pre-registered falsifiers came out as: H1 (CLIP-based MADation retrains score the neutral FRLL
photo above the smiling one) not falsified, 13 of 13; H2 (short training keeps them at ≤ 0.60) falsified.
What was **withdrawn**: that this shows "the expression cue is used". The smiling FRLL photos also differ in
capture detail (files 1.43 times larger, backdrop 4.8 times noisier in 102 of 102 persons), and C1c shows
that for the ViT-L/14 release and the last-checkpoint retrains the ordering is mainly that capture
difference, not the smile. The five corrected-MAD22 cells could not be tested (no scores exist).

## 2. Timeline (11 Nov 2026, CET)

- ~15:15 Task received from the lead. Read `OWNER_BRIEF.md`, `NOTEBOOK.md`, `11_AUDIT_PLAN.md`,
  `10_ASSET_INVENTORY.md`, `12_STATE_AT_HANDOVER.md`, `experiments/C_cue_checks/result.md` (cue checks C1–C4),
  `08_CUE_MATRIX.md` row 15, and the reviewer's preview scripts `expr_use.py`, `expr_recipes.py` (copies now in
  `/home/narolski/smad-next/experiments/reviews/rev_scripts_20261111/`; their outputs were not seen, only the
  numbers quoted in the task).
- ~15:18 Inventory by listing only (no score values): every primary recipe network has both
  `scores_eval_es.npz` and `scores_eval_last.npz`; `/mnt/t7/wcss_backups/smadcvpr/runs/A12BR/` holds weights
  only. Corrected MAD22: no scores (canonical164 production cancelled; WCSS job 6299123 pending, start forecast
  13 Nov per `/tmp/opencode/wcss-partition-amendment-state.md`). `frll_bona` and `dim_bona` frames are
  byte-identical (sha1 204 of 204); `mordiff_bona` is a different crop (0 of 204).
- 15:23 `prereg.md` written (file time 15:23; header says 15:25). Fixed H1, H2, statistics (a)–(c), probe
  validation rule, cue-matrix reading rule.
- ~15:24 Documentary sources read: FRLL-Morphs `README.txt`, `preprocess.py`, `protocols/`; FRLL `.tem`
  landmark files counted; DiM README; web check of the FRLL-Morphs paper (arXiv 2012.05344, abstract page
  and PDF).
- 15:27 `src/C1b/c1b_read.py` written; smoke run (2 detectors, 2 cells, B = 50) reproduced the reviewer
  preview: ViT-L/14 release AMSL EER 17.65 all / 24.51 neutral-only; 101 of 102 persons.
- 15:28 Full run started in the background; worker pool reduced from 12 to 8 before the start because the
  DGX load average was 87–143. Log `/mnt/t7/smad_next/C1b/c1b_read.log`.
- 15:28–15:30 `src/C1b/c1b_probe.py` written; smoke on 8 images per family passed; full run 15:30–15:39
  (log `/mnt/t7/smad_next/C1b/c1b_probe.log`).
- 15:32 Reader done (111 score sets × 12 cells); `src/C1b/c1b_summarize.py` written and run →
  `c1b_summary.txt`; rerun at 15:39 with the probe tables.
- 15:35–15:45 `result.md` written; small numeric fixes in it (ViT-L/14 BPCER change 13.7 not 15.6; EER
  change 4.5 not 4.6; "2–4 places on all six DiM cells"). Report sent to the lead.
- 16:25 Independent review `experiments/reviews/REVIEW_C1b_20261111.md`: all numbers recomputed and matching;
  causal wording not supported (section 7). Follow-up C1c assigned and run 16:30–17:00.
- 17:20–17:45 Documentation pass (this file): input hash manifests (`src/C1b/c1b_manifest.py`), text of the
  FRLL-Morphs paper extracted and the quotes re-checked, scratchpad-only files copied, correction line added
  at the top of `result.md`. No new statistic computed except two read-only checks listed in section 7
  (ties behind M4; identical es and last score arrays).

Amendments to the registration: none before results. Deviations recorded in `result.md`: the statistic (b)
bootstrap reuses the first 2,000 rows of the 10,000-row person draw of (a) (same seed); "flip beyond noise"
in (c) implemented as the pair's EER-gap interval excluding 0 on opposite sides in the two conditions; the
FE ViT-B/16 release reads in the opposite direction, a case the reading rule did not foresee.

## 3. Data

Inputs (nothing produced as an image; no image re-encoded):

| Input | Path | Items | Origin / hash |
|---|---|---|---|
| Evaluation manifest | `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv` | rows with variant `orig` in sets `frllm`, `dim`, `mordiff` | sha256 `86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9` (asserted in the code). Built by `smadcvpr/prep_eval.py` (registered eval frames, 512 × 512 eye-aligned) |
| Genuine frames | `smadcvpr_data/eval/frllm/frll_bona/NNN_0{3,8}_orig.png` (= `eval/dim/dim_bona/…`, byte-identical); `eval/mordiff/mordiff_bona/…` (MorDIFF crop) | 204 each | from `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral,smiling}_front/` |
| Morph cells (12) | `eval/frllm/{amsl,facemorpher,opencv,stylegan,webmorph}`; `eval/dim/{dim_a,dim_c,fast_dim,fast_dim_ode,greedy_dim,greedy_dim_s}`; `eval/mordiff/mordiff` | 2,175 / 1,222 / 1,221 / 1,222 / 1,221; 500 ×5 and 499 (Fast-DiM-ODE); 1,000 | FRLL-Morphs (Idiap), DiM-FRLL-Morphs (Hugging Face), MorDIFF |
| Network list | `/home/narolski/mambamorph-code/experiments/A36_published-detector-shortcuts/raw/A36_networks.tsv` | 51 primary R × d0 networks | sha256 `51a80e93…5848` |
| Score files (112) | `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/<release>/scores_eval.npz` (key `score_noTTA`), `…/A12BR/<run>/scores_eval_{es,last}.npz` (key `score`), `/home/narolski/mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz` (key `score`, SelfMAD's own crop) | 9 release sets + 102 recipe sets (+ the untrained network of C1c) | every path and sha256: `c1b_input_scores_sha256.csv`. All carry the eval.csv sha in `manifest_sha256` |
| Raw FRLL photos | `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral,smiling}_front/*.jpg` | 204 | sha256 list `c1b_frll_raw_sha256.csv` |
| Probe-validation frames | corrected MAD22 aligned: `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native/{FaceMorpher,MIPGAN_I,MIPGAN_II,OpenCV,Webmorph}/`; MorDIFF eval frames | 1,000 / 1,000 / 999 / 984 / 500; 1,000 | hashes in that folder's `PROCESSED_SHA256SUMS` |
| Probe-target frames | FRLL-Morphs ×5 and DiM ×6 eval frames (as above) | — | — |
| Documents | `/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/{README.txt,preprocess.py,protocols/}`; `/mnt/t7/Datasety/downloads/DiM-FRLL-Morphs/README.md` (l.73–82) | — | read only |
| FRLL-Morphs paper | `/mnt/t7/smad_next/C1b/sarkar2020_pdf/arxiv_2012.05344.pdf` (copied 17:29 from the web-fetch cache) and its extracted text `arxiv_2012.05344.txt` | 1 | sha256 `824c722185c6849826f5e0920a37f2cceed8eab4ee750913797190065b9feaa5`; source https://arxiv.org/pdf/2012.05344 |

Dropped or excluded: the five corrected-MAD22 cells (no detector scores exist); every `eval.csv` row with set
`mad22` (old subset, never read); the MADation `dnorm` / `dscale` diagnostic releases (not detectors).
No file whose name contains `fst`, `valx` or `A12SP` was opened.

Outputs (experiment folder `/home/narolski/smad-next/experiments/C1b/`; sha256 in brackets, first 12 hex):
`prereg.md` (f8bf5b749ec7), `result.md` (changed 17:40 by the correction line), `c1b_read.json` (64c6e36eaece; all
statistics per score set and cell, rank tables), `c1b_within_person.csv` (b49bd8f06ed5), `c1b_cells.csv`
(518582e71c07; EER / BPCER / AUC per set, cell and genuine subset with paired differences and intervals),
`c1b_probe.json` (e4b6976ec128), `c1b_summary.txt` (788a7dbc856a; every table), `c1b_input_scores_sha256.csv`,
`c1b_frll_raw_sha256.csv`. Large: `/mnt/t7/smad_next/C1b/c1b_eer_bootstrap_reps.npz` (24.9 MB, 4ca9726317d3;
EER bootstrap replicates per score set, cell and subset, 2,000 each, float32), logs `c1b_read.log`,
`c1b_probe.log`, `smoke_c1b_probe_and_read_progress.log`. Copies: DGX and the T7 drive only.

## 4. Code

Run order and arguments (Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`):

1. `src/C1b/c1b_read.py [--smoke]` — statistics (a) within-person AUC, (b) EER and BPCER@APCER 5 / 10% per
   cell with genuine = all / neutral / smiling and paired differences, (c) rank tables. Imports `wauc`
   from `src/AD1/ad1_read.py` (sha256 01443f0e…). 8 worker processes. Smoke: 2 detectors, 2 cells, B = 50.
2. `src/C1b/c1b_probe.py [--smoke]` — validation of the C1 expression probe on morphs with expression in the
   file name, and the misclassification-corrected (Rogan–Gladen) smiling share of FRLL-Morphs and DiM. Imports
   `src/C_cue_checks/c_checks.py` (sha256 00d6e627…) unchanged. Smoke: 8 images per family.
3. `src/C1b/c1b_summarize.py` — tables and the fixed falsifiers from the two JSON files.
4. `src/C1b/c1b_manifest.py` — documentation only: sha256 of every input score file and raw FRLL photo.

Code sha256: `c1b_read.py` 509e09c0…, `c1b_probe.py` 9640fdfd…, `c1b_summarize.py` 1d8984b9…,
`c1b_manifest.py` c21df4d3…. Environment: Python 3.12.3, numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0,
Pillow 12.2.0 (DGX, ARM). No model weights loaded: everything is computed from stored scores and decoded
pixels. Seeds: person bootstrap 20261111 (B = 10,000 for (a), first 2,000 rows for (b)); probe bootstrap
20261111 (B = 10,000).

Definitions used by the code: AUC_wp = mean over persons of 1[s(03) > s(08)] + 0.5·1[tie]. EER: thresholds
over all unique scores; flag = score ≥ t; EER = mean of APCER and BPCER at the t minimising their gap.
BPCER@APCER α: t = largest morph score with APCER(t) ≤ α. Two-way person bootstrap: the 102 persons ~
Multinomial(102, 1/102); a photo's weight = its person's count; a morph's weight = product of its two
contributors' counts.

## 5. Results

All numbers below are in `c1b_summary.txt` (complete tables) and the JSON / CSV files of section 3.

**(a) Within-person neutral-above-smiling AUC**, 102 persons, 95% person bootstrap (B = 10,000), FRLL eval
frames; last column on MorDIFF's own crop. Releases (post hoc):

| Release | AUC_wp [95%] | persons neutral > smiling | pooled AUC [95%] | MorDIFF crop |
|---|---|---|---|---|
| MADation ViT-B/16 | 0.578 [0.480, 0.676] | 59 | 0.539 [0.501, 0.577] | 0.529 [0.431, 0.627] |
| MADation ViT-L/14 | 0.990 [0.971, 1.000] | 101 | 0.855 [0.814, 0.898] | 0.794 [0.716, 0.873] |
| MADation FE ViT-B/16 | 0.088 [0.039, 0.147] | 9 | 0.238 [0.193, 0.279] | 0.098 [0.049, 0.157] |
| MADation FE ViT-L/14 | 0.343 [0.255, 0.432] | 35 | 0.405 [0.362, 0.444] | 0.206 [0.127, 0.284] |
| MADation FS ViT-B/16 | 0.539 [0.441, 0.637] | 55 | 0.528 [0.490, 0.567] | 0.657 [0.568, 0.745] |
| MADation FS ViT-L/14 | 0.500 [0.402, 0.598] | 51 | 0.493 [0.437, 0.546] | 0.520 [0.422, 0.618] |
| SelfMAD, own preprocessing | 0.480 [0.382, 0.578] | 49 | 0.489 [0.446, 0.532] | 0.422 [0.324, 0.520] |
| SelfMAD, our pipeline | 0.314 [0.225, 0.402] | 32 | 0.418 [0.379, 0.454] | 0.412 [0.314, 0.510] |
| MixFaceNet-MAD, our frames | 0.471 [0.373, 0.569] | 48 | 0.479 [0.450, 0.509] | 0.529 [0.431, 0.627] |

Recipes, per seed (ties counted as half; see section 7 for M4):

| Recipe, checkpoint | AUC_wp per seed | mean | n ≥ 0.65 | MorDIFF crop per seed |
|---|---|---|---|---|
| M3 last (pre-registered) | 0.88 0.75 0.78 0.67 0.97 0.82 0.72 0.85 | 0.806 | 8 of 8 | 0.90 0.66 0.72 0.66 0.93 0.76 0.85 0.80 |
| M3L last (pre-registered) | 1.00 ×5 (102 of 102 each) | 1.000 | 5 of 5 | 0.94 0.97 0.96 0.99 0.96 |
| M3 es | 0.98 0.99 0.84 0.99 0.94 0.95 0.89 0.95 | 0.942 | 8 | 0.28 0.27 0.22 0.31 0.15 0.34 0.20 0.24 |
| M3L es | 0.96 0.81 0.92 0.96 0.91 | 0.914 | 5 | 0.08 0.13 0.11 0.14 0.09 |
| M1 last / es | 0.49 0.48 0.45 0.54 0.51 / 0.49 0.44 0.49 0.45 0.63 | 0.494 / 0.500 | 0 / 0 | |
| M2 last / es | 0.59 0.48 0.55 0.63 0.56 / 0.55 0.43 0.51 0.63 0.57 | 0.560 / 0.537 | 0 / 0 | |
| M4 last / es | 0.34 0.44 0.44 0.38 0.46 / 0.34 0.00 0.26 0.06 0.33 | 0.414 / 0.199 | 0 / 0 | 0.10 0.28 0.26 0.10 0.29 / 0.10 0.00 0.09 0.00 0.21 |
| M5 last / es | 0.33 0.61 0.25 0.58 0.51 0.45 0.34 0.44 / 0.28 0.67 0.31 0.50 0.65 0.58 0.40 0.54 | 0.440 / 0.491 | 0 / 1 (s2 0.667) | |
| M6 last / es | 0.56 0.65 0.61 0.54 0.48 / 0.56 0.50 0.51 0.58 0.48 | 0.567 / 0.525 | 0 / 0 (s2 last 0.647) | |
| M8 last / es | 0.44 0.58 0.57 0.62 0.60 / 0.59 0.43 0.50 0.63 0.61 | 0.561 / 0.551 | 0 / 0 | |
| M8O last / es | 0.43 0.58 0.51 0.61 0.58 / 0.52 0.51 0.58 0.45 0.54 | 0.541 / 0.520 | 0 / 0 | |

**Fixed falsifiers.** H1: 13 of 13 last-checkpoint MADation-recipe networks have AUC_wp ≥ 0.65 (bar 10) →
not falsified (lowest M3 s4 last 0.667 [0.578, 0.755]). H2: mean over the 8 M3 last networks 0.806 (range
0.667–0.971; falsified at ≥ 0.70) → falsified; 0 of 8 at or below 0.60.

**(b) EER change neutral-only minus all genuine**, 11 imbalanced cells, releases, points [95% two-way person
bootstrap, B = 2,000]:

| Release | amsl | facemorpher | opencv | stylegan | webmorph | dim_a | dim_c | fast_dim | fast_dim_ode | greedy_dim | greedy_dim_s | mean | cells with lower bound > 0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ViT-B/16 | +0.4 [−1.2, +2.9] | +0.1 | +0.1 | +0.3 | +1.1 [−0.2, +3.0] | +0.1 | +0.4 | +0.5 | +0.5 | +0.9 | +1.8 [−0.8, +3.0] | +0.57 | 0 |
| ViT-L/14 | +6.9 [+3.5, +10.3] | +0.0 | +0.1 | +13.3 [+9.3, +18.5] | +1.9 [+0.1, +3.5] | +5.4 [+3.0, +10.4] | +5.4 [+1.9, +8.3] | +5.6 [+2.8, +10.5] | +6.4 [+2.0, +8.5] | +4.0 [+0.7, +6.0] | +1.1 [+0.1, +3.9] | +4.55 | 9 |
| FE ViT-B/16 | −8.4 | −8.8 | −9.9 | −10.8 | −8.8 | −8.3 | −9.3 | −9.8 | −9.7 | −10.7 | −9.3 | −9.42 | 0 (upper bound < 0 in 11) |
| FE ViT-L/14 | −1.0 | +0.0 | −0.4 | −0.6 | −2.0 | −1.0 | −1.3 | −1.1 | −1.0 | −0.2 | −1.1 | −0.88 | 0 |
| FS ViT-B/16 | −0.2 | −1.0 | +0.0 | −1.4 | +0.3 | −1.0 | −0.3 | −1.2 | −0.4 | −0.9 | −2.4 | −0.78 | 0 |
| FS ViT-L/14 | −0.9 | −0.1 | +0.2 | −0.3 | −0.5 | +0.0 | −0.3 | +0.0 | −0.9 | −0.2 | −0.9 | −0.37 | 0 |
| SelfMAD own | −2.0 [−3.5, −0.4] | −0.2 | +0.0 | −1.3 | −2.2 [−4.6, −0.4] | −1.9 | −1.0 | −2.1 | −2.3 | −1.7 | −1.0 | −1.43 | 0 |
| SelfMAD our pipeline | −3.0 | +0.0 | −0.3 | −3.4 | −3.3 | −3.7 | −1.1 | −3.4 | −2.3 | −3.0 | −1.0 | −2.22 | 0 |
| MixFaceNet, our frames | −0.5 | +0.0 | +0.0 | −0.9 | −0.0 | +0.0 | −0.2 | −0.1 | −0.1 | −0.4 | −0.6 | −0.26 | 0 |

EER all / neutral-only / smiling-only per release and cell, BPCER@APCER 5% and 10% per release and cell with
intervals, and MorDIFF (balanced) rows: `c1b_summary.txt`; the same numbers with neutral-only as the
headline column: `../C1c_smiling-half-expression-or-detail/c1c_bench.md`. Examples (ViT-L/14 release): AMSL 17.7 / 24.5 / 7.9,
FRLL-Morphs StyleGAN 52.4 / 65.7 / 34.3, DiM-A 22.0 / 27.4 / 10.8; BPCER@APCER 5% AMSL 31 → 51
(+20 [+14, +25]), DiM-A 43 → 71 (+27 [+19, +34]); mean BPCER@5 change +13.7. FE ViT-B/16 release: BPCER@5
−9 to −19 in every cell.

Recipes, seed mean of the EER change over the 11 cells: M3L last +6.88 (per network +5.8 to +8.6; StyleGAN
+21.4; lower bound > 0 in 35 of 55 network × cell), M3L es +1.74 (22 of 55), M3 last +1.02 (−0.7 to +3.2;
10 of 88), M3 es +2.43 (49 of 88), CNN recipes last +0.17 (−3.1 to +1.7; 2 of 418), es −0.12 (5 of 418).
Spearman of AUC_wp with the mean EER change over all 111 score sets: 0.86.

MorDIFF (balanced cell): ViT-L/14 release EER 28.9 / 31.4 / 26.3 (+2.5 [+0.2, +4.6]); its AUC is higher
against smiling than neutral genuine photos for both neutral morphs (0.834 vs 0.758) and smiling morphs
(0.845 vs 0.775).

**(c) Ranks** (27 rows = 9 releases + 18 recipe-checkpoint seed means; EER, all vs neutral-only): Kendall τ
per cell amsl 0.954, facemorpher 0.964, opencv 0.976, stylegan 0.833, webmorph 0.949, dim_a 0.930, dim_c
0.937, fast_dim 0.901, fast_dim_ode 0.914, greedy_dim 0.874, greedy_dim_s 0.943; 4–29 pair flips per cell.
Release pair flipping with both gap intervals excluding 0 on opposite sides: one (AMSL, ViT-L/14 release vs
FE ViT-B/16 release). Pairs whose gap change interval excludes 0 (e.g. WebMorph: both MADation releases vs
SelfMAD own, change CIs [+1.1, +6.4] and [+1.4, +7.2]): `c1b_read.json` → `ranks`. Release ranking by mean
EER over the 11 cells, all → neutral-only: ViT-L/14 4th → 7th, FE ViT-B/16 7th → 5th, ViT-B/16 5th → 4th
(table in the C1c README).

**Probe validation** (C1 probe, threshold p = 0.5; Clopper–Pearson intervals): corrected MAD22 FaceMorpher
accuracy 0.931 [0.913, 0.946] (sensitivity 0.878, specificity 0.984, AUC 0.977); MIPGAN-I 0.811 [0.785, 0.835]
(sensitivity 0.642, specificity 0.980, AUC 0.969); MIPGAN-II 0.886 (0.820 / 0.952, AUC 0.961); OpenCV 0.978
(0.974 / 0.982, AUC 0.997); Webmorph (all neutral) 0.978; MorDIFF 0.942 (0.900 / 0.984, AUC 0.985).
Misclassification-corrected smiling share (Rogan–Gladen, B = 10,000): FRLL-Morphs AMSL 0.000 [0, 0],
FaceMorpher 0.000 [0, 0.001], OpenCV 0.000 [0, 0.002], WebMorph 0.000 [0, 0.006], StyleGAN 0.050 [0.025, 0.075];
DiM ×6 (neutral by README, control) 0.011–0.059. Pre-registered rule (upper bound ≤ 10%): neutral-only
status supported for 5 of 5 FRLL-Morphs families.

**Documentary support** (re-checked 17:30 in the extracted PDF text): the paper says "For FRLL dataset, we
follow the protocols used in AMSL Face Morph Image dataset by Neubert et al. [10]. Using these protocols
(essentially, which facial image pairs to morph), we generated morphs with the following morphing tools:
OpenCV, FaceMorpher, WebMorph, and StyleGAN 2", that WebMorph "requires 189 landmarks that are available only
in FLLR dataset" (sic), and that with StyleGAN 2 "it is equally easy to generate high-quality morphs for
smiling expressions as it is for the neutral faces"; it does not state the expression of its morphs. Local:
`preprocess.py` renames AMSL `001_03_002_03_alpha0.5_combined_morph_q33.jpg` → `001_002.jpg`; FRLL ships
`.tem` templates for `neutral_front` only (102 of 102; 0 for `smiling_front`); the FRLL-Morphs protocols
enrol `raw/neutral/NNN_03` and probe with `raw/smiling/NNN_08`; DiM README l.73 and 81: neutral (`03`) only.

## 6. Checks

Verified: smoke run reproduced the reviewer preview to two decimals (17.65 / 24.51; 101 of 102); every score
file's `manifest_sha256` equals the eval.csv hash (asserted); `frll_bona` = `dim_bona` byte-identical; the
independent reviewer recomputed AUC_wp, EER and BPCER tables with its own code and every number matched
(`REVIEW_C1b_20261111.md`, "Every number recomputed by the reviewer matches"; its interval for the
ViT-L/14 mean change, 3.4 to 5.8, equals C1c's [3.42, 5.81]); the probe was validated on 5,483 morphs with
known expression; the two quoted sentences of the paper were checked against its text.

Not verified: that the 03 and 08 photos differ only in expression (false, see section 7); MAD22 Webmorph
(no scores); MixFaceNet-MAD with its own crop (suspended branch); the training epoch of the MADation
releases; what the es checkpoint rule was (its metadata may contain validation scores, which are off limits);
the content of Fig. 2 of the paper (see section 7).

## 7. Dead ends, failures, corrected and withdrawn statements

Corrections from the independent review (16:25) and from C1c, each with the corrected wording:

1. **Withdrawn: "the restriction is a matched comparison: same person, session, camera and file pipeline;
   only the expression differs"** (`result.md`, reading caveat). Reason: the smiling FRLL files are 1.43
   times larger (102 of 102 persons; 1.25–1.88) with identical pixel size, JPEG tables and subsampling, and
   their backdrop is 4.8 times noisier (102 of 102; C1c step 2). Corrected: "the smiling half differs from the
   morph sources in expression and in capture detail".
2. **Withdrawn: "the expression cue is used" / proposed row 15a status "USED (MADation ViT-L/14 release, M3L
   recipe)".** Reason: the release's ordering fades as detail is removed while the smile stays visible
   (0.99 → 0.78 on the FRLL crop at 256-px files; 0.79 → 0.53 on MorDIFF's crop) and is weak in photo pools
   without the FRLL capture difference (FERET 0.564, FRGC 0.570); M3L last is at 0.45–0.58 there. Corrected:
   "the smiling half of the FRLL genuine class (expression together with a capture-detail difference)
   changes benchmark numbers; no intervention isolates expression; status PRESENT, USE UNTESTED". The C1c
   proposal for row 15 replaces the C1b one.
3. **Corrected: "M3 recipe reads expression (AUC_wp 0.67–0.97) with small EER effects".** Reason: the
   ordering vanishes or reverses at low resolution (0.33 at the DiM-matched set) and is 0.49–0.57 on FERET.
   Corrected: "M3 last orders the FRLL photos by capture detail".
4. **Reading of H1 narrowed.** H1's numbers stand (13 of 13), but "CLIP-based MADation networks lower the
   morph score for smiling genuine faces" holds only for the FRLL smiling photos; the last-checkpoint
   networks do not do it for smiling faces in FERET or FRGC (C1c). H2's numeric outcome (falsified) also
   stands, with the same caveat on what is read.
5. **Corrected: "CNN recipes do not show it".** Reason: ties were counted as half. The SelfMAD-style recipe
   M4 has 0 persons with the neutral photo higher in every network; its AUC_wp 0.34–0.46 (last) came only
   from 70–94 tied persons (identical scores); among untied persons the smiling photo is always higher
   (checked 17:35 in `c1b_within_person.csv`, columns n_neutral_above and n_ties). Corrected: "M4 ranks the
   smiling FRLL photo above the neutral one in every untied pair (reversed), not in FERET / FRGC".
6. **Corrected (found during this documentation pass): "No CNN recipe network … reaches 0.65"**
   (`result.md` H1 paragraph). M5 s2 es has 0.667 [0.578, 0.755] (the M5 row of the same file shows "n ≥ 0.65
   = 1"); M5 s5 es and M6 s2 last are at 0.647.
7. **Not re-verifiable: "Fig. 2 shows neutral contributors and neutral morphs"** (`result.md`, documentary
   support). The figure was not viewed in this pass (images may not be loaded now), and the session log of
   the PDF page reads does not let me confirm what was displayed. Treat as unverified. The quoted sentences
   were re-checked in the extracted text and stand. Also "web check done, pages 1–5 read" should read "web
   check done; quotes verified against the extracted text on 11 Nov 17:30".
8. **Headline column changed** (review): tables now lead with neutral-only genuine photos; the all-photo
   number beside it (C1c step 4).
9. Count error in the cue checks C1 (not this owner's): "11 of 17" imbalanced cells should be 12 of 17
   (DiM ×6 + FRLL-Morphs ×5 + MAD22 Webmorph); flagged in `result.md`, confirmed by the review.

Other failures and limits: no bug found in the reader (reproduction and the reviewer's recomputation
match). The worker pool was lowered from 12 to 8 before the full run (load). MixFaceNet-MAD on our frames is
reversed on four FRLL-Morphs cells (EER 75–98) and M4 is reversed on the benchmarks (mean EER 89), so
both stay descriptive. The probe misses a third of the smiling MIPGAN-I morphs (sensitivity 0.642), so the
corrected StyleGAN share (5.0%) cannot exclude a small smiling share.

## 8. Observations and ideas

- For two recipe networks the es and last score arrays are identical (M4 s1, M6 s5; checked 17:36), i.e. the
  early stop fell on the last checkpoint. Any es-vs-last contrast should count them once.
- On MorDIFF's crop every es checkpoint of M3 and M3L reverses (0.08–0.34) while the last checkpoints stay
  positive; the reviewer found a correlation with the tilt of the zero-filled border (ρ −0.16 to −0.38),
  not followed up.
- The frozen-encoder releases read smiles in the opposite direction (smiling photo more morph-like; FE
  ViT-B/16 0.09 on FRLL, 0.32 on FERET in C1c). A frozen CLIP encoder plus a trained head therefore carries an
  expression direction learned from SMDD.
- At a threshold fixed on development photos, the ViT-L/14 release flags 6 of 102 neutral and 1 of 102
  smiling FRLL photos (C1c, H4): the benchmark effect is not only an EER artefact.
- Reviewer consequence: any FRLL control that mixes neutral and smiling photos inherits the file
  difference (AD1 same-person mixes, the FRLL pool of AR1, AD1b where it uses the smiling photo).
- The FRLL-Morphs paper notes StyleGAN 2 morphs smiling faces as easily as neutral ones; the StyleGAN family
  has the highest corrected smiling share (5.0%).

## 9. Open items and next steps

- Corrected MAD22 (WCSS job 6299123): rerun (b) for the five cells, above all MAD22 Webmorph, the twelfth
  imbalanced cell.
- An intervention that separates expression from capture detail: the half-exchange test proposed by the
  reviewer (needs the author's ruling that a hard rectangular pixel copy is permitted image code).
- MixFaceNet-MAD with its own crop once that branch is repaired.
- Decide (lead) on the C1c wording for row 15 of `08_CUE_MATRIX.md`.

## 10. Handover state

Nothing running; no queued task; no file in progress. Compute: CPU only on the DGX, about 15 minutes of
wall time over 8 processes; 0 GPU-hours; 0 USD. Files copied out of the scratchpad in this pass: the
paper PDF (`/mnt/t7/smad_next/C1b/sarkar2020_pdf/`), the probe smoke log
(`/mnt/t7/smad_next/C1b/smoke_c1b_probe_and_read_progress.log`).

## 11. Reproduce from scratch

```bash
cd /home/narolski/smad-next
PY="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
$PY src/C1b/c1b_read.py --smoke         # 2 detectors, 2 cells; expect ViT-L/14 AMSL EER 17.65 / 24.51
$PY src/C1b/c1b_read.py                 # ~5 min, 8 workers -> experiments/C1b/c1b_read.json, *.csv,
                                        #   /mnt/t7/smad_next/C1b/c1b_eer_bootstrap_reps.npz
$PY src/C1b/c1b_probe.py --smoke        # 8 images per family
$PY src/C1b/c1b_probe.py                # ~9 min -> experiments/C1b/c1b_probe.json
$PY src/C1b/c1b_summarize.py > experiments/C1b/c1b_summary.txt
$PY src/C1b/c1b_manifest.py             # input hash manifests
pdftotext -layout /mnt/t7/smad_next/C1b/sarkar2020_pdf/arxiv_2012.05344.pdf /mnt/t7/smad_next/C1b/sarkar2020_pdf/arxiv_2012.05344.txt
```
