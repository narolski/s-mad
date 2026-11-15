# NEXT native-adapter implementation handoff — 14 November 2026

**Status: review-ready implementation increment; full adapter integration remains incomplete. No scientific release.**
Author: bounded OpenCode implementation worker taking over the imported Boole task. This is an author receipt, not an independent approval. Bound selection rule v3 (`dbeb940`) remains authoritative.

## Exact files owned and changed

1. `src/NEXT/native_adapters.py` — new, library-only native decoders.
2. `src/NEXT/tests/mock_native_adapters.py` — new synthetic tests.
3. `src/NEXT/read_selection.py` — prior-selection validation for confirmation; no new production dispatch.
4. `experiments/NEXT_method-selection-rule/OPENCODE_ADAPTER_HANDOFF_20261114.md` — this receipt.

The pre-existing dirty files recorded at entry were preserved. No commits, cluster commands, real candidate archives/scores, sealed inputs, production reader invocation, production once markers, or scientific conclusions were produced. Existing tests use disposable synthetic archives and a disposable test journal only.

## Implemented

### Native fit payloads

`load_fit` decodes the established AB1 A/Sb, SbFM and BB2L E3 A/Sb selection formats. It checks source name/arm/seed, H100, package/overlay/recipe tokens, unrestricted 6,250-step scoring, task identity, metadata, finite logged losses, evaluation manifest hash and complete ID order, and unique training paths/kinds/labels and finite vector shape. E3 requires its fixed learning rate and an explicit admitted batch setting from the registered 256/1 or 128/2 possibilities. It returns training arrays for subsequent registered fit-gate evaluation; it does **not** manufacture an own-registration pass.

### Second-engine supplemental payloads

`load_sbfm_supplement` reads the actual `AB1FMSUPP-v1` final archive layout (`./` members), binds the submitted config bytes and pre-read receipt hash, locates the exact source model, requires its final technical record and complete family hashes, then verifies the whole-fit-manifest bit-identity gate **before decoding any score NPZ**. It accepts only exact source archive hash/name, manifest, row count, H100 and zero differences with own-rule agreement 1. Both TT1 and MEDS require exact ordered IDs, seed, floating finite one-dimensional logits. Missing final status rejects diagnostic partials. Another model's failure does not erase a successful model or make a failed model eligible.

### DINOv3 wave-2 payloads

`load_dinov3_w2` follows amendments 7c/7d: unique task membership, fixed scorer hashes, GPU, recorded nonnegative failure/refusal counters, and the per-model full-manifest exact gate before any family NPZ. It supports E3 candidate/control and the AB1 Sb comparator. It decodes only MS1 storage, TT1 and MEDS families required by NEXT; counters are retained rather than turning a job-wide nonzero exit into a fabricated failure of every seed. Border-path identity includes the supplemental archive hash, preventing accidental equivalence between distinct scoring artifacts.

All decoders hash the same open descriptor used to read the tar, never extract files or load weights, reject normalized member aliases/traversal, and use `allow_pickle=False`. Expected manifests/config/source identities are explicit caller inputs that must be pinned and independently admitted. This library alone provides no admission boundary or scientific verdict.

### Confirmation

`validate_confirmation_selection`, called by production preflight for the confirmation stage, now checks prior result schema, selection stage, identical rule hash, all eight dispositions, the named winner, and agreement of that winner with the fixed-order criteria. A label-only or internally contradictory prior result is refused. This is confirmation binding support, **not** fresh-source adapter approval.

## Tests and review-ready receipt

Executed from `/home/narolski/smad-next`, using only generated fixtures:

```sh
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/NEXT/tests/mock_native_adapters.py
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 /home/narolski/mambamorph-code/.venv-spark/bin/python -I src/NEXT/tests/mock_selection.py
```

Results: **10 new tests passed; 19 existing tests passed.** `git diff --check` passed. New tests exercise real generated tar/NPZ layouts, both SbFM supplement sources, E3 candidate/control and AB1 comparator, unrelated model failures, full gate identity mutations, a nonzero difference of 1e-12 (no tolerance fallback), proof of no NPZ decode before a failed gate, partial/config/receipt/family corruption, wrong score order/duplicates/shape/non-finite/object dtype/seed, normalized tar aliases and traversal, digest changes, native fit/training row corruption, unsupported GX/fresh sources, and confirmation fixed-order contradictions.

