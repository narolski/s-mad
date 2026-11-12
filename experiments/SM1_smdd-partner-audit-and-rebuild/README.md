# SMDD five-partner audit and rebuild of the standard training set (SM1): full record

Owner: hypothesis-owner agent, 11 Nov 2026. Registration: `prereg.md` (amendments A1 to A11; A12 = post hoc
addendum after the independent review `experiments/reviews/REVIEW_SM1_20261111.md`). Short verdict:
`result.md`. Code: `/home/narolski/smad-next/src/SM1/`. Large outputs: `/mnt/t7/smad_next/SM1/`.

## 1. Question and current answer

SMDD (Synthetic Morphing Attack Detection Development dataset, Damer et al., CVPRW 2022) is the field's standard
training set: 25,000 StyleGAN2 genuine renders and 15,000 landmark morphs at 256 px per split. On disk, every
training morph has one of only **five** second contributors (the same five renders for all 3,853 first contributors);
the evaluation split has five other partners. The paper's sentence reads naturally as five random partners per key
image; the release differs from that natural reading (not called a bug). Questions: (1) do released SMDD-trained
detectors memorise the five partners (Part 2 and the no-new-image tests T-A, T-B); (2) does rebuilding SMDD with
balanced partners, warped halves as genuine images and history crossing change what a head on frozen CLIP
features learns (Part 3), and the same with LoRA fits on Athena. **Status 11 Nov 21:45:** Part 1, T-A, T-B, T-C,
Part 2 (crop path and whole files), the frozen-head Part 3 (13 arms x 5 seeds) and the A12 tonight items (evaluation-
partner reference, sharpness inside storage strata, fixed-threshold paired table, rewrite of `result.md` with the
review's wording and withdrawn statements) are done. Running on Athena: 35 LoRA fits (A9 to A11), the A12 feature job
(five-random-partner arm, softened AR1 copies) and 4 ViT-B/16 fits of arms b and b′. Plain summary (wording of the
review, section 3): the release has five partner images per split, unlike the natural reading of the paper (content
check pending); released detectors score morphs with the five training partners above morphs with SMDD's own
evaluation partners by 0.4 to 1.0 logit for the adapted MADation releases (near their ceiling) and 3.8 to 13.4 for
the frozen-encoder releases and MixFaceNet-MAD; on frozen CLIP heads, training on the five causes this trace. On
frozen heads (our frames, first-test data, arms fixed in advance), more partners lower native EER but raise flags on
history-matched genuine photos; halves and history copies lower the storage reaction at a cost in landmark error and
in untouched photos flagged at a fixed camera-photo threshold; no rebuilt arm passes the sharpness acceptance (0.89
to 0.96 inside every storage size), so Part 3 is descriptive.

## 1a. Author's ruling of 12 Nov: development exposure of the remedy arms

Ruling: no benchmark set may be used to develop a method. The remedy arms of this experiment, history crossing (e) and
history crossing + JPEG copies (f), and by the same logic the look-alike arm c (the morph base of d, e and f, proposed
by SMDD-T as a better SMDD) and the halves arms d and d+, have been scored on benchmark cells; those scores are
**development exposure** and are labelled so. They are never presented as benchmark results of a proposed method. The
audit arms (Part 2, the partner audit, and the partner-only arms a, a256, b, K = 5 random, K = 50, K = 500, b′, c′)
stay audits of SMDD's construction only as long as no sentence recommends them as a training set. The FRLL JPEG photos
are benchmark-derived, so the e-against-f JPEG comparison is exposure too. The team (including the protocol-network
owner, PN1) has seen benchmark scores of history-crossing and JPEG remedies.

Still to score benchmark cells by their registered run script (12 Nov 13:00; the author may stop them):
- rented machine sm1b: SM1B_bp_s401, SM1B_b_s402, SM1B_bp_s402 (partner-only arms b, b′, not remedy arms): every
  cell of `ad4_eval.csv` (FRLL-Morphs 5 families, MorDIFF, DiM 6, corrected MAD22 5, native and E7), the AR1 ladder,
  the FRLL JPEG photos, and the audit set;
- Athena, queued, forecast late December: 3545823_[2-19] and 3545894_[20-24], ViT-L/14 fits of a (s403 to s405), c,
  d, e (5 seeds each) and f (5 seeds): the same cells. If they ever run, the c, d, e, f fits add remedy exposure; to
  prevent it they must be cancelled (`scancel 3545823 3545894`), which only the lead or author decides.
No new benchmark scoring of c, d, e or f is submitted by this owner.

Benchmark cells on which the remedy arms have been scored (native and history-matched E7 genuine pools of each):
- FRLL-Morphs: AMSL, FaceMorpher, OpenCV, StyleGAN, WebMorph (morphs, FRLL genuine photos, E7 copies per family);
- MorDIFF (morphs, genuine, E7 copies);
- DiM: DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S (morphs, genuine, E7 copies);
- corrected MAD22: FaceMorpher, MIPGAN-I, MIPGAN-II, OpenCV, Webmorph (morphs, genuine, E7 copies);
- FRLL genuine photos under JPEG 90 / 70 / 50 (derived from the FRLL benchmark photos).
Score sets that touched them: frozen heads e, f, d, d+ (our recipe, 5 seeds; `heads/`), the same with the release
recipe (`heads_fz1/`), and on the rented machine the ViT-B/16 LoRA fits of e and f (A13; `ad4_eval.csv`, the same
cells) as they finish; the ViT-L/14 LoRA fits of d, e, f would too if Athena runs them. Reads: `p3_full.json`,
`p3_fz1.json`, `a12_fixed*.json`, `a12_border.json`, the A11 history-pool and A10 JPEG reads. Not benchmark cells:
the AR1 ladder and halves (FRGC / colorFERET / FRLL-derived, our development material), the softened AR1 copies
(AF0), the audit set and SMDD's own splits.

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
- 20:15 `run_p3f.sh` done: all saved heads rescored with the JPEG frames (`heads.py --rescore`), arm (f) heads
  (5 seeds + bootstrap), readers rerun (`p3_full.json` now 13 arms with JPEG and history-pool reads); Laplacian
  acceptance of (f) 0.724 at the loader size (`lapvar_f.json`; not accepted). Tables in `result.md`.
- 20:30 ViT-B/16 smoke 3545916 hung after the optimiser setup for 23 min (AveCPU 3 min; 14 loader workers at batch
  256; shared-memory pressure suspected, not verified); cancelled with its dependent array 3545917 and resubmitted
  with 6 loader workers: smoke 3545956 → fits 3545957_[0-9] (afterok). ViT-L/14 fits run at 0.49 it/s (about 3.9 h
  of training per fit; 25 fits about 100 A100-hours).
- 20:30 Frozen-head partner audit (`p2_full.json` heads / did): heads trained with the five partners show a gap of
  5.8 to 6.1 logits (placebo p < 1e-5); heads trained without them 0.1 to 1.3; the FE ViT-L/14 release header 4.92
  (p 0.0006). Written to `result.md`.
- 20:45 Part 2 primary (releases on own crops) read (`p2_full.json`): every primary release shows partner
  memorisation under the registered rule (gap 1.7 to 16.2 logits, intervals above 0, placebo p ≤ 0.0044). The lead's
  falsifier does not hold. Report sent to the lead. Still running: `run_p2.sh` (FS crops, whole-file pass, then
  `read_p2.py` for the bridge and the secondary readings) and the Athena fits.

- 20:50 Lead: independent review `REVIEW_SM1_20261111.md` (verdict: needs qualification); follow-ups 1 to 13; DGX
  limit 2 processes, OMP 2, nice 10; T7 floor 50 GB free; list of local pack tars with verified Athena copies sent.
  `run_p2.sh` (6 workers) stopped; whole-file pass restarted as `run_p2_whole.sh` (1 process + 2 loader workers).
- 21:10 Amendment A12 (post hoc addendum, items 1 to 13) registered in `prereg.md` before any A12 score.
- 21:12 A12 item 1 (`a12_partner_ref.py`): trained − KE for releases (crop) 0.43, 0.95, 3.87, 3.76, 13.36; heads
  with the five 4.0 to 4.4, without −1.15 to −0.03; DiD a − b′ 5.25 [5.14, 5.36]. Its first run (about 1 min)
  overlapped with the whole-file pass, so the DGX briefly had 4 of my processes (limit 2); rerun at 21:20 alone,
  with the whole-file scores (trained − KE 0.44, 0.45, 4.14, 3.46, 4.57).
- 21:13 Whole-file Part 2 pass done (1,050 s, 10,055 x 5 releases); `read_p2.py` rewrote `p2_full.json` (bridge,
  whole-file secondary; every release's registered rule outcome "partner memorisation").
- 21:15 Implementation notes for A12 items 9 to 12 added to `prereg.md` (before any of their scores).
- 21:16 A12 item 3 (`a12_fixed.py`): fixed-threshold paired table (camera threshold and own rule) for 12 arms + FE
  header; reproduces the review's JPEG increments (a +0.196, c +0.121, d +0.072, e +0.032, f +0.068).
- 21:17 A12 item 11: `armd5.csv` (`pairs_d5.py`; pool reconstruction reproduces `armd50.csv` and `armd500.csv`
  exactly; 3 backward swaps); built on leaseB as overlay task `d5` on pack b (8-pair check: wrapper = 78 CLI 0,
  leaseB = DGX references 0; full 14,734 in 95 s, 0 failures); fetched (sha256 OK) and installed in `img/armd5`.
- 21:20 A12 item 2 (`a12_sharp.py`): Laplacian AUC inside storage strata 0.89 to 0.96 (d 0.948, e 0.952 / 0.898,
  f 0.886 to 0.956 at 224 px); two-variable rule d 0.948, e 0.928, f 0.927. Class balance of f inside strata for all
  five seeds 0.363 to 0.379 (`a12_armf_strata.json`).
- 21:24 `sm1gpu_img_a12.tar` (armd5 + 3,744 softened AR1 copies of the protocol-network experiment, 2.74 GB) streamed
  to Athena without a local copy (`athena_stream.sh`; T7 at 54 GB free); lists overlay, LoRA manifests for b / b′ and
  the audit manifest uploaded; Athena `lora_run.sh` was byte-identical to the local pre-A12 copy before the update.
  Submitted (account plgmultivision-gpu-a100, `--exclude=t0010`): 3546033 feature pass MODE a12, 3546034_[0-3]
  ViT-B/16 fits of b, b′ (no separate smoke: the A11 smoke of the same script passed; only the manifest tar and the
  armsb image set differ).
- 21:45 `result.md` rewritten (review wording, WITHDRAWN statements with reasons, A12 tables, Part 3 labels).

- 21:30 to 21:55 A12 CPU items 5 to 9 (at most 2 processes): item 5 `heads_fz1.py` (60 heads, about 4 s each) and
  reads (`p3_fz1.json`, `a12_fixed_fz1.json`, `a12_partner_ref_fz1.json`): arm a diffusion rise +6.68 [5.09, 8.16]
  (ours +11.32), e +0.03; neither supported nor falsified. Item 6 `a12_border.py`: b → b′ on the two border-free
  cells −2.77 (falsified: within 1 point of −3.42); c → d −0.25 there against +5.97 on the bordered cells. Item 7
  `a12_partner_var.py`: per-partner spread 0.25, 0.15, 6.2, 3.2, 3.45; width ratio 1.44, 1.45, 3.81, 2.79, 2.13.
  Item 8 `a12_names.py`: named partner the most similar of five for 97 / 98 of 100; first contributor above 20
  random renders 100 / 100. Item 9 `a12_sharp_slope.py`: falsified (genuine Δρ 0.0004; morph Δρ +0.08 in the
  opposite direction). `result.md` updated.
- 21:52 Athena: ViT-L/14 tasks 2 to 24 still pending (ReqNodeNotAvail with a 7 h limit; 13 nodes reserved, 23
  failed); 3546033, 3546034 pending (Priority).

- 22:00 Arm d5 wired into `compose.py`, `heads.py`, `read_p3.py` (steps b → d5, d5 → K = 50), `a12_fixed.py`,
  `a12_partner_ref.py`; chain `run_a12f.sh JOB` (fetch, merge, compose, heads both recipes, readers,
  `a12_af0soft.py` for item 13) waits for 3546033. `sm1_lora_audit.py` smoke on the 3-step smoke fit submitted as
  3546052 (pipeline check only; its scores mean nothing).

- 22:10 Lead: Athena cannot start the queue tonight; ViT-B/16 fits move to one rented RTX 6000 Ada (amendment A13,
  registered). Prepared `src/SM1/rented/` (RUNBOOK.md, drive.sh with one `all` command, remote_setup.sh,
  unpack_one.sh, fit_local.sh, remote_smoke.sh, remote_queue.sh); uploads from owner sessions are refused tonight,
  so the lead starts the driver. 12 packs, 45.8 GB; about 14 h for 12 fits.

- 22:49 to 02:50 (rented, lead's machine `/mnt/t7/smad_next/vast/sm1b`, RTX 6000 Ada, not an A100): setup 3,238 s
  (45.8 GB, every pack hash OK), smoke rc 0 (1.43 it/s, peak 30,840 MiB, audit check max diff 0.0), Athena ViT-B/16
  jobs 3545957 and 3546034 cancelled, queue started 22:49 UTC. Bug: the `queue` step's ssh never returned (the
  backgrounded `cd && nohup ... &` list kept the session's stdout), so `all` never reached its pull loop; the lead
  copied SM1B_a_s401 and SM1B_c_s401 by hand (hashes re-checked here). Fixed in `rented/drive_v2.sh` (queue line;
  new `pullloop` step with a final pull and RELEASE); the running `drive.sh` was not edited (bash reads it while it
  runs) and its stuck processes were not killed (permission refused). Single-seed descriptive rows in `result.md`.
  `lora_read.py` takes a prefix and output name (SM1B, lora_scores_vitb) and skips non-folders.

- 12 Nov 10:12 Athena 3546033 (A12 features) done; `run_a12f.sh 3546033` (fetch sha OK, merge, d5 compositions, d5
  heads both recipes, readers, `a12_af0soft.py`): H-new-1 falsified (d5 landmark-7 5.07); softened-copy increments
  e / f +0.03 to +0.05 against +0.09 to +0.28 for the other arms. T7 28 GB free at 10:15 (not my writes).

- 12 Nov 11:40 Eight rented ViT-B/16 fits (a, c, e, f x 401, 402) back (hashes OK; pulled by the lead);
  `lora_read.py` now also reads `audit/scores_audit.npz` (ids unconverted); registered reading in `result.md`
  (`p3_lora_vitb.json`, `a12_fixed_vitb.json`, `a12_partner_ref_vitb.json`). Release check for sm1b answered to the
  lead: weights = `ad4eval/last_trainable.pt` (312,570 B) in every tar; only the machine logs and smoke folder were
  not copied back (one rsync given); no RELEASE written by me.

- 12 Nov 15:22 to 15:31 A15 dev run on sm1b (started by the lead with `drive_v2.sh dev`): **no score produced.** Owner
  bug: the dev step uploaded `remote_dev.sh` but not the updated `sm1_lora_audit.py`, so the machine's setup-time
  scorer rejected `--check-npz` and all 6 fits were skipped (log `results_rented/dev/dev.log`); no network scored any
  data. At 15:31:11 the stale `drive.sh all` (PID 2725924) wrote RELEASE (12 of 12 fit tars verified). Fixed in
  `drive_v2.sh` (dev uploads the scorer, clears the done-marker); A15 runs again only on the lead's start (sm1b if kept,
  else `devfresh` on another lease).
- 12 Nov 15:25 Full registered ViT-B/16 reading of all 12 fits (a, b, b′, c, e, f x 401, 402) in `result.md`
  (`p3_lora_vitb12.json`, `a12_rank_vitb12.json`, `a12_fixed_vitb12.json`); reader `a15_read.py` written for A15.

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
- Lists `lists/`: `arm{b,bp,c,cr,d50,d500,d5}.csv` (14,734 each; d5 = A12 item 11), `arma.csv` / `arma256.csv` (14,734 / 14,236 release
  files), `armc_15k.csv`, `armcr_15k.csv`, `audit.csv` (9,520), `audit_renders.csv` (535), `ar1h.csv` (536),
  `jpeg_assign.csv` (46,330), `shrink_armc.csv`, smoke lists. Summary `pairs_all.log`, `experiments/.../pairs_summary.json`.
- Images `img/`: `armb, armbp, armd50, armd500, armd5` (14,734 each; armd5 built 21:17 on leaseB, tar
  `lease/sm1_d5_out.tar`), `armc` (15,000 morphs + 30,000 halves; the first
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
  A12: `sm1gpu_lists_a12.tar`, `sm1lora_manifests_b.tar`, `sm1lora_manifests_audit.tar` (local and Athena);
  `sm1gpu_img_a12.tar` on Athena only (streamed; sha256 bc7c784b…, `gpupack/stream_sm1gpu_img_a12.tar.json`,
  file list `gpupack/filelist_a12.txt`).
- A12 lists: `flists/train_armd5.csv` (14,734), `flists/test_af0soft.csv` (3,744: AF0 `ar1soft.csv` + `ladsoft.csv`,
  base = the SM1 id of the unsoftened AR1 image).
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
| `run_p2_whole.sh` | Part 2 whole-file pass + `read_p2.py` under the 20:50 DGX limit |
| `a12_partner_ref.py` | A12 item 1: trained − KE, KE − U, own-rule miss by partner kind, head DiD (`--heads-dir` for FZ1 / LoRA) |
| `a12_sharp.py` | A12 item 2: Laplacian AUC inside storage strata, two-variable rule |
| `a12_fixed.py` | A12 item 3: fixed-threshold paired table (camera threshold, own rule; `--dir` for other score sets) |
| `heads_fz1.py` | A12 item 5: heads with the release (FZ1) recipe, no flip → `heads_fz1/` |
| `a12_partner_var.py` | A12 item 7: per-partner EER of the SMDD splits, one-way vs two-way intervals |
| `a12_names.py` | A12 item 8: file names against ArcFace similarity, 100 morphs per split |
| `a12_sharp_slope.py` | A12 item 9: Spearman of head logit against log Laplacian variance per class |
| `sm1_lora_audit.py`, `athena_lora_audit.sbatch`, `a12_lora_prep.py` | A12 item 10: audit set scored by finished LoRA fits |
| `pairs_d5.py`, `prep_d5.py`, `a12_flists.py`, `athena_stream.sh` | A12 items 11, 13: five-random-partner list, leaseB overlay task, feature lists, streamed upload |
| `a12_lora_lists_b.py`, `athena_lora_b2.sbatch` | A12 item 12: ViT-B/16 fits of arms b, b′ |

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
bootstrap variant `p3_full_boot.json`); Part 2 (`p2_full.json`). A12: `a12_partner_ref.json` (item 1),
`a12_sharp.json` (item 2), `a12_fixed.json` + `a12_fixed_seeds.csv` (item 3), `a12_armf_strata.json`, `pairs_d5.json`. Partner matching for the audit
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
  The resubmitted smoke then hung with 14 loader workers at batch 256; cancelled and resubmitted with 6 workers
  (3545956 smoke, 3545957 production).
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

A12 (`prereg.md`): items 1 to 9 done (`result.md`). Remaining: 10: when fits finish, fetch result tars, then submit
`athena_lora_audit.sbatch` with FITS="SM1L_... SM1B_..." (`-A plgmultivision-gpu-a100 --exclude=t0010`), read with
`a12_partner_ref.py` style reader per family. 11 and 13: after job 3546033, merge features (`merge_feats.py`), add
arm `d5` to `compose.py` / `heads.py` / `read_p3.py` (steps b → d5, d5 → K = 50), fit 5 seeds, read; score the
softened AR1 copies with the e and f heads (and the others) at both thresholds. 12: after 3546034, `lora_read.py`
into a separate folder, `read_p3.py --seeds 401,402`.

## 10. Handover state (22:00)

- DGX: nothing of mine running. Limit: 2 processes, OMP 2, nice 10. T7 54 GB free (floor 50 GB): no new local
  copies over 1 GB; large data goes to Athena (stream with `athena_stream.sh`).
- leaseB: task d5 done and fetched (sha256 OK); `/workspace/sm1` holds the venv, packs, logs and the d5 result tar
  (volatile, ends about 23:00). Nothing else to run there.
- Athena (account plgmultivision-gpu-a100): ViT-L/14 fits 3545823_[0-19] (tasks 0 and 1 running on t0016; the rest
  pending, ReqNodeNotAvail), 3545894_[20-24] (arm f, pending); ViT-B/16 3545957_[0-9] (pending, Priority);
  A12: 3546033 (features MODE a12), 3546034_[0-3] (ViT-B/16 b, b′). Results in
  `/net/pr2/projects/plgrid/plggrestoration/smad-next/results/SM1/` with `.sha256`. Each fit's result tar holds
  `ad4eval/last_trainable.pt` and `meta.json` (needed by A12 item 10). To read the fits: as before (copy back with
  one flock rsync, check sha256, extract into `/mnt/t7/smad_next/SM1/athena/lora/`, `lora_read.py`, `read_p3.py
  --dir ... --name lora_vitl`); check the T7 floor first.
- WCSS: job 6301971 stale (will fail).
- Compute: Athena about 1.5 GPU-h used before A12; planned fits about 100 (ViT-L/14) + 9 (ViT-B/16) A100-hours;
  A12 adds about 0.1 (features), about 4 (b, b′ fits) and about 2 (audit scoring).

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
