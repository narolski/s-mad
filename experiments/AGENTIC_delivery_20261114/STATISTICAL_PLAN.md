# Statistical contract and implementation queue for agentic delivery

Prepared 14 November 2026 from existing registrations, reviewed reports, source code and metadata documentation. No candidate score, sealed score, model, image or archive member was opened. No analysis, training, cluster query or submission was run.

**Status:** operational design for the newly authorised workflow, not a replacement for the binding selection rule and not a release to score a benchmark. The future-cycle numerical margins and analysis configuration listed below must be fixed and independently reviewed before that cycle starts. No significant win is guaranteed. Negative and inconclusive outcomes are valid deliverables.

## 1. Two separate statistical tracks

### Current registered selection: preserve exactly

The approved rule is `experiments/NEXT_method-selection-rule/prereg_draft_v3.md`, bound at `dbeb940`. Its fixed challenger order, criteria (a)–(f), comparison roles, seeds, support inputs, deadlines, missing-seed rules, bootstrap and once-only journal govern the current cycle. The newer proposed benchmark average must not be substituted into this rule.

- Complete technical admission, then apply the existing selection once.
- Selection results are selection-biased, not unbiased estimates of the chosen method's effect.
- Confirm a selected challenger using seeds 413–417 and its registered comparator/control, applying the same rule. Failure retains Sb.
- A prospective benchmark protocol belongs after confirmation and freeze; its endpoint must reconcile with section 8 of the approved rule and the final evaluation protocol before release. A silent endpoint change is prohibited.
- The four-of-five and other counts in the current rule are operational registered rules, not universal significance tests. Preserve them instead of retrofitting a different p-value interpretation.

### Prospective extension: a bounded new cycle

The following defines the proposed target and implementation requirements. It does not retrospectively make MAD22 untouched, and it does not alter a completed result. A future cycle uses fresh seed IDs assigned in its registration; it must not reuse 413–417 as “fresh” after current confirmation has consumed them.

## 2. Define the population and estimand before evaluation

For benchmark b, fixed eligible family set F_b, method m and fit seed s, compute family EER e(m,s,b,f) using the fixed score direction and interpolation/tie convention. The prospective balanced error is:

    T(m) = (1/2) × sum_b [ (1/|F_b|) × sum_f mean_s e(m,s,b,f) ]

Here b ranges over corrected MAD22 and FRLL-Morphs. EER is reported in percentage points. Average per-network EERs; never average logits across networks. Family sizes do not determine endpoint weights. The target represents these two benchmark collections, not a random sample of all possible morph engines.

For each prespecified comparator j, delta_j = T(candidate) − T(comparator_j), so negative is better. Also compute the two benchmark-specific differences. If a released detector supplies only one fixed network, inference for that comparator is conditional on that release; no between-fit variance is fabricated. Retrained comparator results are a separate prespecified comparison with all its registered seeds.

Before release, a frozen manifest must specify:

1. Included family sets, raw/processing-history forms, genuine pools and exclusions, with scientific reasons independent of new scores. Do not automatically remove a hard family or change a comparator's preprocessing to obtain a gain. The previous MAD22 FaceMorpher exclusion is historical context, not a blanket exclusion rule for a new endpoint.
2. Comparator names, exact weight hashes, inference code, crop and preprocessing definitions; which comparisons are primary versus descriptive. “Others” must become a finite list. The previously evaluated SelfMAD, MADation ViT-B/16, MADation ViT-L/14 and MixFaceNet-MAD are an initial inventory, not an automatically complete field comparison.
3. Row identity, source-photo identity, contributor identities, engine, derivative relation, benchmark membership and immutable split assignment. Missing values receive explicit dispositions.
4. A separate landmark-family summary, because an average driven by GAN-render discrimination cannot establish identity-specific detection. No subgroup becomes the headline after observing its advantage.

## 3. Dependence and exposure are first-class inputs

