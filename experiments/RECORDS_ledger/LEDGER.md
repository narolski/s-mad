# Record keeper's ledger (RECORDS)

Append-only. Each entry is dated with `date` on this machine (DGX, CET). Verdicts: VERIFIED, WRONG, NOT CHECKABLE.
The record keeper checks records only: no images, no sealed or closed benchmark data, no cluster access. It does not
interpret results and does not correct other owners' files; discrepancies are reported here and to the lead.
Sources: `git` on `origin/sprint-plan-v2`, file mtimes, `/mnt/t7/smad_next/dispatch/` (STATE.md, ticks.log, MEMORY.md,
submit_queue/done/), owner logs under `/mnt/t7/smad_next/<ID>/`.

---

## Entry 1. `date`: Fri Nov 13 06:55:53 PM CET 2026 (started); written up to Fri Nov 13 07:03:42 PM CET 2026

### 1a. Evening conclusions (`18_EVENING_CONCLUSIONS_20261113.md`, commit 8e9ff7a)

| Claim | Verdict | Evidence |
|---|---|---|
| File committed as 8e9ff7a | VERIFIED | commit, on origin/sprint-plan-v2, 17:38:36, adds only this file |
| "Written by the lead at 17:45 CET" | WRONG | committed 17:38:36 (git); 17:45 is about 7 min after the commit |
| Freeze rule amended at 6691adc | VERIFIED | 6691adc 07:04:46, FINAL prereg section 1 freeze rule, on origin |
| C2P scored on a different GPU and precision from the stored scores; platform check removed every plain network | VERIFIED | REVIEW_PN1_C2P_20261113.md:9 (L40S TF32 off vs A100 PCIe TF32 on; gate removed all five plain networks) |
| C2P-R "drafted and pre-run checked" | NOT CHECKABLE as "reviewed" | draft `PN1/prereg_c2pr_draft.md` (e8488ef, e63a6ad); the pre-run check is recorded only inline (lines 85-87, "GO WITH FIXES"); no review file in experiments/reviews/ |
| 0 of 100 seam-only flagged; same-person vs seam-only 0.86-0.93 (REVIEW_PR1_PART1) | VERIFIED | PR1/result.md:18 and :20 (dev 0.863-0.927); review exists, "accept with corrections" |
| Sb − B +0.15 to +0.21, Sb − A +0.12 to +0.14; Sb 0.873-0.906 vs floor 0.886 (REVIEW_AB1) | VERIFIED | recomputed from AB1/result.md:82 per seed: Sb−B 0.149/0.212/0.180/0.156/0.147; Sb−A 0.122/0.143/0.136/0.117/0.125; floor :102; review `AB1/REVIEW_AB1_20261113.md` |
| "replicated on ten seeds across two platforms" | NOT CHECKABLE (not recomputed) | AB1 gives 5 seeds (408-412, H100); the other 5 are PN1 FS1 (403-407, A100) |
| Plain arm rises 27-39 points (trained size), 6-15 (untrained); Sb at most 4.5 and 2.1 | VERIFIED | AB1/result.md:83 A Δf fm61 +0.265..+0.385; :87 amsl112 +0.055..+0.152; Sb max +0.045 / +0.021 |
| Storage verdict "inconclusive", two seeds miss the two-sided bar toward genuine | VERIFIED | AB1/result.md:28 |
| Sb untrained-size pass does not replicate on fresh seeds (REVIEW_SE1_A100) | VERIFIED | REVIEW_SE1_A100_20261113.md:25 (amsl112 2/4) |
| ~21,000 photos, eight unseen sources; protocol arm within rule on all seven seeds; candidate 4 of 5 (REVIEW_TT1_FS) | VERIFIED | REVIEW_TT1_FS_20261113.md:13 (21,035), :33, :92 |
| 865 NIST mugshots; all three arms within rule; candidate flags 0.1-0.5%; false alarms in small images enlarged ~3x | VERIFIED | TT1/tt1_read_meds.json nets.PN1_Sb_s403..407.flag = 0.0035, 0.0035, 0.0046, 0.0046, 0.0012; TT1/result.md:506-509 |
| Border: Sb 2.9-16.3%, protocol arm 0-1.9%, none without border ("TT1 follow-up, reviewed") | VERIFIED | TT1/result.md:371-376 (Z3, zfs.json), section header :349 "reviewed by results-reviewer (opus)"; no separate review file |
| 83-90% of same-person morphs flagged (cited to REVIEW_PR1_PART1) | VERIFIED with a source note | PR1 fresh seeds give 83.2-88.5% (PR1/result.md:117); 0.83-0.90 is the SE1 A100 Sb range (SE1/result.md:29) |
| 31-48% of same-person splices flagged | VERIFIED | PR1/result.md:19 (dev 31-41%) and :119 (37.2-48.2%) |
| Margin falls from about 4-5 to about 1-2 logits on new persons | VERIFIED | PR1/result.md:136 (training 3.96-4.94, test 1.08-1.79) |
| 78-90% of GAN renders of a single photo flagged (PR1_PART2/PART3) | VERIFIED | PR1/result.md:261 and :227; reviews PART2, PART3 exist ("accept with corrections") |
| MS1: twice as many missed at the same rule, unchanged ranking (REVIEW_MS1) | VERIFIED with a note | REVIEW_MS1_20261113.md:27-31: miss median 0.271 → 0.585; resmatch AUC 0.874 vs 0.861; the same finding also reports CFD AUC 0.952 → 0.866 |
| SE1: same-person morphs 25-32% instead of 83-90%; splices unchanged (REVIEW_SE1_A100) | VERIFIED | SE1/result.md:28-29 |
| Removing matched negatives: same-person splices 70-74% vs 36-41% (REVIEW_AB1) | VERIFIED | AB1/result.md:40 and :96 |
| BB2: did not fit its own splices; inconclusive (REVIEW_BB2_PART1) | VERIFIED | REVIEW_BB2_PART1_20261113.md:3 |
| MADation ViT-B/16 and MixFaceNet-MAD "lose 13-20 points on landmark families"; ViT-L/14 barely moves (REVIEW_CB1_BORDER_HISTORY) | WRONG as stated | CB1/result.md:227-235: AMSL and WebMorph +12.8 to +19.6 fit; OpenCV is +3.90 (ViT-B/16) and +5.88 (MixFaceNet); MixFaceNet MAD22 FaceMorpher +8.37; ViT-L/14 −0.54 to +1.98 (VERIFIED) |
| SMDD partner trace 0.72-0.91 for three released detectors (REVIEW_SM1_A23) | VERIFIED | SM1/a23_rank_rel.json crop_path: ViT-B/16 0.7158, ViT-L/14 0.7676, MixFaceNet 0.9094 |
| 0.723 ± 0.032 for our five-seed ViT-L/14 retrain (REVIEW_SM1_VITL_5SEED) | VERIFIED | SM1/a14_rank_vitl_5seed.json a.auc 0.7233; SD of auc_per_seed recomputed 0.032 |
| MorDIFF 0.0% on every seed, on both backbones ("AD4, reviewed") | number VERIFIED; "reviewed" NOT VERIFIED for ViT-L/14 | AD4/result.md:43 (ViT-B/16) and :71 (ViT-L/14). Review file exists only for ViT-B/16 (REVIEW_AD4_VITB_20261111.md); AD4/README.md:1151 records a review of the cluster-stack readings at about 08:50 with no file |
| Audit table: 20 shortcuts × 9 arms, 122 of 180 reviewed | NOT CHECKABLE (counts not recomputed) | SA1 commit e443fb2 subject: "recount 122 reviewed, 16 unreviewed, 27 empty of 180" |
| WCSS read deadline "latest 15 Nov 18:00, by the author's ruling of 17:15" | time WRONG | the ruling was recorded in 3a6440e at 17:13:31, and amendments citing it were committed from 17:14:04; it came before 17:13:31 |
| IDistill on the DGX ends 14 Nov morning | NOT CHECKABLE | no log checked by RECORDS |
| Spend about 48.5 USD of 50 | NOT CHECKABLE | no billing record here; NOTEBOOK 15:10 says 46.5 at 15:10 |

