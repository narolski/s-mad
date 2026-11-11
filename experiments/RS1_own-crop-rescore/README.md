# Own-crop re-score of the audit rows (RS1): full record

Owner: RS1 hypothesis owner (Claude agent). Started 11 Nov 2026, 16:30 CET. Short verdict page: `result.md` (not
yet written). Registration: `prereg.md` (base text 16:50, amendment 1 17:30, amendment 2 17:45).

Abbreviations: EER = equal error rate (%). AUC = area under the ROC curve. E7 ("resmatch") = the existing control
that gives a genuine photo the morphs' shrink-and-store history. MTCNN = the face detector used by the MADation and
MixFaceNet-MAD crop. LoRA / FE / FS = the three MADation release types (low-rank adapted encoder; frozen encoder
with trained head; encoder trained from scratch). A46, A41, A43, A32 = earlier experiments of the CVPR program in
`/home/narolski/mambamorph-code` (their records: `experiments/A46_diffusion-register-raw-files/`,
`experiments/A41_shortcut-proof-zero-gpu/`, `experiments/A43_mordiff-two-by-two/`,
`experiments/A32-RSX_resolution-shortcut/`).

## 1. Question and current answer

Our audit rows about released detectors were scored on our own 512-pixel eye-aligned frames, where the published
EERs are not reproduced. RS1 re-scores each release through its own crop and preprocessing on the raw benchmark
files, labels every row "reproduced" or "our pipeline, published number not reproduced" (window max(1.5, 25%) of the
published EER), and for reproduced rows measures the effect of history-matched genuine photos, storage at the
published size, the neutral / smiling split, extra processed genuine pools (amendment 2), and the MorDIFF ladder.

Status 11 Nov 17:50: **running on the DGX** (crops and scoring in progress, see section 10). No RS1 score of a
MADation or MixFaceNet release has been read yet. The SelfMAD rows come from existing files and were read once to
test the analysis code (they reproduce the A41 x7 table exactly). Athena is blocked (Slurm account association
missing); a pack is ready there for later.

## 2. Timeline

- 16:30. Read OWNER_BRIEF, NOTEBOOK, audit plan, asset inventory, handover state, ideas round 2, the AD1 / AG5 / cue
  review, the MorDIFF ladder re-read (AD1) result, the landmark ladder (AR1) prereg and code.
- 16:35. Found the A46 RGB-only result (own-crop re-score of all seven MADation / MixFaceNet releases on raw files,
  descriptive). Its per-image score files are at `/mnt/t7/smad_heldout/a46_rgb_only_20261108/scores/<release>/`.
- 16:38. Opened the published tables: MADation arXiv 2501.03800v3 HTML and SelfMAD arXiv 2504.05504 HTML, parsed
  with Python's html.parser (raw HTML in the session scratchpad, parser `src/RS1/` not needed afterwards; the values
  are copied into `prereg.md`). MADation Table 2 permutes the ViT-L/14 OpenCV / WebMorph / MorDIFF labels against
  Table 1 (Table 1 used).
- 16:45. **Finding (no score read):** the A46 E7 pools (`e7area_*`) were made from the SelfMAD-cropped copies of the
  raw E7 files (`/mnt/t7/smad_heldout/a41g/x7/a41g_x7/e7area_*`, 197 x 245) instead of the raw E7 files (428 x 428 in
  `/mnt/t7/smad_heldout/a41g/x7work/in/s*/e7area_*`). A46's E7 numbers for MADation are therefore a crop of a crop.
  RS1 crops the raw E7 files.
- 16:50. `prereg.md` written (before any RS1 score).
- 16:52. `src/RS1/manifest.py build`: 22,091 entries later (see section 3); all A46 crops hash-checked against their
  SHA256SUMS; raw E7 and A43 stored files hash-checked.
- 16:55. Crop smoke (8 raw E7 files): 8 of 8 retained, crop looked right (face, RGB). Score smoke (FE ViT-L/14, 8
  A46 crops): ran, 226 s mostly start-up.
- 16:57. Full crop started, 2 shards. **Shard 0 failed at start with CUDA out of memory** (shared GB10, unified
  memory, swap full). Restarted 17:02.
