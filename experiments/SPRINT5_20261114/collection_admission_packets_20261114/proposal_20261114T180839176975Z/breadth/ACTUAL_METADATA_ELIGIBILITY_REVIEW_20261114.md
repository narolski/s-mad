# Independent actual breadth metadata eligibility — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of Sol implementation/packet author.
**GO_ACTUAL_METADATA_ELIGIBILITY_FOR_ROOT_PRIMARY_READ_RELEASE** for the exact cohort and frozen scope below. This report does not issue GO_READER_READ or execute any scientific read.

## Independent actual checks: PASS

Validated all10 actual envelopes using frozen validate_envelope and exact registered plans, actual full roster validator, actual metadata-release validator and validate_binding(require_committed=True). No mocked checks or collector/read invocation. Each envelope hash/path matches READER_ROSTER; its original archive identity, opaque digest and transfer provenance match the independently reviewed original opaque roster exactly. No tar/header/member or score/checkpoint access occurred in this task. Opaque bytes were already independently hashed in the prerequisite review, and the future admission/loader rehashes them before payload use.

Collection output contains exactly the registered per-fit envelopes, READER_ROSTER and COLLECTION_COMPLETE, with no COLLECTION_FAILED or substituted/extra envelope. Complete marker matches exact roster hash and count. Native execution records show exit0, matching frozen collector commands/output paths, no scientific authority and no claim. Unlike relying on exit0 alone, every actual envelope was independently revalidated.

All actual source/train/eval hashes, complete100-step schedules, last-checkpoint presence metadata, finite loss metadata, architecture a12_clip_vitb16_madation/res224, H100/torch2.11.0+cu128/CUDA12.8, float32 eval/no-autocast and pinned TF32/cuDNN flags pass. Reference byte gate:2,496/zero differences/max_abs0. Own-fit gate:21,277/zero differences/max_abs0. Every dev21,277/TT1 34,411/MEDS1,018/GD11,042 count is complete and finite. Battery metadata are eligibility evidence, not scientific benchmark interpretation.

Breadth: narrow_more_variants/broad_fewer_variants ×511–515,100×32=3,200 image exposures per fit.

## Exact pins

- Verification JSON: ACTUAL_METADATA_ELIGIBILITY_VERIFICATION_20261114.json; SHA256 df7388803e290d8e4bd522c54f9ba582c4a0531a51a0df9c03d3fd6c08824e5e.
- reader_roster_sha256: 34796a3fd83096aabeacc8e25c79954ed41311e0585107423c88b9bd44052d3c
- opaque_roster_sha256: 1680c52e03a3b4d719aa20ad1e54b81d6e463589caf03e1c8c43ccce89e248a5
- reader_manifest_sha256: e96b36f1abd1d132871fb1cf1358eded82d888efb289409ff10e51f41d4a5101
- binding_sha256: bf5c55bc6d6663f57be70503c68c939f6b0e0f579513548973e423cdc118e808
- metadata_release_sha256: ca25b56f27faff41b2cad01c52e13cbfba915183d069919f77eaa4c23bd06383
- execution_sha256: 01f745de81daaa67f78144ca56f894e6611d91805b5718406c6627953e9adcd3
- complete_sha256: 510b83f498ad9ef46ba00e33411179274049adca5c8c1b56225240c05b45a9f6
- collector_review_sha256: b086df6ef2ff07669e0d143a578c4b9b6350e0a45b37f5b2061439b3b25b568c
- input_admission_sha256: ccb311f38e277db22c12327a5fe693af0bd528bfab1dc13b6ee3d12f2a5006c9
- source_last_commit: a29502ebcf5b0f70a10c137cf398f155db39a8d2

The collector execution commit041fc6e12ad9f950ef5db7666d4c0678b38e517a contains byte-identical reader SHA256SUMS and every manifest-listed source file (independently compared via git show). Live committed-input validation and source manifest checks pass. Frozen original shared helpers remain hash-verified. No author/source edits were made.

