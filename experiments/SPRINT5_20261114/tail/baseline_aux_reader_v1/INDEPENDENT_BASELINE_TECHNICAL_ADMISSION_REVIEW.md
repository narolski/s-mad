# Independent actual baseline auxiliary technical admission review — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of Sol collector/reader author.
Decision: **GO_BASELINE_AUXILIARY_TECHNICAL_INPUTS_ONLY**. Same-baseline existing runtime/bytegate metadata reuse is supported for the exact archive/member/source chain below. This review does not issue the auxiliary scientific release, decode arrays or establish baseline NPZ ID/schema/finiteness.

## Exact pins

- Actual technical RECEIPT.json:619b555568d131d7c4681bfeb2d50f5225e241b1edeab3737b07e28973e3f4ae.
- ROOT_TECHNICAL_RELEASE.json:1aba530e4e80fc4b40a31b84bdab8481efc6f6ed492766216661fc6d6414bad0.
- ROOT_INPUT_ADMISSION.json:1018fce769719e45fdc627e0fbcecbba28329915b4a9e55b8513000359150992.
- Reader/collector source manifest692b0cde2e47fc62133fca3f58a4f4d4ff6c7357d0096d6e93b2ee4b6f30054a.
- Input binding4b5861f8b506c68b73cef8bf4d95b4093a9822971a8d85728fe370c9d36c5ae4.
- Independent code/input reviewee36c91c91fd2609a9eaa78f07edbabad9a591b9f7601f27cbabf78bf154dd85.
- Policy adoptiona227479a3f28e7012ab6a41e4dc54cb478a8f769d683d379676a53c3ca5b3ca2.
- BASELINE_GATE_REUSE_CHAIN.json:db2c3b714bff37908f494013f0ab9ceeb804682a5a2cd77b764e6240eee723a8.
- Independent ASTRA_ACTUAL_BASELINE_TECHNICAL_CHECKS_20261114.json:3d5031d7ee650d0d3c7355efd63f2392b7d7abfa717a3c38e044b9229a0f0956.

## Actual checks: PASS

Rehashed receipt, source manifest/members, release and all baseline gate-chain referenced sources/receipts. Actual validate_release for technical scope and technical_receipt validation passed. Actual metadata.validate(require_committed=True) passed604pins with real Git checks. Every source file matches adopted commit45a62dba67bebbffe704b46b363d571fda119be1 byte-for-byte. The earlier uncommitted-input gate is now closed for these bytes.

Actual collector receipt identifies original AB1_Sb_s408 archivea84b551f2f18c51898213f4932965f89b88fe7eac0398ac28cd37c04e4b3b0aa and exact AB1_Sb_s408/scores_eval.npz. Reviewed capture enforces unique regular member and bounded size, then streams its opaque hash. Recorded size3,150,518bytes; member SHA25683e3bf359ea39e5b373c453d578c610a7798041efa0d345e7fbf5fc710523a25. Receipt binds technical release/source/input/policy and five fixed metadata-member digests. No FAILURE.json is present. This review validates the captured receipt and frozen capture logic; it does not independently reopen/recompute archive or member bytes.

Source identity PASS corresponds to seed408/CLIP B16 MADation/res224, original21,277dev rows/limit0 and pinned pack/overlay, as enforced in reviewed collector. Runtime receipt reports torch2.11.0+cu128,NVIDIA H100 and scorer common.py hashb5d42a99cae4f1f2f6dd2965d4973c8f9f65cf73212ffd0a17af4daee33bbea8 matching binding. Precision/TF32 statement is grounded in pinned scorer source, not inferred from a new environment process. Checkpoint hash01b8c103d6f835699cea1e689c48859c3eba3057181f290a03a790a0cf8b8ccf is metadata only; no independent checkpoint rehash.

## Existing same-baseline gate reuse: supported, not a new gate

Existing source manifest5e25d43ce54763011b85f669826c3d375ffdda4270a7a2ac545a40b48675beb5 and run.sh/check_gate.py hashes match bound source-chain receipts. run.sh explicitly hashes original AB1_Sb_s408.tar to a84b..., extracts that archive's meta/last_trainable/scores_eval, and passes that SAME scores_eval.npz as --expect-eval to the baseline battery before the training-only pass. Its technical gate checker requires reference byte_identical/zero differences/max_abs0 and own-fit passed/21,277common/zero differences.

Existing root admission90e5a49bda1383d73a053d9c66869976d3a291f4a35dc6c86d970a54199ec2ea records successful job6321187, strictreference and21,277ownfit bytegatePASS, and no scientific dev-score read. Training release4d6cec6bedbc538342859c53e602ef9e3831b847f51bc0f3ccaff756c9329969 and gate-chain proposal receipts remain pinned. The later training-only archive/reference hashes are distinct outputs, not replacements for original a84b... baseline; source linkage connects their gate evidence to that original member. Together with actual original runtime/source capture, this supports narrowly reusing the admitted SAME baseline gate evidence. No gate was rerun, no array comparison performed, and no new raw-gate-file verification is claimed.

For root's technical admission fields, runtime_and_bytegate_status=PASS_SAME_BASELINE_ADMITTED_METADATA and same_baseline_existing_gate_reuse_authorized=true are warranted only with exact receipt/gate-chain/source pins above.

## Remaining scientific boundary

Baseline actual ordered IDs, embedded manifest, shape/dtype and logit finiteness remain UNKNOWN_UNTIL_AUXILIARY_CLAIM. Opaque member hash and successful technical capture are not those numerical validations. Reader retains explicit full-container serialization validation only after its permanent auxiliary claim; numerical outputs are restricted to538baseline/468candidate IDs. Original primary chain remains byte-bound and unchanged; auxiliary ONCE/OUTPUT are currently absent.

Root may issue a hash-bound technical-input admission referencing this review, then independently decide the separate exact auxiliary scientific release under adopted after-primary point-only policy. No CI/NI/winner, camera/sealed expansion or primary reread is authorized here. Unsigned skeleton remains a proposal; reviewer has not signed or issued a release.

No actual archive/header/member/NPZ/checkpoint or scientific scores were opened, no collector/reader/claim executed, and no GPU/cluster/scheduler action performed. Original sources and other agents' files remain unchanged.
