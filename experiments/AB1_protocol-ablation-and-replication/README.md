# Which part of the training protocol removes which shortcut, and does the result replicate (AB1): full record

## 1. Question and current answer

13 Nov 2026, 09:25. Status: registered (this commit); smoke job 6310091 pending on WCSS; 40-fit array going into the
dispatcher's queue; no fit run, nothing read.
Two questions. (a) Do the replacement storage test (contrast 2-prime, C2P) and contrast 1 (Sb above B on landmark
morphs) replicate on five new seeds (408-412) on WCSS H100? (b) Which part of the protocol (warp-only images, halves,
stored-small copies, matched splice negatives) carries which reduction (warp, softness, storage, seam / same-person
splice)? No answer yet. No arm is a method candidate.

## 2. Timeline

- 08:44 task received (lead). Read OWNER_BRIEF.md, NOTEBOOK.md, 17_MORNING_REPORT_20261113.md, the strategist report,
  PN1 prereg (terms, amendments 4, 10, Sp, C2P), FS1 v4 contrasts, SE1 and MS1 scripts.
- 08:46 dispatcher: Athena cannot carry the block (all A100 nodes reserved); plan for WCSS H100.
- 08:47 built manifests and overlay: `/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AB1/mk_ab1.py`
  (summary `/mnt/t7/smad_next/AB1/ab1_summary.json`).
- 08:48 found that SE1's registered array trains A and Sb at 408-412 with the same recipe on the same platform;
  proposed to reuse them (one network per arm and seed). Dispatcher noted it; lead approved via the dispatcher with
  conditions (say so in the registration before any fit; same platform and software build; follow SE1's platform;
  keep a rented fallback).
- 08:51 overlay uploaded to WCSS `packs/AB1/` (sha256 checked there: OK).
- 08:52 first local test failed with "adds: command not found": run.sh was edited while bash was executing it (an
  artefact of editing a running script, not a code bug). 08:53 re-run: 20 steps, 8 rows, rc 0, tar written (237 s).
- 08:58 scripts, rescore.py, rescore_tf32.py and the FS1 Sb s403 tar staged and uploaded to `packs/AB1/` (all sha256 OK).
- 08:59 smoke written to `/mnt/t7/smad_next/dispatch/submit_queue/wcss_ab1_smoke.cmd`. Pre-run review (Opus) started.
  Ten-line design summary sent to the lead.
- 09:03 dispatcher submitted the smoke as WCSS job 6310091 (pending; Slurm forecast start 18:30 at 09:10).
- 09:05 lead (via dispatcher): put the fit array in the queue at the registration commit, beside the smoke; outputs count
  only if the smoke passes.
- 09:15 pre-run review GO WITH FIXES (`PRERUN_AB1_20261113.md`, saved by the owner; the reviewer could not write).
  Fixes: SbH rebuilt keeping af0_half61 (overlay v2 171fdb21…, SbH b8e17cd2…, 3,831 unique, 7,200 rows); reader seed
  counting, seed-mean decider, provenance checks, training-row flags; pins hard-coded in the job files; disclosures.
  Mock reads: full (`ab1_read_mock.json`) and with two Sb seeds missing (`ab1_read_mock_drop2.json`, gives "not read").
  The first vectorised-AUC edit of the reader was lost because a `pkill -f` matched its own shell; the reader keeps
  c2p_read's AUC (a mock read takes about 2 min).
- 09:15 lead's decision (via dispatcher): SE1 moves to rented A100 PCIe machines; AB1 fits its own A and Sb on WCSS
  H100 and never reads SE1's networks. Array is now 40 tasks (`ab1_fit.sbatch` 186fd6bc…, limit 2:30).
- 09:20 uploaded to WCSS packs/AB1: ab1_overlay_v2.tar, run_v2.sh (cfa4ed26…), ab1_fit.sbatch, ab1_long.sbatch (all
  sha256 checked there). The v1 files (run.sh 893e856a…, ab1_overlay.tar 4e3afaa1…) stay for the smoke.
- 09:25 registration commit 61f7994 (pushed). Fit array file `wcss_ab1_fit.cmd` in the dispatcher's queue.
- 09:30 lead: the twice-as-long Sb arm (SbL) stays unsubmitted. The PR1 owner's registered training-row reading (not
  yet reviewed) is "same-person splices underfit with two-person splices fit (class weighting or identity); no
  longer-training arm without an author decision"; the lead puts it to the author.
- 09:34 dispatcher submitted the fit array as WCSS job 6310270_[0-39] (Nice 0). Forecasts at 09:34 (unreliable): smoke
  6310091 start 17:20; array none. The array counts only if the smoke passes (dispatcher cancels it otherwise).
