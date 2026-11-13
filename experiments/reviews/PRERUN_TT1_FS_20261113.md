Reviewer: experiment-reviewer (Opus), 13 Nov 2026, read-only. Pre-run check of the TT1 fresh-seed block (prereg_fs1_block.md at a2fef5c). Report as returned, unedited; saved by the TT1 owner after the record keeper's ledger (486d089). Fixes were registered in ab81b35.

**Verdict: GO WITH FIXES.** One blocker has to be fixed before `start`: the FS1 driver will release the host while the TT1 job is running. Fixes 2 to 4 are a short reader and registration amendment, and they must be committed before any score exists. Everything else is minor.

What checks out (read-only checks; I opened no sealed or benchmark files):
- **Script pins.** All five sha256 in prereg_fs1_block.md §6 match the files at a2fef5c. `tt1_read.py` is 4546f520 and the pack's `bin/rescore.py` is 6f6eede7.
- **Code and weights.** Every .py file under `code/` in `tt1_pack.tar` matches `pn1_pack_fs.tar` byte for byte. Both packs hold the same base weights (`4b869929…`).
- **Stored scores.** All 15 `scores_eval.npz` files come from the same machine and GPU: host e8bf0b3abe77, A100-PCIE-40GB, GPU-5bd20020. Each has n=19,797 unique ids, `manifest_sha256` f0f29f22, `common.py` b5d42a99 and limit 0. They were made by run.sh → pn1_score.py (737d6e35, same as the repo) with the FS pack 96c31ae2.
- **Tar layout.** Members are `PN1_<arm>_s<seed>/{meta.json,last_trainable.pt,scores_eval.npz}`, which is what the extraction at remote_tt1_fs.sh:43-44 expects. Every `pn1_eval.csv` path is under `eval/` (pn1 11,797, hn2 5,000, a14 3,000), so extracting only `pn1/data/eval` is enough.
- **No benchmark rows.** `pn1_eval.csv` has 19,797 rows. `tt1_score.csv` (c0055b51) has 34,411 rows: tt1 30,994, gate 3,417, all under `eval/tt1/<8 sources>` and `eval/tt1ref`. A search for benchmark and sealed names finds 0 rows in either list. The R2 caveat carries over: celebrities in the LFW/CFP/AgeDB packs may overlap CASIA-WebFace identities (not checked).

**(1) Will the gate reproduce byte identity? Probably yes.**
- What matches pn1_score.py: same host and stack; identical code and weights; all rows in manifest order at batch 64, so the batches match, including the last batch of 21 (19,797 = 309×64+21); TF32 on for matmul and cuDNN. The flip pass, `non_blocking`, worker count and cuDNN defaults do not change the first logit.
- What is untested: no earlier byte-identity result compares the full `last.pt` load against the base + `last_trainable.pt` rebuild. The amendment-14 and tt1c identities were rescore.py against rescore.py.
- So if the frozen tensors in `last.pt` differ from the safetensors by even one bit, all 15 networks fail together and the block is "not available". That costs about 0.4 USD, so it is acceptable, but say so beforehand (see I2).

## Findings

**B1 (blocker): the host will be destroyed partway through the job.**
- `drive_fs.sh:133-137` writes RELEASE as soon as every queue named in QUEUES is DONE. QUEUES is currently `all sp`. Nothing in drive_fs.sh checks TT1_DONE.
- The guard destroys the instance on RELEASE (`src/vast/guard.py:5-6,61`).
- remote_tt1_fs.sh:27 starts only when the Sp queue frees the lock, which is the same moment DONE_sp becomes reachable. The FS driver polls every 10 min, while the TT1 job needs about 40-50 min. Measured on tt1c: about 80 s per network for the TT1 rows, so roughly 14 min for the gate and 30 min for the TT1 rows here.
- The claim in prereg §4 that "the FS1 driver … holds the release" is not implemented.
- **Fix before `start`:** `echo "all sp tt1" > /mnt/t7/smad_next/vast/pn1fs/QUEUES`. `keep()` is unaffected. After the TT1 driver writes `tt1/TT1_DONE`, the lead runs `touch DONE_tt1` and the next FS pull writes RELEASE, or the lead writes RELEASE by hand. Add one line to prereg §4 saying this.

**M1 (major): the "Sb above B" lead cannot be confirmed.**
- §0 says the block tests the 401/402 lead "Sb more than B" (+0.021/+0.031, both intervals above 0, result.md:108-111).
- But TT-H6 (tt1_read_fs.py:124-138) only prints "X lower than Y" for the pairs B−A, Sb−A and Sb−B. No result can produce "Sb higher than B".
- **Fix (amendment now):** add the pair `("B","Sb")` with the same rule, or reword §0 to "printed only".

**M2 (major): no across-seed summary, and the bar sits exactly at the effect seen.**
- The B−A effect on 401/402 was −0.033/−0.035, right at the −0.03 bar. Requiring at least 4 of 5 seeds past the bar will probably print "not distinguished" even if the true effect equals what was observed. The seed spread is as large as the arm gap (B F̄ 0.024 vs 0.002).
- The reader prints no across-seed mean ± SD at all.
- **Fix:** also print, for each arm and each pair, the mean ± SD over passing seeds of F̄, F_max and ΔF̄, plus the sign count. Add a note that the bar equals the 401/402 effect size. No GPU needed.

