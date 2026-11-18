# Source-only cross scorer and NEXT adapter plan

This packet deliberately contains no executable model/scientific reader. It freezes design.py, spec order, masks and generated CPU fixtures so methodology and missing provenance can be reviewed now. Future production scorer needs a separate exact source digest and independent prereview.

## Exact derivative boundary

rz1_score.main -> rz1_patch.apply(code) -> common.build_run_model(meta) -> common.build_model -> archs_a12.build_a12 -> timm pretrained visual tower. Set RZ1_RES512='1' BEFORE patch/app/build; CLIP_RES512 permits img_size512. Original timm checkpoint filter bicubic-resamples14×14positions to32×32; first-step source guard expects1025tokens and1e-5positional agreement. Preserve original meta LoRA reconstruction via common.lora_settings and apply_lora, original pretrained weights and normalization. Do not replace this with another CLIP implementation or interpolate a trained512embedding again.

Original archived scoring producer writes last_trainable.pt, not a fullcheckpoint. Rebuild frozen tower from exact pinned pretrained weights; load trainable overlay weights_only=True. Require state keyset exactly expected trainable set and missing keys exactly frozen state, zero unexpected; source-derived approach in rz1_rescore.py. Preserve buffers and norms according to exact original source; missing pretrained/buffer provenance is HOLD. last_pt.sha256 is an archived descriptor, not proof the new serialization hashes identically. Do not save a rebuilt checkpoint.

Future cross-only scorer retains ONLY original score(rows,tta=False,spec) path: rz1_patch.set_spec -> common.ImageItems in fixed metadata order -> DataLoader(bs64,workers7,shuffleFalse,original defaults) -> model.eval/no_grad -> C.forward_logit(model,x)[0].float -> float32 rows. Original matmul/cudnn TF32 flags true. No autocast, augment, sampler, training, TTA, scoring eval/train/TT1/MEDS populations, train_acc_rule0, torch.save or image saving. Iterate all14specs at512. Output cross IDs/specs/logit14×13771 float32 plus exact source/checkpoint/input descriptors and timing/memory technical receipt. No arbitrary meta dump.

Reference acquisition is separately authorized selective array access: original scores_eval and scores_tt1 ID/logit only, match INPUT_BINDING native_reference_id_mapping, exact metadata manifest hashes/IDorder/schema/finiteness; no other scientific fields read. First native cross-only pass must equal those same-ID original float32 logits bytewise. Gate is NOT yet possible without array access. Batchcontext differences may cause failure; hold with no tolerance fallback. Proposed reconstruction and expected IDcoverage need reviewer/root adoption first.

Avoid calling rz1_score.main wholesale (would score four non-cross populations, write weights and train accuracy). Avoid rz1_rescore.main (AB1-specific extraction/fullcheckpoint output). Reference only their pinned source logic in a new derivative. Any technicalcollector must precede live payload grant; no generic info.json dump since train_acc_rule0 is scientific.

## Adapter contract to implement after independent adoption

Input exact5seed roster + perseed supplement archive/hash + exact14spec/manifest/mask/inputsourcepins + native equality receipt and executedsource/runtime. Validate all associations/uniqueIDs/schema/float32shape/finiteness before calculation. Same-ID original reference gate mandatory. Compute only registered flagshare changes/kappa with design order. Missing seed has explicit failed/unread status; denominator5. Keep comparator/floor/NI/other native eligibility untouched. Canonical NEXT is not patched now. Later integration delta must be independently reviewed and bind the original once-only policy.

## Required next admissions

1. Root adopt methodology/spec/masks/native-reference reconstruction after independent review.
2. Separate technical scope supplies exact per-model meta, frozenweight/trainable descriptors, executed versions/driver/guards/scorer and original output-member hashes, as allowlisted in REQUIRED_TECHNICAL_FIELDS_PROPOSAL.json. Opaque bodyhashes do not permit decoding.
3. Pin actual scorer/adapter source and fixtures, execution resource/timing envelope; independent code review.
4. Root separately authorize exact checkpoint/image/native-reference access and bounded GPUworker, then later NEXT once-only scientific admission. No existing plan or packet itself grants these.
