# Frozen Sb networks, seeds 403-407 (the paper's method)

These are the five networks frozen by the author's ruling of 13 Nov 2026 and read once on corrected MAD22
(experiments/FINAL_sealed-benchmark-read). They are the "Sb (Ours) (5 seeds)" row of Table 1.

- Architecture: CLIP ViT-B/16 (timm `vit_base_patch16_clip_224.openai`, public weights) with LoRA; training
  configuration in each `meta.json`.
- `last_trainable.pt`: the trainable parameters only (LoRA adapter and head), about 0.3 MB per network.
- `SOURCE_TARS_SHA256SUMS`: checksums of the full result archives (weights, scores, logs) in
  `/mnt/t7/smad_next/PN1/results_fs/`; they match the checksums registered in the sealed-read prereg (lines 340-344).
- `TRAINABLE_SHA256SUMS`: checksums of the weight files in this folder.

Training data: FRGC and color FERET photographs and morphs built from them; check the dataset terms before any
public release of these weights.
