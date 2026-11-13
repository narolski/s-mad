# Input resolution and resize method (RZ1): full record

Owner: RZ1 owner (Claude agent for the lead). Machines: DGX (code, local smoke) and WCSS H100 (all fits and scores).
Registration: `prereg.md`. Code: `src/RZ1/`. Large outputs: `/mnt/t7/smad_next/RZ1/`. Follows DOCUMENTATION.md.

## 1. Question and current answer

Do a 512-px input, the fixed resize kernel, or a per-image mix of kernels in training change detection and the
storage, unseen-source and border shortcuts of the protocol network? Do native crops beat the whole frame at the same
token count? No answer yet: no fit has run.

## 2. Timeline (machine clock, CET)

- 13 Nov about 18:20: task received from the lead. Read OWNER_BRIEF.md, NOTEBOOK.md (13 Nov), the evening conclusions,
  the AB1 prereg, result and README, the AB1 code, BB2's README, result and DINOv3 programme plan, both strategist
  reports, and the TT1 manifests.
  - The SA1 table was not read beyond its use in the conclusions.
- Frame geometry from `prep_eval.py`'s docstring (read only): eyes at (190, 210) and (322, 210), so 132 px apart.
  Consequence: fm61 ≈ a 237-px frame and amsl112 ≈ a 437-px one, against the 224 input.
- DGX measurement, CLIP ViT-B/16 with random weights, batch 16, qkv gradients (`scratchpad/meas.py`, GPU shared):
  - 224: 0.278 s per step, 2.29 GB;
  - 512: 1.788 s per step, 9.61 GB;
  - so 6.4 times the time and 4.2 times the memory.
- About 18:50: plan sent to the lead. BB2 owner told; reply: no overlap, DINOv3 stays at 224, the loader is a possible
  later drop-in. Lead's decisions (dispatcher relay):
  - wave 1 go;
  - wave 2, crops and 512, go;
  - register together if that costs at most about 30 minutes;
  - submit unthrottled, in the order wave 1, crops, 512.
- The author kept the freeze (about 18:36): RZ1 arms are development rows. Times in lead messages after 17:00 were
  about 45 minutes ahead (dispatcher relay); the registration carries machine-clock notes.
- WCSS environment checked: `~/dmenv` has timm 1.0.30, Pillow 12.3.0, numpy 2.5.2, torch 2.11.0+cu128 and cv2 5.0.0.
  TT1 pack present on Lustre `packs/TT1/tt1_pack.tar`. MEDS pack not on WCSS (to upload to packs/RZ1).
- Code written:
  - rz1_kernels, rz1_patch, rz1_train, rz1_score, rz1_guard, mk_rz1, run_rz1.sh, the sbatch files.
  - CPU test of the kernels on one TT1 frame: fixed:pil_bilinear equals the current loader exactly (max difference 0).
    The other kernels differ by a mean of 0.17-0.56 grey levels.
  - The crop equals the integer slice; fixed at 512 is the identity.
- mk_rz1.py:
  - The first run stopped on a cross-id collision (ids of ab1x and TT1 overlap, for example ar1_*). Fixed by
    prefixing the source.
  - Cross manifest 2f41e6d4…, 13,771 rows; overlay 3cdc538e….
- Local smoke started (`/mnt/t7/smad_next/RZ1/localtest/smoke.sh`): SbMR seed 408, 20 steps, limit 8, the full input
  path, then Sb512 with 3 steps, no TT1. The run reached training with the guard passing (197 tokens, mixR,
  3 x 224 x 224).
- Pre-run review (Opus) started on prereg.md and the code.

## 3. Data

See prereg section 3 (all pins). The local smoke uses the DGX copies: `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar`,
`AB1/ab1_overlay.tar`, `AB1/x/ab1x_overlay.tar`, `TT1/tt1_pack.tar` and `TT1/meds/tt1m_meds.tar`.

## 4. Code

`src/RZ1/` (prereg section 3). Overlay built by `mk_rz1.py` into `/mnt/t7/smad_next/RZ1/overlay_tree` and
`rz1_overlay.tar`.

## 5. Results

None yet.

## 6. Checks

