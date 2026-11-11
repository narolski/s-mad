# FZ1: do frozen foundation features read the mixing step of a morph? (full record)

Owner: FZ1 hypothesis owner (Claude agent), started 11 Nov 2026 15:17 CET. `prereg.md` = registration,
`result.md` = short verdict, this file = full record. Code `/home/narolski/smad-next/src/FZ1/`, large outputs
`/mnt/t7/smad_next/FZ1/`.

## 1. Question and current answer

Question (hypothesis H-new-3 of the lead): the frozen OpenAI CLIP ViT-L/14 image encoder carries a linear
read-out of latent mixing in diffusion-autoencoder (DiffAE) morphs; a head trained on SMDD only would rank our
DiffAE morphs above one-photo DiffAE reconstructions without ranking reconstructions above camera photos, while
the fully adapted MADation release loses this. Trigger: the released MADation "FE" ViT-L/14 (frozen CLIP + trained
linear head) gives B vs D 0.852 on the A43 MorDIFF material, unlike every adapted release.

Status 11 Nov 20:15 CET: **finished** (all four parts run). Results:
- P1 (re-read of existing release scores): the six reviewer-preview AUCs reproduce to three decimals.
- P2 (probe = gate G-c): a cross-validated logistic probe on frozen features separates every A43 contrast
  (B20 vs D20, B vs D, C20 vs D20, B20 vs C20) at AUC 0.945–1.000 on all four feature sets (CLIP with MADation
  input, CLIP with native input, DINOv3, DINOv2); StyleGAN3 morph vs one-identity render 0.886–0.936; StyleGAN3
  morph vs spread-matched render 0.583–0.632.
- P4 (simple statistics): on the 224 input no single statistic matches the probe; on the central 256 × 256 of
  the 512 frame Laplacian variance alone gives 0.966 for B vs D (morphs higher), and a 7-statistic logistic
  0.988 matches the probe there; for B20 vs D20 the statistics stay at 0.66–0.70.
- P3 (five SMDD-only heads with the MADation FE recipe, seeds 401–405): B vs D 0.789–0.792, D vs R0
  0.508–0.512 in every seed, so the registered prediction (≥ 4 of 5 seeds with B vs D ≥ 0.75 and D vs R0 ≤ 0.60)
  is met 5 of 5 ("supported"). Same heads: B20 vs D20 0.626–0.628, C20 vs D20 0.51, StyleGAN3 0.48–0.50,
  MorDIFF EER 40.2–40.7%. The heads are nearly identical across seeds and correlate 0.87–0.88 (Spearman) with
  the released FE head.

## 2. Timeline

All times CET, 11 Nov 2026.
- 15:17 Read `OWNER_BRIEF.md`, `NOTEBOOK.md`, `11_AUDIT_PLAN.md`, `10_ASSET_INVENTORY.md`,
  `12_STATE_AT_HANDOVER.md`, `experiments/AD1/result.md`, `experiments/AG5/result.md`, the reviewer previews
  (copied to `src/FZ1/reviewer_preview/`), the A43 README, the MADation training code
  (`/home/narolski/mambamorph-code/baselines/MADation/src`) and the A36 port (`mambamorph-code-a43/smadcvpr/
  a12_released.py`, `a36_madation.py`) to learn the release's input convention (BGR, (x − 0.5)/0.5 at 224, PIL
  bilinear from the 512 frame; head on L2-normalised projected embedding; class 0 = attack).
- 15:26 `prereg.md` written, before any new computation (P1 marked post hoc).
- 15:30 P1: `python -I src/FZ1/fz1_p1.py --smoke`, then full → `experiments/FZ1/p1_release_reread.json`,
  log `/mnt/t7/smad_next/FZ1/p1.log`. Preview check passed.
- 15:31 Extracted `A12REL/madation_fe_vitl14` and `_fe_vitb16` from the release tar to the scratchpad; found
  the FE ViT-L/14 `training.log` in the scratchpad (`ext/madation_weights/vitl14_fe/`). Both copied at 17:28 to
  `/mnt/t7/smad_next/FZ1/release/` (see Data).
- 15:35 First equivalence check failed to load: the cached `pytorch_model.bin` is in OpenAI layout, not timm
  layout (bug 1). Fixed with timm's `checkpoint_filter_fn`.
