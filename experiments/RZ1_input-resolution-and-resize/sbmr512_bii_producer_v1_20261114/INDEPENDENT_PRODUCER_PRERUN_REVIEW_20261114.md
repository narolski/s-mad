# Independent SbMR512 B(ii) producer review — 2026-11-14

Reviewer astra_sprint_plan_review, other than author Sol. Source, registered input metadata and generated CPU fixtures only. No archive/header/member, weights, images, NPZ, model, CUDA, scheduler or scientific reader accessed.

## Decision

GO_BOUNDED_SOURCE_AND_FIRST_BATCH_TIMING_PREPARATION_ONLY.
HOLD_ACTUAL_RECONSTRUCTION_TIMING_AND_FULL_PRODUCTION until exact staged inputs/runtime, reconstruction permission, launcher and fresh root release are independently admitted. This review does not authorize backend imports, model construction, NPZ deserialization or scientific interpretation.

A prospectively specified, falsifiable native-bytegate reconstruction is a legitimate experiment. It does not require a theorem of equivalence for every hidden historical cache. First original eval batch0 has no earlier train/MEDS forward predecessor; its fixed seed408/64 rows/native+flip128-forward-sample timing test can therefore be separately authorized once its actual sources/runtime/inputs are bound. A pass certifies only that fixed batch's selected native float32 bytes and technical execution. It cannot certify TT1 history, every input, all perturbations, full runtime or all-state equivalence.

Full B(ii) retains conditional status: omitted train between eval and TT1, and omitted MEDS before original cross execution, change history. The native gate over ALL13771 targets must pass before any perturbation; failure is terminal HOLD without retry, A/cross-only fallback, state reset, altered schedule or relaxed tolerance. Root must prospectively adopt that bounded conditional interpretation, not assert unproved historical equivalence. The current admission boolean omitted_train_meds_without_replay_reviewed must mean this explicit limited policy decision, not fabricated empirical evidence; timing needs no full-TT1 historical equivalence claim.

## Independently checked implementation

All source/package manifest entries and all12 upstream SOURCE_PINS match. Seven author CPU tests independently PASS in0.064s. They exercise reversed target-map order, cross output order, batch boundaries63/64, last partial batches, duplicate/missing/path/offset rejection, mutation rejection, failed native gate before spec2, actual registered13771-row mapping, expected sample/call counts and unsigned-release refusal. AST parses all source. These are toy/source tests, not a reconstruction result.

engine.mapping writes by exact cross_ids index, not target_mapping enumeration. Every target must occur once; context ID/path/label/batch/offset must match. Full run retains all14 fixed specs, eval24859 then TT134411, batch64, final27/43. eval native l0.cpu().tolist precedes flip and TTA host transfer; TT1 native only. Compared directly with pinned rz1_score.py9b678429... source. Full intended counts remain5,889,030 image-forward samples,92,120 batched calls and963,970 sealed cross values across five seeds. Noncross lists are transient and no scientific aggregate is exported.

Model is eval/no_grad; exact overlay keyset/schema/finite checks and missing=frozen state keys are explicit. Population-level registered state digests detect state_dict mutations, not hidden Python/kernel caches. The five312981-byte overlays are not full original last.pt checkpoints. Backend construction depends on independently pinned frozen pretrained content, buffers, timm positional rebuild and normalization/source. One rebuilt model is retained across specs, with no reseed/reset fallback.

authorize precedes exclusive output/CLAIM creation; CLAIM precedes actual content hashing, model imports, checkpoint/image/reference decoding. Source hashes, exact seed, fixed output, admission hash, independent review hash and technical attachment hash are checked. Native mismatch creates FAILED and cannot create scientific success. Full output is14×13771 float32 sealed logits, not kappa/performance. The attachment adapter is source-only association checking; it is not permission to decode values. Python assertions require an unoptimized interpreter: future launcher must reject -O/PYTHONOPTIMIZE and sanitize import paths/environment. Current package deliberately lacks a reviewed live launcher/durability/resource release.

## Concrete issues for the next source/release step

1. Reference loading is unnecessarily broad and expensive. Backend._references loops over BOTH eval and TT1 even in timing mode with eval-only requested IDs. Each repeated z["logit"] access inside the selected-ID loop materializes/decompresses the NPZ array again. This is not a new statistic, but it is real deserialization work and can dominate full-run time. Recommended bounded author revision: skip a population with no requested IDs, load its authorized id/logit/manifest arrays once, validate once, select requested values and release arrays. Do not edit this frozen version in place; re-pin and independently delta-review any correction. Under unchanged v1, a timing release must explicitly authorize BOTH reference containers' metadata/logit-array deserialization, even though only fixed eval-target values are inspected; an eval-only permission would not cover this code. Prefer narrowing code, not widening permission silently. Full-production timing estimates must include the current repeated decode cost or use a reviewed revision.
2. TIMING_REBUILD.elapsed_seconds starts AFTER Backend construction, and includes worker startup, state hashing, reference loading and comparison. It is neither total cold reconstruction wall time nor isolated GPU forward time. Wrapper must record total process/setup/collection durations; label this interval precisely. CUDA peak memory is process peak including construction, not necessarily batch-only peak. Two calls/128 samples are hardcoded after successful path; useful generated backend count tests can strengthen verification.
3. Seven tests do not comprehensively exercise a minimally valid release with each individual admission field corrupted, every content pin missing, import-shadowing, or abrupt-worker durability. Add generated release/schema and launcher fixtures before actual execution approval. Ensure required paths (meta, references, complete applicable images, frozen weights, dependency source/native libraries) are obligatorily present in actual_content_pins; an arbitrary empty map must not be treated as provenance. Existing flags alone do not establish those facts.
4. Full mode's all13771 native gate is stronger than first-batch timing. Do not reuse a timing receipt as full native pass. Root may authorize the later full native phase conditionally under a new release; no perturbation before its full native gate. Complete five-seed denominator and all failures remain.

