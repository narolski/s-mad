# MONITOR WCSS 2026-11-16T1841Z (19:41 CET) — smoke v3.1 PASS, HOLD arrays resubmitted

## 1. Smoke verdict: PASS
- Smoke **6340410_401** (ARM=B, 4xH100, TL 20 min, node r18-9, sbatch md5 2d91c81592b446f4214bc20a8debfb54,
  v3 pack sha 189968df...246cc07d verified server-side 18:38Z): ended `sacct State=TIMEOUT Elapsed=00:20:00
  ExitCode=0:0` — TL wall as designed, no crash.
- Live(survivable) log `logs/keep/madation_B_v3sbr_s401/train_stdout.log` (v3.1 lustre keep dir — the v3.1
  logging fix worked; log survived SIGKILL/TL):
  - env v3 built, torch import assert OK (py3.9, cuda 12.1, H100);
  - `training start 19:21:15Z`, LoRA attach OK (trainable 73728 / 149694465 = 0.0493%);
  - trainset 1,600,000 rows / Total Step 6250; ran to `Global Step: 2100` at TL;
  - sustained `Speed 480–527 samples/sec` (≈1 h/seed), `Loss 0.69 → 0.08`, no NCCL/CUDA errors anywhere.
- PASS criteria met: pip from v3 pack OK; H100 sm_90 backward sustained 18 min (both v2 failure modes cleared);
  kill was purely TL. **Gate flipped.**

## 2. HOLD arrays resubmitted (operator authorization 2026-11-16 ~19:30 CET; originals 6334803/6334804/6334807 gone)
| Arm | New job id | Spec | Smoke-line basis for ETA |
|---|---|---|---|
| H1 B (MADation ViT-B/16 LoRA) | **6340883_[401-405]** | gpu:hopper:4, 4xH100, nice 40, TL 6:00 | 480–527 samples/s ⇒ ~1.0–1.1 h/seed; 5 seeds ⇒ seq ~5.5 h, but tasks parallelize as nodes free |
| H3 X (MixFaceNet-MAD) | **6340884_[401-405]** | gpu:hopper:1, 1xH100, nice 41, TL 8:00 | per-GPU batch 256; X ran 0.3–1 h/seed historically |
| H2 L (MADation ViT-L/14 LoRA) | **6340885_[401-405]** | gpu:hopper:4, 4xH100, nice 42, TL 6:00 | dispatch ETA 2–3 h/seed ⇒ TL 6:00 = ~2× margin (—no-requeue, so margin kept) |

- All three PENDING Reason=None at 18:38Z (eligible, awaiting hopper nodes). Partition: 20 mix + 8 alloc + 8
  idle~ (power-save, spin-up on demand) hopper nodes ⇒ wake-up latency minutes; first starts expected well
  within the hour. Result-guard in v3 sbatch skips any seed with existing `$T.tar.sha256` in results.
- Export spec: `--export=ALL,ARM=B|L|X,AD6_L=/lustre/pd03/hpc-narolski-1790461090/smad-next/AD6`; keep dir
  `logs/keep/madation_{B,L}_v3sbr_s4xx|mixfacenet_X_sbr_s4xx/`; results → `AD6/results/` with sha256 receipts.
- Untouched: 6294928 mv30-ABC15 (operator-held). 6310127 H4 SelfMAD finished earlier today (H4 RUNNING→done).

## 3. HOLDS_20261116.md
Rows H1/H2/H3 updated: new job ids + "RESUBMITTED (v3 stack)" status; B: nice 40. Scoring remains follow-up
(pipeline on /home, commit f987c31) — training-dispatch is the deliverable tonight; hand scoring to main when
tars land in `AD6/results/`.

## 4. Risks
- L/14 speed on 4xH100 v3 stack unmeasured (TL 6:00 gives 2× margin vs dispatch ETA; B smoke speed exceeds
  dispatch estimate, so L likely fits; worst case a seed dies at TL and reruns with the guard skipping done seeds).
- Checkpoint save (step 6250, epoch-1 guard) happens only after ~1 h — outside smoke coverage; v2 epochs saved
  fine on Athena with the same code; v3 differs only in pip wheels.
- Node power-saved idle~: add ~few-min wake delay per node.