- 15:38 Check, TF32 on: encoder tensors identical, score max |Δ| 4.7e-3 > 2e-3 tolerance (fails the prereg rule).
- 15:41 / 15:48 Check fp32 (max |Δ| 2.6e-3, still > 2e-3) and TF32 again with logit diagnostics.
- 15:52–15:59 Calibration control with the wrong channel order (RGB): max |Δ| 0.98. Decision: residual is
  cross-device arithmetic (reference run on H100 with TF32); continue; deviation recorded; all features fp32.
- 15:52 Feature run 1 (`run_feats.sh`); first launch failed on an unknown `--rgb` flag (bug 2), relaunched.
- 16:04–16:21 CLIP (MADation input) features for A43 (684 s) and StyleGAN3 (253 s). The machine was heavily
  loaded (load average 90–140, swap full), about 3–5 images/s.
- 16:22 Stage switch (`switch_stage2.sh`): killed run 1 after the StyleGAN3 file so that the other backbones'
  probe sets come before the long SMDD pass; started `run_feats2.sh` (one-pass orig + flip for SMDD added).
- 16:24 P2 probe for CLIP (MADation input) (`fz1_probe.py --run clip_mad --jobs 1`, about 90 s).
- 16:25 P4 (`fz1_stats.py`), after a smoke on 30 images per arm (8 is too few for nested CV, bug 4).
- 16:37–17:05 CLIP native, DINOv3, DINOv2 features; their probes by `run_probes_dino.sh`; aggregate at 17:05
  → `p2_probe.json`, `p2_probe.csv`.
- 17:05 CLIP eval-set features (8,267 images) started, fp32, about 17 s per batch of 64.
- 17:13 Micro-benchmark of fp32 against TF32 speed failed with CUDA out of memory (machine memory full); not
  retried. Decided to extract SMDD with TF32 for throughput (allowed by the prereg): `run_feats3.sh` waits for the
  eval file, stops the fp32 SMDD pass and runs SMDD orig + flip with TF32.
- 17:20 Author's documentation instruction received; this README written 17:31.
- 17:38 CLIP eval-set features written (8,267 × 768, 1,933 s, fp32). `run_feats3.sh` stopped the fp32 SMDD pass
  as planned.
- 17:41 Stage 3 died in its 8-image smoke: CUDA out of memory while moving the model to the GPU (machine memory
  full from other jobs; 31 GB available a minute later). Relaunched as `run_feats3b.sh` (same commands, up to 6
  tries per step, 90 s apart; tries logged in `logs/progress.txt`).
- 17:44 Stage 3b: smoke ok; the full pass failed once more with CUDA out of memory at model load (17:45), the
  second try ran from 17:48 at 12–23 s per batch of 64 (two forward passes each).
- 18:25 Diagnosis: the 4 loader workers were idle (0.3% CPU) while the main process waited on the shared GPU
  (96% busy, 14 processes), so the pass was GPU-bound, about 3 h left. Killed stage 3b at batch ~140/625 and
  restarted as two contiguous halves in parallel (`run_feats4.sh`, new `--part k/n` and `--workers` options in
  `fz1_feats.py`, merge by `merge_parts.py` with an id-order check against `train.csv`). 6 CPU processes,
  about 4.6 GB GPU memory in total. Smoke of the part path ok 18:27; both halves running from 18:28.
- 19:29 Both halves at batch 190 of 313 (13–25 s per batch, varying with the load); expected end about 20:00.
- 20:03–20:05 Both halves finished (try 1 each); merged into `feats/clip_mad/smdd.npz` and `smdd_flip.npz`
  (40,000 × 768 each; ids checked against `train.csv` order).
- 20:05 P3 smoke (`fz1_heads.py --smoke`, 1 seed, 2 epochs) found bug 5 (the prediction summary iterated over
  the `_release_head_on_our_features` entry); fixed, smoke rerun ok.
- 20:06–20:08 P3 full run (`OMP_NUM_THREADS=4 python -I src/FZ1/fz1_heads.py`, log `logs/p3_heads.log`) →
  `experiments/FZ1/p3_heads.json`, head weights `/mnt/t7/smad_next/FZ1/heads/head_s40{1..5}.pt`, A43 scores
  `heads/scores_a43.npz`. Prediction met in 5 of 5 seeds ("supported" under the registered rule).