Code/test SHA256 at handoff:

```text
b04874a950a1d89592ff0e8cc6ee67c5985d6597040682800e9e242367717727  src/NEXT/native_adapters.py
7241211ad84fe2f67cc4ac287847e36aafae4edecbefd02b620f8b6e5724ca25  src/NEXT/read_selection.py
4381a8798de8392ca94494844ca0942547b7a3506c4bfc54580bf50d233672ac  src/NEXT/tests/mock_native_adapters.py
```

These hashes supersede neither the previous independent review nor its release conditions. The changed reader and new code require a new independent review.

## Remaining implementation work — not scientific exclusions

The new library is deliberately **not yet wired into `preflight` or `execute`**. The existing global refusal for otherwise eligible SbFM/GX/DINOv3 therefore remains. The task's full native-selection goal is not claimed complete. A code gap cannot exclude an arm, justify default Sb, or be described as an infrastructure failure.

To complete integration:

1. Extend admission to bind and receipt-check **both fit and supplemental artifacts**, exact source identities, submitted config, complete native manifest orders, and the new module itself. Add that module to mandatory code pins. Preserve opaque preflight and once-before-member-access ordering. Selection source pins must bind the original AB1 comparators, not arbitrary admitted names.
2. Assemble normalized network inputs with border rows taken from the same exact-gated supplemental path for both compared networks. Bind MS1 storage additions for E3. Do not use SbFM's original fit border rows against rescored comparator borders merely because the IDs agree.
3. Bind the training-list-specific SbFM/GX transfer rows; the current `prepare_contrasts`/`execute` paths still assume Sb. Add registered native training/fit/other guards rather than equating decoder success with criterion (f). Preserve the SbFM FaceMorpher "seen engine" disclosure.
4. Implement DINOv3's full unpaired numerical route: candidate 403–407 minus AB1 comparator 408–412 seed mean, separate comparator availability and failures, shared component draws with independent seed resampling, appropriate floor/descriptive intervals, E3 splice-fit gate (AUC ≥0.80 on unique lad_S4 vs lad_S3), and its frozen seed-mode evidence. The existing unpaired bootstrap helper is not a substitute for this integration. Current `execute` remains RZ-specific (paired roles and refit yardstick).
5. Add end-to-end synthetic admission/normalized-output/decision tests for these integrated routes. Existing decoder tests cannot establish a complete scientific invocation.

## Requirements that cannot be invented

- **GX:** `experiments/GX1_gan-morphs-in-training/READINESS_20261114.md` documents no admitted training manifest, registered/pinned amendment-2 runner/output schema, pre-fit floor, or complete TT1/MEDS/border route. The draft `src/GX1/gx1_admission.py` is unrelated dirty work and was not changed. Generation metadata is insufficient to define a fit decoder. No speculative GX schema was added.
- **Fresh confirmation:** current AB1/SbFM/E3 runners/source-pin lists cover selection seeds only; the existing RZ refit adapter hard-pins original AB1 408–412 sources. Need the committed independently reviewed fresh 413–417 fit/scoring registration, exact source pins/receipts, and arm-specific provenance extension. An admission-supplied hash alone must not silently replace the original comparator pins. DINOv3 fresh comparison semantics must remain consistent with v3's unpaired rule and its same-fresh-seed instruction; obtain a reviewed operational mapping before wiring it.
- **SbMR512 and Sbc:** existing kernel-test registration and author crop-scope blockers remain separate from this work.
- **Release:** exact committed clean-tree admission, complete authoritative eight-arm dispositions, arrival/hash cutoff evidence, all support/floor pins and independent review remain required. No admission JSON or GO line was created.

## Static sources used

Both requested continuation briefs, current notebook/status/delivery/workflow records, approved v3, `READER_20261114.md`, `PRERUN_NEXT_READER_20261114.md`, existing reader/tests, AB1 `prereg_fm.md`, `run_fm.sh`, `ab1_read.py`, `ab1fm_read.py`, the committed SbFM supplement runner/config/validator, BB2 `prereg.md` amendments 7–7d, `bb2_gate.py`, `bb2l_w2.sbatch`, `run_lr.sh`, `bb2l_fit.sbatch`, `bb2l_read.py`, `freeze_mode_L.py`, PN1 native scorer/rescorer, and GX readiness. No candidate result file was used to infer a format.

