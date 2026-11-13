# Second backbone for the protocol recipe (BB2): full record

Owner: BB2 owner (Claude agent), DGX and WCSS. Started 12 Nov 2026, 23:30 CET. Follows
`/home/narolski/smad-next/DOCUMENTATION.md`. Registration: `prereg.md` (this folder). Short verdict: `result.md`.
Code: `/home/narolski/smad-next/src/BB2/`. Large outputs: `/mnt/t7/smad_next/BB2/`.

## 1. Question and current answer

Does the pattern that the protocol network (PN1) fresh seeds (FS1) show on CLIP ViT-B/16 repeat when the same three
arms (A plain recipe, B protocol negatives, Sb protocol + face-spliced morphs with matched negatives) are trained with
the same data, lists, seeds 403-405 and development reads on a second backbone? Backbone: DINOv3 ViT-L/16 (no ViT-B
DINO weights exist on disk; prereg section 2). Status 12 Nov 2026 23:52: code, CPU equivalence test, reader and draft
registration written; DGX smoke running; draft goes to the independent pre-run review. No fit submitted. No answer yet.

## 2. Timeline (CET, machine clock)

- 12 Nov 23:30 Read OWNER_BRIEF.md, DOCUMENTATION.md, NOTEBOOK.md (12 Nov), PN1 README / prereg (arms, amendment 4,
  FS1, D1-D3, R1-R6), prereg_fresh_seeds_v4_frozen.md, BENCHMARK_EXPOSURE.md (not re-read in full), src/PN1/run.sh, the
  pack code (train.py, archs_a12.py, common.py LoRA, pn1_score.py), FINAL prereg (robustness row), PRERUN_PN1_REMEDIES,
  A49 records, MS1 prereg part 2 and src/MS1/wcss/.
- 23:31-23:36 Weight search. DGX: DINOv3 ViT-L/16 (timm and HF), DINOv2 ViT-L/14, DINOv2 ViT-S/14; no ViT-B DINO.
  WCSS (one ssh, `find ~ /lustre/pd03/hpc-narolski-1790461090 -maxdepth 7 -name "models--*"`): no DINO cache found;
  `~/dmenv`: timm 1.0.30, torch 2.11.0+cu128, transformers 5.19.0. Decision DINOv3 ViT-L/16 sent to the lead 23:36.
- 23:37 Checked timm Eva (DINOv3): fused `attn.qkv` Linear(1024, 3072) without bias, so `LoRAQKV` applies; no absolute
  position embedding (RoPE); `global_pool="token"` = CLS after the final norm.
- 23:38 `src/BB2/archs_a12.py` (pinned `bedfeb86…` + new entry `a12_dinov3_vitl16_madation` and class
  `DINOv3MADation`). CPU build: weights from the overlay path, 318 of 318 tensors equal the file; LoRA 24 blocks,
  trainable 197,633.
- 23:39-23:47 CPU equivalence test of the CLIP path (`test_clip_identical.sh`): arm B 3 steps batch 8, arm Sb 5 steps
  batch 8. First comparison run flagged only the tree path in `meta.json["arch_extra"]["weights"]` and `train_hours`;
  comparator fixed to drop wall-clock keys and normalise the two tree paths (no change to what is trained); both PASS.
- 23:42 GPU memory measurement on the DGX (bs 16 and 32, train mode, LoRA): CLIP ViT-B/16 3.79 GB per 32 images,
  DINOv3 ViT-L/16 8.61 GB per 32 images -> about 70 GB at batch 256.
- 23:44 overlay built (`build_overlay.sh`), sha256 `7c0a0b41…`. 23:44:46 DGX smoke started (run.sh, arm Sb seed 403, 20
  steps, 64 scoring rows, batch 64 x 4 accumulation to keep DGX memory modest and to exercise the fallback path).
- 23:47 upload of the FS1 pack and the overlay to WCSS `.../smad-next/packs/BB2/` started (rsync under the lock).
  A WCSS check at 23:4x found the Slurm controller unreachable ("Unable to contact slurm controller").
