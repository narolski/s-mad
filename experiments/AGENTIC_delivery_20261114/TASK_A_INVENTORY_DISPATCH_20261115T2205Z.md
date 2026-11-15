# TASK A — inventory + dispatch decision (2026-11-15T22:05CET / 21:05 UTC) + MONITOR_20261115T2205Z

## 1. Inventory: COMPLETED vs UNSCORED, last 24 h

| Cohort | Job | Cluster | Seeds | State | Scored on frozen FRLL/MAD22? |
|---|---|---|---|---|---|
| MADation B/16 retrain (ours) | 3545814 | Athena | 401–405 | COMPLETED (1,289–1,318 s) | **NO — UNSCORED** (archives SHA-verified, 14-full-archive recovery) |
| MADation L/14 retrain (ours) | 3545813 | Athena | 401–405 | COMPLETED (5,453–5,480 s) | **NO — UNSCORED** (as above) |
| MixFaceNet retrain (ours) | 6310125 | WCSS | 401–405 | COMPLETED; final 405 archive durable SHA 73c31443… | **NO — UNSCORED** |
| SelfMAD retrain (ours) | 6310127 | WCSS | 401–404 | COMPLETED (63,284–63,827 s) | **NO — UNSCORED** |
| SelfMAD retrain seed 405 | 6310127_405 | WCSS | 405 | RUNNING (elapsed 13,109 s at 22:05 CET) | NO — ETA **≈ 16 XI 12:58 CET** (mean 63,540 s; worst 13:05) |
| Frozen networks (Sb 403–407, SelfMAD RW, MADation B/L RW, MixFaceNet RW) | — | GB10 | — | READ DONE 15 XI (amendment f58383c…, results bcd7e820…, 43/43 recount PASS) | **YES — scored & integrated in manuscript (main b728f63)** |

## 2. Dispatch decision: NOT dispatched (0 jobs), with prepared deadlock-breaker
Registered scoring of the retrain cohorts is **HOLD by the registered queue itself**
(COMPUTE_QUEUE.json: MixFaceNet 6310125 → "scientific eligibility/scoring remains HOLD";
SelfMAD 6310127 no admission entry; scoring of retrains "remains pending" — supplement.tex:2511 binding wording).
The 15 Nov author-ruling amendment (71a0cab, SHA f58383c…) enumerated **frozen networks only**;
adding retrained-checkpoint rows to the benchmark population is a NEW registered read scope.
Per governing rules (GO only on SHA-verified reports + registered HOLDs are lifted only by owner/author
action, not by scheduling convenience) I did NOT submit scoring. Prepared instead (append-only, dated):
- Draft amendment AMENDMENT_RETRAIN_SCORING_SCOPE_20261115 (this file §5) ready to file on operator GO;
- Dispatch recipe: pinned RS1 score.py --mode own (script pin 56bb1244…) on frozen FRLL roster
  (manifest SHA 6af62341…) + MAD22 corrected population; platforms in order: GB10 (idle, crops+env local
  at /mnt/t7/smad_next/RS1/crops; ~1.2 h/checkpoint, 15 checkpoints ⇒ run 2-parallel ≈ 9–10 h) or
  WCSS H100 env (already registered for this scorer type), Vast.ai NOT used (cancelled);
- Labelling rule per Task A: retrained rows = "(ours, 5 seeds)" distinct from "(RW)" released-weights rows.

## 3. Third-party detector survey (overnight candidates) — 0 dispatchable
Registry facts (NOTEBOOK.md:108 + ledger): released weights on hand: MADation (all variants),
MixFaceNet-MAD, SelfMAD (WCSS) — already scored/integrated. For the Task-A list:
| Detector | Public checkpoint? | Overnight dispatch? | Missing |
|---|---|---|---|
| FD-MAD | **no public weights** (ledger) | no | weights |
| Inception-MAD (SMDD) | **no public weights** | no | weights |
| OrthoMAD | internal scratch A12 re-implementation only (C1b), no public ckpt registered | no | public weights OR a registered new-read decision for our re-implementation (new workload, needs GO) |
| PW-MAD | **no public weights** | no | weights |
| IDistill | internal production exists but eligibility HOLD (6312778 TIMEOUT; smoke 6312775 failed; "running jobs are not eligible results") | no | eligibility admission + smoke pass |
| SelfMAD++ | not present in any ledger/registry entry | no | unknown — nothing registered |
| MADDDPM | not present in any ledger/registry entry | no | unknown — nothing registered |
C1b's internal arms (OrthoMAD/PW-MAD-style scratch fits) are NOT released-weights comparators and are not
registered for the sealed-benchmark populations — treating them as scoring targets tonight would create
unregistered benchmark rows.

## 4. Backlog position ("9-item backlog locked state")
The 22:05 CET manual cycle before this file found: WCSS — 405 RUNNING (12,568 s then, 13,109 s now),
6294928_[4-13] JobHeldUser-held by user action (NOT dispatched by us; held by the user's own hold);
projects (ACT and new) all JobHeldUser. Athena — squeue EMPTY for plgpnarolski (18:01Z and at poll;
allocation not_active per project watch 23:00 CET: gpu-a100 available but "due to the currently optical
premises" → effectively idle Capacity with nothing queued). Nothing scored since 21:39Z: no cohort
became SCORED; the frozen-network FRLL read remains the only new score set of the evening.

## 5. One-sentence unblock needed from operator/author
"The registered scoring HOLD on retrain cohorts 3545813/3545814 (MADation B/L, Athena) and 6310125
(MixFaceNet, WCSS) is lifted; SelfMAD cohort enters after 6310127_405 completes (~12:58 CET 16 XI);
scoring = frozen FRLL 7,265-row roster + corrected MAD22, registered own-crop pipeline, rows labelled
'(ours)'; results enter tables only after postresult review (GO-on-SHA-verified)."

## Cluster poll @ 22:05 CET (this cycle)
- WCSS: 6310127_405 RUNNING 13,109 s; remaining ≈ 50,431 s ≈ 14.0 h ⇒ **ETA 16 XI ≈ 12:58 CET (mean), 13:05 CET (worst)**; 6294928_[4-13] PENDING (JobHeldUser) — unchanged.
- Athena: queue empty; no dispatch (see §2/§3).
