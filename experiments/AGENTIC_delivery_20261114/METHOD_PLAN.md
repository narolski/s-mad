# Method development work package: controlled training and transfer

Status: actionable design draft, 14 November 2026. The author authorized implementing the agentic workflow. This document prepares a subsequent research cycle; it is not a new binding selection rule, a completed preregistration, or permission to access sealed benchmarks. No image, latent, candidate score, model checkpoint or benchmark output was opened to prepare it. No job was submitted.

## 1. Preserve the approved cycle

Finish the bound version-3 selection rule (`experiments/NEXT_method-selection-rule/prereg_draft_v3.md`, binding commit `dbeb940`) before introducing another method-selection cycle. Its ordered list, required controls, deadline, five-seed accounting and fallback remain unchanged. A selected challenger needs confirmation at seeds 413–417 under that rule. Missing reader adapters are implementation blockers, not scientific failures.

The current GAN-control candidate (GX) already addresses part of the rendering question. Complete its registered admission, training amendment, manifests, simple-cue learners and reviewed training/scoring path rather than duplicate it under a new name. The generation-metadata audit establishes completed generation logs, not admitted images or scientific success. Its optional MIPGAN-II data remain outside training, exactly as registered. A new matched-count study must not change the existing GX/GXp contrast after the fact.

This draft fixes a work order, not scientific pass margins. Existing numerical margins apply only inside their original registrations. New practical-effect, equivalence and non-inferiority margins must be justified by the statistics owner and fixed in the next registration before its candidate outcomes are read. Until then, implementation can use synthetic fixtures but no confirmatory verdict may be produced.

## 2. Questions and work order

| Priority | Question | Deliverable | Why first |
|---|---|---|---|
| M1 | Does matched-negative content help beyond row count, class balance and exposure? | A count- and sampling-controlled ablation with independent negative-family factors | The existing removal contrast also changes 312 unique images, 624 rows and class mix. |
| M2 | Can rendering sensitivity fall without suppressing true attack detection? | Admitted matched rendering-control training lists and joint detection/control tests | One-photo MIPGAN renders trigger Sb strongly; mere threshold shifts are insufficient. |
| M3 | Does the benefit survive an excluded manipulation engine and new identities? | A locked transfer matrix and one prospectively untouched development confirmation panel | Existing face-only blend-versus-warp gain is inconclusive; already inspected controls cannot become blind confirmation. |

M1 begins with reuse of the already registered batch-C ablation, not new fits. The controls audit and lead report that its fifteen SpV/BN/BV fits completed and were collected unopened; this is completion metadata, not a scientific verdict. Amendments 7/7b of the AB1 registration already test Sb − SpV (matched row count and positive repetition) and BN − BV (negative content without splice positives). Those reads must follow their original registration, provenance gates and independent review. They do not match unique-image diversity: SpV has 312 fewer unique images. The factorial below is a contingent extension only if a material content-versus-diversity or negative-family attribution question remains after that existing study. Do not launch it merely to repeat the same contrasts.

M2 initially consumes the existing GX cycle's registered result, without claiming that its unmatched GXp control answers M1. M3 metadata and dependency audits can proceed while M1 is prepared. Do not introduce additional backbones, new losses or an architecture search in this cycle.

## 3. Count- and class-balanced matched-negative ablation (M1)

### Existing registered work to consume first

| Existing contrast | Question already covered | Residual limitation |
|---|---|---|
| Sb − SpV | Does the effect survive matching training row count, class mix and positive repetition? | Matched-negative content and 312 additional unique images remain inseparable. |
| BN − BV | Do matched negatives help without face-spliced positives, with identical positive rows? | Added matched content also changes unique negative diversity. |
| (Sb − SpV) − (BN − BV), printed | Does adding splice positives change the matched-negative effect? | Descriptive interaction under the existing registration, not a newly promoted primary test. |

The original registered tests, multiplicity handling and shape-link sensitivity rows are retained. No result from these unopened fits is assumed.