- 17:00. Analysis code tested on the existing SelfMAD files (`--smoke --B 50`). Reader check: SelfMAD raw-file EERs
  AMSL 2.44, FaceMorpher 0.98, OpenCV 0.37, WebMorph 7.36, StyleGAN 16.60, MorDIFF 1.49, DiM-A 4.41, Greedy-DiM 6.39
  equal the A41 x7 table (`mambamorph-code/experiments/A41_shortcut-proof-zero-gpu/raw/results/a41g_x7.md`).
- 17:03. Scoring of the reused A46 crops started; **failed at start with CUDA out of memory**. Rewrote
  `run_score.sh` with retries (6 tries, 3 min apart); restarted 17:05.
- 17:13. Crop list reordered by priority (A43 control images and raw E7 first; DiM aligned E7 last); journals of
  both shards merged so no box is recomputed (664 boxes kept). Shards restarted.
- 17:16. Shard 0 failed again at start (CUDA out of memory). 17:20 restarted inside a retry loop.
- 17:20. Lead: Athena available. Read `ATHENA.md`. Wrote amendment 1 (corrected MAD22 cells, FS releases, Athena
  platform). Built `src/RS1/athena_pack.py`, `athena_run.py`, `athena_rs1.sbatch`; pack build started (9.6 GB).
  First Athena login worked; the shared venv there does not exist yet, so the job builds its own environment.
- 17:28. MADation ViT-B/16 scored on the 11,264 reused A46 crops (1,366 s). File not opened.
- 17:35. Lead: Athena accounts not associated, do not submit; account to use `plgrestorearc-gpu-a100`. Amendment 2
  from the EV1 review (extra pools, 0.5 rule, threshold pools as a column, paired logit shifts, SelfMAD both genuine
  definitions, border check). Added 7,001 amendment images (`manifest.py amend`), orchestration `run_after.sh`
  started (17:47).
- 17:39. Athena pack finished: `/mnt/t7/smad_next/RS1/athena/rs1a_pack.tar`, 9.58 GB, sha256
  c1cf34ddc9b454252b571c8f8a23b6c38ef291abdb8a15d162b4a7a97acc0661 (code, wheel, 7 weight files, 11,264 A46 crops,
  10,795 images to crop incl. corrected MAD22, 32 crop-check files). Not uploaded (Athena blocked). Second pack with
  the amendment-2 images and the full manifest: `athena/rs1a_pack_amend.tar` (building). `athena_rs1.sbatch` now uses
  account `plgrestorearc-gpu-a100` and extracts the second pack if present.
- 17:45. `analyse.py` extended for amendment 2 (0.5-rule rates, threshold pools as a column, paired logit shifts,
  neutral-only reproduction columns, separate bootstrap draws for FEI subjects and FFHQ images; the FRLL draw is
  unchanged: 102 persons, seed 20261111). Tested on the existing SelfMAD files: SelfMAD at its 0.5 rule flags 0% of
  unprocessed photos, 44.6% after 50% shrink-and-enlarge, 78.9% with the MorDIFF history on our frames, 97.1% of
  stored-small photos: the same values as the EV1 review (consistency check of the new code). `border.py` written and
  tested on 8 files per source (our aligned AMSL frames: 9.5% black pixels; MTCNN and SelfMAD raw-file crops: 0%).
- 17:48. Platform check (MADation ViT-B/16, 11,264 reused A46 crops, DGX rescoring vs the registered A46 RGB-only
  scores from WCSS): PNG crops agree to at most 9.4e-5 in probability; **the FRLL-Morphs crops, which the release
  crop step stores as JPEG (the SMDD script re-saves a .jpg input as .jpg), differ: 1,070 of 7,061 by more than 0.001,
  at most 0.78** (FRLL photo crops, also JPEG, agree to 2e-6). Likely cause: JPEG decoding differs between Pillow
  12.2.0 on the DGX and the WCSS container's Pillow (the Athena environment pins Pillow 10.2.0 like the container).
  Native EERs from the two score sets: AMSL 3.44 vs 3.49, FaceMorpher 0.49 vs 0.86, OpenCV 1.47 vs 1.47, StyleGAN
  17.17 vs 17.17, WebMorph 1.51 vs 1.88, MorDIFF 0.99 vs 0.99. Separately, **on the DiM cells the EER moves by up to
  1.5 points between platforms although the scores differ by at most 4e-5 in probability (5.5e-4 in logit)**: the
  ViT-B/16 logits of photos and DiM morphs are packed between about -12.2 and -10.3, so near-ties decide the EER.
  Both are recorded in `rs1_platform_check.json`; result tables print both platforms where both exist.
