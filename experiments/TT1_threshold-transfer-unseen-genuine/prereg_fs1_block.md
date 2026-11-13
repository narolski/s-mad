# Registration TT1-FS: the fresh-seed networks of the protocol network (FS1) on the TT1 unseen genuine sources

This text is registered at the git commit that adds it, which comes before any FS1 network is scored on a TT1 row.
It replaces the draft `prereg_fs1_block_draft.md` (16cccc0) and follows the lead's instruction of 13 Nov 07:15.
- FS1's own registered reading is committed (cdccb25; reviewed b5abb4b).
- The TT1 pack is staged and verified on pn1fs: STAGE_OK at 06:44:17 (`/mnt/t7/smad_next/vast/pn1fs/tt1/tt1_fs_drive.log`).
- Development data only. Benchmark and sealed sets stay closed.

## 0. What this can and cannot show (carried over from the TT1 review, F4 and Q6)

- **False alarms only.** These sources have no morphs, so no miss rate and no detection claim. The frames are
  low-resolution (faces enlarged 1.7x and 3.5x) and carry a black border from our aligner.
- **Not a sharp-source result.** The same B network that met the rule on these frames flagged 17.8% of FFHQ genuine
  photos (B_s401, TT1).
- **The camera-photo threshold does not transfer.** τ_cam reads are printed only, labelled "saturated band".
- **Not shown by any reading here:** calibration; the cause of a source effect; a benchmark or generalisation
  statement; that one arm is better overall. No arm, seed or threshold is chosen from TT1. FS1's frozen contrasts and
  the MS1 arm choice are not revisited.
- **What TT1 seeds 401/402 already showed.** These were two-seed leads: B fewer genuine flags than A, Sb more than B,
  and A's storage-size reaction. This block tests them on five fresh seeds. Every fresh seed was trained on the same
  host (pn1fs), so seed and machine are not confounded here, unlike 401/402.

## 1. Networks (15 deciding networks; the replicate is not part of this block)

A, B, Sb at seeds 403-407, last checkpoint, trained by FS1 on pn1fs (A100 PCIe 40 GB, image
pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime).
- Pins: the sha256 of each verified local copy (`/mnt/t7/smad_next/PN1/results_fs/PN1_<arm>_s<seed>.tar.sha256`).
  The driver writes them into `nets_pins.txt`; the host checks every tar against them.
