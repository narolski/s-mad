# Current resource policy — supersedes rental recommendations below

Author ruling, 14 November: **No paid H100 capacity. H100-only work stays on WCSS; A100 work uses Athena as its primary resource.** The existing USD10 fallback remains bounded and may only fund cheaper compatible hardware when it materially accelerates an admissible result. Earlier H100 rental estimates are historical arithmetic, not active recommendations or funding requests. Preserve registered platform requirements; report/defer work that cannot meet its deadline rather than weaken gates. See COMPUTE_POLICY.json.

# Computation coordination for method delivery

Prepared 14 November 2026 by the dedicated computation-coordinator agent. This is an operational plan and queue, not a live daemon or a scientific release. No SSH, submission, cancellation, score access, rental, or spending was performed by this agent. The lead supplies cluster observations and performs cluster mutations through the established locks.

## Current assessment

The immediate bottleneck is a combination of queue delay and scientific-software readiness. Extra GPUs cannot repair missing selection adapters, incomplete GX admission/training preparation, or an unreviewed reader. Do those CPU tasks now while registered GPU jobs age in the queue. Reuse the completed count-balanced ablations rather than train them again.

Evidence freshness:

- Lead reports a read-only WCSS accounting query at about 11:19 CET on 14 November: 6319490, 6319491, 6319494, 6319495, 6319264 and 6319579 were all PENDING. This agent did not independently query the cluster; parent report is the source.
- `ATHENA_SNAPSHOT.json`, observed 14 November 10:22:06 UTC / 11:22:06 CET, records MADation B pending with unavailable nodes and MADation L remaining tasks pending for resources. MixFaceNet completed; one MADation L task completed in 1:31:03. Partition summaries include failed and mixed nodes. A mixed node does not imply a GPU allocation is available to this user or fits an eight-GPU job.
- The current NEXT archive-arrival and local hash-verification cutoff is **15 November 2026, 18:00 CET**. Confirmation may follow afterward. No operational deadline below changes that scientific rule.

## Responsibilities and separation

The computation coordinator owns `COMPUTE_QUEUE.json`, resource placement recommendations, dependency estimates, capacity shortfalls and rental proposals. It does not choose favorable models, alter training batches/steps/seeds to fit a slot, inspect sealed scores, or relax admission gates.

The lead remains the sole WCSS SSH owner, using `/tmp/opencode/wcss-client.lock`, and executes reviewed commands. Athena uses its command and transfer locks; authentication failure is reported without repeated login attempts. A scheduler query failure means unknown state, never an inferred completion. All remote commands are batched where independent; no GPU placeholder or sleeping allocation is used.

There are six roles (including scientific review) and four concurrent agent slots. During execution keep lead, method implementer and computation coordinator active, with the fourth slot used by the independent controls/statistics reviewer needed next. At reviewed-result milestones, rotate the scientific reviewer in for hypothesis synthesis. When no compute intervention is pending, the coordinator records a durable handoff and yields its slot. Reviewers may rotate, but the author of an artifact cannot provide its independent release review. This role is task-driven; no persistent background monitor is claimed.

## Priority queue and useful outputs

| Priority | Work / job | Meaningful output it unblocks | Placement and next action |
|---|---|---|---|
| P0 CPU | Repair/review batch-C reader provenance and stage already verified archives | Count/class-controlled negative-content ablation | Local bounded CPU work; no additional fits. Registered reader and independent review govern score access. |
| P0 CPU | Complete NEXT native adapters and admission; GX admission/training preparation | Makes queued outputs scientifically usable | Local synthetic implementation and independent review before scientific reads. Do not buy GPUs while this is the only blocker. |
| P1 | SbFM supplementary scoring, 6319579 | Required support for first challenger in fixed order | Existing H100 scoring environment; two-hour limit. Preserve existing submission. |
| P1 | Comparator rescore retry, 6319491 | Paired yardstick for resolution challengers | H100, same pinned environment and exact gate; approximately 45-minute estimate, 2.5-hour limit. |
| P1 | DINOv3 rescoring, 6319264 | Complete backbone challenger evidence | Existing registered platform; four-hour limit. No duplicate submission. |
| P1 long | Fifteen 512-pixel fits, 6319490 | Three five-seed registered arms | H100: about 4.398 h per fit projected from smoke; six-hour per-task limit. Keep array queued; inspect concurrency and actual allocation before changing scheduler-only settings. |
| P2 | GX ten fits plus scoring, not ready | Rendering-control candidate | Estimated 10–15 H100-hours plus 1–2 scoring hours; not measured. Admission/manifests/review first. Existing generation is complete; do not regenerate. |
| P2 short | IDistill and MADation diagnostics, 6319494/6319495 | Decide whether baseline recovery can proceed | 30/15-minute limits, separate diagnostic namespaces. Preserve failed attempts and existing production. |
| P2 | Athena MADation arrays | Released-comparator replication | Respect existing eight-GPU requests and recipe. Do not turn a distributed eight-GPU job into a one-GPU job as a queue optimization. |
| P3 future | Selected method confirmation | Fresh-seed confirmation | Reserve capacity after nominated recipe and comparator requirements are fixed; do not pre-train alternative candidates on confirmation seeds. |