- 09:35 dispatcher relayed the lead's rule: every network is scored on the GPU model and build it was trained on. AB1
  does this by construction (pn1_score.py inside each fit job). The smoke's FS1 Sb s403 rescoring measures the A100 to
  H100 difference and, as registered, decides nothing in AB1 (no AB1 number is compared with an A100 number).
- 09:36 amendment 1 (prereg): R1 relabelled "first test at seeds 408-412: passed / not passed / uninformative" (the
  FS1 C2P read was uninformative, review REVIEW_PN1_C2P_20261113.md F7/Q5); reader aacb11cd…. Confirmed for the lead:
  the 1,480 hold-out rows (ms1ffhq) are scored inside each fit job by pn1_score.py (all 21,277 rows of ab1_eval.csv,
  limit 0) with TF32 on (pn1_score.py lines 45-46), on the same H100 and build as the fit; every statistic of a network
  comes from its one scores_eval.npz, so no C2P statistic mixes scores from two jobs or platforms.
- 09:38 dispatcher: SE1's rented A100 fits started 09:35 and its WCSS jobs were cancelled; AB1's A and Sb are its own
  (array 6310270, WCSS H100), as registered. AB1's smoke 6310091 and array 6310270 are first in our WCSS order.

## 3. Data

- FS1 pack `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar` = WCSS `packs/BB2/pn1_pack_fs.tar`, sha256 96c31ae2… (unchanged).
- AB1 manifests `/mnt/t7/smad_next/AB1/manifests/`: train_SbZ 9b429554…, train_SbH b8e17cd2… (v2; v1 a64c8e0c… smoke only), train_SbS 9c7e43ff…,
  train_AS b7e9f3a3…, train_Sp cf386dc7… (copy of the registered PN1 Sp manifest), ab1_eval.csv 93a5ba23… (21,277 rows:
  FS1 pn1_eval 19,797 + MS1 hold-out 1,480). Row counts: prereg section 2.
- Overlay v2 `/mnt/t7/smad_next/AB1/ab1_overlay.tar` sha256 171fdb213444442762d4a716b7470dd885cd5879ba9ddda0c542060af4b4d149
  (copy on WCSS `packs/AB1/ab1_overlay_v2.tar`). v1 4e3afaa1… exists only on WCSS (`packs/AB1/ab1_overlay.tar`, smoke).
- Reference network for the platform measurement: `/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s403.tar` 8dec83b8… (copy on
  WCSS `packs/AB1/`).

## 4. Code (`src/AB1/`)

- `mk_ab1.py` manifests, eval manifest, overlay. `run.sh` one fit = one task (copy of src/SE1/run.sh, AB1 changes
  marked; sha256 893e856a… at upload). `wcss/ab1_smoke.sbatch` (7c6af62e…), `wcss/ab1_fit.sbatch` (64b319fc…, array 0-29),
  `wcss/ab1_long.sbatch` (0896814a…, conditional SbL, not submitted). `ab1_read.py` the single read. `ab1_platform.py`
  smoke platform measurement. `rented/drive_ab1.sh`, `rented/remote_ab1.sh` fallback (adapted from src/MS1/rented,
  syntax-checked only, not run).
- Environment on WCSS: `~/dmenv` (torch 2.11.0+cu128). DGX test: .venv-spark (torch 2.12.1+cu130), code path only.

## 5. Results

none yet.

## 6. Checks

- Local DGX code-path test of run.sh (SbH s408, 20 steps, 8 rows): rc 0; training set size 7,350 = the manifest.
  Log `/mnt/t7/smad_next/AB1/localtest/run.log`. The hold-out rows were not exercised by it (PN1_LIMIT takes the first
  rows); the WCSS smoke rescores the smoke network on all 1,480 hold-out rows.
- Not yet verified: H100 step rate, the reader on real tars, the rented fallback scripts.

## 7. Dead ends and failures

- 08:52 local test rc 127 caused by editing run.sh during its execution; re-run passed.

## 8. Observations and ideas

none yet.

## 9. Open items and next steps

Pre-run review, fixes, registration commit with pins; fit array to the dispatcher's queue; SE1 job IDs for A and Sb
(dispatcher will send); smoke result and platform numbers; fetch, two copies, single read; result.md; results review.

## 10. Handover state

- WCSS job 6310091 (smoke, owner AB1 owner, about 20 min once started; forecast 17:20). WCSS job 6310270_[0-39] (40
  fits, owner AB1 owner, about 1.2 h each, limit 2:30; expected end about 1.5-3 h after the array starts, depending on
  how many GPUs it gets). Logs: /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/ab1-{smoke,fit}-*.out. If the smoke
  fails: the dispatcher cancels 6310270, the owner fixes and re-queues. Fetch: `bash src/AB1/fetch_ab1.sh smoke|fits`. Compute used: about 0.1 DGX
  GPU-hours (local test). The local test work folder was deleted (owner's own file).

## 11. Reproduce from scratch

See prereg section 10.