## Minimal next CPU runtime/source metadata probe contract (not executed)

Freeze a new create-only probe receipt tied to exact interpreter path and interpreter SHA. Use standard-library sys/sysconfig/importlib.metadata to record Python version, executable/prefix, distribution versions and locations/RECORD hashes for torch, torchvision, timm, numpy, Pillow, opencv, transformers/huggingface dependencies actually imported by common/archs. Hash the exact model-wrapper, timm factory/vision-transformer/positional-resize/attention/layer sources, preprocessing and relevant installed native library files. Read source/installation metadata only: no torch/timm/model import, CUDA API/driver query, downloads, model cache content, weights, data or NPZ.

This closes *current mutable-venv identity* only. It cannot reconstruct historical executed package identity from today's installation. Compare it to preserved admitted runtime/build receipts; explicitly retain UNKNOWN historical fields. Root can adopt the current frozen reconstruction environment as a prospective test subject with terminal exact-byte rejection rather than pretend it is proved historical identity. Actual backend defaults need a separately admitted bounded runtime probe or exact reviewed runtime receipt; metadata-only inspection cannot empirically attest cudnn/default precision flags. Actual backend construction checks torch2.11.0+cu128/CUDA12.8/H100, reviewed defaults, explicit TF32true and positional rebuild; complete timm/source/native dependencies must be bound, not inferred from torch alone.

Then separately authorize exact overlay schema/baseweight/image provenance staging and the narrowly scoped reference exception, inspect and bind those receipts, review a sanitized bounded worker with early native ID/create-only claim/durable failure retention, and issue a new root timing release. No automatic full release follows timing. Source publication, all scientific reads and existing NEXT once remain HOLD.

## Exact pins and verification

Source SHA256SUMS7d22f492d102daebfea395b383055aa305668c09100a0c99531e66bc180c5990.
Evidence PACKAGE_SHA256SUMS35d1131322766613ffa97baaa6b12b6b67c864f955bddc4edfbfb379adf42026.
Prereg18e3f5ebf0df618bbd9c12ab61bc2417fa1175f83bc5a7402112bd7bc92f6503.
Handoff1a79bfd5296a4cd191af294d955ed71e9a4174ba820934fbd9e20da8ca6ffc92.
Independent source checks748ab546969d81ae336017670b9826152b58cfc482770f90fbc514bfffd23d8b.
Independent upstream pin checks b3aad0ae690d592e875a19002f10ed665fb3cd59a315b18c071bc5ea9872eccb (same JSON bytes as source pin list, independently rehashed).
Exact context04b8580bd16629c3c58bc5351c9d8b1809b92c903f41285cda87a3bfb7b6a5bc; cross input41f693ddabd1134fcae04c89c8d934f77793b2dd74780798c066cffed6ccecc2.
Prior actual opaque technical attachment review495f24ddccbb5b69383a9790ea7dc2c175f5ba72ee11a0d67db605ee0afd5b16; handoff0e05feb84065b069db1e1ae708a644f880d3e5a855f7bfd9fb9bbc0c3f6cd836. These prove recorded opaque provenance, not decoded reconstruction.

No author/canonical/v1/v2 source changed and no execution/read release issued.

## Final narrow disposition after root scope clarification

HOLD_UNCHANGED_V1_TIMING_OR_FULL_EXECUTION: require the narrow separately pinned v1r1 reference-loader correction before executable admission. The repeated logit array accesses scale as selected-ID count times full-container array size (quadratic when both grow together); this is confirmed by source control flow and normal NPZ indexing semantics, not by opening any actual container. Timing currently opens TT1 despite zero TT1 targets. Cache each required container once, skip nonrequested populations before opening, and add generated counters proving at most one logit-array fetch per needed container and zero TT1 opens for eval-only timing. Author was notified directly; reviewer did not edit code.

Full-container deserialization for compressed reference validation/comparison still needs explicit future ROOT permission even after that optimization. Only fixed timing-batch selected targets may enter comparison; no nonselected statistics/score export. This is a narrow code/scope fix, not a requirement to prove all hidden cache states. GO for source/timing preparation remains; actual reconstruction and full production remain HOLD.