- All 15 local copies were verified at this commit.
- PN1_Arep_s401 (FS1's replicate) is not scored.

## 2. Per-network platform gate (TT1-D3 rule, re-registered explicitly; review F9)

**Rule, verbatim:** "a deciding network that fails the gate makes the decision 'not available'; never read on one
seed."
- The gate is applied per network. A network that fails is not scored on TT1 rows.
- Every read that needs a failed network is printed "not available (failed platform gate)".
- An arm statement needs at least 4 of 5 seeds that passed the gate AND agree. With fewer than 4 passing seeds for an
  arm, every decision involving that arm is "not available".
- No tolerance is changed after seeing a gate.

**Gate rows:**
- Every row of the FS1 development evaluation manifest `pn1_eval.csv` (sha256
  `f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045`, 19,797 rows). The FS1 pack builder asserts that
  it contains no benchmark row.
- Scored in manifest order, batch 64, TF32 on (matmul and cuDNN), exactly as pn1_score.py did when it stored each
  fit's `scores_eval.npz` on this host.
- Scorer: `src/TT1/rescore_tf32.py` (sha256 below), which runs `src/PN1/rescore.py`
  (`6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e`) unchanged after setting TF32 on.
- The rows span the whole logit range: camera photos, ladder rungs, morphs, splices, FFHQ genuine and FFHQ morphs.

**Criterion:** byte identity of the float32 logit on every row against the stored `scores_eval.npz`, per network
(`src/TT1/gate_check_fs.py`).

**TT1 rows:** for passing networks only, the TT1 list rows are scored with rescore.py unchanged (PyTorch defaults:
matmul TF32 off), the same path as seeds 401/402:
- fam tt1: 30,994 rows;
- fam gate: R_cam, R_ffhq, M_ffhq, 3,417 rows, used as reference pools.

## 3. Platform pins (from `PLATFORM_PINS_FOR_FINAL_READ.md`, asserted or recorded by the job)

| Item | Value |
|---|---|
| GPU | A100 PCIe 40 GB, sm_80 (the host that stored the FS1 scores); UUID in gpu.txt |
| Driver and CUDA | driver recorded; CUDA 12.1 |
| Image and torch | pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime; torch 2.2.1 (asserted) |
| cuDNN | `torch.backends.cudnn.version()` recorded in versions.txt |
| Packages | timm 1.0.27, numpy 1.26.4, Pillow 10.2.0 (asserted); installed by the FS1 setup with the pip pins of remote_setup.sh; not reinstalled |
| TF32 | gate: on, as for the stored scores; TT1 rows: PyTorch defaults, as for TT1 seeds 401/402 |
| Attention backend | the torch 2.2.1 default (unchanged); recorded as default |
| Precision | float32, no autocast |
| cuDNN benchmark | `cudnn.benchmark` default False |
| Batching | batch 64; order fixed by the lists: FS1 `pn1_eval.csv` `f0f29f22…` for the gate; TT1 `tt1_score.csv` `c0055b51…` for the reads |

**Hashes:**
- `tt1_pack.tar` `2109f742b0378c188f394a3b26c363ef2ffb0ea43eab78ecea7674884022c554`;
- `pn1_pack_fs.tar` `96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004`;
- base weights `4b869929…` (in both packs);
- `common.py` `b5d42a99…`.

## 4. Running beside the Sp fits: decision

The ablation-arm (Sp) fits train on the same GPU until about 12:45, using 30.8 of 40 GB.

**Decision: do not score beside them.** The job takes the host-wide fit lock (`/workspace/pn1/fs_queue.lock`, also
taken by the Sp queue) and starts when the Sp queue ends.

Reasons:
- The host has 63 GB RAM and 32 cores shared with one training process and its 7 loader workers. A memory failure
  would kill an Sp fit, which costs more than the wait.
- Inference needs only about 3 GB of GPU memory, so GPU memory alone would fit.
- Concurrency does not change the arithmetic, so the gate would decide either way. The registered order is lock
  first.

Expected start about 12:45; gate about 13 min, TT1 rows about 25 min; expected end about 13:30, before the 15:51
deadline. Cost about 0.4 USD within the lease cap.

This driver never writes RELEASE; the lead releases pn1fs after the Sp fits are fetched and verified. The driver
writes `/mnt/t7/smad_next/vast/pn1fs/tt1/TT1_DONE` only after the result tar and logs are verified with a second
local copy. The FS1 driver or the lead holds the release until then.

## 5. Reads and rules

- **Reader:** `src/TT1/tt1_read_fs.py` (sha256 below; mock-tested with one network missing). It uses the registered
  TT1 reader's statistics unchanged (`tt1_read.py` `4546f520…`: pools U_p, references, 2,000 bootstrap draws
  `default_rng(20261122)`, inflation k for packs, mid-rank AUCs). Family lower bounds are clipped at 0, as in the TT1
  reader correction.
- **Per network:** R1 to R5 as in TT1-S.
- **Printed for every network (no rule):**
  - F̄ at cut-offs 0, −0.5, −1, −2;
  - geometry-224 and geometry-112 flag shares;
  - border-reference flag shares per family;
  - R_cam 5th-95th percentile;
  - unseen family medians minus R_cam median.
