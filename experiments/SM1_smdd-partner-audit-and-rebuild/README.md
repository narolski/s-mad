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
features learns (Part 3), and the same with LoRA fits on Athena. **Status 11 Nov 20:10:** Part 1, T-A, T-B, T-C,
the Laplacian acceptance and the frozen-head Part 3 (12 arms x 5 seeds) are done (`result.md`). Running: Part 2
scoring on the DGX, arm (f) frozen heads and JPEG reads, 25 ViT-L/14 and 10 ViT-B/16 LoRA fits on Athena. Plain
summary so far: the release differs from the natural reading of the paper (five partners per split); on the
release's own training split the ViT-B/16 release misses no more evaluation-split morphs than training morphs (within
1 point), the other four primary releases miss 4 to 9.5 points more; three of five releases rank the five training
partner renders higher than other renders more often than chance; on frozen CLIP heads, replacing the five partners
by 50 or more partners lowers the landmark-cell EER by about 3 points, and adding halves and history copies lowers
the rise under history matching; no rebuilt arm passes the sharpness acceptance, so all Part 3 numbers are
descriptive.

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
- 18:05 pack a (audit 9,520 pairs + AR1 halves 536 pairs, 0.49 GB, sha256 f48f125a…) built and sent to leaseB
  (upload 591 s; the upload direction to leaseB is slow, about 0.8 MB/s at that time).
- 18:08 DGX smoke builds of (c) and (c′) (1,500 + 500 files) are pixel-identical to the leaseB files (max 0); the
  leaseB set installed at `/mnt/t7/smad_next/SM1/img/{armc,armcr}`.
- 18:10 to 18:30 arm (e) shrink step on the DGX (`shrink.py run`, 1 worker): 45,000 files (14,734+ (c) morphs and
  their halves; the 15,000-row list) written to `img/arme` at 80 px.
- 18:18 amendment A8: the T-A / T-B DGX pass scores a stratified subsample (`flists/tab_sub.csv`, 7,810 images)
  because the shared GPU is saturated (1,600 images per 285 s for three small releases). Running as
  `run_tab_multi.sh` (log `logs_tab_sub.log`), five primary releases in one process, then the FS pair.
- 18:20 contributor landmarks finished (3,858 renders, 2,672 s, all faces). All lists written (`pairs_all.log`):
  N = 14,734 release pairs with both contributors admissible (266 dropped by the A5 rule); (a) 256 x 256 subset
  14,236; (b′) 2,433 replacement partners, cap 7; dose K = 50 (each partner at most 295 times), K = 500 (at most
  30); (c) look-alike rank median 0, max 10.
- 18:22 geometry expression check (`expr_geom.json`): FRLL 5-fold accuracy 0.79 to 0.95; smile rate of the SMDD
  genuine renders 0.78, of the release morphs' mean shapes 0.97, of the contributor renders 0.85; trained
  partners' smile probabilities 0.77 to 1.00. The probe is trained on FRLL photos (domain shift), so absolute
  rates are uncertain; descriptive only.
- 18:24 GPU feature pack: `sm1gpu_code.tar` (sha256 6dde0451…, 1.74 GB: feats_gpu.py, common.py, a12_released.py,
  the cached OpenAI ViT-L/14 weights, 19 lists) and image tars `sm1gpu_img_{test,base,armsc,audit,arme,armsb}.tar`.
  `feats_gpu.py` reproduces `feats.py` on the DGX to 1.2e-7 on 8 images. AR1 manifest grew to 19,515 rows (new
  rung R2wm) after my first list; snapshot `ar1_manifest_snapshot_9c69d44f.csv`.
- 18:26 leaseB task a done (9,520 audit morphs + 536 AR1 morphs + 1,072 halves, 0 failures); installed at
  `img/{audit,ar1h}`. Our 536 AR1 morphs equal AR1's own OpenCV R4 files pixel for pixel (`ar1h_vs_ar1_r4.json`).
- 18:28 pack b (arms b, b′, K = 50, K = 500: 58,936 pairs) built and being sent to leaseB.
- 18:30 Lead: Athena accepts jobs (account plgrestorearc-gpu-a100); the feature pass and the LoRA fits run there.
  Code tar uploaded to Athena `packs/SM1/` in 153 s (11 MB/s); image tars follow one per connection.