`DATA_CATALOG.md` documents 102 FRLL persons / 204 frontal photos underlying the corrected MAD22 genuine side; the MAD22 result explicitly records their exposure. FRLL-Morphs derives from FRLL. Exact cross-benchmark morph/derivative overlap remains an audit task, not an established count here.

Build an overlap manifest from permitted metadata before score access. Join every repeated genuine photo, contributor identity, source derivative and morph pairing across both benchmarks. Components must be global across benchmarks and families; independently bootstrapping the same people once for MAD22 and again for FRLL would understate dependence.

For the proposed primary uncertainty analysis, use common component draws across candidate, all comparators, families, benchmarks and processing forms. Resample training seeds as an additional dimension when the estimand includes training randomness. Use paired seed draws only where the training design creates genuine paired runs; equal integer seed labels across unrelated architectures do not create pairing. Unpaired trained arms use independent seed draws but shared source-component draws. Fixed released weights are not resampled as if they were multiple fitted networks.

A connected-component bootstrap is not automatically feasible: morph partner edges may create a giant component or only a few independent clusters. First report component counts, size distribution, largest share and effective concentration using metadata. If the graph collapses, refuse ordinary component-bootstrap inference. The pre-run review must then select and validate a dependence-aware alternative (for example an explicit multi-membership design), or restrict the inferential claim / collect independent data. Never split a large component arbitrarily to manufacture precision.

The resampling implementation must also fix what happens when a draw has one class, absent families, undefined EER or insufficient observations. Report invalid-draw frequency. No outcome-dependent retry/drop rule. Validate coverage with simulations reflecting the actual dependency graph before production use.

MAD22 is development-exposed. A p-value computed after further MAD22-informed method development does not undo selection bias. FRLL-Morphs is not an independent identity replication of MAD22. The joint mean can describe a frozen method on these collections, but a generalization claim needs independent, untouched evidence. State the exposure on every relevant output.

## 4. Success is a conjunction, not a weighted score

| Requirement | Statistical decision | Failure / unresolved state |
|---|---|---|
| Superiority to each fixed comparator | The simultaneous one-sided upper confidence bound for every primary delta_j is below zero. Also report raw effects and simultaneous intervals. | Any bound includes zero: no claim of superiority to the full comparator set. Do not substitute the mean comparator or drop the strongest one. |
| Practical benefit | The effect reaches a prespecified smallest worthwhile improvement, with the exact criterion fixed before evaluation. | Statistical significance alone does not imply a useful gain. |
| No hidden benchmark regression | Each benchmark-specific upper difference bound is below its prespecified non-inferiority margin, for the registered comparisons. | A positive average cannot compensate for failing a required benchmark condition. |
| Fixed-threshold utility | Attack miss rates meet the prespecified benefit criterion while genuine false alarms satisfy their bound, using thresholds fixed outside evaluation. | Lowering both attack and genuine scores is not automatically an improvement. |
| Processing-control resistance | Simultaneous bounds for registered paired perturbation effects lie within prespecified tolerances; attack sensitivity also remains acceptable. | A nonsignificant effect is not equivalence; a control with insufficient precision is inconclusive. |
| Mechanism and transfer | The registered matched-identity/processing contrasts and excluded-engine contrasts pass, with all required simple-cue comparisons. | Failure limits the claim even when benchmark superiority passes. |

Use one documented multiplicity family for the confirmatory primary comparator claims. A conservative baseline implementation is Bonferroni simultaneous one-sided bounds; a more powerful joint resampling method may replace it only after independent pre-run validation and pinning. Do not choose a correction after comparing verdicts. Predefine allocation across confirmatory endpoint families, subgroup tests and successive research cycles. Current NEXT rules retain their own registered inference.

Testing that all required superiority statements hold is an intersection requirement; simultaneous intervals additionally permit separately reporting each comparator statement. Distinguish those claims in the registration. Print every comparator and interval regardless of significance.

## 5. Thresholds and controls

