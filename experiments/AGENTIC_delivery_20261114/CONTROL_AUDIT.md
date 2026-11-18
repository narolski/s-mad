# Artifact resistance and benchmark dependence: control audit

Status: operational design for the newly authorised workflow, 14 November 2026. This is a document-only audit of existing registrations, reviewed results and catalogue metadata. No benchmark image, sealed score, challenger payload or result archive was opened. No run was launched. This document does not amend the approved selection rule or release a scientific read.

## Role and authority

The controls agent independently tries to explain a candidate's apparent improvement using processing rather than the claimed mechanism. It owns the control manifest, estimands and alternative-explanation report, not training recipe choice. The statistics agent independently validates inference. A method owner cannot mark their own controls passed or remove a failing control.

Current selection is governed by `experiments/NEXT_method-selection-rule/prereg_draft_v3.md`, bound at `dbeb940`. Its thresholds, order, fresh-seed confirmation and missing-evidence rules remain authoritative. The more demanding next-cycle controls below are proposed scientific gates, not retrospective changes to that cycle.

“Shortcut-free” is not an attainable universal certification from a finite battery. The release claim must enumerate tested perturbations, source populations, engines and thresholds. Failure to find a significant difference is not evidence of invariance; equivalence/non-inferiority requires a justified bound and adequate precision.

## Evidence that motivates the battery

| Existing reviewed finding | Implication for the next workflow |
|---|---|
| Morph-free shrink/enlarge training reaches 0.0% MorDIFF-native EER in 10/10 networks; AD4 cluster review | Good morph-versus-photo ranking is not sufficient evidence of morph-specific detection. Keep morph-free reference models and construction controls. |
| Sb flags 78–90% of one-photo MIPGAN renders; R2-vs-camera AUC 0.992–0.998; PR1 GD2 | The current candidate has a large rendering response. A new candidate must reduce it without simply suppressing attack scores. |
| Sb two-person-vs-same-person MIPGAN AUC 0.619–0.690; no beyond-simple-cue licence; PR1 | A second-identity claim must survive same-person and low-level-cue controls. R4-vs-camera performance cannot substitute. |
| Face-plus-halo blend-vs-warp AUC Sb 0.889; Sb−B +0.011 [−0.010,+0.031]; XF1 | No established Sb advantage in this diagnostic; require an independent engine/host confirmation for a stronger claim. |
| Plain storage false-alarm rise 26.5–38.5 pp at fm61 vs Sb 0–4.5 pp; formal AB1 overall storage verdict inconclusive | Distinguish beneficial false-alarm attenuation from score invariance. Keep both genuine and attack responses. |
| Removing matched negatives loses 0.049 AUC on pooled two-person-vs-same-person whole-frame ranking; AB1 | Content, count and class balance need separation. Existing AB1 batch C already addresses part of this and must be read under its own rules before duplicate fitting. |

## Current-cycle gates: implement exactly, do not reinterpret

These are a navigation summary of selection-rule v3; the bound registration controls if wording differs.

| Dimension | Existing binding criterion | Required evidence |
|---|---|---|
| Controlled ranking | Within-D two-person-vs-same-person OpenCV ladder mean difference at least −0.02; no seed below −0.06 | Pinned 360 rows, 110 person components, registered D edges/draws and coverage; shape-link sensitivity and engine subsets printed |
| Surround matching | Matched AUC gain at least +0.015 and at least half the full landmark gain | Pinned 360 pairs; acknowledge face-interior floor remains 0.949, despite surround floor about 0.504 |
| Storage | Challenger-minus-comparator rise in own-rule flags at most +0.02 at both sizes on at least 4/5 seeds; platform plain control and morph-evasion rule satisfied | Pinned paired storage rows, both sizes, exact platform/scoring path |
| Genuine-source transfer | Seven-family mean flag-share difference at most +0.02; MEDS upper person-bootstrap bound at most 10% on at least 4/5 | TT1 family mapping, MEDS group mapping, unchanged own threshold |
| Same-person splice and border | S3 flag-share difference at most +0.05 and border-photo difference at most +0.01 on at least 4/5 | Both arms' border rows must use the same valid scoring path |
| Viewer resize, applicable arms | Registered held-out and training-kernel kappa at most 0.05 on at least 4/5 | SbMR/SbM registered cross tables; SbMR512 cannot qualify without a preread registered kernel test |
| Simple-cue comparison | Required floor prints; specified lower bound above zero on at least 4/5 is needed for the “beyond hand-made statistics” wording | Per-row transfer scores from the same training list and separate in-distribution floors; not interchangeable |

These gates mostly bound regression relative to a comparator; passing them alone does not establish low absolute artifact sensitivity. Missing mandatory evidence means not read/ineligible under the rule, not a favourable scientific result. Missing reader implementation is an operational blocker, not a failed arm.

## Next-cycle battery: freeze before any candidate read

For each row, preregister exact sources, host/person-component graph, pair IDs, image-history hashes, transforms, engines, own-threshold rule, seeds, estimator, uncertainty method, missingness policy, multiplicity family and margins. The notation below defines estimands but intentionally does not invent tolerances from the already observed results.