These priorities express dependency urgency, not permission to alter Slurm priority or scientific challenger order. Ready independent jobs should run concurrently where allocations permit. Longer necessary tasks should keep queue age while short dependent scorers use suitable backfill opportunities. Do not cancel/requeue merely to chase speculative start forecasts.

## Capacity arithmetic and latest starts

Use `latest_start = cutoff − conservative_runtime − transfer_and_hash_buffer − prerequisite_time`. Record optimistic, central and conservative scenarios separately; never convert `squeue --start` into a guaranteed reservation. Unknown prerequisite duration means latest start remains conditional.

The following **planning examples** use a one-hour transfer/hash buffer, chosen operationally and not measured. Replace it with measured pack/output rates; a slower transfer moves starts earlier. They assume prerequisites are already complete and all listed parallel slots begin together:

| Work | Capacity scenario | Compute allowance | Conditional latest start for 15 Nov 18:00 CET |
|---|---|---:|---|
| SbFM supplement | Existing single allocation | 2 h scheduler limit | 15 Nov 15:00 |
| Refit rescore | Existing single allocation | 2.5 h scheduler limit | 15 Nov 14:30 |
| DINO rescoring | Existing single allocation | 4 h scheduler limit | 15 Nov 13:00 |
| 15 × 512 fits | 15 concurrent H100s | 1 wave × 6 h | 15 Nov 11:00 |
| 15 × 512 fits | 5 concurrent H100s | 3 waves × 6 h | 14 Nov 23:00 |
| 15 × 512 fits | 3 concurrent H100s | 5 waves × 6 h | 14 Nov 11:00 — already passed at snapshot |

Fifteen fits require about **66 H100-hours** by the smoke projection, or **90 GPU-hours** at all task limits. Those are alternative planning estimates, not extra workloads. Task granularity matters: total GPU-hours divided by wall time is a necessary capacity check, not a schedule guarantee. At three slots, expected-runtime arithmetic could still differ from the conservative table; report that uncertainty rather than declaring failure. A smaller scientifically permitted set must come from the registration, never from the coordinator choosing favorable seeds.

Preliminary shortfall: three H100 slots alone no longer provide conservative completion of all fifteen 512 fits by the current cutoff. Five slots starting by 14 November 23:00 would provide three conservative waves under the example buffer. Actual WCSS slot availability and array concurrency need a lead query before this becomes a procurement request. The short scorers additionally need their own slots or explicitly scheduled time. GX adds 11–17 estimated GPU-hours only after its non-compute blockers clear.

## Cluster optimization checklist

1. Query only relevant task states, requested GPU count/model, array concurrency, limits, reasons and measured step rates; retain timestamped receipts. Inspect completed result archives by hash only until admitted.
2. Confirm whether a blocked workload is CPU/software, allocation, storage/transfer, failed smoke or scientific admission. Assign the remedy to that cause.
3. WCSS uses registered H100 environments, large-pack staging in `$TMPDIR`, durable per-task archives and `--extra=FORCE_RM_TMPDIR`. No node-exclusion lists. Enforce the local free-space rule before transfers exceeding 1 GB.
4. Athena may take only GPU-compatible registered workloads. Existing A100 tasks keep their environment; new approved tasks use the pinned image. No computation/build on login nodes; use approved MEMFS/RAM budgets for packs and few large files on shared storage. Current account/fair-share and limits must be refreshed; historic grant balances are not live available capacity.
5. Check legitimate account/partition eligibility and backfill fit. Adjust limits only from measured runtime plus margin, with no loss of required steps/scoring. Never reduce GPUs in a multi-GPU algorithm without methodological review.
6. A100 is not a silent replacement for H100. Cross-platform paired training can alter results. Any relocation needs the registration's exact platform and source-order rules, reviewed amendment if required, and the full byte-identity scoring gate; the same GPU marketing family alone is not sufficient.
7. Retain successful partial scoring archives with hashes where the existing runner supports it. An interrupted partial is not admitted as complete. Never overwrite a successful output or race two implementations for the most favorable result.