### Contingent new design

Use the same single-network CLIP ViT-B/16 + LoRA implementation and last-checkpoint recipe as the existing training ablation. Pin exact implementation, training steps, optimizer, batch composition, platform and seed block in the new registration. Reserve a fresh five-seed block through the lead's seed ledger; do not reuse the confirmation seeds 413–417 or assume unused seed numbers.

Use a four-arm factorial over two negative families, with face-spliced positive images identical in every arm:

| Arm | Same-person splice negative slots | Seam-only negative slots | Positive slots |
|---|---|---|---|
| M1-00 | Prespecified active-control negatives | Prespecified active-control negatives | Identical face-spliced positives |
| M1-10 | Same-person splice negatives | Active-control negatives | Identical face-spliced positives |
| M1-01 | Active-control negatives | Seam-only negatives | Identical face-spliced positives |
| M1-11 | Same-person splice negatives | Seam-only negatives | Identical face-spliced positives |

Active-control negatives are eligible existing bona fide/approved control images from the same training identities and source pools, selected before outcomes using a deterministic rule. They retain their correct negative labels. They must not be unrelated benchmark photographs or mislabeled two-person morphs. Specify selection strata and deterministic tie-breaking in the registration. Do not select replacements by detector scores or select whichever replacement gives the desired result.

Every arm must have the same total rows, positive/negative counts, optimizer updates and per-class minibatch schedule. Pin the row-slot schedule so the same training step uses the corresponding slot across arms. Also report unique image, identity and source counts and the multiplicity of every image. Equal row counts alone do not imply equal effective diversity. If the inventory cannot support matching unique counts and source/identity exposure, either construct eligible controls with an already approved generator before registration or explicitly narrow the claim; repeated rows must never be presented as matching independent sample size.

Keep the base protocol negatives and all ordinary positive rows byte-identical across the four arms. All identity/component splits precede control construction. Remove links through contributors, partner photos and shape donors, not just duplicated host names.

### Endpoints and falsifiers

- Primary causal contrast: M1-11 minus M1-00 on two-person versus same-person whole-frame morph ranking at fixed blend-strength strata. This avoids testing only the same negative construction supplied during training.
- Prespecified secondary contrasts: the main effects of each negative family and their interaction; two-person versus same-person face-splice ranking; fixed-threshold genuine flags and missed attacks.
- Include every arm's storage, border, camera-source and one-photo reconstruction checks. A lower control flag rate accompanied by unacceptable loss of morph detection does not pass.
- Register the multiplicity family, numerical useful-effect margin, tolerable regressions, bootstrap unit and handling of sparse strata before execution. The statistics owner owns these choices and precision assessment.
- Falsifier: no supported useful gain in the primary comparison under the registered inference, or a required detection/robustness guard fails. A wide interval is inconclusive, not proof of no effect. A better ranking is not a claim that same-person morphs are rejected.
- A positive factorial result licenses a content effect under the matched design. It does not by itself establish two-identity recognition or cross-engine generalization.

## 4. Rendering controls without a new generator (M2)

### Existing route and assets

Reuse the existing MIPGAN-I / MIPGAN-II-style generation implementation under `src/AG1/` and GX plans under `src/GX1/`. Reuse the existing unchanged OpenCV and FaceMorpher paths for landmark constructions. Do not add blur, resize, compression or replacement alignment code. The existing `src/GX1/gx1_admission.py` remains an unreviewed draft until independent review; this plan does not admit it.

The current GX design adds matched two-person renders and one-person controls to the Sb prefix. The protocol already specifies alignment and identity-admission checks; apply those as written, preserve failures, and keep matched rows together when dropping invalid images. Do not choose identity thresholds from detector performance.

After the current cycle, the next rendering study should use a count-controlled pair:

- M2-control: identical added two-person positive renders, plus the same number of deterministically selected eligible active-control negative slots.
- M2-matched: identical added positives, but those negative slots contain paired one-photo and same-person renders.

