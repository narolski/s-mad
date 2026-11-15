# Benchmark cue checks C1–C4 (expression balance, person overlap, colour statistics, chroma format): full record

Owner: hypothesis-owner agent (Opus), 11 Nov 2026. `result.md` is the short verdict; this README is the
full record.

Terms. Cell = one benchmark comparison of one morph family against its genuine ("bona fide") photos.
FRLL = Face Research Lab London set (102 persons × neutral photo `_03` and smiling photo `_08`; the genuine
class of every cell here). MAD22c = the corrected SYN-MAD 2022 (author re-upload of 9 Nov 2026). DiM /
Greedy-DiM = diffusion morph families on FRLL. AUC = area under the ROC curve. O = max(AUC, 1 − AUC) of a
single feature (A41's one-feature separability). LR = logistic regression. Chroma subsampling = JPEG's
reduced colour resolution (4:2:0 = PIL sampling 2; 4:4:4 = 0).

## 1. Question and current answer

Status: **finished** 11 Nov 2026 (about 15:00 CET); independent review "accept-qualified".

Questions and answers, 17 cells (FRLL-Morphs ×5, MAD22c ×5, MorDIFF, DiM ×6):
- C1, expression balance: **12 of 17 cells are imbalanced** (corrected from "11"; section 7): all six DiM
  families (README: neutral only), all five FRLL-Morphs families (inferred by a validated probe: ≤ 7%
  smile-like) and MAD22c Webmorph (file names: 500 neutral) have neutral-only morphs against a genuine
  class that is half smiling, so "smiling ⇒ genuine" alone separates at AUC up to 0.75. Balanced: MAD22c
  FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV and MorDIFF (5 cells).
- C2, person overlap: no FRLL image is in any audited training set by path or label; the public SelfMAD
  code's default selects its checkpoint on test data including the FRLL genuine photos (whether the
  release was made this way is unknown).
- C3, colour statistics: on our aligned crops, per-channel mean and standard deviation separate every cell
  (person-grouped LR AUC 0.71–1.00; 0.61–0.98 without the zero border).
- C4, chroma subsampling: alone it separates only MAD22c Webmorph (4:4:4 morphs vs 4:2:0 photos, O = 1.00);
  elsewhere it is either equal (0.50) or coincides with PNG vs JPEG.

## 2. Timeline

- 11 Nov ~14:22: task received with AD1 and AG5. Reading of `08_CUE_MATRIX.md` rows 13b, 13c, 14, 15 and
  A41's file table (`/home/narolski/mambamorph-code/smadcvpr/results/A41/a41_files.{md,json}`; its
  header reader `a41_read.header`, raw globs `DCA_CELLS`).
- ~14:44: C2 by reading: training manifests (`smadcvpr_data/manifests/train.csv`, `train_r6.csv`,
  `train_r8.csv`; manifests only, no scores), the SelfMAD code mirror
  (`/home/narolski/mambamorph-code/baselines/SelfMAD`: `configs/train_config.json`, `train__.py`,
  `eval__.py`) and the MADation config (`baselines/MADation/src/config.py`, `src/utils/logging.py`).