- 23:50 `bb2_read.py` written; mock test (random logits in mock tars, a fake FS1 reading) runs end to end.
- 23:48-23:52 draft `prereg.md`, this README, `result.md`. Commit 05a8e25 (pushed): code, draft, test outputs.
- 23:52:47 upload of `pn1_pack_fs.tar` and `bb2_overlay.tar` to WCSS `packs/BB2/` finished (rsync rc 0, about 5 min).
- 23:53 DGX smoke passed: run.sh rc 0, wall 498 s (pack copy and check 86 s, overlay 10 s, 20 steps at batch 64 x 4 in
  459 s on the shared GB10, scoring 64 + 64 rows); tar `/mnt/t7/smad_next/BB2/dgxsmoke/results/BB2smoke_Sb_s403.tar`
  (sha256 `ce0ed1e0…`) holds last_trainable.pt (98 tensors = the trainable set; 48 of 48 LoRA B matrices moved from
  zero), meta.json, train.log, scores, env.txt, gpu.txt, task_info.txt. Rebuild check: `common.build_run_model(meta)` +
  `last_trainable.pt` loads with no missing trainable key (the path the sealed read will use). Work folder deleted.
- 23:54 independent pre-run review started (experiment-reviewer, given the files, not conclusions). Draft path sent to
  the lead.
- 23:55 run.sh (`0eaa4dce…`) and the smoke script uploaded to WCSS for the WCSS smoke (not a fit; it only decides the
  batch rule of section 4 of the prereg).
- 13 Nov 00:00 pre-run review back: GO WITH FIXES (`experiments/reviews/PRERUN_BB2_20261113.md`). Applied (prereg
  section 12): DINOv3 history disclosed (the Sb idea came from a frozen DINOv3 head read on MAD22); fit script takes
  batch and time from the command line and refuses other batch settings (tested locally: refuses '/', '256/2'); memory
  rule with a 72 GiB peak bound, both batch modes run in the smoke; OOM/timeout rerun rule; reader read-seed rule now
  includes non-finite train.log losses; training-adequacy control (own-rule training accuracy >= 0.75 per arm) for
  contrasts 1 and 3; contrast 2 not read with < 2 seeds; `featcheck.py` platform check (DGX CPU reference
  `featref_cpu.npz` 89f3defe…, repeat on CPU max diff 0.0; the DGX GPU was out of memory (other users) so the reference
  is CPU fp32). Reader re-run on mock tars. Not applied: seeds 406/407 (lead/author decision).
- 00:05 registration commit (this commit; `date` Fri Nov 13 12:05:19 AM CET 2026).
- 00:06 uploaded to WCSS `packs/BB2/`: featcheck.py, featref_cpu.npz, bb2_smoke.sbatch, bb2_fit.sbatch with .sha256
  files; all hashes checked on WCSS (pack, overlay, run.sh, featcheck, reference, both sbatch: OK).
- 00:07:20 smoke sbatch refused: "Unable to contact slurm controller (connect failure)". 00:15:10 the one allowed
  retry refused the same way (squeue also could not reach the controller). Stopped and reported to the lead. Nothing
  of BB2 is queued or running on WCSS.
- 00:47 the lead submitted the smoke with the registered command after the controller came back: **WCSS job 6308946
  (bb2-smoke), PENDING, priority 682; owner BB2 owner; workload: the smoke of prereg section 9 (complete on WCSS,
  hash-checked); expected run about 30-45 min once started.** Slurm's forecast for our other WCSS jobs: 15 Nov 01:00,
  after the experiment stage ends, so WCSS may not deliver BB2 in time. Lead: no polling; one check at about 09:00.
