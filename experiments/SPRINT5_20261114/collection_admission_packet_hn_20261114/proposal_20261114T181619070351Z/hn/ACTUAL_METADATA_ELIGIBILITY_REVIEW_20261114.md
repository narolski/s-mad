# Independent actual HN10 metadata eligibility — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of Sol reader/packet implementation.
Decision: **GO_ACTUAL_METADATA_ELIGIBILITY_FOR_ROOT_PRIMARY_READ_RELEASE**.
This report does not issue GO_READER_READ, execute scientific analysis or create a read claim.

Actual complete10 matched/self × seeds531–535 envelopes independently passed frozen validate_envelope with exact registered plans, full roster validation, actual root metadata-release validation and validate_binding(require_committed=True). The latter rechecks1,034 input pins, committed source/input paths, shared prefit inputs/floors and registered bootstrap metadata. All envelope hashes/paths match the reader roster; original archive/provenance fields match the previously independently opaque-hashed inventory without additions or substitutions. This task read only registered source/input metadata, envelopes, roster, completion and root execution/release JSON; no archives, headers, NPZ, weights or scientific values.

The output directory contains exactly ten expected envelopes plus roster/completion, no COLLECTION_FAILED or extra fit receipt. Native execution exit0 and completion are corroborated by every envelope passing, not used alone. Actual100 updates, batch248,24,800 exposures, last-checkpoint header presence, complete finite training metadata, exact schedule/train/eval/source, a12_clip_vitb16_madation/res224, H100/torch2.11.0+cu128/CUDA12.8 and pinned arithmetic pass. Reference2496 and own-fit21277 gates report zero differences/max_abs0. All four battery counts21,277/34,411/1,018/11,042 are complete and finite.

Actual HN_warmstart metadata for all ten fits passes single admitted AB1 Sb408 conditioning, fresh AdamW/no inherited moments, fixed checkpoint path suffix and nonempty sorted unique trainable parameter names. Provenance remains the source-pinned worker's hash-verified a84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa archive→AB1_Sb_s408/last_trainable.pt extraction chain. No independent checkpoint rehash, optimizer-state reconstruction or independent-pretraining claim is made.

## Exact pins

- Verification JSON: ACTUAL_METADATA_ELIGIBILITY_VERIFICATION_20261114.json, SHA256 092fda4daaf16e5044c3fe0ee0615a27e278068d17db01eb827a27ae3ae15365.
- reader_manifest_sha256: a8a083a686ab47cf8f02e5a7da9e6dec92a797e33c5ec9b4e75f979e30400794
- binding_sha256: 51ae40530ee4a848aece44693c143923a68636eb769468e5e5637904ab8eede3
- reader_roster_sha256: cc7fb2a7b96d39dd7735281db79f9e53d7832e64676de1f4307709cfef351742
- opaque_roster_sha256: 621611f53e89b601dae00c937893b6ef193548be8a74d15591081080a3c17a10
- metadata_release_sha256: 338b2681bc127718d58226d7633ca8b04ea795ecd15c34b33949b86498b4b67c
- execution_sha256: 4dc078c6c1e040d6ede06adc0d3d3cc33d8ec555450e3d5d78b3be9f56a5a9f5
- execution_source_commit: 0f5e9942a2c4e10211c37bb6d79e94577d1e5a36
- complete_sha256: 61d3823afa96fac91038a03a32f9bfac36997423b1dec92dc5cc123ca515cf9d
- collector_review_sha256: 234b1bf8fc9e70faf15911e16b0e4e4596ebf20d04e1e4b4466dd3bdbac726e1
- input_admission_sha256: 1166086a0ccae0e229ba9a4cf9bd6fd4f530199b1c1ed1de40a2d722bac96c71

Every reader-manifest file and SHA256SUMS was independently byte-compared to the collector execution source commit; identical. Live required committed-input validation passed. Frozen shared helpers remain hash verified.

| Task | Envelope SHA256 |
|---|---|
| SPRINT5_2_pilot_v1_matched_s531 | 93d10bbb8da440adab09cdb7c9b8d0ec4156681c68cd652b5308350bb9977b6a |
| SPRINT5_2_pilot_v1_self_s531 | 4c1398cc9388b88ffa24c7f869c68ee816bcfe7612a5b1ddda58b2add4d5cdb8 |
| SPRINT5_2_pilot_v1_matched_s532 | 558965ffdd3f0a4b3f50151fef99587d83bad7d8876c91fddb250df9c7535759 |
| SPRINT5_2_pilot_v1_self_s532 | 0bdc7969a0b074cb4a49cd9656d6e01b9ba88d7b5ef87796db7cdcc5c31e57a4 |
| SPRINT5_2_pilot_v1_matched_s533 | 6f1e8313a463eae7254009e70b3994923d72bf9a809ab30cb6bd507aa9fb882c |
| SPRINT5_2_pilot_v1_self_s533 | beae81647c26347319bb66d8cf9d15c08aca6fbf090a6a235a089b35667a05a5 |
| SPRINT5_2_pilot_v1_matched_s534 | 302bca94b42eb1d3553d93bbd98ce781a1b6361891892df890f963fd7b19145f |
| SPRINT5_2_pilot_v1_self_s534 | 3004de614a506509c330d3d4cbff6cb6fd28664f5c8df8781719f927613ac442 |
| SPRINT5_2_pilot_v1_matched_s535 | 40ea2ebefaeaac209920874ba7ffebfbff61ab33e2acb78d59fb6aba71e3d395 |
| SPRINT5_2_pilot_v1_self_s535 | c8153e8351a2c0acc38671ab52b70ece66ab578e4559457421a2364a7cddb828 |

Full per-fit archive/source, warmstart and battery gate metadata are retained in the hash-bound verification JSON.

## Read boundary and prospective interpretation

Actual ONCE and OUTPUT paths were absent and left absent. Reviewed read.py retains independent exact GO_READER_READ admission before create-only/fsynced permanent claim, and claim before payload.arrays. Complete10 inputs and reviewed envelope chain are mandatory; no retry, alternate journal, seed substitution or winner selection. Future loader access is restricted to the two admitted dev NPZ containers for integrity/equality validation and returns only fixed200 nativeS4/S3dev100 IDs. It will deserialize those containers physically; no historical191/camera metrics or checkpoint data are returned. No such access occurred in this review.

Keep exact200/40 components/15 fixed floors. RNG2026111402 and registered10,000 accepted label-conditional component draws from10,178 attempts, then paired continuation seeds, remain fixed. Descriptive95% percentile intervals are conditional on readable fixedD strata, not unconditional95% coverage. Point mean gain≥.03 and at least4positive seed effects are descriptive transfer-support criteria only; show intervals alongside, with no added CI-positive/floor gate or statistical-superiority/adoption claim. This tests transfer onto the existing S4/S3 evaluation, not a newly held-out HN construction pool or identity specificity. Preserve disclosed construction nuisance floor max.7433476 and conditional interval[.7125105,.7959151]; conditional single-warmstart variability and native-only scope remain explicit. Camera remains HOLD; baseline auxiliary is outside this reader scope.

Root may now make the separate exact-version read decision: bind this report as independent_review, the new READER_ROSTER hash above, unchanged source/input/admission pins, and collector_review234b1bf8fc9e70faf15911e16b0e4e4596ebf20d04e1e4b4466dd3bdbac726e1 matching all envelopes. Recheck absence immediately before any released run. This review itself leaves scientific read HOLD and performs no collector/reader/claim, GPU, scheduler or model computation.