- ~14:45: C1 sources: FRLL-Morphs README and protocols (`/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/`),
  DiM README (`/mnt/t7/Datasety/downloads/DiM-FRLL-Morphs/README.md` l.73: "we only used faces with neutral
  expressions … category 03"), file names.
- ~14:46: wrote `src/C_cue_checks/c_checks.py`; first smoke failed (section 7), fixed, smoke passed; full
  run 14:46–14:48 (32,310 images, 0 decode errors), log `c_checks.log`.
- ~14:55: wrote `src/C_cue_checks/probe_check.py` (validation of the expression probe on named morphs),
  ran it (about 4 min, background), added the result to `result.md`.
- ~15:00: `result.md` with proposed `08_CUE_MATRIX.md` edits; handed back.
- 11 Nov afternoon: independent review (cell-count correction; expression-use preview, now C1b).
- 11 Nov ~17:30: documentation pass: input file list `c_inputs_filelist.tsv.gz`; correction note added to
  `result.md`.

## 3. Data

Per-cell input lists (38,022 rows = cell × role × file, with byte sizes):
`/home/narolski/smad-next/experiments/C_cue_checks/c_inputs_filelist.tsv.gz` (sha 5101dd03…). Content
hashes of the 32,310 distinct images were not computed (I/O cost); existing hash lists: corrected MAD22
raw `mambamorph-code/experiments/dataaudit/marco_owncloud_20261109T103840Z/verified_inventory.json`,
aligned `…/mad22_canonical_E7_inputs_v3_20261109T113746Z/PROCESSED_SHA256SUMS`; FRLL raw
`/mnt/t7/smad_heldout/a41_diffae/data/provenance/raw_frll.sha256`.

| Cell group | Stored ("raw") files | Aligned crops | n morph / genuine |
|---|---|---|---|
| FRLL-Morphs amsl, facemorpher, opencv, stylegan, webmorph | `/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/morph_<f>/*`; genuine `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral_front,smiling_front}/*` | `/home/narolski/mambamorph-code/smadcvpr_data/eval/frllm/<f>/*_orig.png`, genuine `eval/frllm/frll_bona` (rows of `eval.csv`, variant `orig`) | 2,175 / 1,222 / 1,221 / 1,222 / 1,221 vs 204 |
| MAD22c FaceMorpher, MIPGAN_I, MIPGAN_II, OpenCV, Webmorph | `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/<fam>/`, genuine `BonaFide/` | `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/native/<fam>/` | 1,000 / 1,000 / 999 / 984 / 500 vs 204 |
| MorDIFF | `/mnt/t7/Datasety/downloads/MorDIFF/MorDIFF_crop/*/morphed/*`; genuine frll_base | `eval/mordiff/mordiff`, `eval/mordiff/mordiff_bona` | 1,000 vs 204 |
| DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S | `/mnt/t7/Datasety/downloads/DiM-FRLL-Morphs/morphs/<f>/*`; genuine frll_base | `eval/dim/<f>`, `eval/dim/dim_bona` | 500 each (Fast-DiM-ODE 499) vs 204 |

Never used: `/mnt/t7/Datasety/downloads/MAD22` (old subset). Outputs: `c_checks.json` (ddf83ea0…),
`c_checks.log` (08f973b6…), `probe_check.json` (f596a719…), `c_inputs_filelist.tsv.gz`.

## 4. Code

| Script | sha256 | Job |
|---|---|---|
| `/home/narolski/smad-next/src/C_cue_checks/c_checks.py` | 00d6e627… | builds the cell lists; per image: header facts (container, chroma sampling, mode, ICC, progressive, bit depth) of the stored file; per-channel mean/std of the stored file and of the aligned crop (all pixels and non-zero pixels, zero-border fraction); a 22×36 grey lower-face thumbnail (rows 300–432, cols 150–366 of the 512 frame, 6×6 block means in memory); then C1, C3, C4 per cell |
| `/home/narolski/smad-next/src/C_cue_checks/probe_check.py` | 1ac64ce1… | refits the expression probe on the genuine frames and applies it to morphs with known expression (MorDIFF, MAD22c FaceMorpher, OpenCV, Webmorph) |

Environment: spark venv (Python 3.12.3, numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.0, Pillow 12.2.0,
OpenCV 4.11.0), CPU, 14 worker processes. No weights. Methods:
- C1: expressions from file names (`_03`/`_08`, MorDIFF folders `neutral_front*`/`smiling_front*`); where
  names lack them, the probe = standardised LR (C = 0.1) on the thumbnail, trained on the 204 FRLL genuine
  frames (neutral 0 / smiling 1), 5-fold by person (fold = sha1("c3-" + person) mod 5). O of the
  expression label computed with smiling = 1, mixed pair = 0.5.
- C3: one-feature AUC per statistic; LR on the 6 statistics (standardised), 5 folds by person: test = items
  with any person in the fold, train = items with no person in the fold (folds overlap for morphs);
  reported as the mean of the fold AUCs.
- C4: categorical O = AUC of the in-sample per-category morph share used as the score.

## 5. Results

Source: `c_checks.json` (per-cell fields `C1`, `C3_raw`, `C3_al`, `C4`), `probe_check.json`.

### 5.1 C1 expression

| Cell | Morph expression | Smiling share morph / genuine | O (label alone) |
|---|---|---|---|
| MAD22c FaceMorpher | 500 neutral + 500 smiling pairs | 0.50 / 0.50 | 0.50 |
| MAD22c MIPGAN-I | 500 + 500 | 0.50 / 0.50 | 0.50 |
| MAD22c MIPGAN-II | 500 + 499 | 0.50 / 0.50 | 0.50 |
| MAD22c OpenCV | 489 + 495 | 0.50 / 0.50 | 0.50 |
| MorDIFF | 500 + 500 | 0.50 / 0.50 | 0.50 |
| **MAD22c Webmorph** | 500 neutral | 0.00 / 0.50 | **0.75** |
| **DiM ×6** | neutral (README); probe smile-like 2.6% (DiM-C) to 6.8% (Greedy-DiM) | ≈0 / 0.50 | ≈0.75 |
| **FRLL-Morphs ×5** | not in names; probe smile-like: amsl 1.0%, facemorpher 1.1%, opencv 1.1%, stylegan 6.9%, webmorph 1.5% | ≈0 / 0.50 | ≈0.75 (inferred) |

No named morph mixes expressions (only 03/03 and 08/08 pairs). Probe: cross-validated accuracy on genuine
photos 0.853 (folds 0.842–0.857); on named morphs AUC against the file-name label 0.985 (MorDIFF), 0.977
(MAD22c FaceMorpher), 0.997 (MAD22c OpenCV); flags 90%, 88%, 97% of the smiling morphs and 2.2% of the
all-neutral MAD22c Webmorph morphs.

### 5.2 C2 person overlap

| Training data | FRLL inside? |
|---|---|
| `train.csv` (69,882 rows: `train/smdd` 40,000 synthetic; FERET and FRGC bona fide and morph arms), `train_r6.csv` (4,223 FRGC), `train_r8.csv` (5,000 FERET/FRGC self-morphs) | 0 paths matching frll/facelab/london/mordiff/dim; FERET (1993–96), FRGC (2002–04) and FRLL (2017) have no shared person labels; face matching not run |
| MADation releases | SMDD training (`MADTrain` → `smdd_train_cropped.csv`); the config evaluates MAD22, MorDIFF and all FRLL-Morphs lists during training; checkpoint saved every N epochs (`logging.py` l.116–120); released epoch undocumented |
| SelfMAD release | README silent; shipped `configs/train_config.json`: `train_dataset: SMDD`, `saving_strategy: testset_best` → `train__.py` l.178–190 keeps the epoch with the lowest mean EER on `default_datasets("original")` = FRGC-, FERET- and FRLL-Morphs (`eval__.py` l.55–82). If the release used the defaults, its checkpoint was selected on FRLL-Morphs test images |
| MixFaceNet-MAD release | SMDD |
| Pretraining (CLIP, ImageNet), SMDD's generator (FFHQ) | not verifiable (no identity labels) |

### 5.3 C3 colour statistics

| Cell | Stored file O / LR | Aligned O / LR | Aligned non-zero LR | Zero-border median morph / genuine |
|---|---|---|---|---|
| FRLL-Morphs amsl | 0.984 / 0.999 | 0.714 / 0.851 | 0.760 | 0.053 / 0 |
| FRLL-Morphs facemorpher | 1.000 / 1.000 | 0.992 / 0.996 | 0.983 | 0.260 / 0 |
| FRLL-Morphs opencv | 1.000 / 1.000 | 0.973 / 0.990 | 0.966 | 0.192 / 0 |
| FRLL-Morphs stylegan | 0.997 / 0.999 | 0.817 / 0.899 | 0.893 | 0.032 / 0 |
| FRLL-Morphs webmorph | 0.993 / 0.999 | 0.688 / 0.840 | 0.764 | 0.051 / 0 |
| MAD22c FaceMorpher | 0.986 / 0.996 | 0.704 / 0.841 | 0.822 | 0.054 / 0 |
| MAD22c MIPGAN-I | 0.996 / 0.999 | 0.905 / 0.932 | 0.971 | 0.040 / 0 |
| MAD22c MIPGAN-II | 0.996 / 1.000 | 0.910 / 0.917 | 0.978 | 0.041 / 0 |
| MAD22c OpenCV | 0.584 / 0.630 | 0.667 / 0.771 | 0.771 | 0 / 0 |
| MAD22c Webmorph | 0.598 / 0.648 | 0.660 / 0.772 | 0.772 | 0 / 0 |
| MorDIFF | 1.000 / 1.000 | 0.565 / 0.781 | 0.614 | 0.526 / 0.544 |
| DiM-A | 0.994 / 0.998 | 0.632 / 0.713 | 0.614 | 0.031 / 0 |
| DiM-C | 0.996 / 0.998 | 0.663 / 0.711 | 0.609 | 0.033 / 0 |
| Fast-DiM | 0.995 / 0.998 | 0.674 / 0.751 | 0.625 | 0.032 / 0 |
| Fast-DiM-ODE | 0.988 / 0.995 | 0.635 / 0.840 | 0.826 | 0.033 / 0 |
| Greedy-DiM | 0.994 / 0.997 | 0.671 / 0.758 | 0.749 | 0.034 / 0 |
| Greedy-DiM-S | 0.995 / 0.998 | 0.661 / 0.764 | 0.763 | 0.034 / 0 |

Per-statistic AUCs and per-fold LR AUCs: `c_checks.json`. On stored files the one-feature mean AUCs are near
0 (morph files darker on average than the 1350² genuine frames); stored-file separation is therefore
likely a framing/background cue as much as a colour cue (not examined further).

### 5.4 C4 header formats

| Cell | Morph format | Genuine format | O sampling | O container·sampling·mode·progressive |
|---|---|---|---|---|
| FRLL-Morphs ×5, MAD22c FaceMorpher, OpenCV | JPEG 4:2:0 RGB | JPEG 4:2:0 RGB | 0.50 | 0.50 |
| **MAD22c Webmorph** | JPEG 4:4:4 (500) | JPEG 4:2:0 (204) | **1.00** | **1.00** |
| MAD22c MIPGAN-I/II, MorDIFF, DiM ×6 | PNG | JPEG 4:2:0 | 1.00 (with container) | 1.00 |

Mode RGB, no ICC, no progressive JPEG, 8 bit in every cell.

### 5.5 Proposed `08_CUE_MATRIX.md` edits (not applied; corrected count)

Rows 13b, 13c, 14 as in `result.md`. Row 15 corrected: "Yes in **12 of 17** cells: DiM ×6 (README),
FRLL-Morphs ×5 (probe ≤ 7% smile-like), MAD22 Webmorph (names) … balanced in MAD22 FaceMorpher,
MIPGAN-I/II, OpenCV and MorDIFF (**5** cells)"; status PRESENT, USE UNTESTED for the 12 (15a), ABSENT for
the 5 (15b).

## 6. Checks

Verified: 0 decode errors over 32,310 images; header facts agree with A41's table for every cell A41
covered (FRLL-Morphs, MorDIFF, DiM; MAD22 Webmorph subsampling O = 1.00 also on the corrected set); the
expression probe was validated on 2,984 named morphs (AUC 0.98–1.00); the reviewer re-ran parts (C3 quick
check, `rev_scripts_20261111/c3_quick.py`) and accepted. Not verified: content hashes of the images; FRLL-
Morphs morph expression from its authors (inferred only); identity overlap by face matching; the SelfMAD
release's actual training run; the MADation release epoch.

## 7. Dead ends and failures

- First smoke failed: `ValueError: This solver needs samples of at least 2 classes` — the smoke took the
  first 8 files of each list and the first 8 genuine files are all neutral. Fixed by taking the first 4
  and the last 4 files (the `SMOKE` line in `c_checks.py`, edited with sed; this changes only `--smoke`).
- `probe_check.py` exceeded the 120 s foreground limit; moved to the background, completed normally.
- An unsupported explanation in my first `result.md` ("MAD22c OpenCV and Webmorph … share the genuine
  photos' canvas") was removed the same afternoon: A41 shows their pixel widths differ; the reason for
  their low stored-file separation was not examined.
- Statements corrected by the independent review (11 Nov):
  1. "11 of 17 cells imbalanced … the other 6 balanced" → **12 of 17 imbalanced, 5 balanced**. Reason:
     arithmetic error (6 DiM + 5 FRLL-Morphs + 1 MAD22 Webmorph = 12). The proposed row-15 edit in
     `result.md` carries the same error; corrected in 5.5 and in a dated note in `result.md`. (The review
     text itself still says "11 imbalanced cells" in its expression bullet; the count is 12.)
  2. C1 only showed the cue is in the files; the review's preview (to be registered as C1b) shows CLIP-
     based MADation networks score neutral genuine photos as more morph-like than smiling ones (ViT-L/14
     release: 101 of 102 persons, AUC 0.855), so the imbalance flatters CLIP-based rows by 2–7 EER points
     (e.g. ViT-L/14 AMSL 17.7 → 24.5, Greedy-DiM 9.8 → 13.8 with neutral-only genuine photos); CNN recipes
     and SelfMAD do not show it. These are the reviewer's numbers; registered rerun = C1b.

## 8. Observations and ideas

- FRLL-Morphs FaceMorpher and OpenCV morphs carry large zero borders on our aligned frames (median 26% and
  19% of the frame); even without those pixels colour statistics separate at 0.97–0.98.
- MorDIFF's aligned frames have about 53–54% zero border in *both* classes (the published crops are tight),
  which is why its aligned colour separation is the weakest (0.61 non-zero).
- MIPGAN cells separate at 0.97–0.98 on non-zero aligned pixels: generator colour rendering differs from
  the camera photos.
- The SelfMAD checkpoint-selection default is worth an email question to its authors (planned around
  14 Nov), together with the MADation released epoch.

## 9. Open items and next steps

- C1b (running, another owner): registered expression-use test with a neutral-only genuine column.
- Colour-matched (histogram transfer) control on the aligned frames, rescored (row 13c).
- Face-matching overlap search (embeddings) of FRLL against FERET, FRGC and SMDD.
- Read the epoch field from the original SelfMAD archive.

## 10. Handover state

Nothing running. Compute: about 10 CPU-minutes (14 processes), 0 GPU-hours, 0 USD. The run's console
output is saved as `c_checks.log`; no other file lives only in /tmp or a scratchpad.

## 11. Reproduce from scratch

```bash
cd /home/narolski/smad-next
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
$PY -I src/C_cue_checks/c_checks.py --smoke                       # 6 cells, 4+4 files per list
$PY -I src/C_cue_checks/c_checks.py > experiments/C_cue_checks/c_checks.log 2>&1   # -> c_checks.json (~3 min, 14 workers)
$PY -I src/C_cue_checks/probe_check.py                            # -> probe_check.json (~4 min)
```
