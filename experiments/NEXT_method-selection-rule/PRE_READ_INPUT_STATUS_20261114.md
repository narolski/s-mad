# Development inputs for next method selection

Prepared 14 November 2026 in Codex against bound rule version 3 (`dbeb940`). This is a candidate-independent input package, not selection output or permission to open challenger archives. No candidate output, image, checkpoint or sealed benchmark product was read. No model was fitted and no image operation was executed.

## What already existed

The adversary's amendment 5 was committed and executed after the draft selection-rule review. Its outputs were committed at `bf96003` (13 November 21:01:58 CET) and pinned in `experiments/ADV_shortcut-floors/floors/pins_stage9.sha256`. This resolves several gaps described in the earlier draft and today's initial handoff:

| Required input | Verified existing product | Validation |
|---|---|---|
| Development plus clean test ladder | `sel360_rows.csv` | Exact source selection; 360 rows, 180 positives, 110 evaluation-pool person components; 100 development plus 80 clean test hosts |
| Blend difference for ladder rows | `/mnt/t7/smad_next/BD1/d_values.csv` | Every R4/R3 row maps to the D of its host's S4/S3; all 360 D values finite and positive |
| Shape-linked test hosts | `/mnt/t7/smad_next/DATA/overlap/shape_linked_test_hosts.csv` | 32 distinct test hosts, exact pool/split provenance; 11 are among the 80 clean test hosts |
| Landmark contrast | `lcomb_heldout.csv` and development manifest | 3,000 identical row IDs and labels, including 1,000 positives |
| Surround-matched subset | `lcomb_smatch_rows.csv` | All 360 pairs reproduced exactly using logit surround_gbt, 0.1 SD caliper and default_rng(20261117) |
| Same-data transfer learners | `transfer_Sb_rows.csv`, `transfer_SbFM_rows.csv` | Each has 3,000 landmark rows, 360 ladder rows and 720 matched-subset rows; exact IDs, labels, components and finite per-row scores |
| Within-D and regional controls | `sel360_withinD.json`, full source heldout/regional/withinD files | Matching committed historical pins; selected per-row controls included below |

Every current line of `experiments/ADV_shortcut-floors/pins.sha256` verifies. Neither its source directory nor its registration had uncommitted changes when inspected. The old `run_floors.py` pin failure has been resolved in the recorded work; no source re-pin was needed here.

## Prepared files

`src/NEXT/prepare_inputs.py` packages and validates only explicit allowed development sources. `inputs/manifest.json` records their hashes, committed provenance where available, snapshot paths and checks. `inputs/pins.sha256` hashes all packaged files, the manifest and the packaging/validation code, using paths relative to the repository root.

The package includes byte-identical copies of the original floor outputs and training manifests, as well as these deterministic joins:

- `inputs/sel360_with_D_and_floors.csv`: exact selection ladder with D, source component, label, host, role, shape-link flag, all-cue and non-F27/non-BLEND held-out scores, and regional held-out scores.
- `inputs/sel360_D_strata.json`: log-D quintile edges over those 360 rows, per-stratum class counts and coverage. Every stratum has at least ten rows per class; coverage is 1.
- `inputs/landmark_combined_rows_and_floors.csv`: exact landmark row set with all-cue, non-F27/non-BLEND and regional held-out values.
- `inputs/shape_linked_test_hosts.csv`, `test_hosts_clean_of_dev.csv` and `ladder_split.csv`: explicit person-list provenance for the subset definitions.
- `inputs/floors/`: original matching IDs, transfer per-row files, regional and within-D reports, held-out floor scores, and the descriptive `lcomb_bal` inputs.

Full-582-row `ri_R4_vs_R3_withinD.json` and regional JSON summaries are preserved as provenance. They must not be represented as summaries of the 360-row subset. The selected merged per-row controls provide the correct inputs for the rule's shared component-bootstrap calculations. The existing `sel360_withinD.json` contains its registered all-cue point and interval summaries; it is not a substitute for recomputing network-minus-floor differences with the rule's shared draws.