Let f_t(x) = 1[score(x)>t], with t fixed on permitted development data before confirmation; let ΔFA_T = mean(f_t(T(x))−f_t(x)) on matched genuine images, and ΔMISS_T the analogous change in attack misses. Report paired changes, absolute post-transform rates and class-conditional score shifts. Uncertainty must preserve person/partner dependencies and training-run variability.

| Gate | Paired control and estimand | Failure / inconclusive condition | Numeric readiness |
|---|---|---|---|
| Storage/resolution/compression | Reuse approved native/stored versions of the same genuine and morph images. Estimate ΔFA_T, ΔMISS_T, paired score shift and discrimination retention separately for every prespecified transform. | Fails if an adverse bound exceeds the frozen tolerance or attack retention fails. Inconclusive if intervals cannot establish the bound. A move toward genuine is not automatically harmless if attack misses rise. | New-cycle absolute FA ceiling, score-equivalence margin and miss-retention margin UNRESOLVED. Existing v3 bounds apply only to v3. No new transform code is authorised by this document. |
| Rendering | Same source photo vs one-photo reconstruction; compare same-person and two-person mixes through the same engine. Estimate reconstruction flag share, two-person attack detection and AUC(two-person,same-person), with matched simple-cue learners. | Fails if reconstruction response exceeds the frozen ceiling or retained attack performance fails; broad score suppression cannot pass. No identity claim if a simple-cue explanation remains adequate. | Absolute ceiling, minimum retained detection and meaningful controlled gain UNRESOLVED; existing PR1 descriptive thresholds are not imported as new confirmation gates. |
| Blending versus geometry | Matched two-person blends vs warp-only controls using unchanged approved generators, whole-frame and specified face-region forms. Estimate AUC and paired method gain, alongside same-list transfer learners. | Fails/inconclusive if improvement is absent/too imprecise or fully explained by registered nuisance controls. Warp-only differs in noise averaging, so passing this contrast alone is not identity evidence. | Gain/equivalence tolerances and final region definition UNRESOLVED; use existing XF1 definition only if explicitly registered for replication. |
| Identity relationship | Two-person vs same-person blends with matched engine/history, nuisance strata and contributor-aware partitions. Estimate within-stratum AUC gain, coverage, absolute flag shares and nuisance-reference contrasts. | Fails if the prespecified gain bound is not met, effective coverage is inadequate, identity/source leakage exists, or same-person rejection claim fails at the fixed threshold. Same-person manipulations remain mechanism controls, not necessarily bona fide. | Minimum useful gain, coverage minimum and absolute same-person ceiling UNRESOLVED. |
| Surround/border | Matched camera and morph frames under existing approved constant-colour blanking and existing surround matching. Estimate ΔFA, ΔMISS, network-vs-surround learner and retained face-region gain. | Fails if benefit disappears under the registered test or nuisance shifts explain it. Constant-colour blanking itself can be out of distribution; report it explicitly rather than label every shift background dependence. | Final region/mask and effect limits UNRESOLVED. Face-plus-halo does not isolate the face interior. |
| Source and engine transfer | Exclude a complete manipulation engine and source-person components from development/selection. Apply frozen threshold and report fixed family averages and worst-family checks. | Fails if the retained-performance/false-alarm bound is missed; not held-out if engine outcomes affected recipe choice. An already-inspected FaceMorpher pool cannot become untouched by renaming it. | Excluded engine/source manifest, loss margin and minimum sample precision UNRESOLVED. |
| Data-level shortcut challenge | Morph-free reference training and per-row low-level transfer learner from each candidate's own list; separate in-distribution learner. | No “beyond tested cues” claim unless the preregistered network-minus-reference bounds pass. Being below an in-distribution learner is not proof that the network uses those cues. | Learner recipes/features and simultaneous comparison rule to be pinned; retain equal-data and in-domain labels. |

All mandatory gates are conjunctive. No weighted overall score can hide a failed control. Each gate emits PASS, FAIL, INCONCLUSIVE or NOT_READ with machine-readable provenance and a reason. Both INCONCLUSIVE and NOT_READ block the stronger claim; they are not evidence that a shortcut exists. Numerical bounds must be justified by the target operating requirement and development-only precision planning, then independently reviewed and frozen. Do not choose them to admit Sb or a preferred challenger.

## Existing ablation coverage: avoid redundant work

AB1 preregistration amendments 7/7b already define:

- SpV: Sb positive rows and class counts retained while the matched negatives are replaced by repeated native negatives; this controls row count/class mixture, not unique-image diversity.
- BN and BV: matched-negative content without splice positives versus repeated-native control, with identical positive rows; primary comparison BN−BV replaces the earlier confounded BN−B.
- Interaction (Sb−SpV)−(BN−BV) is printed; near-certain S4-vs-S3 training-negative effects are not treated as independent tests.
- Batch C is 15 fits at seeds 408–412. The current delivery record reports completed, hash-verified, opaque outputs. This audit did not read them.

