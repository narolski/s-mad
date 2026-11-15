# Follow-ups (c): landmark-ladder morphs (H-new-5) and held-out generator renders (H-new-4), ViT-B/16 networks (AD4 Amendment 4), post hoc follow-up

Flag on the networks: not reproduced on this stack. The ladder images are the landmark ladder's (AR1) own 512 frames, not our benchmark frames. The networks were trained only to flag shrink-and-enlarge copies of synthetic faces.

Unblanked re-score gate: AD4_m3mf_s401 MISS (max |dAUC| 0.0009, min tau 0.988), AD4_m3mf_s402 pass (max |dAUC| 0.0004, min tau 0.991), AD4_m3mf_s403 pass (max |dAUC| 0.0004, min tau 0.992), AD4_m3mf_s404 MISS (max |dAUC| 0.0012, min tau 0.987), AD4_m3mf_s405 MISS (max |dAUC| 0.0008, min tau 0.989), AD4_m3perm_s401 pass (max |dAUC| 0.0001, min tau 1.000), AD4_m3perm_s402 pass (max |dAUC| 0.0001, min tau 1.000), AD4_m3perm_s403 pass (max |dAUC| 0.0001, min tau 0.999), AD4_m3perm_s404 pass (max |dAUC| 0.0002, min tau 0.999), AD4_m3perm_s405 pass (max |dAUC| 0.0001, min tau 0.999), AD4_m3zero_s401 pass (max |dAUC| 0.0000, min tau 1.000)

The three misses (Kendall tau 0.987 to 0.989) are probably ties and near-ties at the saturation floor, where small numerical differences between the GB10 and the rented cards reorder scores; they are reported as misses and not rescued (review, Subject 2).

## H-new-5: incomplete (2 of 5). Morph-free seed-mean gap AUC(R4 vs R0) − AUC(R3 vs R0): OpenCV 0.009 [-0.008, 0.023], FaceMorpher -0.006 [-0.029, 0.015] (rule: at most 0.1 for both tools supported).

| tool | network | R3 vs R0 | R4 vs R0 | gap | R4 vs R3 | R3 vs R2w | R4 vs R2w |
|---|---|---|---|---|---|---|---|
| opencv | `AD4_m3mf_s402` | 0.911 | 0.919 | 0.008 | 0.520 | 0.847 | 0.860 |
| opencv | `AD4_m3mf_s403` | 0.895 | 0.904 | 0.009 | 0.504 | 0.826 | 0.835 |
| opencv | `AD4_m3perm_s401` | 0.553 | 0.608 | 0.054 | 0.554 | 0.544 | 0.597 |
| opencv | `AD4_m3perm_s402` | 0.647 | 0.722 | 0.074 | 0.584 | 0.637 | 0.712 |
| opencv | `AD4_m3perm_s403` | 0.554 | 0.504 | -0.050 | 0.448 | 0.526 | 0.475 |
| opencv | `AD4_m3perm_s404` | 0.385 | 0.334 | -0.051 | 0.442 | 0.397 | 0.346 |
| opencv | `AD4_m3perm_s405` | 0.519 | 0.507 | -0.012 | 0.488 | 0.524 | 0.513 |
| opencv | `AD4_m3zero_s401` | 0.490 | 0.503 | 0.013 | 0.514 | 0.492 | 0.505 |
| facemorpher | `AD4_m3mf_s402` | 0.866 | 0.864 | -0.002 | 0.484 | 0.845 | 0.842 |
| facemorpher | `AD4_m3mf_s403` | 0.835 | 0.826 | -0.009 | 0.469 | 0.820 | 0.810 |
| facemorpher | `AD4_m3perm_s401` | 0.548 | 0.610 | 0.062 | 0.563 | 0.544 | 0.606 |
| facemorpher | `AD4_m3perm_s402` | 0.654 | 0.734 | 0.080 | 0.593 | 0.648 | 0.729 |
| facemorpher | `AD4_m3perm_s403` | 0.545 | 0.491 | -0.054 | 0.444 | 0.539 | 0.485 |
| facemorpher | `AD4_m3perm_s404` | 0.376 | 0.335 | -0.041 | 0.453 | 0.380 | 0.339 |
| facemorpher | `AD4_m3perm_s405` | 0.516 | 0.507 | -0.009 | 0.491 | 0.509 | 0.500 |
| facemorpher | `AD4_m3zero_s401` | 0.488 | 0.501 | 0.013 | 0.514 | 0.494 | 0.508 |

## H-new-4: incomplete (2 of 5). SMDD evaluation renders below the FRLL genuine median in 2 of 2 morph-free seeds.

Reading (review `REVIEW_PN1_TIER1_20261112.md`, Subject 2): **indistinguishable: both at the trained floor.** The −0.03 and −0.05 logit differences lie inside a floor whose 5th to 95th percentile spans about 0.03, and no interval was computed; they are not evidence for or against H-new-4.

| pool | network | n | pool median logit | FRLL genuine median logit | difference |
|---|---|---|---|---|---|
| smdd_eval | `AD4_m3mf_s402` | 1000 | -3.65 | -3.62 | -0.03 |
| smdd_eval | `AD4_m3mf_s403` | 1000 | -3.67 | -3.62 | -0.05 |
| smdd_eval | `AD4_m3perm_s401` | 1000 | -0.00 | 0.00 | -0.01 |
| smdd_eval | `AD4_m3perm_s402` | 1000 | -0.01 | -0.00 | -0.00 |
| smdd_eval | `AD4_m3perm_s403` | 1000 | -0.01 | -0.02 | 0.01 |
| smdd_eval | `AD4_m3perm_s404` | 1000 | -0.00 | -0.01 | 0.01 |
| smdd_eval | `AD4_m3perm_s405` | 1000 | 0.01 | 0.04 | -0.04 |
| smdd_eval | `AD4_m3zero_s401` | 1000 | 0.00 | -0.00 | 0.01 |
| h3 | `AD4_m3mf_s402` | 423 | -1.76 | -3.62 | 1.85 |
| h3 | `AD4_m3mf_s403` | 423 | -2.72 | -3.62 | 0.91 |
| h3 | `AD4_m3perm_s401` | 423 | -0.00 | 0.00 | -0.00 |
| h3 | `AD4_m3perm_s402` | 423 | -0.00 | -0.00 | 0.00 |
| h3 | `AD4_m3perm_s403` | 423 | -0.01 | -0.02 | 0.00 |
| h3 | `AD4_m3perm_s404` | 423 | -0.01 | -0.01 | 0.00 |
| h3 | `AD4_m3perm_s405` | 423 | 0.01 | 0.04 | -0.04 |
| h3 | `AD4_m3zero_s401` | 423 | -0.00 | -0.00 | -0.00 |
| h4b | `AD4_m3mf_s402` | 338 | 3.47 | -3.62 | 7.09 |
| h4b | `AD4_m3mf_s403` | 338 | 3.54 | -3.62 | 7.16 |
| h4b | `AD4_m3perm_s401` | 338 | 0.01 | 0.00 | 0.00 |
| h4b | `AD4_m3perm_s402` | 338 | -0.00 | -0.00 | 0.00 |
| h4b | `AD4_m3perm_s403` | 338 | 0.00 | -0.02 | 0.02 |
| h4b | `AD4_m3perm_s404` | 338 | -0.00 | -0.01 | 0.01 |
| h4b | `AD4_m3perm_s405` | 338 | -0.00 | 0.04 | -0.05 |
| h4b | `AD4_m3zero_s401` | 338 | -0.01 | -0.00 | -0.01 |