EER is a ranking-derived benchmark summary, not the error of a deployed threshold. Each network's operating threshold must be chosen using only a pinned permitted development calibration set and the registered rule. Specify how released detectors use their published operating point or a common development calibration protocol. Never tune separate thresholds on benchmark labels to improve operating-point claims.

Report both attack misses (APCER) and genuine false alarms (BPCER), by benchmark and family, with dependency-aware uncertainty. For paired perturbations, estimate within-source changes and the threshold-specific decisions; do not substitute unrelated-image false-alarm differences. Report ranking and fixed-threshold outcomes separately.

Control tolerances must be justified by the allowed false-alarm/attack-loss budget and measurement precision, not by the candidate's observed response. New numerical tolerances are intentionally unset here. Existing NEXT tolerances remain exactly binding for current selection.

## 6. Precision and power feasibility before new fits

Deliver a CPU-only simulation report using synthetic outcomes and permitted development summaries; no sealed-score variance estimates. The report must vary plausible effect sizes, seed variance, source-component dependence, class imbalance, family heterogeneity and comparator correlation. Label every assumption and distinguish approximate power from a guarantee.

Report:

- Probability of satisfying the entire effectiveness-plus-control conjunction, not only one favorable test.
- Interval width and coverage for superiority, benchmark non-inferiority, false-alarm tolerance and control equivalence.
- The marginal benefit of more independent people, more manipulation engines and more fits. More derivatives of the same people do not equal more independent samples.
- Sensitivity to giant components, limited training seeds, invalid bootstrap draws and low/zero observed errors.
- A resource proposal linked to measurable precision, without retroactively imposing a new resource cap on already authorised work.

Before launch, pin: the smallest worthwhile improvement; per-benchmark non-inferiority margins; genuine false-alarm and attack-loss bounds; processing-equivalence tolerances; confidence level and multiplicity allocation; bootstrap algorithm, random seed and replication count; admissible invalid-draw rules; candidate cap, fit budget and retry policy; threshold calibration rule; independent-unit sufficiency criteria; and all source manifests. These are unresolved design fields, not permission to choose them after results.

No repeated resampling until significance changes, repeated benchmark peeking, extra training seeds because the interval nearly excludes zero, or changing the family mix. If Monte Carlo precision is insufficient near the decision boundary, the treatment must have been fixed in advance; report a fragile/inconclusive decision rather than silently rerunning.

## 7. Current NEXT reader: exact implementation queue

This audit reads code and documentation only. No production invocation or once journal was created. Status is based on local records, not a live scheduler poll.

