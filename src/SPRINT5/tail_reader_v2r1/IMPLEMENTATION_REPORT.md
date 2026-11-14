# Tail v2r1 admission repair handoff

R1 fixes the exact independent review blocker from `reader_implementation_v2/ASTRA_TAIL_V2_IMPLEMENTATION_REVIEW.md`, SHA `2286e62c29415f8dfb5e84657a9ea0aefbb72dde5f3d4f7e83e78e73a31add64`. Frozen v2 source `5ae5f48e8b5525ae53a3603f24444a0efef833c567bc52caa308fb9119fba195` and binding `36866c220c1df69b57ca69fb271121c9704ad417e2f93358eac4398cc8e8fdfa` remain preserved. New source is `src/SPRINT5/tail_reader_v2r1/`; new evidence/binding is `tail/reader_implementation_v2r1/`.

`validate_binding` now resolves the input argument once as `binding_path`, keeps input iteration in `pin_path`, and passes the actual binding to explicit committed-path selection and Git validation helpers. Real temporary-Git regressions pass for clean tracked binding and reject tracked-but-dirty and untracked bindings with all other pins clean. A production-wiring regression ensures the original binding path reaches that gate. Matching a new digest cannot bypass the separate Git requirement.

All 26 existing fixtures plus two regressions PASS (28 total). Full input-only metadata/design checks are repeated. Primary `tail_stats.py`, `diagnostics.py`, collector, payload and shared utilities remain byte-identical to frozen v2. Only admission repair, binding/evidence version pointers, tests/docs and the result-facing required-baseline annotation change. No statistical definition, RNG, journal, output, candidate scope or actual release changes. The same once journal/output remain shared across all revisions. No actual candidate payload, collector/reader, checkpoint, GPU or scheduler access occurred.

Exact diffs and an immutable delta manifest accompany this handoff. Independent delta review and root adoption of the new binding remain pending; scientific, collector, baseline and camera releases remain HOLD.

---

Preserved v2 implementation context follows; its source/input pins identify the historical v2 snapshot rather than this new revision:

# Tail v2 implementation handoff

Status: CODE_ONLY_READY_FOR_INDEPENDENT_REVIEW. Source: `/home/narolski/smad-next/src/SPRINT5/tail_reader_v2/`. Evidence: `experiments/SPRINT5_20261114/tail/reader_implementation_v2/`. No actual candidate archive, logits, score member, checkpoint, model weights, collector or reader invocation occurred. No GPU or scheduler operations occurred.

V1 remains exactly preserved: source manifest `d2912f78818bc32ef7164eb9bd3327fc579453b2a216347c3e5405deb536dd30`, input binding `f91984a65b46578b57486a8b101b3181e698f6df212d2b6a31c23059d488082f`. Paired, breadth, HN and adopted policies were not changed. V2 uses the SAME permanent once journal and output as v1; the two versions cannot authorize separate reads. No actual journal claim exists from this work.

The entire `tail_stats.py` file is byte-identical to v1. Primary 90%-positive calibration, six FA cells, all eight NI slots, exact bootstrap order and RNG, and the metadata design hash are unchanged. V2 attaches diagnostics only after unchanged primary analysis. Scope/release/input binding is separately versioned.

Diagnostics implement root adoption commit `8cd6b8e`, receipt SHA `3c679d59e513ab3fd405f73ee164229c7914bac80cd1afc650ed824942102f17`, exact proposal `1bd8504fe153f733d8fd038be52c99752d669eba251fc592410668db12dae446` and independent review `12dba40a594d488f8e4c4048eb1b25e29e09962f851433792161a97c88d8711d`.

Six AUC cells use the same-source native held-out positive mixture against each genuine processing cell. Positive pools are FERET 54 rows/13 components (46 AF0, 4 R4, 4 S4) and FRGC 126/14 (100 AF0, 13 R4, 13 S4); pair denominators are 3,780 and 3,276. The label states native attack mixture versus the genuine processing level, without implying processing matching or an isolated source effect.

Eight quantile distributions are the six genuine cells plus two native positive pools. The fixed grid [.10,.50,.90,.95] uses float64 linear interpolation. Raw Qp and Qp−original primary tau are reported for every arm/seed, arithmetic means and both paired contrasts. No calibration quantiles, processed-positive proxy, extra probability, RNG, winner gate or diagnostic CI is added. Every diagnostic explicitly says NOT_ESTIMATED_DESCRIPTIVE_DIAGNOSTIC with interval null. This is a prospective uncertainty clarification, not uncertainty PASS or equivalence.

Verification: 26 generated-only tests PASS. The 19 primary/admission/collector/journal fixtures remain, plus seven diagnostic/differential checks: shared once/output constants; six AUC/eight quantile panels and explicit null uncertainty; tied/perfect/reversed ranks and contrast orientation; n2/n26 interpolation and unequal pair denominators; joint calibration+evaluation additive shift preserves AUC/threshold-relative quantiles while raw quantiles shift; nonfinite/calibration/processed-proxy rejection; byte-identical v1 primary source, exact differential primary/NI/bootstrap output and no RNG creation/advancement by diagnostics.

Input-only validation reproduces 70 calibration positives/26 components, 180 evaluation positives/27 components, 288 genuine rows, all 15 exact training plans and zero calibration/evaluation person/photo/component overlap. All 10,000 attempted bootstrap draws reproduce design hash `54ffe7325dfbd9d1821bafbdf916f8ed5cef24aed5388a66f5295e65749d5db4`, with no redraw and no empty required calibration/genuine cells. The actual positive guard component counts 10/0/17/17 still make complete utility INCONCLUSIVE regardless of candidate effects.

Remaining gates: independent v2 implementation/collector/tests review; root adoption of the new v2 binding; complete 15-fit opaque metadata admission; separate collector and scientific read releases bound to exact v2 source and roster. The frozen-baseline-threshold panel remains REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION; inherited camera auxiliary remains HOLD. Thus completing this implementation does not declare all preregistered scientific reporting complete or grant a scientific read. No actual fit eligibility or result is inferred from submissions/files.