---

## Continuation increment — 14 November 2026, after MAIN's integration instruction

**Supersedes the earlier implementation-gap list and code hashes above. Stable for independent review; author receipt only, not approval.**

### Integration completed for the defined selection routes

The production entry point now admits and dispatches the registered **SbFM paired route** and **DINOv3 five-candidate/five-comparator route**. These no longer have a blanket unsupported-adapter refusal. GX and fresh native confirmation remain explicitly refused. No real admission or scientific invocation was created or run.

1. **Opaque admission and exact provenance.** `native_preflight` binds the decoder module, every used source fit, supplemental archive, source inventory, manifests, training-list references, producer code, submitted SbFM config, E3 frozen seed mode, role/seed mappings, eligibility review, and arrival/hash receipts. Both fit and supplemental binary hashes are verified without opening tar members. AB1 Sb hashes remain hard-pinned to the original 408–412 sources; SbFM sources must also match the fixed submitted config; E3 sources must match the committed five-seed freeze. The SbFM config and both supplemental producers have fixed registered hashes. Native module bytes are checked again before dispatch. Receipt identity/digest changes abort the invocation, rather than losing a seed and permitting default Sb.
2. **Normalized native dispatch.** `native_network` validates full fit manifests and unique training rows, then loads the admitted exact-gated supplement. Both compared networks receive border rows from the same supplemental archive (path identity includes its digest). E3 storage rows come from the W2 MS1 family, for both candidate and comparator; no mean-logit network is formed. The E3 plain control consumes only its required MS1 supplemental family, not TT1/MEDS: unrelated missing control families do not create an extra selection gate. Its fit and full-manifest exact gate are still required. The B fit is read for registered fit/read-seed guards, without unnecessary rescoring.
3. **Training-list-specific transfer prints.** All supplied transfer files receive exact per-set row, label, component and finite-score checks. SbFM candidate floors use `train_SbFM` references; comparators use `train_Sb`. The existing RZ/E3 use of `train_Sb` is retained. FaceMorpher descriptive rows for SbFM carry the required **seen engine** label.
4. **Registered criterion (f).** SbFM's H-fm3 original-engine guard uses the exact 191 test R4 + 191 test R2w OpenCV rows, same-seed comparator, inclusive −0.02 margin and comparator <0.98 testability ceiling. E3 requires finite A/B/Sb fits, their three-arm training adequacy (≥0.75 over unique training rows), and Sb's splice-fit AUC ≥0.80 on unique lad_S4 versus lad_S3 rows. These are computed from validated native training arrays. E3 storage applies the separate registered X/A adequacy gate; B adequacy is not silently added to the storage criterion. No decoder success alone substitutes for these guards.
5. **DINOv3 statistics.** Every candidate scalar is compared with the mean of the five original AB1 comparator statistics. Per-comparator floor prints remain separate. The seeds×components bootstrap independently resamples candidate/comparator seeds on the same component draws, for seed-mean intervals on all detection and descriptive contrasts. Per-candidate gain CIs are not mislabeled as full unpaired intervals; the output points to the arm seed-mean interval. Floor intervals remain per-network component intervals, as required by the four-of-five floor wording. Fixed challenger order and inclusive margins remain unchanged.
6. **Actual orchestration tested.** `run_admitted` contains the existing production preflight/prepare/claim/execute/result-or-failure sequence; CLI `main` calls it with the unchanged production defaults. Tests exercise this same function with generated data, a synthetic git control plane and a separate temporary journal root. Preflight creates no journal and permits no tar member access; payload dispatch asserts the durable intent already exists. Both successful and failed attempts refuse replay. Private synthetic MEDS row identifiers do not enter the serialized result.

### Native admission extension (metadata contract, not an admission)

The original `next-admission-v1` top-level requirements and independently pinned exact GO review still apply. For a read native arm, add:

