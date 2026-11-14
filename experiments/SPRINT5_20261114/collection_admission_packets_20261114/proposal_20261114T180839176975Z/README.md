# Breadth10 and tail15 metadata-collection proposal packets

Both complete opaque cohorts are present: breadth10 and tail15. Only durable transfer receipts, source/input metadata, file stats, sidecar text and opaque archive hashes were used. No tar member/header listing, extraction, score/checkpoint interpretation, actual collector or scientific reader invocation occurred.

The real reader input preflights used validate_binding(...,require_committed=True), with actual Git and shared-prefit verification. All reader dependency inputs, source policies, source files, root admission/code-acceptance and prior independent review paths were tracked and clean. The original tail root receipt remains preserved; the newly committed collector-compatible receipt is bound, with an exact JSON delta included. Its literal baseline enum HOLD retains the separate REQUIRED reporting annotation.

Each subpacket contains:
- EXPECTED_TASKS.json and complete OPAQUE_ARCHIVE_ROSTER.json from exact tasks/seeds, local paths, remote origins, receipt hashes, archive byte sizes and actual opaque SHA256 rechecks.
- INPUT_SOURCE_PREFLIGHT.json and ACTUAL_ROSTER_VALIDATION.json. The actual roster validators passed; the actual release validators rejected the unsigned proposals.
- PROPOSED_METADATA_COLLECTION_RELEASE.json. It is unsigned: decision PROPOSED_GO_METADATA_COLLECTION_ONLY, independent review SHA null. It grants no execution. No hashes or review signatures were guessed.
- ROOT_COMMAND_AFTER_REVIEW_ONLY.txt with the exact independently gated collector command, fixed fresh output path and a future ROOT_METADATA_COLLECTION_RELEASE.json path. That actual release file does not exist here.
- PACKET_STATUS.json; the tail subpacket additionally contains ROOT_ADMISSION_COMPAT_EXACT_DELTA.json.

Required next actions belong to root and the independent reviewer:
1. Independently check both actual complete rosters, durable receipt/hash pins, current collector design/code, input/source provenance, output freshness and the exact tail compatibility delta.
2. Write and bind INDEPENDENT_COLLECTION_PACKET_REVIEW.md (or issue a reviewed release pointing to another exact independent review path/hash).
3. Root issues separate exact GO_METADATA_COLLECTION_ONLY releases for breadth and tail, binding the relevant roster, reader/source/input admission and independent review. Replace the proposal decision and fill the actual review hash only in a NEW root release, preserving this proposal.
4. Execute each fixed command only after its own reviewed release. The collectors then admit actual metadata; opaque arrival alone does not establish successful fit eligibility.

There is no metadata collection release, scientific read, stage advancement, baseline-score or camera admission in this packet. The required baseline-threshold panel remains HOLD; no full scientific result is claimed. Both fixed output directories were absent at preflight and are never created by this preparation.

FINAL_FREEZE_MANIFEST.json pins all existing proposal artifacts, including the preparer and original manifest. Later root review/release files are separate additions; they must bind these exact frozen rosters and source/input hashes. No frozen reader/statistics code was changed.
