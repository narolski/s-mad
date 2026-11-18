# Scientific review and hypothesis development [AGENTIC]

Prepared 14 November 2026 in response to the author's request for a scientific-review agent. This is a bounded initial review of published local result reports and existing registrations. No candidate archive, raw score, image, checkpoint or sealed benchmark was opened. No job was submitted. The hypotheses below are explanations to test, not findings.

## Purpose

Turn reviewed experimental outcomes into the next most informative decision under the remaining time. Optimize scientific information and claim clarity, not the chance of obtaining a small p-value. A reliable null, a disproved mechanism, a diagnosed invalid control or a narrower defensible claim can be the best result.

The scientific-review agent owns this hypothesis queue and an evidence-to-claim synthesis. It does not own the detector implementation, approve its own proposed experiment, choose checkpoints or seeds, or authorize a benchmark read. Independent methodological review and independent conclusions review remain separate assignments. If this agent substantially designs a protocol, another reviewer must approve it.

The approved NEXT rule, fixed candidate order, admission requirements and fresh confirmation remain unchanged. An outcome-inspired hypothesis belongs in a dated prospective amendment or a new cycle; it cannot reinterpret an old primary test. MAD22-informed ideas are labeled as such. FRLL overlap and earlier exposure remain disclosed.

## When the lead activates it

| Event | Input packet | Required response |
|---|---|---|
| A scientific result has passed independent conclusions review | Registration and amendments; full per-seed result table; intervals; controls; failed/missing runs; review disposition | What changed in our understanding; strongest remaining alternative; continue/stop/next-test recommendation |
| A registered test is invalid or cannot be read | Failure evidence and affected dependencies, without treating missing scores as negative science | Cheapest repair versus abandon/defer; separate implementation failure from hypothesis failure |
| Compute coordinator reports a material delay or capacity change | Measured runtime, queue uncertainty, exact deadline and resource options | Re-rank by time to a useful conclusion; identify CPU-only or existing-output work that can proceed |
| Two reviewed findings conflict | Both complete reports and protocol differences | List plausible differences; propose one discriminating comparison instead of averaging away the conflict |
| An important gate is about to close | Current evidence, unfinished hypotheses and mandatory current-cycle work | Freeze the claim table; stop optional exploration; preserve unresolved questions |

Use event-driven review, not continuous speculative brainstorming or repeated peeking at accumulating results. The lead sends a short task for each meaningful event and records its output. No permanent background agent or autonomous wake-up mechanism is installed by this document.

## Coordination with the other roles

1. **Lead → scientific review:** deliver one immutable result packet and the decision that needs resolving. Include the actual deadline, not an assumed urgency.
2. **Scientific review → method agent:** send a hypothesis card with the cheapest distinguishing experiment and explicit alternatives. Ask for implementation feasibility, not an unconstrained search.
3. **Controls agent → scientific review:** challenge whether the comparison actually separates the explanations; identify data leakage, processing mismatch and controls that are trivial by training design.
4. **Statistics agent → scientific review:** assess estimand, power/precision, dependence, multiplicity and whether the proposed outcome would be informative. A low-power null cannot falsify a useful effect.
5. **Computation coordinator → scientific review:** return earliest credible result windows, dependencies, GPU-hours, transfer/setup costs, portability risks and alternatives. No current price or queue ETA is assumed.
6. **Scientific review → lead:** recommend RUN, REPAIR, DEFER or STOP, with the claim gained or lost for each possible outcome. The lead resolves disagreements in writing and dispatches only registered, independently reviewed work.
7. **After review of the new result:** close the card as supported, contradicted, inconclusive or invalid under its original rule; create at most one targeted successor if justified. Retain the original prediction and unfavorable result.

There are now **six roles with four concurrent slots**, including the lead. Roles are durable responsibilities, not six continuously running processes. Suggested rotations:

- Result interpretation: lead + scientific review + statistics + controls.
- Experiment preparation: lead + method + controls/statistics reviewer + computation.
- Execution: lead + method + computation + the reviewer needed next.

The scientific agent yields after its recommendation and returns at the next event. Do not displace a critical implementation or admission review merely to keep every role visibly active. Never let the author of an artifact provide its independent approval.

## Hypothesis card and ranking rule

Every card records: ID and date; motivating reviewed observation and source; hypothesis; strongest alternative; distinguishing predicted pattern; falsifier and inconclusive region; cheapest valid test; existing work to reuse; required registration/review; dependencies and estimated end-to-end time; outcomes-to-claims mapping; named owner and reviewer; next decision.

