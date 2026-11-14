# Independent pre-run review: NEXT native selection integration

14 November 2026. New independent statistics/code reviewer; not the implementation author. Reviewed the current working bytes, approved v3 at `dbeb940`, prior `PRERUN_NEXT_READER_20261114.md`, and the **appended continuation increment** of `OPENCODE_ADAPTER_HANDOFF_20261114.md`.

## Verdict

**CHANGES REQUIRED before GO-for-commit of this increment as a complete v3 reader.** One substantive software blocker is invented: the global refusal with exactly four usable DINOv3 candidate seeds. The complete five-by-five route and SbFM route passed the reviewed synthetic checks. No production admission or scientific read is approved by this review.

## F1 — major: exactly-four-candidate refusal contradicts the rule's read-seed provision

Locations: `src/NEXT/read_selection.py:375–377,994–1001`; corresponding integration tests currently assert the refusal.

V3 §4 explicitly defines **“Seed-mean = the mean of d_s over the read seeds.”** Section 5 introduces its counts with **“For DINOv3 ... the same counts apply”**, then allows **“4 of 4 with four”** and says **three or fewer**, not four, are not read. BB2's inherited five-seed mode likewise expressly allows four read seeds. Five-seed *mode* is not a guarantee of five surviving fits/gates.

The §3 parenthesis about resampling five candidate seeds describes the complete planned design. It must be read together with the explicit incomplete-read provision, not used to delete it. A failed fifth fit is retained as a failure in the five-seed counting denominator; it contributes no invented AUC. The defined point estimand is the mean of the four read candidate statistics against the fixed five-comparator mean. Its empirical seeds × components bootstrap resamples the **four observed candidate seeds, four draws with replacement**, independently of five comparator draws, sharing the component replicate. This is the ordinary bootstrap of the specified read-seed mean, not imputation of a fifth fit. No change to rows, thresholds, margins, eligible sources or scientific rule is needed.

Required correction: remove both exactly-four global refusals; compute the same seed-mean intervals for four or five usable candidates (the helper already supports these shapes); retain denominator five, all-four passing counts, and three-or-fewer not-read. Change the author tests from expecting refusal to checking these outcomes, including a post-claim failure. Apply and independently check this interpretation **before any real outcome is read**, uniformly for all registered failure causes. Do not resample five values from four fits, invent a failure score, or selectively omit an interval.

The new independent probe reproduces both refusals. Its two `expectedFailure` cases are **documented defects, not passing acceptance tests**. Remove those decorators when fixing F1.

## Missing comparator: a different, necessary fail-closed condition

V3 §3 fixes the **five H100 AB1 Sb fits**, and §4 repeats **“comparator's five-seed mean.”** The read-seed mean exception governs candidate d_s; it does not define a replacement baseline when one of those five comparator statistics is absent. Missing/nonfinite/exact-gate-refused comparator evidence makes that specified baseline unavailable. Null-comparator preflight refusal and runtime global refusal are defensible while the arm is admitted as `read`.

Do not compute a reduced four-comparator mean, pair unlike seeds, impute a comparator, or turn this into a losing DINOv3 result/default Sb. Any eventual non-read disposition must instead be independently substantiated under the existing permitted missing-input/infrastructure provisions before admission; a software limitation alone is insufficient. Thus this necessary baseline condition does **not** justify the exactly-four-candidate restriction. This review authorizes no post-result rule amendment or replay.

## Audited behavior with no additional finding

