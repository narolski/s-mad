# Genuine pools of the threshold-transfer experiment (TT1)

raw_manifest.csv sha256 `a7aebe163328d12652c512fcb169152e7c3c4c31f63833d91e1ae3d63dd12168`; aligned_manifest.csv sha256 `8b3c6fa932ac24c13a086984468539ba841f2facc1ac883be34c89b1c6971bef`. Enlargement, IED and border: aligned images only. Sharpness and greyscale: all kept photos (raw images).

## Per source

| Source | Photos kept | Persons / pseudo-identities | Aligned share | Failures (no face / frontal filter) | Median source IED (px) | Median enlargement to 132 px (p10-p90) | Median Laplacian variance (p10-p90) | Greyscale share | Median black-border share of the 512 frame |
|---|---|---|---|---|---|---|---|---|---|
| replay_attack | 200 | 50 | 1.000 (200) | 0 / 0 | 76.14 | 1.734 (1.656-1.813) | 21.6 (15.3-32.8) | 0.000 | 0.4264 |
| msu_mfsd | 70 | 35 | 0.929 (65) | 1 / 4 | 76.38 | 1.728 (1.647-1.806) | 73.9 (20.6-321.7) | 0.000 | 0.4255 |
| oulu_npu | 989 | 55 | 1.000 (989) | 0 / 0 | 77.08 | 1.713 (1.65-1.777) | 643.9 (308.1-1252.5) | 0.000 | 0.4384 |
| casia_fasd | 150 | 50 | 1.000 (150) | 0 / 0 | 76.57 | 1.724 (1.656-1.841) | 86.4 (37.3-301.5) | 0.000 | 0.428 |
| lfw | 7701 | 4859 | 0.784 (6035) | 0 / 1666 | 37.59 | 3.511 (3.347-3.746) | 198.5 (90.8-441.3) | 0.004 | 0.4008 |
| calfw | 6098 | 3098 | 0.818 (4987) | 2 / 1109 | 37.61 | 3.51 (3.356-3.721) | 537.9 (244.3-1085.3) | 0.075 | 0.4021 |
| cfp_ff | 4737 | 1586 | 0.998 (4726) | 1 / 10 | 38.1 | 3.465 (3.25-3.678) | 1408.1 (618.9-2906.2) | 0.016 | 0.5292 |
| agedb_30 | 5296 | 2338 | 0.743 (3937) | 0 / 1359 | 37.52 | 3.518 (3.366-3.7) | 837.7 (228.7-2310.7) | 0.275 | 0.4006 |

## Per family

| Source | Photos kept | Persons / pseudo-identities | Aligned share | Failures (no face / frontal filter) | Median source IED (px) | Median enlargement to 132 px (p10-p90) | Median Laplacian variance (p10-p90) | Greyscale share | Median black-border share of the 512 frame |
|---|---|---|---|---|---|---|---|---|---|
| replay_attack | 200 | 50 | 1.000 (200) | 0 / 0 | 76.14 | 1.734 (1.656-1.813) | 21.6 (15.3-32.8) | 0.000 | 0.4264 |
| msu_mfsd | 70 | 35 | 0.929 (65) | 1 / 4 | 76.38 | 1.728 (1.647-1.806) | 73.9 (20.6-321.7) | 0.000 | 0.4255 |
| oulu_npu | 989 | 55 | 1.000 (989) | 0 / 0 | 77.08 | 1.713 (1.65-1.777) | 643.9 (308.1-1252.5) | 0.000 | 0.4384 |
| casia_fasd | 150 | 50 | 1.000 (150) | 0 / 0 | 76.57 | 1.724 (1.656-1.841) | 86.4 (37.3-301.5) | 0.000 | 0.428 |
| lfw_calfw | 13799 | 7957 | 0.799 (11022) | 2 / 2775 | 37.6 | 3.51 (3.351-3.733) | 309.3 (110.3-830.1) | 0.035 | 0.4015 |
| cfp_ff | 4737 | 1586 | 0.998 (4726) | 1 / 10 | 38.1 | 3.465 (3.25-3.678) | 1408.1 (618.9-2906.2) | 0.016 | 0.5292 |
| agedb_30 | 5296 | 2338 | 0.743 (3937) | 0 / 1359 | 37.52 | 3.518 (3.366-3.7) | 837.7 (228.7-2310.7) | 0.275 | 0.4006 |
| all | 25241 | 12071 | 0.836 (21089) | 4 / 4148 | 37.83 | 3.49 (3.253-3.707) | 508.3 (130.4-1827.5) | 0.080 | 0.4166 |