### 1b. NOTEBOOK.md, 13 Nov entries from 17:15 on

| Claim | Verdict | Evidence |
|---|---|---|
| Entry headed "17:15" | WRONG (header time) | committed in 3a6440e at 17:13:31 |
| Correction entry: the 17:15 entry "committed at about 17:11" | WRONG | 3a6440e is 17:13:31 |
| SE1 A100 block read once at 64c025a | VERIFIED | 64c025a 17:06:38, on origin, adds SE1 result.md and se1_read.json |
| SE1 numbers: S3 0.34-0.41 vs Sb 0.36-0.41; R3 0.25-0.32 vs 0.83-0.90; landmark_combined 0.909-0.911 vs 0.886-0.904 | VERIFIED | SE1/result.md:28-29, :49 |
| SE1 "wording deviation approved by the lead (17:25)" | WRONG | recorded in 1b8b120 at 17:14:04, 11 minutes before 17:25 (the correction entry already says this time came from memory) |
| "review running" (SE1) | VERIFIED | REVIEW_SE1_A100_20261113.md committed in f302cfa at 17:12:57 |
| MEDS scoring started on se1d at 17:06 | VERIFIED (assuming the rented host's log clock is UTC) | `/mnt/t7/smad_next/TT1/results/logs_TT1M_se1d/remote_m.log` "2026-11-13T16:05:56 start"; driver fix 41803d6 at 17:05:44 |
| Entry headed "18:30"; author ruling quoted at 18:28 | WRONG (header); 18:28 VERIFIED only to the minute | committed in e29b51b at 18:27:42; the ruling must be before 18:27:42 |
| Frozen tars pinned by sha256 in the C2P registration (2715e48) | VERIFIED | 2715e48 07:03:22, PN1 prereg C2P.2 lists Sb 403-407 prefixes 8dec83b8, de670689, 3a3a53fd, d2cf5faa, 865c0455; they match `/mnt/t7/smad_next/PN1/results_fs/PN1_Sb_s40[3-7].tar.sha256` |
| Strategist file STRATEGIST_EVENING_20261113.md exists | VERIFIED | experiments/reviews/STRATEGIST_EVENING_20261113.md (c688a62 17:45:04) |
| Entry headed "18:50" | WRONG (header) | committed in 5328624 at 18:32:28 (correction entry says this) |
| Second-engine arm to the AB1 owner | VERIFIED | registration 9c0ed39 18:43:49; job 6315597 (7e3c59e 18:47:49; dispatcher MEMORY.md:202) |
| Entry headed "19:20" | WRONG (header) | committed in 3169af7 at 18:35:39 (correction entry says this) |
| "asked at 18:55, unanswered" (in the 19:20 entry) | WRONG | the entry was committed at 18:35:39; the correction entry does not list this time |
| 36 two-person MIPGAN-I morphs usable | VERIFIED as reported | GX1/README.md timeline ("36 usable existing morphs") |
| Entry headed "19:25"; ruling at 19:25 | WRONG | committed in bfc5b1f at 18:36:07 (correction entry says this) |
| Correction entry headed "18:46 machine clock" | WRONG by about 1 min | committed in 46a5e89 at 18:45:24 |
| Correction entry: commit times 18:27:42, 18:32:28, 18:35:39, 18:36:07 | VERIFIED | git log of NOTEBOOK.md |
| Lead's message times 19:05, 19:15, 19:35, 19:50, 20:00 lie between 18:36 and 18:46 | NOT CHECKABLE | messages are not on file |
| Entry "18:56" (five roles) | VERIFIED | 5092bc6 at 18:56:13 |
| OWNER_BRIEF five roles at 6e42c86 | VERIFIED | 6e42c86 18:52:09, OWNER_BRIEF.md only |
| NEXT draft 351a7f2; pre-run check GO WITH FIXES saved | VERIFIED | 351a7f2 18:47:52; PRERUN_NEXT_SELECTION_RULE_20261113.md "Verdict: GO WITH FIXES" |
| GX1 smoke 6315653 and arrays 6315654, 6315655 submitted, pending | VERIFIED (IDs); state from dispatcher only | submit_queue/done/wcss_gx1_*.631565[3-5].cmd; STATE.md "0 of ours running" |
| BB2 wave-2 rescoring registered (d7018f8), "in the dispatcher queue" | d7018f8 VERIFIED; "in the queue" WRONG | d7018f8 18:50:49 is the registration; it was already submitted as 6315675/6315676 (done/ files 18:52:46; 1a10fa3 18:53:56) before this 18:56 entry |

### 1c. Dispatcher records (found while checking times)

| Claim | Verdict | Evidence |
|---|---|---|
| ticks.log lines "19:04", "19:08", "19:15", "19:25"; STATE.md "Last tick 19:15 CET (machine)", "ORDER (lead 19:30)" | WRONG | ticks.log mtime 18:56:45, STATE.md mtime 18:55:36, `date` at that time 18:56-18:57. These times are ahead of the machine clock by about 15-35 min |
| ticks.log order | WRONG (minor) | a line "17:30" comes before "17:25" |
| MEMORY.md: MS1 reported fc5d6d3 | VERIFIED that fc5d6d3 does not exist | `git cat-file` fails; the real commit is 594756d (18:49:02) |

### 1d. GAN-morphs owner report (GX1)

| Claim | Verdict | Evidence |
|---|---|---|
| b6d2dce = registration, 18:40:15 by git | VERIFIED | commit, on origin; 18:40:15; adds GX1/prereg.md and src/GX1/build_gx1.py. Note: its text then gave the times 18:50 and 19:35 (corrected later in eabdcc4/edcf862) |
| eabdcc4 = amendment 1 | VERIFIED | 18:48:45, on origin; amendment 1 (F1-F8, generation pins), PRERUN_GX1_20261113.md, README, three WCSS scripts. Its text said "about 18:55 machine clock", which was after its own commit (fixed by edcf862) |
| edcf862 = time notes | VERIFIED | 18:50:08, on origin; 4-line time fixes in README and prereg; the submit files it mentions exist (mtime 18:49:54) |
| 748f4e2 = amendment 1b | VERIFIED (content); one time WRONG | 18:51:09, on origin; adds amendment 1b. Its text says the lead's answers were "received 18:52 machine clock", which is after the commit |
| c4ea2ad = README with job IDs 6315653, 6315654_[0-11], 6315655_[0-7] | VERIFIED | 18:51:24, on origin; IDs match `submit_queue/done/wcss_gx1_gensmoke.6315653.cmd`, `..._gen_mip1.6315654.cmd` (`--array=0-11`), `..._gen_mip2.6315655.cmd` (`--array=0-7`) and MEMORY.md:209 |
| Submission "about 18:52" (README) | WRONG | README committed at 18:51:24 already contains the IDs. Submission was between 18:49:54 (cmd files written) and 18:51:24. ticks.log says "19:08", which is also wrong |
| Smoke gate GX1_SMOKE_OK | VERIFIED | src/GX1/wcss/gx1_gen_smoke.sbatch:18 `echo GX1_SMOKE_OK` after `set -euo pipefail` and both smoke shards |
| Gate wiring at submission | WRONG at c4ea2ad, fixed later | amendment 1 F6 (prereg.md:154) and the cmd headers say the arrays go in with afterok / after the smoke. They were submitted beside the smoke without a dependency (README c4ea2ad). The dispatcher added `afterok:6315653` afterwards (MEMORY.md:216; README 646e8b2 18:57:43) |
| Pre-run review | VERIFIED | `GX1/PRERUN_GX1_20261113.md`, "Verdict: GO WITH FIXES", committed in eabdcc4. The file is in the experiment folder, not in experiments/reviews/ |
| Registered before any run | VERIFIED | no GX1 image, score or result file exists. Note: person selection and prep started at 18:37:16 (README), before the 18:40:15 registration; that was data prep, not a score. `/mnt/t7/smad_next/GX1` holds inputs/build/pack only |
| Job state | NOT CHECKABLE beyond the dispatcher | STATE.md: 0 of ours running |

### 1e. Experiment folders: registration, pre-run review, first result, post-result review

Times are git commit times (month-day, CET). "First result" = first commit adding a read or result file other than
mocks. Where a registration and its first result share one bulk commit, git cannot show the order. Pre-run and
post-result files are looked for in experiments/reviews/ and in the experiment folder.

| Folder | Registration | Pre-run review | First result | Post-result review | Flag |
|---|---|---|---|---|---|
| AB1 | 61f7994 11-13 09:21:59 (B2 324b4fa 14:52; Sbx 7e4a974 17:56; SbFM 9c0ed39 18:43) | PRERUN_AB1, _AMEND2, _AB1B2, _AB1X, _AB1FM (folder) | 8109cad 11-13 14:31:27 ab1_read.json | REVIEW_AB1_20261113.md (folder) | none; B2, Sbx, SbFM have no result yet |
| AD1 | cd4c11f 11-11 14:56:34 | none | same commit (labelled post hoc) | REVIEW_AD1_AG5_C_20261111 | order not checkable; no pre-run |
| AD1b | 1bf6f16 11-11 15:27:38 | none | e8b0d9d 11-11 16:16:16 result.md | none | no pre-run; no post-result review |
| AD4 | 4068c3a 11-11 15:38:00 | PRERUN_AD4 (committed e8b0d9d 16:16:16) | e8b0d9d 11-11 16:16:16 ad4_cells_m3.csv | REVIEW_AD4_VITB only | pre-run file committed together with the first reading; ViT-L/14 reading has no review file |
| AD5 | fb6697f 11-11 18:00:43 | PRERUN_AD5 (df15044 19:21:07) | MixFaceNet s401 fetched bcb8046 11-13 14:45 (descriptive) | none | pre-run file committed after the Athena submission (dce4ae6 19:08); no post-result review |
| AF0 | bcdd7e1 11-11 14:55:27 | none | 1bf6f16 11-11 15:27:38 | none | no pre-run; no post-result review |
| AG1 | 5a19286 11-11 17:25:21 (bulk) | PRERUN_AG1 (a0a8ab2 17:57:09) | ed053bc 11-12 12:15:44 | REVIEW_AG1_20261112 | none |
| AG5 | cd4c11f 11-11 14:56:34 | none | same commit (post hoc) | REVIEW_AD1_AG5_C_20261111 | order not checkable; no pre-run |
| AR1 | 5a19286 11-11 17:25:21 (bulk) | none | e48e4c9 11-11 20:29:23 | REVIEW_AR1_20261111 | no pre-run |
| AS0 | 62f86e1 11-11 18:26:32 | none | f61fc10 11-11 19:40:47 tables.md | REVIEW_AS0_20261111 | lists_summary.json (b0d50d6 18:14:34) committed before the registration; no pre-run |
| BB2 | 4393990 11-13 00:05 (draft 05a8e25 11-12 23:51) | PRERUN_BB2, _A1, _A2, _A3, _A45, _PLAN, _W2 | 203e2fe 11-13 15:37:49 | REVIEW_BB2_PART1 | none (05a8e25 result.md says "No result") |
| BD1 | 33bdee6 11-13 17:49:13 | PRERUN_BD1 (9562302 17:55:49) | 83daa17 11-13 17:57:18 | REVIEW_BD1 (92d8e05 18:04:14) | amendment 2: 7697fbf 18:07, pre-run 23266fb 18:14, read ca76ca3 18:15, review 18:18, all in order. Amendment 4: registered 1cd0304 18:19:59, read db07b4b 18:20:16 (17 s later), **no pre-run file**; review REVIEW_BD1_AMEND4 18:21:36 |
| C1b | 1bf6f16 11-11 15:27:38 | none | 5c8608e 11-11 15:42:09 | REVIEW_C1b_20261111 | no pre-run |
| C1c | 7518e2d 11-11 17:00:54 | none | same commit | none | order not checkable; no reviews |
| CB1 | fb0c5d5 11-12 23:36:46 | none | 9cc05b4 11-13 01:12:05 | REVIEW_CB1_BORDER_HISTORY, REVIEW_CB1_SA1CELLS | no pre-run file |
| C_cue_checks | none | none | cd4c11f 11-11 14:56:34 | REVIEW_AD1_AG5_C (if "C" covers it) | no registration |
| DG1 | e025d6b 11-11 17:29:14 | PRERUN_DG1 (180b168 19:24:42), PRERUN_DG1_SAMEORTH | result.md e408128 11-11 17:37:38 (content not checked) | none | pre-run file committed after the first result.md; no post-result review |
| EV1 | 70090d2 11-11 17:00:23 | none | same commit | REVIEW_EV1_20261111 | order not checkable; no pre-run |
| FINAL | 71fa6e4 11-12 23:17:29; last amendment 6691adc 11-13 07:04:46 | PRERUN_FINAL_SEALED_READ_20261112 | none committed | none | the MAD22 read scope set at about 18:36 is not committed as a FINAL amendment. `FINAL/final_thresholds.json` is untracked (mtime 18:44:41). The read package and stand-in tests exist under /mnt/t7/smad_next/FINAL (names and times only checked) |
| FZ1 | 1bf6f16 11-11 15:27:38 | none | 5a19286 11-11 17:25:21 | REVIEW_FZ1_20261111 | no pre-run |
| FZ2 | b6f4abd 11-11 20:33:44 | none | 7258bc0 11-11 20:39:14 | REVIEW_FZ2_AR1A10_20261112 | no pre-run file |
| GX1 | b6d2dce 11-13 18:40:15 | PRERUN_GX1 (folder; eabdcc4 18:48:45) | none | none | see 1d |
| ID0 | 5a19286 11-11 17:25:21 (bulk) | none | same commit (result.md) | REVIEW_ID0_20261111 | order not checkable; no pre-run |
| LA1 | draft only (7121c76 11-13 18:36:59) | PRERUN_LA1_PLAN | none | none | not registered, nothing run |
| MS1 | 3d4411b 11-12 23:03:22 (build plan); comparison draft cb1cf09 23:18 | PRERUN_MS1_COMPARISON (b9d615b 23:22:46) | cf66f36 11-13 09:49:56 ms1_read.json | REVIEW_MS1, _PART3, _PART3B | none |
| NEXT | draft only (351a7f2 11-13 18:47:52) | PRERUN_NEXT_SELECTION_RULE | none | none | not registered |
| PD1 | subfolders: gan, landmark, diffae 5a19286 11-11 17:25:21; transfer f3024b0 21:11:26 | none | gan, landmark: same bulk commit; diffae b0d50d6 18:14; transfer 9503618 21:20 | none | no pre-run; no post-result review; gan and landmark order not checkable |
| PN1 | dce4ae6 11-11 19:08:34 | PRERUN_PN1 (6f3f544 19:55:53) and six later | f9a0b51 11-11 19:48:45 tier0_tables.md | REVIEW_PN1_* (6 files) | first pre-run file committed after tier0_tables.md; split_summary.json (a978fa9 19:01) before the registration |
| PR1 | a6e274a 11-13 08:54:44 | PRERUN_PR1 (4320366 09:16:23) | 6aa02f8 11-13 09:21:30 | REVIEW_PR1_PART1/2/3, _Z5 | amendment 3 registered 90caa9e 09:33 and read ea24c3d 09:34 with no pre-run file (post hoc) |
| RS1 | 5a19286 11-11 17:25:21 (bulk) | none | same commit (rs1_results_smoke.json) | REVIEW_RS1_20261112 | no pre-run |
| RZ1 | **not committed** (prereg.md untracked, mtime 18:51:55) | none | none | none | `/mnt/t7/smad_next/RZ1/localtest` written 18:59:38, before any registration commit (a local test; content not checked); no pre-run file |
| SA1 | 3a0065e 11-13 08:50:35 (G9, G11) | none | table v1 e96bf68 08:40:24 ("zero scoring") | REVIEW_SA1_20261113 | result.md committed 10 min before prereg.md (v1 compiles reviewed results); no pre-run |
| SE1 | c8bbaf0 11-13 09:01:05 (A1 6b09c2a 14:19:10) | PRERUN_SE1, PRERUN_SE1_A1 | 64c025a 11-13 17:06:38 | REVIEW_SE1_A100 (f302cfa 17:12:57) | none; the H100 block has no result yet |
| SM1 | 5a19286 11-11 17:25:21 (bulk) | PRERUN_SM1 (a0a8ab2 17:57:09), PRERUN_SM1_A18 | c1ed82a 11-12 16:00:26 a15_read.json (earlier files in the bulk commit) | 10 REVIEW_SM1_* files | order of the first files not checkable |
| TT1 | 3912ae4 11-12 23:10:39 (pools); TT1-S 01557ce 23:25; MEDS 4ca7755 11-13 13:47:43 | PRERUN_TT1_SCORING (7c0ecb6 23:19:21) | cf963d1 11-13 01:53:40 tt1_read.json; MEDS read 48af747 17:15:46 | REVIEW_TT1, REVIEW_TT1_FS | MEDS block is called "reviewed" in result.md:429 but has no review file |

### 1f. CLAIMS block from the SMDD partner audit owner (SM1), relayed by the lead

| Claim | Verdict | Evidence |
|---|---|---|
| commit db320f5 "ViT-L/14 arm a seeds 404, 405 fetched, verified and read" | VERIFIED | 11:36:23, on origin; p3_lora_vitl.json, p3_lora_vitl_seeds.csv, result.md |
| commit ae614b4 "audit seed 403 read (0.699; 3-seed 0.737)" | VERIFIED | 11:00:30, on origin; a14_rank_vitl_3seed.json auc 0.7367, per-seed 403 0.6991 |
| commit dcda12e "audit seeds 404, 405 read (A14 5-seed 0.723); audit_conv.py" | VERIFIED | 11:43:50, on origin; a14_rank_vitl_4seed/5seed.json, src/SM1/audit_conv.py |
| commit 8f044b2 "five-seed review saved and applied" | VERIFIED | 11:48:29, on origin; REVIEW_SM1_VITL_5SEED_20261113.md + result.md; review verdict "needs qualification" |
| file p3_lora_vitl.json sha256 b994fe5665da47fc | VERIFIED | sha256sum; file clean in git |
| file a14_rank_vitl_5seed.json sha256 f922bac38ca1d208 | VERIFIED | sha256sum |
| file REVIEW_SM1_VITL_5SEED_20261113.md sha256 ca14463f57b98705 | VERIFIED | sha256sum |
| file src/SM1/audit_conv.py sha256 21a3bf5154516346 | VERIFIED | sha256sum |
| file SM1 result.md sha256 89dbccd1db6399ff | VERIFIED | sha256sum |
| landmark-7 native EER 2.304 (2.2828, 2.9593, 1.9976, 1.3299, 2.9497) | VERIFIED | arms.a["mean_eer:native:landmark7"].mean 2.30387; seed mean recomputed 2.3039 |
| landmark-7 change under history −0.259 | VERIFIED | arms.a["mean_rise:landmark7"].mean −0.25898 |
| diffusion-7 change −3.89 (−1.846, 0.3256, −8.8841, −6.5781, −2.4688) | VERIFIED | arms.a["mean_rise:diff7"].mean −3.8903; recomputed −3.8903 |
| MorDIFF native EER 50.62 (51.4853, 38.7127, 54.0108, 59.3069, 49.6049) | VERIFIED | arms.a["eer:native:mordiff:mordiff"].mean 50.6241; recomputed 50.624 |
| MorDIFF change under history 4.07 | VERIFIED | arms.a["rise:mordiff:mordiff"].mean 4.0688 |
| MorDIFF own-rule miss 0.996-1.0 | VERIFIED | arms.a["e7miss:own_rule:mordiff:mordiff"].seeds 1.0, 1.0, 0.999, 0.996, 1.0 |
| history-matched MorDIFF genuine flagged 0.0, all seeds | VERIFIED | arms.a["e7flag:own_rule:mordiff:mordiff"].seeds all 0.0 |
| partner-trace AUC 0.7233 [0.7151, 0.7315] | VERIFIED | a14_rank_vitl_5seed.json a.auc, a.auc_ci |
| per-seed AUC 0.7554, 0.7556, 0.6991, 0.6854, 0.721 | VERIFIED | a.auc_per_seed; their mean is 0.7233, SD 0.032 (matches 8f044b2 subject) |
| trained − KE gap 0.0413 [0.0289, 0.056] | VERIFIED | a.trained_minus_KE, a.gap_ci |

Summary: the SM1 block is fully VERIFIED. The GX1 report has correct hashes and job IDs, but two times are wrong
(748f4e2 "18:52", README "about 18:52") and the arrays were submitted without the registered afterok gate (added
later). In the evening conclusions, the CB1 "13-20 points" range and "AD4 reviewed" for ViT-L/14 are wrong as stated,
and so is the time 17:45. Notebook header times are wrong as the correction entry says. Not listed there: "18:55" in the
19:20 entry, "17:11" (the real time is 17:13:31), "18:46" (18:45:24), and BB2 wave 2 "in the queue". The dispatcher's
ticks.log and STATE.md carry times 15-35 min ahead of the machine clock. BD1 amendment 4 has no pre-run file. RZ1 and
the FINAL MAD22 scope are not committed while work for them is already on disk.