- 18:33 The AR1 crop script changed under me (AR1 owner added MTCNN batching; `--boxes-out` removed): a frozen
  copy is now used, `src/SM1/ar1copy/{crop_rgb.py (sha256 07b179bd…), ar1_common.py (42806acb…)}`. Its header
  documents the deviation: same-size images batched by 16, boxes within 0.04 px of one-by-one detection.
- 18:35 `compose.py` writes the arm compositions (`/mnt/t7/smad_next/SM1/compose/<arm>_s<seed>.json`, full and
  smoke) used by both the frozen heads and the LoRA fits; `heads.py` rewritten to read them and the Athena
  features (first version kept as `heads_v1_unused.py`, never run).
- 18:38 leaseB task b 8-pair check passed (78 CLI vs wrapper 0; leaseB vs DGX references 0 over 32 files); full
  task b started (96 workers).
- 18:40 Audit MTCNN crops restarted as 3 shards (`run_crops.sh`; one process ran at 1.3 images/s).
- 18:42 Athena facts from the lead (ATHENA.md updated): `-C localfs` gives only 4 GB of `$SCRATCH_LOCAL`; jobs use
  `-C memfs` and `$MEMFS` (RAM disk, counts toward `--mem`, at most 120G per GPU for one-GPU billing). Two locks:
  short commands `/tmp/smadnext-athena-cmd.lock`, transfers `/tmp/smadnext-athena.lock` with `-w 1800` (a flock
  timeout returns 1 silently; it is a local wait, not a refused login). `athena_feats.sbatch` and `athena_up.sh`
  changed accordingly.
- 18:44 GPU image tars done: test 8.90 GB (sha256 59cb6455…), base 5.52 GB (5c79a7b8…), armsc 6.63 GB (3df23935…),
  audit 1.52 GB (344a6c32…), arme 0.62 GB (aeb57d6b…); armsb follows the leaseB task b.