| Work item | Exact paths / evidence | Completion requirement |
|---|---|---|
| Preserve approved numerical logic | `src/NEXT/read_selection.py`; `experiments/NEXT_method-selection-rule/prereg_draft_v3.md`; `experiments/reviews/PRERUN_NEXT_READER_20261114.md` | Current native coverage is `rz1_fit` and `rz1_refit`. Independent review currently approves commit/current scope, not a scientific read. |
| Implement second-engine native adapter | `experiments/AB1_protocol-ablation-and-replication/prereg_fm.md`; `experiments/AB1_protocol-ablation-and-replication/SUPPLEMENTAL_RESCORE_20261114.md`; `src/recovery_20261114/sbfm_supplement/`; `experiments/reviews/PRERUN_SBFM_SUPPLEMENT_20261114.md` | Bind v2 fit provenance, H-fm guards, paired AB1 comparator and complete supplemental TT1/MEDS/border sources. Job 6319579 submission is not completion. Add synthetic valid and adversarial format tests before native member access. |
| Implement DINOv3 native adapter | `experiments/BB2_second-backbone/prereg.md` amendments 4–7d; `src/NEXT/read_selection.py` helper `unpaired_seed_component_interval`; `experiments/NEXT_method-selection-rule/ELIGIBILITY_20261114.md` | Fix E3 seed mode; require fit/splice-adequacy and per-network exact-rescore gates; join W2 outputs and all required control rows. Existing unpaired numerical helper is not a native adapter. Job 6319264 must not be duplicated. |
| Establish GAN-training admission and adapter | `experiments/GX1_gan-morphs-in-training/prereg.md`; `experiments/GX1_gan-morphs-in-training/READINESS_20261114.md`; draft `src/GX1/gx1_admission.py` | Generation metadata alone is insufficient. Need reviewed image/identity admission, admitted manifest, GX/GXp lists, floors, training amendment 2, smoke and complete training/rescore inputs. Do not treat the unreviewed draft as executed. |
| Complete current RZ1 evidence | `experiments/RZ1_input-resolution-and-resize/RESCORE_RECOVERY_20261114.md`; `experiments/NEXT_method-selection-rule/ELIGIBILITY_20261114.md` | Preserve original A408 output and collect exact-gated retry source evidence for the yardstick; all required roles and source hashes must agree. Submission 6319491 is not a gate pass. |
| Resolve 512 resize-mixing kernel test | `experiments/RZ1_input-resolution-and-resize/prereg.md`; `src/NEXT/read_selection.py` explicit SbMR512 refusal | Register and review the missing cross-kernel test before read, and extend native support. A completed fit cannot supply this missing scientific prerequisite. |
| Resolve interior crop scope | `experiments/NEXT_method-selection-rule/prereg_draft_v3.md` section 12(4); reader `crop_scope_ruling` requirement | Pin the actual author ruling; no inferred answer from elapsed time or a different resolution approval. |
| Fresh confirmation adapters | `src/NEXT/read_selection.py` `AB1_SB_SOURCE_PINS` and confirmation checks; `experiments/NEXT_method-selection-rule/READER_20261114.md` | Original source pins cover 408–412 only. Pin the registered fresh 413–417 source networks and reviewed formats for whichever arm is selected. Stage separation already exists but is not sufficient. |
| Close batch and admit once | Proposed `experiments/NEXT_method-selection-rule/ADMISSION.json` (not created by this audit); required schema documented in `READER_20261114.md` | Every fixed-order arm has an evidence-backed disposition; all receipts meet the 15 November 18:00 CET arrival/hash deadline; independent review binds exact admission SHA through `NEXT_ADMISSION_GO`; clean committed pin set and exact environment pass preflight. |
| Test adapters and refusal paths | `src/NEXT/tests/mock_selection.py` | Expand existing synthetic tests for all new schemas, wrong arm/seed/source mappings, incomplete joins, duplicates, nonfinite data, timing, unsupported eligible arms, and confirmation source pins. Independent reviewer checks rule mapping and floor columns. |

An otherwise eligible arm with an unsupported adapter blocks the entire scientific invocation before candidate members are opened. It cannot be marked a scientific failure to let a supported arm or Sb win. The rule's allowed missing/infrastructure/deadline dispositions require actual evidence. Current pin validation does not substitute for admission.

## 8. Artifacts and ownership for the next milestone

Statistics agent prepares the estimand specification, overlap/precision audit, synthetic analysis tests and immutable analysis configuration. Method agent supplies hypotheses and permissible data/fit manifests, not benchmark-dependent endpoints. Controls agent independently defines nuisance controls and tests simpler explanations. The lead integrates reviews, resolves release conditions and holds benchmark access.

The next review packet should contain the above unresolved parameters with rationale, a metadata-only overlap manifest, simulation report, reader test results, comparator manifest and a claims table mapping every proposed sentence to its required tests. No benchmark release until the packet is complete. Result reports must retain all failures, missing outcomes, effect sizes, intervals and exposure labels.

Sources read: the continuation brief; `OWNER_BRIEF.md`; `NOTEBOOK.md`; `DATA_CATALOG.md`; the binding NEXT rule, reader documentation, eligibility record and reader source. This document is a prospective statistical design, not an additional empirical finding.

## 9. Immediate independent progress: count/class-matched ablation batch C