- 17:50. SelfMAD own scoring (AR1 `score.py --mode own`) smoke on 8 FEI frames: ran (one CUDA out-of-memory start
  failure first, then 224 s), dlib found a face in 8 of 8.
- 18:22. MADation ViT-L/14 scored on the reused A46 crops (3,251 s). Platform check: 399 of 11,264 crops differ from
  the registered A46 scores by more than 0.001 (max 0.92); native EER DGX vs WCSS e.g. MorDIFF 27.48 vs 28.81 (PNG
  crops: near-tied saturated scores), DiM-A 29.95 vs 31.39, AMSL 8.83 vs 8.87.
- 18:25. Lead: Athena accepts jobs (account `plgrestorearc-gpu-a100`); if the full scoring would take more than about
  an hour on the DGX, move it there; all rows compared with each other must come from one platform.
  **Decision (18:30, sent to the lead): Athena for every MADation / MixFaceNet-MAD row** (all cells, amendment
  pools, corrected MAD22, FS releases), because the remaining DGX work (7,001 amendment crops, three releases on
  11,264 crops, five releases on 11,885 new crops) was several hours at the DGX's throughput. **SelfMAD stays on the
  DGX**, scored there on one platform (raw FRLL photos, raw MorDIFF morphs, raw E7 MorDIFF files, A43 stored images,
  FEI, FFHQ; 9,209 images, `lists/selfmad_own_dgx.csv`, `run_selfmad_dgx.sh`, started 18:30); the existing SelfMAD
  files (WCSS) form a second, separate SelfMAD run. Stopped on the DGX at 18:29: the MADation scoring of the A46 crops
  (FE ViT-L/14 had just failed its first start with CUDA out of memory) and the amendment crops (`run_after.sh`). The
  finished DGX ViT-B/16 and ViT-L/14 scores and the 4,884 DGX crops serve as the equivalence check.
- 18:31. Athena folders `packs/RS1`, `tasks/RS1`, `results/RS1`, `envs/RS1` created; resumable upload of both packs
  started (`athena_upload.sh`: rsync --partial --append-verify, each connection at most 240 s under the transfer
  lock). A `pkill -f athena_upload.sh` killed my own shell (its command line matched); the orphaned rsync was then
  killed by PID and the upload restarted.
- 18:40. Lead: on Athena `-C localfs` gives only 4.0 GB of `$SCRATCH_LOCAL` (a smoke job of the lead died there with
  "No space left on device"); use `-C memfs` and work in `$MEMFS` (a RAM disk counted in `--mem`, at most 120 GB per
  GPU). Two locks: short commands `flock -w 300 /tmp/smadnext-athena-cmd.lock ssh ...`, transfers
  `flock -w 1800 /tmp/smadnext-athena.lock rsync ...`; a flock timeout returns 1 silently (a local wait, not a refused
  login). `athena_rs1.sbatch` changed to `-C memfs`, `--mem=110G`, work in `$MEMFS/rs1` (about 30 GB).
- 18:49. Both packs on Athena (`packs/RS1/rs1a_pack.tar` 9.58 GB in 13 min, `rs1a_pack_amend.tar` 2.53 GB, sha256
  6cdce864dd33b1d05748b63a9e6a18981813769cb695214c466532d18c146df6); the job checks both hashes on the compute node.
- 18:50. **Athena smoke job 3544220** submitted (`sbatch --time=01:00:00 --export=ALL,RS1_LIMIT=8 tasks/RS1/athena_rs1.sbatch`:
  builds `envs/RS1/venv`, unpacks, crops 8 images of every set, scores them and 8 reused A46 crops of every set with
  all seven releases). Log `.../smad-next/logs/RS1-3544220.out`; result `results/RS1/rs1a_smoke_3544220.tar`.

## 3. Data

All under the DGX. Master manifest `/mnt/t7/smad_next/RS1/manifest.csv` (columns id, set, label, persons, photo,
expr, src_path, src_sha256, crop_origin, crop_path); a copy before amendment 2: `manifest_before_amend2.csv`.

