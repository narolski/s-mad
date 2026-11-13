# Which part of the training protocol removes which shortcut, and does the result replicate (AB1): full record

## 1. Question and current answer

13 Nov 2026, 14:45. Status: finished; read once as registered and reviewed (`result.md`, `REVIEW_AB1_20261113.md`).
Two questions, on 40 CLIP ViT-B/16 LoRA networks (8 arms × seeds 408-412, WCSS H100, development data only):
(a) Replication: contrast 1 (Sb above B on FFHQ landmark morphs) replicates on 5 of 5 seeds, but Sb is not shown to
exceed the best single statistic; the replacement storage test, read for the first time on these seeds, is inconclusive
for Sb (passes at the trained size on 5 of 5, at 112.7 px on 3 of 5, failing only a two-sided mean bar while its flag
rise is 0) and for B. (b) Mechanism: the storage reduction is spread across components (without stored-small copies Sb
fails the bars at the trained size but keeps only 20-38% of the plain arm's reaction; stored copies alone do not
suffice); the matched splice negatives keep same-person splices down (0.36-0.41 against 0.70-0.74 without them); the
warp-only and seam-only reads sit at the floor; the native halves are not needed given their stored copies. No arm is a
method candidate.

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
  Mock reads: full (`ab1_read_mock.json`) and with two Sb seeds missing (`ab1_read_mock_drop2.json`, gives "not read"; later replaced, see 10:40).
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
- 10:08 on the lead's instruction, read the PN1 Sp arm at 403-405 once under its own registration (verdict falsified;
  PN1 result.md, review REVIEW_PN1_SP_20261113.md applied); dated note in this prereg.
