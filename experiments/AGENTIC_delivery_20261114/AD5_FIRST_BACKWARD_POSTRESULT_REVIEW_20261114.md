# AD5 first-backward post-result technical review — 14 November 2026

Verdict: FAILURE PRESERVED; DIAGNOSTIC LOCALIZATION SUCCESSFUL. Batch6321768_401 failed1:0 at18:46:20CET; this is neither startup failure nor a smoke pass. No production/score read admitted. The pending-job interactive migration is now inapplicable: original ran and failed, so never forge CANCELLED_UNSTARTED or replay it through that adapter.

Independently recomputed8/8file sizes/SHA256 and inner5file SHA256SUMS in /mnt/t7/smad_next/coordination_20261114/ad5_firstbackward_collection_20261114T175157Z: allPASS, no missing files. Receipt AD5_FIRST_BACKWARD_POSTRESULT_VERIFICATION_20261114.json. Inspected exact technical logs only, after launch/source/prereg verification; test lists are empty and original config forces AD5_NO_TEST=1. No checkpoint/model/image/scientific score payload opened. This reviewer authored diagnostic instrumentation, so this technical interpretation is evidence-grounded but not an independent reapproval of its own new diagnostic source; next package needs a different pre-reviewer.

## Established observations

Reviewed launch commit2c6ee4b, exact script e090bd45f69cbc30b58ac1faa5c711cde672a75d842e944e5882a1c0eb4e7f92 and patcher04668b872d83171bf7a2ae909a7955f266fd44b51237805e0b629e955b309f0f. Instrumentation receipt confirms original trainer e905cc… and exact reviewed replacement f9cfa6…. H10095830MiB, driver595.112.07, Python3.9.25, torch2.0.1+cu118, CUDA11.8. Environment built46s; original reduced training list3311rows; one256×3×224×224float32 batch.

train_stdout.log SHA1b218a15ae7d096f1f2e9a635cb495abe6707989a61fc664767bc51acbae4bad contains, in order: INPUT, PRE_FORWARD, ENCODER_OK, HEADER_OK; no BACKWARD_COMPLETE marker. Synchronization establishes encoder and normalized-feature/header forward completed before backward failure. Anomaly reports **ScaledDotProductEfficientAttentionBackward0** and its forward call in exact packed LoRA layers.py511:

    attn_output = self.scaled_dot_product_attention(q,k,v,attn_mask,dropout_p,is_causal)

The first exception at instrumented trainer.py210 is loss_image.backward(): CUDA illegal instruction. Native frames identify at::native::_efficient_attention_backward and _scaled_dot_product_efficient_attention_backward_cuda. Therefore actual failing autograd path is memory-efficient SDPA backward; this is stronger evidence than mere enabled backend flags. Earlier speculation about clip_grad_norm is superseded: clipping and optimizer UPDATE are never reached. Optimizer objects were constructed unchanged, as prereview clarified.

Later SIGABRT/elastic childexit−6 occurs during fatal cleanup; parent child_exit.txt is1 and outer shell retains failure. No smoke/production success can be inferred. The cuDNN nvrtc workaround warning precedes successful encoder/header and is not established as causal.

## What remains a hypothesis

This localizes an operation/backend, not the underlying defect or a proven repair. It does not distinguish a torch2.0.1+cu118 efficient-attention/H100 kernel issue from data/layout-specific behavior or another low-level interaction. No assertion that upgrading CUDA, disabling all attention optimizations, removing clipping, changing batch/precision or switching hardware fixes training is licensed.

Minimal useful next computation: fresh-process synthetic SDPA default versus explicit math backend on SAME H100/cu118 stack with fixed source-derived B/16 shape/layout and generated tensors; no model/data/weights. New prospective package/namespace and independent pre-review are mandatory, not an automatic retry. See AD5_SDPA_PROBE_PREREG_20261114.md. Successful math probe only supports a candidate backend workaround; any production implementation change still needs its own amendment/equivalence review and actual complete gating smoke. If default does not reproduce or math also fails, retain that result and diagnose further; no fallback parameter search.