| Set | Images | Source | Crop |
|---|---|---|---|
| G_raw | 204 | raw FRLL front photos `/mnt/t7/Datasety/downloads/frll_base/extracted/{neutral,smiling}_front/` | A46 RGB crop (reused) |
| M_amsl / facemorpher / opencv / webmorph / stylegan | 2,175 / 1,222 / 1,221 / 1,221 / 1,222 | raw FRLL-Morphs `/mnt/t7/Datasety/downloads/FRLL-Morphs/facelab_london/morph_*` | A46 |
| M_mordiff | 1,000 | raw MorDIFF `/mnt/t7/Datasety/downloads/MorDIFF/MorDIFF_crop/*/morphed/` | A46 |
| M_dim_a ... greedy_dim_s | 500 each (fast_dim_ode 499) | raw DiM `/mnt/t7/Datasety/downloads/DiM-FRLL-Morphs/morphs/` | A46 |
| E7raw_mordiff / dim_a / greedy_dim | 204 each | raw E7 files `/mnt/t7/smad_heldout/a41g/x7work/in/s*/e7area_*` (prep_eval.degrade 'R', registered resmatch scale; sha in `x7_inputs.csv`) | new |
| Galn_frll / Galn_mordiff | 204 each | our aligned native frames `smadcvpr_data/eval/frllm/frll_bona/*_orig.png`, `eval/mordiff/mordiff_bona/*_orig.png` (the MorDIFF-cell frames differ from the FRLL ones; DiM-cell frames equal FRLL ones) | new |
| E7aln_<family> (12 families) | 204 each | our aligned E7 frames `eval/*/*_resmatch_<family>.png` | new |
| a43_A, B, B20, C, C20, D, D20, E | 200, 200, 200, 102, 102, 204, 204, 204 | A43 stored files `/mnt/t7/smad_heldout/a43/data/a43/stored/<arm>/` (manifest `a43.csv` sha ce3a264a) | new |
| amendment 2: Gjpeg50_frll, Gjpeg70_frll, Gresample50_frll | 204 each | `eval/frllm/frll_bona/*_{jpeg50,jpeg70,resample50}.png` | new |
| amendment 2: FEI_neutral, FEI_smiling | 198, 187 | gtest frames `smadcvpr_data/gtest/{neutral,smiling}/bona/` (gtest.csv sha 5ededd6f) | new |
| amendment 2: FF_orig, FF_E7diffae, FF_E7lmc | 2,000 each | `/mnt/t7/smad_heldout/ffhq_morphs/eval/ffhqm/ffhq_bona/*_{orig,resmatch_diffae,resmatch_landmark_complete}.png` (ffhqm.csv sha 732b53c8) | new |

Reused A46 crops: `/mnt/t7/smad_heldout/a46_corrective_20261108/rgb_clip/<pool>/` (manifest
`manifests/a46c_rgb_clip.csv`, SHA256SUMS checked: 0 mismatches). New crops: `/mnt/t7/smad_next/RS1/crops/main/`
(list `lists/tocrop.csv`, 4,884) and `crops/amend/` (list `lists/tocrop_amend.csv`, 7,001). Crop check (32 raw files
already cropped by A46): `lists/cropcheck.csv` -> `crops/check/`.

Corrected MAD22 (Athena pack only so far): raw `/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/author_files/original_sorted/`
(4,687 files, hash-checked against `mambamorph-code/experiments/dataaudit/marco_owncloud_20261109T103840Z/verified_inventory.json`),
aligned `mad22_canonical_E7_inputs_v3_20261109T113746Z/{native/BonaFide,e7/<family>}` (1,224, hash-checked against
`PROCESSED_SHA256SUMS`). Athena pack `/mnt/t7/smad_next/RS1/athena/rs1a_pack.tar` (+ `.sha256`; manifest
`athena_manifest.csv`, 22,091 rows) - not yet uploaded.

Existing SelfMAD scores reused (release sha 0ad8db6f): A41 x7 raw files
`/mnt/t7/smad_heldout/a41g/a41g_out/x7/selfmad_hrnet_w18/x7/scores_a41g_x7.npz` (manifest `a41g/x7/manifests/a41g_x7.csv`,
sha 5d6d8412); A32-RSX frames `mambamorph-code/experiments/A32-RSX_resolution-shortcut/raw/selfmad_own_eval.npz`
(eval.csv sha 86d055d3); A43 own frames `/mnt/t7/smad_heldout/a43/a43_out/a43/selfmad_hrnet_w18/own/scores_a43.npz`.

