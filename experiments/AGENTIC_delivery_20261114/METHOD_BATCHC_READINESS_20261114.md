# Count-controlled training ablation (AB1 batch C): method handoff

14 November 2026. Method/results role. **Code readiness verified at the exact snapshot below; production and scientific admission remain pending.** Existing OpenCode implementation and evidence were preserved. No reader source was changed, candidate archive member decoded, candidate score read, real reader invoked, canonical claim created, scheduler contacted, commit made or push performed by this worker.

## Current implementation and tests

The existing repaired reader uses the registered fifteen-fit overlay `bf276e548c5dc5a3c8d590d0500754c1d49ec87ad2e7b30237f05db94ffcafa7`, checks exact TASK/ARM/SEED and full pinned evaluation ID order before historical dict conversion, refuses duplicate IDs/nonfinite logits, and atomically claims the canonical pair-C journal before native access. A changed output pathname cannot bypass that claim. Failures retain it. The required within-D reports are preserved verbatim with context-only/different-population labels and verified committed bytes/stage-6 pins before the claim. The transfer companion separately validates the three registered learners and labels their summaries descriptive/unstratified.

| Artifact | SHA256 |
|---|---|
| `src/AB1/ab1_pm3_read.py` | `11dd5aef7e3a86a4d208e3ad75f81b6be80a62bce5ad958fad3c74f454cbf7f0` |
| `src/AB1/tests/test_pm3_admission.py` | `2c49cf1fb9d64f202eb9f49b510b8b991652762f31065d5790697fef0b7c7e3f` |
| `src/AB1/ab1c_transfer_report.py` | `d47f597712bb793a00a7dff9da104a6b43eb09f5bac845fc2c90d462efddd9ef` |
| `METHOD_BATCHC_OPAQUE_AUDIT_20261114.py` | `539f358222ee94ba98b48118deaac9423c5d714cf0dc38ed5a5186bacdacbd2b` |
| `METHOD_BATCHC_OPAQUE_RECEIPT_20261114.json` | `e18b23c3bed9419b97aceeef7d94c6448775131e8fda50af6c72f6e606387b23` |

Fresh synthetic reruns: all **24 admission/context tests passed** in 0.035 s; companion self-test passed. Three existing ResourceWarnings concern unclosed temporary synthetic manifests in historical `ab1_read.py:59`; no assertion failed. Opaque helper synthetic checks covered missing archive, missing sidecar, correct bytes, wrong named archive, wrong digest and duplicate sidecar entries. No full mock was repeated because the unchanged snapshot already has independently reviewed exact old/new full-mock equality after excluding only the new context field.

Commands used from `/home/narolski/smad-next`, each with `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 nice -n 10`:

```bash
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AB1/tests/test_pm3_admission.py
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/AB1/ab1c_transfer_report.py --self-test
/home/narolski/mambamorph-code/.venv-spark/bin/python -I experiments/AGENTIC_delivery_20261114/METHOD_BATCHC_OPAQUE_AUDIT_20261114.py --out experiments/AGENTIC_delivery_20261114/METHOD_BATCHC_OPAQUE_RECEIPT_20261114.json
```

The new audit imports standard-library byte/JSON/path/process helpers only, never tarfile, NumPy, a reader or an archive decoder. Its output is create-only. It compares 49 current dependency hashes with the existing independent integrity receipt, and computes streaming SHA256 over the exact 30 opaque archive byte streams plus their named sidecars. This is integrity work, not a preliminary native read.

## Fresh opaque integrity evidence

Execution: `2026-11-14T11:41:38.131663+00:00` through `2026-11-14T11:41:38.235353+00:00`; observed HEAD `7d5e06b7440269de37b338fa7be81940dd9c55a8`. Shared repository HEAD advanced during this assignment; source hashes match the existing reviewed snapshot. This worker did not commit. All **49 dependencies and 30 archive/sidecar checks passed**, total archive size 146,739,200 bytes. All names, requested arm/seeds, resolved paths, sizes and individual hashes are in the new receipt. The `seed_requested` field is a filename/request identity, never proof of embedded native seed.