- 20:15 `result.md` completed; README updated.

## 3. Data

Inputs (none modified, none generated):
- A43 MorDIFF material: manifest `/mnt/t7/smad_heldout/a43/data/manifests/a43.csv`, sha256
  ce3a264adb30928d6ae3abfb63619ed4b35fcb0ebb7fcca7e5001b212a5df4b8, 2,024 rows: A 200 published MorDIFF morphs,
  B 200 / B20 200 our same-pair DiffAE morphs (100 / 20 steps), C 102 / C20 102 same-person mixes (neutral +
  smiling of one person), D 204 / D20 204 one-photo reconstructions, E 204 genuine photos stored like the arms,
  plus eval rows R0 = `mordiff_bona` 204, `frll_bona` 204, A_reg = 200 published morphs in the registered
  frames. Images: 512 frames `/mnt/t7/smad_heldout/a43/data/a43/frames/<arm>/` and
  `/home/narolski/mambamorph-code/smadcvpr_data/eval/...`; stored small PNGs `a43/data/a43/stored/<arm>/`
  (used for PNG size in P4; sizes equal the manifest `file_bytes`, asserted).
- Eval manifest `/home/narolski/mambamorph-code/smadcvpr_data/manifests/eval.csv`, sha256
  86d055d349c63a225893ace30cb3db8b1e9aea4e72350d78152126d7a49d56c9. Used rows: R1 = `mordiff`/`resmatch` 204;
  FRLL-Morphs `amsl` 2,175, `facemorpher` 1,222, `opencv` 1,221, `webmorph` 1,221 (`orig`) with `frll_bona`
  `orig` 204 and each family's `resmatch` 204; MorDIFF `orig` 1,000 with `mordiff_bona` 204 and `resmatch` 204.
  Total 8,267 ids in the eval feature set. MAD22 rows of this file (old subset) never used.
- StyleGAN3: `/mnt/t7/smad_heldout/h3_sg3/data/manifests/h3sg3.csv` (sha 4b29a7c9…): `h3_sg3`/`orig` 423
  morphs, `h3_bona`/`orig` 423 one-identity renders; `/mnt/t7/smad_heldout/a37_sg3ctl/data/manifests/
  a37spread.csv` (sha 28bde1ef…): `orig` 423 spread-matched renders. 512 frames.
- SMDD (P3 training only): `/home/narolski/mambamorph-code/smadcvpr_data/manifests/train.csv` (sha
  b3d5f5f8…), rows with `source = smdd`: 25,000 bona fide `train/smdd/os25k_bf_t/`, 15,000 morphs
  `train/smdd/m15k_t/`, 256 × 256 PNG, all `val = 0`.
- Release scores: A43 `/mnt/t7/smad_heldout/a43/a43_out/a43/<net>/rel/scores_a43.npz` (`score_noTTA`;
  scored on H100 with TF32, bs 32); `/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12REL/<net>/
  scores_eval.npz`, `scores_h3sg3.npz`; `/mnt/t7/smad_heldout/a41g/a41g_out/x4/<net>/rel/scores_a37spread.npz`.
- MADation release: `/mnt/t7/wcss_backups/madation_official_upload/madation_official.tar` (sha c0048fc1…).
  Persistent copies made for this experiment (local use only, not for redistribution):
  `/mnt/t7/smad_next/FZ1/release/madation_fe_vitl14_model.safetensors` (sha 74dd7fbc…, equals convert.json
  output hash), `madation_fe_vitl14_convert.json`, `madation_fe_vitl14_training.log` (sha 1d1932f3…, equals the
  convert.json input hash).

Produced (all under `/mnt/t7/smad_next/FZ1/`):
- `feats/<backbone>/<set>.npz` (id, feat float32, meta json with weights, normalisation, tf32 flag, seconds).
  Done: clip_mad a43 (sha 7d056001…), sg3 (7bb18f7f…); clip_native a43 (db5641a0…), sg3 (bd22b178…); dinov3 a43
  (be616df1…), sg3 (27fe8fac…); dinov2 a43 (36b383c1…), sg3 (d8b00b8a…). In progress: clip_mad eval (fp32),
  clip_mad eval done 17:38 (fp32); clip_mad smdd + smdd_flip (TF32) in progress. `*_smoke.npz` = 8-image tests.