## Commands and checks

From any working directory, using the existing numerical environment:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/NEXT/prepare_inputs.py prepare
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/NEXT/prepare_inputs.py verify
```

Preparation passed all structural assertions. Initial verification passed 38 pins; the independent-review additions bring the package to 44 pins. A temporary copied package with one changed byte was rejected as input drift. Verification with `--require-clean` rejected the current uncommitted package, as required. `git diff --check` passed. No original source or existing working change was modified.

After independent review and a lead-owned commit, run the same validator from the committed isolated worktree with `verify --require-clean`. The final selection reader must call the strict validator before opening any challenger archive; passing it verifies input integrity only, not all selection admission conditions.

## Remaining work before opening results

1. Independently review this package and its provenance; commit the exact files and pins from a clean tree. The shared worktree has unrelated changes, so the lead plans an isolated worktree without stashing or restoring others' files.
2. Establish challenger eligibility, fit/platform gates, deadline receipts and score-exposure history separately. This package does not assert any challenger qualifies.
3. The GX training manifest and its per-row transfer learner are absent. Do not mark GX input-ready or substitute another training list. If GX proceeds, register and review the required learner computation and pin its inputs before the applicable result read.
4. Implement and independently review a full selection reader that applies version 3 exactly once, with shared bootstrap draws, comparators, fixed order and all criteria. No unified reader was identified in the inspected current preparation/adversary code; the packaging script is deliberately not one.
5. Floors and pins are fixed before result access. Later changes require an explicit provenance record and cannot silently replace pre-read inputs. Previously opened challenger scores are governed by version 3 section 7.

## Claims

- Commit `bf96003`: existing amendment-5 matching, ladder and per-row learner products (verified in git).
- `inputs/manifest.json`: source-level and package SHA256 inventory.
- `inputs/pins.sha256`: 44 files verified by the validator after the independent-review additions.
- Exact deterministic counts: 360 ladder rows; 110 components; 32 shape-linked test hosts; 3,000 landmark rows; 360 matched pairs; 4,080 transfer rows per training list.

## Independent review additions

The independent baseline-recovery reviewer requested explicit descriptive row subsets and clarification of matched floor provenance. Added before any challenger access:

- `facemorpher_same_180_hosts_R4_vs_R3.csv`: 360 native FaceMorpher rows, 180 positives, the same 100 development and 80 clean test hosts. This read is unstratified; for SbFM it must be labelled **seen engine**.
- `sel360_without_shape_linked.csv`: 338 rows after removing the 11 shape-linked test hosts among the 180 selected hosts.
- `sel360_development_only.csv`: 200 rows; `sel360_clean_test_only.csv`: 160 rows.
- `lcomb_smatch_rows_and_floors.csv` and `matched_floor_provenance.json`: explicit joined per-row floor inputs on the pinned matched rows.

Both agents independently reproduced the rule's quoted matched-subset floor values directly from the original full-landmark cross-fitted held-out predictions restricted to the 720 pinned rows: surround_gbt 0.5036728395061728, face_gbt 0.9485956790123458, and all-cue logreg 0.9451157407407407. These reproduce the rule's 0.504/0.949 reference and the v2 review's 0.945. The separate `lcomb_smatch_build.json` diagnostic refitted models only on the matched rows and has different values; it must not be substituted. No new fit is required to recover the rule's referenced per-row controls.

The floor-only `sel360_withinD.json` confidence intervals use default_rng(20261119). They must never substitute for network-minus-floor confidence intervals: version 3 requires shared component-bootstrap draws with default_rng(20261115), recomputed together for networks and controls.

The initial, superseded package manifest and pin list were preserved at `/mnt/t7/smad_next/NEXT/pre_review_input_package_20261114_1024/`. Their hashes differ from the reviewed extension, as expected. The final preparation/verification commands above passed on the extended package.
