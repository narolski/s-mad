# Registration TT1-X: extension of the TT1 fresh-seed block to the Sp arm and to SbM3, for the shortcut audit table (SA1)

Status: registered at the git commit that adds this text. The lead requested it on 13 Nov (SA1 has empty cells for
border, crop geometry and unseen genuine sources for Sp and SbM3). At this commit:
- no Sp or SbM3 network has been scored on a TT1 row by TT1;
- no MS1 score has been opened.

It inherits TT1-FS (`prereg_fs1_block.md`, a2fef5c + amendment ab81b35) in full: the F4 limits (false alarms only;
low-resolution bordered frames; not a sharp-source result; no detection or miss claim), the platform pins, the reads
R1-R5 and the clipped intervals. Only what differs is written here.

## Part 1: the Sp arm (seeds 403-405) on pn1fs, after the main block

- **Networks.** PN1_Sp_s403, s404, s405 (registration Sp in PN1 prereg.md; trained on pn1fs after FS1's fits, same
  GPU GPU-5bd20020…, same image). Pins: the sha256 of the verified local copies of the Sp result tars; the driver
  writes them into `nets_pins.txt`.
  - Sp is an ablation arm with three seeds. It enters no TT1 decision rule. Its numbers are printed only, labelled
    "Sp, three seeds, printed only".
  - The per-network gate rule still applies: a failing network is not scored and is printed "not available (failed
    platform gate)".
- **Gate.** As TT1-FS §2, unchanged:
  - Every row of the FS1 evaluation manifest `pn1_eval.csv` (f0f29f22…, 19,797 rows). The Sp pack does not change it:
    `mk_sp.py` asserts byte equality. Sp's stored scores_eval.npz were made by run.sh → pn1_score.py on that manifest.
  - Scored in manifest order, batch 64, TF32 on.
  - Byte identity per network.
- **TT1 rows.** For passing networks, fam tt1 (30,994) and fam gate (3,417) of `tt1_score.csv` (c0055b51…) with
  rescore.py unchanged.
- **Scripts.**
  - `src/TT1/rented/remote_tt1_x.sh`: a copy of remote_tt1_fs.sh parameterized by TAG, its own bin and work folders,
    pinned GPU UUID and deadline.
  - `src/TT1/rented/drive_tt1_x.sh`: never writes RELEASE; writes `tt1/TT1X_DONE_sp` after two verified copies.
  - sha256 of both are at this commit, below. Neither touches the running main job's files.
  - Mechanics tested on the DGX mock host (test mode; one 401 network, rows differ by design → not scored).
- **Order and time.** The job is started on pn1fs once the three Sp tars are fetched and verified locally. It takes the
  host's fit lock, so it runs after the main TT1-FS job: gate about 3 min, TT1 rows about 5 min, extraction about
  3 min. Expected end about 13:45, before 15:51; the skip rule (under 60 min left) applies. **No deadline extension is
  needed** unless the Sp queue ends after about 13:30; in that case the lead is told before the start.
- **Release.** The lead adds "tt1x" to QUEUES. The lead touches DONE_tt1x only after `tt1/TT1X_DONE_sp` exists.
- **Reader.** `src/TT1/tt1_read_x.py`, written and mock-tested before any Sp TT1 score exists, pinned in a short
  amendment. It prints R1-R5, the TT1-FS printed reads (F̄ at cut-offs; geometry and border flags; R_cam spread) and
  the TF32-split print, per Sp network. Beside them it prints the same reads for FS1 Sb at seeds 403-405 from the
  TT1-FS result, as a reference only. No rule.

## Part 2: SbM3 (seeds 403-407): no new scoring, a read of scores MS1 already makes

The MS1 owner confirmed (13 Nov, message from the MS1 owner) that no job is needed:
- **References.** Under deviation MS1-D2 (86b4b69), every MS1 machine's queue ends with a held-out step. It runs
  rescore.py unchanged (6f6eede7…, logit without flip) on the TT1 reference rows of `tt1_score.csv` (R_cam, R_cam^border
  ×7, R_cam^geo224, R_cam^geo112, R_ffhq^border; 6,170 rows per network). It runs on the L40S 48 GB that trained each
  network (torch 2.2.1). Tars: `MS1H_m1|m2|m3.tar` in `/mnt/t7/smad_next/MS1/results_rented/`.
- **Unseen photos.** The 21,089 aligned TT1 frames are in the MS1 fit-pack evaluation manifest (d1fab6ad…). They were
  scored inside each fit by run.sh → pn1_score.py (TF32 on, batch 64) on the training machine.
- **No platform gate is needed.** Every SbM3 score comes from the machine and stack that trained the network. Nothing
  is moved across platforms. The GPU model is L40S, so SbM3 numbers are never compared bit-for-bit with A100 numbers.

**Stated limits, before reading:**
- (a) The U frames were scored with TF32 on and the references with TF32 off. Measured on PN1 networks, that split
  moves logits by up to 0.035 near the decision boundary. The R3(c), R3(f), R3(g) AUCs therefore mix two TF32 settings.
  This is printed as a label and is not corrected.
- (b) The U pool available is all 21,089 aligned frames. U_p (21,035) is taken as the subset by id, so the primary pool
  is unchanged.
- (c) The R_ffhq and M_ffhq reference rows are not in the tt1ref step:
  - u is computed from MS1's in-pack FFHQ rows if present, labelled "in-pack, TF32 on";
  - R3(b) and R3(d) are printed "not available" where a pool is missing.