- 00:50 rented variant prepared for the author's 09:00 decision (nothing rented): `src/BB2/rented/RUNBOOK.md`
  (what the registration allows: platform deviation needed for any rental; 80 GB cards keep the registered memory
  rule; 48 GB cards fall to the registered 128 x 2 without amendment; 40 GB cards would need an amendment), layouts,
  wall time and cost for 1-3 machines, keep rule), `remote_bb2.sh`, `drive_bb2.sh` (HOST PORT LEASE placeholders);
  queue rerun logic tested with a stand-in run.sh.

- 13 Nov 03:12-03:17 WCSS smoke job 6308946 ran on r18-11 (NVIDIA H100, 95,830 MiB, GPU-25f4d639…; torch 2.11.0+cu128,
  timm 1.0.30): 256 x 1: rc 0, 100 steps at 1.12 it/s, loss 0.6881 at step 100, peak memory.used 69,225 MiB; feature
  check max |diff| 6.8e-7 against the DGX CPU reference (tolerance 1e-3), rc 0; 128 x 2: rc 0, 1.18 it/s, peak 35,627
  MiB. Outputs fetched to `/mnt/t7/smad_next/BB2/smoke_wcss/` (both tars sha256 OK; log, memory logs, features).
- 08:30 **rules applied (prereg section 4 and 9):** memory rule -> batch 256 in one pass (69,225 ≤ 73,728 MiB);
  projected fit time 6,250 / 1.12 it/s = 1.55 h + about 0.15 h pack copy and scoring = 1.7 h; time limit 1.5 x 1.7 h +
  0.5 h = 3.05 h -> `--time=0-03:03:00`.
- 08:30:14 fit sbatch refused ("Unable to contact slurm controller"); 08:35:53 the one retry refused the same way.
  Reported to the lead. The lead put the exact command into the dispatcher's queue
  (`/mnt/t7/smad_next/dispatch/submit_queue/wcss_bb2_fits.cmd`); the dispatcher submits it when the controller
  answers and raises the array throttle from 5 to 9 (lead's operational decision: WCSS has about 20 idle H100 nodes;
  prereg section 9 said at most 5 GPUs at once; every fit still runs alone on one GPU, so no fit changes). Job ID: to
  be recorded when the dispatcher reports it.
- 08:40 amendment 1 drafted (C2P reads on the MS1 FFHQ hold-out with 3-seed counting via `bb2_c2p_read.py` and the
  rescoring job `wcss/bb2_c2p.sbatch`; S3 printed reads; room for a seam-shortcut arm); mock test of the reader passed;
  rescore.py on the BB2 smoke network matched its WCSS logits on shared af0 rows within 5.2e-5. Draft commit ddf8b0b;
  pre-run review (Opus) started.

- 08:45-08:53 amendment 1 fixes applied (c092af5), amendment 2 drafted and checked (review
  `experiments/reviews/PRERUN_BB2_A2_20261113.md`, GO WITH FIXES); fixes 1-6 applied; amendments 1 and 2 registered
  (prereg sections "Amendment 2 pre-run check" and "Registration of amendments 1 and 2"). Diffs:

```
$ diff src/BB2/run.sh src/BB2/run_s5.sh
1a2
> # BB2 amendment 2: run.sh (0eaa4dce...) with seeds 406 and 407 added to the seed list; nothing else changed.
42c43
< case "$SEED" in 403|404|405) ;; *) die "seed $SEED" ;; esac
---
> case "$SEED" in 403|404|405|406|407) ;; *) die "seed $SEED" ;; esac                      # BB2 amendment 2: seeds 406, 407
$ diff src/BB2/wcss/bb2_fit.sbatch src/BB2/wcss/bb2_fit2.sbatch
3c3
< #SBATCH -J bb2-fit
---
> #SBATCH -J bb2-fit2
10,13c10,13
< #SBATCH --array=0-8%5
< #SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-fit-%A_%a.out
< # Second backbone (BB2), prereg sections 4 and 9: nine fits (arms A, B, Sb at seeds 403, 404, 405), one per array task,
< # seed by seed, at most 5 GPUs at once; src/BB2/run.sh (sha256 in run.sh.sha256) on the FS1 pack + BB2 overlay (both
---
> #SBATCH --array=0-5%6
> #SBATCH -o /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-fit2-%A_%a.out
> # Second backbone (BB2), amendment 2: six fits (arms A, B, Sb at seeds 406, 407), one per array task,
> # seed by seed, at most 6 GPUs at once; src/BB2/run_s5.sh (sha256 in run_s5.sh.sha256) on the FS1 pack + BB2 overlay (both
23,24c23,24
< ARMS=(A B Sb A B Sb A B Sb)
< SEEDS=(403 403 403 404 404 404 405 405 405)
---
> ARMS=(A B Sb A B Sb)
> SEEDS=(406 406 406 407 407 407)
28c28
< (cd "$P" && sha256sum -c --quiet run.sh.sha256)
---
> (cd "$P" && sha256sum -c --quiet run_s5.sh.sha256)
35c35
<   BB2_BS=$BB2_BS BB2_ACCUM=$BB2_ACCUM PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run.sh"
---
>   BB2_BS=$BB2_BS BB2_ACCUM=$BB2_ACCUM PN1_LOCAL=1 PN1_PY=$HOME/dmenv/bin/python PN1_WORKERS=7 bash "$P/run_s5.sh"
```

- 08:56 queued for the dispatcher: `wcss_bb2_fits2.cmd` (six fits, amendment 2) beside `wcss_bb2_fits.cmd` and
  `wcss_bb2_c2psmoke.cmd`. Lead 09:0x: no lower GPU cap; up to 15 H100s at once for BB2 is accepted (author's order to
  fill idle nodes). WCSS controller still refusing commands; job IDs to follow from the dispatcher.

- 09:03 submitted by the dispatcher (owner: BB2 owner): **6310084** bb2-fit (nine fits, array 0-8, throttle 9),
  **6310092** bb2-fit2 (six fits, seeds 406/407, array 0-5%6), **6310085** bb2-c2psmoke (C2P job smoke). All PENDING
  (Priority); Slurm forecast start of 6310084: 13 Nov 16:14; expected end of each fit 1.7 h after its start (about
  18:00 for the first wave if the forecast holds; limit 3:03). GPU-hours: 15 fits x 1.7 h ≈ 25.5 H100-h + smoke 0.3 +
  C2P job ≈ 0.5. Next check at the forecast start (16:15), then at start + 1.7 h; fetch with `src/BB2/fetch_bb2.sh`.

- 09:07 dispatcher (operational deviation, recorded): time limit of 6310084 and 6310092 lowered from 3:03 (prereg
  rule 1.5 x projected + 0.5 h) to 2:15 (projected 1.65 h + about 30%) to help backfill; Nice=10 on all BB2 jobs. A
  fit that reaches the limit is an infrastructure failure: rerun once with twice the time (prereg section 4).
  Forecast start 18:10 (unreliable).

- 09:4x amendment 3 registered (fda35f4) after its pre-run check (`experiments/reviews/PRERUN_BB2_A3_20261113.md`);
  probe and amended C2P job uploaded and hash-checked on WCSS; dispatcher asked to cancel 6310085 and submit the
  replacement smoke `wcss_bb2_c2psmoke2.cmd`. Lead: fits stay queued; the CLIP branch stays as registered ("passes" ->
  repeat sentences; any other verdict -> "No CLIP effect to repeat; printed only"); no further change.

- 10:04 dispatcher: 6310085 cancelled (never ran); amended C2P smoke submitted as **6310376** (bb2-c2psmoke2, Nice 10,
  output `results/BB2_smoke/BB2C2Psmoke2.tar`, about 15-20 min once started). Fits 6310084 / 6310092 pending,
  forecast 17:10 (unreliable).