## 4. Code

`/home/narolski/smad-next/src/RS1/`:

| File | Job |
|---|---|
| `ar1_common.py`, `crop_rgb.py`, `score.py`, `stats.py` | byte-identical copies of the landmark ladder (AR1) files (sha 42806acb, 07b179bd, 56bb1244, 7da0afd8) |
| `manifest.py build / merge / amend` | image manifest, crop lists, merge of crop results into `lists/score.csv` |
| `rs1_score.py` | runs AR1 `score.py` with the two FE weight files added to its weight table; checks the copies' hashes |
| `run_crop.sh` | 2 crop shards, crop check, merge |
| `run_score.sh a46 / new / amend` | scores one crop list with the five releases (retries on CUDA out of memory) |
| `run_after.sh` | waits for the main crops, crops amendment 2, merges, scores new and amendment crops, then SelfMAD own on FEI / FFHQ / A43 stored |
| `analyse.py` | all tables (person bootstrap B = 2,000, seed 20261111) -> `experiments/RS1_own-crop-rescore/rs1_*.csv`, `rs1_results.json` |
| `tables.py` | markdown tables from `rs1_results.json` |
| `platform_check.py` | rescored A46 crops vs the registered A46 RGB-only scores; crop-check boxes vs A46 boxes |
| `athena_pack.py`, `athena_run.py`, `athena_rs1.sbatch` | Athena pack, path wrapper, job (not submitted) |

Release preprocessing as reconstructed (the A46 RGB-only path):
- Crop (MADation, MixFaceNet-MAD): the SMDD script `/mnt/t7/thirdparty/smdd_9683229_20261107/image_preprocess.py`
  lines 9 (MTCNN(select_largest=True, post_process=False, min_face_size=64)), 21 (cv2.imread, BGR), 24 (detect),
  32-40 (5% margin, slice). The original passed BGR pixels to MTCNN and left negative slice indices unbounded (the A46
  crop defect); the corrected path `mambamorph-code-a46/smadcvpr/a46_corrective_crop.py` lines 34-36 (RGB pixels to
  MTCNN) and 39-60 (same 5% arithmetic, all four edges clamped) is used. AR1 `crop_rgb.py` batches up to 16 images
  of equal size per detect call (AR1 measured at most 0.04 px box difference).
- MADation input: `mambamorph-code/baselines/MADation/src/data/loaders.py` lines 208-247 (FaceDataset: cv2.imread,
  so BGR; Resize([224, 224]); Normalize(0.5, 0.5); label bonafide = 1, so morph = class 0). Implemented in
  `mambamorph-code-a46/smadcvpr/a12_released.py` lines 88-95 (spec) and 129-138 (`adapt_input`: RGB loader output ->
  BGR, (x - 0.5) / 0.5). Decision key `score_noTTA` = sigmoid of the morph logit; RS1 ranks on `logit_noTTA`.
- MixFaceNet-MAD: `a12_released.py` lines 100-104 (BGR, (x - 0.5) / 0.5, 224, class 0 = attack).
- SelfMAD (existing scores): `mambamorph-code/smadcvpr/rsx_selfmad_own.py` (dlib frontal detector, 81 landmarks,
  landmark box + margin, 384 x 384, /255, softmax[:, 1]); A41 x7 used the release's own `crop.py` on raw files.

Environment (DGX): crops in `/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv` (facenet-pytorch 2.6.0, torch
2.12.1+cu130 from `.venv-spark`, OpenCV 4.11.0, numpy 1.26.4); scoring `/home/narolski/mambamorph-code/.venv-spark/bin/python`.
Weights: MADation LoRA ViT-B/16 ddb1455b, LoRA ViT-L/14 bb452ded, FE ViT-B/16 6a4d93ba, FE ViT-L/14 74dd7fbc,
FS ViT-B/16 a7cacd47, FS ViT-L/14 6071ec7b (all in `/mnt/t7/smad_heldout/mad22_production_cpu_stage_v1/payload/models/<sha>.safetensors`);
MixFaceNet-MAD `/mnt/t7/mixfacenet_mad_official/mixfacenet_SMDD.pth` (3d507c8b); SelfMAD
`/mnt/t7/smad_next/AR1/weights/selfmad_release/hrnet_w18_checkpoint.model.safetensors` (0ad8db6f, fetched by AR1).

