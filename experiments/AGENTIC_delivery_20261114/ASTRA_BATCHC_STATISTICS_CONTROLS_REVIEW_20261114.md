# Independent statistics and controls admission review — 14 November 2026

Reviewer: Astra, independent of the method implementer and prior reviewers. Snapshot: HEAD `7d5e06b7440269de37b338fa7be81940dd9c55a8`; checks began at 12:41 CET. **NO-GO for production reading at this snapshot. GO for the reviewed implementation and metadata-only integrity packet.** No candidate archive, score payload, sealed benchmark or production reader was opened or invoked. No cluster action, commit or source modification was performed. Only this review is authored here.

## Exact reviewed packet

| File | SHA256 |
|---|---|
| src/AB1/ab1_pm3_read.py | 11dd5aef7e3a86a4d208e3ad75f81b6be80a62bce5ad958fad3c74f454cbf7f0 |
| src/AB1/tests/test_pm3_admission.py | 2c49cf1fb9d64f202eb9f49b510b8b991652762f31065d5790697fef0b7c7e3f |
| src/AB1/ab1c_transfer_report.py | d47f597712bb793a00a7dff9da104a6b43eb09f5bac845fc2c90d462efddd9ef |
| METHOD_BATCHC_OPAQUE_AUDIT_20261114.py | 539f358222ee94ba98b48118deaac9423c5d714cf0dc38ed5a5186bacdacbd2b |
| METHOD_BATCHC_OPAQUE_RECEIPT_20261114.json | e18b23c3bed9419b97aceeef7d94c6448775131e8fda50af6c72f6e606387b23 |

The last two paths are relative to this review directory. Independently verified all five hashes, HEAD identity of the three implementation files, and all 49 dependency hashes in the receipt. Checked 30 distinct archive receipt entries, all passing; 15 batch-C entries bind the authoritative NEW_COLLECTION receipt. I did not independently hash or parse the archives. The script performs opaque hashing only and honestly labels the 15 comparator sources as lacking authoritative collection binding. Its `all_byte_checks_passed` is not an admission flag. The accompanying METHOD_BATCHC_READINESS_20261114.md was also reviewed: its release restrictions agree with this disposition. A terminology correction was requested: R4/R3 means two-person versus same-person whole-frame morph, not blend-versus-warp (warp-only is R2w). This wording correction does not change the statistical implementation.

Independently executed `src/AB1/tests/test_pm3_admission.py`: **24 tests passed**, 0.029 seconds; three existing unclosed synthetic-manifest ResourceWarnings at `ab1_read.py:59`. Companion `--self-test`: PASS. Interpreter was `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`, with four BLAS/OMP thread limits of 2 and `nice -n 10`. Existing floor/learner numerical validation is supported by the separately authored OPENCODE independent review and its pinned receipts; this review did not repeat numerical reference reads.

## Registration and controls

Read AGENTS/CONTINUE, current owner/workflow/notebook, delivery README/statistical/control plans, prior workflow and batch-C admission reviews, source binding, AB1 amendments 4/4b/5/5b/7/7b and their pre-run review. AB1 prereg lines 642–716 govern this ablation; prospective new-cycle requirements do not silently replace it.

- `ab1_pm3_read.py:259–266,355–435` implements H-c1 = Sb−SpV, H-c2 = BN−BV, seeds 408–412. Primary is OpenCV R4/R3 D-stratified on dev+clean80; secondary is unstratified S4/S3 clean80 with positive full-set stratified gain. The +0.03 margin, positive lower 95% bound, four-of-five (or all four readable) sign requirement, unstratified agreement and dev/clean sign cap are retained. Fewer than four readable seeds is not read. Interaction is printed only.
- Independently checked permitted training manifests: all four arms have 8,386 rows, 4,193 per class. Positive row multisets agree exactly for Sb/SpV and BN/BV after removing only the arm annotation. Unique IDs are 5,535 / 5,223 / 5,411 / 5,099 respectively. Both contrasts therefore control row/class counts and positive repetition; **content and 312 extra unique images remain inseparable in both pairs**. Neither pair proves a pure content effect or excludes diversity. BN−B is confounded by positive repetition and remains descriptive.
- The bootstrap at lines 337–390 samples host-partner connected components jointly across arms and seeds. Metadata-only reconstruction gives 151 components on 180 primary hosts (largest 6; sizes 133×1,13×2,1×3,3×4,1×6), and 51 on 80 secondary hosts (33×1,13×2,1×3,3×4,1×6). No repeated external partner was found within either host set. This is compatible with the registered graph units; no giant-component failure is present. Intervals condition on these fitted seeds: seeds themselves are not resampled. They are not population-level uncertainty over arbitrary retraining, engines or sources.
- D quintile boundaries are recomputed inside each component draw by the registered statistic; unreadable stratified draws are excluded and counted. Secondary always uses the unstratified branch fixed by amendment 5b, not a result-dependent switch. Retain invalid-draw counts, paired seed coverage and all failures in the result review.
- 99.5% intervals are sensitivity prints. They do not provide 16-verdict familywise 95% coverage; nominal 95% verdicts must not be marketed as a corrected confirmatory discovery. The registered family description is historical, including superseded/descriptive comparisons, and is not repaired after seeing results.
- S4/S3 effects are expected from training by design (prereg 703–704), not fresh mechanism tests. The clean69 sensitivity is retained. Post-freeze ablations cannot become NEXT candidates or alter the frozen method (prereg 644–645). Prior development findings and the 7b timing disclosure must remain explicit.
- `_within_d_context` at lines 67–106 validates committed context and stage-6 pins, preserves both full JSON objects, and labels different populations/context-only. It runs before the production claim (300–302), and mock mode substitutes synthetic placeholders. The transfer companion prints the registered same-data learners with correct population/threshold labels; it makes no network-minus-learner inference. Neither in-domain floors nor these transferred learners are interchangeable with the D-stratified deciding statistic.