- **Arm verdicts** for TT-H1 to TT-H5 use the per-network rules of TT-H1 to TT-H5 (TT-H4 for B and Sb against A of
  the same seed). An arm verdict needs at least 4 of 5 passing seeds with the same per-seed verdict. Otherwise it
  reads "mixed (n of m seeds ...)", or "not available" with fewer than 4 passing seeds.
  - TT-H1 per seed: "fails as predicted" (at least 4 failing families for A, at least 2 for B and Sb); "transfers"
    (every family's upper bound ≤ 10%); otherwise "not as predicted".
- **TT-H6 (descriptive):** "X has lower genuine flag rates than Y on seeds 403-407" only if ΔF̄ ≤ −0.03 with the
  paired interval excluding 0 on at least 4 of 5 seeds where both networks passed. Otherwise "not distinguished", or
  "not available". Pairs: B − A, Sb − A, Sb − B. The intervals capture image sampling only, not training variance.
- **Read once,** by the owner, after the result tar is verified. No re-run after seeing scores, except an
  infrastructure failure re-run unchanged.

## 6. Scripts (sha256 at this commit)

| Script | sha256 |
|---|---|
| `src/TT1/rented/remote_tt1_fs.sh` | 88c179e570ceb18c74d725a6ea1e7976a935303a78a12846161261458e0cd85e |
| `src/TT1/rented/drive_tt1_fs.sh` | 80cacd1845a67cfdeade75f766b3f34ab60e09f9bf6e9a7e330ea0b69bd4e0b5 (15 tasks) |
| `src/TT1/rescore_tf32.py` | 0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5 |
| `src/TT1/gate_check_fs.py` | 6d1962bf6a0811b250bbdf81e18adce27838f4388794cc5ae6d73a772b823f55 |
| `src/TT1/tt1_read_fs.py` | fe9f97401f3633c2947b23af685be5587e741ed97163d64810e971469f5b4a62 |

## 7. Amendment after the pre-run check (`date`: Fri Nov 13 07:34:47 AM CET 2026; registered at the git commit that adds this section, before the job starts and before any score)

Pre-run check by the experiment-reviewer (opus): GO WITH FIXES (one blocker, three majors, six minors). Applied:
- B1 (blocker): the FS1 driver would have released pn1fs when the Sp queue ended. The lead wrote "all sp tt1" to
  `/mnt/t7/smad_next/vast/pn1fs/QUEUES` (07:35); the lead touches DONE_tt1 only after this driver writes
  `tt1/TT1_DONE` (two verified copies). The job writes nothing under /workspace/pn1 except taking the lock.
- I2 (lead agreed, 07:35): if all 15 networks fail the byte-identity gate, the outcome is recorded as a platform
  finding and the block is "not available"; no fallback tolerance gate. (The untested element: pn1_score.py loaded the
  full last.pt, rescore.py rebuilds base weights + last_trainable.pt.)
- M1: TT-H6 gains the pair B − Sb (sentence "B has lower genuine flag rates than Sb on seeds 403-407", same rule), so
  "Sb above B" can be confirmed.
- M2: printed per arm (F̄, F_max, S_F, Ā) and per pair (ΔF̄): mean ± SD over passing seeds and the sign count. Stated:
  the −0.03 bar equals the size of the 401/402 B − A effect, so "not distinguished" is likely even at that effect.
- M3: TT-H4 for B and Sb needs A of the same seed; a seed whose A failed counts as unavailable for B and Sb, so an arm
  with fewer than 4 such seeds reads "not available". Mock re-run with A missing on two seeds and Sb on one
  (`tt1_read_fs_mock2.json`): A, and B/Sb TT-H4, read "not available"; others read normally.
- m1: agreement is counted on the bare per-seed verdict; labels ("geo reference weak", "uninformative") are appended if
  any seed carries them. m2: TT-H1 "uninformative" label restored (R_cam share > 5% on a seed). m3: printed family
  intervals clipped at 0, Clopper-Pearson printed beside zero-event families.
- I3: printed per network: max and median |Δ| and decision changes between the job's TF32-off R_cam logits and the
  stored TF32-on scores. τ_cam labelled "from the stored TF32-on scores, applied to TF32-off logits (printed only)".
- m5: the job asserts GPU UUID GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad and records cudnn.benchmark,
  cudnn.deterministic, TF32 flags and SDPA backend flags in versions.txt. I4: skip if under 60 min remain before the
  15:51 deadline (epoch check after the lock). m4: the pull loop starts at about 12:40 (it stops after 3 h).
- m6: deviation from TT1-S §9 declared: §9 planned a tolerance gate, 16 networks and one network tar; this block uses
  byte identity on the FS1 evaluation rows (TF32 matched), 15 deciding networks (replicate not scored) and per-tar pins.
  On a FATAL (crash) result the release is held for one unchanged re-run if time allows. Stale script comments fixed.
- Re-pinned: `src/TT1/tt1_read_fs.py` 87356fd74746b08f621e3e0c4e38554c80f475fae7d0d1f5e7f8634cb144f227; `src/TT1/rented/remote_tt1_fs.sh` 4f22914c6c8cdafba69e9901b1eda4c3629a2dbcc4cfbe29f80a9a8c6a49e16f; `src/TT1/rented/drive_tt1_fs.sh`
  d764237b3a39d41583c6e06ea57b216a6e34244da81fa8b359a49b9775913ced; rescore_tf32.py and gate_check_fs.py unchanged. Mechanics re-tested on the DGX mock host (test mode).
