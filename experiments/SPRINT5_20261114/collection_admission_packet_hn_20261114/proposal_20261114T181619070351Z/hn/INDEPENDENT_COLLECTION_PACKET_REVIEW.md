# Independent HN10 metadata-collection admission review — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of Sol packet/reader author.
Decision: **GO_METADATA_COLLECTION_DESIGN_AND_OPAQUE_ROSTER_FOR_ROOT_RELEASE**.
This is not an actual collection release, successful-fit eligibility finding, scientific read, camera release or adoption/publication decision.

## Exact scope and pins

- FINAL_FREEZE_MANIFEST.json: 6dad13ca83ea90dd5ba5a51138daec6f12ea6a4e7f1c1d3a45406a71b5cb213b.
- OPAQUE_ARCHIVE_ROSTER.json: 621611f53e89b601dae00c937893b6ef193548be8a74d15591081080a3c17a10.
- Unsigned proposal: d629acac4e43e94dca5c1d330a95c91967253945a725d3a842eb60602e84536f.
- Reader manifest: a8a083a686ab47cf8f02e5a7da9e6dec92a797e33c5ec9b4e75f979e30400794.
- Input binding: 51ae40530ee4a848aece44693c143923a68636eb769468e5e5637904ab8eede3.
- Root input admission: 1166086a0ccae0e229ba9a4cf9bd6fd4f530199b1c1ed1de40a2d722bac96c71.
- Independently produced packet-root ASTRA_INDEPENDENT_METADATA_CHECKS.json: 36dd6f06b4d93f7984d3ee7297b993c3794d40892358023b8ca6c0c1004bbaba.

Every frozen manifest-listed file and reader source member was independently hashed and matched. Actual validate_binding(require_committed=True) passed without mocking Git/shared verifier: 1,034 input pins and 100 distinct tracked-clean repository paths. Metadata/floors and registered HN bootstrap design reproduction passed. Actual full-roster validator passed; actual unsigned proposal validation rejected with “wrong release”, as intended.

## Opaque arrival and provenance: PASS

Independently streamed SHA256 over exactly ten named HN archives, verified file sizes, sidecar hashes/content digests/basenames, and hash-bound durable transfer receipt entries at exact remote source paths. Exactly nine are from sprint_complete_cohorts_20261114T180257Z and only self_s535 from hn_pair_collection_20261114T181157Z. Other archive records in these receipts were not selected or hashed. The inventory is exactly matched/self × seeds 531–535, with unique archive paths and hashes. No archive header/member listing or extraction occurred.

Warmstart provenance is appropriately limited. Source-pinned hn1_transfer/worker.sh checks whole AB1_Sb_s408.tar SHA256 a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa before extracting AB1_Sb_s408/last_trainable.pt and binding HN_WARMSTART. The collector validates HN_warmstart.json conditioning, fresh AdamW/no inherited moments, exact path suffix and nonempty sorted unique trainable parameter names. This is the admitted archive/source extraction chain, not an independent checkpoint-byte rehash or evidence of five independently pretrained initializations.

## Collector and release design: PASS

Reviewed actual collector.py/admission.py and the pinned shared safe metadata helper. Independent exact GO_METADATA_COLLECTION_ONLY plus source/binding/roster/review/input-admission hashes and committed inputs are required before archive access. All ten opaque hashes are rechecked before exclusive output directory creation. Fixed-name JSON/TXT/LOG metadata only are decoded; the helper requires a unique regular member bounded to 8 MiB. NPZ/last checkpoint files are checked only for unique regular nonempty headers. No NumPy/checkpoint deserialization, camera-array selection or scientific computation is performed by collection.

Before metadata eligibility, each fit must match its exact schedule/source/train/eval pins, H100/torch2.11.0+cu128/CUDA12.8 and arithmetic flags, a12_clip_vitb16_madation/res224, last checkpoint, 100 updates × 248 images = 24,800 forward images, complete step metadata and finite logged losses. Reference gate requires 2,496 rows with zero byte differences/max_abs; own-fit gate requires 21,277 common rows with zero differences/max_abs. Battery counts dev21,277/TT1 34,411/MEDS1,018/GD11,042 must be complete, finite and image-verified. These are prospective collector requirements, not already-observed values from candidate archives.

The collector records per-fit envelopes and complete roster; failure creates COLLECTION_FAILED. Scientific reader requires distinct GO_READER_READ and matching reviewed metadata receipts. Primary descriptive scope remains fixed200/40 components/15 floors; matched-minus-self criteria remain descriptive, with no new CI-positive/adoption rule. Camera HOLD and no camera-array access remain intact.

## Root handoff

No blocking correction for the exact metadata-only scope. Root may issue a separate release referencing this review hash and the exact packet, then collect into the proposed fresh output directory. It was absent at review. Review all ten actual envelopes before any scientific release; missing/failed eligibility does not authorize seed replacement. No collector, scientific reader, journal claim, GPU/cluster/scheduler action, checkpoint access or scientific payload read was performed. Opaque arrival proves transfer integrity only. Scientific read and camera remain HOLD.