- 11:51-11:54 fits started (dispatcher): 6310084_[0-8] all nine running from 11:51:20 to 11:54:22; 6310092_0 and _1
  running from 11:54:22, _[2-5] pending (forecast 13:01); C2P smoke 6310376 pending. Expected ends about 13:30-13:35
  (1.65 h), limit 14:06-14:09.

- 12:12 step-rate check (logs on WCSS): 12 fits running (6310084_[0-8], 6310092_[0-2]); steps 900-1300 of 6,250;
  rates 0.97-1.19 it/s (the slowest at 0.97-1.01: 6310084_0, _3, _6, 6310092_0; 6,250 steps at 0.97 it/s = 1.79 h +
  about 0.1 h copy and scoring = 1.9 h, inside the 2:15 limit with about 20 min to spare). Expected ends 13:30-13:50
  for the nine; fetch planned at 13:55.

- 13:24 dispatcher: seven fits COMPLETED (exit 0, 1:29:31-1:30:25 each). 13:24:51 first fetch (`fetch_bb2.sh`): 8 tars
  verified (local = .sha256 = WCSS sha256): B 403-406, Sb 403-406 (see `/mnt/t7/smad_next/BB2/results/fetch.log`).
  Not opened: no reader runs before the seed mode is frozen (amendment 2).

- 13:56 second fetch: 12 of 15 tars verified (A, B, Sb at 403-406). Seed 407 (6310092_3-5) running at 13:57: steps
  1,100-1,400 at 0.97-1.19 it/s; expected ends about 15:15-15:30; next fetch 15:35. Squeue refused (controller); logs
  read directly. No tar opened.

- 14:10-14:12 C2P smoke 6310376 (Nice 0, limit 40 min, node r14-7, NVIDIA H100 GPU-c91bbdc6…) ran, exit 0, 1:54.
  Fetched `/mnt/t7/smad_next/BB2/smoke_wcss/BB2C2Psmoke2.tar` (sha256 OK). PASS: probe gpu_ok "NVIDIA H100"; torch
  2.11.0+cu128; matmul and cuDNN conv fp32_precision "tf32", matmul and conv relative error vs fp64 2.9e-4 / 3.0e-4 (TF32
  in effect; legacy flags not remapped away); wrapper and rescore.py sha256 at their pins in env.txt; 6 of 6 family
  files finite (af0 1,339, ffhq 5,000, ms1ffhq 1,480 per network); on the 21 rows also scored in the fits, the
  rescored logits equal the fits' pn1_score.py logits bit for bit (max |Δ| 0.0). Smoke networks only; never read as a
  result.

## 3. Data

- FS1 development pack `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar` sha256 `96c31ae2…` (unchanged; arms' manifests and the
  evaluation manifest inside; see prereg section 3). Unpacked tree used by the tests: `/mnt/t7/smad_next/PN1/fs_tree/`.
- DINOv3 weights: `~/.cache/huggingface/hub/models--timm--vit_large_patch16_dinov3.lvd1689m/snapshots/30c1109559f65dea34316b0d4842d35c5771fe11/model.safetensors`
  sha256 `45172f20…`, copied into the overlay as `pn1/hf/a12/vit_large_patch16_dinov3.lvd1689m.safetensors`.
- Overlay `/mnt/t7/smad_next/BB2/bb2_overlay.tar` sha256 `7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad`
  (BB2SUMS, archs_a12.py, weights).
- Local test trees: `/mnt/t7/smad_next/BB2/pinned/pn1` (real-file copy of the FS1 code, checked against the pack's
  SHA256SUMS), `/mnt/t7/smad_next/BB2/tree/pn1` (same + BB2 archs_a12.py + weights). Data and hf are symlinks into the
  FS1 tree.
- WCSS: `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/BB2/` (upload in progress).

## 4. Code (`/home/narolski/smad-next/src/BB2/`; DGX Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`, torch 2.12.1+cu130, timm 1.0.27)