Read these only after their registered inputs/reviews/admission are satisfied. Use their outcome and limitations to decide what genuinely remains for the next cycle; do not re-run until significant. Separate S0/S3 content and unique-diversity controls remain distinct questions.

## MAD22 / FRLL-Morphs dependence audit: documentary findings only

| Finding | Evidence | Status and implication |
|---|---|---|
| Corrected MAD22 genuine side comprises 204 FRLL photos of 102 people, neutral and smiling | FINAL prereg §3 and §7; reviewed FINAL result labels | CONFIRMED IN RECORDS. These genuine scores were exposed by the 13 Nov read. |
| FRLL-Morphs evaluation uses FRLL genuine photos and derivatives | DATA_CATALOG §§2,7; FINAL prereg §7 explicitly describes unavoidable FRLL-photo exposure | CONFIRMED IN RECORDS. FRLL-Morphs is not independent of MAD22 on the genuine side. |
| Candidate FRLL-Morphs morphs remained unscored at that read | FINAL prereg §1/§7; continuation and delivery record | DOCUMENTED SCOPE. Do not infer current filesystem payload state or open scores to verify. The candidate's restrictions remain in force. |
| Earlier MAD22 seeds informed recipe choice; later MAD22 method results are development-exposed | FINAL prereg §7, reviewed result and NOTEBOOK 13 Nov 21:30 | CONFIRMED IN RECORDS. A new p-value cannot remove prior method-selection exposure. |
| Exact identity, source-photo and morph-derivative overlap between the two morph pools | Catalogue contains dataset provenance/counts but no cross-benchmark deduplication ledger | NOT ESTABLISHED. No claim of morph-level disjointness or independence is justified. |
| Catalogue's early “closed benchmark” label for MAD22 | Catalogue initial timestamp predates completed read; later FINAL and NOTEBOOK record exposure | STALE GENERIC LABEL. Use the later explicit exposure record. |

Required metadata-only audit package before the next evaluation registration:

1. A custodian-approved manifest, without scores or images, mapping each evaluation row to benchmark, family, source-photo identifier/hash, contributor identities, derivative parent and processing history. Access to existing metadata must be confirmed separately from permission to open benchmark content.
2. Counts of shared persons, exact source images, byte-identical derivatives and documented derived-image relationships, plus unresolved mappings. Do not assert zero overlap from missing metadata.
3. A unified dependency representation for both benchmarks. The statistics reviewer must choose and validate the joint resampling scheme; never resample their shared genuine people independently. Existing FINAL uses a contributor-aware pigeonhole bootstrap, while NEXT development uses connected components; these are not silently interchangeable.
4. A fixed benchmark weighting and family list chosen before new scores. Equal benchmark weights define an estimand, not independent replications. Do not exclude a difficult family after seeing a new candidate's result; any artifact-saturated exclusion needs prospective justification and the full descriptive table.
5. An exposure ledger separating recipe-level prior knowledge, candidate score access, source-image reuse and genuinely untouched evidence. An independent external source is needed for the strongest generalisation claim.

No source filenames, biometric identifiers or restricted-image data were copied into this report.

## Release language

Allowed now: “Matched-control training improved controlled development ranking and attenuated storage-induced false alarms; benchmark performance was competitive, with unresolved rendering and blending explanations.” Keep the already registered result qualifications.

Allowed after a properly passed new battery: “The method improved the prespecified endpoint and resisted the listed processing perturbations within the stated bounds on the tested sources and engines.” Name the tests and remaining exclusions.

Not licensed by any finite battery: “shortcut-free,” “all artifacts removed,” or a universal claim that the detector sees two identities. A benchmark superiority result cannot substitute for the mechanism gates; passing mechanism gates cannot substitute for superiority evidence. MAD22 development exposure and FRLL shared genuine photos remain disclosed even after all future tests pass.

## Source ledger

- `experiments/NEXT_method-selection-rule/prereg_draft_v3.md`, §§4–7: binding current selection gates.
- `experiments/AB1_protocol-ablation-and-replication/prereg.md`, amendments 7/7b: existing count/class control fits.
- `experiments/AB1_protocol-ablation-and-replication/result.md`: reviewed development results and qualifications.
- `experiments/PR1_protocol-reads-existing-networks/result.md`, GD2 and wording section: rendering controls.
- `experiments/XF1_ffhq-facemorpher-matched-render/result.md`: blend-versus-warp diagnostic.
- `experiments/reviews/REVIEW_AD4_CLUSTER_20261113.md`: morph-free evidence and platform caveats.
- `experiments/FINAL_sealed-benchmark-read/prereg.md`, §§1,3,5,7; `result.md`: exposure, contributor resampling and MAD22 outcome.
- `DATA_CATALOG.md`, §§2,7: documented inventories and processing provenance; not a fresh content audit.
- `NOTEBOOK.md` and `experiments/RECORDS_ledger/CODEX_DELIVERY_20261114.md`: latest recorded handoff, not current scheduler observation.
