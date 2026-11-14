# Independent NEXT technical collector V2 implementation review — 2026-11-14

Reviewer: Astra / astra_sprint_plan_review, independent of collector author.

**HOLD_SOURCE_SEMANTICS_CORRECTION_REQUIRED.** No implementation GO line and no live technical collection authorization. One concrete native-versus-integrity classification defect must be corrected by the author in a newly frozen version/delta. This is source/synthetic review only; no actual archive/header/member/log/NPZ/checkpoint, native scientific reader, claim, GPU or cluster access occurred.

## Exact reviewed package

Collector c500e0922dde6c263eb07d271b97f9ff544096a544b3b4fbb217d0b0b8a691d6.
Predicates e120030bedd37f8f8c858fa6a7541f0502085ab31c59997ca1ce85e381e9dcaf.
PACKAGE_SHA256SUMS30930699637515aff40a11be41c75826ae9e19eb4fc2ee99beb525e61772d917.
TYPED_SCOPE1ccf3e92bcba38134ccdbf42ce4a041315e5f555e26d9561ad2c5eb3ed09bd15.
Root source-only adoption739bb565d51886a0c8e25ded9f42889e862a5a31b1c8f5a14638955c120c06a1; independent plan reviewa447905be5511887ad9b2fc455146a336bf855887cdc5bf7d1d5c52ef5b1e265; SOURCE_GRAMMAR_MAPf9832aec6e8d81af65fb07d7c5ef5c32ab5484a2d5de6e0a509719f573a9b0a8.
All13 package entries and all83 source/input pins independently rehashed PASS. Scope retains77 records=75networks+2supplements, denominator5, all15 missing BB2 submitted-batch proofs and exactly5 SbMR512 technical descriptors. Independent checks file SHA c2b5f2de4abc4377ff0b3040546a9729f455cb75a6d7aa7e17f0a1e2de72c5fb.

Independently executed only README safe synthetic commands:23 unit tests PASS,77 records×2 generated canary variants=154 PASS. Additional generated differential cases below reveal a gap in that suite; synthetic coverage PASS is not source equivalence proof.

## Blocking finding: RZ1 fit native token semantics strengthened

native_metadata_predicates_v2.evaluate, tokens branch for fmt rz1_fit, computes every individual native token as `(k +   +  .join(vs) +  ) in x +  `. This adds a trailing-space condition to all PINS and to the final skip_tt1 value. Actual src/NEXT/read_selection.py load_rz_network uses PINS fragments without trailing space, followed by precisely four other fragments: spec and primary with trailing space, grouped res/bs/accum with trailing space, and `steps 6250 limit 0 skip_tt1 0` WITHOUT trailing space. Existing grouped native_fragments correctly preserve the latter, but extra individual native rows can contradict it.

Generated tests built from the actual frozen RZ1_SbMR_s408 task_info descriptor, with no real archive: (1) append `suffix` to its correct pack_sha256 value; (2) append `suffix` after final skip_tt1 0. Original native recipe all-fragments predicate is True in BOTH cases. Collector reports native FAIL for recipe.pack_sha256 and recipe.skip_tt1 respectively. These malformed strings should fail strict integrity, but must not be mislabeled as failures of the unchanged native predicate. This matters precisely because the adopted design promises separation and forbids false native failures.

Required minimal repair: represent the exact source native fragment list explicitly and evaluate it literally. Keep individual token/unique-token checks solely as strict_integrity_status where they add constraints beyond the native fragment. Do not change the canonical native reader or weaken strict integrity to conceal the distinction. Add differential tests for PINS suffix, final skip_tt1 suffix, trailing whitespace/tab/newline and grouped fragment order/adjacency; compare the generated native predicate to source semantics. Re-freeze collector/predicates/scope/package hashes and request bounded delta review. No live outcomes need to be opened to fix this.

## Other assessed boundaries

Whole-log lexical loss predicate matches the exact unanchored case-insensitive native regex. Generator/all short circuit for native_fit versus eager float-list conversion for RZ is retained: later malformed token after nonfinite can produce FAIL versus UNKNOWN respectively. Only presence/count/finite/conversion status is exported, no captures/values/lines. The prospective root adoption authorizes precisely that technical boundary; future live release must still explicitly enable it. It is not a training-only loss claim.

Supplement joins fixed configured name/seed/sourceSHA/manifest/count to unique status/gate; missing and duplicate associations do not silently become survivors. Literal valid/Boolean receipt flags are distinct from Python numeric equality. Exact tt1/meds and digest shape checks are present. W2 native per-model task membership, GPU substring, three script hashes, counters and exact_gate are separate from full20-task planned integrity. RZ refit full PINS/historical scorer/train_Sb history, source tar/SHA, gate and limit are represented; prospective gate.manifest check is not mislabeled native. Unsupported device structured values become UNKNOWN rather than a guessed string conversion.

Missing15 BB2 bs/accum proof stays UNKNOWN, not a posthoc choice among128×2/256×1. Per-record failures remain in all77 output records; no eligibility/global-winner filtering exists. Five SbMR512 info/env additions expose only restricted versions/digests/normalizedH100 or fixed comparisons. train_acc_rule0/scientific siblings are lexically skipped, not decoded or exported. last_pt_sha256 is explicitly the full checkpoint hash, not invented trainable checkpoint hash. Scorer TF32/noTTA/runtime/kernel admission remains UNKNOWN/separate; env fresh-process flag does not certify scorer runtime.

Release checks precede collect_archive calls: exact decision/packet/source/predicates/review hash and GO line/output/CPU/whole-log scope, then all source pins. Same regular O_NOFOLLOW descriptor is hashed before tar traversal. Tar traversal has100000-header cap, selected8MiB/member and256MiB parse budget, duplicate-normalized paths, traversal/link/device/sparse refusal. No extractall or NPZ parsing. Selected JSON bounded-depth parser does not decode skipped scalar values; fixed error codes avoid input-fragment leakage. All errors/records remain explicit. JSON output and digest/completion files use exclusive temporaries, fsync, rename and final directory fsync. Incomplete output is not completion or retry authority. A completed technical collection would still not mean native/scientific eligibility.

## Required follow-up and remaining HOLD

Author source correction and independent delta review first. After exact implementation GO, root must adopt clean committed owned files, verify staged pins, issue a separate exact technical-only release and independently review actual technical collection. Even after those steps, native payload/schema/ID/floors/C2P/NI/exposure/kernel and unresolved policy gates remain separate. No NEXT preflight/read/claim or scientific admission is authorized here. Original proposals, V1 and canonical native sources were preserved; no author file was edited by reviewer.