| Task | Envelope SHA256 |
|---|---|
| SPRINT5_4_pilot_v1_narrow_more_variants_s511 | 6965604bf3980ad3aff582ad58905dc7978755595f83c9a1f69dfd1b2775292c |
| SPRINT5_4_pilot_v1_broad_fewer_variants_s511 | 49b0b5d6fb7f8b04db2ffde21130672f03316af6c1f8f4f16bc5f485a7b387e6 |
| SPRINT5_4_pilot_v1_narrow_more_variants_s512 | ec94c6a7395fbd267bbbf70389fc87c4ba1bfce48fab037a285652b76e5a4465 |
| SPRINT5_4_pilot_v1_broad_fewer_variants_s512 | 233dc8fdcf940fa9987ba65517fd311723fb84bb0a50d41c2aa1096ab52be288 |
| SPRINT5_4_pilot_v1_narrow_more_variants_s513 | 2a74fae15caca6b123d72226b91b43a57c8ade7c6f773feba847daadbc483b50 |
| SPRINT5_4_pilot_v1_broad_fewer_variants_s513 | aa7a52c9adbd40ca87ade65d36f852d3c3599859de3b9fae3b77f94e28411aca |
| SPRINT5_4_pilot_v1_narrow_more_variants_s514 | 72be3eedc806fc5e600ee64334f581b9a29121d7c6185ff53c3cbc61d7a60e71 |
| SPRINT5_4_pilot_v1_broad_fewer_variants_s514 | 012f03beb4e94cb8b00658603b05e667664dbbb2c59d35e8a9387b54ddfd6921 |
| SPRINT5_4_pilot_v1_narrow_more_variants_s515 | 3a6c763ee0317ccf85fcebc3c66b66c203cd8cc7c60678a7a08565b7b9295018 |
| SPRINT5_4_pilot_v1_broad_fewer_variants_s515 | 355aa87a64807fd70fabb767839bf8496279ba58237e15eb055e37d9f8e7554d |

Full archive/source/battery gate pins for every fit are retained in the hash-bound verification JSON.

## Scientific boundary and permitted scope

Breadth: exact200 native S4/S3 dev100 rows, 40 full components, 15 fixed cross-fitted floor predictions; broad-minus-narrow equal-five-D AUC, with all five paired seeds. RNG2026111404 uses source-stratified components then joint seed indices per replicate. Preserve all10,000 records, including151 structurally undefined and9,849 readable draws; conditional-readable percentile95% intervals do not establish unconditional95% coverage. Fewer than two finite draws or zero variance is INCONCLUSIVE; unexpected nonfinite readable values are fatal. Maximum of fixed15 floors is recomputed per shared draw, without nuisance refitting. No binary success/adoption gate, isolated identity-count claim, camera threshold or historical191 metrics.

Reviewed read.py/payload.py and create-only journal source: A.admit validates separate GO_READER_READ, complete cohort, committed input/floor metadata and exact receipts before any claim; create-only/fsynced CLAIM precedes first candidate NPZ access. Fixed permanent ONCE and OUTPUT paths were absent at this review and were not created. Exceptions terminate the permanent journal; no retry, alternate journal, seed replacement or seed selection is allowed.

Important physical/logical boundary: a future released loader must deserialize the two admitted dev NPZ containers to verify hash/schema and exact own-fit equality, then returns only registered primary/calibration/evaluation IDs. It does not return historical191/camera arrays or interpret their metrics. This review did not deserialize either container. No weights are loaded by the reader.

## Required root release binding

Root may issue an exact-version GO_READER_READ only after its own check, using the READER_ROSTER hash above (not the original opaque roster hash), independent_review_path/hash for this report, and collector_review_path/hash for the prior b086df6ef2ff07669e0d143a578c4b9b6350e0a45b37f5b2061439b3b25b568c review that every envelope binds. Retain the exact source/binding/input-admission scope and a fresh pre-read absence check. This report grants eligibility for that root decision only, not actual read permission. No baseline/camera expansion or final adoption/publication GO is implied.
