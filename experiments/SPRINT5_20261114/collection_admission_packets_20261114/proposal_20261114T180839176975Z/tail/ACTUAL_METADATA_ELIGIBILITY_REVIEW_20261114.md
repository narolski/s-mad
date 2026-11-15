# Independent actual tail metadata eligibility — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of Sol implementation/packet author.
**GO_ACTUAL_METADATA_ELIGIBILITY_FOR_ROOT_PRIMARY_READ_RELEASE** for the exact cohort and frozen scope below. This report does not issue GO_READER_READ or execute any scientific read.

## Independent actual checks: PASS

Validated all15 actual envelopes using frozen validate_envelope and exact registered plans, actual full roster validator, actual metadata-release validator and validate_binding(require_committed=True). No mocked checks or collector/read invocation. Each envelope hash/path matches READER_ROSTER; its original archive identity, opaque digest and transfer provenance match the independently reviewed original opaque roster exactly. No tar/header/member or score/checkpoint access occurred in this task. Opaque bytes were already independently hashed in the prerequisite review, and the future admission/loader rehashes them before payload use.

Collection output contains exactly the registered per-fit envelopes, READER_ROSTER and COLLECTION_COMPLETE, with no COLLECTION_FAILED or substituted/extra envelope. Complete marker matches exact roster hash and count. Native execution records show exit0, matching frozen collector commands/output paths, no scientific authority and no claim. Unlike relying on exit0 alone, every actual envelope was independently revalidated.

All actual source/train/eval hashes, complete100-step schedules, last-checkpoint presence metadata, finite loss metadata, architecture a12_clip_vitb16_madation/res224, H100/torch2.11.0+cu128/CUDA12.8, float32 eval/no-autocast and pinned TF32/cuDNN flags pass. Reference byte gate:2,496/zero differences/max_abs0. Own-fit gate:21,277/zero differences/max_abs0. Every dev21,277/TT1 34,411/MEDS1,018/GD11,042 count is complete and finite. Battery metadata are eligibility evidence, not scientific benchmark interpretation.

Tail: bce/mean/cvar ×521–525,100×256=25,600 image exposures per fit; all training-reference and objective-trace eligibility flags pass the reviewed collector schema. This is metadata validation, not independent reconstruction of gradients/optimizer states.

## Exact pins

- Verification JSON: ACTUAL_METADATA_ELIGIBILITY_VERIFICATION_20261114.json; SHA256 3347861cc1bd4acf4966c00b7717b0d0db16bff618769119831d9637dffbccbd.
- reader_roster_sha256: 08502ee93c955e5e43c645d2a7a2230cecf52c38558aabf80dcaeae0d11c7e88
- opaque_roster_sha256: e99840224f61f28b6825712eb8665e41cb1d1dfb6569cf5119375e35c5a3eea9
- reader_manifest_sha256: 943d47ef9ac0638c46dc1fdaf65782cabbd43d93405ce80305c4bac58c1fce5b
- binding_sha256: ff2aa74853658d1d318725e42eedbdd2ac16cde8d7da57971c04e4447626c6a2
- metadata_release_sha256: 71aa13da51d86fef0d2747575749bddeafebdfd21c6c1107c00cc9e244c9a1db
- execution_sha256: 1c074c5485b26463311398f3de4f95f6de03bb0db97ae1a92b633c1bc7d75723
- complete_sha256: 288f8c6d61aee7a88afee1980488bba81b48de0e7ee711ff759c67a199e98285
- collector_review_sha256: b086df6ef2ff07669e0d143a578c4b9b6350e0a45b37f5b2061439b3b25b568c
- input_admission_sha256: 1d85babbc525f4b3dcf966e988ca7e9eba0caab980f228fa093e4ce25f6c9556
- source_last_commit: 2a1e908d656e2d248c006874b6b7a5121a86d27b

The collector execution commit041fc6e12ad9f950ef5db7666d4c0678b38e517a contains byte-identical reader SHA256SUMS and every manifest-listed source file (independently compared via git show). Live committed-input validation and source manifest checks pass. Frozen original shared helpers remain hash-verified. No author/source edits were made.

