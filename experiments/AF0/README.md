# Alpha-field probe on frozen features (AF0): full record

Owner: AF0 hypothesis owner (Claude agent), DGX (GB10). Started 11 Nov 2026, 14:57 CET. Plain-language rules of
`DOCUMENTATION.md`. `result.md` is the short verdict page; `prereg.md` is the lead's binding registration.

## 1. Question and current answer

Question (prereg, lead): if the training target is a mixing-fraction map a(x) that varies inside each image, does a
per-patch head on frozen patch tokens learn to see texture superposition (and not image-constant cues), so that its
mean prediction separates real landmark morphs from processed genuine photos and does not move with photo history?
The lead added four waves the same afternoon (registered in `result.md` before their numbers): the clean-negative test
(CN0) and the mirror distance (free rider); wave 2 (ghost-energy target), wave 3 (controls: softness can meet the pass
marks), wave 4 (softened examples through the approved shrink-and-enlarge path).

Status 11 Nov 17:30 CET: running. First small pass done (DINOv3 ViT-L/16 at 512, ridge, 600 training morphs):
F1 = 0.275 [0.235, 0.312] (between the drop mark 0.2 and the pass mark 0.4); F2 = 0.9992 [0.9968, 1.0000] (met).
The same head shifts genuine photos by 0.73 R0 standard deviations from R0 to the warp-only rung R2w on FaceMorpher
(0.30 on OpenCV), which is above F3's 0.3 limit if F3 is read on R2w (the lead's addition); on R2 (= R0 pixels) the
shift is 0.08 / 0.00. Full design, F3-F5, CN0, mirror, waves 2-4 are in progress (section 10). No conclusions drawn.

## 2. Timeline (11 Nov 2026, CET)

- 14:57 Read OWNER_BRIEF, prereg, SEEDS S1, 11_AUDIT_PLAN, AR1 prereg / pool / code. Machine load average 48-146
  all afternoon (other owners at nice 0; all AF0 processes run at nice 10 as ordered and get 6-12% of a core each).
- 15:00 `src/AF0/af_morph.py` written: reuses the unchanged engine `scripts/68_hires_morph.py` through
  `scripts/78_tool_morph.py` (module object `hm`), records the engine's own float32 warped images W_A, W_B and its
  triangles by wrapping `hm._warp_tri` during one unchanged `hm.morph` call; blends clip((1-a)W_A + a W_B), uint8 cast.
- 15:05 `src/AF0/pairs.py` (persons, split, manifest). Candidates = AR1's `candidates()` imported unchanged
  (6,921 frames, 1,399 subjects); minus the 536 AR1 hosts/partners; neutral only; AR1's pixel-duplicate rule
  (164 dropped) -> 663 persons (colorFERET 613, FRGC 50), 715 photos; split 80/20 per database by person (seed
  20261512). Frames + .tem copied byte-identically to `/mnt/t7/smad_next/AF0/src/` (sha256 checked).
- 15:08 Verification a = 0.5 vs unchanged engine on 8 pairs: max abs diff 0 (in-process `hm.morph`), and 0 against
  PNGs written by the `78_tool_morph.py` command line (`verify_u50.json`, `verify_u50_vs_78cli.json`,
  `src/AF0/verify_78cli.py`). Zero field = engine's warped host exactly (8/8).
- 15:10 8-image smoke build (`manifest_smoke8.csv`), visual check `check_smoke8_fields.png`; wave-1 build (800
  morphs) at 1,164.5 images/min with 6 processes (`/mnt/t7/smad_next/AF0/build_log_wave1.json`).
- 15:12 Feature smoke test (DINOv3, 8 AR1 images, flip): OK. 15:13 first extraction attempt died: CUDA out of memory
  at `model.to()` (unified memory: system RAM free ~2 GB at that moment, swap full); retried, ran (4.3 img/s).