Balance counts, labels, training schedule and identity/source exposure using the same audited machinery as M1. The existing unmatched GXp arm remains descriptive for this content-effect question. Use existing admitted training assets only; if required pair coverage is absent, report the shortfall rather than silently regenerate a different distribution.

### Joint success requirement

Test two-person versus same-person renders as the primary identity-related contrast, with two-person versus one-photo renders and one-photo versus camera responses beside it. Require preserved fixed-threshold attack detection and improved rendering-control behavior jointly under prospectively fixed margins. Compare against simple-cue learners trained on the same training lists and evaluated on the same person-disjoint rows. Floors fitted directly on evaluation rows are separately labeled diagnostic references.

Falsifiers: control flags improve only by moving all scores toward genuine; morph detection deteriorates beyond the registered margin; same-person/two-person ranking shows no useful supported gain; or an improvement disappears on the excluded engine. These outcomes must remain visible even if MAD22 improves.

## 5. Engine and identity transfer (M3)

Create a metadata-only manifest before viewing any new outcomes. Each row records source photo hash, contributor identities, partner/shape-donor components, generator implementation hash, engine family, construction rung, split, prior exposure and which method may train on it. The adversarial-controls owner independently audits the disjointness claims.

| Train path | Excluded evaluation path | Interpretation / limitation |
|---|---|---|
| OpenCV-only landmark constructions | Existing FaceMorpher controls on identity-disjoint development hosts | Engine holdout only if no FaceMorpher images enter that model's training. Existing inspected panels remain development diagnostics. |
| MIPGAN-I-style construction | Existing admitted MIPGAN-II-style controls | Excluded implementation, but related GAN family; do not call it broad generator-family generalization. |
| Landmark or GAN training | Existing DiffAE matched controls, if provenance and identity checks pass | Different generator family; prior result exposure must be recorded. Reused panels are not blind confirmation. |

For a genuinely prospective development confirmation, reserve identities and a construction panel whose images/outcomes have not been used for method selection. Establish availability from metadata only. If every eligible panel has already been inspected, build a new panel using the unchanged approved generator and genuinely excluded identities after preregistration, or label the exercise retrospective. A relabeled split cannot restore blindness.

The already trained SbFM candidate has seen FaceMorpher; that engine is not its held-out-engine test. R3/R4 comparisons on new hosts are not identity-specific proof when low-level blend statistics remain predictive. Retain blend-strength stratification, region controls and the corresponding simple-cue comparisons.

No FRLL person enters training, refitting, calibration or development-panel construction. MAD22 is development-exposed; FRLL genuine overlap through MAD22 remains disclosed. Source-overlap audits use authorized metadata, not a new scoring read of sealed benchmarks.

## 6. Resource plan and stop rules

This is a planning estimate, not new spending authorization or a hard resource cap. Use the current approved resources and lead-controlled submissions. Register a concrete resource envelope once the real-command smoke measures runtime, memory, storage and score volume. Do not infer queue start times from old snapshots.

| Package | Fits / operations proposed | Planning basis |
|---|---|---|
| Existing batch C | No new fits; fifteen completed fits await their registered read | Reuse-first; do not duplicate completed SpV/BN/BV training. |
| M1 factorial, only for residual question | 4 arms × 5 fresh seeds = 20 fits | Existing AB1 reported 35–55 minutes per fit, approximately 12–19 H100-hours before new control scoring and overhead; not a promise for this new workload. |
| M2 matched-content pair | 2 arms × 5 fresh seeds = 10 fits, only if existing GX does not make the question moot | GX readiness estimated 10–15 H100-hours for ten fits with added scoring, plus 1–2 supplementary hours; smoke must replace the estimate. |
| M3 | Existing-score comparisons only where registered and authorized; otherwise locked scoring jobs | Number of admitted rows × measured scorer rate; no estimate invented before manifest audit. New generation, if needed, receives its own measured estimate. |
| Confirmation | One fixed nominated recipe and its registered comparators, five fresh seeds each | Exact fit count and control arms are fixed in the new registration before selection; no unlimited promotion of runners-up. |