- Fifteen new arms: `/mnt/t7/smad_next/coordination_20261114/archives/AB1C/AB1C_{SpV,BN,BV}_s{408..412}.tar`. Current bytes and sizes match the authoritative `NEW_COLLECTION_VERIFIED.json` at `2026-11-14T10:32:47.178346+01:00`, including recorded remote source paths. The collection receipt SHA is `a4027f628d460a5f131b030962fd6e7c8031e084849787c30c47f101511177af`.
- Fifteen comparators: `/mnt/t7/smad_next/AB1/results/AB1_{Sb,B,Sp}_s{408..412}.tar`. Current hashes match current named sidecars. **Upstream authoritative collection provenance is not established by this new receipt**, because the new-arm collection does not contain these comparators. Sidecar agreement alone does not close that requirement.
- All 49 source/metadata/floor/learner dependencies still match the prior independent receipt `OPENCODE_BATCHC_B2_INDEPENDENT_LOGS_20261114/integrity.json` (`2667c71a9900302482c665d46ff6d95b1ef90b59274fbfe0dcd9a9533ef8aa89`). Absolute live dependency paths remain explicit; checkout cleanliness alone does not isolate them.
- Canonical `C.claim.json` and `C.complete.json` were absent under `/mnt/t7/smad_next/AB1/READ_ONCE_PM3` at the fresh audit. This is a timestamped observation, not a reservation. No production output was created or output directory prepared by this worker.

Existing independent reference-only numerical checks are in `OPENCODE_BATCHC_INDEPENDENT_REVIEW_20261114.md`: 12 floor/type checks with synthetic zero candidates, within-D committed context and all three real descriptive learner joins/summaries. They access existing reference values, not candidate outcomes. Their underlying inputs remain unchanged in the 49-path check; those prior numerical outputs were not recomputed here.

## Remaining release work

1. Independent reviewer checks this audit/receipt and current implementation, then lead binds exact sources and all external inputs through the applicable clean committed pin/release procedure. An implementation commit does not itself release production.
2. Bind comparator authoritative collection provenance, all thirty completed-fit/arrival dispositions, and the applicable cutoff/late treatment. The timestamped batch-C scheduler record already reports all fifteen `6316845` tasks completed with `0:0`, latest `2026-11-14T10:26:14`; lead must bind its receipt rather than infer native successful training from archive presence.
3. Bind exact production command/environment, fresh durable output and stdout/stderr/exit receipts. The command requires explicit `--c-results /mnt/t7/smad_next/coordination_20261114/archives/AB1C --ab1-results /mnt/t7/smad_next/AB1/results`; the default C path is not the collected location. Recheck source/input bytes and journal/output absence at release. The reader claims internally; never preclaim.
4. Only the authorized guarded first read can establish embedded task identity, evaluation score order/finite values, training/evaluation manifests, H100/steps/pack/overlay/n_items/loss gates. Do not run `_validate_native_archive` as opaque preflight. Preserve failures and journal; no automatic recovery/replay.
5. Independent results review precedes interpretation. Missing/native-invalid outcomes remain explicit with their actual reason. Neither code readiness nor missing software/data becomes a scientific negative result. No NEXT challenger promotion or sealed benchmark read follows from this ablation.

## Registered scientific scope and complete result handoff

H-c1 is **Sb−SpV** on OpenCV two-person whole-frame morph versus same-person whole-frame morph (R4/R3; warp-only is R2w), D-stratified on 100 development plus 80 clean test hosts, with the inherited unstratified agreement/sign cap. It controls total row count, class balance and positive repetition; matched-negative content remains inseparable from 312 additional unique images. H-c2 is **BN−BV** on the same primary population, with identical positive rows and no face-spliced positives; negative diversity still differs. Neither test alone identifies an identity-specific mechanism.

Secondary S4/S3 on clean80 is near-certain by training design and is not new mechanism evidence. The difference-of-differences is printed only. Shape-link sensitivity is dev+clean69. Preserve the registered 2,000 joint component draws, RNG and thresholds; 99.5% intervals are sensitivity prints, not complete 16-verdict familywise control. The bootstrap conditions on these five trained seeds and registered dependence structure; it does not establish universal out-of-identity transfer.

After release, the reviewer packet must retain all six arms and all five requested seeds (including missing, negative and inconclusive), all loader statuses, per-seed primary/secondary stratified and unstratified values, paired gains, readable-seed/draw counts, intervals, sign cap, registered verdict and printed interaction. Print all diagnostic populations and all-cue/nuisance floors with original population labels, the within-D context and the three same-data descriptive learners. No seed/family selection, new margin, dropped negative row, engine-scope change or new inference is authorized. Link every table to exact reader output/source/input hashes.