Keep at most three active cards. First prioritize a completed, admissible experiment that resolves an existing ambiguity; then a cheap repair or analysis that unlocks a consequential result; then a new experiment with a feasible review-to-result path. Rank by the decision it resolves, validity of the distinction, chance of an interpretable answer, time to that answer, and resources required. Avoid numerical “information gain” scores without a justified model.

“Promising for significance” is not a ranking criterion. Do not add seeds until significant, remove an unfavorable family, change margins after seeing results, or repeat an inconclusive test without a documented precision or design improvement. Infrastructure retries preserve failed attempts and use the original permitted retry rules.

## Initial ranked hypothesis queue

### SR-1 — Does matched-negative content matter beyond row count and class balance?

**Observation:** In the development ablation, full training Sb exceeds the version without matched negatives Sp by +0.049 AUC [0.028, 0.073], with all five paired gains positive. Positives alone, Sp − B, give −0.008 [−0.033, 0.022]. Removing the negatives also changes 312 unique images, 624 rows and class composition. These results cannot isolate content from those changes. [AB1 result, amendment-5 analysis]

**Hypothesis:** The matched-negative content contributes beyond row count and class balance. **Alternative:** altered sampling/class composition explains much of the apparent gain; or negative-image diversity rather than the specific control content is responsible.

**Cheapest distinguishing test:** Reuse the completed, unopened batch-C fits: Sb − SpV and BN − BV under amendments 7/7b. Do not launch duplicate fits. Sb/SpV share row count, class mix and positive repetition; BN/BV test matched negatives without splice positives and with identical positive rows. Unique-image diversity is still not matched.

**Prediction and decision branches:**
- Registered H-c1 “present” supports a content-or-diversity effect beyond row count/class mix.
- H-c2 “present” supports an effect without splice positives under this construction.
- If H-c1 is absent or inconclusive, the previous count/class-mix explanation remains possible; do not say the original result was disproved solely from a wide interval.
- If H-c1 is present but H-c2 is not, an interaction with positives is plausible, not established; the registered interaction is descriptive.
- Neither contrast proves identity-specific recognition or isolates seam-only from same-person negatives.

**Falsifier:** Apply the original registered effect criterion and inconclusive region unchanged. The registration's “absent” bound can rule out its useful-effect size; a merely nonsignificant estimate cannot. A result explained by the remaining diversity mismatch limits the content-specific claim.

**Time and dependencies:** Zero additional training GPU-hours. CPU interpretation runtime is not yet measured. Admission depends on the repaired overlay guard, correct recovered-archive paths, once-only protection, required committed learner references and independent review. The statistics plan records these blockers. This is the first priority because the expensive work already exists.

**Next action:** Method/statistics finish the reader and companion reporting; independent reviewer clears exact sources; lead releases the registered development read; scientific review receives the reviewed result packet. The S0/S3 factorial remains contingent on a consequential unresolved question, not automatic.

### SR-2 — Can matched rendering controls reduce the rendering shortcut without losing attack sensitivity?

**Observation:** Sb flags 78–90% of one-photo MIPGAN renders and 98–100% of same-person renders. Two-person versus same-person AUC is only 0.619–0.690, while one-photo render versus camera AUC is 0.992–0.998. This leaves a strong rendering explanation. [PR1, GD2]

**Hypothesis:** Supplying matched one-photo and same-person renders as controls can reduce rendering-driven decisions while preserving discrimination of two-person attacks. **Alternative:** training merely shifts all manipulated images toward genuine; or the apparent improvement is specific to one generator and low-level statistics.

**Cheapest distinguishing test:** Complete the already registered GX admission/training/selection path. Generation completion is not image admission. Reuse its paired constructions, identity checks, fixed seeds and registered controls; do not create a new rendering arm to bypass current constraints. Optional MIPGAN-II observations retain their registered descriptive status.

**Distinguishing prediction:** Lower one-photo/same-person render responses together with retained attack detection and improved matched two-person ranking. A lower false-alarm rate alone is insufficient. Inspect registered same-data simple-cue references and the prescribed transfer controls.

**Falsifier / inconclusive region:** Apply the original GX and NEXT decision rules to current work. Failure of attack-preservation or required control gates defeats the joint claim. An inconclusive ranking interval or insufficient admitted data leaves the mechanism unresolved. Any new equivalence bounds or cross-engine confirmation test require prospective registration; none are invented here.

**Time and dependencies:** Existing plans estimate 10–15 H100-hours for ten fits plus 1–2 scoring hours, not a measured runtime. Image admission, manifests, learner preparation, runners and independent review precede fits. Computation coordinator supplies a credible end-to-end window; extra GPUs do not repair missing admission/code. No guaranteed pre-cutoff completion is asserted.

