# DRAFT: Amendment C2P-R (re-scoring of contrast 2-prime on the training platform)

DRAFT. Not registered; nothing of it has run on pn1fs. Text from the post-result review
`experiments/reviews/REVIEW_PN1_C2P_20261113.md` (e2af82c), section Q2, with the scripts' hashes filled in. It is
registered only by copying it into `prereg.md` at a commit that comes after the author's verbatim yes and before any
C2P-R score exists.

> **Amendment C2P-R (re-scoring of contrast 2-prime on the training platform).** Registered at the commit that adds
> this text, before any C2P-R score exists. Author approval: [verbatim].
>
> *Disclosure.* C2P was scored on an L40S with TF32 off (`C2P_m1.tar` 4e25fcc1ed845229420337021831b54ca107336eb91073d38e7c14b747f8d542),
> but the stored FS1 logits came from A100 PCIe 40 GB with TF32 on (`pn1_score.py`). This contradicted PLATFORM_PINS
> item 7 (f2c2023) and C2P.2's "never two GPU models". All A networks, B 403/404/406/407 and Sb 404 failed the gate's
> maximum condition. The first read (0cb89c5, `c2p_read.json` 62ee0bf430388be8094158f3f3aac429521612751a29c91c2290ae28ff4e5598)
> is final for that run: "uninformative", no method frozen. It printed the hold-out statistics of Sb 403/405/406/407
> and B 405. This amendment was written after those numbers were seen. No hold-out statistic of any other network has
> been computed. Their L40S scores, in `C2P_m1.tar`, were loaded into memory by the reader and not used (attestation in
> `c2p_result.md`, 272ce45). They stay unread until C2P-R has been read, and any later use is labelled post hoc.
>
> *Machine.* pn1fs (instance 60326762, A100 PCIe 40 GB, image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, FS1 pip
> pins). `gpu.txt` must show the UUID of the GPU that trained the FS1 fits (GPU-5bd20020-715e-e9fd-b9d3-f89ca57849ad;
> the remote script aborts otherwise); otherwise no score is made. Fallback, only if pn1fs fails before any row is
> scored: one A100 PCIe 40 GB lease with the same image (not SE1), with a copy of `remote_c2pr.sh` whose only change
> is the GPU-name check 'NVIDIA A100-PCIE-40GB', pinned by sha256 in a commit before it runs; disclosed. In practice
> the 16:00 rule applies. Never L40S, H100 or GB10.
>
> *Networks.* The 15 FS1 tars (sha256 as C2P.2), last checkpoint, read on the host from
> `/workspace/pn1/root/results/PN1/` and checked against `nets_pins.txt` (made from the verified local copies).
>
> *Scoring.* `src/PN1/rescore.py` 6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e, unchanged, run through `src/TT1/rescore_tf32.py`
> 0d0b6b6fb5ebc4d5bdbe15384fcd00e13c0756785ed22743893186e68245d8d5 (matmul and cuDNN TF32 on, as `pn1_score.py`), batch 64, float32. Families af0, ffhq,
> ms1ffhq for all 15 networks, in one job. The hold-out images are uploaded in `c2pr_pack.tar`
> (48e042a89ced7ca1c5a22601796c5830d55e161bfcdfb481e51349032380bf18, 561,582,080 bytes, 1,480 images + the MS1 evaluation manifest d1fab6ad…; every image checked
> against the MS1 pack SHA256SUMS of c11b16bc… by `src/PN1/c2pr/build_c2pr_pack.py` 15112296… and on the host); code,
> base weights and the FS1 evaluation images come from pn1fs's own `pn1_pack_fs.tar` (96c31ae2…). Scripts:
> `src/PN1/c2pr/remote_c2pr.sh` 410f064e7cc3591e5b6173b2b4c156122019a92c169f56656499b78401dae6f8, `src/PN1/c2pr/drive_c2pr.sh`
> 47148bece4545d05b4c4d5c1b20bda0eb647cc8cd30060dc7c6ab22e20d93496. Mock tests (DGX, 13 Nov 09:40-09:44): the remote script ran end to end on one
> network with stand-in paths (lock, pins, extraction, merge of the hold-out images, three families scored, result tar,
> rc 0); the driver's pull was run against that output (3 of 45: "no decision") and against a FATAL result tar
> (C2PR_DONE + C2PR_FAILED); after the pre-run fixes the remote script was run again end to end (rc 0) and a second
> start was refused without overwriting ("a result tar exists already"). Disclosure: the mock runs scored Sb 403 (a
> network that passed the first gate and whose first-run statistics were already printed) on the DGX GB10 with stand-in
> paths; those score files were deleted unopened by the owner. The remote script takes the host's FS1 queue lock
> (`/workspace/pn1/fs_queue.lock`), aborts if the lock is taken after 14:51 CET (its built-in limit: 60 min before 15:51, kept as a margin although
> the lead moved pn1fs's lease deadline to 16:30 on 13 Nov), works in a new folder
> `work_<epoch>`, records the effective torch, cuDNN, TF32 and SDPA settings in `env.txt`, and refuses to run if a
> result tar exists. The driver's `start` refuses unless this amendment, with the remote script's sha256, is in
> `prereg.md` at HEAD; its pull loop runs until C2PR_DONE or 16:00 CET.
>
> *Gate and reader.* C2P.2 gate unchanged (99th percentile ≤ 0.05, max ≤ 0.10, agreement ≥ 99.5% on 6,339 rows).
> `c2p_read.py` 45e72914d960214131a5b4a11aefd2e301a2236e908d77d20d94136c1d7d5840 unchanged, run once with `--c2p C2P_fs.tar` only, output
> `c2p_rerun_read.json`. C2P.3-C2P.5 are unchanged.
>
> *Decision.* The C2P-R verdicts are the inputs to FINAL section 1, which is amended to name them. If a network fails
> the gate, C2P.2 applies and the result is final: no further platform, setting or threshold. A result whose rc is not
> 0 is not read; its score files stay unopened and it counts as a machine failure. A machine failure is repeated once,
> unchanged, on the fallback. If C2P-R is not read by 16:00 CET on 13 Nov 2026, the
> first-run verdict stands.
>
> *Reporting.* Both runs, all 30 gate rows, the cause of the first failure, the 0.15 → 0.10 tightening made before any
> score, and the sentence: "The re-scoring was registered after the protocol-plus-splice networks' storage statistics
> from the first run were seen."

## Machine plan (for the lead)

- Queue name for pn1fs's hold list: `c2pr`; done marker `/mnt/t7/smad_next/vast/pn1fs/c2pr/C2PR_DONE` (+ `C2PR_FAILED`
  on a verified FATAL result); this driver never writes RELEASE.
