# PN1 tier0: key reads (named seed 401; all seeds in tier0_key.csv)

| read | clip224_A0_s401 | clip224_B0_s401 |
|---|---|---|
| a R2w_vs_R4_opencv | 0.999 [0.998, 1.000] | 0.999 [0.997, 1.000] |
| a R2w_vs_R4_opencv excess | +0.123 [+0.090, +0.154] best=b3_.125-.25 0.876 | +0.123 [+0.090, +0.154] best=b3_.125-.25 0.876 |
| a R2w4_vs_R4_opencv | 0.999 [0.997, 1.000] | 0.999 [0.996, 1.000] |
| a R2w4_vs_R4_opencv excess | +0.125 [+0.091, +0.156] best=b3_.125-.25 0.875 | +0.124 [+0.091, +0.156] best=b3_.125-.25 0.875 |
| a R2w_vs_R4_facemorpher | 0.999 [0.998, 1.000] | 0.999 [0.998, 1.000] |
| a R2w_vs_R4_facemorpher excess | +0.120 [+0.087, +0.150] best=b3_.125-.25 0.880 | +0.120 [+0.087, +0.150] best=b3_.125-.25 0.880 |
| a R2w4_vs_R4_facemorpher | 0.999 [0.998, 1.000] | 0.999 [0.999, 1.000] |
| a R2w4_vs_R4_facemorpher excess | +0.114 [+0.082, +0.144] best=b3_.125-.25 0.885 | +0.114 [+0.082, +0.144] best=b3_.125-.25 0.885 |
| b R0_61_vs_R4_opencv | 0.998 [0.996, 1.000] | 0.998 [0.995, 1.000] |
| b R2w_61_vs_R4_opencv | 0.999 [0.996, 1.000] | 0.998 [0.995, 1.000] |
| b R0_61_vs_R4_facemorpher | 0.999 [0.998, 1.000] | 0.999 [0.998, 1.000] |
| b R2w_61_vs_R4_facemorpher | 0.999 [0.998, 1.000] | 0.999 [0.998, 1.000] |
| c shift R0->R0_61 (SD) | +0.222 [+0.175, +0.267] | +0.182 [+0.127, +0.243] |
| c shift R0->R0_112 (SD) | +0.071 [+0.031, +0.110] | +0.097 [+0.048, +0.148] |
| d H1 AUC | 0.862 [0.841, 0.882] | 0.893 [0.873, 0.911] |
| e MAD22 OpenCV_native EER% | 4.41 [2.50, 6.67] | 5.39 [3.43, 7.36] |
| e MAD22 OpenCV_e7 EER% | 4.90 [2.83, 7.35] | 5.39 [3.43, 7.84] |
| e MAD22 Webmorph_native EER% | 6.00 [4.41, 8.33] | 5.39 [3.20, 7.35] |
| e MAD22 Webmorph_e7 EER% | 6.00 [4.41, 8.34] | 5.39 [2.94, 8.01] |
| own_rule flag T_R0 % | 0.0 (0/191) | 0.0 (0/191) |
| own_rule flag T_R0_61 % | 0.0 (0/191) | 0.0 (0/191) |
| own_rule flag T_R0_112 % | 0.0 (0/191) | 0.0 (0/191) |
| own_rule flag FRLL_bona_native % | 0.0 (0/204) | 0.0 (0/204) |
| own_rule flag FRLL_bona_jpeg70 % | 0.0 (0/204) | 0.0 (0/204) |
| own_rule flag FRLL_bona_jpeg50 % | 0.0 (0/204) | 0.0 (0/204) |
| own_rule flag FRLL_bona_resample50 % | 0.0 (0/204) | 0.0 (0/204) |
| own_rule flag FRLL_bona_blur1 % | 0.0 (0/204) | 0.0 (0/204) |
| own_rule flag MAD22_OpenCV_e7 % | 0.0 (0/204) | 0.0 (0/204) |
| own_rule flag MAD22_Webmorph_e7 % | 0.0 (0/204) | 0.0 (0/204) |
| own_rule placed T_R2w_opencv % | 0.0 (0/191) | 0.0 (0/191) |
| own_rule placed T_R2w4_opencv % | 0.0 (0/191) | 0.0 (0/191) |
| own_rule placed T_R2w_opencv_61 % | 0.5 (1/191) | 0.0 (0/191) |
| own_rule placed T_R3_opencv % | 50.3 (96/191) | 42.9 (82/191) |
| own_rule placed T_R3m_opencv % | 72.8 (139/191) | 84.8 (162/191) |
| own_rule miss T_R4_opencv % | 4.2 (8/191) | 5.8 (11/191) |
| own_rule miss T_R4_facemorpher % | 3.1 (6/191) | 3.1 (6/191) |
| own_rule  T_R4_opencv_61 % | n/a | n/a |
| own_rule miss MAD22_OpenCV_morph % | 47.0 (282/600) | 43.5 (261/600) |
| own_rule miss MAD22_Webmorph_morph % | 65.8 (329/500) | 55.4 (277/500) |
| own_rule miss H1_morph % | 79.8 (477/598) | 48.7 (291/598) |
| own_rule family-mean miss (gating) % | 49.2 | 38.3 |
| dev flag T_R0 % | 6.3 (12/191) | 3.7 (7/191) |
| dev flag T_R0_61 % | 9.9 (19/191) | 5.8 (11/191) |
| dev flag T_R0_112 % | 7.9 (15/191) | 4.7 (9/191) |
| dev flag FRLL_bona_native % | 1.5 (3/204) | 2.5 (5/204) |
| dev flag FRLL_bona_jpeg70 % | 2.0 (4/204) | 2.5 (5/204) |
| dev flag FRLL_bona_jpeg50 % | 3.4 (7/204) | 2.0 (4/204) |
| dev flag FRLL_bona_resample50 % | 2.5 (5/204) | 2.0 (4/204) |
| dev flag FRLL_bona_blur1 % | 2.5 (5/204) | 2.5 (5/204) |
| dev flag MAD22_OpenCV_e7 % | 1.5 (3/204) | 2.5 (5/204) |
| dev flag MAD22_Webmorph_e7 % | 1.5 (3/204) | 2.5 (5/204) |
| dev placed T_R2w_opencv % | 4.7 (9/191) | 3.1 (6/191) |
| dev placed T_R2w4_opencv % | 5.8 (11/191) | 4.2 (8/191) |
| dev placed T_R2w_opencv_61 % | 11.5 (22/191) | 5.8 (11/191) |
| dev placed T_R3_opencv % | 78.0 (149/191) | 74.9 (143/191) |
| dev placed T_R3m_opencv % | 90.1 (172/191) | 93.7 (179/191) |
| dev miss T_R4_opencv % | 0.5 (1/191) | 0.5 (1/191) |
| dev miss T_R4_facemorpher % | 0.0 (0/191) | 0.0 (0/191) |
| dev  T_R4_opencv_61 % | n/a | n/a |
| dev miss MAD22_OpenCV_morph % | 15.8 (95/600) | 18.0 (108/600) |
| dev miss MAD22_Webmorph_morph % | 28.0 (140/500) | 22.4 (112/500) |
| dev miss H1_morph % | 52.2 (312/598) | 24.9 (149/598) |
| dev family-mean miss (gating) % | 24.1 | 16.5 |
| tau_dev binding pool | D_R0_61 | D_R0_112 |
| tau_dev pools missing | none | none |
| K0 (R2w61 vs R4 < 0.60) | False | False |
| 2x2 | not read: g3_R2w_vs_R4_61, g4_R2w112_vs_R4_112, g4b_R2w61_vs_R4_61 | not read: g3_R2w_vs_R4_61, g4_R2w112_vs_R4_112, g4b_R2w61_vs_R4_61 |
| NU-a violations >10% | none | dev:H1_bona=0.112 |
| NU-b fails | dev:T_R0_112=0.0785/hi0.1262 | dev:H1_bona=0.112/hi0.1401 |
| NU-d miss R4_61 (own, dev) | None | None |
