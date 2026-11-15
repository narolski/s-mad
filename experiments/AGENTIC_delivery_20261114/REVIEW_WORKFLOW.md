# Independent workflow and batch-C guard review

Review date: 14 November 2026. Reviewer: controls worker, independent of the workflow integrator, method-plan/guard author and statistics-plan author. The reviewer authored `CONTROL_AUDIT.md`; this review does not constitute independent approval of that document. Only documentation, source code and synthetic temporary fixtures were read. No native score/archive payload was accessed, no production once marker was created, and no SSH/git operation occurred.

## Disposition

**GO for operational workflow preparation and the narrow overlay/once-only repair as reviewed below; NO-GO for production batch-C score reading or benchmark release.** The six-role workflow preserves the bound current selection rule, explicitly separates prospective thresholds, and does not pretend to enforce OS-level access separation or unattended monitoring. The plans correctly prioritize consuming already-completed count-control fits before duplicating work. Scientific and numerical readiness is not established by these documents.

## Reviewed code and synthetic verification

| File | SHA256 at review |
|---|---|
| `src/AB1/ab1_pm3_read.py` | `4ba06f2ab7e3a340d65eed2163762f2b52983dc6ec0ddcf856d69c340a8380be` |
| `src/AB1/tests/test_pm3_admission.py` | `3e5c52c895a52e08cd270b1ecbe486e1241394644303099abfc6692f9f5e69ee` |

Executed independently:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 \
  /home/narolski/mambamorph-code/.venv-spark/bin/python -I \
  src/AB1/tests/test_pm3_admission.py