| Task | Envelope SHA256 |
|---|---|
| SPRINT5_3_pilot_v1_bce_s521 | 5723add3a2962f0449ed398ca990929e7ce0d54786dad6fd371492093459c084 |
| SPRINT5_3_pilot_v1_mean_s521 | 0cb1932907a5e911f0a3ba386915b57b5e049c128668445199e246d413179f69 |
| SPRINT5_3_pilot_v1_cvar_s521 | 9ef119011ff80561ab1e508d4c74d1dd4a54dcb278d92908e78181eaf7991845 |
| SPRINT5_3_pilot_v1_bce_s522 | f722e8b9b6b280f0e035cff74300d904e058956c90fb206d799f61cc75499591 |
| SPRINT5_3_pilot_v1_mean_s522 | c210440027c0dbdddee5d8edda769fcdd427c8547969e65a0d24508da4b45b9d |
| SPRINT5_3_pilot_v1_cvar_s522 | 97a5e82738019275938d609019e91ef120b1b998e9980499f337b850ffb8889b |
| SPRINT5_3_pilot_v1_bce_s523 | 94740b6cefe0ee4a6118e5160b90770e99b62c34b219f88dbe8237c7ce96376c |
| SPRINT5_3_pilot_v1_mean_s523 | afc42020d97f69700fc64741442d7ef7e9a1409e0810c9351688924fdefbe430 |
| SPRINT5_3_pilot_v1_cvar_s523 | 5e1ac2b43c07ea0d6cc6edf43a980429eacb9d032c5db262f082c6b32e21772a |
| SPRINT5_3_pilot_v1_bce_s524 | da23af0c086eb7ca1b32c2a17f4185d678d4dec260148faa00628e6a79f78f5e |
| SPRINT5_3_pilot_v1_mean_s524 | acbab80336ff35f2afbec3d2c38bbb20b0beb4319e3d7608e8035093b42a909c |
| SPRINT5_3_pilot_v1_cvar_s524 | a7df34691c9d2dba9d18c2a5d2924e9d3f110d4a8ec1cb457ded210b055bbe68 |
| SPRINT5_3_pilot_v1_bce_s525 | d839a34754a7bdefd1db53e14c662f1e42bad3c0a215987dbfd1ef3bb49bac7c |
| SPRINT5_3_pilot_v1_mean_s525 | c0f998650fe774059dcc160a8ea1bc6fb33f5e798c717cd44e2b305cf29ea7a5 |
| SPRINT5_3_pilot_v1_cvar_s525 | c3042a2bdf9ffb3f378bfbe58f6c0744bdb9795497820824c8b2bddb7338a405 |

Full archive/source/battery gate pins for every fit are retained in the hash-bound verification JSON.

## Scientific boundary and permitted scope

Tail: exact70 independently eligible positive calibration rows,180 positive evaluation rows and288 genuine evaluation rows, with source/person/component provenance fixed by adopted policy. Primary FAR uses strict score>nextafter(sorted positive calibration[floor(.10*n)],-inf), float64, separately per network; it is not the132-camera/order127 rule. RNG2026111403 draws evaluation source-stratified components, independent calibration components, then joint five paired-seed indices;10,000 attempts/no redraw. Six genuine source×processing FAR cells and all registered contrasts remain descriptive, with pointwise approximate95% percentile intervals. Eight simultaneous2pp NI slots retain Bonferroni alpha.00625 and margin−.02, minimum20 components and zero-variance safeguards. Known family support10/0/17/17 means NI remains INCONCLUSIVE irrespective of outcomes; absent AF0-s61 is not dropped. Point-only source AUC/quantile diagnostics use all seeds, float64 linear [.1,.5,.9,.95] raw and primary-threshold-centered quantiles, no additional RNG/CI/winner. Baseline threshold panel remains REQUIRED_BUT_HOLD_PENDING_SEPARATE_BINDING_AND_ADMISSION; camera HOLD. No claim of established noninferiority, population utility or shortcut mechanism.

Reviewed read.py/payload.py and create-only journal source: A.admit validates separate GO_READER_READ, complete cohort, committed input/floor metadata and exact receipts before any claim; create-only/fsynced CLAIM precedes first candidate NPZ access. Fixed permanent ONCE and OUTPUT paths were absent at this review and were not created. Exceptions terminate the permanent journal; no retry, alternate journal, seed replacement or seed selection is allowed.

Important physical/logical boundary: a future released loader must deserialize the two admitted dev NPZ containers to verify hash/schema and exact own-fit equality, then returns only registered primary/calibration/evaluation IDs. It does not return historical191/camera arrays or interpret their metrics. This review did not deserialize either container. No weights are loaded by the reader.

## Required root release binding

Root may issue an exact-version GO_READER_READ only after its own check, using the READER_ROSTER hash above (not the original opaque roster hash), independent_review_path/hash for this report, and collector_review_path/hash for the prior b086df6ef2ff07669e0d143a578c4b9b6350e0a45b37f5b2061439b3b25b568c review that every envelope binds. Retain the exact source/binding/input-admission scope and a fresh pre-read absence check. This report grants eligibility for that root decision only, not actual read permission. No baseline/camera expansion or final adoption/publication GO is implied.