## When to escalate additional compute

Operational defaults proposed here, not scientific gates:

- **Warn now** when all critical GPU paths remain pending and their start times are unknown; give scenario bounds and the next decision time.
- **Prepare an actionable capacity proposal** whenever conservative slack is less than rental setup + transfer + smoke + one recovery margin, or measured available slots cannot complete the ready workload by cutoff.
- **Escalate immediately** for repeated node unavailability or a deadline-threatening queue/resource change. Do not wait for the cutoff to pass.
- **Do not recommend a lease yet** if its workload is unreviewed, its required data is absent, a necessary CPU blocker cannot finish before the lease would help, or its hardware cannot satisfy the registered experiment.
- Reassess at actual job starts/completions, failed gates, measured runtime deviations and planned decision times. During an active work turn, batch a fresh query when evidence becomes stale enough to affect placement. No unattended monitoring is implemented by this plan.

The present recommendation is to prepare an H100 fallback specification and resolve the reader/admission blockers in parallel. No current price, lease availability or account balance has been inspected; therefore no priced rental recommendation or claimed savings is made.

## Required Vast.ai capacity proposal

Before requesting additional spending, the coordinator delivers the following filled record (not a generic request):

- Decision timestamp and deadline; exact scientific output and downstream decisions unblocked.
- Existing job IDs/status, source receipts, current slot scenarios, and the best cluster-only completion range.
- Ready script/code hash, registration and independent review; eligibility for relocation and source-precedence/duplicate-prevention rule.
- Exact GPU model/variant and count, measured VRAM, CPU/RAM, scratch and durable storage requirements; pinned software/container hashes and host-driver constraints.
- Each input pack: bytes, SHA256, current host and transfer route; measured transfer rate and predicted upload/download duration; data handling terms checked for those assets.
- Setup, eight-image smoke and full reproducibility-gate duration; acceptance and abort criteria; no sealed rows in plumbing tests.
- Current timestamped offer ID, region, availability and reliability evidence, hourly instance price and storage/network charges. Obtain live provider evidence through the authorized tools; do not reuse old prices.
- Useful GPU-hours, billed setup/transfer/idle hours, conservative runtime, hard lease stop time, total cost cap and verified account balance/remaining authorized envelope. Calculate `total = rate × billed hours + storage + transfer + explicit contingency` with unit clarity (per GPU versus per instance).
- Two alternatives where available: minimum capacity to meet cutoff and faster capacity; show expected time saved against the cluster scenarios and which uncertainties remain.
- One named owner for launch/monitor/teardown, budget alarm, checkpoint/archive recovery, SHA verification and teardown receipt. Destroy the lease when its ready queue drains or cap/abort criterion is met; never rent to wait on missing manifests.

Standing WORKFLOW.md confines normal Vast use to data generation needed by other experiments, when WCSS wait exceeds rental runtime; it also specifies approval boundaries for spending beyond balance, a lease over USD20, or cumulative Vast over USD100. Current requested fallback may involve training/scoring and therefore requires an explicit scope disposition under that policy before purchase. Prior authorization for a completed MAD22 rental is not reused as a new lease budget. The user's request authorizes concrete extra-capacity reporting, not an unbounded purchase. The lead should apply any later explicit session authorization without asking redundantly.

## Sources and handoff

Sources: `ATHENA.md`; `OWNER_BRIEF.md`; `WORKFLOW.md`; `experiments/RECORDS_ledger/CODEX_DELIVERY_20261114.md`; current `METHOD_PLAN.md`; `ATHENA_SNAPSHOT.json`; parent WCSS observation; existing submission receipts under `/mnt/t7/smad_next/coordination_20261114/`. `COMPUTE_QUEUE.json` encodes the current recommendations, unknowns and conditional times. The lead integrates it into the overall state record. This role does not claim active monitoring after its task finishes.
