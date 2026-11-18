# Network weights kept in this repo

Trainable parameters only (LoRA adapter and head, 0.3-0.8 MB each) with `meta.json`, `train.log` and the checksum of each full result archive (`SOURCE_TARS_SHA256SUMS`; archives with scores stay on the data drive). The CLIP base weights are the public timm releases.

| Folder | Contents | Networks |
|---|---|---|
| sb_frozen_s403-407 | the paper's frozen method (Table 1) | 5 |
| arms_fresh_s403-407 | A, B, Sp; the Sb seeds are in sb_frozen_s403-407 | 13 |
| arms_dev_s408-412 | A, AS, B, Sb, SbH, SbS, SbZ, Sp | 40 |
| count_balanced_s408-412 | batch C | 15 |
| b2_s408-412 | batch B2 | 25 |
| morph_free_b16 | AD4 m3mf + label-permuted control | 10 |
| morph_free_l14 | AD4 m3lmf + label-permuted control | 10 |

Retrained comparators (MADation, MixFaceNet-MAD, SelfMAD; hundreds of MB each) are not in git; see the Google Drive folder noted in NOTEBOOK.md.

Training data are FRGC and color FERET photographs (and SMDD for the morph-free networks); check the dataset terms before any public release.
