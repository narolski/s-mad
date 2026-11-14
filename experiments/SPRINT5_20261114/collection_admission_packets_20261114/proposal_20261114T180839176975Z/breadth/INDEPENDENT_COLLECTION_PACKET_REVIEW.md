# Independent breadth/tail metadata-collection packet review — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of packet/reader author Sol.
Decision: **GO_METADATA_COLLECTION_DESIGN_AND_OPAQUE_ROSTER_FOR_ROOT_RELEASE**.
This is not a metadata collection release, actual-fit eligibility verdict, scientific read, baseline/camera release or publication approval. Root must issue the separate exact releases. Both unsigned proposals were rejected by the actual validators, as required.

## Exact reviewed packet

FINAL_FREEZE_MANIFEST.json SHA256 eb2d37990b08513ddc0ff0804b88d5b997e7dcbb93836fc76ea49719c7ef7e8d. Every listed file independently rehashed and matched.
Independent evidence: ASTRA_INDEPENDENT_METADATA_CHECKS.json SHA256 a845362e11b367ce5a9ef90dd808248a88daef620f40b9e487a89e633660fb56, in the packet root.

| Cohort | Roster SHA256 | Reader manifest SHA256 | Binding SHA256 |
|---|---|---|---|
| breadth, 10 fits | 1680c52e03a3b4d719aa20ad1e54b81d6e463589caf03e1c8c43ccce89e248a5 | e96b36f1abd1d132871fb1cf1358eded82d888efb289409ff10e51f41d4a5101 | bf5c55bc6d6663f57be70503c68c939f6b0e0f579513548973e423cdc118e808 |
| tail v2r1, 15 fits | e99840224f61f28b6825712eb8665e41cb1d1dfb6569cf5119375e35c5a3eea9 | 943d47ef9ac0638c46dc1fdaf65782cabbd43d93405ce80305c4bac58c1fce5b | ff2aa74853658d1d318725e42eedbdd2ac16cde8d7da57971c04e4447626c6a2 |

## Independent checks: PASS

Recomputed all 25 archive hashes as opaque byte streams, sizes, sidecar hashes/content digests/basenames, and linked durable transfer receipt hashes. Each archive and sidecar agrees with its exact remote-source entry in the receipt. No tar member was listed or extracted. Receipt provenance proves durable byte arrival; it does not establish scientific validity or successful training.

Ran each frozen admission module separately with actual validate_binding(require_committed=True), actual validate_roster, and actual unsigned-release rejection. No mocked Git/subprocess checks. Breadth: 210 input pins, 79 distinct tracked-clean repository paths, 10 exact arm/seed plans. Tail: 130 input pins, 106 distinct tracked-clean paths, 15 exact plans. Shared prefit verifier ran through the validator. Breadth metadata/floor loading and tail metadata/design reproduction passed. All reader-manifest source hashes matched. Each cohort has the exact full arm×seed inventory, distinct archive hashes and resolved paths. Breadth seeds 511–515; tail seeds 521–525. Source/admitted-input/policy/prereg/review dependencies remain pinned. Actual input-admission hashes were also checked directly.

## Collector boundary and eligibility design: PASS

Reviewed both collector/admission sources and shared member_bytes helper. Collection requires independent GO_METADATA_COLLECTION_ONLY, exact source/binding/roster/review/admission hashes, clean committed pins, and every opaque archive digest before creating its exclusive output directory. Fixed-name JSON/TXT/LOG metadata only are decoded. The helper requires one regular member and an 8 MiB size cap. NPZ and checkpoint names are inspected as unique nonempty regular-file headers only; no NumPy/torch deserialization occurs. Camera payloads are not selected. Source-pinned tail TRAIN_ONLY reference and objective trace are metadata checks, not detector-result reads.

Before an eligible envelope can be written, collectors enforce exact architecture/resolution/platform/arithmetic, source/manifest/schedule, last checkpoint header, finite logged loss and complete steps. Breadth is 100×32 = 3,200 forward images; tail 100×256 = 25,600. Reference byte gate requires 2,496 rows, zero differences and max_abs=0; own-fit gate requires 21,277 common rows, zero differences and max_abs=0. All dev/TT1/MEDS/GD battery counts (21,277/34,411/1,018/11,042) and finite/completeness metadata must pass. Tail additionally checks fixed 100-step objective trace with finite state and bounded duals, required objective-state header, and absence of failure artifacts. This does not independently reconstruct optimizer dynamics from trace.

Collection creates per-fit metadata envelopes and complete roster only after checks; exceptions preserve COLLECTION_FAILED. The scientific reader still requires separate GO_READER_READ plus collector review and matching envelopes/archives. Opaque arrival is not all-25 eligibility: actual gate values remain uninspected until root releases metadata collection.

## Tail compatibility receipt: PASS, schema-only

Independently compared original receipt 85fb4129e1432e7f59540c997a46f8c76ee16d6c73095fae99ed3704813e033e to compatibility receipt 1d85babbc525f4b3dcf966e988ca7e9eba0caab980f228fa093e4ce25f6c9556. Only timestamp, literal baseline HOLD enum, explicit REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION reporting requirement, adopted point-only diagnostics enum, and explanatory supersession/correction fields differ. Source/input/policy/review pins and scientific/camera HOLD remain unchanged. The original receipt is retained. This does not waive the still-required separately admitted baseline panel or create diagnostic confidence intervals.

## Root action and limits

No blocking correction found for the exact proposed metadata-only collection scope. Root may create separately hash-bound GO_METADATA_COLLECTION_ONLY releases referencing this review at the cohort paths, exact rosters, code/bindings and fixed proposed output directories, then run the reviewed collectors. Retain all collection failures; independently review actual envelopes before any scientific release. No actual collector, reader, journal claim, archive-member listing/extraction, candidate NPZ/weights access, GPU, scheduler or WCSS operation was performed for this review. No scientific outcome is asserted. Baseline auxiliary remains required but HOLD; camera and scientific reads remain HOLD.