- 10:40-10:55 amendment 2 (lead's instruction): H-sp1, H-sp2, H-sp3 (+ threshold-free H-sp3b) for Sp against Sb at
  408-412, disclosed as set after seeing 403-405; pre-run check GO WITH FIXES (PRERUN_AB1_AMEND2_20261113.md), fixes
  applied; H-ab4 code compares counts (inclusive margins), text unchanged. Reader fb990bb5…; mocks: full
  (ab1_read_mock.json) and one Sb seed missing (ab1_read_mock_drop1.json, n = 4 path); the older drop-two mock, which
  predated amendment 2, was replaced.
- 11:48-11:50 smoke 6310091 ran on WCSS r18-1 (H100, GPU-b5bc6200…), exit 0, 2 min 23 s: all hash checks OK; pack and
  overlay v1 unpacked; 100 training steps in 111 s (2.62 it/s; a full fit is about 40 min of training plus about 3 min
  of pack copy and scoring); scoring and copy-back done; rescoring of FS1 Sb s403 on 6,339 gate rows and of the smoke
  network on the 1,480 hold-out rows done (all finite). Fetched and verified to /mnt/t7/smad_next/AB1/smoke/.
  Platform measurement (descriptive, decides nothing): FS1 Sb s403 A100 PCIe stored logits against H100 rescoring,
  p99 |Δlogit| 0.0047, max 0.026, own-rule agreement 1.000 (`smoke_platform.json`). Smoke verdict: PASS, sent to the
  dispatcher at 11:55; array 6310270 stays.
- 12:00 dispatcher lowered the array's limit from 2:30 to 1:15 (expected 43-45 min per fit; about 1.7x margin).
- 12:29-12:34 tasks 6310270_[0-8] started (seed 408 all eight arms, seed 409 arm A); _[9-39] pending, forecast 13:06.
  First ends expected about 13:15.
- 13:14-14:22 all 40 fits COMPLETED, exit 0 (35-36 min; A and AS 45-55 min; WCSS outage about 13:30-13:55 without
  failures). All 40 tars fetched and verified (T7 drive and Lustre).
- 14:26 first read run crashed while loading training scores (KeyError 'id'; scores_train.npz has path/kind), before any
  statistic: deviation D1 in prereg; reader fixed (74ecdf7a…, also checks manifest hashes). 14:31 read once.
  Verdicts and numbers in result.md.
- 14:38 results review (Opus): every number and verdict reproduces; corrections F1-F9 applied to result.md (storage
  spread across components; H-ab2 floor-limited, H-ab3 not; "not shown to exceed" the floor; S3 reduction is about the
  training fit; H-sp1 shrinkage; SbH repeats confound; Δm toward genuine). Reviewer's scripts kept in src/AB1/review/,
  output review_recompute.json; review text REVIEW_AB1_20261113.md.
- 15:00 Note 2 registered (5455c42) before computing; sharpness of flipped persons: A and SbS not enriched, AS
  inconclusive (ab1_sharp.json); short review (Opus) confirmed every number, wording applied; reviewer's script
  src/AB1/review/sharp_recompute.py.
- 15:10 follow-up batch B2 drafted for the author (prereg_b2_draft.md): SbR, SbH61, SbSp, SbnS0, SbnS3 (25 fits,
  ab1b2_fit.sbatch, run_b2.sh, overlay /mnt/t7/smad_next/AB1/b2/ab1b2_overlay.tar d2038b98…) + SbL (5 fits,
  ab1_long.sbatch); about 23-27 H100-hours; nothing uploaded or submitted.
- 15:20 lead: go for B2 without SbL (author's standing instruction for today; SbL stays with the author). Draft renamed
  prereg_b2.md; reader src/AB1/ab1b2_read.py written and mock-tested (full; two seeds dropped; real AB1 loading path with
  no B2 tar). Pre-run check GO WITH FIXES (PRERUN_AB1B2_20261113.md), all fixes applied; pins in pins_b2.sha256.
  run_b2.sh differs from run.sh v2 only in: header comment; OVERLAY path ab1b2_overlay.tar and pin d2038b98…; SUMS file
  AB1B2SUMS; arm list SbH61|SbSp|SbnS0|SbnS3|SbR (SbL line removed); results folder results/AB1B2. 25 fits, about
  15 H100-hours.
- 15:45 registration commit 324b4fa; B2 files uploaded to packs/AB1 (hashes verified); queue file wcss_ab1b2_fit.cmd;
  dispatcher submitted WCSS array 6313020_[0-24] (limit 1:15, owner AB1 owner, about 36 min per fit; expected end
  about 1.5 h after start). Read with src/AB1/ab1b2_read.py after fetching to /mnt/t7/smad_next/AB1/b2/results
  (fetch: rsync of results/AB1B2, as fetch_ab1.sh). Local staging folders removed.

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

### Border-crossed arm Sbx (13 Nov evening)
- 17:55 lead's instruction (strategist evening synthesis, item 5). Built with src/AB1/mk_ab1x.py: 1,385 border-blanked
  training copies (25% of every kind; masks from TT1 U_p frames not used by any TT1 border reference), 3,582 border
  evaluation rows (development persons, FFHQ HN2); overlay /mnt/t7/smad_next/AB1/x/ab1x_overlay.tar e5886e72… (also on
  WCSS packs/AB1). Local 20-step test passed (10,484 items). Pre-run check GO WITH FIXES (PRERUN_AB1X_20261113.md),
  fixes applied; registration prereg_x.md at 7e4a974; pins in pins_x.sha256.
- Submitted by the dispatcher: wcss_ab1x_fit.6314811.cmd / wcss_ab1x_rescore.6314812.cmd
  (fit array: 5 fits, limit 1:15, results/AB1X; rescore job: Sb/B on border rows, results/AB1X/AB1Xrescore.tar).
  Read with src/AB1/ab1x_read.py when both have ended, latest 15 Nov 18:00. Local test folder
  /mnt/t7/smad_next/AB1/localtest_x holds only the 20-step test tar and log.

### Second-engine arm SbFM (13 Nov evening; strategist's TD1, author's go)
- 18:50 lead's instruction. Built with src/AB1/mk_ab1fm.py: Sb's 8,386 rows unchanged + a self-balanced block of
  FaceMorpher ladder rows of training hosts (R4fm 124, R2wfm 156, R2w4fm 124; 560 rows, half attacks); no FaceMorpher
  splices (no seam in their negatives), no partner-side half (does not exist), no ladder stored copies (as Sb).
  Evaluation manifest ab1x_eval.csv with the border rows. Overlay /mnt/t7/smad_next/AB1/fm/ab1fm_overlay.tar 681525d8…
  (WCSS packs/AB1). Hypotheses: H-fm1 landmark_combined +0.02 / +0.005 (primary), H-fm2 test FaceMorpher R4 vs R2w,
  H-fm3 OpenCV guard; printed engine-crossed table, storage, S3, R3, border, engine-prior diagnostic.
- Dead end: a first build re-balanced the whole manifest (FaceMorpher attack share 0.594, Sb's repetition changed);
  replaced before registration (pre-run check F2). A loading-path test of the reader on real AB1 tars wrote a scratch
  JSON with the H-fm2/H-fm3 baselines; deleted unopened at 18:42 (F1).
- Pre-run check GO WITH FIXES (PRERUN_AB1FM_20261113.md), fixes applied; registration prereg_fm.md; pins pins_fm.sha256.
- Submitted by the dispatcher as WCSS job 6315597_[0-4] (limit 1:15, results/AB1FM); read with src/AB1/ab1fm_read.py when the 5 fits end, latest 15 Nov 18:00.
- Note on times (Fri Nov 13 18:48 CET 2026): the lead's message times quoted above as "17:55" (Sbx instruction) and "18:50" (SbFM instruction) are not machine-clock times (lead's correction, NOTEBOOK 18:46): SbFM's instruction arrived between 18:32 and 18:46; the author's cut-off ruling ("17:15") was committed at about 17:11. Git commit times are the record.
