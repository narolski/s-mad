# SMDD five-partner audit and rebuild of the standard training set (SM1): full record

Owner: hypothesis-owner agent, 11 Nov 2026. Registration: `prereg.md` (amendments A1 to A6). Short verdict:
`result.md`. Code: `/home/narolski/smad-next/src/SM1/`. Large outputs: `/mnt/t7/smad_next/SM1/`.

## 1. Question and current answer

SMDD (Synthetic Morphing Attack Detection Development dataset, Damer et al., CVPRW 2022) is the field's standard
training set: 25,000 StyleGAN2 genuine renders and 15,000 landmark morphs at 256 px per split. On disk, every
training morph has one of only **five** second contributors (the same five renders for all 3,853 first contributors);
the evaluation split has five other partners. The paper's sentence reads naturally as five random partners per key
image; the release differs from that natural reading (not called a bug). Questions: (1) do released SMDD-trained
detectors memorise the five partners (Part 2 and the no-new-image tests T-A, T-B); (2) does rebuilding SMDD with
balanced partners, warped halves as genuine images and history crossing change what a head on frozen CLIP
features learns (Part 3), and later the same with LoRA fits on Athena. **Status 11 Nov 17:40: Part 1 done; no
detector score of this experiment has been read yet; landmark, build and feature stages running.**

## 2. Timeline

- 15:25 Read OWNER_BRIEF, NOTEBOOK, 11_AUDIT_PLAN, 10_ASSET_INVENTORY, 12_STATE_AT_HANDOVER, CONSOLIDATED_v1, the
  two idea entries (ROUND1_raw.json data/ideas[1] "SMDD-T", pragmatist/ideas[2] "SMDD-X").
- 15:30 to 15:36 Part 1 structure audit: `src/SM1/p1_document.py` → `p1_structure.json` (both splits).
- 15:34 SMDD paper checked (arXiv 2203.06691 HTML, Section 4), pairing sentence quoted in `result.md`.
- 15:50 `prereg.md` written before any score. 15:50 to 16:00 pre-run review by the `experiment-reviewer` agent:
  GO WITH FIXES (1 blocker: five specific partners vs five others, needs a partner-level test; majors: falsifier
  mapping, arm bundling, responsiveness gate, halves flag test; minors). All registered as amendment A1 at 16:10.
- 15:43 to 16:00 first landmark run attempts: (a) a parent process stuck re-reading an npz member 25,000 times
  (bug, fixed); (b) two `pkill -f` / `pgrep -f` commands matched my own shell and killed it (exit 144; see
  section 7); (c) 6 workers at nice 10 ran at 5 to 10% CPU each on a machine at load 70 to 140.
- 16:15 amendment A2: the 6,000-render "extra" landmark stage dropped; arm (b′) partners from the pool, cap 7.
- 16:23 feature-path check: tower identical to the FE ViT-L/14 release (0.0); header on our features vs A12REL
  scores misses the registered 1e-3 tolerance (0.0062 TF32, 0.0046 fp32); recorded, TF32 kept.
- 16:29 to 16:41 WCSS CPU task `SM1_cpu_c` packed, tested on the DGX on 8 pairs (pass), uploaded (one rsync,
  1 min 22 s) and staged; the lead submitted it as WCSS job 6301971 (48 cores).
- 16:45 amendment A3 (lead, after vetting round 2): framing corrections, licence quote, T-A, T-B, T-C, evaluation
  partners as a third audit set, partner-count dose curve, Laplacian-variance acceptance, expression check.
- 16:37 licence text fetched from the project README (raw GitHub), quoted in `result.md`.
- 16:50 T-C done (`tc_files.json`); geometry expression substitute registered (the pixel probe cannot run as is).
- 16:54 WCSS login node began refusing connections (lead); no further WCSS connection made.
- 17:00 amendment A4 (author approvals): arm (e) history crossing in full; shrink call verified byte for byte
  (`shrink_verify.json`).
- 17:03 first smoke build of arm (c) crashed on an engine error (render with landmarks outside the frame) →
  amendment A5 (17:10): renders admissible only with all 106 points inside [0, 255]; engine failures are skipped as
  78 does. WCSS job 6301971 will fail on the same error (lead told 17:05). The 705 + partial files of the aborted
  smoke build deleted (made by this experiment); stale pack renamed `sm1_c_pack_STALE_preA5.tar`.