## Admission checklist and remaining blockers

1. **PASS — implementation binding:** reviewed guards/context/companion are committed and unchanged at the hashes above. Exact task/arm/seed, full ordered eval IDs, duplicate/shape/nonfinite checks precede the historical loader. Correct batch-C overlay is pinned. Prior B1 is resolved.
2. **PASS within existing evidence — references:** all 49 dependencies rehash correctly, including real resolved paths. Prior independent B2 receipt covers 12 floor/type numerical checks and three learner validations. Do not imply the synthetic guard suite alone exercises this path.
3. **PARTIAL / BLOCKER — source provenance:** the method receipt binds 30 opaque byte/sidecar checks and upstream collection for 15 batch-C archives. Comparator authoritative source/collection provenance for Sb/B/Sp ×408–412 remains unbound. Add evidence or an explicit independent provenance disposition before read; sidecar agreement alone is insufficient. Bind completed-fit/arrival/deadline and late/missing dispositions for all 30. Native success cannot be inferred from filenames. See METHOD_BATCHC_OPAQUE_AUDIT_20261114.py collection branch and its `remaining` field, and OPENCODE_BATCHC_ADMISSION_20261114.md B3–B4.
4. **BLOCKER — complete execution release:** no reviewed release receipt binds a fresh durable output, exact command/interpreter/environment, these source/input/collection hashes and failure handling. Use `--c-results /mnt/t7/smad_next/coordination_20261114/archives/AB1C` and `--ab1-results /mnt/t7/smad_next/AB1/results`. Default C path is not the collected path (`ab1_pm3_read.py:51,253`). No `-O`: imported guards use assertions. Recheck all resolved dependency bytes even from an isolated checkout, because imports include live absolute paths.
5. **REQUIRED AT RELEASE — once/output state:** method receipt records no canonical C claim/completion. Recheck via lexists, including fresh output and parent readiness. Reader takes its own atomic claim at line 302; do not preclaim or use real invocation as preflight. Claim persists on failure; no deletion, alternate-output retry or silent re-read. Guard rejection is an infrastructure/provenance disposition, not evidence of a scientifically failed model. All statuses require later review.
6. **REQUIRED DURING/AFTER AUTHORIZED READ:** actual native provenance and finite ordered scores are checked only on first authorized payload access. Keep exact command, start/end, stdout/stderr, exit status and output hash. Independent results review remains mandatory before any scientific conclusion. This review does not assert native guards already passed.

An independent release addendum may close items 3–5 against exact evidence; until then the disposition remains **NO-GO**. No additional fit, benchmark read, promotion or threshold change is authorized by this review.

## Contribution 3 interpretation boundary

The intended contribution is reduced response to specified artifacts while preserving or improving face-spliced attack detection. An AUC increase alone can result from score redistribution and does not establish that conjunction. Batch C supplies a count-controlled development ablation with the diversity limitation above. Its expected S4/S3 comparison alone does not establish independent robustness. Any eventual contribution statement must connect separately supported genuine/control false-alarm behavior and attack sensitivity at a fixed, prospectively specified operating threshold, with per-seed and dependency-aware uncertainty and named perturbations. Do not invent a new post-result decision threshold, claim universal shortcut freedom, or replace the registered batch-C decision with this future target. MAD22 development exposure and shared FRLL genuine-photo exposure remain applicable.

CLAIMS:
- commit 7d5e06b7440269de37b338fa7be81940dd9c55a8 Bind independently reviewed Batch-C guards and reference preflight
- file src/AB1/ab1_pm3_read.py sha256 11dd5aef7e3a86a4
- file METHOD_BATCHC_OPAQUE_RECEIPT_20261114.json sha256 e18b23c3bed9419b9
- number synthetic guard tests = 24 @ independent execution 2026-11-14 12:41 CET
- number rehashed receipt dependencies = 49 @ independent metadata verification
- number primary/secondary graph components = 151/51 @ independent permitted split-metadata reconstruction