- 15:20 Wave-2 morph build started with 2 processes (CPU budget); finished 16:29 (57 img/min under load 80-146).
- 15:23-16:30 DINOv3 tokens for the AR1 ladder (8,294 images; list reordered so the first-pass block came first).
- 15:40 First-pass ridge on CPU was starved (11% CPU); killed; GPU retry hit a transient CUDA OOM; the third run fit
  ridge on GPU but predicted on CPU for 20+ minutes (starved); killed; prediction moved to GPU (`--reuse-ridge`), done
  in 228 s. 16:36 first-pass metrics written to `result.md` (16:40).
- 15:45 Lead's additions arrived: fact (R2 = R0 pixels), CN0, mirror distance (registered in `result.md`).
- 16:05 Wave 2 registered (ghost energy). 16:40 wave 3 registered (controls), after reading
  `ideas/CONSOLIDATED_v2.md` sections 1 and 3. 16:50 wave 4 registered (softened examples).
- 16:37 Benchmark list subsampled to `bench_s` (all genuine + at most 600 morphs per cell, seed 401) because DINOv3
  runs at 1-4 img/s on the shared GPU (other owners' feature jobs: SM1, FZ1, PD1).
- 16:45 Verified the shrink-and-enlarge path (wave 4): `prep_eval.degrade` reproduces 8 A47 I-3 copies bit for bit;
  the full E7 branch reproduces 8 registered FRLL `_resmatch_` frames bit for bit (`wave4_verify.json`).
- 16:55 Chains started (section 10). 17:00 an accidental `pkill -f` pattern matched my own shell and killed three
  waiting chains (heads, halves/softening, sanity); they were recreated as script files (`src/AF0/chain_*.sh`).
  A stale waiter whose `pgrep` pattern matched itself was found and killed (17:12).
- 17:05 DINOv3 full heads (ridge, MLP x5, logistic) started on 4,000 training morphs + 569 photos.
- 17:55 ghost.py finished: measured targets for 1,640 pairs (800 wave-1 + 840 further uniform-0.5 pairs), 3,120 halves
  (`ghost_targets.npz` 48.8 MB, `halves.csv`). AR1 softened evaluation copies done (600 sources x 2 strengths,
  `soft_ar1soft_src.csv`, list `ar1soft`).
- 17:40 CN0 on CLIP ViT-L/14-224, image-level part (cue part waited for the cue statistics): see section 5.
- 18:00 The DINOv3 full heads had run 45 min reading only ~1 GB: the time went into the per-image patch-mask
  computation (prep) for af0_w2 under CPU starvation, not into reading. Fixes: exact block means for integer
  footprints (`af0lib.patch_mean`, identical to the area matrix to 3e-16) and a pread-based token reader
  (`af0lib.Tok`, 270 MB/s, equal to the memory map on test indices). Heads restarted (18:02).
- 18:03 A second accidental `pkill -f` (pattern contained in my own command line) killed my shell and the restarted
  heads; rule adopted: kill only by PID. Two of my own background wait loops matched the halves chain's
  `pgrep -f "ghost.py --wave"` and blocked it for ~10 min; killed by PID (18:05).
- 18:05 CN0 rerun inside `chain_clip224_full.sh` died with CUDA out of memory (system RAM); `heads.cuda_ok()` now
  retries 10 x 60 s and then falls back to the CPU.
- 18:10-18:20 wave-3 target sanity (`wave3_target_sanity.json`, section 5): only D passes the lead's rule; the
  registered g fails (higher on flat skin); G and Dm fail on the contrast correlation. Arms (d)/(e) switched to D.
- 18:18 first `soften.py build --list soft_src` died at the face detector's model load (CUDA out of memory; the
  detector in prep_eval is the torch-on-GPU `dmad.quads.gpuface.gpu_face_app`, not onnxruntime); `chain_soft.sh` now
  retries up to 10 x 60 s; resumed (outputs already written are skipped).
- 18:30 CLIP ViT-L/14-336 extraction split into its own queue (`queue_clip336.txt`) so it does not wait behind the
  softened list; the CLIP-224 queue file was truncated in place after its current line (bash reads queue files
  lazily; a new inode would not have been seen).