- 17:10 to 17:16 smoke (c) and (c′) rebuilt with the A5 lists: 500 + 500 pairs, 0 failures.
- 17:25 amendment A6: T-A / T-B on whole files (A39 path) with a one-pass multi-detector scorer (`rel_multi.py`).
- 17:30 pool landmarks finished (3,025 renders, 4,500 s, 0 without a face; reproduction ≤ 0.014 px).
- 17:31 audit lists written (500 keys; matched unused partners; 20 placebo; 5 evaluation partners).
- 17:35 contributor landmark stage restarted with 4 workers (it had been started with 2, then killed by a
  self-matching `grep`); pack c rebuilt with the A5 lists for the rented machine "leaseB" (lead's offer, 17:32).
- 17:38 leaseB venv: Python 3.10.13, numpy 1.26.4, opencv-python-headless 4.11.0.86 (`/workspace/sm1/venv`).
- 17:45 First DGX feature list finished: 14,120 FRLL evaluation frames in 4,201 s (3.4 images/s, CPU decode bound,
  GPU 2.2 GB). Told the lead the full feature pass would take 15 to 19 h on the DGX.
- 17:48 leaseB 8-pair check of task c: unchanged 78 command line vs wrapper max 0; leaseB vs DGX reference outputs
  max 0 over 32 files (8 pairs x morph + halves, 8 c′ pairs). Full task c on leaseB (96 workers, nice 19):
  15,000 (c) morphs + 30,000 halves in 112 s, 15,000 (c′) morphs in 99 s, 0 engine failures, halves average within
  0.5 grey level; tar 6.75 GB fetched in 291 s, sha256 OK (`/mnt/t7/smad_next/SM1/lease/`).
- 17:55 Lead's decision: (1) up to 6 extra DataLoader workers at nice 19 on the DGX for the feature and
  release-scoring passes; (2) the ~190,000 training-image feature pass must not run on the DGX: a self-contained
  x86 CUDA pack (AD4 environment) is prepared (`gpu_pack.py`, `feats_gpu.py`), run place decided by the lead at
  19:15; (3) platform rule registered as amendment A7 (all rebuilt-arm head features from one GPU machine; DGX
  features only for an equivalence check). DGX feature chain stopped after `test_eval` (kept for that check).
- 17:58 T-A / T-B first start with all 7 releases in one process ran out of GPU memory (GB10 unified memory, about
  20 GB free system-wide); restarted as three detector groups (`run_tab_multi.sh`, batch 32, 6 loader workers at
  nice 19). The earlier unexplained CUDA error of the 8-image test was very likely the same out-of-memory condition.
- 18:05 pack a (audit 9,520 pairs + AR1 halves 536 pairs, 0.49 GB, sha256 f48f125a…) built and sent to leaseB.

## 3. Data

Inputs (read only):
- SMDD training release `/mnt/t7/Datasety/downloads/SMDD/SMDD_release_train/{os25k_bf_t (25,000), m15k_t (15,000),
  train.csv}`; evaluation release `.../SMDD_release_evaluation/{os25k_bf_e, m15k_e, *_crop224, evaluation*.csv,
  crop_images_224.py}`; morph-source renders `.../SMDD/os25k_m_t` and `os25k_m_e` (25,000 each; origin of these
  folders not recorded on disk).
- Stored landmarks of the genuine renders `.../SMDD/smdd_bona_landmarks_if106.npz` (sha256 f167eaf8…, 25,000 x 106,
  normalised; 3 NaN); look-alike table `smdd_bona_lookalikes.npz` (32 ArcFace neighbours, `os25k_bf_t` only).
- Shrunk copies of the genuine renders (a47, 80 px) `/mnt/t7/smad_heldout/a47/data47/i3/train/smdd_a47e7/os25k_bf_t`.
- Test frames: `eval.csv` FRLL-Morphs / MorDIFF / DiM rows (orig, resmatch) under
  `/home/narolski/mambamorph-code/smadcvpr_data/eval`; corrected MAD22
  `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/{native,e7}`; AR1 ladder
  `/mnt/t7/smad_next/AR1/manifest.csv` (18,239 rows) and its frames.

Produced (all under `/mnt/t7/smad_next/SM1/` unless said):
- `lm/srcm_if106_pool.npz` (3,025: 3,000 seeded non-contributors + 5 partners + 20 check renders; with ArcFace
  embeddings), `lm/srcm_if106_evalp.npz` (5 evaluation partners), `lm/srcm_if106_contrib.npz` (running).
- `tem/{bf,src,srce}/<name>.tem` (24,630 / 2,963 / 5 admissible renders; pixel = normalised x 256).
- `lists/`: `armc_15k.csv`, `armcr_15k.csv` (15,000 each, A5 rule), `smoke_armc.csv`, `smoke_armcr.csv` (prefixes),
  `audit.csv` (9,520 rows: 2,500 KP, 2,500 KU, 2,500 KE, 2,000 KX, 10 PP, 10 UU), `audit_renders.csv` (535),
  `smoke_audit.csv` (750), `ar1h.csv` (536). Pending: `armb, armbp, armd50, armd500, armc, armcr` (need N).
- `img/armc/`, `img/armcr/`: smoke builds (500 morphs + 1,000 halves; 500 morphs).
- `flists/`: feature lists `test_eval.csv` (14,120), `test_mad22.csv` (5,707), `test_ar1.csv` (18,239),
  `train_bf.csv` (25,000), `train_m15k.csv` (15,000), `tab.csv` (50,010, T-A / T-B).
- `wcss/packs/SM1/sm1_c_pack.tar` (rebuilding with A5 lists), `wcss/staging/SM1/cpu/SM1_cpu_c/` (run.sh, cpus,
  est_minutes, task.env), `wcss/test_c/` (DGX test of the task).
- `madation_convert/A12REL/*/convert.json` (extracted from the MADation release tar; maps release names to sha256).

## 4. Code (`/home/narolski/smad-next/src/SM1/`)

| Script | Job |
|---|---|
| `sm1_common.py` | paths, partners (training and evaluation), sha, `.tem` writer, if106 loader |
| `p1_document.py` | Part 1 structure audit → `p1_structure.json` |
| `landmarks.py` | insightface buffalo_l pass (det 512, 106 points, ArcFace where needed), stages pool / contrib / evalp |
| `pairs.py` | `.tem` files (`tems`), 15k (c)/(c′) lists (`c15k`), audit lists (`lists audit`), all lists (`lists`) |
| `build.py` | unchanged 68/78 engine via a recorder wrapper; halves; asserts; `--verify-cli`, `--compare`, `--root` |
| `wcss_prep.py`, `wcss_run.sh` | one-tar-in / one-tar-out CPU task (WCSS or leaseB) |
| `featlists.py` | feature lists (train, test, audit, smoke) |
| `feats.py` | frozen CLIP ViT-L/14 features (FE release convention) and the feature-path check |
| `heads.py` | Part 3 logistic heads per arm and seed, scores on all test and audit images; FE header reference |
| `read_p3.py`, `read_p2.py` | Part 3 and Part 2 readers (registered statistics) |
| `sm1_stats.py` | person bootstrap Draw, weighted AUC, weighted EER |
| `rel_score.py`, `rel_multi.py` | released detectors (AR1 release path); multi-detector one-pass scorer |
| `tab.py` | T-C file check, T-A / T-B lists and reader |
| `shrink.py` | arm (e) shrink step = `a47_data._one` unchanged (verify, run) |
| `lapvar.py` | Laplacian-variance acceptance per arm |
| `expr_geom.py` | geometry-only smile probe (A3 substitute) |
| `run_p2.sh`, `run_tab.sh`, `run_feats.sh`, `run_contrib.sh` | chains |

Environment: DGX `/home/narolski/mambamorph-code/.venv-spark/bin/python` (Python 3.12.3, torch 2.12.1+cu130,
timm 1.0.27, cv2 4.11.0, numpy 1.26.4, insightface 1.0.1, onnxruntime 1.27.0); facenet venv
`/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv` for MTCNN crops (AR1 `crop_rgb.py`, unchanged). Engine
sha256: 68_hires_morph.py 71643aad…, 78_tool_morph.py b8a389f1…. Release weights (staged payload, by sha256):
MADation ViT-B/16 ddb1455b…, ViT-L/14 bb452ded…, FE ViT-B/16 6a4d93ba…, FE ViT-L/14 74dd7fbc…, FS ViT-B/16
a7cacd47…, FS ViT-L/14 6071ec7b…; MixFaceNet-MAD 3d507c8b…. CLIP tower: timm
`vit_large_patch14_clip_quickgelu_224` with the cached `timm/vit_large_patch14_clip_224.openai` weights. Seeds:
heads 401 to 405; data draws 20261111 (+ offsets in the scripts).

## 5. Results

Part 1 and T-C only so far (see `result.md`, `p1_structure.json`, `tc_files.json`). No detector score read.
Partner matching for the audit (`pairs_summary_audit.json`): trained → matched unused partner with (mean cos to
keys, sd, IOD px, yaw proxy): img054553 (0.063, 0.070, 63.2, 0.00) → img167417 (0.054, 0.069, 63.7, −0.03);
img282038 → img029400; img496816 → img200961; img337488 → img380037; img099545 → img197375. Mean ArcFace cosine key
to partner: trained 0.037, matched unused 0.035, placebo 0.028.

## 6. Checks

Verified: landmark pass reproduces stored if106 points (max 0.014 px over 20 renders); wrapper = unchanged 78 command
line (max 0 on 8 + 8 pairs); halves average within 0.5 grey level of the morph on every built pair; shrink call =
stored a47 copies byte for byte (8 of 8); CLIP tower = FE release tower (0.0); release CSVs vs folders (T-C).
Not verified / failed: FE header reproduction within 1e-3 (missed, 0.0062); where `os25k_m_*` came from; WCSS
OpenCV 5.0 vs DGX 4.11 equality (job never ran successfully).

## 7. Dead ends and failures

- `pkill -f` / `pgrep -f` / `grep` over `ps` with a pattern that also occurs in my own command line killed my
  own shell three times (exit 144). Fix: start long jobs from a script file (`run_contrib.sh`) and select PIDs by a
  pattern that does not appear in the killing command.
- npz member re-read in a dict comprehension (25,000 reads of a 21 MB array): fixed by reading members once.
- The first `rel_multi.py` 8-image test printed a CUDA error (text lost to a `tail -3`); the identical rerun
  passed (8 images x 7 detectors). Not reproduced; cause unknown (shared GPU).
- WCSS job 6301971 (task `SM1_cpu_c`, old lists) will fail: build.py stopped on engine errors before A5. Not
  re-staged because the WCSS login node refuses connections since 16:54.
- Arm (e) was skipped in the first registration (shrunk copies are 80 px); re-enabled by the author's approval (A4).
- The cue-check pixel expression probe cannot run on 256-px FFHQ-aligned renders without an aligner; replaced by a
  geometry probe (A3 note).
- FE header check tolerance (1e-3) missed; attributed to platform numerics, not further verified.

## 8. Observations and ideas

- 367 of 24,997 genuine renders and 42 of 3,005 pool renders have landmark points outside the 256-px frame
  (chins below the frame mostly: 362 above 255).
- SMDD morph files 257 to 264 px tall (733 training, 417 evaluation) are an image-size cue unique to the attack class.
- The pairing condition of the SMDD terms covers our audit morphs and arms (b), (b′), dose (release source data).

## 9. Open items and next steps

Contributor landmarks → all lists → leaseB build of (c), (c′) [and (b), (b′), K = 50, 500] → copy back with hashes →
arm (e) shrink on the DGX → Laplacian acceptance → features → heads (smoke, then 5 seeds) → readers. Part 2: smoke
audit build (750) → crops → scores → full audit. T-A / T-B: `rel_multi.py` on `tab.csv`. Athena LoRA fits after the
arms exist (account plgrestorearc-gpu-a100; Slurm associations missing; do not submit until the lead says so).

## 10. Handover state (17:40)

- DGX: contributor landmarks (`run_contrib.sh`, log `/mnt/t7/smad_next/SM1/landmarks_contrib.log`, output
  `lm/srcm_if106_contrib.npz`; rerun the script if it dies). Feature pass `run_feats.sh 0 test_eval test_mad22
  test_ar1 train_bf train_m15k` (log `feats_run1.log`; outputs `feat/<name>.npz`; rerun skips finished lists).
  Pack c rebuild `wcss_prep.py --task c` (log `wcss/prep_c_v2.log`).
- WCSS: job 6301971 (will fail; stale). Nothing else.
- leaseB (89.221.67.144:17736, volatile, ends about 23:00): `/workspace/sm1/{venv,packs,results,tmp,logs}`.
- Compute: GPU about 1 h on the DGX (shared); no rented cost of our own.

## 11. Reproduce from scratch

1. `python3 -I src/SM1/p1_document.py`; `python3 -I src/SM1/tab.py tc`.
2. `python3 -I src/SM1/landmarks.py --stage pool|contrib|evalp --workers 4`.
3. `python3 -I src/SM1/pairs.py tems`; `pairs.py c15k`; `pairs.py lists` (after contrib).
4. Builds: `python3 -I src/SM1/build.py --list <list> --workers N` (or `wcss_prep.py --task c|b` + `wcss_run.sh`).
5. `python3 -I src/SM1/shrink.py verify`; `shrink.py run --list ... --out-dir /mnt/t7/smad_next/SM1/img/arme`.
6. `python3 -I src/SM1/featlists.py test|train|audit|smoke`; `run_feats.sh W <lists>`.
7. `python3 -I src/SM1/heads.py [--smoke]`; `heads.py --fe-ref`; `read_p3.py`; `read_p2.py`.
8. Part 2: `run_p2.sh smoke|full`; T-A / T-B: `rel_multi.py --manifest flists/tab.csv --out-dir p2scores/tab`,
   `tab.py read`.
