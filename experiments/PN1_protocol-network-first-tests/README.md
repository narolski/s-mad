# Protocol network, first tests (PN1): full record

Owner: PN1 hypothesis owner (Claude agent), DGX and Athena. Started 11 Nov 2026, 18:42 CET. Follows
`/home/narolski/smad-next/DOCUMENTATION.md`. Registration: `prereg.md` (this folder). Short verdict: `result.md` (when
numbers exist). Code: `/home/narolski/smad-next/src/PN1/`. Large outputs: `/mnt/t7/smad_next/PN1/`.

## 1. Question and current answer

Question: does the registered MADation recipe (CLIP with LoRA, last checkpoint), trained on manifest B (negatives =
camera photos, warp-only images, the morph's own warped halves and 61.2 px stored copies of photos and halves;
attacks = two-person morphs and their 61.2 px copies), keep the morph signal while not reacting to storage history
and softness at one fixed threshold, where the same recipe on manifest A (camera photos against two-person morphs)
does react? Tier 0: logistic heads on frozen CLIP ViT-L/14 (224) and DINOv3 (512) features, DGX CPU. Tier 1: four
ViT-B/16 LoRA fits on Athena (manifests A and B, seeds 401 and 402).

Status 11 Nov 19:10 CET: registration written (`prereg.md`, sha256 recorded in section 2); person split fixed; softened
development photos being built; feature extraction starting. No score or statistic of PN1 exists yet. Answer: none.

## 2. Timeline (11 Nov 2026, CET, machine clock)

- 18:42 Read OWNER_BRIEF, DOCUMENTATION, ATHENA, NOTEBOOK, CONSOLIDATED_v3, the three vetted cards, the records of
  AF0, AR1, SM1, AD4 (sections 3 to 10, `run.sh`, Athena job files), EV1. Inspected list files, feature caches and
  `train.py` / `common.py` of the AD4 pack (row selection, sampler, loader) to fix the manifest convention.
- 18:50 Found: 67 of the 663 AF0 persons are validation-reserved (`prep_train.is_val`); the ladder partner map is a
  permutation (each host is the partner of exactly one host), so a random development draw leaves only 48 to 88
  ladder training hosts; choosing the development hosts among the partners of test hosts leaves 156 (124 with a usable
  morph). Registered that rule.
- 18:58 `src/PN1/split.py` run (CPU, lists only): `split/ladder_split.csv`, `split/af0_split.csv`,
  `split/split_summary.json`. T = AF0's 200 softened hosts (seed 401, checked identical), 191 readable; D = 100 (seed
  402); L = 156 / 124.
- 19:00 Coordinator's addition (certificate, matched-subsample test, new rung R2w4, class wording) received and put
  into the registration before any computation.
- 18:59 to 19:03 `src/PN1/soften_dev.py`: list of 226 development camera photos (100 development-ladder R0 + 126 AF0
  validation photos outside V); 8-image test (4 photos x 2 strengths) passed (all aligned, scales 0.456 to 0.874);
  full build started (PID 2335741, nice 10, log `/mnt/t7/smad_next/PN1/soften_dev.log`).
- 19:01 `src/PN1/lists.py`: lists r2w4 (1,072), frll_e5 (1,020), r2w4_td (600, test and development hosts), frll_e5s
  (612, jpeg50 / blur1 / resample50).
- 19:02 8-image test of `src/PN1/featmean.py` (CLIP) started; very slow on the loaded machine (load average about 90).
- 19:06 `prereg.md` written (sha256 `efc5c32a…` before two header-time corrections). Report 1 sent to the lead.
- 19:07 to 19:19 DGX GPU queue 1 (`src/PN1/run_gpu1.sh`, nice 10, one process): CLIP means for eq8_ar1 (8-image
  equivalence set), r2w4 (1,072) and frll_e5 (1,020): 676 s wall. Equivalence on 8 ar1 images against the mean of AF0's
  cached tokens: max |difference| 0.049 (mean |value| 0.41), correlation 0.99998 (bf16 kernels; not bit-equal).
  DINOv3 part started 19:18:50 (eq8_ar1, ar1soft, r2w4_td, frll_e5s).