- **Opaque admission/source binding:** preflight checks clean committed pin closure, rule ancestry, exact admission GO bytes, all eight dispositions, eligible-arm review, source inventory, role/seed mapping and original hard-pinned AB1 comparator sources. SbFM is additionally bound to the submitted configuration; E3 to the frozen five-seed source map and batch 256 × 1. Fit and supplemental binary hashes/path/time receipts are checked without tar member access. Native module pinning is mandatory and rechecked at dispatch. Digest changes are global failures, not a seed silently removed from selection.
- **Receipt limits:** an inventory or `producer_sha256` field alone cannot prove actual producer/job history. The independently pinned admission review must establish it from authoritative submission/arrival evidence. The hard supplement-producer/config pins and embedded scorer/config checks support that boundary. No actual receipt/admission package was certified here.
- **Once ordering:** `run_admitted` performs preflight, support and contrast validation, then claims the fixed stage journal before `execute` opens candidate members. Success and failure both block replay. Tests exercise the actual orchestrator with a separate temporary journal. Native archive readers rehash their open descriptor, reject aliases/traversal, use non-pickle NPZ decoding, and check exact ordered finite rows. Supplemental exact gates precede supplemental score decoding; fit arrays are read after the once claim.
- **Same-path borders:** candidate and comparator border rows are replaced from the same admitted supplemental archive. Path identity includes its digest. DINOv3 MS1 rows also come from the W2 route for both sides. E3 A uses only its required MS1 family; missing unrelated A TT1/MEDS is not an invented guard.
- **Floors:** SbFM uses the `train_SbFM` transfer rows; its comparator uses `train_Sb`. E3 uses Sb. Training-list references, per-set IDs, labels, components and finite values are validated; four in-distribution floor families and both transfer learners are printed. Per-network floor differences share the network's component draws. Actual transfer fitting provenance and fixed floor-column choices remain an external admission obligation. SbFM FaceMorpher descriptives carry “seen engine.”
- **Criterion (f):** SbFM H-fm3 uses the 191 test OpenCV two-person morphs versus 191 warp-only rows, inclusive −0.02 margin and comparator AUC <0.98 testability. It does not add H-fm1/H-fm2 hypotheses as extra selection gates. E3 requires finite A/B/Sb fits, unique-row own-rule training accuracy ≥0.75 for all three, and candidate lad_S4 versus lad_S3 training AUC ≥0.80. Four passing seeds are required. A finite under-adequate fit remains in the read and fails its gate; it is not discarded for a better mean. Storage uses its separate candidate/A adequacy condition, not B adequacy.
- **Five-by-five statistics:** each candidate scalar subtracts the mean of five comparator statistics, not a statistic of averaged logits. Component replicates are shared within a contrast across all networks/floors. Candidate and comparator seeds are independently resampled from a stream separate from the component stream. Required detection/descriptive seed-mean intervals are output, with per-comparator floor prints. Per-candidate intervals are not mislabeled as full unpaired intervals. The independent nonconstant seed/component oracle agrees. Fixed challenger order and inclusive/strict margins are preserved.

## Validation and exact reviewed bytes

Independently executed all **38 author tests: 19 selector + 10 decoder + 9 integration; all passed**. Integration took 10.674 s. Added only `experiments/reviews/probe_next_native_opencode_20261114.py`: one independent bootstrap oracle passed, two F1 reproductions expected-failed (2.447 s). The author integration fixtures generate full manifest populations but use 12 component draws for speed; the independent numerical oracle uses 2,000. Synthetic git/constant substitutions do not validate a real clean-checkout admission.

Commands from `/home/narolski/smad-next`, with `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2`, interpreter `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`:

```text
src/NEXT/tests/mock_selection.py
src/NEXT/tests/mock_native_adapters.py
src/NEXT/tests/mock_native_integration.py
experiments/reviews/probe_next_native_opencode_20261114.py
```

`git diff --check` passed. Rule hash equals the file at binding commit `dbeb940`.

```text
5188ad9a696d86c935191a4fd45bee0f0762186c199a5bbd7d8368e87bf62667  experiments/NEXT_method-selection-rule/prereg_draft_v3.md
5b8f47d5a92858ad1250fc2e213a7ded6f57e6b3165420b2a747346ca5ef55e3  experiments/NEXT_method-selection-rule/OPENCODE_ADAPTER_HANDOFF_20261114.md
2347e31412ec10795a4b34eaecdb9d27a3a0d736fd7e1673ff03e687080fae2b  src/NEXT/read_selection.py
ebb40edda27a08034a6087a737109509e65c3c5ad76c748767cd19a49f2ff17c  src/NEXT/native_adapters.py
c99dd9c03917969fd11d09a579314f8ad782117dfe0c7c90b14dd7a7d591f37e  src/NEXT/tests/mock_selection.py
4381a8798de8392ca94494844ca0942547b7a3506c4bfc54580bf50d233672ac  src/NEXT/tests/mock_native_adapters.py
9c033a5c1e60f8bd4dd06285d2cd3aa9617284f09f95c261dbcaba363a04347d  src/NEXT/tests/mock_native_integration.py
6126929ae6a9187057a4dede074215448a773e9cfdfeef6ddb1387734760da75  experiments/reviews/probe_next_native_opencode_20261114.py
```

Static source checks included SbFM's registration/runner/supplement producer, E3 registration including amendments 2, 4 and 7c/7d, `run_lr.sh`, `freeze_mode_L.py`, W2 producer and `bb2_gate.py`, alongside the exact reader/decoder/test sources. No production scores/archives, sealed inputs or cluster were accessed; no commit or production journal was made. Only this new review and its independent probe were written.

## Remaining external admission blockers