- `native_source_inventory`: committed pinned JSON mapping exact fit prefix (without `.tar`) to SHA256. This authenticates each source alongside the hard original Sb pins, SbFM submitted-config pins and E3 frozen-mode pins. Independent review must establish source/producer/job provenance from authoritative receipts; matching JSON alone does not prove a scheduler history.
- `native_manifests`: mapping of names to `{path, sha256}`. Required common names: `ab1_eval`, `train_A`, `train_Sb`, `tt1`, `meds`; SbFM also needs `fm_eval`, `train_SbFM`; E3 also needs `fs_eval`, `train_B`, `ms1`. Paths are resolved against the repository (absolute pinned paths also work). Fixed original evaluation/A/Sb/SbFM hashes are enforced; TT1/MEDS must match the common support hashes. Family population/order is checked (TT1 30,994, MEDS 1,018, MS1 1,480). These are full original manifests, not candidate-dependent subsets. All files must be in the committed pre-read pin closure.
- `transfer_files.SbFM` when SbFM is read, in addition to `Sb`; `transfer_training_sha256` maps each required training-list tag to its exact native training-manifest hash. Final independent review must verify the transfer artifact's actual training provenance, not merely its field names.
- `dinov3_seed_mode` when E3 is read: committed pinned frozen-mode JSON with `mode: five`, seeds 403–407 and the exact source `tars` map. No three-seed mode is silently expanded to five.
- `networks[key]` for native fits: existing `archive`, `sha256`, `arm`, integer `seed`, plus `format: native_fit`, exact `prefix`; E3 also requires `batch_spec: [256, 1]`, its registered E3 configuration. The lower-level decoder's general 128/2 schema support does not make that setting eligible for this E3 route.
- `supplements[key]`: `{archive, sha256, format, producer_sha256}`. Format is `sbfm_supplement` or `dinov3_w2`. SbFM additionally carries `config: src/recovery_20261114/sbfm_supplement/config.json` and its fixed `config_sha256`. The corresponding registered producer file must be pinned. Supplemental keys must not collide with source network keys.
- The original receipt map also contains every used supplemental key, with its exact archive/path/hash/time, `hash_verified: true` and matching `producer_sha256`. Selection's archive/hash cutoff applies to every required fit and supplement. The registered producer identity must be substantiated in independent admission review.
- SbFM arm: seeds 408–412; `candidate` = same-seed AB1FM SbFM, `comparator` = original same-seed AB1 Sb, `control` = same-seed AB1 A; `supplement` selects the single common SbFM supplement. Each role lists all five seed keys, using null only for a registered missing seed. No RZ yardstick role is used.
- DINOv3 arm: seeds 403–407; `candidate` = BB2L Sb, `control` = BB2L A, `fit_guard` = BB2L B at those seeds; `comparator` maps 408–412 to the original five AB1 Sb fits; `supplement` selects the single W2 archive. No same-seed pairing or RZ yardstick is fabricated.

Preflight requires the new module itself in the pin closure. It does not import candidate readers or inspect candidate members. All authoritative dispositions for the other arms remain required.

### Residual blockers, separated by cause

**Unresolved v3 edge-case semantics — explicit global refusal, not scientific loss:**

- **Missing/failed AB1 comparator in the DINOv3 route.** V3 defines each contrast against the comparator's five-seed mean and resamples five comparator seeds. No reduced-comparator mean, seed imputation or favorable subset is specified. A null comparator is refused during preflight; a comparator whose native gate/schema fails stops the scientific invocation after its journal claim. A reviewed rule interpretation is needed before implementing a different missing-comparator treatment.
- **Exactly four usable DINOv3 candidate seeds.** V3 permits four read seeds for counts but explicitly specifies resampling five DINOv3 seeds for intervals. The complete five-seed numerical route is implemented. With exactly four usable candidate seeds, the reader refuses globally rather than invent a four-seed bootstrap, resample five observations from four fits, impute the missing seed, or omit the required interval. If explicit missing fits already leave four complete A/B/Sb triples, preflight refuses before any journal or member access. If the fourth-only state is revealed by a native fit/gate failure during execution, the failed journal is retained. Three or fewer usable candidates retain the explicit registered not-read outcome. This bounded refusal is documented for reviewer adjudication, not a proposed change to v3.

**Missing external registrations/artifacts:**