| File | Job |
|---|---|
| `archs_a12.py` | pinned archs_a12.py + DINOv3 entry (only reached through the new arch name) |
| `build_overlay.sh` | builds `bb2_overlay.tar` (deterministic) |
| `run.sh` | one fit = one task: FS1 pack + overlay (both hash-checked), unchanged train.py with the FS1 flags and `--arch a12_dinov3_vitl16_madation`, unchanged pn1_score.py, one result tar |
| `test_clip_identical.sh` | CPU proof that the CLIP path is unchanged (pinned tree against BB2 tree) |
| `bb2_read.py` | registered reader (imports fs_read.py unchanged); `--mock DIR` test |
| `wcss/bb2_smoke.sbatch` | WCSS smoke, decides the batch rule |
| `wcss/bb2_fit.sbatch` | nine fits, array `0-8%5` (`__BS__`/`__ACCUM__` filled from the smoke's rule before upload) |

## 5. Results

None yet.

## 6. Checks

- CLIP path unchanged: `clip_identical_B.json`, `clip_identical_Sb.json` (PASS; 203 tensors equal; logits bit-equal).
- DINOv3 weights load exactly (318 / 318 tensors equal).
- Reader mock test: `bb2_mock.json` (random logits; no real score).
- Not verified: timm 1.0.30 (WCSS) against 1.0.27 (DGX) DINOv3 outputs; the WCSS smoke runs the WCSS version.

## 7. Dead ends and failures

- First CPU comparison reported PASS false only because of the tree path and wall-clock; comparator fixed (section 2).
- Local test tree built first with symlinked code files: `common.py` resolved its own folder to the AD4 tree and would
  have imported the pinned archs_a12.py; rebuilt with real-file copies before any test.

## 8. Observations and ideas

- DINOv3 timm default input is 256; BB2 keeps 224 (the CLIP arm's pixels).

## 9. Open items and next steps

DGX smoke result; pre-run review; registration commit; WCSS smoke; fit submission; fetch; read; post-result review.

## 10. Handover state (13 Nov 09:05)

- WCSS jobs (owner BB2 owner): 6310084 (9 fits), 6310092 (6 fits), 6310376 (C2P smoke, amended; 6310085 cancelled); all PENDING; forecast start
  16:14; logs `/lustre/pd03/hpc-narolski-1790461090/smad-next/logs/bb2-fit-6310084_<i>.out`, `bb2-fit2-6310092_<i>.out`,
  `bb2-c2psmoke` -> `bb2-c2p-6310085.out`; results `.../results/BB2/` and `.../results/BB2_smoke/BB2C2Psmoke.tar`.
- After the fits: `bash src/BB2/fetch_bb2.sh` at each end; then `python3 -I src/BB2/freeze_mode.py` and commit
  `seed_mode.json`; then queue the C2P job with `BB2_TASKS` = the frozen read set (15 or 9 tasks) and the default
  output; then run `bb2_read.py` and `bb2_c2p_read.py --c2p .../BB2C2P.tar` once each; results-reviewer.
- If a fit fails: non-finite -> never rerun; out of memory or time limit -> rerun once at 128 x 2 with twice the time
  (`BB2_TASKS="<index>"`, array `0-0`), labelled; other infrastructure failure -> rerun once unchanged.
- Nothing runs on the DGX for BB2.

## 11. Reproduce from scratch

```
src/BB2/build_overlay.sh /mnt/t7/smad_next/BB2
src/BB2/test_clip_identical.sh /mnt/t7/smad_next/BB2/test_clip B 3 8
src/BB2/test_clip_identical.sh /mnt/t7/smad_next/BB2/test_clip_Sb Sb 5 8
python3 -I src/BB2/bb2_read.py --mock /mnt/t7/smad_next/BB2/mock
# WCSS: upload packs/BB2 (FS1 pack, overlay, run.sh + run.sh.sha256, sbatch files), then
/opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR bb2_smoke.sbatch ; ... bb2_fit.sbatch
python3 -I src/BB2/bb2_read.py
```
