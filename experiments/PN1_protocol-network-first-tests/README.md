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

Training call (tier 1): `train.py --arch a12_clip_vitb16_madation --regime d0 --split train90 --lofo none --lr 3.33e-06
--seed S --res 224 --workers 7 --recipe=v1 --label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps=6250
--ft=lora --lora-targets=qv --lora-r=2 --lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw
--wd=0.05 --head-lr=3.33e-05 --bs=256 --aug=flip --sched=const --clip-grad=5 --pos-weight=1` (train.py `cbb2cbd1…`;
trainable parameters 74,241, as AD4). Seeds 401 (named) and 402. Athena image `smad_torch221_cu121_v1.sif`
(`fedeff10…`).

## 5. Results

### 5.1 Tier 0, CLIP ViT-L/14 224 (frozen mean tokens, logistic heads)

Full tables: `tier0_tables.md` (seed 401), `tier0_key.csv` (all seeds), JSON per head in `tier0/`. Training rows:
A0 1,246 (518 photos, 728 u50), B0 4,415 (photos 518, zero 730, halves 1,456, photo_61 254, halfA_61 363, u50 728,
u50_61 366). Test ladder 191 hosts.

| Read (seed 401) | A0 | B0 |
|---|---|---|
| R2w vs R4, OpenCV | 0.999 [0.998, 1.000] | 0.999 [0.997, 1.000] |
| excess over best of 27 statistics (band b3, 0.876) | +0.123 [+0.090, +0.154] | +0.123 [+0.090, +0.154] |
| R2w4 vs R4, OpenCV (excess) | 0.999 (+0.125 [0.091, 0.156]) | 0.999 (+0.124 [0.091, 0.156]) |
| R0_61 vs R4 / R2w_61 vs R4 | 0.998 / 0.999 | 0.998 / 0.998 |
| 2 x 2: R2w vs R4_61; R2w_112 vs R4_112; R2w_61 vs R4_61 | 1.000; 1.000; 0.999 | 0.999; 0.999; 0.999 |
| shift R0 -> R0_61 (SD of R0 logits) | +0.222 [0.175, 0.267] | +0.182 [0.127, 0.243] |
| shift R0 -> R0_112 | +0.071 [0.031, 0.110] | +0.097 [0.048, 0.148] |
| H1 AUC | 0.862 [0.841, 0.882] | 0.893 [0.873, 0.911] |
| MAD22 OpenCV EER native / E7 (%) | 4.41 / 4.90 | 5.39 / 5.39 |
| MAD22 Webmorph EER native / E7 (%) | 6.00 / 6.00 | 5.39 / 5.39 |
| R4 vs R3, OpenCV | 0.853 | 0.865 |
| τ_0.5: flag on every genuine pool | 0% | 0% |
| τ_0.5: miss ladder R4 / R4_61 / MAD22 OpenCV / Webmorph / H1 (%) | 4.2 / 5.2 / 47.0 / 65.8 / 79.8 | 5.8 / 4.7 / 43.5 / 55.4 / 48.7 |
| τ_dev binding pool | development R0_61 | development R0_112 |
| τ_dev: flag T_R0 / T_R0_61 / T_R0_112 / FRLL jpeg50 (%) | 6.3 / 9.9 / 7.9 / 3.4 | 3.7 / 5.8 / 4.7 / 2.0 |
| τ_dev: miss ladder R4 / R4_61 / MAD22 OpenCV / Webmorph / H1 (%) | 0.5 / 0.0 / 15.8 / 28.0 / 52.2 | 0.5 / 0.5 / 18.0 / 22.4 / 24.9 |
| τ_dev: family-mean miss over gating cells (%) | 24.1 | 16.5 |
| τ_dev: placed R3 / R3m (%) | 78.0 / 90.1 | 74.9 / 93.7 |
| marks: K0; 2 x 2; NU-a; NU-d | not triggered; pass; none > 10%; 5.2/0.0% | not triggered; pass; H1 genuine 11.2% at τ_dev; 4.7/0.5% |

Seeds 402 to 405: AUCs within 0.001 of seed 401; A0 shift 0.22 to 0.26; B0 seed 402 chose C = 10 (others C = 1) and
gives shift +0.036, H1 0.904, family-mean miss 10.4%.

DINOv3, the certificate and the matched-subsample test: pending.

### 5.2 Tier 1

Not run.

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

- AF0 includes 67 validation-reserved persons (49 in its training split).
- AF0's alternating softened list put every halfA copy at 61.2 px and every halfB copy at 112.7 px (pair index and row
  parity coincide), so the 61.2 px halves in B and C are host-side halves only.
- At the own 0.5 rule both frozen heads flag no genuine image and miss 44 to 80% of MAD22 and Poisson morphs: the
  operating point sits far on the genuine side (descriptive).

## 9. Open items and next steps

DINOv3 tier 0 (Athena smoke job); certificate and matched-subsample test (cues); pack upload; smoke job; lead's GO;
six fits; tier-1 reads; result.md; results review by the lead.

## 10. Handover state (19:55)

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
$P build_pack.py; $P build_featx.py r2w4_td=... frll_e5s=... devsoft=... soft=... ladsoft=...
```