- 18:37 CLIP-224 full heads done and metrics written (`metrics_clip224_full.json`, section 5).
- 18:40 MADation ViT-L/14 reference numbers from the registered A12REL eval scores (`madation_vitl14_ref.json`).
- 18:45 Lead's round-3 task: softened copies (112.7 px and 61.2 px) of AR1 OpenCV R4, R3 (536 hosts) and R3m (200
  ar1soft hosts) for the protocol-network tests (PN1): `chain_ladsoft.sh` (soften.py unchanged; outputs hard-linked
  under `img/soft_ladder/<rung>_<strength>/`; lead's list `lists/ar1soft_ladder.csv`; extraction list
  `lists/ladsoft.csv`; then cue statistics; CLIP-224 and DINOv3 extraction appended to both queues).
- 18:48 Scoring loop rewritten to read each token chunk once for all heads (it re-read 17 GB per head on the ladder);
  DINOv3 full scoring restarted with `--score-only` (heads were already saved).

Amendments / deviations so far (all reported in `result.md` when final): bench subsample (`bench_s`); wave 2 / 3 / 4
at reduced scale (ghost targets and halves only for wave-1 pairs plus all uniform-0.5 pairs; softened copies only of
the training split, one strength per image alternating; AR1 softened evaluation on 200 hosts); MLP sees 384 random
patches per image per seed (RAM); CLIP ViT-L/14-336 may not be reached tonight.

## 3. Data