After F1 is corrected and independently rechecked, release still requires: actual clean committed pin closure and exact independent admission GO; authoritative eight-arm dispositions and closed eligible batch; source/job/producer and cutoff receipts for every fit/supplement; actual five-seed E3 mode evidence; actual pinned SbFM training-specific transfer artifact and its provenance; all prescribed support/floor pins fixed before payload opening. GX's missing registered fit schema/manifests/floors/support route cannot be disguised as an excluded contender. Sbc crop scope and SbMR512 kernel registration remain separate requirements. Native fresh confirmation 413–417 still needs registered producers, source pins/receipts and reviewed comparator mapping. A later independent outcome review remains necessary. This file provides no `NEXT_ADMISSION_GO` authorization.

---

## Independent F1 recheck — 14 November 2026

**F1 RESOLVED. GO-for-commit of the native-selection implementation increment at the exact hashes below. No production admission or scientific read is released.** This verdict supersedes the initial changes-required verdict for these corrected bytes; the initial finding and its evidence remain above.

Independently inspected the correction and appended author handoff. Verified the narrow reader delta mechanically: restoring the removed preflight refusal and old execution refusal/interval condition **in memory only** reproduces the original reviewed reader SHA256 `2347e31412ec10795a4b34eaecdb9d27a3a0d736fd7e1673ff03e687080fae2b`. Thus no other reader behavior changed in this correction. Decoder and other author-test hashes remain identical to the initial review; approved rule bytes remain unchanged.

### Acceptance findings

1. Explicitly missing candidate fits now pass opaque preflight with four survivors. Execution emits the detection and descriptive intervals with four observed candidate arrays against the same five comparator arrays. The unchanged helper draws `len(candidate)` candidate indices and independently `len(comparator)` comparator indices per shared component replicate: **four draws from four observed candidate fits, five from the fixed five comparators**. No fifth candidate value is imputed. Both independent and author nonconstant numerical oracles agree over 2,000 replicates.
2. Planned denominator stays **five**, the failed fifth seed remains recorded as failing every seed-count criterion, and all four surviving seeds must pass a four-of-five bar. The acceptance tests verify the mean gain, all eight contrast intervals, the ladder interval alias, 4×12 versus 5×12 orchestration arrays, and criterion (f) failing when one survivor fails its guard.
3. The real `run_admitted` orchestrator is tested with a generated fixture and temporary journal: candidate failure **after the durable intent** now yields a valid four-survivor result and COMPLETE receipt. The five-survivor path still succeeds. Replay is refused on both paths before payload dispatch.
4. With a second candidate unavailable, three read seeds remain the registered not-read outcome and no deciding seed-mean intervals are emitted. The selector's general fewer-than-four branch is unchanged.
5. Missing comparator remains a preflight refusal; an exact-gate-failed comparator remains a runtime global refusal. The post-claim comparator-failure orchestration test retains FAILED.json, writes no result, and refuses replay. No reduced-comparator fallback was introduced.

Removed both `expectedFailure` decorators from the reviewer-owned probe and updated its description. **All 42 tests passed independently: 19 selector, 10 decoder, 10 integration, 3 reviewer probes**, with no expected failures or unexpected successes. Integration: 11.765 s; reviewer probes: 2.473 s. Used the same four thread limits and isolated interpreter documented above, with `nice -n 10`. `git diff --check` passed.

### Exact rechecked hashes

```text
f20f42578275aa3d92b8c695ab86827a526b7f62016b98ec242bf17c0b390830  src/NEXT/read_selection.py
ebb40edda27a08034a6087a737109509e65c3c5ad76c748767cd19a49f2ff17c  src/NEXT/native_adapters.py
c99dd9c03917969fd11d09a579314f8ad782117dfe0c7c90b14dd7a7d591f37e  src/NEXT/tests/mock_selection.py
4381a8798de8392ca94494844ca0942547b7a3506c4bfc54580bf50d233672ac  src/NEXT/tests/mock_native_adapters.py
5dc13bc1f19557c4b45ef5df23a94a66162a9f6d0ba1785c3d6536934e434e90  src/NEXT/tests/mock_native_integration.py
b7469879051f37a370a3b589e431cb88518b53801062de3b2ec395599edb4f75  experiments/reviews/probe_next_native_opencode_20261114.py
5188ad9a696d86c935191a4fd45bee0f0762186c199a5bbd7d8368e87bf62667  experiments/NEXT_method-selection-rule/prereg_draft_v3.md
6c5ab9eedbd773d78a64945de02399fff7b996fabe580d935627d4ce66a657c6  experiments/NEXT_method-selection-rule/OPENCODE_ADAPTER_HANDOFF_20261114.md
```

All external admission/registration blockers listed above remain in force, including exact clean committed admission and receipts, authoritative eight-arm dispositions, training-specific floors, actual E3 freeze evidence, GX support, crop/kernel scope and fresh-confirmation registration. This is software GO-for-commit only, not an admission GO. The recheck changed only this review and its probe; no real candidate payload, registration, cluster, commit or production journal was accessed or changed.