- The kernel CPU test (above).
- Local smoke of the real path on the DGX (`/mnt/t7/smad_next/RZ1/localtest/`):
  - SbMR, 20 steps, all inputs including TT1 and MEDS, limit 8: rc 0 in 281 s. Guard pre ok (197 tokens, 3 x 224 x 224)
    and post ok. All five score files and the 9 x 8 cross table are finite.
  - Sb512, 3 steps at 64 x 4, without TT1: the first run failed in the guard, because the 224 reference tower was
    refused while CLIP_RES was 512 (a guard bug, fixed: the guard builds the reference at CLIP_RES 224 and restores
    it). The rerun gave rc 0: guard pre (1,025 tokens; embedding equal to the bicubic resample, max difference 0) and
    post ok (res 512, bs 64, accum 4).
  - The overlay was rebuilt after the guard fix (b166b522…); `repin.sh` writes the pins into run_rz1.sh and the sbatch
    files.

- Pre-run review: GO WITH FIXES (`PRERUN_RZ1_20261113.md`). Fixes are in prereg section 12, including the code
  changes: four held-out test transforms in the cross table, and cv2 single-threaded. Overlay rebuilt (dccf37d2…).
- Local smokes after the fixes (3 steps):
  - Ac (interior crop, without TT1): rc 0 in 132 s, guard pre and post ok.
  - AN without TT1 failed in scoring: the cross table holds TT1 rows, which are absent in that test mode. This is a
    test-knob artefact; run_rz1.sh now drops the cross table when RZ1_SKIP_TT1 is set.
  - AN rerun with the full inputs and the 13-spec cross table: rc 0 in 196 s, guard ok, all scores written.

## 7. Dead ends and failures

- The mk_rz1 id collision (fixed before any use).

## 8. Observations and ideas

- At 224 the storage-test copies keep almost all the content an ideal 224 resize would keep. The plain storage
  reaction is therefore a kernel and near-limit effect at 224. This is the mechanism wave 1 tests.

## 9. Open items

- rz1_read.py: own loader, TT1 wrapper, mock tests, pinned before the first tar is fetched (prereg section 12, m5).
- Input-matched floors at 224 and for the crop, printed only (M3); crop hull coverage on CPU (m1).
- 512 array: queued only after the WCSS smoke, with --time from its 512 step rate (M6).
- Author's reading of "native resolution crops" (M7), through the lead.

## 10. Handover state

- Registration commit 3c3470d. Files on WCSS `packs/RZ1/` verified against `pins.sha256`: run_rz1.sh dc5d0838…,
  rz1_overlay.tar dccf37d2…, tt1m_meds.tar 3fb917b2…, and the four sbatch files.
- In the dispatcher's queue (13 Nov, machine clock about 19:05):
  - wcss_rz1_smoke.cmd: gates every RZ1 array; never read.
  - wcss_rz1_w1.cmd: 35 fits, limit 2:00, results/RZ1.
  - wcss_rz1_crop.cmd: 10 fits, limit 2:00.
  - Submitted by the dispatcher: smoke 6316283, wave 1 array 6316284 (35 tasks), crop array 6316285 (10 tasks).
  - Owner: RZ1 owner. Expected end: about 1-2 h after each array starts with up to 32 GPUs.
- Logs: /lustre/pd03/hpc-narolski-1790461090/smad-next/logs/rz1-{smoke,w1,crop,512}-*.out.
- Local test outputs: /mnt/t7/smad_next/RZ1/localtest/results/ (20-step and 3-step tars, code-path checks only, never
  read).

### Amendment 1 (rescoring AB1's A and Sb), 13 Nov about 19:10-19:20 by the machine clock
- Lead's yes to the reviewer's improvement 3, with the condition: write the amendment with a bit-identity gate, ask for
  its pre-run check, then queue it behind wave 1.
- Code: `rz1_rescore.py`, `run_rz1r.sh` (the input section of run_rz1.sh copied unchanged), `wcss/rz1-rescore.sbatch`.
- Local code-path test on the DGX (AB1_Sb_s408, 64 rows, `/mnt/t7/smad_next/RZ1/localtest/run_r.log`): rc 0.
  - The rebuild loads exactly the trainable keys.
  - The gate fails, as expected on another GPU model and with a strided 64-row subset: max |Δ| 0.0134 against the
    H100 logits, own-rule agreement 1.000.
  - rz1_score.py outputs written. This is a code-path check only, never read.
- Not submitted: waiting for the pre-run check (lead).