**Claim consequences:** Success supports resistance to the tested rendering controls, not universal shortcut freedom. Failure is scientifically useful evidence that this training intervention does not isolate the claimed signal at the tested resolution/dose.

**Next action:** Lead and computation coordinator establish whether current registered GX work can finish admissibly. If not, preserve it for later and do not weaken gates or replace seeds to fit the deadline.

### SR-3 — Are the current gains engine-specific, or do they survive stronger blending controls?

**Observation:** On the face-plus-halo blend-versus-warp diagnostic, Sb AUC is 0.889, B is 0.879, and the paired gain is +0.011 [−0.010, 0.031]. The seed-level interval is wider. All methods remain consistent with low-level blending/noise cues; in-domain hand-crafted references reach 0.925/0.917. These references are not a like-for-like generalization contest. [XF1]

**Hypothesis:** Part of the training benefit is tied to the familiar construction rather than a transferable identity-related signal. **Alternatives:** a real transfer effect exists but is too small for the present panel; low-level blending cues transfer while identity information adds little; the grey surround/halo changes the task.

**Cheapest next evidence:** First consume the existing registered SbFM engine-crossed and same-data-reference outputs through the approved reader, with all current controls. SbFM has trained on FaceMorpher, so FaceMorpher cannot be called its excluded engine. A better in-engine score alone does not answer this hypothesis.

**Distinguishing prediction:** A transferable benefit should persist on a genuinely excluded construction and identities under matched processing, without depending on the image surround, and beyond the prospectively specified simple-cue comparison. A disappearing gain across engines supports construction dependence only if the comparison has adequate precision and matched difficulty; otherwise it is inconclusive.

**Falsifier / limits:** No supported transferable advantage under a sufficiently informative registered design limits the transfer claim; it does not prove that all identity information is absent. The current XF1 result does not license a claim that Sb detects blending better than B or recognizes identity mixing.

**Time and dependencies:** Reuse existing results first; no new fitting is recommended now. A new untouched panel or eroded-hull test is deferred until separately registered and capacity is demonstrated. XF1 explicitly places its optional seed-plus-block/eroded-hull follow-ups after the deadline. Do not turn a repeated re-analysis into independent confirmation. Exact new-test runtime is unknown.

**Claim consequences:** A clear null or shortcut explanation strengthens the controlled-evaluation contribution while narrowing the training claim. A valid transfer gain motivates a fresh confirmation cycle, not an immediate benchmark opening.

**Next action:** Controls/statistics map existing engine/identity exposure and references; computation identifies whether any residual cheap test can finish without delaying current selection. Otherwise defer and write the limitation explicitly.

## Time discipline and reporting

The current scientific archive/hash cutoff remains 15 November 18:00 CET; confirmation can follow under the approved rule. It is not replaced by an operational meeting schedule. For every proposed experiment, the computation coordinator calculates latest useful start from measured or clearly labeled estimated setup, queue, runtime, transfer, validation and review costs.

As an operational default, in the final 60–90 minutes before a relevant delivery milestone, prioritize collecting, hashing, validating and reviewing already-produced evidence rather than optional new exploration. This is discretionary planning, not a new scientific cutoff: the lead uses actual remaining work and measured durations, and never postpones the registered deadline. If a short existing task can safely finish and unblock a required result, it remains eligible. No speculative fit is justified merely because a GPU is idle.

After each event, the scientific agent returns a compact memo:

1. **What changed:** at most three evidence-backed findings, with source and scope.
2. **What remains unexplained:** the strongest competing explanation and the claim it limits.
3. **Recommended decision:** RUN / REPAIR / DEFER / STOP, named owner, dependency and expected result window.
4. **What each outcome would mean:** positive, null, inconclusive and invalid branches.
5. **Queue update:** at most three active hypotheses, with one displaced or closed when another enters.

Do not use the borderline MAD22 non-inferiority result (3.37% vs 4.72%; difference −1.4 pp [−3.51, +0.98]) as evidence that superiority is nearly guaranteed. It is development-exposed, not a basis for optional stopping or favorable subset selection. The scientific objective is a defensible account of what works, why, and under which controls.

## Source record

- `experiments/AB1_protocol-ablation-and-replication/result.md`, registered amendments 7/7b in `prereg.md`.
- `experiments/PR1_protocol-reads-existing-networks/result.md`, GD2 and its reviewed interpretation.
- `experiments/XF1_ffhq-facemorpher-matched-render/result.md`.
- `experiments/FINAL_sealed-benchmark-read/result.md`.
- `experiments/GX1_gan-morphs-in-training/prereg.md`.
- This workflow's method, control, statistical and computation plans; all prospective choices remain subject to their documented registration and review requirements.