- `probe_raw_<backbone>.json` (out-of-fold probabilities for 6 contrasts × 5 fold seeds), `probe_oof.npz`,
  `probe_reps_a43.npz` (bootstrap replicates used by P4), `p4_stats_values.npz` (per-image statistics).
- `logs/` (every run), `p1.log`, `check_*.log`, `p1_tables.md`, `p2_tables.md`, `p4_tables.md`.
- Small results in `/home/narolski/smad-next/experiments/FZ1/`: `p1_release_reread.json` (78e442df…),
  `check_clip_vs_release_{fp32,tf32,tf32_run1,fp32_rgbcontrol}.json`, `p2_probe.json` (f50aa82d…),
  `p2_probe.csv`, `p4_stats.json` (f97fdbb1…). Pending: `p3_heads.json`.

Dropped items: none.

## 4. Code

`/home/narolski/smad-next/src/FZ1/`, all run with `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`.
- `fz1_common.py`: manifests (sha asserted), arm groups, person parsing, AD1's `wauc` and pigeonhole `Draw`
  (verbatim copy), weighted EER, neutral-above-smiling, paired flag change.
- `fz1_eval.py`: `Ctx` (bootstrap draws) and `evaluate(scores)` = all A43 contrasts, R0→R1 flag change at the
  MorDIFF EER threshold (full cell and 200-sample), neutral-above-smiling, benchmark EERs with intervals,
  StyleGAN3 contrasts. Used by P1 and P3, so releases and heads are read identically.
- `fz1_p1.py [--smoke]`: P1 re-read.
- `fz1_feats.py --backbone clip_mad|clip_native|dinov3|dinov2 --set a43,sg3,eval,smdd+flip [--smoke]
  [--no-tf32] [--bs 64]`; `--check [--no-tf32] [--rgb]` = equivalence check against the FE release. Images via
  the existing loader `mambamorph-code/smadcvpr/common.py` `ImageItems(res=224)` (sha ee71517a…; PIL bilinear,
  the only resize). Skips existing outputs.
- `fz1_probe.py --run <backbone> --jobs 1`, then `--aggregate`: P2 probes (StandardScaler + L2 logistic, C from
  {1e-3 … 10} by inner 3-fold grouped CV; outer 5 folds by host person (A43) or pair (StyleGAN3); fold seeds
  401–405, primary 401).
- `fz1_heads.py [--smoke]`: P3, MADation FE recipe on cached features, seeds 401–405, plus the end-to-end
  check of the released head on our features.
- `fz1_stats.py [--smoke]`: P4.
- `fz1_report.py p1|p2|p3|p4`: markdown tables.
- Runners: `run_feats.sh` (stage 1), `switch_stage2.sh` (stage switch; ran once at 16:22), `run_feats2.sh`
  (stage 2), `run_probes_dino.sh`, `run_feats3.sh` (stage 3, SMDD with TF32), `run_feats3b.sh` (stage 3 with
  retries), `run_feats4.sh` (stage 4, two parallel halves), `merge_parts.py` (joins the halves).
- `reviewer_preview/`: the reviewer's read-only preview scripts (copied from the session scratchpad).
Environment: Python 3.12.3, torch 2.12.1+cu130, timm 1.0.27, scikit-learn 1.9.0, numpy 1.26.4, scipy 1.17.1,
OpenCV 4.11.0, Pillow 12.2.0, safetensors 0.8.0. Weights (HF cache blob = sha256): CLIP
`timm/vit_large_patch14_clip_224.openai` `pytorch_model.bin` eb70c15b…, loaded with `weights_only=True` into
`vit_large_patch14_clip_quickgelu_224`; DINOv2 `vit_large_patch14_dinov2.lvd142m` 0424a5d1…; DINOv3
`vit_large_patch16_dinov3.lvd1689m` 45172f20…. Seeds: probes 401–405 (fold assignment), heads 401–405, bootstrap
seeds as AD1 / AG5.

## 5. Results