Proposed search bound after consuming existing registered evidence: at most the four-arm M1 extension and one two-arm M2 extension, followed by one fixed nomination and one confirmation attempt. This is a scientific search-space bound for the proposed cycle, not a replacement of any author-approved resource envelope. The lead integrates it into the reviewed registration before execution. If no recipe qualifies, end the cycle with the prior candidate and report the negative or inconclusive outcome. Do not launch more seeds solely to cross a significance threshold.

A scientific failure is not retried as infrastructure recovery. A documented infrastructure retry preserves the failed attempt, uses the same pinned scientific workload and follows the registration's retry rule. No placeholder jobs, GPU waiting loops or unreviewed production scripts.

## 7. Ready-to-run checklist and agent handoff

The method owner delivers the following, in order:

1. Metadata inventory and prior-exposure ledger; confirm that all new-study rows are authorized development data.
2. Deterministic control-slot manifests plus an audit of class counts, unique images, identity/source coverage and row multiplicities; synthetic checks for mismatched labels, leakage and missing pairs.
3. A complete registration from `prereg/TEMPLATE.md`, including fixed seed block, endpoints, margins, multiplicity, all guards, failure handling, stopping rule and the current-cycle separation.
4. Exact code/data hashes and launchable command; independent pre-run review by an owner who did not implement it.
5. An eight-image real-command smoke only on authorized development rows after review, then measured resource request and complete workload staging for the lead. No production submission with unresolved thresholds or missing evidence.
6. Per-seed results, all failures, intervals and guard outcomes; independent results review before any paper-level claim.

The method owner does not open sealed scores, change the current NEXT rule, choose favorable seeds, submit jobs directly, or edit the independent reviewer report. The controls owner may reject the mechanism claim even if effectiveness improves. The statistics owner may declare insufficient precision even if point estimates improve. The lead integrates the two gates without trading one for the other.

## 8. Computation-coordinator handoff

A dedicated computation coordinator owns resource inventory, WCSS/Athena placement, dependency timing and extra-capacity recommendations. Its role is separate from scientific review. With six roles (including independent scientific review) and four concurrent slots, keep the coordinator and method execution active when jobs need intervention and rotate the independent reviewer into a freed slot; a method author never reviews their own release. Actual WCSS access/submission follows the lead’s single-connection lock and does not create a second concurrent SSH owner.

Every experiment handoff must include: exact GPU model and software build; required and measured GPU memory; CPU/RAM; input pack locations, byte sizes and SHA256; expected scratch/output bytes and durable copies; measured step/scoring rates and projected runtime; scheduler limit; dependencies and job IDs; admission and review receipts; and the bit-identity scoring gate. If any value is unmeasured, mark it unknown and measure it in the reviewed smoke rather than guessing.

Proposed platform for direct paired comparisons is the existing H100 training/scoring environment. Athena placement is allowed only where the registration and software/GPU reproduction requirements permit it; moving a fit across GPU models is not a scheduling-only change. Preserve same-platform paired comparators. A rented A100 cannot silently replace an H100 confirmation or final scoring path.

The coordinator reports additional compute needs as a concrete shortfall: ready workload, blocked dependency, measured GPU-hours/memory/storage, available WCSS/Athena capacity, deadline consequences and an itemized Vast option if useful. This draft grants no rental purchase. Apply the standing spending policy and existing session authorization; any genuinely additional approval request must concern the final concrete lease/cost proposal. Never rent merely to await missing manifests or review.

Latest parent-reported scheduler observation: the six checked jobs were PENDING on fresh accounting. This document is not a live monitor and makes no predicted queue-start guarantee.

## Source records consulted