- GX still lacks its admitted training manifests/output schema, amendment-2 runner, floors and complete scored support route. It remains an unsupported eligible-arm blocker; it cannot be discarded because this code cannot decode it.
- Native confirmation 413–417 still needs its registered producers, source pins/receipts and reviewed comparator mapping. Original selection-source pins are not relaxed. RZ's existing fresh-source guard remains in force.
- E3 needs an actual independently admitted five-seed freeze; a three-seed freeze does not supply the defined v3 route. SbFM needs the actual pinned per-row training-list transfer artifact. No existence/completion of either is asserted by these synthetic tests.
- Sbc author crop scope, SbMR512 kernel registration, closed eligible batch, final clean committed pin closure, exact admission/receipts, and independent review remain release requirements.

**Implementation gaps from the first increment:** admission/dispatch, native normalization, per-training-list transfer handling, registered native guards, the complete five-by-five E3 numerical route and full orchestration tests are now closed for the stated formats. The residual edge cases above are blocked pending an authoritative interpretation/registration, not silently converted into a default decision. A reviewer may require corrections; this author receipt does not approve the implementation.

### Tests and stable code receipt

**38 synthetic tests pass:** 19 existing selector tests, 10 native decoder tests, 9 new integration tests. The integration suite covers generated full-size native manifest layouts, candidate/control/comparator/B fit paths, submitted-config/source/producer/arrival/module pins, same supplemental border replacement, distinct SbFM transfer floors, AUC-of-each-network means (a deliberate fixture would give the wrong answer under mean logits), fixed-order choice, original-engine/adequacy/splice gates including exact thresholds, missing-seed dispositions, unresolved-bootstrap refusal, comparator gate abort, opaque preflight, actual once-before-member access, success/FAILED receipts and replay refusal. Only immutable production constants and git control-plane state are replaced by synthetic equivalents; the native archive loaders, manifest/row validation, statistics, orchestration and decisions run normally.

Commands (from the repository, using the same four thread limits as the first receipt):

```sh
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/NEXT/tests/mock_selection.py
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/NEXT/tests/mock_native_adapters.py
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/NEXT/tests/mock_native_integration.py
```

`git diff --check` passed. Last integration run: 9 tests, 10.721 seconds, OK. Earlier decoder and selector suites passed; after the final storage-adequacy and known-four-seed preflight corrections the integration suite was rerun, including its distinct B-versus-X/A guard assertion and post-claim failure/replay test.

Current exact source hashes:

```text
2347e31412ec10795a4b34eaecdb9d27a3a0d736fd7e1673ff03e687080fae2b  src/NEXT/read_selection.py
ebb40edda27a08034a6087a737109509e65c3c5ad76c748767cd19a49f2ff17c  src/NEXT/native_adapters.py
c99dd9c03917969fd11d09a579314f8ad782117dfe0c7c90b14dd7a7d591f37e  src/NEXT/tests/mock_selection.py
4381a8798de8392ca94494844ca0942547b7a3506c4bfc54580bf50d233672ac  src/NEXT/tests/mock_native_adapters.py
9c033a5c1e60f8bd4dd06285d2cd3aa9617284f09f95c261dbcaba363a04347d  src/NEXT/tests/mock_native_integration.py
```

Registered static producer/config hashes additionally checked during implementation (metadata/source files only):

```text
b44834782a552ab87c66518fa90563ce804963f763b2c54d0b6642d3120db507  src/BB2/wcss/bb2l_w2.sbatch
4ec95da9ac37d3f958124b5d5cb72a812497601b3acaad4d264bc00e41294ddf  src/recovery_20261114/sbfm_supplement/config.json
2dd5535b64901691176f0268130fecc48f34145709d7081bde8f9f9cbb41474b  src/recovery_20261114/sbfm_supplement/run_supplement.py
916bef3b0f62054c9d2281915d4a3146753c0438b6a4ee6b26435ce0b9bf50f5  src/BB2/run_lr.sh
48fe853c13d7ab77ed362300c3984c7640f9dfcae1ff9237457015268d927bf4  src/AB1/run_fm.sh
```

Files owned across both increments are now the five source/test files above and this handoff. This continuation changes the reader, native decoder, existing mock selector test (unsupported-arm fixture now correctly uses GX), adds the integration test file, and appends this receipt. `mock_native_adapters.py` is unchanged from the first increment. Unrelated work, including concurrent lead/worker changes, was not overwritten, staged or committed. No cluster calls, real candidate payload/score access, sealed inputs, real scientific invocation or production once markers occurred.

---

## F1 correction receipt — 14 November 2026