- Order: C2P-R takes `fs_queue.lock` after the Sp fits end (about 12:45), before the TT1 block, its extension and PR1's
  job. TT1-FS waits for `/workspace/c2pr/DONE` (or `NO_C2PR`, or 13:30) before taking the lock (TT1 owner, restarted 09:47,
  remote_tt1_fs.sh 2feaba74…, note 451c419); PR1 waits for TT1's DONE_FS.
- Time: stage about 10 min (561 MB at about 1 MB/s; can run while Sp fits, as it touches only `/workspace/c2pr`), scoring
  about 20-35 min. C2P-R must be started on the host (waiting on `fs_queue.lock`) before the Sp queue ends and before
  13:30 CET (TT1-FS waits for `/workspace/c2pr/DONE` or `NO_C2PR` only until 13:30, then joins the flock, which is not
  FIFO). If Sp is still running at 13:15, the lead decides whether to write `NO_C2PR`. If the author declines, write
  `/workspace/c2pr/NO_C2PR` at once. The lock must be taken by 14:51 (the script's built-in margin). The lease deadline is 16:30
  (moved by the lead on 13 Nov; cap unchanged); the read-by time stays 16:00.
- Commands after the author's yes and the registration commit:
  ```
  cd /home/narolski/smad-next/src/PN1/c2pr
  bash drive_c2pr.sh 149.248.21.7 30078 /mnt/t7/smad_next/vast/pn1fs stage
  bash drive_c2pr.sh 149.248.21.7 30078 /mnt/t7/smad_next/vast/pn1fs start
  nohup setsid bash drive_c2pr.sh 149.248.21.7 30078 /mnt/t7/smad_next/vast/pn1fs loop > /dev/null 2>&1 &
  python3 -I /home/narolski/smad-next/src/PN1/c2p_read.py --c2p /mnt/t7/smad_next/PN1/c2pr/C2P_fs.tar \
    --out /home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/c2p_rerun_read.json     # once
  ```

## Pre-run check

experiment-reviewer (opus), 13 Nov ~09:50: GO WITH FIXES (findings 1-8). Applied: 1 (pull loop to 16:00), 2 (timing and
NO_C2PR text), 3 (rc ≠ 0 not read; 60-min margin), 4 (fallback sentence), 5 (refuse second start; new work folder), 6
(driver checks the registration and the remote script's sha256 at HEAD), 7 (env.txt as TT1 plus skip_gpu), 8 (mock
disclosure). Not done: the improvement "assert that the MS1 tree's SHA256SUMS belongs to pack c11b16bc…" (every image
is checked against that SHA256SUMS; tying the file to the pack tar would need reading the 14.5 GB tar). The reader
already prints p99 and max |Δ| per network (to be compared with the review's prediction max < 1e-3, printed only).