Full tables are in `result.md` (P1, P2, P4) and in the json files. Headlines with intervals:
- P1, released FE ViT-L/14: B20 vs D20 0.655 [0.580, 0.730], B vs D 0.852 [0.798, 0.902], C vs D 0.721
  [0.673, 0.769], C20 vs D20 0.498, B20 vs C20 0.653, D vs R0 0.459 [0.426, 0.492], D20 vs R0 0.561, E vs R0
  0.380, R1 vs R0 0.465, StyleGAN3 morph vs render 0.505, vs spread 0.475; R0→R1 flag rate 34.8% → 29.9%
  (−4.9 [−9.3, −0.5] points); neutral above smiling 0.343 [0.255, 0.431] (FRLL-Morphs genuine); EER native / E7:
  AMSL 21.6 / 23.0, FaceMorpher 3.9 / 4.4, OpenCV 4.4 / 4.9, WebMorph 9.8 / 10.3, MorDIFF 34.8 / 32.4.
- P2: see section 1; per-cell numbers in `result.md` and `p2_probe.json`.
- P4: see section 1; per-statistic numbers in `result.md` and `p4_stats.json`.
- P3: full per-seed tables in `result.md`; `p3_heads.json`. B vs D 0.789 [0.725, 0.850] to 0.792 [0.728,
  0.853]; D vs R0 0.508–0.512 (intervals about ±0.03); B20 vs D20 0.626–0.628; C vs D 0.667–0.671; C20 vs D20
  0.510–0.514; E vs R0 0.455–0.458; R1 vs R0 0.520–0.523; flag change R0→R1 0.0 to +1.5 points; neutral above
  smiling 0.588–0.608; EER native / E7: AMSL 22.5–23.5 / 28.0–28.4, FaceMorpher 4.4 / 4.9–5.4, OpenCV 4.8–4.9 /
  5.9–6.4, WebMorph 7.9–8.3 / 11.3–12.3, MorDIFF 40.2–40.7 / 40.7–41.2. Released FE head on our features
  reproduces every stored AUC within 2.7e-4.

## 6. Checks

Verified:
- Manifest hashes asserted in code (A43, eval). A43 R0 scores equal eval-file scores (max |Δ| 3e-8).
- P1 reproduces the reviewer preview to three decimals; my reader is AD1's verbatim (AD1 had reproduced A43).
- CLIP encoder equals the release's frozen encoder bit for bit (297 tensors). Released head on our features
  vs stored scores, 72 images: fp32 max |Δ score| 2.6e-3, mean 4.7e-4, Pearson 0.999997; TF32 4.7e-3 / 5.3e-4;
  wrong-channel control 0.98 / 0.37 / Pearson 0.42 (`check_clip_vs_release_*.json`). Why needed: to show that the
  features used for the probes and the new heads are the features the FE release reads.
- Head training code unit-tested on synthetic data (constant lr 0.01 as the release scheduler gives; loss falls).
- Every script run on 8 images (30 for P4) with its real command line first.
Not verified:
- The pre-registered 2e-3 tolerance itself (missed; see section 7).
- That our SMDD copy equals MADation's `smdd_train_cropped.csv` (39,730 images in its log against our 40,000;
  crops may differ).
- End-to-end check done in P3: released FE head on our fp32 features vs stored scores, all 2,024 A43 rows: max
  |Δ score| 9.2e-3, mean 4.6e-4; every A43 / StyleGAN3 AUC within 2.7e-4; benchmark EERs within 0.07 points.

## 7. Dead ends and failures

1. Bug 1, 15:35: `load_state_dict` on the cached CLIP `pytorch_model.bin` reported every key missing; the cache
   holds OpenAI layout. Fix: `timm.models.vision_transformer.checkpoint_filter_fn`.
2. Check (ii) missed the registered tolerance (2e-3) in both TF32 and fp32. Not a pipeline error by the
   calibration control; continued and recorded as deviation 1 in `result.md`. The lead may judge.
3. Bug 2, 15:52: `run_feats.sh` passed `--rgb` before argparse knew it; script exited; flag added, relaunched.
4. Process matching: `pgrep -f run_feats.sh` also matched the AF0 owner's `src/AF0/run_feats.sh`, and
   `pkill -f "<pattern>"` killed my own shell (its command line contained the pattern). Later scripts match
   `^/bin/bash /home/narolski/smad-next/src/FZ1/...` only. No other owner's process was touched.
