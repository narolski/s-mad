# AD5 multi v1r1 independent postresult review — 2026-11-14

Reviewer: Astra / astra_compute_unblock_plan; independent of Sol producer. I previously independently reviewed its source/launcher and authored a separate conditional full-recovery proposal; neither role supplies automatic full-training admission.

**PASS36UPDATE_CHECKPOINT_SMOKE.** Job6323877 completes the registered narrow real36-update and own-checkpoint roundtrip technical gate. Root may adopt that result. Full training, L-arm recovery, scientific performance, production admission, default/math equivalence and underlying driver/kernel root cause are NOT ESTABLISHED.

## Integrity and execution

Exact collection `/mnt/t7/smad_next/coordination_20261114/ad5_real_math_multi_v1r1_results_20261114T200359Z/COLLECTION_VERIFIED.json` SHA115917baed20ad148c162957f16928e9438015af41fa07dc23a31a12df935307. Independently streamed opaque hashes and checked sizes for all252files/600169203bytes, including newly produced checkpoint artifacts without decoding them. Independently verified every237-entry worker SHA256SUMS (abcff990fbd00759489b78ab658b9f94671391f4eb11a2dc6a76a91ccea21b10). No MANIFEST_FAILURE or other failure receipt exists in this collection; supervisor final snapshots all stable and hash-matched. Checks artifact AD5_MULTI_V1R1_POSTRESULT_CHECKS_20261114.json SHA f4d00c6835c4d6574983e989b6ae4a4d4cc42ac4adbbf35850d40a3490583205 records exact verification counts and ranges.

Source manifest6ebbe3a0b1ea18dd449a8561f8d79baf55667329d1e239035cfc9efaadec6418: all40files independently match working source AND Git objects at a5a4876245c68cfe17c93e48a65c6713d1452fda. Root releasedf08e6fad4a275a140f4fff951c751fb14ec56d8c45b232e5500fc536b61a667 binds prereg085053c4..., independent prereview588e30d8c6ce1a82a63aaece36b323df46bc29598abe961b129b68a3fcc120bc, exact source, clean-owned-source and site receipts; every referenced receipt hash and claim release digest matches. Root release names root as reviewer; the independently authored review bytes are Astra's pinned document. This metadata naming does not change review authorship.

Collected native accounting:COMPLETED0:0,21:12:26–21:14:10CET,104s,one H100/8CPU/120G. Child, supervisor, worker, node and srun all exit0. Supervisor has no errors/reason/TERM/KILL and eligibility is corroborated by complete records, not inferred from exit0.15min allocation and150G local storage are requested resource bounds;150G is not measured quota. Early node-entry720s timing is not proof of native allocation age. Native accounting here is a collected receipt, not a fresh reviewer cluster query.

## All36 steps and original lifecycle

All36 ordered step directories verified:1800 exact expected gradient tensor records (48visual q/v LoRA+2header each step), all present/finite; each group has nonzero gradients. At step1,24 LoRA-A gradients are zero, consistent with B initialization; all model gradient norms are nonzero in subsequent35steps. Zero first-step A gradient is not missing-gradient failure, and parameter changes under AdamW do not establish nonzero data gradients by themselves.

Every expected parameter remains finite with optimizer step equal to its exact step1..36; every group changes; all floating model/header state and optimizer moments are finite at each step. Both preclip group norms remain finite/positive: model[0.008406814187765121,0.013327793218195438],header[0.06956074386835098,0.17900118231773376], below unchanged max5. Each loss-finite assertion passes, no numeric loss is used for selection. All36 backend receipts explicitly flash=false/math=true/memory_efficient=false.

Each batch has256 exact matching actual/original sampler indices, valid range[0,3310], consistent canonical IDs, recomputed order SHA, float32[256,3,224,224] images and float32 targets. Each epoch has3072 distinct visited indices over12 batches; three epochs total9216 training sample exposures. Labels were checked against target by pinned runtime, not independently reloaded by reviewer. Original sampler seed0/epoch and nonmutating enumeration CPU-RNG assertions are source-bound runtime gates; no RNG replay, transformed-pixel equality or uninstrumented trajectory equivalence was claimed.

Epoch receipts0/1/2 show12/24/36 updates, scheduler completion and original save callbacks. No checkpoint at epochs0/1; final pair present at2. Source inverse-AST proof preserves original two zero_grad per batch, scheduler/log/TensorBoard/save/close flow. Counts of6 scheduler steps,72 zero_grad calls,36 logging/TensorBoard calls and3 save callbacks are supported by source flow plus completed receipts, not a separate serialized scheduler-state reconstruction. Legacy printed38 is not completed count.

Actual Python3.9.25,torch2.0.1+cu118/CUDA11.8,H100,ARM B/ViT-B16/seed401,3311rows,global256/world1/FP32/accumulation1 and original LoRA/BCE/AdamW configuration agree with setup/log/source. Log test paths and test_data are empty. Retained warning about cuDNN nvrtc workaround, TypedStorage and launcher deprecations did not become failures and are not erased or labelled causal.

## Exact own-checkpoint gate

CHECKPOINT_ROUNDTRIP SHA8f09bbf59700b50fbbe073ccdae29dd2eb1cf78697d52ae011432adc251f8b15 attests only newly produced3_backbone.pth SHAa5b7f91f588fffc7e518cba8598453fcd991d15db070b19b49eec3fa7ccbd7ba and3_header.pth SHA47cf8e1f4191870bbba0734fc91226e2d66d7f1e4abda148026261e5e1393e10. Both opaque copied artifacts independently match these hashes and supervisor snapshots. Pinned runtime performed weights_only load, strict key/shape/dtype/state byte comparisons, train/unmerge before reload, and then eval/math/noTTA on the same retained last training batch. Receipt confirms exact float32[256,2] logit-byte equality, digestb00053c82024bf12ce539dca300e67ce9b3a962cc791b8a237c96f01f2a0e95c; no numeric logits exported. Reviewer did not load checkpoint tensors or independently repeat model inference. This is a source-attested executed gate with opaque artifact integrity, not an inference from file existence.

MULTI_RESULT SHA783ca498bf9918e677cfaabfd2a68beea0f071e59669387c6f8bcbdc4874071a confirms36updates per optimizer/three epochs. Peak CUDA allocation37251569152bytes (34.693GiB); instrumented35.379740632s includes observation and final checkpoint roundtrip, not isolated steady-state throughput.104s native includes setup/teardown. Neither establishes full-fit runtime or long-horizon numerical stability.

## Consequence and retained limits

This closes only the reviewed B reduced-list multi-update/save/reload smoke. Preserve prior illegal-instruction failures6310087/6310124/6310126/6319495/6321768 and synthetic/default-path results; preserve original v1 R1HOLD and v1r1 repair history. No failed attempt becomes a pass; no evidence establishes default-backend mathematical/bitwise equivalence or low-level root cause.

The existing `full_math_recovery_proposal_20261114` remains a prospective source-only proposal requiring a DIFFERENT independent methodology/source reviewer, complete fullCSV/converter metadata pins, remaining-budget and runtime/resource reconciliation, a new full producer with40epoch/6200update semantics, clean committed inputs and fresh root release. B smoke does not license L. Full scorer/converter/reference checks and scientific performance reads remain separately gated. No full producer was authored or submitted in this postreview.

Scope: exact admitted technical JSON/log/source/release/journal records and opaque artifact hashes only. No image/data/model/checkpoint decoding, candidate/scientific archive, GPU, scheduler query or reader rerun.