- 18:44 Amendment A9 registered (LoRA fits on Athena, arms a, c, d, e x seeds 401 to 405, record's M3L command,
  AD4 scorer on AD4's evaluation manifest and the AR1 manifest). Prepared: `lora_lists.py` → 20 training manifests
  (`/mnt/t7/smad_next/SM1/lora/manifests/train_sm1<arm>_s<seed>.csv`, 39,734 rows each; d and e drawn per seed) and
  `sm1_ar1_eval.csv` (20,587 rows); `sm1lora_manifests.tar` (74.7 MB); `lora_run.sh` (task script modelled on AD4's
  run.sh; images from the GPU tars already on Athena, so no second image upload) and `athena_lora.sbatch` (array
  0..19, memfs, 120G, 12 h). Not run on the DGX first: the job needs the 11 GB AD4 pack plus 23 GB of SM1 tars in a
  RAM disk and the DGX CPU is saturated; the Athena smoke (3 steps, 8 images scored) is the 8-image test.
- 18:45 leaseB task b done: 4 x 14,734 morphs (b, b′, K = 50, K = 500), 0 engine failures, wrapper = 78 CLI and
  leaseB = DGX references (0); tar fetched (432 s, sha256 OK) and installed in `img/{armb,armbp,armd50,armd500}`.
- 18:45 Athena feature smoke job 3544208 (1 A100, `athena_feats.sbatch` MODE=smoke): environment Python 3.10.4,
  torch 2.2.1+cu121, timm 1.0.27, numpy 1.26.4, pillow 10.2.0, QuickGELU tower confirmed; 3 x 400 test images at
  107 to 149 images/s; result tar sha256 OK. Equivalence with the DGX features on the 400 common FRLL rows: max
  |Δ feature| 4.9e-4, max |Δ FE-header logit| 0.022 (`feat_equivalence.json`); the 400 rows are all morphs, so the
  AUC difference is computed on the full test set after the production job.
- 18:53 Uploads to Athena done: test (922 s), base (588 s), arme (539 s), armsc (189 s), audit (45 s);
  armsb and the LoRA manifests queued.
- 18:59 Athena LoRA smoke job 3544789 (array index 0 = arm a seed 401, 3 steps, 8 images scored): 39,734 training
  items (14,734 morphs, 25,000 genuine, pos_weight 1, regime d0 kept every row), wall 148 s, result tar sha256 OK.
  (A mistake on my side: I ran `sha256sum -c` over the pack tars on the Athena login node, against the rule that
  nothing is computed there; not repeated.)
- 19:08 armsb tar (6.46 GB, sha256 1d028856…) uploaded in 181 s. Full feature job 3545820 submitted (MODE=full,
  all 7 tars, all 19 lists; running on t0013 at 19:09).
- 19:09 LoRA production array 3545823_[0-19] submitted (arms a, c, d, e x seeds 401 to 405; 12 h limit each;
  estimate 3 to 5 A100-hours per fit, under 100 in total).
- 19:13 Author's decision (via the lead): the JPEG branch of `prep_eval.degrade` (jpeg90, jpeg70, jpeg50) may run
  unchanged on training images; class categories in force. → amendment A10 (arm f; JPEG reads for all arms).
- 19:15 T-A / T-B primary five releases scored (7,810 images x 5, 3,755 s); read (`tab_sub.json`); FS pair running.
- 19:20 `prep_eval.align(prep_eval.degrade(img, "jpeg70"))` reproduces the existing evaluation files
  `001_03_jpeg70.png` and `002_03_jpeg70.png` byte for byte (`jpeg_verify.json`). JPEG assignment: 46,330 images
  (23,241 jpeg90, 23,089 jpeg70) over every image that can enter arm (e) (`lists/jpeg_assign.csv`); DGX build with
  one worker running (`jpeg_arm.py build`, log `logs_jpeg_build.log`, outputs `img/armf/{jpeg90,jpeg70}/`).
- 19:24 Athena feature job 3545820 done (all lists, about 340 images/s, ~16 min); fetched, sha256 OK, merged into
  `/mnt/t7/smad_next/SM1/feat_athena/`. Equivalence on all 14,120 FRLL frames: max |Δ feature| 1.0e-3, FE-header AUC
  0.88252 vs 0.88253. Pool-cue AUC 0.507. Smoke heads and reader done (`p3_smoke.json`), numbers in `result.md`.
- 19:30 LoRA task script updated on Athena before any production task started: arm (f) inputs
  (`sm1gpu_img_armf.tar`, to come), FRLL JPEG frames (`sm1gpu_img_jpegeval.tar`, 612 files, sha256 ea7f7477…) scored
  as a third manifest, manifests `sm1lora_manifests_v2.tar` (sha256 5b1c41c1…; the a/c/d/e manifests are identical
  to version 1, checked). The pending array picks up the new script when its tasks start.
- 19:32 Laplacian acceptance (`lapvar.json`): no rebuilt arm accepted (best: arm e, 0.716 at the loader size);
  release arm 0.993; morph vs own halves 0.881 (variance ratio 0.52).
- 19:44 The lead, with the author's approval, moved the pending LoRA array 3545823_[0-19] from account
  plgrestorearc-gpu-a100 to plgmultivision-gpu-a100 (`scontrol update`; priority about 5,200 → 11,585; Athena has
  only 12 working nodes tonight). Same job files and software. Arm (f) fits are submitted with
  `-A plgmultivision-gpu-a100` too.
- 19:45 Audit MTCNN crops done (3 shards; 10,055 of 10,055 retained). Part 2 scoring queued after the T-A / T-B FS
  pair (`run_p2.sh`, log `logs_p2.log`).
- 19:45 JPEG build done: 46,330 copies in 1,029 s (`logs/jpeg_build.json`). Arm (f) image tar (sha256 in
  `gpupack/sm1gpu_img_armf.tar.sha256`) and code tar v2 (lists `test_eval_jpeg`, `train_armf_jpeg`) uploaded (87 s,
  52 s). Laplacian check of arm (f): the first run crashed on a variable-name bug in `lapvar.py` (loop variable `n`
  shadowed the sample size), fixed and rerun.
- 19:48 Submitted: Athena feature job 3545893 (MODE=f: JPEG frames + arm f copies; account plgrestorearc) and the
  arm (f) LoRA fits 3545894_[20-24] (`-A plgmultivision-gpu-a100`).
- 19:50 Full frozen-head run done (12 arms x 5 seeds + FE reference; `p3_full.json`); numbers in `result.md`.
  `heads.py` gained `--rescore` (recompute saved heads on an extended test bank, for the JPEG frames).
- 19:55 T-A / T-B FS pair scored (7,810 x 2, 1,589 s); `tab_sub.json` rewritten with all seven releases. Part 2
  scoring started (`run_p2.sh`). LoRA tasks 3545823_0 and _1 running on t0016 (arm a, seeds 401, 402).
- 19:58 Athena feature job 3545893 (MODE=f) done: test_eval_jpeg (612) and train_armf_jpeg (46,330) features;
  `run_p3f.sh 3545893` queued (rescore all heads with the JPEG frames, arm f heads, readers).
- 20:05 Amendment A11 (lead, after the protocol-network pre-run review): 10 ViT-B/16 LoRA fits (arms a, c, d, e, f x
  seeds 401, 402; `athena_lora_b.sbatch`, `lora_run.sh` with RECIPE=m3), history-matched pool flag reads, validity
  condition on arm (a), storage strata checked (class balance holds in every stratum). First submission 3545913 /
  3545914 cancelled (smoke task name collided with production); resubmitted 3545916 (smoke) → 3545917_[0-9].
- 20:08 `read_p3.py` gained the A11 reads (history-matched pool flag and miss per cell at the own rule and at the
  camera-photo 5% threshold).

## 3. Data

Inputs (read only):
- SMDD training release `/mnt/t7/Datasety/downloads/SMDD/SMDD_release_train/{os25k_bf_t (25,000), m15k_t (15,000),
  train.csv}`; evaluation release `.../SMDD_release_evaluation/{os25k_bf_e, m15k_e, *_crop224, evaluation*.csv,
  crop_images_224.py}`; morph-source renders `.../SMDD/os25k_m_t` and `os25k_m_e` (25,000 each; origin of these
  folders not recorded on disk).
- Stored landmarks of the genuine renders `.../SMDD/smdd_bona_landmarks_if106.npz` (sha256 f167eaf8…, 25,000 x 106,
  normalised; 3 NaN); look-alike table `smdd_bona_lookalikes.npz` (32 ArcFace neighbours, `os25k_bf_t` only).
- Shrunk copies of the genuine renders (a47, 80 px) `/mnt/t7/smad_heldout/a47/data47/i3/train/smdd_a47e7/os25k_bf_t`.
- Test frames: `eval.csv` FRLL-Morphs / MorDIFF / DiM rows (orig, resmatch) and the FRLL genuine jpeg90/70/50 rows
  under `/home/narolski/mambamorph-code/smadcvpr_data/eval`; corrected MAD22
  `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/{native,e7}`; AR1 ladder
  `/mnt/t7/smad_next/AR1/manifest.csv` (19,515 rows when snapshotted, sha256 9c69d44f…, copy
  `/mnt/t7/smad_next/SM1/ar1_manifest_snapshot_9c69d44f.csv`) and its frames.

Produced (all under `/mnt/t7/smad_next/SM1/` unless said):
- Landmarks `lm/srcm_if106_{pool (3,025), contrib (3,858), evalp (5)}.npz`; `.tem` files `tem/{bf,src,srce}/`.
- Lists `lists/`: `arm{b,bp,c,cr,d50,d500}.csv` (14,734 each), `arma.csv` / `arma256.csv` (14,734 / 14,236 release
  files), `armc_15k.csv`, `armcr_15k.csv`, `audit.csv` (9,520), `audit_renders.csv` (535), `ar1h.csv` (536),
  `jpeg_assign.csv` (46,330), `shrink_armc.csv`, smoke lists. Summary `pairs_all.log`, `experiments/.../pairs_summary.json`.
- Images `img/`: `armb, armbp, armd50, armd500` (14,734 each), `armc` (15,000 morphs + 30,000 halves; the first
  14,734 pairs are the arm), `armcr` (15,000), `arme` (45,000 80-px copies), `armf/{jpeg90,jpeg70}` (46,330),
  `audit` (9,520), `ar1h` (536 morphs + 1,072 halves). Builds of b, b′, c, c′, K = 50, K = 500, audit, ar1h on leaseB
  (tars and logs in `lease/`); e and f on the DGX.
- Storage strata per arm: a to d, K = 50, K = 500 hold 256-px files (a also the 733 release files 257 to 264 px tall);
  e holds 256 px and 80 px copies, half each, in both classes (morph share 0.371 in each stratum); f adds JPEG
  90 / 70 copies to about a third of e's images (morph share 0.363 to 0.379 per stratum, overall 0.371).
- Feature lists `flists/` (test_eval 14,120; test_mad22 5,707; test_ar1 19,515; test_ar1h 1,072; test_eval_jpeg
  612; audit 10,055; train lists of every arm; tab.csv 50,010 and tab_sub.csv 7,810).
- Athena features merged per list: `feat_athena/<list>.npz` (jobs 3545820 and 3545893); DGX features
  `feat/test_eval.npz` (equivalence check only).
- Arm compositions `compose/<arm>_s<seed>.json`; LoRA manifests `lora/manifests/` (tar `gpupack/sm1lora_manifests_v2.tar`).
- GPU packs `gpupack/`: `sm1gpu_code.tar`, `sm1gpu_code_v2.tar`, `sm1gpu_img_{test,base,armsc,audit,arme,armsb,
  jpegeval,armf}.tar` (+ `.sha256`); same files on Athena `/net/pr2/projects/plgrid/plggrestoration/smad-next/packs/SM1/`.
- Scores: `heads/` (frozen heads, 5 seeds and boot variant; `feref.npz`), `heads/smoke/`, `p2scores/` (releases on
  audit crops), `p2scores/whole/`, `p2scores/tab_sub/`; Athena results `athena/`.
- `madation_convert/A12REL/*/convert.json` (maps release names to sha256); `sources/` (SMDD README and paper HTML
  as fetched 11 Nov).

## 4. Code (`/home/narolski/smad-next/src/SM1/`)

| Script | Job |
|---|---|
| `sm1_common.py` | paths, partners (training and evaluation), sha, `.tem` writer, if106 loader |
| `p1_document.py` | Part 1 structure audit → `p1_structure.json` |
| `landmarks.py` | insightface buffalo_l pass (det 512, 106 points, ArcFace where needed), stages pool / contrib / evalp |
| `pairs.py` | `.tem` files, (c)/(c′) 15k lists, audit lists, all lists (A5 frame rule, dose arms) |
| `build.py` | unchanged 68/78 engine via a recorder wrapper; halves; asserts; `--verify-cli`, `--compare`, `--root` |
| `wcss_prep.py`, `wcss_run.sh`, `lease_sm1.sh` | one-tar-in / one-tar-out CPU tasks (WCSS or leaseB) and the leaseB driver |
| `shrink.py` | arm (e) shrink step = `a47_data._one` unchanged |
| `jpeg_arm.py` | arm (f): JPEG verification, assignment, build with `prep_eval.degrade` unchanged |
| `featlists.py`, `compose.py` | feature lists; arm compositions |
| `feats.py`, `feats_gpu.py`, `gpu_pack.py`, `athena_feats.sbatch`, `merge_feats.py` | features (DGX check; Athena pass; packs; merge; equivalence) |
| `heads.py`, `read_p3.py`, `pool_cue.py`, `lapvar.py` | Part 3 heads, reader, pool-cue check, sharpness acceptance |
| `rel_score.py`, `rel_multi.py`, `ar1copy/crop_rgb.py`, `run_crops.sh`, `run_p2.sh`, `read_p2.py` | Part 2 |
| `tab.py`, `run_tab_multi.sh` | T-A / T-B / T-C |
| `lora_lists.py`, `lora_run.sh`, `athena_lora.sbatch`, `athena_lora_b.sbatch`, `lora_read.py` | LoRA fits |
| `expr_geom.py` | geometry-only smile probe (A3 substitute) |
| `run_p3.sh`, `run_p3f.sh`, `run_feats.sh`, `run_contrib.sh`, `run_gpupack.sh`, `athena_up.sh` | chains |
| `heads_v1_unused.py`, `run_p2_v1_unused.sh` | superseded first versions, never run to a result |

Environment: DGX `/home/narolski/mambamorph-code/.venv-spark/bin/python` (Python 3.12.3, torch 2.12.1+cu130,
timm 1.0.27, cv2 4.11.0, numpy 1.26.4, insightface 1.0.1, onnxruntime 1.27.0); facenet venv
`/mnt/t7/thirdparty/facenet_pytorch_2.6.0_20261107/venv` (MTCNN crops); leaseB venv `/workspace/sm1/venv` (Python
3.10.13, numpy 1.26.4, opencv-python-headless 4.11.0.86); Athena shared venv (Python 3.10.4, torch 2.2.1+cu121,
timm 1.0.27, numpy 1.26.4, pillow 10.2.0). Engine sha256: 68_hires_morph.py 71643aad…, 78_tool_morph.py b8a389f1….
prep_eval.py 374408ab…, a47_data.py fcd48e1a…. Release weights (staged payload, by sha256): MADation ViT-B/16
ddb1455b…, ViT-L/14 bb452ded…, FE ViT-B/16 6a4d93ba…, FE ViT-L/14 74dd7fbc…, FS ViT-B/16 a7cacd47…, FS ViT-L/14
6071ec7b…; MixFaceNet-MAD 3d507c8b…. CLIP tower: timm `vit_large_patch14_clip_quickgelu_224` with the cached
`timm/vit_large_patch14_clip_224.openai` weights (sha256 eb70c15b…). Seeds: heads and fits 401 to 405; data draws
20261111 (+ offsets in the scripts).

## 5. Results

See `result.md` for every table: Part 1 and T-C; expression; T-A / T-B (`tab_sub.json`); Laplacian acceptance
(`lapvar.json`, `lapvar_f.json`); Part 3 smoke (`p3_smoke.json`) and full (`p3_full.json`, `p3_full_seeds.csv`,
bootstrap variant `p3_full_boot.json`); Part 2 (`p2_full.json`, pending). Partner matching for the audit
(`pairs_summary_audit.json`): trained → matched unused partner: img054553 → img167417, img282038 → img029400,
img496816 → img200961, img337488 → img380037, img099545 → img197375; mean ArcFace cosine key to partner: trained
0.037, matched unused 0.035, placebo 0.028.

## 6. Checks

Verified: landmark pass reproduces stored if106 points (max 0.014 px over 20 renders); wrapper = unchanged 78 command
line (max 0 on every task's 8-pair check, DGX and leaseB); leaseB outputs = DGX outputs (32 per task + 2,000 smoke
files, max 0); our AR1 morphs = AR1's R4 files (536 of 536); halves average within 0.5 grey level of every morph;
shrink call = stored a47 copies byte for byte (8 of 8); `prep_eval` jpeg70 path reproduces two evaluation files byte
for byte; CLIP tower = FE release tower (0.0); `feats_gpu.py` = `feats.py` on the DGX (1.2e-7); Athena vs DGX features
on 14,120 frames (max 1.0e-3, AUC Δ 1e-5); pool-cue AUC 0.507; release CSVs vs folders (T-C).
Not verified / failed: FE header reproduction of A12REL scores within 1e-3 (0.0062); where `os25k_m_*` came from;
the T-A / T-B full 50,010-image set (only the registered 7,810-image subsample); WCSS OpenCV 5.0 equality.

## 7. Dead ends and failures

- `pkill -f` / `pgrep -f` / `grep` over `ps` with a pattern that also occurs in my own command line killed my
  own shell three times (exit 144). Fix: start long jobs from script files and select PIDs by patterns that do not
  appear in the killing command.
- npz member re-read in a dict comprehension (25,000 reads of a 21 MB array): fixed by reading members once.
- `rel_multi.py` with 7 releases at once ran out of GPU memory (GB10 unified memory, ~20 GB free system-wide; the
  first 8-image test's "CUDA error" was the same); fixed by detector groups of at most 5.
- WCSS job 6301971 (task `SM1_cpu_c`, pre-A5 lists): would fail on engine errors; WCSS refused connections from
  16:54, so it was never re-staged; all builds went to leaseB / the DGX instead.
- First smoke build crashed on an engine error for out-of-frame landmarks → A5 (705 files deleted).
- The DGX feature pass ran at 3.4 images/s (CPU decode under load 70 to 190); moved to Athena (A7).
- The AR1 crop script changed while in use by another owner; a frozen copy is used (`ar1copy/`).
- A single MTCNN crop process ran at 1.3 images/s; split into 3 shards.
- The T-A / T-B full set would have taken hours on the shared GPU; registered subsample (A8).
- `lapvar.py` arm-f branch: loop variable shadowed the sample size (TypeError); fixed and rerun.
- The ViT-B/16 smoke job was first submitted without a `_smoke` task suffix (it would have written the production
  task's result name); cancelled with its dependent array and resubmitted (3545916 smoke, 3545917 production).
- On Athena I ran `sha256sum -c` over the pack tars on the login node once (against the rule); not repeated.
- Arm (e) was first skipped (80-px copies) and then approved (A4); the pixel expression probe could not run (A3 note).

## 8. Observations and ideas

- 367 of 24,997 genuine renders and 42 of 3,005 pool renders have landmark points outside the 256-px frame
  (mostly chins below the frame: 362 above 255).
- SMDD morph files 257 to 264 px tall (733 training, 417 evaluation) are an image-size cue unique to the attack class;
  dropping them (a256) changes the frozen-head numbers by at most 1 EER point.
- The pairing condition of the SMDD terms covers our audit morphs and arms (b), (b′), dose (release source data).
- One evaluation-split partner (img005071) is missed far more often than the other four by four of five releases.
- Frozen heads on arm (c) (look-alike pairs) have the largest diffusion-cell rise under history matching (+21 points);
  adding halves (d) or history copies (e) brings it to +7 and +3.5 at a landmark-cell cost of +4 and +6 EER points.

## 9. Open items and next steps

Part 2 reading (after the DGX scoring, about 21:00 to 22:30); arm (f) frozen heads and the JPEG / history-pool reads
(`run_p3f.sh`); LoRA fits: fetch each `SM1L_*` / `SM1B_*` tar from Athena results with its sha256, `lora_read.py`,
then `read_p3.py --dir /mnt/t7/smad_next/SM1/lora_scores --name lora_vitl` (and a ViT-B/16 folder); DiD of the audit
for the frozen heads is in `read_p2.py`. Arm (a)'s history-matched flag rate decides whether the storage comparison
counts (A11).

## 10. Handover state (20:10)

- DGX: `run_p2.sh` (Part 2 scoring, log `logs_p2.log`; rerun skips finished detectors); `run_p3f.sh 3545893` queued
  behind the boot readers (log `logs_p3f.log`; safe to rerun).
- Athena (account plgmultivision-gpu-a100 for the fits): 3545823_[0-19] ViT-L/14 fits (arms a, c, d, e; tasks 0 and
  1 running), 3545894_[20-24] ViT-L/14 arm (f), 3545916 ViT-B/16 smoke → 3545917_[0-9] ViT-B/16 fits (afterok).
  Results land in `/net/pr2/projects/plgrid/plggrestoration/smad-next/results/SM1/<task>.tar` with `.sha256`;
  logs in `.../logs/SM1L-*`, `SM1B-*`. If a task fails, rerun once with the same seed (A9).
- leaseB: nothing running; `/workspace/sm1` holds the venv, packs and logs (volatile, ends about 23:00).
- WCSS: job 6301971 stale (will fail).
- Compute so far: Athena about 1 GPU-h (features + smokes); planned fits about 100 + 9 A100-hours (within 150).

## 11. Reproduce from scratch

1. `python3 -I src/SM1/p1_document.py`; `python3 -I src/SM1/tab.py tc`.
2. `python3 -I src/SM1/landmarks.py --stage pool|contrib|evalp --workers 4`.
3. `python3 -I src/SM1/pairs.py tems`; `pairs.py c15k`; `pairs.py lists`.
4. Builds: `wcss_prep.py --task c|b|a` + `lease_sm1.sh up|run8|run|fetch` (or `build.py --list <list>`).
5. `shrink.py verify`; `shrink.py run --list lists/shrink_armc.csv --out-dir img/arme`; `jpeg_arm.py verify|assign|build`.
6. `featlists.py test|train|audit|test_jpeg`; `compose.py`; `gpu_pack.py code [name]`; `gpu_pack.py images SET lists`;
   `athena_up.sh <tars>`; `sbatch athena_feats.sbatch` (MODE=smoke|full|f); `run_p3.sh JOB`; `run_p3f.sh JOB`.
7. Part 2: `run_crops.sh`; `run_p2.sh`. T-A / T-B: `run_tab_multi.sh` (TABLIST=tab_sub).
8. LoRA: `lora_lists.py`; tar the manifests; `sbatch athena_lora.sbatch` / `athena_lora_b.sbatch`; `lora_read.py`.
