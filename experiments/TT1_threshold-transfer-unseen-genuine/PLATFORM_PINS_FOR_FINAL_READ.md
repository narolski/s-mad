# Platform pins for the sealed final read

This list is for the owner of the final benchmark protocol. It comes from TT1: review F10
(`experiments/reviews/REVIEW_TT1_20261113.md`), gates DGX / tt1a / tt1b / tt1c, and amendments H-new-5 and TT1-D1 to D3.
Written 13 Nov 2026.

## Rule

A score or threshold may be compared with another only if both were produced on the same stack, as defined below. A
pre-registered gate must show this before any benchmark row is scored.

## Why (measured in TT1)

**The decoder and resize are not the problem.** The decoded image, the resized image and the input tensor are
bit-identical between the DGX stack (torch 2.12.1+cu130, Pillow 12.2.0, GB10) and the A100 stack (torch 2.2.1, Pillow
10.2.0). Source: `diag_stack_compare.json`.

**The network computation is the problem.** On the GB10, the same network and the same input tensor give logits that
differ from the A100 by 0.061-0.088 on mid-range rows. Source: `diag_kernels.json`, H-new-5.
- No TF32 setting or attention backend removes this. The best of six settings still differs by 0.088.
- The GB10 / torch 2.12 stack is therefore EXCLUDED as a scoring platform for any comparison with A100-made scores.

**Floor rows hide platform differences.** Rows with logits near the head floor barely move, so a gate built only from
them can pass while mid-range rows differ.

| Rows (DGX against A100) | Max \|Δ\| |
|---|---|
| Camera photos (floor rows) | 0.005 |
| FFHQ genuine (mid-range rows) | 0.088 |

**Batch composition changes the last bits on the same A100 stack.**
- The same rows scored in other batches of 64 gave 16-25 of 3,000 rows different by at most 2.2e-5 (tt1a).
- Scored in the original order and batching, they were byte-identical (tt1b, tt1c: 0 of 3,000).

**TF32 matters near the decision boundary.** Camera logits stored by pn1_score.py (TF32 on) against rescore.py (TF32
off, PyTorch defaults) differ by up to 0.035. The worst row is Bn_s401 ar1_000377, stored −0.133, which is close to
the own rule. The result was deterministic: tt1b and tt1c gave identical numbers.

## Pins (every item recorded and asserted by the scoring job before any row is scored)

1. **GPU:** model and compute architecture. TT1's scoring-equivalent stack is NVIDIA A100-SXM4 (sm_80), 40 GB or
   80 GB. PCIe 40 GB was byte-identical in PN1 amendment 14. Record the GPU UUID per run.
2. **Driver:** recorded. TT1 tt1c used 595.91.07; PN1 hosts are recorded in their gpu.txt.
3. **CUDA runtime:** 12.1 (image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`).
4. **torch build:** exactly 2.2.1 (the image's build). torchvision as in the image, held by constraints.
5. **cuDNN version:** `torch.backends.cudnn.version()` recorded. TT1 did not record it; the image tag says cuDNN 8.
   Record it in the final job.
6. **Python packages:** timm 1.0.27, huggingface_hub 0.36.2, safetensors 0.8.0, numpy 1.26.4, pyyaml 6.0.3,
   Pillow 10.2.0 (pip pins of `src/PN1/rented/remote_setup.sh`). Python 3.10.13 (image).
7. **TF32:** set explicitly for both `torch.backends.cuda.matmul.allow_tf32` and `torch.backends.cudnn.allow_tf32`.
   - It must equal the setting that produced any stored score or threshold the read is compared with.
   - pn1_score.py (training-time scoring, τ thresholds) used True / True.
   - rescore.py uses the torch 2.2.1 defaults (matmul False, cuDNN True).
   - If thresholds come from pn1_score.py runs, score with TF32 on, or recompute the threshold on the final stack
     under a pre-stated rule.
8. **Attention backend:** timm uses fused attention (`F.scaled_dot_product_attention`), and on A100 torch selects the
   kernel. Pin it explicitly (for example `torch.nn.attention.sdpa_kernel`) or record the default and keep it
   identical.
9. **Precision:** float32, no autocast, no bf16 or fp16. The model is in eval mode.
10. **Determinism:** `torch.backends.cudnn.benchmark = False`; deterministic algorithms where available (record the
    flag).
11. **Batching:** batch size 64, list order fixed by the pinned list (sha256). Data-loader workers do not change
    batch composition; the order does. Rows compared byte-for-byte with stored scores must be scored in the same
    order and batching as the run that stored them (TT1-D2).
12. **Hashes:**
    - rescorer `src/PN1/rescore.py` 6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e;
    - `common.py` b5d42a99cae4f1f2f6dd2965d4973c8f9f65cf73212ffd0a17af4daee33bbea8;
    - base weights `vit_base_patch16_clip_224.openai.safetensors`
      4b8699299b1e8997753c64b052ba32031449d5d853f55a039148560ee02b820f;
    - each network's `last_trainable.pt` and `meta.json` (and the result tar sha256);
    - the scoring list and every image (SHA256SUMS).
13. **Gate before any benchmark row:**
    - **Rows:** previously scored rows that span the logit range. Include floor rows (camera photos) AND mid-range or
      upper rows (for example FFHQ genuine and FFHQ morphs), each scored in the order and batching of the stored run.
    - **Criteria:** fixed in advance, for example byte identity on rows stored by the same script and batching, plus a
      tolerance with zero decision changes on rows stored by another script.
    - **Per network:** a network that fails is not scored. A deciding network that fails makes its decision "not
      available"; it is never read on one seed.
    - **On failure:** stop, write RELEASE + FAILED after verified copies, report. No tolerance is changed after
      seeing a gate.
14. **Copies:** the result tar and logs verified by sha256, with a second local copy, before the machine is released.
    Each run's tar is named by its lease.