- 19:08 `featpool.py` (AF0 token caches -> means) first version read through a memory map: no progress in 2 minutes
  (page faults); killed by PID, rewritten with `os.preadv` (AF0's reading scheme): 11 to 25 MB/s on the loaded drive.
  DINOv3 means of af0_w1, af0_w2, ar1, bench_s, h1 are taken from PD1's existing pooled files
  (`/mnt/t7/smad_next/PD1/landmark/feat/dinov3_512/af0_<list>_mean.npz`, same statistic: mean over the patch tokens of
  AF0's float16 tokens, float32), saving about 35 GB of reads; af0_w1 is pooled by PN1 as well to compare.
- 19:13 Coordinator: author's decision on the JPEG branch; amendment 1 (manifest C, JPEG reads) appended to the
  registration at 19:20 before any computation. 19:26 amendment 2 (person frequency instead of a partner count that
  equals the label). 19:28 coordinator: Athena jobs run from the container image
  `/net/pr2/projects/plgrid/plggrestoration/smad-next/containers/smad_torch221_cu121_v1.sif` (sha256 `fedeff10…`);
  `src/PN1/run.sh` and the job files changed to call `apptainer exec --nv` (DGX tests keep the host Python).
- 19:23 Development softening finished: 452 copies, 0 failures (`/mnt/t7/smad_next/PN1/soft_devsoft_src.csv`); list
  `devsoft` (452, sha256 `017c47fe…`).
- 19:23 `jpeg_c.py verify` failed on its own pin: AF0's `soften.py` changed at 19:14:54 (sha256 `aa90f271…`; only a
  `--reverse` option added to its build; `load_pe` and `e7_branch` unchanged). `soften_dev.py` had imported the
  earlier file (`49fa4151…`) at 18:59. `jpeg_c.py` now pins `prep_eval.py` itself; verification to be rerun.

## 3. Data

- Person split: `split/ladder_split.csv`, `split/af0_split.csv`, `split/split_summary.json` (hashes inside).
- Lists (`/mnt/t7/smad_next/PN1/lists/`, AF0 list format): `devsoft_src.csv` (226, sha256 `cb847cde…`),
  `r2w4.csv` (1,072, `a5d98464…`), `r2w4_td.csv` (600, `488fabc3…`), `frll_e5.csv` (1,020, `71b69756…`),
  `frll_e5s.csv` (612, `7a601b26…`).
- Softened development photos: `/mnt/t7/smad_next/PN1/img/soft/{fm61,amsl112}/<id>_<strength>.png` (in progress),
  log of the build `/mnt/t7/smad_next/PN1/soft_devsoft_src.csv` (when done).
- Inputs read (never modified): AF0 lists, features, images, softened copies (`/mnt/t7/smad_next/AF0/`); AR1 frames,
  manifests and the new rung R2w4 (`/mnt/t7/smad_next/AR1/`); SM1 ladder halves (`/mnt/t7/smad_next/SM1/img/ar1h/`);
  the AD4 pack extraction (`/mnt/t7/smad_next/AD4/test/work/task_AD4_m3mf_s401/ad4/`); `eval.csv` FRLL variants.

## 4. Code (`/home/narolski/smad-next/src/PN1/`, Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`)

| Script | Job |
|---|---|
| `split.py` | person split (prereg section 2) |
| `soften_dev.py` | stored-small copies of development camera photos via AF0's `soften.py` (sha256 `49fa4151…`, imported unchanged) |
| `lists.py` | PN1 lists (r2w4, frll_e5, devsoft) |
| `featmean.py` | mean patch-token features via AF0's `feat.py` (sha256 `4529c523…`, imported unchanged) |

## 5. Results

None yet.

## 6. Checks

- split.py asserts: `prep_train.is_val` equals the local copy for all hosts; the partner map is a permutation; T equals
  the AF0 softened-host list; AF0 and ladder persons are disjoint.

## 7. Dead ends and failures

- A random development draw (seed 402 over all non-test hosts) would have left 88 ladder training hosts with a usable
  morph (48 if partners of test hosts are also excluded); replaced by the registered partner rule before any score.

## 8. Observations and ideas

- AF0 includes 67 validation-reserved persons (49 in its training split); the AF0 owner may want to know.

## 9. Open items and next steps

Tier 0 features and cues; softened ladder morphs (AF0 owner; ask the lead after 21:00 if missing); tier 0 heads;
pack and Athena smoke job; lead's GO; four fits.

## 10. Handover state

- DGX PID 2335741 `soften_dev.py build` (nice 10), log `/mnt/t7/smad_next/PN1/soften_dev.log`; rerun the same command
  if it dies (finished files are skipped).
- DGX `featmean.py --limit 8` test (CLIP) running.
- Compute so far: DGX CPU only; no Athena job.

## 11. Reproduce from scratch

```
cd /home/narolski/smad-next/src/PN1; P="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
$P split.py
$P soften_dev.py list; $P soften_dev.py build --limit 4; $P soften_dev.py build
$P lists.py r2w4; $P lists.py frll_e5   # r2w4_td and frll_e5s: subsets written by the inline step of 19:01 (to be moved into lists.py)
```