**M3 (major): the "fewer than 4 seeds" rule is not applied correctly in TT-H4.**
- At tt1_read_fs.py:105-109, when A failed the gate on a seed, the B or Sb verdict for that seed becomes an NA string that still counts as a passing seed.
- With A at 3 passing seeds, B's TT-H4 then reads "mixed (3 of 5…)" where §2 says it must be "not available". The mock only removed Sb_s405, so this path was never tested.
- **Fix:** `arm_rule({s: (net(a,s) if net("A",s) is not None else None) for s in SEEDS}, f)`, and return NA if A has fewer than 4 passing seeds. Re-run the mock with A missing on 2 seeds.

**m1 (minor): the "geo reference weak" label changes the agreement count in TT-H5.**
- In TT-H5 (line 121) the label is added to each seed's verdict string before seeds are counted, so the label alone can turn agreement into "mixed". TT-H5 in tt1_read.py:407-409 counts agreement on the bare verdict first. Count on the bare verdict, then append the label if any seed is weak.

**m2 (minor): the "uninformative" label is missing from TT-H1.** TT-H1 drops the label for networks whose R_cam share exceeds 5% (TT1-S §6; tt1_read.py:341). Add it back.

**m3 (minor): the §0.2 lower-bound clip is applied only inside the H1 test.** The `fam_flag_ci` values printed in the output stay unclipped, and zero-event families keep [0,0] intervals. Clip the printed bounds and print the Clopper-Pearson interval beside each zero-event family, as in the F8 correction.

**m4 (minor): the polling loop will stop before the job starts.** `loop` stops after 3 h (drive_tt1_fs.sh:60). If it starts with `start` now, it ends around 10:30. Start it at about 12:40, or pull at the job's ETA.

**m5 (minor): pins are recorded but not checked.**
- The GPU UUID, cuDNN `benchmark`/`deterministic` flags and SDPA backend flags are recorded or missing, but never asserted.
- Add an assert that `nvidia-smi` shows UUID GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad, and print `cudnn.benchmark`, `cudnn.deterministic` and `torch.backends.cuda.{flash,mem_efficient,math}_sdp_enabled()` into versions.txt (Pins 8 and 10).

**m6 (minor): small consistency and housekeeping fixes.**
- **τ_cam uses a different TF32 setting.** It comes from the stored TF32-on scores but is applied to TF32-off logits, which breaks Pin 7 as written. It is printed only and done the same way as Sb/Bv in TT1. Label it, or recompute it from the job's own R_cam rows.
- **Stale comments.** The script headers say "16 FS1 tasks" and cite the draft prereg.
- **Uncommitted README.** README.md has an uncommitted 6-line edit; commit it.
- **Undeclared deviation from TT1-S §9.** §9 planned a tolerance gate, 16 networks and `tt1_nets_fs.tar`; the block uses byte identity, 15 networks and per-tar pins. Say so in the registration.
- **No re-run window after a crash.** On a FATAL result the lead may release the host and lose the allowed unchanged re-run. State that the release is held for one re-run if time allows.

**(3) and (5) are sound.**
- The TT1 driver never writes RELEASE.
- TT1_DONE is written only after the tar and logs pass sha256 checks in two locations.
- If the host is unreachable or rc is unreadable, the driver makes no decision.
- If the job is killed, no DONE_FS is written, so no decision follows.
- Not scoring beside the Sp fits is right. The host has 63 GB of RAM shared with a training process and its 7 loader workers, so the main risk is memory. Arithmetic is unaffected. The lock path matches remote_fs.sh:29 and remote_sp.sh:27.
- **(6) F4 limits and platform pins:** the limits are carried over correctly in §0. Using TF32 on for the gate and TT1-S defaults for the reads is a deliberate choice. It is disclosed, and it keeps the reads comparable with 401/402.

## Improvements (by value per GPU-hour)
1. **I1 (0 GPU):** the reader amendments M1-M3 and m1-m3, plus a mock that removes A on 2 seeds. These need a registration amendment before scoring; that is allowed now.
2. **I2 (0 GPU, needs a lead or author decision now):** decide in advance what an all-15 gate failure means, either "platform finding, block not available" or the TT1-S §4 tolerance gate as a labelled fallback. Decide before the gate runs.
3. **I3 (0 GPU):** print max |Δ| and decision changes between the job's TF32-off R_cam logits and the stored TF32-on ones. This measures the effect of the TF32 split on these networks.
4. **I4 (seconds):** add a deadline check after the lock is taken: skip if less than 60 min remain before 15:51.

## Questions for the authors
- Does the lead agree to hold RELEASE through QUEUES (B1), or should it be handled another way?
- Which outcome applies if all 15 networks fail the gate (I2)?

Key paths: /home/narolski/smad-next/src/PN1/rented/drive_fs.sh, /home/narolski/smad-next/src/TT1/tt1_read_fs.py, /home/narolski/smad-next/src/TT1/rented/remote_tt1_fs.sh, /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/prereg_fs1_block.md, /mnt/t7/smad_next/vast/pn1fs/QUEUES
