# Protocol network, first tests (PN1): full record

Owner: PN1 hypothesis owner (Claude agent), DGX and Athena. Started 11 Nov 2026, 18:42 CET. Follows
`/home/narolski/smad-next/DOCUMENTATION.md`. Registration: `prereg.md` (this folder; amendments 1 to 3). Short verdict:
`result.md` (when tier 1 is read). Code: `/home/narolski/smad-next/src/PN1/`. Large outputs: `/mnt/t7/smad_next/PN1/`.

Terms: R0 camera photo; R0_61 / R0_112 the photo stored small (shrunk to 61.2 or 112.7 px between the eyes and enlarged
by the registered path); R2w warp-only image (toward the mean shape of the person's two photos); R2w4 warp-only image
toward the two-person mean shape (geometry-matched negative); R3 same-person morph; R3m mirror self-morph; R4
two-person morph; "_61"/"_112" stored copies. AF0 = the alpha-field probe (its images: photo, zero = warp-only toward
the pair's mean shape, u50 = two-person morph, halfA/halfB = the morph's own warped halves). τ_0.5 = own rule;
τ_dev = 5% false alarms on every development camera-photo pool (incl. its 61/112 px copies). Classes: genuine (camera
photo and its stored copies), attack (two-person morph and its copies), single-subject (everything else; negatives in
training, own table in reporting).

## 1. Question and current answer

Question: does the registered MADation recipe (CLIP with LoRA, last checkpoint), trained on manifest B (negatives =
camera photos, warp-only images, the morph's own warped halves and 61.2 px copies of photos and halves; attacks =
two-person morphs and their 61.2 px copies), keep the morph signal while not reacting to storage history and softness
at one fixed threshold, where the same recipe on manifest A (camera photos against two-person morphs) does react?
Amendment 1 adds manifest C (B plus JPEG 90/70 copies of half of B's images in both classes).

Status 11 Nov 19:55 CET: tier 0 on CLIP features done (section 5.1); DINOv3 tier 0, certificate and matched-subsample
test pending (inputs being computed); tier 1 pack being written; Athena smoke job next; the six fits wait for the
lead's GO (pre-run review restarted by the lead). No conclusion is drawn here.

## 2. Timeline (11 Nov 2026, CET, machine clock)

- 18:42 Read OWNER_BRIEF, DOCUMENTATION, ATHENA, NOTEBOOK, CONSOLIDATED_v3, the three vetted cards, the records of
  AF0, AR1, SM1, AD4 (sections 3 to 10, `run.sh`, Athena job files), EV1. Inspected list files, feature caches and
  `train.py` / `common.py` of the AD4 pack (row selection, sampler, loader) to fix the manifest convention.
- 18:50 Found: 67 of the 663 AF0 persons are validation-reserved (`prep_train.is_val`); the ladder partner map is a
  permutation (each host is the partner of exactly one host), so a random development draw leaves only 48 to 88
  ladder training hosts; choosing the development hosts among the partners of test hosts leaves 156 (124 with a usable
  morph). Registered that rule.
- 18:58 `src/PN1/split.py` (CPU, lists only): `split/ladder_split.csv`, `split/af0_split.csv`, `split/split_summary.json`.
  T = AF0's 200 softened hosts (seed 401, checked identical), 191 readable; D = 100 (seed 402); L = 156 / 124.
- 18:59 to 19:23 `src/PN1/soften_dev.py`: 226 development camera photos (100 development-ladder R0 + 126 AF0
  validation photos outside V); 8-image test passed (aligned, scales 0.456 to 0.874); full build 452 copies, 0 failures
  (PID 2335741).
- 19:00 Coordinator's addition (certificate, matched-subsample test, rung R2w4, class wording) put into the
  registration before any computation (section 9).
- 19:01 `src/PN1/lists.py`: r2w4 (1,072), frll_e5 (1,020); subsets r2w4_td (600) and frll_e5s (612) written inline.
- 19:06 `prereg.md` written (sha256 `efc5c32a…` before header-time corrections). Report 1 to the lead.
- 19:07 to 19:19 DGX GPU queue 1 (`run_gpu1.sh`): CLIP means for eq8_ar1, r2w4, frll_e5 (676 s). 8-image check
  against AF0's cached tokens: max |difference| 0.049 (mean |value| 0.41), correlation 0.99998 (bf16; not bit-equal).
- 19:08 `featpool.py` first version (memory map) made no progress; rewritten with `os.preadv`. DINOv3 means of af0_w1,
  af0_w2, ar1, bench_s, h1 taken from PD1's pooled files (same statistic); PN1's own pooling of af0_w1 equals PD1's
  file exactly (max difference 0.0).
- 19:13 Author's decision on the JPEG branch: amendment 1 (manifest C, JPEG reads) registered 19:20. 19:26 amendment 2
  (person frequency in the certificate). 19:28 container image for Athena; `run.sh` and job files use
  `apptainer exec --nv`. 19:48 account `plgmultivision-gpu-a100` (amendment 3, 19:52).
- 19:18 to 19:34 DGX DINOv3 for eq8_ar1 and ar1soft (897 s, 1.7 to 1.9 images/s); stopped after ar1soft; the other
  DINOv3 sets go to the Athena smoke job (`build_featx.py`). 19:34 to 19:35 CLIP devsoft (73 s).
- 19:23 `jpeg_c.py verify` failed on its own pin of AF0's `soften.py` (changed 19:14:54 by AF0: only a `--reverse` build
  option; the functions PN1 used are identical). `jpeg_c.py` now pins `prep_eval.py` directly. 19:30 CPU-only
  verification impossible (prep_eval's detector needs CUDA); 19:35 on the GPU: 4 of 4 FRLL jpeg70 evaluation files
  reproduced pixel for pixel and byte for byte (`jpeg_verify.json`, 31 s).
- 19:24 AF0's softened training list complete (1,084 fm61 + 1,085 amsl112 rows); `mkmanifests.py sources`.
- 19:29 AF0 extracted CLIP tokens of its softened list; pooled by PN1 (13 s).
- 19:33 to 19:35 27-statistic floors (`cues27.py`) for r2w4, ar1soft, devsoft, frll_e5.
- 19:35 to 19:44 DGX 8-image test of the Athena task script (`run.sh` with host Python, test pack, 3 steps, 8 scored
  rows): rc 0, 540 s, result tar written (`/mnt/t7/smad_next/PN1/dgxtest/`).
- 19:35 to 19:45 tier 0 on CLIP (both arms, 5 seeds); 19:42 AF0's ladder stored copies done (R4, R3 for 536 hosts, R3m
  for 200, both strengths; 12 of 12 sampled files equal AF0's sha256 list); AF0 extracted their CLIP tokens; tier 0 CLIP
  rerun with them at 19:50 to 19:53 (heads identical; ladder-copy reads added).
- 19:46 to 19:49 JPEG copies for manifest C (`jpeg_c.py build`, CPU, 2,549 copies; 8-image test first).
- 19:52 final manifests A, B, C and evaluation manifest; tier 0 report to the lead (CLIP).
- 19:53 full pack being written (`build_pack.py`); then the DINOv3 tar for Athena (`build_featx.py`).
- 19:58 Independent pre-run review in (`experiments/reviews/PRERUN_PN1_20261111.md`, GO WITH FIXES): the whole-manifest
  class balance made "stored at 61.2 px" a cue for "morph" in B (odds ratio about 2.3) and left a database cue in A
  (attack share 0.688 FRGC against 0.359 colorFERET). 20:00 the pack build was stopped before completion (PIDs 2430592,
  2435752). 20:05 lead's decisions registered as amendment 4 (the lead's "amendment 3"); first tier-0 tables moved to
  `tier0_v1_provisional*` (disclosed: read by owner and lead before the review). Code changed: `mkmanifests.py`
  (database x history strata, Bn draw), `tier0.py` (same strata, Bn0, partner-safe inner folds, 224-px floor),
  `reads.py` (τ_cam, τ_V, storage marks, partner-cycle bootstrap), `pn1lib.py` (cycle map, person folds), `cert.py`
  (random person folds with dropping; nuisance-only certificate), `run.sh` (arm Bn accepted), job files (eight fits,
  smoke on arm Bn), `tier1.py` written (reader with P-g bootstrap). 20:01 fixed manifests and pack build restarted
  (`chain_cpu4.sh`); 20:02 tier 0 recompute queued behind the certificate cues (`chain_cpu3.sh`).
- 20:12 Amendment 5: reference row "standard recipe on released SMDD" (eight A12-BR ViT-B/16 R retrains, last
  checkpoints; sha256 in `ref_smdd_m3_last_sha256.txt`), scored by `score_ref.sh` on Athena; tar `build_refnets.py`.
- 20:15 pack pinned (sha256 `5c642790…`, 10,159,360,000 bytes) in the registration and in the job files; 20:15 to
  20:23 upload of pack and DINOv3 tar (439 s), hashes checked on Athena; 20:23 smoke job 3545947 submitted
  (plgmultivision-gpu-a100); 20:24 reference tar uploaded and checked.
- 20:21 certificates and matched-subsample test computed (section 5.1b, 5.1c).
- 20:24 to 20:28 smoke job 3545947 (t0015, A100-SXM4-40GB): the pack copy and check passed (67 s), then `apptainer`
  failed: the job file set `PN1_ROOT` to the smoke folder and `run.sh` derives the image path from it
  ("could not open image /memfs/3545947/smoke/root/containers/..."); SMOKE_RC 255. The DINOv3 extraction part ran
  (eq64 and 6,421 images at about 110 images/s) and wrote `results/PN1/featx_out.tar`. Fix in the smoke job file only
  (`PN1_SIF` passed explicitly; DINOv3 part skipped when its output exists); `run.sh` unchanged. Resubmitted as
  3545968 at 20:37.
- 20:38 T7 drive full (8 KB free; a copy-back failed with "No space left on device"). PN1 deleted only its own
  intermediates (symlink trees, the 8-image test pack, the DINOv3 and reference tars already verified on Athena; hashes
  in `deleted_local_tars_sha256.txt`): 12 GB free. Lead told.
- 20:38 to 20:44 smoke job 3545968 (t0012): pack 30 s, 200 steps at 1.24 it/s (loss 0.689 -> 0.684), scoring 64 + 64
  rows, result tar written; SMOKE_RC 0, peak 30,833 MiB. Projection: 6,250 steps about 1.4 h, plus about 5 min of copy
  and scoring per fit (3 h limit kept).
- 20:45 GO conditions met (amendment 4 registered, smoke passed from the image): eight fits submitted as array
  3545976_[0-7] (`pn1_array.sbatch` sha256 `73168ec1…`), reference-row job 3545977 (`pn1_ref.sbatch` `8e4aa4dc…`,
  `score_ref.sh` `8968013d…`), both on plgmultivision-gpu-a100.
- 20:59 Slurm forecast (squeue --start): fits 12 Nov 16:56, reference job 13 Nov 12:01 (23 A100 nodes down, 13
  reserved; our user's other owners' jobs pending at similar priority). Time limits of my own pending jobs reduced
  with `scontrol update` (fits 3 h -> 2 h 15 min, reference 2 h -> 1 h) to match the smoke rate; forecast unchanged at
  21:00. `sbatch --test-only` forecasts for a new job: 16 Nov (plgmultivision) and 20 Dec (plgrestorearc). Lead told;
  decision on priority is the lead's.
- 21:06 Lead: keep waiting; a rented A100 may be arranged by the lead as fallback. Amendment 6 (one platform for all
  tier-1 networks) registered; runbook and scripts in `src/PN1/rented/` (RUNBOOK.md, drive.sh, pull_loop.sh,
  remote_setup.sh, remote_smoke.sh, remote_queue.sh, score_ref_local.sh = score_ref.sh with host Python and local
  paths only). `refnets.tar` rebuilt (byte-identical, sha256 `101da1e5…`). "Runbook ready" sent.
- 21:20 to 21:52 rented machines (lead): pn1a 173.183.191.220 (A100-SXM4 40 GB, 16 cores) seed-401 fits + reference row;
  pn1b 82.66.51.122 (A100-SXM4 80 GB, 128 cores) seed-402 fits; amendment 7 registered 21:21. Setup on both: pack and
  reference tar hashes OK, pinned packages (python 3.10.13, torch 2.2.1+cu121, timm 1.0.27, numpy 1.26.4, pillow
  10.2.0, safetensors 0.8.0, huggingface_hub 0.36.2, pyyaml 6.0.3). pn1a smoke (arm Bn, 200 steps): 1.53 it/s, peak
  30,835 MiB, rc 0. 21:46 Athena array 3545976 cancelled; Athena reference job 3545977 had completed (7 min 46 s) and is
  discarded (amendment 6). Queues: pn1a started 21:46, pn1b 21:49 (the first `drive.sh queue` call hung on the open
  ssh; pn1b started separately). Pull loops (`pull_loop.sh`) every 10 min into `/mnt/t7/smad_next/PN1/results_rented/`.
- 20:39 DINOv3 means from Athena installed (`postfeatx.py install`, files `ath_*.mean.npy`); tier 0 on DINOv3 started.
- Note: `lists.py cert_a` was rerun at about 19:58 after the ladder copies joined the catalogue, so `cert_a.csv` now
  lists more rows than the cue file `cert_cert_a.npz` (computed from the 11,573-row version); the ladder copies get
  their cues from the separate `ladsoft` cue job.

## 3. Data

Person split (`split/`): 536 ladder hosts; V (validation-reserved) 8 hosts and 67 AF0 persons, excluded everywhere;
test T 200 (191 read), development D 100, ladder training L 156 (130 FRGC, 26 colorFERET), of which 124 with a usable
morph; AF0 training persons kept 481, development 115.

Lists (`/mnt/t7/smad_next/PN1/lists/`): devsoft_src (226, `cb847cde…`), devsoft (452, `017c47fe…`), r2w4 (1,072,
`a5d98464…`), r2w4_td (600, `488fabc3…`), frll_e5 (1,020, `71b69756…`), frll_e5s (612, `7a601b26…`), ladsoft (2,544,
`f05da119…`; AF0's copies, ids equal AF0's ladsoft list), ar1h (248, `4b6572dd…`; SM1 halves of the training-host R4),
cert_a (11,573), cert_b (8,152), jpeg_sel (2,549, `2afced10…`), eq8_ar1 (8).

Images made by PN1: `/mnt/t7/smad_next/PN1/img/soft/{fm61,amsl112}/` (452 development copies);
`/mnt/t7/smad_next/PN1/img/jpeg/{jpeg90,jpeg70}/` (2,549 JPEG copies of manifest-B images, log `jpeg_build.csv`).

Training manifests (`/mnt/t7/smad_next/PN1/manifests/`; rows balanced by seeded repetition of the smaller class):

| Manifest | Unique negatives | Unique attacks | Rows | Draws per row in 6,250 x 256 | sha256 |
|---|---|---|---|---|---|
| A | 674 (AF0 photos 518, ladder R0 156) | 852 (AF0 u50 728, ladder R4 124) | 1,704 | 939 | `ffd8fb9b…` |
| B | 3,881 (A's + AF0 zero 730, AF0 halves 1,456, ladder R2w 156, ladder halves 248, photo_61 254, halfA_61 363) | 1,218 (A's + u50_61 366) | 7,762 | 206 | `b890f441…` |
| C | 5,821 (B's + 1,940 JPEG copies) | 1,827 (B's + 609 JPEG copies) | 11,642 | 137 | `a01840ef…` |

For comparison: the registered SMDD recipe draws each of its 40,000 rows about 40 times; PN1 has about 640 training
persons against SMDD's 25,000 synthetic identities.

Evaluation manifest `pn1_eval.csv` (23,640 rows, `44f049d1…`): test and development ladder (all rungs, both engines,
stored copies), AF0 validation images, the full FRLL-Morphs and corrected-MAD22 cells of the AD4 evaluation manifest
(files from the AD4 pack extraction, hash-checked there), FRLL benign variants, the Poisson set H1.

Features (`/mnt/t7/smad_next/PN1/feat/{clip224,dinov3_512}/`): `af0_<list>.mean.npy` (pooled from AF0 caches),
`<list>.mean.npy` (PN1 extraction). DINOv3 from PD1 pooled files for af0_w1, af0_w2, ar1, bench_s, h1.

Cues: `/mnt/t7/smad_next/PN1/cues/<list>.npz` (27-statistic floor), `cert_<list>.npz` (certificate cues at 224 and 512).

## 4. Code (`/home/narolski/smad-next/src/PN1/`; DGX Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`)

| Script | Job |
|---|---|
| `split.py` | person split (prereg section 2) |
| `soften_dev.py` | stored copies of development camera photos via AF0's `soften.py` (imported unchanged; sha256 `49fa4151…` at import) |
| `lists.py` | PN1 lists (r2w4, frll_e5, devsoft, ladsoft, ar1h, cert_a, cert_b) |
| `featmean.py` | mean patch-token features via AF0's `feat.py` (sha256 `4529c523…`, imported unchanged); several lists per model load |
| `featpool.py` | means from AF0 token caches (pread) |
| `cues27.py` | 27-statistic floor via AF0's `cues_all.one` (unchanged) |
| `cert_cues.py` | certificate cues through the AD4 pack's loader (`common.py` `b5d42a99…`) |
| `pn1lib.py` | catalogue (class, role, persons), features, heads, statistics |
| `reads.py` | pools, thresholds, reads (a) to (h), tier-0 marks |
| `tier0.py` | tier-0 heads (5 seeds) and reads |
| `cert.py` | certificate and matched-subsample test |
| `mkmanifests.py` | manifests A, B, C, JPEG selection, evaluation manifest, pack file list |
| `jpeg_c.py` | JPEG verification and copies (prep_eval `degrade`, pinned `374408ab…`) |
| `build_pack.py` | tier-1 pack (symlink tree, `tar -h`, SHA256SUMS) |
| `build_featx.py` | DINOv3 tar for the Athena smoke job |
| `pn1_score.py` | tier-1 scorer (ad4_score core; logit without flip, flip average stored) |
| `run.sh` | tier-1 task (unchanged train.py, AD4 M3 flags; container on Athena) |
| `athena/pn1_smoke.sbatch`, `athena/pn1_array.sbatch` | Athena jobs (account plgmultivision-gpu-a100) |
| `run_gpu1.sh`, `run_gpu2.sh`, `run_gpu3.sh`, `chain_cpu1.sh`, `chain_cpu2.sh` | DGX queues |
| `report.py` | key-read tables |
| `tier1.py` | tier-1 reader: reads, marks (P-a to P-g), paired bootstrap of the headline miss, memorisation gaps, reference row; tested on synthetic scores (`/mnt/t7/smad_next/PN1/tier1_synthetic_test/`) |
| `build_refnets.py`, `score_ref.sh`, `athena/pn1_ref.sbatch` | amendment 5 reference row (eight SMDD ViT-B/16 recipe retrains) |
| `postfeatx.py` | install the Athena DINOv3 means; 64-image platform check |
| `upload1.sh`, `upload2.sh`, `fetch.sh`, `watch_job.sh` | Athena transfers (locks), submission after upload, result copy-back with hash checks, job watcher |

Training call (tier 1): `train.py --arch a12_clip_vitb16_madation --regime d0 --split train90 --lofo none --lr 3.33e-06
--seed S --res 224 --workers 7 --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps=6250
--ft=lora --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw
--wd=0.05 --head-lr=3.33e-05 --bs=256 --aug=flip --sched=const --clip-grad=5 --pos-weight=1` (train.py `cbb2cbd1…`;
trainable parameters 74,241, as AD4). Seeds 401 (named) and 402. Athena image `smad_torch221_cu121_v1.sif`
(`fedeff10…`).

## 5. Results

### 5.1 Tier 0, CLIP ViT-L/14 224, recomputed under amendment 4 (current)

Full tables: `tier0_tables.md` (seed 401), `tier0_key.csv` (all seeds), JSON per head in `tier0/`. Heads trained on
the stratified-balanced rows (A0 1,736 rows of 1,246 images; B0 6,642 of 4,415; Bn0 1,482 of 1,246). Inner folds are
partner-safe and drop 40 to 72% of rows as straddling (AF0 pairs link persons densely); C chosen there. Test ladder 191
hosts; intervals over partner cycles. Floor for the excess: best of 39 statistics (27 at 512 px, 12 at 224 px).

| Read (seed 401) | A0 | B0 | Bn0 |
|---|---|---|---|
| R2w vs R4 (excess, best statistic band5@224 0.888) | 1.000 (+0.111 [0.076, 0.152]) | 0.998 (+0.110 [0.075, 0.151]) | 0.999 (+0.111 [0.076, 0.151]) |
| R2w4 vs R4 (excess) | 1.000 (+0.116) | 0.998 (+0.115) | 0.999 (+0.116) |
| R0_61 vs R4 / R2w_61 vs R4 | 0.999 / 0.999 | 0.998 / 0.998 | 0.999 / 0.999 |
| shift R0 -> R0_61 (SD) | +0.295 [0.254, 0.392] | +0.173 [0.127, 0.272] | +0.144 [0.099, 0.234] |
| shift R0 -> R0_112 (SD) | +0.147 [0.114, 0.211] | +0.084 [0.050, 0.141] | +0.037 [0.006, 0.091] |
| H1 AUC | 0.877 | 0.888 | 0.879 |
| MAD22 E7 EER OpenCV / Webmorph (%) | 4.90 / 6.20 | 4.41 / 4.90 | 3.92 / 6.80 |
| τ_0.5: genuine flags (max over pools) | 0.8% (H1) | 1.2% (H1) | 1.3% (H1) |
| τ_0.5: miss MAD22 OpenCV / Webmorph / H1 (%) | 53.3 / 68.2 / 67.4 | 54.2 / 66.0 / 58.5 | 57.7 / 73.4 / 63.9 |
| τ_cam: flag T_R0 / T_R0_61 / T_R0_112 (%) | 12.6 / 20.4 / 15.7 | 6.8 / 8.4 / 7.3 | 2.6 / 5.2 / 4.7 |
| τ_cam: flag FRLL jpeg50 / H1 genuine (%) | 3.9 / 11.0 | 2.0 / 11.5 | 0.0 / 6.7 |
| τ_cam: miss ladder R4 / MAD22 OpenCV / Webmorph / H1 (%) | 0.0 / 12.8 / 21.4 / 29.8 | 0.5 / 14.5 / 24.8 / 25.8 | 0.5 / 19.8 / 34.4 / 36.6 |
| τ_cam: family-mean miss (gating, %) | 16.0 | 16.4 | 22.8 |
| τ_cam: placed R3 / R3m (%) | 87.4 / 95.8 | 81.7 / 94.8 | 74.3 / 88.5 |
| P-c (61.2 px) / P-c2 (112.7 px) / unseen kernels | fail / fail / pass | pass / pass / pass | pass / pass / pass |
| K0; 2 x 2 | no; pass | no; pass | no; pass |

Seed spread: A0 seeds 402 to 404 chose C = 0.1 (401 and 405: C = 10): shift +0.311, τ_cam flag of T_R0_61 7.3%,
family-mean miss 20.4%; B0 identical over the five seeds (C = 0.1); Bn0 seed 405 chose C = 0.001 (shift +0.19).

Provisional first version (whole-manifest balance, host bootstrap, 512-px floor): `tier0_v1_provisional*`,
superseded (amendment 4).

DINOv3 ViT-L/16 512 (seed 401; A0 / B0 / Bn0). DINOv3 means of r2w4_td, frll_e5s, devsoft, AF0 soft and ladsoft were
extracted on Athena (smoke job 3545947, A100, container image); platform check on 64 images also present in the DGX
caches: feature max |difference| 0.0058 (mean |value| 0.113), correlation 0.999998, named B0 head probability max
|difference| 0.0038 (registered tolerance 0.01: within; `featx_platform_check.json`). FRLL jpeg90 / jpeg70 have no
DINOv3 means (not extracted).

| Read | A0 | B0 | Bn0 |
|---|---|---|---|
| R2w vs R4 / R2w4 vs R4 (excess +0.11 over band5@224 0.888) | 0.999 / 0.999 | 0.999 / 0.999 | 0.999 / 0.999 |
| R0_61 vs R4 / R2w_61 vs R4 | 0.999 / 0.999 | 0.999 / 0.999 | 0.998 / 0.998 |
| shift R0 -> R0_61 / R0_112 (SD) | +0.748 / +0.448 | +0.433 / +0.240 | +0.401 / +0.181 |
| H1 AUC | 0.850 | 0.842 | 0.839 |
| MAD22 E7 EER OpenCV / Webmorph (%) | 5.39 / 12.75 | 5.17 / 11.40 | 4.90 / 10.78 |
| τ_cam flag T_R0 / T_R0_61 / T_R0_112 (%) | 6.8 / 23.6 / 13.1 | 6.3 / 10.5 / 9.4 | 5.8 / 10.5 / 6.8 |
| τ_cam flag FRLL jpeg50 / H1 genuine (%) | 0.0 / 5.7 | 0.0 / 3.3 | 0.0 / 1.2 |
| τ_cam miss ladder R4 / MAD22 OpenCV / Webmorph / H1 (%) | 0.0 / 32.0 / 66.4 / 52.2 | 0.5 / 24.8 / 56.4 / 66.6 | 0.5 / 24.5 / 58.6 / 76.6 |
| τ_cam family-mean miss (%) | 37.6 | 37.1 | 40.1 |
| P-c / P-c2 / kernels | fail / fail / pass | fail (10.5%, 0.43 SD) / pass / pass | fail (10.5%, 0.40 SD) / pass / pass |
| K0; 2 x 2 | no; pass | no; pass | no; pass |

### 5.1b Certificate (amendment 4: random person folds, straddling images dropped; THE certificate = nuisance-only)

Files: `cert/cert_tier0.json`, `cert/cert_tier1.json`. AUC out of fold, larger of logistic and gradient-boosted trees
(interval over the first person of each image). Nuisance cues: history, engine, photo pool, border bin, person frequency.

| Set (rows as trained) | Nuisance-only certificate | With softness and pixel cues | Pixel cues only (224 px) | Share dropped |
|---|---|---|---|---|
| manifest A (1,992) | 1.000 | 1.000 | 0.972 | 0.40 |
| manifest B (7,762) | 0.841 [0.818, 0.862] | 0.969 | 0.932 | 0.68 |
| manifest Bn (1,758) | 0.834 [0.789, 0.879] | 0.965 | 0.922 | 0.70 |
| manifest C (11,642) | 0.841 [0.817, 0.864] | 0.962 | 0.928 | 0.68 |
| tier-0 A0 / B0 / Bn0 | 1.000 / 0.851 / 0.858 | 1.000 / 0.976 / 0.951 | 0.975 / 0.946 / 0.878 | 0.41 / 0.72 / 0.71 |

In A the engine cue (every attack went through the morphing tool, no negative did) separates the classes completely; in
B, Bn and C the remaining nuisance signal is mainly that camera photos (no tool) are always negatives. Evaluation cells
(within-cell folds): test ladder R4 vs R2w / R2w4 nuisance 0.66, pixel 0.93; R4 vs R3 0.63 / 0.67; R4 vs R0 or vs any
61.2 px negative 1.00 (engine or history); H1 1.00 / 0.84; every MAD22 and FRLL-Morphs cell 1.00 / 0.98 to 1.00 (the audit
line, not a property of the method).

### 5.1c Matched-subsample test (CLIP, pool = B0's 4,415 unique images; `cert/cert_tier0.json`)

| | Full pool | Matched (exact strata of history, engine, pool, border) | Random, same class counts |
|---|---|---|---|
| images | 4,415 | 2,140 (48.5% kept; every camera photo dropped: no attack has engine "none") | 2,140 |
| nuisance-cue AUC | 0.868 | 0.466 | 0.886 |
| full-cue AUC | 0.982 | 0.925 | 0.963 |
| flag at 5% camera-photo threshold: T_R0 / T_R0_61 / T_R0_112 | 5.2 / 9.9 / 7.9% | 4.7 / 9.4 / 8.4% | 7.3 / 16.2 / 11.0% |
| change R0 -> R0_61 / R0_112 (points) | +4.7 / +2.6 | +4.7 / +3.7 | +8.9 / +3.7 |
| R4 vs R3 AUC; R4 vs R0 EER | 0.864; 1.57% | 0.860; 2.09% | 0.862; 1.57% |

Registered kill rules: k1 (cannot reach 0.60 with 30% kept) not met; k2 (matched not below random by half the full-pool
change: 8.9 − 4.7 = 4.2 ≥ 2.35) not met; k3 (EER worse by > 2 points: +0.52) not met.

### 5.1d Spliced-positive heads (amendment 8; `splice/`, `src/PN1/splice.py`, `splice_lists.py`, `splice_ratio.py`)

Seed 401, test hosts, OpenCV-style engine; A0 / B0 / S-a / S-b. Note: the face-only S0 copy is byte-identical to the
face-only R2w copy (AR1 prereg line 197), so "S0 vs S4 face-only" and "R2w vs R4 face-only" are the same contrast.

| Read | CLIP | DINOv3 |
|---|---|---|
| face-only S0 vs S4 (best baseline 0.906) | 0.746 / 0.734 / 0.830 / 0.798 | 0.759 / 0.778 / 0.851 / 0.848 |
| face-blanked R2w vs R4 (baseline 0.778) | 0.994 / 0.995 / 0.759 / 0.939 | 0.996 / 0.995 / 0.884 / 0.999 |
| native S0 vs S4 (baseline incl. sharpness ratio 0.843) | 0.862 / 0.868 / 0.946 / 0.930 | 0.837 / 0.828 / 0.975 / 0.964 |
| MAD22 E7 EER OpenCV / Webmorph, S-a; S-b | 23.7 / 24.0; 9.8 / 11.3 | 13.8 / 13.2; 2.0 / 3.0 |
| H1 AUC S-a; S-b | 0.821; 0.843 | 0.775; 0.854 |
| shift to 61 px (SD) S-a; S-b | 0.20; 0.10 | 0.36; 0.28 |
| τ_cam gating miss S-a; S-b | 56%; 39% | 25%; 7.8% |

Face-blanked S0 vs S4 is 0.500 (identical images). GPU: CLIP 48 s, DINOv3 182 s (DGX idle at 22:35).

### 5.1e Bracketing test, DiffAE transfer, splice seed spread (amendment 9; `bracket/bracket.json`, `src/PN1/bracket.py`)

Bracketing (share of 191 test hosts with R4 above both R2w and R2w_61; A0 / B0 / Bn0 / S-a / S-b): CLIP 1.000 / 1.000 /
1.000 / 0.958 / 1.000; DINOv3 1.000 / 1.000 / 1.000 / 0.979 / 1.000; best statistic lap_k5@224 0.911 (chosen on the
test hosts). DiffAE set B (256 px; `featmean_any.py`), AUC X vs REC / G / SAME / MIR: CLIP A0 0.657/0.907/0.609/0.339,
B0 0.675/0.924/0.618/0.315, Bn0 0.645/0.897/0.587/0.385, S-a 0.468/0.730/0.695/0.466, S-b 0.561/0.730/0.738/0.552;
DINOv3 A0 0.789/0.939/0.602/0.379, B0 0.790/0.947/0.617/0.374, Bn0 0.791/0.960/0.653/0.409, S-a 0.302/0.627/0.730/0.313,
S-b 0.671/0.863/0.787/0.416; floors 0.650 / 0.868 / 0.693 / 0.624. Splice arms over seeds 401-405: S-a S0 vs S4 CLIP
0.944-0.948, DINOv3 0.975; face-only 0.825-0.832 / 0.844-0.851; S-b face-only 0.798-0.810 / 0.848-0.859.

### 5.1f Post hoc items, face-only heads, face-blanked benchmark reads (amendment 11; `posthoc2/posthoc2.json`)

POST HOC (no pass marks). Seed 401; A0 / B0 / Bn0 / S-a / S-b / F (face-only-trained). FaceMorpher spliced reads are not
used ("seam not matched"); every splice read here is OpenCV-style.
- 3-statistic floor (seam tone luma and R-G, sharpness ratio, band5@224; fitted on 100 development hosts): dev 0.901,
  test 0.856. Excess of native S0 vs S4 over it, CLIP: +0.004 / +0.010 / -0.034 / +0.088 [0.051, 0.127] / +0.072
  [0.033, 0.111] / -0.127; DINOv3: -0.021 / -0.030 / -0.044 / +0.117 [0.082, 0.153] / +0.106 [0.070, 0.144] / -0.216.
- Face-only S0 vs S4: CLIP 0.746 / 0.734 / 0.743 / 0.830 / 0.798 / 0.950 (F: excess over band5@224 +0.044, lower bound
  +0.017); DINOv3 0.759 / 0.778 / 0.791 / 0.851 / 0.848 / 0.992 (F: +0.086, lower bound +0.059). F face-blanked R2w vs
  R4: 0.513 / 0.685; F transfer: MAD22 E7 EER 36.3 / 33.3% (OpenCV), H1 0.562 / 0.533.
- Brackets: (c) margin over the host's own R0 -> R0_61 shift, CLIP 0.995 / 1.000 / 1.000 / 0.932 / 1.000 / 0.691;
  (d) fixed τ_cam, CLIP 0.764 / 0.901 / 0.948 / 0.581 / 0.864 / 0.052, DINOv3 0.728 / 0.869 / 0.848 / 0.686 / 0.869 /
  0.157; (a) face-only S4 above S0, CLIP 0.843 / 0.806 / 0.806 / 0.958 / 0.874 / 0.984.
- Face-blanked benchmark copies (canonical hull): MAD22 E7 EER OpenCV native -> blanked, DINOv3 S-b 1.96 -> 1.96%,
  Webmorph 3.0 -> 7.4%; CLIP B0 4.4 -> 4.4%, 4.9 -> 7.4%; H1 AUC falls to 0.55-0.66 for every head.
- Training-person resampling (10 draws; min / median / max): DINOv3 S-b MAD22 OpenCV E7 EER 1.0 / 2.75 / 8.8%,
  Webmorph 2.8 / 5.0 / 10.8%, τ_cam gating miss 11.6 / 17.9 / 31.0%; DINOv3 B0 5.2 / 5.9 / 7.5%, 11.4 / 13.0 / 13.8%,
  39 / 43 / 48%; CLIP B0 4.4 / 5.9 / 6.8%, 4.4 / 6.4 / 8.2%, 8.3 / 18.1 / 20.2%.

### 5.2 Tier 1

Read as registered on 12 Nov about 03:00 (`tier1.py --results /mnt/t7/smad_next/PN1/results_rented`); full tables in
`result.md` (section "Tier 1"), JSON per network in `tier1/`, comparisons and the reference row in `tier1/compare.json`.
Result tars and logs: `/mnt/t7/smad_next/PN1/results_rented/` (sha256 checked by the pull loops). Registered reading of
every arm: "inconclusive, no claim" (P-c, P-c2, P-d fail; P-g non-inferior only for C 402).

## 6. Checks

- `split.py`: `prep_train.is_val` equals the local copy for all hosts; partner map is a permutation; T equals the AF0
  softened-host list; AF0 and ladder persons disjoint.
- Feature equivalence: DGX CLIP re-extraction vs AF0 tokens on 8 images (max 0.049, r 0.99998); PN1-pooled vs PD1
  DINOv3 means identical.
- JPEG call: 4 of 4 jpeg70 evaluation files reproduced byte for byte.
- DGX 8-image test of `run.sh` (3 steps): rc 0; trainable parameters 74,241; result tar holds scores, `last_trainable.pt`,
  meta, logs.
- AF0 ladder copies: 12 of 12 sampled files equal AF0's sha256 list.
- Not verified: platform equality of DINOv3 between GB10 and A100 (64-image check planned in the smoke job); the
  Athena container path for this pack (smoke job).

## 7. Dead ends and failures

- A random development draw would have left 88 (strictly 48) ladder training hosts with a usable morph; replaced by the
  registered partner rule before any score.
- 19:08 to 19:32: the first restart of `featpool.py` stopped the wrong process (`pgrep -f ... | head -1` returned the
  wrapper shell); the second pooling process (PID 2345152) kept running, so for about 20 minutes three PN1 CPU
  processes ran (one more than allowed); DINOv3 means of af0_w1 and af0_w2 were written twice (identical content).
  Stopped by PID. Rule: stop only by the Python PID read from `ps`.
- 19:30 JPEG verification on the CPU impossible (prep_eval's detector requires CUDA); the first GPU attempt hit a
  transient CUDA out-of-memory error; moved into the PN1 GPU queue.
- DINOv3 on the shared GB10 at 1.7 to 1.9 images/s; stopped after ar1soft; remaining sets to Athena.
- 19:45 a wait loop `until ! pgrep -f "tier0.py ..."` matched its own command line and never ended; stopped.
- DGX GPU use: 676 + 897 + 73 + 31 + 540 s = 37 minutes of one shared process, over the 30-minute allowance.

## 8. Observations and ideas

- Review F11 count: 149 ordered AF0 pairs (84 in the training split, before the V exclusion) have both a zero image
  and a u50 morph; in all 149 the zero file is byte-identical to that morph's halfA (`zero_halfA_duplicates.json`).
  So up to 84 training negatives of B, Bn and C appear twice (as "zero" and as "half"). Manifests not changed (pack
  pinned); stated here.

- AF0 includes 67 validation-reserved persons (49 in its training split).
- AF0's alternating softened list put every halfA copy at 61.2 px and every halfB copy at 112.7 px (pair index and row
  parity coincide), so the 61.2 px halves in B and C are host-side halves only.
- At the own 0.5 rule both frozen heads flag no genuine image and miss 44 to 80% of MAD22 and Poisson morphs: the
  operating point sits far on the genuine side (descriptive).

## 9. Open items and next steps

DINOv3 tier 0 (Athena smoke job); certificate and matched-subsample test (cues); pack upload; smoke job; lead's GO;
six fits; tier-1 reads; result.md; results review by the lead.

## 10. Handover state (12 Nov 03:05)

- Rented pn1a (173.183.191.220:24545, lease folder `/mnt/t7/smad_next/vast/pn1a`): first queue done (4 fits + reference
  row verified); second queue PN1_Sb_s401, PN1_Bv_s401 running (pack 2), expected end about 04:55. pn1b
  (82.66.51.122:53776, `/mnt/t7/smad_next/vast/pn1b`): first queue done; second queue PN1_Sb_s402, PN1_Bv_s402, expected
  end about 06:20. Pull loops (`pull_loop.sh`) write RELEASE per lease folder when 7 / 6 tars are verified.
- After those: read amendment 10 with `tier1.py` extended to arms Sb and Bv (development ladder first).

## 10b. Handover state (20:47, superseded)

- Athena: array 3545976_[0-7] (PN1_A_s401, PN1_B_s401, PN1_Bn_s401, PN1_C_s401, then the s402 four), each about 1.5 h
  (1.24 it/s; time limit 2 h 15 min since 20:59), logs `/net/pr2/projects/plgrid/plggrestoration/smad-next/results/PN1/logs/fit-3545976_<i>.out`, result
  tars `.../results/PN1/PN1_<arm>_s<seed>.tar` (+ .sha256). Reference job 3545977 (log `ref-3545977.out`, tar
  `PN1_REF_smdd_m3.tar`). Both pending at 20:46 (priority).
- DGX: `watch_fits.sh` (log `/mnt/t7/smad_next/PN1/watch_fits.log`) polls sacct (one ssh per check) and runs
  `fetch.sh` (copy-back with sha256 checks to `/mnt/t7/smad_next/PN1/results/`) whenever a task has ended.
- After all tasks end: `tier1.py` (reads, marks, P-g bootstrap, gaps, reference row) and `report.py tier1`; then
  `result.md`.
- If a fit fails on infrastructure: rerun that array index once unchanged (`sbatch --array=<i> tasks/PN1/pn1_array.sbatch`);
  never rerun a run with non-finite loss or weights (amendment 4 item 7).
- Compute: Athena 0.16 GPU-hours (two smoke jobs); projected 8 x 1.6 + 0.5 = about 13 GPU-hours.

## 10a. Handover state (19:55, superseded)

- DGX `chain_cpu1.sh` (certificate cues cert_a, cert_b, devsoft; log `/mnt/t7/smad_next/PN1/chain_cpu1.log`).
- DGX `chain_cpu2.sh` (pack, then DINOv3 tar; log `/mnt/t7/smad_next/PN1/chain_cpu2.log`).
- Athena: task folders and job files uploaded to `/net/pr2/projects/plgrid/plggrestoration/smad-next/tasks/PN1/`
  (`run.sh` sha256 `3db27192…`, same file as the DGX test). No job submitted yet.
- If a chain dies: rerun its script (finished outputs are skipped).

## 11. Reproduce from scratch

```
cd /home/narolski/smad-next/src/PN1; P="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
$P split.py
$P soften_dev.py list; $P soften_dev.py build --limit 4; $P soften_dev.py build
$P lists.py r2w4; $P lists.py frll_e5; $P lists.py devsoft; $P lists.py ladsoft; $P lists.py ar1h; $P lists.py cert_a; $P lists.py cert_b
# r2w4_td = r2w4 rows of test/dev hosts; frll_e5s = frll_e5 rows jpeg50/blur1/resample50 (inline step of 19:01)
bash run_gpu1.sh; bash run_gpu2.sh; bash run_gpu3.sh          # CLIP/DINOv3 means, JPEG verify, DGX run.sh test
$P featpool.py clip224:af0_w1 clip224:af0_w2 clip224:af0_h clip224:ar1 clip224:ar1soft clip224:bench_s clip224:h1 \
   clip224:soft clip224:ladsoft dinov3_512:af0_w1 dinov3_512:af0_h
$P cues27.py r2w4=... ar1soft=... devsoft=... frll_e5=...; $P cert_cues.py cert_a=... cert_b=... devsoft=...
$P tier0.py --backbones clip224; $P report.py tier0
$P mkmanifests.py sources; $P jpeg_c.py verify; $P jpeg_c.py build; $P mkmanifests.py final
$P build_pack.py; $P build_featx.py r2w4_td=... frll_e5s=... devsoft=... soft=... ladsoft=...; $P build_refnets.py
bash upload1.sh; bash upload2.sh        # pack, DINOv3 tar, tasks; smoke submission; reference tar
# Athena (command lock): sbatch tasks/PN1/pn1_array.sbatch; sbatch tasks/PN1/pn1_ref.sbatch
bash fetch.sh; $P postfeatx.py install; $P tier0.py --backbones dinov3_512; $P postfeatx.py check; $P cert.py tier0
$P tier1.py; $P report.py tier1
```