- `OWNER_BRIEF.md`, `WORKFLOW.md`, `NOTEBOOK.md` (historical top-of-file status is not a live scheduler snapshot).
- Bound NEXT selection rule, especially sections 3–8 and disclosures in section 11.
- `experiments/GX1_gan-morphs-in-training/prereg.md` and `READINESS_20261114.md`.
- AB1 registration amendments 7 and 7b and `src/AB1/mk_ab1c.py` (read for existing design, not outcomes).
- Existing AB1 reviewed findings as summarized in the continuation brief and current discussion. This work did not recompute or access their raw scores.

No numeric scientific margin is newly declared by this draft; the next preregistration is incomplete until those choices, exact manifests and independent review are recorded.

## Implementation handoff: batch-C admission guards (14 November)

Implemented only in `src/AB1/ab1_pm3_read.py` and synthetic tests at `src/AB1/tests/test_pm3_admission.py`:

- Corrected the stale ten-task overlay pin `62712bb9…` to the exact fifteen-task amendment-7b/run_c.sh pin `bf276e548c5dc5a3c8d590d0500754c1d49ec87ad2e7b30237f05db94ffcafa7`. The registered current overlay is accepted; the obsolete one is rejected. No scientific statistic, margin, seeds, row definitions or bootstrap code changed.
- Added `--c-results` and `--ab1-results` to point to verified collected archives. Defaults retain their former directories. Archive names and the existing sidecar, manifest, GPU, steps, pack and overlay checks remain unchanged.
- Added a canonical durable exclusive claim under `/mnt/t7/smad_next/AB1/READ_ONCE_PM3/<pair>.claim.json`, before any archive loader. The production CLI cannot redirect that marker; changing `--out` cannot bypass it. Claims persist after failure and must never be automatically deleted. The claim records reader hash, output path, input directories and overlay.
- Existing outputs, including dangling symlinks, are refused. Output publication is create-only and fsynced; successful completion adds a separate create-only completion receipt with output hash. A crash can leave partial output and a permanent claim: that is intentionally blocked for independent disposition, not an automatic reread.
- Mock runs never create a production claim and cannot overwrite outputs.

Validation: eleven synthetic tests passed using the repository's existing Python environment. Tests exercised all three batch-C arms through the actual unchanged archive loader using temporary synthetic score arrays, obsolete-overlay refusal, racing claimants, retry refusal with a new output path, mock isolation, output preservation, and source-order assurance that the claim precedes all archive loaders. The unchanged loader emits ResourceWarnings about unclosed synthetic manifest reads; no real archive was used.

Production remains blocked pending independent review and any remaining scientific-print requirements. The guard change does not certify completeness of the existing reader. In particular, amendment 7 requests the same-data learners for `train_SpV` and `train_BN` when committed. The current pm3 reader has no learner argument/print path, unlike the parent pm reader's conditional `--learner`/`--learner-sha` path; it also does not carry over the parent's within-D-floor context print. This work did not invent a new learner, silently remove the requested print or promote a new test. The statistics/adversarial owner must identify the exact committed artifacts and applicable required prints, then review a display-only integration before production if needed. Adding BV to that learner scope requires an explicit reading of the amended requirement, not an assumption. No production marker or output was created by these tests.

Independent-review follow-up: the pm3-local native archive guard now checks exact TASK/ARM/SEED assignments against the requested archive, rejects duplicate assignments, requires one regular task.env and score member, validates the pinned evaluation-manifest hash, and requires one-dimensional, equal-length, unique evaluation IDs and logits in the exact registered manifest order. Non-finite logits are rejected. This runs before the unchanged historical loader can collapse/truncate arrays through `dict(zip)`. Both batch-C and its AB1 comparators use the wrapper; the pm3 FS1 route receives the same row/identity guard. Historical loader files and their hashes remain unchanged. Eighteen synthetic tests pass, including wrong seed, duplicate seed, duplicate IDs, truncated logits, reordered/foreign IDs and non-finite scores. Real archives remain unopened; production remains subject to independent review and the separate print/completeness disposition.
