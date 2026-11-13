# DRAFT: TT1 FS1 block, the 16 fresh-seed networks on the TT1 pools

Status: draft, prepared on 13 Nov 2026 (review REVIEW_TT1_20261113.md, step 7 and F9). It is not registered and
nothing has run. It is to be registered as a TT1 amendment, with the pins below, after FS1's own registered read is
committed (about 09:00), and before any FS1 network is scored on a TT1 row.

## 1. Networks

- The 16 FS1 fits, last checkpoint: A, B, Sb at seeds 403-407, plus the replicate A seed 401. They were trained by FS1
  on host pn1fs (A100 PCIe 40 GB, torch 2.2.1 image).
- Pins come from FS1's verified copies in `/mnt/t7/smad_next/PN1/results_fs/<task>.tar.sha256` (`fs_kept/`). The
  driver writes them into `nets_pins.txt`, and the host checks every tar against them.
- **Deciding networks:** A, B, Sb at seeds 403-407 (15 networks).
- **Printed only:** the replicate A_s401 ("platform plus nondeterminism" against A_s401 of tt1c; it enters no rule).

## 2. Per-network gate (re-registered explicitly; review F9)

**Rule, quoted exactly:** "a deciding network that fails the gate makes the decision 'not available'; never read on
one seed."

- The gate is applied per network.
- A network that fails is not scored on TT1 rows, and every read that needs it is printed "not available (failed
  platform gate)".
- An arm statement needs at least 4 of 5 seeds that pass the gate and agree (section 4). If fewer than 4 seeds pass
  for an arm, every decision involving that arm is "not available".
- No tolerance is changed after seeing a gate.

**Gate rows:**
- Every row of the FS1 development evaluation manifest `pn1_eval.csv` (sha256 `f0f29f22…`, 19,797 rows; development
  only; its builder asserts no benchmark row).
- Scored in the manifest order, batch 64, with TF32 on, as pn1_score.py did when it stored each fit's
  `scores_eval.npz`.
- Scorer: `src/TT1/rescore_tf32.py` (runs `src/PN1/rescore.py` 6f6eede7… unchanged after switching TF32 on). The model
  build is rescore.py's, from base weights plus the trainable tensors.
- The rows span the whole logit range: camera photos, ladder rungs, morphs, FFHQ genuine and FFHQ morphs.

**Criterion:**
- Byte identity of the float32 logit on every row against the stored `scores_eval.npz`, per network
  (`src/TT1/gate_check_fs.py`).
- This is expected on the same host and stack.

**Why not the 3,417-row TT1 gate:** FS1's stored FFHQ scores were made by pn1_score.py (TF32 on, whole-manifest
batching), not by rescore.py. Matching TF32 and batching makes byte identity the right criterion.

**TT1 rows** for passing networks are scored with rescore.py unchanged (PyTorch defaults, TF32 off), exactly as for
seeds 401/402, so the 401/402 and FS1 numbers come from the same scoring path.

## 3. Pools, reader, rules

- Same list (`tt1_score.csv` `c0055b51…`, fam tt1, plus fam gate for R_cam / R_ffhq / M_ffhq).
- Same pack (`tt1_pack.tar` `2109f742…`) and same pools.
- Reader `tt1_read.py`, extended to seeds 403-407 (pin at registration). Reads R1-R5 unchanged.
- Hypotheses TT-H1 to TT-H5 are evaluated per arm with the 5-seed rule: an arm verdict needs at least 4 of 5 seeds
  with the same per-seed verdict, and otherwise reads "mixed".
- TT-H6 stays descriptive. "X has lower genuine flag rates than Y on seeds 403-407" is printed only if ΔF̄ ≤ −0.03
  with the paired interval excluding 0 on at least 4 of 5 seeds.
- No arm, seed or threshold is chosen from TT1. FS1's frozen contrasts and the MS1 arm choice are not revisited.
- Printed for the review's leads:
  - B − A and Sb − B per seed at cut-offs 0, −0.5, −1, −2 (H-new-3 slope F(−0.5) − F(0), Sb against B);
  - geometry-112 and border flag shares per arm;
  - R_cam spread and unseen medians in logits and in u.

## 4. Platform and order

**Preferred: pn1fs (the FS1 host).**
- It already holds the FS1 pack and the 16 result tars, and its stack is the one that stored the gate scores.
- Only `tt1_pack.tar` (8.1 GB) must be staged there. At tonight's 1.25 MB/s that takes about 1.8 h, so stage it now
  with a bandwidth limit, while the fits run.
- The scoring job takes the host's FS1 queue lock (`/workspace/pn1/fs_queue.lock`), so it never runs at the same time
  as a fit. It starts after FS1's 16 fits and before any later queue (the Sp fits) that takes the lock.
- **Disk:** the job needs at least 30 GB free (it checks). The host has 100 GB; a fit uses about 35 GB; the staged
  pack is 8.1 GB.
- **Release:** the FS1 driver must not release pn1fs before TT1's `/mnt/t7/smad_next/vast/pn1fs/tt1/TT1_DONE` exists.
  `drive_tt1_fs.sh` writes it only after the result tar and logs are verified with a second local copy. This needs one
  line in the FS1 driver, or a hold by the lead.

**Alternative:** a fresh A100 lease with tt1_pack.tar and pn1_pack_fs.tar (16.9 GB, about 4 h upload tonight). Not
recommended.

**Cost on pn1fs:**
- Gate: 16 × 19,797 rows at about 400 rows per second, about 13 min.
- TT1 rows: up to 16 × 34,411 rows, about 25 min.
- About 0.3 USD at 0.47 USD/h. No new lease.

## 5. Scripts (sha256 at this draft; re-pinned at registration)

| Script | sha256 | Mechanics test |
|---|---|---|
| `src/TT1/rented/remote_tt1_fs.sh` | `88c179e5…` | tested on the DGX with a mock host tree, test mode, one 401 network (whose rows differ by design): pins, lock, extraction, gate scoring, per-network gate decision ("row sets differ" → not scored) work. No FS1 score was opened. |
| `src/TT1/rented/drive_tt1_fs.sh` | `2c7e23b4…` | syntax only |
| `src/TT1/rescore_tf32.py` | `0d0b6b6f…` | |
| `src/TT1/gate_check_fs.py` | `6d1962bf…` | |

## 6. Commands for the lead (key and known_hosts of the pn1fs lease folder)

```
# now: stage the pack (resumable; bandwidth limit 1,000 KB/s so the FS1 pulls keep their share)
bash /home/narolski/smad-next/src/TT1/rented/drive_tt1_fs.sh 149.248.21.7 30078 /mnt/t7/smad_next/vast/pn1fs stage
# after FS1's read is committed and the 16 tars are verified locally, and after the TT1 FS1-block registration commit:
bash /home/narolski/smad-next/src/TT1/rented/drive_tt1_fs.sh 149.248.21.7 30078 /mnt/t7/smad_next/vast/pn1fs start
bash /home/narolski/smad-next/src/TT1/rented/drive_tt1_fs.sh 149.248.21.7 30078 /mnt/t7/smad_next/vast/pn1fs loop
```

If the stage step is interrupted, re-running it resumes (rsync --partial).