**Disposition: scientifically separate from NEXT, but not executable unchanged.** AB1 amendments 7 and 7b explicitly make SpV, BN and BV post-freeze ablation rows, not challengers or method candidates. The registration says to read once when all 15 fits end, latest 15 November 18:00, with later rows labelled late. The pre-run review is `experiments/reviews/PRERUN_AB1_A6_A7_20261113.md` (GO WITH FIXES); amendment 7b records the BV addition and other fixes. No Batch-C-specific score hold was found in the reviewed registration/README; the nearby SbFM hold is a different experiment. This ablation can proceed without opening NEXT challengers once its own technical blockers are repaired and independently reviewed.

This already-trained experiment directly addresses a gap in contribution 3. H-c1 is Sb − SpV; H-c2 is BN − BV. Both primary decisions concern two-person versus same-person whole-frame morphs. It controls row count/class mix and positive repetition, **not unique-image diversity**: matched negatives add 312 unique images relative to repeats. Do not schedule a redundant version until these registered results are read. Same-person splice outcomes are near-certain by training design and not new mechanism tests; the interaction is printed, not a separately powered test.

### Static blockers found before score access

1. **Wrong overlay guard in the pinned reader.** `src/AB1/ab1_pm3_read.py` hashes to the registered amendment-7b value `d21180d7e51b1126cf7fc605d6853603263397e62e9a63ccdfa0dfbffeb1576c`, but its `C_OVERLAY` constant still equals the earlier `62712bb9d5066443d5737c84da852d055ab248930d5f38fc8b77ba0074a34c68`. Amendment 7b and `src/AB1/run_c.sh` instead require `bf276e548c5dc5a3c8d590d0500754c1d49ec87ad2e7b30237f05db94ffcafa7` for the 15-fit overlay containing BV. The imported `ab1_read.load` explicitly checks that constant. The unchanged reader would reject the new networks as `overlay off`. Fix only this guard against the pre-existing registration, re-pin, independently review and mock-test before any real member is opened. This is not grounds to mark the experiment scientifically unreadable.
2. **Recovered archives are not at the reader's hardcoded path.** The expected `/mnt/t7/smad_next/AB1/c/results/AB1C_<arm>_s<seed>.tar` files are absent at audit time. Receipt `experiments/RECORDS_ledger/codex_20261114/NEW_COLLECTION_VERIFIED.json` locates all 15 at `/mnt/t7/smad_next/coordination_20261114/archives/AB1C/`. Stage verified references and `.tar.sha256` sidecars at the expected path, or independently review a path-only adapter. Preserve original receipts and bytes. The comparator source is `/mnt/t7/smad_next/AB1/results/AB1_{Sb,B,Sp}_s{408..412}.tar`; verify all 15 files and sidecars without member access.
3. **Same-data learner printing is not implemented.** The registration requires the SpV/BN same-data learners when committed; `experiments/ADV_shortcut-floors/floors/transfer_{SpV,BN,BV}.json` and per-row CSVs now exist. The current pm3 CLI has no learner argument and prints only six all-cue/nuisance floors. A reviewed companion print or narrow extension must join the pinned learner references without changing the deciding statistic. Report the scope of these references accurately; no new learner selection based on Batch C outcomes.
4. **Once-only execution requires the reviewed reader repair.** The original pm3 overwrites `--out` and has no once journal. The method worker is adding an internal canonical per-pair atomic claim before native access. Use that reader-owned claim; do not externally preclaim the same journal, which would make the reader refuse. Preserve failures and require review before recovery. The NEXT journal must not be used for this separate ablation. The independent controls review also identified missing native seed and duplicate-ID validation; these are release blockers until repaired and synthetically tested.

### Remaining preflight without reading scores