5. Bug 4: the P4 smoke on 8 images per arm failed (empty folds, fewer groups than inner splits); guard added
   for empty folds and the smoke uses 30 per arm.
6. Throughput: the shared GB10 under load 90–140 gives 3–5 images/s for ViT-L at 224 in fp32; SMDD (80,000
   forward passes) would take hours. Stage 1 was killed after its StyleGAN3 file (planned), stage 2 will be killed
   after the eval file (planned) and SMDD done with TF32 in stage 3.
8. 17:41 stage 3 (`run_feats3.sh`) died with CUDA out of memory at model load (machine memory full); retried by
   `run_feats3b.sh`, whose full pass failed once more the same way (17:45) and then ran; killed 18:25 at batch
   ~140/625 (about 37 min of GPU work discarded) to restart as two parallel halves (`run_feats4.sh`).
7. 17:13 a fp32-vs-TF32 speed test died with CUDA out of memory (machine memory 106/121 GB used, swap full). Not
   retried; running extraction unaffected.
9. 20:05 bug 5 in `fz1_heads.py` (prediction summary read the check entry as a seed); fixed before the full run.

## 8. Observations and ideas

- Every frozen feature set separates the A43 arms almost perfectly (also same-person mix vs reconstruction,
  C20 vs D20 ≥ 0.991), so within A43 the arms differ in something easily linearly readable; the probe does not
  show that this is identity mixing. The central-crop Laplacian variance (0.966 for B vs D, morphs higher)
  points to a texture / noise difference between decoding from mixed latents and from an inverted latent at 100
  steps; at 20 steps it is much weaker (0.661) while the probe stays at 0.987.
- The released FE head's ordering (B vs D 0.852 > B20 vs D20 0.655) follows the statistics' ordering
  (100 steps stronger than 20), not the probe's (both near 1). Post hoc only.
- On StyleGAN3 the probe separates morphs from one-identity renders of a third person (0.89–0.94) but much less
  from renders matched in latent spread (0.58–0.63), as AG5 / A37 found for the detectors.
- FE ViT-B/16 flags E7 photos more often (39.7% → 69.6%) while FE ViT-L/14 does not (34.8% → 29.9%).

## 9. Open items and next steps

- None inside the registration. Lead's review pending.
- Not planned here (lead's call): probes trained on one arm pair and tested on another generator or step count;
  a probe on the central crop only.

## 10. Handover state (17:31 CET)

Nothing of FZ1 is running (checked 20:15). All feature files, probes, heads and logs are on the T7 drive
(`/mnt/t7/smad_next/FZ1/`); small results in this folder. The scratchpad copies of the release files are
duplicated in `/mnt/t7/smad_next/FZ1/release/`; the scratchpad is no longer needed.
Compute: about 3.5 GB10-hours of shared GPU time (all feature extraction, including about 0.6 h discarded when
stage 3b was killed), CPU minutes for P1, P2, P3, P4.
No WCSS, Athena or Vast use.

## 11. Reproduce from scratch

```
cd /home/narolski/smad-next
PY=/home/narolski/mambamorph-code/.venv-spark/bin/python
$PY -I src/FZ1/fz1_p1.py                                    # P1
$PY -I src/FZ1/fz1_feats.py --check --no-tf32               # equivalence check (also: without --no-tf32; with --rgb)
for bb in clip_mad clip_native dinov3 dinov2; do $PY -I src/FZ1/fz1_feats.py --backbone $bb --set a43,sg3 --no-tf32; done
$PY -I src/FZ1/fz1_feats.py --backbone clip_mad --set eval --no-tf32
$PY -I src/FZ1/fz1_feats.py --backbone clip_mad --set smdd+flip          # TF32 on (default)
for bb in clip_mad clip_native dinov3 dinov2; do OMP_NUM_THREADS=1 $PY -I src/FZ1/fz1_probe.py --run $bb --jobs 1; done
OMP_NUM_THREADS=1 $PY -I src/FZ1/fz1_probe.py --aggregate     # P2
OMP_NUM_THREADS=1 $PY -I src/FZ1/fz1_stats.py                 # P4 (needs the P2 aggregate)
OMP_NUM_THREADS=4 $PY -I src/FZ1/fz1_heads.py                 # P3
$PY -I src/FZ1/fz1_report.py all
```