## 5. Results

None read yet for MADation / MixFaceNet. SelfMAD (existing files, analysis-code test only, B = 50): see `result.md`
when written.

## 6. Checks

Done: A46 crop hashes (0 mismatches); raw E7, A43 stored, MAD22 raw and canonical v3 hashes; copied AR1 files
byte-identical; SelfMAD reader reproduces the A41 x7 EERs exactly. Planned: platform check of rescored A46 crops
against the registered A46 RGB-only scores; 32-file crop check against A46 boxes.

## 7. Dead ends and failures

- Crop shard 0 failed twice at start with CUDA out of memory (16:57, 17:16) and the first scoring run once (17:03):
  the shared GB10 has unified memory and full swap. Fix: retry loops (`run_score.sh`, the shard-0 loop, `run_after.sh`).
- Throughput under `nice -n 10` at load average about 90: MTCNN crops about 0.4 images/s per process; ViT-B/16
  scoring 11,264 crops in 23 min.
- `run_score.sh` was edited (17:45) while its a46 run was executing; bash may read the changed tail after its loop.
  Check `run_score_a46.log` for a stray error after the last detector; the score files themselves are unaffected.
- A46's E7 pools are crops of SelfMAD crops (section 2, 16:45).
- The Athena shared environment `.../smad-next/venv` does not exist; the RS1 job builds `envs/RS1/venv` itself.

## 8. Observations and ideas

- The release crop step re-saves JPEG inputs as JPEG (quality 95, OpenCV default), so the crops of JPEG benchmark files
  carry one more JPEG generation and their scores depend on the JPEG decoder of the scoring machine (section 2,
  17:48). AR1's `crop_rgb.py` stores every crop as PNG: on the corrected MAD22 (JPEG bona fide, FaceMorpher, OpenCV,
  Webmorph files) the Athena crops therefore differ from the original script by that JPEG generation (recorded as a
  deviation in amendment 1's run).
- MADation ViT-B/16 logits on DiM crops and FRLL photos are packed in a narrow band (about -12.2 to -10.3): EERs on
  those cells are numerically fragile (up to 1.5 points between two GPUs).

- For FRLL StyleGAN2 the E7 control is the identity (StyleGAN2 morphs have a larger inter-eye distance than the
  photos, so the registered rule leaves the photo unchanged).
- MorDIFF-cell aligned frames (`mordiff_bona`) differ from the FRLL-cell frames of the same photos.

## 9. Open items and next steps

Finish crops and scoring on the DGX; platform and crop checks; border check (amendment 2 d); analysis extensions for
amendment 2 (0.5 rule, threshold-pool column, paired logit shifts, SelfMAD both definitions); `result.md`; Athena run
when the account works (corrected MAD22 cells and FS releases need it unless run on the DGX).

## 10. Handover state (11 Nov 17:50)

DGX processes (all `nice -n 10`):
- `run_crop.sh` (PID 2073469) with crop shard 1 (PID 2073478); log `/mnt/t7/smad_next/RS1/crops/main_shard1.log`.
- shard-0 retry loop (PID 2077408, crop PID 2077409); log `crops/main_shard0.log`.
- `run_score.sh a46` (PID 2066860; scorer PIDs change per release); log `/mnt/t7/smad_next/RS1/run_score_a46.log`,
  per-try logs `scores/log_<release>__a46_try<k>.log`.
- `run_after.sh` (started 17:47); log `/mnt/t7/smad_next/RS1/run_after.log`.
If a step fails: every script is idempotent (skips finished outputs); rerun the same command. Crops resume from
their box journals. Compute so far: DGX GPU only (shared); Athena 0 GPU-hours.

## 11. Reproduce from scratch

```
P=/home/narolski/mambamorph-code/.venv-spark/bin/python; S=/home/narolski/smad-next/src/RS1
$P -I $S/manifest.py build && $P -I $S/manifest.py amend
$S/run_crop.sh            # main crops (2 shards), crop check, merge
$S/run_score.sh a46       # five releases on the reused A46 crops
$S/run_after.sh           # amendment crops, merge, new + amendment scoring, SelfMAD own on new pools
$P -I $S/platform_check.py
$P -I $S/analyse.py --B 2000 && $P -I $S/tables.py > /mnt/t7/smad_next/RS1/tables.md
```