```

Result: **11 tests passed** in 0.019 seconds. Tests use only synthetic temporary archives and claims. Three `ResourceWarning` messages identify pre-existing unclosed manifest readers in `ab1_read.py:59`; these do not invalidate the test outcome, but should not be described as a warning-free run.

Confirmed by code inspection and tests:

- Correct batch-C overlay `bf276e548c5dc5a3c8d590d0500754c1d49ec87ad2e7b30237f05db94ffcafa7` agrees with the registered launcher. All three synthetic batch-C arms pass the native loader; the obsolete overlay is rejected.
- Atomic create-only canonical claim is taken before any archive loader and persists on failure. Concurrent claimants produce only one winner; changing the output path cannot bypass the per-pair claim. Mock mode does not consume a production claim.
- Existing output, including a dangling symlink, is refused; output is create-only and fsynced. CLI cannot override the canonical claim root.
- Configurable source paths are recorded in the claim, preserving path-adapter provenance.

These are narrow guard tests, not complete scientific analysis or native dataset admission tests.

## Production-blocking findings

### R1. Seed provenance is not checked by the imported native loader

`ab1_read.load` verifies arm by substring and source provenance but does not compare `SEED` in `task.env` with the requested seed. The wrapper assigns the filename's requested seed to the result. A renamed/mispacked valid archive can therefore be assigned the wrong seed while passing the current guard. Require exact parsed arm and seed identity in a pm3-local wrapper (rather than silently modifying the historical shared reader), and a synthetic wrong-seed refusal test. Seed identity is essential to all paired contrasts.

### R2. Evaluation row arrays are silently collapsed/truncated

`ab1_read.load` constructs `dict(zip(id, logit))` without asserting unique IDs or equal array lengths. Duplicate rows collapse and unequal lengths truncate; pm3's later check verifies only that needed IDs exist and are finite. Require exact one-dimensional array shape agreement, unique IDs and the expected evaluation manifest membership/order or an explicitly validated permutation. Add synthetic duplicate-ID and mismatched-length refusal tests. A valid manifest hash stored inside an NPZ is not sufficient validation of its contents.

### R3. Required transfer-learner reporting remains pending independent review

The statistics agent is preparing the companion. At this review snapshot no transfer companion was available under `src/AB1/*transfer*`. The existing pm3 output prints in-distribution floors but not the required same-data learner report. Review the companion, exact learner pins, joins, exclusions and scope labels before release; no production command is approved by the narrow guard tests.

### R4. Complete external dependency and admission receipt is still required

Before native reading, independently pin/verify the complete source archive list and sidecars, actual task seed identity, comparator sources, manifests, transitive imports, floor paths and environment. The once claim records paths and reader hash, not a complete admitted input-set hash. Existing absence of pre-read admission enforcement is acknowledged by the workflow; operational release must supply the exact reviewed receipt. Missing dependencies cannot be retroactively called scientifically failed models. A failed claim is retained for independent recovery disposition, not automatically deleted/retried.

## Documentation corrections

1. `STATISTICAL_PLAN.md` §9 says to execute “with the lead's once-read guard already claimed.” This is stale after the patch: **the reader itself takes the canonical claim**. Replace with: “After independent admission, with no existing canonical claim/output and the output directory prepared; the reader atomically claims before archive access.” The producer command also needs its reviewed `--c-results` mapping if archives remain in the collection directory. Do not pre-create the reader's claim or use its real command as preflight.
2. `workflow_state.json` still describes stale overlay and once-protection as unresolved implementation blockers. Mark them “implemented; narrow synthetic review passed; production admission pending” after this review is integrated, while adding R1/R2 and companion/admission blockers. Do not mark the overall read ready.
3. README/state now correctly specify six roles. `COMPUTE_PLAN.md` still says five roles; align that descriptive count and rotation with the README. The scientific reviewer delivers hypotheses, not its own release approval.
4. A linked `SCIENTIFIC_REVIEW.md` is forthcoming, not yet evidence at this snapshot. Keep its status pending until delivered and reviewed. Likewise, the unresolved numerical parameters in prospective plans block new confirmatory launches, not current work under already bound registrations.

## Positive design findings and remaining scope

The statistical plan correctly distinguishes shared people from independent benchmark replications, warns that partner graphs may collapse into a giant component, separates fixed releases from retrained seed uncertainty, and does not treat non-significance as equivalence. The method plan correctly acknowledges unique-image diversity remains unmatched in existing SpV/BV controls. Compute plans preserve existing jobs, qualify runtime assumptions and do not infer platform compatibility or spending approval.

A file-based checklist is operational coordination, not enforcement against arbitrary filesystem access. The workflow describes that limitation honestly. No evidence supports a guarantee of significance, superiority or universal shortcut freedom. Numerical tolerances, precision feasibility, fresh transfer panels and benchmark dependency manifests remain future preregistration work. The current NEXT selection still requires complete native adapters, reviewed admission and registered confirmation.

Review will need an addendum pinned to the repaired guard/companion hashes before any native batch-C invocation. No output interpretation or scientific conclusion is issued here.

## Addendum A: companion and documentation corrections

Subsequent inspection confirms the compute plan now specifies six roles and the statistics plan now explicitly forbids externally preclaiming the reader journal. Documentation findings 1 and 3 above are resolved in the current files; the preceding observations are retained as review history.

Reviewed `src/AB1/ab1c_transfer_report.py`, SHA256 `d47f597712bb793a00a7dff9da104a6b43eb09f5bac845fc2c90d462efddd9ef`. Independently ran its `--self-test` through the same constrained interpreter/environment as above. **PASS**: tied AUC, strict threshold convention, summary roundtrip, duplicate/nonfinite/label/count rejection. No real learner rows were loaded for this review.

**GO for commit of the descriptive companion in its stated scope.** It reads only committed, stage-pinned existing learner files; verifies common metadata across SpV/BN/BV, checks selection row identity/labels/components, recomputes summaries and refuses mismatches. It preserves the distinction between unstratified references and the D-stratified AB1 deciding statistic, and between original contrast populations and clean-host subsets. Its output is create-only and it performs no fit, candidate read or network-minus-learner inference.

The synthetic self-test validates numerical primitives and refusals, not the complete real-file provenance path. Actual committed-input pin validation, exact summary reproduction and the output hash remain required preflight evidence. No candidate admission is conferred by a successful companion print. If a later claim needs a network-minus-learner inference, that requires a separate registered join/uncertainty analysis; this companion intentionally does not provide one. R3's missing implementation is addressed; integration/provenance remains under R4. R1/R2 native loader repairs were not yet available at this addendum's hash snapshot and remain production blockers.

The subsequently delivered `SCIENTIFIC_REVIEW.md` was also inspected. Its six-role rotation, bounded event-driven synthesis, three-card limit, prospective hypotheses and prohibition on significance-driven selection agree with the workflow. It correctly labels SbFM's FaceMorpher as a seen engine and distinguishes a sufficiently precise null from an uninformative result. GO as an operational hypothesis queue, not a preregistration or run release. Documentation finding 4's missing-file condition is resolved; its general requirement to retain unresolved future thresholds remains.

## Addendum B: native task and row validation repair

Independently inspected and tested the repaired reader:

| File | Final reviewed SHA256 |
|---|---|
| `src/AB1/ab1_pm3_read.py` | `a31f51955b78f4c1e746446a0555b1dcd7d4f010e7b85c4e4715782dea8076fb` |
| `src/AB1/tests/test_pm3_admission.py` | `c667782d57effc482587f031cd438ca82e3afabb938b7d3a6d301bff84c1a6aa` |
| `src/AB1/ab1c_transfer_report.py` | `d47f597712bb793a00a7dff9da104a6b43eb09f5bac845fc2c90d462efddd9ef` |

The guard suite now passes **18 synthetic tests**, independently rerun in 0.033 seconds with the same interpreter and thread limits. The pre-existing manifest-resource warnings remain. R1 and R2 are resolved in this code scope: a local preloader hashes the archive and pinned evaluation manifest, checks unique regular tar metadata members, parses exact TASK/ARM/SEED with duplicate-key refusal, requires one-dimensional equal-length ID/logit arrays, rejects duplicate/nonfinite values, and enforces the exact full pinned evaluation ID order before the legacy dict conversion. Both batch-C and AB1-comparator paths use this preloader; FS1 also routes through it. Historical imported readers were not modified.

Source-only compatibility check: the AB1 driver writes the unquoted `TASK`, `ARM`, `SEED` lines expected by the parser; `run_c.sh` preserves the task file into the archive. `pn1_score.py` scores the manifest in order at limit zero and stores those IDs directly. No native task file or score payload was opened to establish compatibility; exact native provenance remains part of admission.

**Final implementation disposition: GO for commit of the guard repair, its tests and the descriptive companion at the hashes above. Production read remains NO-GO pending the complete reader-context/external-dependency admission and registered result paths/pins.** The repair does not itself establish that all historical task files satisfy its stricter guard, that every required floor context can be evaluated, or that the entire scientific calculation completes. Test success is not a release receipt. If a real preflight reveals an incompatibility, retain the exact evidence and obtain a prospective reviewed repair; do not weaken identity/order checks after observing outcomes.