- Verify exact source hashes for `src/AB1/ab1_pm3_read.py` after the reviewed correction; imported `ab1_pm_read.py` is presently `ba6efdada789c2a42ef47fa1fa39e707012f66641be40b6346ce9b45b067ed5e`, imported `ab1_read.py` is `74ecdf7a2ecb35812dcf4e5d5b9f5c3b1f095fc6846ae6f4813bfb28404d035b`. Record their transitive imports and environment. The historically appended pins file contains earlier versions; validate the explicitly registered current version, not every historical line as if all were simultaneous requirements.
- Hash and validate the registration's training manifests under `/mnt/t7/smad_next/AB1/c/manifests/`; the AB1 eval manifest; PN1 split tables; `/mnt/t7/smad_next/DATA/overlap/test_hosts_clean_of_dev.csv`; and `/mnt/t7/smad_next/BD1/d_values.csv`. These are the permitted metadata inputs, not benchmark scores. Current code checks 100 development hosts, 191 read test hosts, 80 clean hosts, 32 linked hosts and the fixed clean-host/D hashes.
- Verify committed floor pins for `ri_R4_vs_R3`, `ri_S4_vs_S3`, `dev_S4_vs_S3`, `test_cv_R4_vs_R3`, `test_fm_R4_vs_R3`, `test_S4_vs_S3`, each JSON plus `_heldout.csv`. `src/adversary/check.py` reads them from an absolute live-repository path and checks `pins_stage*.sha256`; a clean reader checkout alone does not isolate those floor bytes. Bind these exact external dependencies in the release receipt.
- Re-run the existing `--pair C --mock` path into a distinct mock output; use synthetic archives to test the corrected overlay acceptance and stale-overlay rejection. Do not use production files as a smoke test.
- Inspect native loader guards before release. Existing load checks include GPU, pack, overlay, steps, train/eval manifests, task arm, item count and finite training loss; the pm3 wrapper checks finite required evaluation rows. Independent release review should verify seed identity and duplicate row handling as well, rather than assuming filenames establish seed provenance.

### Exact production command after the above release (not executed)

Run from the reviewed checkout rooted at `/home/narolski/smad-next`, with a durable output directory created and no prior canonical pair-C claim; the reviewed reader claims its own journal internally:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 \
  /home/narolski/mambamorph-code/.venv-spark/bin/python -I \
  src/AB1/ab1_pm3_read.py --pair C \
  --out /mnt/t7/smad_next/AB1/c/read_20261114/ab1_pm3_read_C.json
```

Use `--mock` and a different filename for the synthetic command only. The interpreter path exists locally. Reader runtime was not measured in this audit; it performs many 2,000-draw floor comparisons and should not be promised as instantaneous. A successful output must go to an independent results reviewer before conclusions; preserve the exact stdout, exit status, source pins, input hashes and output hash. AB1's registered 99.5% sensitivity intervals are not a complete correction for the expanded 16-verdict family; retain the amendment's qualification rather than claiming family-wise significance.

### Learner companion implementation added after this audit

`src/AB1/ab1c_transfer_report.py` implements the registered descriptive companion. It reads only committed, unchanged stage-11/12 learner files and the pinned selection-row reference; reproduces existing unstratified AUC/flag summaries from per-row predictions; verifies the exact row/label/component correspondence for sel360 and between the three arms; and embeds full original summaries with exact set metadata. It does not read candidate archives, fit learners, compute new hypothesis tests or claim that the unstratified summaries are the D-stratified primary statistic. Splice component IDs are preserved from the registered source and checked equal across arms, not re-derived from images.

Synthetic self-test passed (ties, strict thresholds, summary consistency, duplicate/nonfinite/label/count refusals). Production invocation has not occurred. Independently review before using:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 \
  /home/narolski/mambamorph-code/.venv-spark/bin/python -I \
  src/AB1/ab1c_transfer_report.py \
  --out /mnt/t7/smad_next/AB1/c/read_20261114/ab1c_transfer_report.json
```

The output is exclusive-create, with no overwriting; this report is descriptive reuse of already committed learner data, separate from the once-only network read.