**Order (lead's and MS1 owner's condition):** the MS1 registered read is committed first. TT1 opens no MS1 score
before that commit.

**Reader:** `src/TT1/tt1_read_ms1.py`. It is written after the MS1 read is committed, reading ids only (no score) to
build the pools, and is mock-tested and pinned in an amendment before any SbM3 score is read. It applies the TT1 reader
statistics unchanged and prints the SA1 cells per SbM3 seed:
- R1 own-rule flags per source;
- R3(a), (c), (e), (f), (g);
- geometry-224 and geometry-112 flags and paired shifts;
- border flags and paired shifts.

It decides nothing. MS1's own registered comparisons are not revisited.

## Cost

- Part 1: about 0.2 A100-hours inside the pn1fs lease, about 0.1 USD.
- Part 2: 0 GPU.

## Scripts (sha256 at this commit)

| Script | sha256 |
|---|---|
| `src/TT1/rented/remote_tt1_x.sh` | 39aaa573251d2aaf8aeebc75ad802ec16d55853240b67ba3362d976d7752113c |
| `src/TT1/rented/drive_tt1_x.sh` | c7291730270042a561fefc936482acdcee96e6475d351649858394bf1ab52867 |
| `src/TT1/rescore_tf32.py` | 0d0b6b6f… (unchanged) |
| `src/TT1/gate_check_fs.py` | 6d1962bf… (unchanged) |

## Amendment after the pre-run check (`date`: Fri Nov 13 09:04:46 AM CET 2026; registered at the git commit that adds this section, before any start or read)

Pre-run check (experiment-reviewer, opus): GO WITH FIXES (B1, M1-M3, m1-m3). Applied:
- B1: `drive_tt1_x.sh start` is run only after `/mnt/t7/smad_next/vast/pn1fs/tt1/TT1_DONE` exists (main job verified,
  two copies), so X never writes into /workspace/tt1/logs while the main job's log listing is open, and X cannot take
  the lock before the main job. Expected X end about 13:55, before the 14:51 skip point. GD0/PR1 waits for DONE_sp or
  NO_SP at most 30 min after DONE_FS and writes only under /workspace/pr1 (PR1 owner, 13 Nov); I tell the lead and the
  PR1 owner if X is not started.
- m1: exact start call (pinned): `TAG=sp TASKS="PN1_Sp_s403 PN1_Sp_s404 PN1_Sp_s405"
  LOCAL_TARS=/mnt/t7/smad_next/PN1/results_fs GPU_UUID=GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad
  DEADLINE_EPOCH=1794581505 GATE_PACK=/workspace/pn1/root/packs/PN1/pn1_pack_fs.tar
  GATE_PACK_SHA=96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004 bash src/TT1/rented/drive_tt1_x.sh
  149.248.21.7 30078 /mnt/t7/smad_next/vast/pn1fs start` (deadline epoch = 13 Nov 15:51:45 CET). If the Sp tars are
  elsewhere, LOCAL_TARS is the folder holding their verified copies (recorded in the README).
- m3: free disk on pn1fs is checked (df) right before `start`; the job itself aborts under 30 GB.
- m2: DONE_sp is written on success and on FATAL; if the job dies before finish or is never started, I write NO_SP
  remotely and tell the PR1 owner and the lead.
- M1 (Part 2 limit (c) replaced): R_cam, R_ffhq and M_ffhq are taken from each MS1 fit's in-pack rows (TF32 on; ids
  matched to tt1_score.csv fam gate, R_cam ids with the `rcam_` prefix removed). R3(a), R3(b) and u use only in-pack
  TF32-on logits. R3(c), R3(g) mix TF32 on (U) with TF32 off (references) and are labelled so. R3(e), R3(f) use the
  tt1ref R_cam (TF32 off) on both sides (not mixed). R3(d) uses R_ffhq^border (off) against in-pack R_ffhq (on),
  labelled mixed. Printed per network: max and median |Δ| and own-rule changes between tt1ref R_cam (off) and in-pack
  R_cam (on) on the L40S. Limit (a) corrected: the 0.035 figure was measured on PN1 networks on A100, not on the L40S.
- M2: Part 2 reads MS1's Sb and SbV networks from the same tars, by the same reader, beside SbM3 per seed and machine.
  The SA1 SbM3-vs-Sb contrast uses the L40S Sb only; the A100 FS1 Sb is printed as a reference. Label: seeds 403+406,
  404+407 and 405 come from three L40S machines (seed and machine confounded across seeds, not within a seed).
- M3: for SbM3, every read built on R_ffhq, R_ffhq^border, M_ffhq or u carries the label "trained source (FFHQ),
  development persons excluded, other pipeline". The unseen-genuine SA1 cell uses the seven TT1 families only.

## Reader pin, Part 1 (`date`: Fri Nov 13 11:09:37 AM CET 2026; before any Sp TT1 score is opened)

`src/TT1/tt1_read_x.py` d7760b030f71548211b0fc0642b85e88c363e0db5a9ecbf6b26a1ce4bac8ac02 (TT1 reader statistics unchanged; TT1-FS printed reads; clipped intervals and
Clopper-Pearson; TF32-split print; no rule). Disclosure: written after the Sp result tar
(`TT1_pn1fs_sp.tar`, gate 3 of 3 passed, byte identity) had been fetched and verified, but before any Sp TT1 score was
opened (the registration said "before any Sp TT1 score exists"; the job finished earlier than planned). Mock-tested on
random scores only. FS1 Sb 403-405 reference values are copied from `tt1_read_fs.json`.