All under `/mnt/t7/smad_next/AF0/` (T7 drive on the DGX) unless stated; 46 GB at 17:30.
- `src/{feret,frgc}/<subject>/*.png|.tem`: 715 aligned 512 x 512 frames (record's 73_delin_align output) + 106-point
  landmarks, byte copies of `smadcvpr_data/{train/bona_frgc,train/bona_feret,arms/r6_frgc}` (arms is in /dev/shm).
- `manifest.csv` (sha256 43becaca...): 5,000 morph rows (id, kind, split, db, field, seed, pid_A, pid_B, A, B, image,
  map, wave) + 715 photo rows. Copy: `experiments/AF0/manifest.csv`. Counts: `experiments/AF0/pairs_summary.json`.
- `img/{train,val}/{zero,u25,u50,grad,bump}/*.png` (5,000 morphs), `maps/{split}/{field}/<id>.npy` (float16 512^2
  a(x)) and `<id>_lm.npy` (106 mean-shape landmarks); `maps/zero_512.npy` (photos). Field definitions: `result.md`.
- `img/{train,val}/{halfA,halfB}/*.png`: warped halves (wave 2/3 negatives), being written by `ghost.py`
  (selection: wave-1 pairs + every u50 pair = 1,680 pairs; halfA of zero-field pairs not written: identical to the
  zero-field image). `ghost_targets.npz` (after ghost.py): per pair g, D, G, sdo at grids 32/24/16; `halves.csv`.
- `img/soft/{amsl112,fm61}/*.png`: softened copies (wave 4), being written by `soften.py`.
- Lists (`lists/*.csv`, columns id, path, set, cell, rung, tool, p1, p2, geom, g1, g2, w1):
  af0 (5,715), af0_w1 (1,515; sha 5b7597bb...), af0_w2 (4,200; b436be27...), ar1 (8,294; AR1 ladder R0, R2, R2w, R3,
  R3m, R4, NC for frgcferet + FRLL pools, both tools; 2a1c48a0...), bench (10,159; 6e52b59c...), bench_s (5,936;
  1b774a2d...), h1 (1,196; Poisson set orig variant; be230757...), ar1g (1,800; AR1 graded FaceMorpher m = 0-0.5;
  7806a754...), ar1soft_src (600; 200 seeded hosts x R0 + R2w both tools; ee4fcee2...); to come: af0_h, soft_src,
  soft, ar1soft.
- Benchmark sources (read only, evaluation only): FRLL-Morphs frames from `smadcvpr_data/manifests/eval.csv` set
  frllm (frll_bona orig 204; amsl/facemorpher/opencv/webmorph orig; the families' E7 'resmatch' genuine frames 204
  each); corrected MAD22 `/mnt/t7/smad_heldout/mad22_canonical_E7_inputs_v3_20261109T113746Z/{native,e7}`
  (BonaFide 204; FaceMorpher 1,000, OpenCV 984, Webmorph 500; E7 204 per family); Poisson set
  `/mnt/t7/smad_heldout/h1_poisson/data/manifests/h1poisson.csv` (598 morph + 598 genuine, orig). AR1 images read
  from `/mnt/t7/smad_next/AR1/img/` and `/mnt/t7/smad_next/AR1/src/` (never modified).
- Features `feat/<backbone>/<list>.tokens.npy` (N, T, 1024) float16, `.ids.npy`, `.done` (progress), `.meta.json`
  (transform), `.mirror.npy` (N, T, 2) per-patch mirror distances for flip runs. Backbones: dinov3_512 (32 x 32),
  clip224 (16 x 16), clip336 (24 x 24).
- `prep/g{32,24,16}_<list>.npz` (face-hull fraction and target per patch) and `_inner.npz` (inner-face hull);
  `canonical_lm.npy` (mean landmarks of the wave-1 training images: the fixed hull for benchmark frames).
- `cues/<list>.npz`: 26 cue_floor statistics + PNG bytes per image (wave-3 floor, CN0 part b), being written.
- `heads/<backbone>/<tag>/`: ridge.npz, mlp_s40X.pt, logreg.npz, pred_<head>_<list>.npz (patch predictions float16,
  score = mean in hull, score_top10, score_median, score_inner, score_periph), log.json.

## 4. Code (`/home/narolski/smad-next/src/AF0/`, run with `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`)

Environment: Python 3.12, torch 2.12.1+cu130, timm 1.0.27, scikit-learn 1.9.0, scipy 1.17.1; onnxruntime has only the
CPU provider (face detection in prep_eval runs on CPU). Weights from the local Hugging Face cache, offline:
timm/vit_large_patch16_dinov3.lvd1689m (blob 45172f20...), timm/vit_large_patch14_clip_336.openai (18012c78...),
timm/vit_large_patch14_clip_224.openai (pytorch_model.bin eb70c15b...). Seeds: split 20261512, morph fields per row,
MLP 401-405, bootstrap [20261111, 1] (AR1's), subsamples 401.
Engine pins: 68_hires_morph.py 71643aad7deaabbead698367342434242ec6955fc654c4d19a8f504b41f96d7a, 78_tool_morph.py
b8a389f10ce685fc95b50c69cbcdcf3d44a818ed3d6c04a79849534365cf12b1; prep_eval.py 374408ab... (imported, never edited).

| Script | Job |
|---|---|
| af_morph.py | alpha-field morph engine (verify / build) |
| pairs.py | persons, split, pair manifest |
| lists.py, lists_extra.py | extraction lists (af0, ar1, bench; ar1g, af0_w2, af0_h, h1, soft_src, soft, ar1soft_src, ar1soft) |
| feat.py | frozen tokens (+ mirror distances with --flip), resumable |
| run_feats.sh, after.sh | sequential GPU queues with retries; `wait <file>` lines |
| af0lib.py | shared: lists, landmarks, face-hull and inner-hull patch fractions, area-weighted patch means, stats (AR1's stats.py: a41_read.Draw, a36_read.wauc, analyze.eer) |
| heads.py | ridge / MLP / logistic heads, targets alpha, g, D, G, const, shuffle; wave-3/4 arms; --score-only |
| metrics.py | F1, F2, F3, F5 panels, template and pair-swap controls, Laplacian-variance / best-simple floors |
| f4.py | F4 sets and read |
| cn0.py | clean-negative test |
| mirror.py | mirror distance AUCs |
| ghost.py | wave-2/3 targets g, D, G, contrast; writes halves |
| sanity.py | wave-3 target sanity (flat vs busy, contrast correlation, same-person / mirror ratios) |
| soften.py | wave-4 shrink-and-enlarge path (verify / build) |
| cues_all.py | cue_floor statistics per image |
| thumbs.py, thumb_heads.py | 32-pixel thumbnail baselines |
| sheets.py | prediction-map contact sheets |
| arms.py | wave-3/4 five-arm ablation fits and reads |
| chain_*.sh | the waiting chains of section 10 |
| verify_78cli.py, explore_candidates.py | one-off checks (copied from the scratchpad) |

## 5. Results

First pass (DINOv3, ridge, wave-1 training): see `result.md` table; full numbers in
`experiments/AF0/metrics_dinov3_512_first.json`; F1 template baseline 0.231 [0.138, 0.312], F1 after removing the
template 0.228 [0.190, 0.267], pair swap 0.209 [0.145, 0.275] (52 image pairs, 16 hosts)
(`/mnt/t7/smad_next/AF0/metrics_first_v2_test.json`).
Mirror distance, CLIP ViT-L/14-224, content-aligned (preliminary; benchmark part on a partial extraction):
frgcferet FaceMorpher R2 vs R4 0.715 [0.671, 0.759], R2w vs R4 0.678, R3 vs R4 0.580; OpenCV R2 vs R4 0.608
[0.564, 0.649], R2w vs R4 0.598; FRLL R0 vs R1 (native vs E7 frames) 0.47-0.48 per family (folded 0.52-0.53).
To be finalised in `experiments/AF0/mirror_clip224.json`.

## 6. Checks

Verified: engine equivalence (section 2); field continuity (0 uncovered pixels); DINOv3 transform is identity resize
on 512 frames (assert in feat.py); landmark layout 0-32 = contour (plotted, `check_landmark_index_layout.png`);
all benchmark frames share the canonical eye positions (`check_benchmark_frames_canonical_eyes.png`); wave-4 path bit
for bit (`wave4_verify.json`); NC vs R3 = 0.5 exactly because both tools return identical images for (S, H), (H, S).
Not verified: CLIP transforms beyond timm's own config; FRGC neutral = BlankStare and env codes (taken from AR1).

## 7. Dead ends and failures

- CUDA out of memory at model load / tiny allocations (15:13, 15:42): unified memory with system RAM nearly full and
  swap full; retried later. `torch.cuda.mem_get_info` showed only ~4 GB free at times.
- CPU starvation: nice-10 processes get 6-12% of a core; numpy BLAS spawned 20 threads in prep (710% CPU) -> killed,
  rerun with OMP_NUM_THREADS=1. Ridge prediction in numpy took 20+ min -> moved to GPU.
- `lists_extra.py` failed under `python -I` (script folder not on sys.path) -> path insert.
- Self-killing `pkill -f` (17:00) and a self-matching `pgrep` waiter (17:12): chains rewritten as script files.
- Wave-2 halves/targets cut to wave-1 + u50 pairs; softened copies cut (CPU-bound face detector on CPU provider).
- The registered contrast-normalised ghost target g fails the flat-skin check on our data too: on 1,000 uniform-0.5
  morphs its median on the flattest quartile of in-hull patches is 1.031 against 0.873 on the busiest (contrast rank
  correlation -0.13). The flat-excluding variants fail the other half of the rule: gradient disagreement G (flat 1.57
  < busy 3.78 but contrast correlation 0.70) and D above median contrast Dm (0 < 12.9, correlation 0.82). Only the
  plain disagreement D passes (flat 11.66 < busy 12.89, correlation 0.10). Same-person / two-person ratios on the
  OpenCV engine (100 AR1 hosts): g 0.72, D 0.86, G 0.89, Dm 0.83; mirror / two-person: g 0.76, D 0.50, G 0.90, Dm 0.50.
- Softening failures: CUDA out of memory at detector load (18:18 and once more), handled by retries.
- Each token chunk was re-read once per head during scoring (seven heads x 17 GB on the ladder): fixed 18:48.

## 8. Observations and ideas

- The zero-field images (warp only) score above unprocessed photos (validation AUC 0.72 zero-field vs photo; mean
  0.073 vs 0.030), and R2w scores above R0: warping alone moves the alpha head. That is the R2w shift.
- NC = R3 images for both tools: NC adds no information on these builds.
- MAD22 FaceMorpher morphs carry a visible "Powered by Luxand.com" watermark at the bottom of the frame (outside the
  face hull; a cue for frame-level detectors).
- Mirror distance (CLIP-224): FRLL R0 vs R1 stays near 0.5 (0.47-0.48), MAD22 FaceMorpher morph vs native 0.94.

## 9. Open items and next steps

Full DINOv3 heads -> F1-F5 + F4 + shuffled maps; CLIP-224 heads; CN0 (CLIP-224, DINOv3); wave 2 (g, D vs alpha);
wave 3 controls 1-7; wave 4 arms; contact sheets; CLIP-336 if the GPU allows; MADation ViT-L/14 comparison numbers
(A12REL eval scores for FRLL; AR1's scores when written; corrected MAD22 has no score).

## 10. Handover state (17:30 CET)

DGX processes (logs under `/mnt/t7/smad_next/AF0/`):
- GPU queue DINOv3: `run_feats.sh queue_dino_c.txt` (PID 1990099): bench_s (running, 2,400/5,936), then wait for
  `lists/af0_h.csv`, af0_h, h1, ar1g. Log `queue_dino_c.log`. If it dies: rerun
  `WORKERS=2 src/AF0/run_feats.sh /mnt/t7/smad_next/AF0/queue_dino_c.txt` (resumable).
- GPU queue CLIP: `run_feats.sh queue_clip_b.txt` (PID 1989809): af0_w2 (running), af0_h, h1 (flip), ar1soft, soft,
  ar1g, then clip336 af0_w1, af0_w2, ar1, bench_s, h1. Log `queue_clip_b.log`. Same restart rule.
- `heads.py` DINOv3 full (PID 2072898, chain `chain_heads_dino_full.sh`), log `heads_dino_full.log`; then
  `chain_dino_post.sh` (F4 conf/unconf, shuffled maps), log `chain_dino_post.log`.
- `ghost.py --wave 1 --plus-u50 --workers 2` (PID 2066115), log `ghost_w1.log`; then `chain_halves_soft.sh`
  (af0_h list + prep, sanity.py, soft_src list, soften build, soft list + prep), log `chain_halves_soft.log`.
- `soften.py build --list ar1soft_src` (PID 2062317, chain `chain_ar1soft.sh`), log `chain_ar1soft.log`.
- `cues_all.py ar1 h1 bench_s af0_w1` (PID 2042508), log `cues_all.log`; then `chain_thumbs.sh` (thumbnails +
  thumbnail heads), log `chain_thumbs.log`.
If any chain dies, rerun its script; every step skips finished outputs. Compute so far: about 2 GPU-hours of shared
GB10 wall time; no USD; no WCSS / Athena / Vast use (WCSS closed to our address).

## 11. Reproduce from scratch

```
cd /home/narolski/smad-next/src/AF0; P="/home/narolski/mambamorph-code/.venv-spark/bin/python -I"
$P pairs.py
$P af_morph.py verify --n 8 && $P verify_78cli.py
$P af_morph.py build --wave 1 --workers 6 && $P af_morph.py build --wave 2 --workers 6
$P lists.py && $P lists_extra.py af0_w2 && $P lists_extra.py ar1g && $P lists_extra.py h1   # + bench_s (result.md)
for each backbone: run_feats.sh <queue>   # feat.py --backbone B --list lists/L.csv --name L [--flip]
$P heads.py --backbone dinov3_512 --train af0_w1,af0_w2 --eval af0_w1,af0_w2,ar1 --heads ridge,mlp,logreg --tag full
$P heads.py ... --score-only --eval bench_s,h1,ar1g --tag full
$P f4.py make; heads.py ... --train-ids /mnt/t7/smad_next/AF0/f4/{conf,unconf}_ids.npy --tag f4_{conf,unconf}; $P f4.py read
$P metrics.py --backbone dinov3_512 --tag full --af0 af0_w1,af0_w2 --bench bench_s
$P ghost.py --wave 1 --plus-u50 --workers 2; $P lists_extra.py af0_h; $P sanity.py
$P soften.py verify; $P soften.py build --list soft_src --alternate; $P soften.py build --list ar1soft_src
$P cues_all.py ar1 h1 bench_s af0_w1; $P cn0.py read --backbones clip224,dinov3_512 --dense-tag full
$P mirror.py --backbone clip224; $P arms.py fit --backbone clip224; $P arms.py fit --arms a4,b4,c4,d4,e4; $P arms.py read
```