**Author response to `experiments/reviews/PRERUN_NEXT_NATIVE_OPENCODE_20261114.md`; pending independent recheck.** The initial review and all earlier author receipt text are preserved. This section supersedes the earlier claim that four usable DINOv3 candidates require a new rule interpretation. As the independent review establishes, v3 already defines the mean over read candidate seeds and permits four-of-four counts. The earlier global refusal was an implementation error.

### Narrow delta

Changed only `src/NEXT/read_selection.py`, `src/NEXT/tests/mock_native_integration.py`, and this appended receipt in this correction:

- Removed the exactly-four-candidate refusal from both preflight and execution.
- Required detection/descriptive seed-mean intervals now run with either four or five usable candidates. The existing bootstrap helper samples the observed candidate population with replacement, using four draws when four candidates are read, independently of five draws from the fixed comparator population, on the shared component replicate. The helper itself needed no change.
- Retained planned counting denominator five, the failed fifth seed record, and all-four passing requirements. No failure AUC is imputed. Three or fewer usable candidates remain not read and receive no deciding seed-mean intervals.
- Preserved the fixed-five-comparator preflight/runtime refusal and existing once-journal behavior.

### Meaningful synthetic acceptance checks

All **39 author tests passed**: 19 selector, 10 native decoder, 10 integration (the integration suite now includes an explicit 2,000-replicate four-by-five numerical oracle).

The revised integration acceptance test confirms opaque preflight admits an explicit missing candidate; the four-candidate result retains denominator five and the failed seed, computes the expected mean gain, emits all eight detection/descriptive intervals plus the ladder alias, and calls the bootstrap with exactly 4×12 candidate and 5×12 comparator component arrays. Failing one of the four survivors' registration gates makes the four-of-five criterion fail. Dropping a second candidate yields the registered three-read-seed not-read outcome with no deciding intervals.

The actual orchestrator test covers three paths: five-candidate success, a post-claim candidate failure producing a successful four-candidate result/COMPLETE receipt, and a post-claim fixed-comparator failure retaining FAILED.json with no result. Payload access still requires the prior durable intent, and every path refuses replay. The independent four-by-five oracle uses nonconstant seed effects and shared component variation and agrees to absolute tolerance 1e-14 with the implementation.

Commands used the same interpreter and four thread limits documented above:

```text
src/NEXT/tests/mock_selection.py                         19 passed
src/NEXT/tests/mock_native_adapters.py                   10 passed
src/NEXT/tests/mock_native_integration.py                10 passed (12.076 s)
experiments/reviews/probe_next_native_opencode_20261114.py
```

The **reviewer-owned probe was not edited**. Its numerical oracle passed; its two decorated F1 cases now report **unexpected success**, resulting in unittest exit status 1 (`FAILED (unexpected successes=2)`). This is the expected decorator behavior after correcting those defects, not a clean passing probe-suite status. The reviewer can remove its `expectedFailure` decorators during independent recheck. Positive author acceptance tests above cover both corrected cases without expected-failure decorators.

`git diff --check` passed. Current corrected source/test SHA256:

```text
f20f42578275aa3d92b8c695ab86827a526b7f62016b98ec242bf17c0b390830  src/NEXT/read_selection.py
5dc13bc1f19557c4b45ef5df23a94a66162a9f6d0ba1785c3d6536934e434e90  src/NEXT/tests/mock_native_integration.py
```

Preserved review/probe/rule fingerprints:

```text
53726f85b9cdc6460b08dbfc729bda227f2f8bc2c82bea4841fa5deb1a036cc9  experiments/reviews/PRERUN_NEXT_NATIVE_OPENCODE_20261114.md
6126929ae6a9187057a4dede074215448a773e9cfdfeef6ddb1387734760da75  experiments/reviews/probe_next_native_opencode_20261114.py
5188ad9a696d86c935191a4fd45bee0f0762186c199a5bbd7d8368e87bf62667  experiments/NEXT_method-selection-rule/prereg_draft_v3.md
```

The missing-fixed-comparator condition and external admission/registration blockers recorded by the independent review remain. The four-candidate software blocker is removed. No rule text, reviewer file, native decoder, other selector test, real outcome/archive, cluster state, commit or production journal was changed/accessed by this correction. This receipt is not an independent GO or scientific release.
