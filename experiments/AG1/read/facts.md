# AG1 facts table (no interpretation)

Contrast 'X>Y' = AUC of the detector score of rung Y against rung X (0.5 = no separation; above 0.5 = Y scores higher). Intervals: two-way person bootstrap. Excess = detector AUC minus the best simple baseline on the same images.

## Gates
- G-b mip1/frll: pass; oracle AUC R4 vs R3 1.000; R4 verifies both (input) 1.000, (unseen) 1.000; R3 verifies A 1.000; R2 false-match rate 0.0010; thr 0.257
- G-b mip1/primary: pass; oracle AUC R4 vs R3 0.986; R4 verifies both (input) 1.000, (unseen) 1.000; R3 verifies A 1.000; R2 false-match rate 0.0011; thr 0.249
- G-b mip1/feret: pass; oracle AUC R4 vs R3 0.979; R4 verifies both (input) 1.000, (unseen) 1.000; R3 verifies A 1.000; R2 false-match rate 0.0011; thr 0.244
- G-b mip1/frgc: pass; oracle AUC R4 vs R3 0.995; R4 verifies both (input) 1.000, (unseen) 1.000; R3 verifies A 1.000; R2 false-match rate 0.0013; thr 0.269
- G-b mip2/frll: pass; oracle AUC R4 vs R3 1.000; R4 verifies both (input) 1.000, (unseen) 1.000; R3 verifies A 1.000; R2 false-match rate 0.0009; thr 0.257
- RT: {'n': 254, 'median_mean_absdiff': 1.5708595911661785, 'max_mean_absdiff': 3.8914836247762046, 'max_absdiff': 235}

## mip1/frll/madation_vitb16 (primary)

Reading A: mixed; reading B: reads morphing; R3 vs R4: identity reading; R2 vs R3: mixed; AG2: implementation-confounded (bridge AUC outside 0.40-0.60); G-a: no published number given; benchmark EER 18.71%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.748 [0.707, 0.790] | 204 / 204 | thumb (0.994) | 0.524 | -0.247 [-0.287, -0.204] |
| R0>R2 | 0.748 [0.707, 0.790] | 204 / 204 | thumb (0.994) | 0.524 | -0.247 [-0.287, -0.204] |
| R2>R3m (mirror, own rung) | 0.752 [0.704, 0.801] | 102 / 204 | sym (0.952) | 0.952 | -0.200 [-0.252, -0.148] |
| R2>R3 | 0.744 [0.702, 0.790] | 102 / 204 | lapvar (0.683) | 0.545 | 0.061 [0.004, 0.119] |
| R3>R4 | 0.789 [0.686, 0.878] | 102 / 102 | lapvar (0.718) | 0.629 | 0.072 [-0.085, 0.217] |
| R2>R4 | 0.927 [0.863, 0.970] | 102 / 204 | lapvar (0.844) | 0.673 | 0.083 [-0.025, 0.198] |
| R2s>R4 (spread-matched one-person render) | 0.914 [0.841, 0.966] | 102 / 102 | thumb (0.927) | 0.567 | -0.013 [-0.096, 0.075] |
| R3m>R4 (mirror, own rung) | 0.745 [0.649, 0.836] | 102 / 102 | thumb (0.966) | 0.929 | -0.221 [-0.320, -0.127] |
| R0>R4 | 0.982 [0.955, 0.996] | 102 / 204 | thumb (0.997) | 0.689 | -0.015 [-0.042, 0.002] |
| R3>RT (noise floor) | 0.489 [0.470, 0.508] | 102 / 102 | hfband (0.515) | 0.504 | -0.026 [-0.053, -0.002] |
| R0>PUB | 0.893 [0.850, 0.932] | 1000 / 204 | thumb (0.985) | 0.806 | -0.092 [-0.137, -0.050] |
| R2>PUB (AG2) | 0.712 [0.654, 0.770] | 1000 / 204 | thumb (0.962) | 0.795 | -0.250 [-0.316, -0.183] |
| bridge PUB vs BR | 0.207 [0.107, 0.314] | 108 / 108 | thumb (0.972) | 0.627 | -0.764 [-0.877, -0.640] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.365 [0.318, 0.414]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.186 [0.135, 0.247]
- attack detection (R4): 0.980 [0.931, 0.998]
- single-subject: R2 0.544 [0.473, 0.614]; R2i 0.525 [0.454, 0.595]; R2s 0.706 [0.607, 0.792]; R3 0.863 [0.780, 0.923]; R3m 0.814 [0.724, 0.884]; RT 0.804 [0.714, 0.876]
- latent distance medians: {'R2': 7.451307058334351, 'R2s': 5.618855237960815, 'R3': 6.543945074081421, 'R4': 6.44824481010437}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.779, coverage 0.578

## mip1/frll/madation_vitl14 (primary)

Reading A: reads morphing; reading B: reads morphing; R3 vs R4: identity reading; R2 vs R3: identity reading; AG2: implementation-confounded (bridge AUC outside 0.40-0.60); G-a: no published number given; benchmark EER 11.68%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.613 [0.556, 0.668] | 204 / 204 | thumb (0.994) | 0.524 | -0.382 [-0.437, -0.328] |
| R0>R2 | 0.613 [0.556, 0.668] | 204 / 204 | thumb (0.994) | 0.524 | -0.382 [-0.437, -0.328] |
| R2>R3m (mirror, own rung) | 0.852 [0.808, 0.896] | 102 / 204 | sym (0.952) | 0.952 | -0.100 [-0.149, -0.051] |
| R2>R3 | 0.758 [0.713, 0.806] | 102 / 204 | lapvar (0.683) | 0.545 | 0.075 [0.019, 0.131] |
| R3>R4 | 0.874 [0.801, 0.934] | 102 / 102 | lapvar (0.718) | 0.629 | 0.156 [0.037, 0.279] |
| R2>R4 | 0.981 [0.963, 0.994] | 102 / 204 | lapvar (0.844) | 0.673 | 0.137 [0.059, 0.239] |
| R2s>R4 (spread-matched one-person render) | 0.978 [0.954, 0.994] | 102 / 102 | thumb (0.927) | 0.567 | 0.051 [0.008, 0.118] |
| R3m>R4 (mirror, own rung) | 0.757 [0.673, 0.838] | 102 / 102 | thumb (0.966) | 0.929 | -0.208 [-0.299, -0.120] |
| R0>R4 | 0.998 [0.994, 1.000] | 102 / 204 | thumb (0.997) | 0.689 | 0.001 [-0.004, 0.009] |
| R3>RT (noise floor) | 0.491 [0.472, 0.508] | 102 / 102 | hfband (0.515) | 0.504 | -0.025 [-0.052, -0.001] |
| R0>PUB | 0.953 [0.928, 0.973] | 1000 / 204 | thumb (0.985) | 0.806 | -0.032 [-0.062, -0.001] |
| R2>PUB (AG2) | 0.893 [0.859, 0.925] | 1000 / 204 | thumb (0.962) | 0.795 | -0.069 [-0.113, -0.024] |
| bridge PUB vs BR | 0.235 [0.132, 0.352] | 108 / 108 | thumb (0.972) | 0.627 | -0.736 [-0.851, -0.611] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.194 [0.156, 0.235]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.118 [0.077, 0.170]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.270 [0.210, 0.336]; R2i 0.162 [0.114, 0.220]; R2s 0.216 [0.140, 0.308]; R3 0.716 [0.618, 0.801]; R3m 0.853 [0.769, 0.915]; RT 0.686 [0.587, 0.775]
- latent distance medians: {'R2': 7.451307058334351, 'R2s': 5.618855237960815, 'R3': 6.543945074081421, 'R4': 6.44824481010437}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.884, coverage 0.578

## mip1/frll/selfmad_hrnet_w18__own (primary)

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: mixed; AG2: implementation-confounded (bridge AUC outside 0.40-0.60); G-a: no published number given; benchmark EER 0.50%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.996 [0.992, 0.999] | 204 / 204 | thumb (0.994) | 0.524 | 0.001 [-0.007, 0.013] |
| R0>R2 | 0.996 [0.992, 0.999] | 204 / 204 | thumb (0.994) | 0.524 | 0.001 [-0.007, 0.013] |
| R2>R3m (mirror, own rung) | 0.707 [0.661, 0.752] | 102 / 204 | sym (0.952) | 0.952 | -0.245 [-0.297, -0.193] |
| R2>R3 | 0.722 [0.672, 0.771] | 102 / 204 | lapvar (0.683) | 0.545 | 0.039 [-0.031, 0.105] |
| R3>R4 | 0.693 [0.593, 0.783] | 102 / 102 | lapvar (0.718) | 0.629 | -0.025 [-0.147, 0.095] |
| R2>R4 | 0.861 [0.800, 0.911] | 102 / 204 | lapvar (0.844) | 0.673 | 0.018 [-0.069, 0.114] |
| R2s>R4 (spread-matched one-person render) | 0.911 [0.852, 0.957] | 102 / 102 | thumb (0.927) | 0.567 | -0.016 [-0.090, 0.064] |
| R3m>R4 (mirror, own rung) | 0.692 [0.599, 0.777] | 102 / 102 | thumb (0.966) | 0.929 | -0.274 [-0.376, -0.173] |
| R0>R4 | 1.000 [1.000, 1.000] | 102 / 204 | thumb (0.997) | 0.689 | 0.003 [0.000, 0.010] |
| R3>RT (noise floor) | 0.501 [0.479, 0.522] | 102 / 102 | hfband (0.515) | 0.504 | -0.014 [-0.043, 0.013] |
| R0>PUB | 1.000 [0.999, 1.000] | 1000 / 204 | thumb (0.985) | 0.806 | 0.015 [-0.000, 0.039] |
| R2>PUB (AG2) | 0.872 [0.832, 0.908] | 1000 / 204 | thumb (0.962) | 0.795 | -0.091 [-0.140, -0.041] |
| bridge PUB vs BR | 0.607 [0.458, 0.748] | 108 / 108 | thumb (0.972) | 0.627 | -0.365 [-0.523, -0.217] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.429 [0.380, 0.479]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.005 [0.000, 0.027]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.853 [0.797, 0.899]; R2i 0.828 [0.770, 0.877]; R2s 0.843 [0.758, 0.908]; R3 0.990 [0.947, 1.000]; R3m 0.990 [0.947, 1.000]; RT 0.990 [0.947, 1.000]
- latent distance medians: {'R2': 7.451307058334351, 'R2s': 5.618855237960815, 'R3': 6.543945074081421, 'R4': 6.44824481010437}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.546, coverage 0.578

## mip1/frll/selfmad_hrnet_w18__rel (secondary (printed beside))

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: retained; G-a: no published number given; benchmark EER 0.99%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.974 [0.961, 0.985] | 204 / 204 | thumb (0.994) | 0.524 | -0.020 [-0.036, -0.004] |
| R0>R2 | 0.974 [0.961, 0.985] | 204 / 204 | thumb (0.994) | 0.524 | -0.020 [-0.036, -0.004] |
| R2>R3m (mirror, own rung) | 0.784 [0.744, 0.826] | 102 / 204 | sym (0.952) | 0.952 | -0.168 [-0.214, -0.119] |
| R2>R3 | 0.771 [0.723, 0.816] | 102 / 204 | lapvar (0.683) | 0.545 | 0.088 [0.023, 0.150] |
| R3>R4 | 0.733 [0.636, 0.818] | 102 / 102 | lapvar (0.718) | 0.629 | 0.015 [-0.105, 0.131] |
| R2>R4 | 0.920 [0.863, 0.960] | 102 / 204 | lapvar (0.844) | 0.673 | 0.076 [-0.006, 0.165] |
| R2s>R4 (spread-matched one-person render) | 0.940 [0.885, 0.980] | 102 / 102 | thumb (0.927) | 0.567 | 0.013 [-0.055, 0.091] |
| R3m>R4 (mirror, own rung) | 0.717 [0.617, 0.807] | 102 / 102 | thumb (0.966) | 0.929 | -0.249 [-0.355, -0.146] |
| R0>R4 | 1.000 [1.000, 1.000] | 102 / 204 | thumb (0.997) | 0.689 | 0.003 [-0.000, 0.010] |
| R3>RT (noise floor) | 0.500 [0.479, 0.519] | 102 / 102 | hfband (0.515) | 0.504 | -0.016 [-0.044, 0.009] |
| R0>PUB | 1.000 [0.999, 1.000] | 1000 / 204 | thumb (0.985) | 0.806 | 0.014 [-0.000, 0.039] |
| R2>PUB (AG2) | 0.925 [0.895, 0.950] | 1000 / 204 | thumb (0.962) | 0.795 | -0.038 [-0.078, 0.003] |
| bridge PUB vs BR | 0.563 [0.441, 0.693] | 108 / 108 | thumb (0.972) | 0.627 | -0.408 [-0.538, -0.268] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.336 [0.290, 0.384]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.010 [0.001, 0.035]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.662 [0.592, 0.726]; R2i 0.647 [0.577, 0.713]; R2s 0.676 [0.577, 0.766]; R3 0.931 [0.864, 0.972]; R3m 0.931 [0.864, 0.972]; RT 0.931 [0.864, 0.972]
- latent distance medians: {'R2': 7.451307058334351, 'R2s': 5.618855237960815, 'R3': 6.543945074081421, 'R4': 6.44824481010437}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.513, coverage 0.578

## mip2/frll/madation_vitb16 (primary)

Reading A: mixed; reading B: reads morphing; R3 vs R4: identity reading; R2 vs R3: mixed; AG2: implementation-confounded (bridge AUC outside 0.40-0.60); G-a: no published number given; benchmark EER 13.27%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.785 [0.743, 0.827] | 204 / 204 | thumb (1.000) | 0.566 | -0.215 [-0.257, -0.173] |
| R0>R2 | 0.785 [0.743, 0.827] | 204 / 204 | thumb (1.000) | 0.566 | -0.215 [-0.257, -0.173] |
| R2>R3m (mirror, own rung) | 0.734 [0.698, 0.774] | 102 / 204 | sym (0.947) | 0.947 | -0.213 [-0.260, -0.163] |
| R2>R3 | 0.711 [0.676, 0.749] | 102 / 204 | lapvar (0.638) | 0.532 | 0.073 [0.017, 0.129] |
| R3>R4 | 0.769 [0.674, 0.856] | 102 / 102 | thumb (0.656) | 0.618 | 0.113 [-0.019, 0.234] |
| R2>R4 | 0.893 [0.830, 0.945] | 102 / 204 | thumb (0.728) | 0.650 | 0.165 [0.065, 0.271] |
| R2s>R4 (spread-matched one-person render) | 0.891 [0.820, 0.950] | 102 / 102 | thumb (0.927) | 0.529 | -0.036 [-0.123, 0.050] |
| R3m>R4 (mirror, own rung) | 0.730 [0.628, 0.822] | 102 / 102 | sym (0.919) | 0.919 | -0.189 [-0.298, -0.088] |
| R0>R4 | 0.977 [0.948, 0.995] | 102 / 204 | thumb (0.990) | 0.714 | -0.014 [-0.046, 0.011] |
| R3>RT (noise floor) | 0.496 [0.478, 0.512] | 102 / 102 | sym (0.504) | 0.504 | -0.008 [-0.029, 0.012] |
| R0>PUB | 0.931 [0.897, 0.960] | 999 / 204 | thumb (0.993) | 0.859 | -0.062 [-0.099, -0.030] |
| R2>PUB (AG2) | 0.730 [0.677, 0.781] | 999 / 204 | thumb (0.952) | 0.824 | -0.222 [-0.283, -0.162] |
| bridge PUB vs BR | 0.310 [0.191, 0.428] | 108 / 108 | thumb (0.976) | 0.758 | -0.666 [-0.788, -0.544] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.346 [0.299, 0.394]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.132 [0.089, 0.187]
- attack detection (R4): 0.961 [0.903, 0.989]
- single-subject: R2 0.559 [0.488, 0.628]; R2s 0.627 [0.526, 0.721]; R3 0.843 [0.758, 0.908]; R3m 0.824 [0.736, 0.892]; RT 0.824 [0.736, 0.892]
- latent distance medians: {'R2': 10.505685806274414, 'R2s': 8.806763648986816, 'R3': 10.350821495056152, 'R4': 9.866408824920654}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.710, coverage 1.000

## mip2/frll/madation_vitl14 (primary)

Reading A: mixed; reading B: reads morphing; R3 vs R4: identity reading; R2 vs R3: mixed; AG2: mixed; G-a: no published number given; benchmark EER 9.81%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.687 [0.631, 0.743] | 204 / 204 | thumb (1.000) | 0.566 | -0.312 [-0.369, -0.257] |
| R0>R2 | 0.687 [0.631, 0.743] | 204 / 204 | thumb (1.000) | 0.566 | -0.312 [-0.369, -0.257] |
| R2>R3m (mirror, own rung) | 0.723 [0.684, 0.768] | 102 / 204 | sym (0.947) | 0.947 | -0.224 [-0.271, -0.172] |
| R2>R3 | 0.678 [0.641, 0.719] | 102 / 204 | lapvar (0.638) | 0.532 | 0.040 [-0.016, 0.097] |
| R3>R4 | 0.767 [0.677, 0.850] | 102 / 102 | thumb (0.656) | 0.618 | 0.111 [-0.014, 0.235] |
| R2>R4 | 0.903 [0.842, 0.950] | 102 / 204 | thumb (0.728) | 0.650 | 0.175 [0.079, 0.279] |
| R2s>R4 (spread-matched one-person render) | 0.959 [0.916, 0.987] | 102 / 102 | thumb (0.927) | 0.529 | 0.032 [-0.016, 0.088] |
| R3m>R4 (mirror, own rung) | 0.710 [0.608, 0.800] | 102 / 102 | sym (0.919) | 0.919 | -0.209 [-0.319, -0.109] |
| R0>R4 | 0.979 [0.940, 0.997] | 102 / 204 | thumb (0.990) | 0.714 | -0.011 [-0.051, 0.014] |
| R3>RT (noise floor) | 0.497 [0.482, 0.511] | 102 / 102 | sym (0.504) | 0.504 | -0.007 [-0.025, 0.010] |
| R0>PUB | 0.963 [0.943, 0.979] | 999 / 204 | thumb (0.993) | 0.859 | -0.030 [-0.053, -0.008] |
| R2>PUB (AG2) | 0.849 [0.806, 0.889] | 999 / 204 | thumb (0.952) | 0.824 | -0.103 [-0.156, -0.052] |
| bridge PUB vs BR | 0.408 [0.296, 0.514] | 108 / 108 | thumb (0.976) | 0.758 | -0.568 [-0.682, -0.467] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.238 [0.197, 0.282]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.098 [0.061, 0.147]
- attack detection (R4): 0.971 [0.916, 0.994]
- single-subject: R2 0.377 [0.311, 0.448]; R2s 0.137 [0.077, 0.220]; R3 0.608 [0.506, 0.703]; R3m 0.686 [0.587, 0.775]; RT 0.618 [0.516, 0.712]
- latent distance medians: {'R2': 10.505685806274414, 'R2s': 8.806763648986816, 'R3': 10.350821495056152, 'R4': 9.866408824920654}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.818, coverage 1.000

## mip2/frll/selfmad_hrnet_w18__own (primary)

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: mixed; AG2: implementation-confounded (bridge AUC outside 0.40-0.60); G-a: no published number given; benchmark EER 0.05%; p(R2 vs R4 <= 0.65) 0.0005

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.979 [0.961, 0.992] | 204 / 204 | thumb (1.000) | 0.566 | -0.021 [-0.038, -0.008] |
| R0>R2 | 0.979 [0.961, 0.992] | 204 / 204 | thumb (1.000) | 0.566 | -0.021 [-0.038, -0.008] |
| R2>R3m (mirror, own rung) | 0.679 [0.634, 0.726] | 102 / 204 | sym (0.947) | 0.947 | -0.268 [-0.321, -0.212] |
| R2>R3 | 0.718 [0.677, 0.761] | 102 / 204 | lapvar (0.638) | 0.532 | 0.080 [0.023, 0.138] |
| R3>R4 | 0.621 [0.517, 0.721] | 102 / 102 | thumb (0.656) | 0.618 | -0.035 [-0.177, 0.108] |
| R2>R4 | 0.810 [0.727, 0.880] | 102 / 204 | thumb (0.728) | 0.650 | 0.082 [-0.039, 0.203] |
| R2s>R4 (spread-matched one-person render) | 0.926 [0.863, 0.968] | 102 / 102 | thumb (0.927) | 0.529 | -0.001 [-0.078, 0.073] |
| R3m>R4 (mirror, own rung) | 0.684 [0.565, 0.789] | 102 / 102 | sym (0.919) | 0.919 | -0.235 [-0.366, -0.118] |
| R0>R4 | 1.000 [0.997, 1.000] | 102 / 204 | thumb (0.990) | 0.714 | 0.009 [-0.001, 0.025] |
| R3>RT (noise floor) | 0.502 [0.479, 0.527] | 102 / 102 | sym (0.504) | 0.504 | -0.001 [-0.029, 0.026] |
| R0>PUB | 1.000 [1.000, 1.000] | 999 / 204 | thumb (0.993) | 0.859 | 0.007 [-0.000, 0.020] |
| R2>PUB (AG2) | 0.987 [0.976, 0.994] | 999 / 204 | thumb (0.952) | 0.824 | 0.035 [0.003, 0.073] |
| bridge PUB vs BR | 0.947 [0.873, 0.992] | 108 / 108 | thumb (0.976) | 0.758 | -0.029 [-0.112, 0.032] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.218 [0.179, 0.261]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.000 [0.000, 0.018]
- attack detection (R4): 0.873 [0.792, 0.930]
- single-subject: R2 0.436 [0.367, 0.507]; R2s 0.196 [0.124, 0.286]; R3 0.775 [0.681, 0.851]; R3m 0.755 [0.660, 0.835]; RT 0.745 [0.649, 0.826]
- latent distance medians: {'R2': 10.505685806274414, 'R2s': 8.806763648986816, 'R3': 10.350821495056152, 'R4': 9.866408824920654}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.537, coverage 1.000

## mip2/frll/selfmad_hrnet_w18__rel (secondary (printed beside))

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: mixed; AG2: implementation-confounded (bridge AUC outside 0.40-0.60); G-a: no published number given; benchmark EER 0.99%; p(R2 vs R4 <= 0.65) 0.0002

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R1 | 0.500 [0.500, 0.500] | 204 / 204 | bytes (0.500) | 0.500 | 0.000 [0.000, 0.000] |
| R1>R2 | 0.948 [0.925, 0.970] | 204 / 204 | thumb (1.000) | 0.566 | -0.052 [-0.075, -0.030] |
| R0>R2 | 0.948 [0.925, 0.970] | 204 / 204 | thumb (1.000) | 0.566 | -0.052 [-0.075, -0.030] |
| R2>R3m (mirror, own rung) | 0.685 [0.644, 0.730] | 102 / 204 | sym (0.947) | 0.947 | -0.262 [-0.310, -0.210] |
| R2>R3 | 0.727 [0.687, 0.773] | 102 / 204 | lapvar (0.638) | 0.532 | 0.089 [0.031, 0.151] |
| R3>R4 | 0.684 [0.574, 0.781] | 102 / 102 | thumb (0.656) | 0.618 | 0.028 [-0.128, 0.175] |
| R2>R4 | 0.851 [0.764, 0.917] | 102 / 204 | thumb (0.728) | 0.650 | 0.123 [-0.006, 0.241] |
| R2s>R4 (spread-matched one-person render) | 0.924 [0.857, 0.970] | 102 / 102 | thumb (0.927) | 0.529 | -0.002 [-0.086, 0.074] |
| R3m>R4 (mirror, own rung) | 0.723 [0.605, 0.816] | 102 / 102 | sym (0.919) | 0.919 | -0.196 [-0.324, -0.091] |
| R0>R4 | 0.998 [0.991, 1.000] | 102 / 204 | thumb (0.990) | 0.714 | 0.007 [-0.005, 0.023] |
| R3>RT (noise floor) | 0.499 [0.481, 0.516] | 102 / 102 | sym (0.504) | 0.504 | -0.005 [-0.027, 0.015] |
| R0>PUB | 1.000 [0.999, 1.000] | 999 / 204 | thumb (0.993) | 0.859 | 0.007 [-0.000, 0.020] |
| R2>PUB (AG2) | 0.971 [0.952, 0.987] | 999 / 204 | thumb (0.952) | 0.824 | 0.020 [-0.017, 0.060] |
| bridge PUB vs BR | 0.890 [0.787, 0.965] | 108 / 108 | thumb (0.976) | 0.758 | -0.086 [-0.196, -0.003] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.233 [0.193, 0.277]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.010 [0.001, 0.035]
- attack detection (R4): 0.922 [0.851, 0.966]
- single-subject: R2 0.456 [0.386, 0.527]; R2s 0.294 [0.208, 0.393]; R3 0.843 [0.758, 0.908]; R3m 0.745 [0.649, 0.826]; RT 0.775 [0.681, 0.851]
- latent distance medians: {'R2': 10.505685806274414, 'R2s': 8.806763648986816, 'R3': 10.350821495056152, 'R4': 9.866408824920654}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.509, coverage 1.000

## mip1/primary/madation_vitb16 (primary, primary cell)

Reading A: mixed; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 18.71%; p(R2 vs R4 <= 0.65) 0.0000, Holm within AG1 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.900 [0.879, 0.920] | 400 / 400 | thumb (0.988) | 0.636 | -0.089 [-0.110, -0.068] |
| R2>R3m (mirror, own rung) | 0.797 [0.766, 0.828] | 200 / 400 | sym (0.950) | 0.950 | -0.153 [-0.188, -0.117] |
| R2>R3 | 0.794 [0.768, 0.822] | 200 / 400 | bytes (0.712) | 0.641 | 0.083 [0.045, 0.120] |
| R3>R4 | 0.661 [0.596, 0.723] | 200 / 200 | bytes (0.622) | 0.578 | 0.039 [-0.042, 0.119] |
| R2>R4 | 0.889 [0.848, 0.923] | 200 / 400 | bytes (0.782) | 0.702 | 0.108 [0.054, 0.160] |
| R2s>R4 (spread-matched one-person render) | 0.873 [0.820, 0.916] | 200 / 200 | thumb (0.881) | 0.615 | -0.008 [-0.073, 0.050] |
| R3m>R4 (mirror, own rung) | 0.653 [0.585, 0.716] | 200 / 200 | sym (0.882) | 0.882 | -0.229 [-0.311, -0.149] |
| R0>R4 | 0.993 [0.986, 0.998] | 200 / 400 | thumb (0.995) | 0.807 | -0.002 [-0.010, 0.008] |
| R3>RT (noise floor) | 0.508 [0.476, 0.542] | 50 / 50 | lapvar (0.514) | 0.506 | -0.006 [-0.046, 0.027] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.346 [0.313, 0.380]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.085 [0.060, 0.117]
- attack detection (R4): 0.985 [0.957, 0.997]
- single-subject: R2 0.608 [0.558, 0.656]; R2i 0.415 [0.366, 0.465]; R2s 0.775 [0.711, 0.831]; R3 0.955 [0.916, 0.979]; R3m 0.935 [0.891, 0.965]; RT 0.980 [0.894, 0.999]
- latent distance medians: {'R2': 7.633354663848877, 'R2s': 5.674907684326172, 'R3': 6.482211589813232, 'R4': 6.539500713348389}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.636, coverage 0.915
- R3 vs R4 within 60 days: 0.641 [0.532, 0.750] n [72, 72]
- AG3 levels vs R2: 0.0: 0.487; 0.1: 0.582; 0.2: 0.656; 0.3: 0.733; 0.4: 0.847; 0.5: 0.904; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.565; 0.2: 0.614; 0.3: 0.669; 0.4: 0.757; 0.5: 0.811; ramp (twin dose: second photo only)

## mip1/primary/madation_vitl14 (primary, primary cell)

Reading A: mixed; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 11.68%; p(R2 vs R4 <= 0.65) 0.0000, Holm within AG1 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.793 [0.762, 0.824] | 400 / 400 | thumb (0.988) | 0.636 | -0.196 [-0.227, -0.165] |
| R2>R3m (mirror, own rung) | 0.849 [0.821, 0.877] | 200 / 400 | sym (0.950) | 0.950 | -0.101 [-0.135, -0.066] |
| R2>R3 | 0.812 [0.780, 0.843] | 200 / 400 | bytes (0.712) | 0.641 | 0.100 [0.057, 0.142] |
| R3>R4 | 0.720 [0.657, 0.779] | 200 / 200 | bytes (0.622) | 0.578 | 0.097 [0.016, 0.179] |
| R2>R4 | 0.946 [0.922, 0.966] | 200 / 400 | bytes (0.782) | 0.702 | 0.164 [0.118, 0.214] |
| R2s>R4 (spread-matched one-person render) | 0.936 [0.907, 0.960] | 200 / 200 | thumb (0.881) | 0.615 | 0.055 [0.010, 0.102] |
| R3m>R4 (mirror, own rung) | 0.664 [0.593, 0.731] | 200 / 200 | sym (0.882) | 0.882 | -0.218 [-0.303, -0.136] |
| R0>R4 | 0.990 [0.982, 0.996] | 200 / 400 | thumb (0.995) | 0.807 | -0.005 [-0.014, 0.005] |
| R3>RT (noise floor) | 0.503 [0.472, 0.534] | 50 / 50 | lapvar (0.514) | 0.506 | -0.011 [-0.048, 0.017] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.234 [0.205, 0.265]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.048 [0.029, 0.073]
- attack detection (R4): 0.990 [0.964, 0.999]
- single-subject: R2 0.420 [0.371, 0.470]; R2i 0.237 [0.197, 0.282]; R2s 0.390 [0.322, 0.461]; R3 0.870 [0.815, 0.913]; R3m 0.880 [0.827, 0.922]; RT 0.880 [0.757, 0.955]
- latent distance medians: {'R2': 7.633354663848877, 'R2s': 5.674907684326172, 'R3': 6.482211589813232, 'R4': 6.539500713348389}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.632, coverage 0.915
- R3 vs R4 within 60 days: 0.702 [0.602, 0.799] n [72, 72]
- AG3 levels vs R2: 0.0: 0.500; 0.1: 0.553; 0.2: 0.618; 0.3: 0.744; 0.4: 0.873; 0.5: 0.933; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.550; 0.2: 0.595; 0.3: 0.665; 0.4: 0.758; 0.5: 0.806; ramp (twin dose: second photo only)

## mip1/primary/selfmad_hrnet_w18__own (primary, primary cell)

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: mixed; AG2: -; G-a: no published number given; benchmark EER 0.50%; p(R2 vs R4 <= 0.65) 0.0000, Holm within AG1 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.927 [0.906, 0.946] | 400 / 400 | thumb (0.988) | 0.636 | -0.061 [-0.083, -0.041] |
| R2>R3m (mirror, own rung) | 0.673 [0.638, 0.709] | 200 / 400 | sym (0.950) | 0.950 | -0.276 [-0.317, -0.237] |
| R2>R3 | 0.716 [0.684, 0.750] | 200 / 400 | bytes (0.712) | 0.641 | 0.004 [-0.043, 0.051] |
| R3>R4 | 0.653 [0.583, 0.721] | 200 / 200 | bytes (0.622) | 0.578 | 0.031 [-0.060, 0.127] |
| R2>R4 | 0.824 [0.776, 0.867] | 200 / 400 | bytes (0.782) | 0.702 | 0.042 [-0.020, 0.106] |
| R2s>R4 (spread-matched one-person render) | 0.870 [0.822, 0.912] | 200 / 200 | thumb (0.881) | 0.615 | -0.010 [-0.071, 0.049] |
| R3m>R4 (mirror, own rung) | 0.683 [0.614, 0.749] | 200 / 200 | sym (0.882) | 0.882 | -0.200 [-0.280, -0.123] |
| R0>R4 | 0.987 [0.977, 0.995] | 200 / 400 | thumb (0.995) | 0.807 | -0.008 [-0.019, 0.003] |
| R3>RT (noise floor) | 0.540 [0.493, 0.589] | 50 / 50 | lapvar (0.514) | 0.506 | 0.025 [-0.026, 0.072] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.646 [0.612, 0.679]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.318 [0.272, 0.366]
- attack detection (R4): 1.000 [0.982, 1.000]
- single-subject: R2 0.975 [0.955, 0.988]; R2i 0.968 [0.945, 0.983]; R2s 0.985 [0.957, 0.997]; R3 1.000 [0.982, 1.000]; R3m 0.995 [0.972, 1.000]; RT 1.000 [0.929, 1.000]
- latent distance medians: {'R2': 7.633354663848877, 'R2s': 5.674907684326172, 'R3': 6.482211589813232, 'R4': 6.539500713348389}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.605, coverage 0.915
- R3 vs R4 within 60 days: 0.660 [0.538, 0.771] n [72, 72]
- AG3 levels vs R2: 0.0: 0.500; 0.1: 0.528; 0.2: 0.648; 0.3: 0.740; 0.4: 0.828; 0.5: 0.848; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.553; 0.2: 0.554; 0.3: 0.620; 0.4: 0.706; 0.5: 0.731; ramp (twin dose: second photo only)

## mip1/primary/selfmad_hrnet_w18__rel (secondary (printed beside))

Reading A: mixed; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 0.99%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.893 [0.872, 0.914] | 400 / 400 | thumb (0.988) | 0.636 | -0.095 [-0.117, -0.074] |
| R2>R3m (mirror, own rung) | 0.717 [0.682, 0.753] | 200 / 400 | sym (0.950) | 0.950 | -0.233 [-0.273, -0.193] |
| R2>R3 | 0.773 [0.744, 0.803] | 200 / 400 | bytes (0.712) | 0.641 | 0.061 [0.016, 0.106] |
| R3>R4 | 0.667 [0.602, 0.731] | 200 / 200 | bytes (0.622) | 0.578 | 0.044 [-0.047, 0.139] |
| R2>R4 | 0.890 [0.850, 0.924] | 200 / 400 | bytes (0.782) | 0.702 | 0.108 [0.051, 0.168] |
| R2s>R4 (spread-matched one-person render) | 0.913 [0.871, 0.947] | 200 / 200 | thumb (0.881) | 0.615 | 0.032 [-0.023, 0.086] |
| R3m>R4 (mirror, own rung) | 0.697 [0.635, 0.759] | 200 / 200 | sym (0.882) | 0.882 | -0.185 [-0.260, -0.113] |
| R0>R4 | 0.991 [0.983, 0.997] | 200 / 400 | thumb (0.995) | 0.807 | -0.004 [-0.014, 0.006] |
| R3>RT (noise floor) | 0.528 [0.490, 0.572] | 50 / 50 | lapvar (0.514) | 0.506 | 0.013 [-0.034, 0.058] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.545 [0.510, 0.580]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.245 [0.204, 0.290]
- attack detection (R4): 1.000 [0.982, 1.000]
- single-subject: R2 0.845 [0.806, 0.879]; R2i 0.835 [0.795, 0.870]; R2s 0.860 [0.804, 0.905]; R3 0.990 [0.964, 0.999]; R3m 0.965 [0.929, 0.986]; RT 0.980 [0.894, 0.999]
- latent distance medians: {'R2': 7.633354663848877, 'R2s': 5.674907684326172, 'R3': 6.482211589813232, 'R4': 6.539500713348389}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.593, coverage 0.915
- R3 vs R4 within 60 days: 0.671 [0.558, 0.775] n [72, 72]
- AG3 levels vs R2: 0.0: 0.492; 0.1: 0.536; 0.2: 0.656; 0.3: 0.742; 0.4: 0.869; 0.5: 0.889; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.527; 0.2: 0.592; 0.3: 0.654; 0.4: 0.748; 0.5: 0.772; ramp (twin dose: second photo only)

## mip1/feret/madation_vitb16 (primary)

Reading A: mixed; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 18.71%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.849 [0.815, 0.882] | 200 / 200 | thumb (0.995) | 0.704 | -0.146 [-0.179, -0.113] |
| R2>R3m (mirror, own rung) | 0.808 [0.763, 0.853] | 100 / 200 | sym (0.958) | 0.958 | -0.150 [-0.202, -0.099] |
| R2>R3 | 0.782 [0.740, 0.821] | 100 / 200 | sym (0.670) | 0.670 | 0.112 [0.053, 0.169] |
| R3>R4 | 0.669 [0.570, 0.763] | 100 / 100 | bytes (0.617) | 0.546 | 0.052 [-0.064, 0.175] |
| R2>R4 | 0.881 [0.817, 0.931] | 100 / 200 | lapvar (0.755) | 0.692 | 0.126 [0.041, 0.222] |
| R2s>R4 (spread-matched one-person render) | 0.848 [0.761, 0.916] | 100 / 100 | thumb (0.879) | 0.560 | -0.031 [-0.129, 0.053] |
| R3m>R4 (mirror, own rung) | 0.627 [0.523, 0.724] | 100 / 100 | sym (0.918) | 0.918 | -0.291 [-0.402, -0.185] |
| R0>R4 | 0.984 [0.966, 0.995] | 100 / 200 | thumb (0.998) | 0.851 | -0.014 [-0.032, -0.001] |
| R3>RT (noise floor) | 0.501 [0.448, 0.552] | 25 / 25 | thumb (0.509) | 0.504 | -0.008 [-0.075, 0.045] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.335 [0.289, 0.384]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.115 [0.074, 0.168]
- attack detection (R4): 0.970 [0.915, 0.994]
- single-subject: R2 0.555 [0.483, 0.625]; R2i 0.405 [0.336, 0.477]; R2s 0.740 [0.643, 0.823]; R3 0.920 [0.848, 0.965]; R3m 0.910 [0.836, 0.958]; RT 0.960 [0.796, 0.999]
- latent distance medians: {'R2': 7.786777973175049, 'R2s': 5.761248350143433, 'R3': 6.563141584396362, 'R4': 6.6301658153533936}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.632, coverage 1.000
- R3 vs R4 within 60 days: 0.636 [0.470, 0.787] n [37, 37]
- AG3 levels vs R2: 0.0: 0.476; 0.1: 0.555; 0.2: 0.634; 0.3: 0.705; 0.4: 0.854; 0.5: 0.907; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.561; 0.2: 0.587; 0.3: 0.633; 0.4: 0.746; 0.5: 0.784; ramp (twin dose: second photo only)

## mip1/feret/madation_vitl14 (primary)

Reading A: mixed; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 11.68%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.741 [0.695, 0.784] | 200 / 200 | thumb (0.995) | 0.704 | -0.254 [-0.299, -0.212] |
| R2>R3m (mirror, own rung) | 0.836 [0.795, 0.877] | 100 / 200 | sym (0.958) | 0.958 | -0.123 [-0.172, -0.073] |
| R2>R3 | 0.772 [0.722, 0.820] | 100 / 200 | sym (0.670) | 0.670 | 0.102 [0.036, 0.165] |
| R3>R4 | 0.729 [0.642, 0.810] | 100 / 100 | bytes (0.617) | 0.546 | 0.112 [-0.001, 0.226] |
| R2>R4 | 0.929 [0.889, 0.962] | 100 / 200 | lapvar (0.755) | 0.692 | 0.174 [0.089, 0.275] |
| R2s>R4 (spread-matched one-person render) | 0.917 [0.869, 0.958] | 100 / 100 | thumb (0.879) | 0.560 | 0.038 [-0.026, 0.103] |
| R3m>R4 (mirror, own rung) | 0.654 [0.554, 0.751] | 100 / 100 | sym (0.918) | 0.918 | -0.265 [-0.376, -0.156] |
| R0>R4 | 0.977 [0.957, 0.992] | 100 / 200 | thumb (0.998) | 0.851 | -0.020 [-0.041, -0.004] |
| R3>RT (noise floor) | 0.502 [0.444, 0.554] | 25 / 25 | thumb (0.509) | 0.504 | -0.006 [-0.083, 0.042] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.230 [0.190, 0.274]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.075 [0.043, 0.121]
- attack detection (R4): 0.990 [0.946, 1.000]
- single-subject: R2 0.385 [0.317, 0.456]; R2i 0.235 [0.178, 0.300]; R2s 0.330 [0.239, 0.431]; R3 0.810 [0.719, 0.882]; R3m 0.870 [0.788, 0.929]; RT 0.840 [0.639, 0.955]
- latent distance medians: {'R2': 7.786777973175049, 'R2s': 5.761248350143433, 'R3': 6.563141584396362, 'R4': 6.6301658153533936}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.634, coverage 1.000
- R3 vs R4 within 60 days: 0.692 [0.567, 0.822] n [37, 37]
- AG3 levels vs R2: 0.0: 0.497; 0.1: 0.564; 0.2: 0.606; 0.3: 0.721; 0.4: 0.829; 0.5: 0.902; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.562; 0.2: 0.576; 0.3: 0.623; 0.4: 0.706; 0.5: 0.744; ramp (twin dose: second photo only)

## mip1/feret/selfmad_hrnet_w18__own (primary)

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: mixed; AG2: -; G-a: no published number given; benchmark EER 0.50%; p(R2 vs R4 <= 0.65) 0.0001

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.868 [0.829, 0.904] | 200 / 200 | thumb (0.995) | 0.704 | -0.126 [-0.165, -0.091] |
| R2>R3m (mirror, own rung) | 0.691 [0.641, 0.741] | 100 / 200 | sym (0.958) | 0.958 | -0.268 [-0.322, -0.213] |
| R2>R3 | 0.742 [0.690, 0.792] | 100 / 200 | sym (0.670) | 0.670 | 0.072 [0.005, 0.136] |
| R3>R4 | 0.653 [0.547, 0.753] | 100 / 100 | bytes (0.617) | 0.546 | 0.036 [-0.106, 0.176] |
| R2>R4 | 0.828 [0.755, 0.889] | 100 / 200 | lapvar (0.755) | 0.692 | 0.073 [-0.034, 0.185] |
| R2s>R4 (spread-matched one-person render) | 0.873 [0.805, 0.931] | 100 / 100 | thumb (0.879) | 0.560 | -0.006 [-0.078, 0.066] |
| R3m>R4 (mirror, own rung) | 0.682 [0.577, 0.779] | 100 / 100 | sym (0.918) | 0.918 | -0.237 [-0.349, -0.131] |
| R0>R4 | 0.971 [0.947, 0.988] | 100 / 200 | thumb (0.998) | 0.851 | -0.027 [-0.050, -0.009] |
| R3>RT (noise floor) | 0.554 [0.472, 0.635] | 25 / 25 | thumb (0.509) | 0.504 | 0.045 [-0.048, 0.122] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.720 [0.673, 0.763]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.475 [0.404, 0.547]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.965 [0.929, 0.986]; R2i 0.950 [0.910, 0.976]; R2s 0.980 [0.930, 0.998]; R3 1.000 [0.964, 1.000]; R3m 1.000 [0.964, 1.000]; RT 1.000 [0.863, 1.000]
- latent distance medians: {'R2': 7.786777973175049, 'R2s': 5.761248350143433, 'R3': 6.563141584396362, 'R4': 6.6301658153533936}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.624, coverage 1.000
- R3 vs R4 within 60 days: 0.668 [0.482, 0.829] n [37, 37]
- AG3 levels vs R2: 0.0: 0.506; 0.1: 0.545; 0.2: 0.707; 0.3: 0.746; 0.4: 0.846; 0.5: 0.861; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.587; 0.2: 0.589; 0.3: 0.672; 0.4: 0.772; 0.5: 0.759; ramp (twin dose: second photo only)

## mip1/feret/selfmad_hrnet_w18__rel (secondary (printed beside))

Reading A: mixed; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 0.99%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.851 [0.815, 0.887] | 200 / 200 | thumb (0.995) | 0.704 | -0.143 [-0.179, -0.108] |
| R2>R3m (mirror, own rung) | 0.737 [0.685, 0.788] | 100 / 200 | sym (0.958) | 0.958 | -0.222 [-0.278, -0.165] |
| R2>R3 | 0.805 [0.760, 0.850] | 100 / 200 | sym (0.670) | 0.670 | 0.135 [0.072, 0.195] |
| R3>R4 | 0.640 [0.543, 0.735] | 100 / 100 | bytes (0.617) | 0.546 | 0.024 [-0.116, 0.164] |
| R2>R4 | 0.886 [0.829, 0.935] | 100 / 200 | lapvar (0.755) | 0.692 | 0.131 [0.035, 0.237] |
| R2s>R4 (spread-matched one-person render) | 0.896 [0.831, 0.949] | 100 / 100 | thumb (0.879) | 0.560 | 0.017 [-0.055, 0.087] |
| R3m>R4 (mirror, own rung) | 0.669 [0.575, 0.762] | 100 / 100 | sym (0.918) | 0.918 | -0.249 [-0.350, -0.150] |
| R0>R4 | 0.980 [0.962, 0.994] | 100 / 200 | thumb (0.998) | 0.851 | -0.017 [-0.036, -0.002] |
| R3>RT (noise floor) | 0.526 [0.454, 0.608] | 25 / 25 | thumb (0.509) | 0.504 | 0.018 [-0.080, 0.106] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.578 [0.527, 0.626]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.315 [0.251, 0.384]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.840 [0.782, 0.888]; R2i 0.785 [0.722, 0.840]; R2s 0.870 [0.788, 0.929]; R3 0.990 [0.946, 1.000]; R3m 0.960 [0.901, 0.989]; RT 1.000 [0.863, 1.000]
- latent distance medians: {'R2': 7.786777973175049, 'R2s': 5.761248350143433, 'R3': 6.563141584396362, 'R4': 6.6301658153533936}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.585, coverage 1.000
- R3 vs R4 within 60 days: 0.665 [0.497, 0.816] n [37, 37]
- AG3 levels vs R2: 0.0: 0.499; 0.1: 0.528; 0.2: 0.692; 0.3: 0.757; 0.4: 0.891; 0.5: 0.899; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.558; 0.2: 0.654; 0.3: 0.709; 0.4: 0.803; 0.5: 0.799; ramp (twin dose: second photo only)

## mip1/frgc/madation_vitb16 (primary)

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 18.71%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.943 [0.921, 0.964] | 200 / 200 | thumb (0.985) | 0.633 | -0.041 [-0.064, -0.018] |
| R2>R3m (mirror, own rung) | 0.798 [0.758, 0.839] | 100 / 200 | sym (0.979) | 0.979 | -0.181 [-0.224, -0.138] |
| R2>R3 | 0.823 [0.791, 0.858] | 100 / 200 | bytes (0.794) | 0.674 | 0.029 [-0.014, 0.073] |
| R3>R4 | 0.668 [0.584, 0.753] | 100 / 100 | sym (0.641) | 0.641 | 0.028 [-0.088, 0.149] |
| R2>R4 | 0.916 [0.876, 0.952] | 100 / 200 | bytes (0.860) | 0.800 | 0.056 [-0.008, 0.129] |
| R2s>R4 (spread-matched one-person render) | 0.916 [0.864, 0.960] | 100 / 100 | thumb (0.920) | 0.709 | -0.005 [-0.071, 0.061] |
| R3m>R4 (mirror, own rung) | 0.684 [0.602, 0.764] | 100 / 100 | sym (0.921) | 0.921 | -0.237 [-0.328, -0.147] |
| R0>R4 | 0.999 [0.997, 1.000] | 100 / 200 | thumb (0.992) | 0.897 | 0.007 [-0.000, 0.025] |
| R3>RT (noise floor) | 0.512 [0.451, 0.579] | 25 / 25 | lapvar (0.530) | 0.515 | -0.018 [-0.095, 0.042] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.357 [0.310, 0.407]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.055 [0.028, 0.096]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.660 [0.590, 0.725]; R2i 0.425 [0.356, 0.497]; R2s 0.810 [0.719, 0.882]; R3 0.990 [0.946, 1.000]; R3m 0.960 [0.901, 0.989]; RT 1.000 [0.863, 1.000]
- latent distance medians: {'R2': 7.503108501434326, 'R2s': 5.579577922821045, 'R3': 6.427915334701538, 'R4': 6.460351228713989}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.576, coverage 0.860
- R3 vs R4 within 60 days: 0.671 [0.515, 0.814] n [35, 35]
- AG3 levels vs R2: 0.0: 0.492; 0.1: 0.610; 0.2: 0.673; 0.3: 0.767; 0.4: 0.849; 0.5: 0.920; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.568; 0.2: 0.637; 0.3: 0.699; 0.4: 0.779; 0.5: 0.848; ramp (twin dose: second photo only)

## mip1/frgc/madation_vitl14 (primary)

Reading A: mixed; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: identity reading; AG2: -; G-a: no published number given; benchmark EER 11.68%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.842 [0.797, 0.882] | 200 / 200 | thumb (0.985) | 0.633 | -0.143 [-0.187, -0.103] |
| R2>R3m (mirror, own rung) | 0.865 [0.824, 0.903] | 100 / 200 | sym (0.979) | 0.979 | -0.114 [-0.160, -0.071] |
| R2>R3 | 0.855 [0.818, 0.892] | 100 / 200 | bytes (0.794) | 0.674 | 0.062 [0.017, 0.105] |
| R3>R4 | 0.720 [0.635, 0.803] | 100 / 100 | sym (0.641) | 0.641 | 0.079 [-0.030, 0.194] |
| R2>R4 | 0.963 [0.934, 0.984] | 100 / 200 | bytes (0.860) | 0.800 | 0.103 [0.045, 0.170] |
| R2s>R4 (spread-matched one-person render) | 0.956 [0.923, 0.982] | 100 / 100 | thumb (0.920) | 0.709 | 0.036 [-0.016, 0.093] |
| R3m>R4 (mirror, own rung) | 0.676 [0.587, 0.764] | 100 / 100 | sym (0.921) | 0.921 | -0.244 [-0.347, -0.146] |
| R0>R4 | 1.000 [0.998, 1.000] | 100 / 200 | thumb (0.992) | 0.897 | 0.007 [0.000, 0.025] |
| R3>RT (noise floor) | 0.496 [0.442, 0.552] | 25 / 25 | lapvar (0.530) | 0.515 | -0.034 [-0.095, 0.012] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.237 [0.197, 0.282]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.020 [0.005, 0.050]
- attack detection (R4): 0.990 [0.946, 1.000]
- single-subject: R2 0.455 [0.385, 0.527]; R2i 0.240 [0.183, 0.305]; R2s 0.450 [0.350, 0.553]; R3 0.930 [0.861, 0.971]; R3m 0.890 [0.812, 0.944]; RT 0.920 [0.740, 0.990]
- latent distance medians: {'R2': 7.503108501434326, 'R2s': 5.579577922821045, 'R3': 6.427915334701538, 'R4': 6.460351228713989}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.532, coverage 0.860
- R3 vs R4 within 60 days: 0.728 [0.572, 0.863] n [35, 35]
- AG3 levels vs R2: 0.0: 0.507; 0.1: 0.537; 0.2: 0.627; 0.3: 0.774; 0.4: 0.921; 0.5: 0.965; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.541; 0.2: 0.617; 0.3: 0.708; 0.4: 0.813; 0.5: 0.882; ramp (twin dose: second photo only)

## mip1/frgc/selfmad_hrnet_w18__own (primary)

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: mixed; AG2: -; G-a: no published number given; benchmark EER 0.50%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.979 [0.967, 0.989] | 200 / 200 | thumb (0.985) | 0.633 | -0.006 [-0.021, 0.010] |
| R2>R3m (mirror, own rung) | 0.659 [0.607, 0.712] | 100 / 200 | sym (0.979) | 0.979 | -0.320 [-0.376, -0.263] |
| R2>R3 | 0.696 [0.654, 0.741] | 100 / 200 | bytes (0.794) | 0.674 | -0.097 [-0.149, -0.045] |
| R3>R4 | 0.650 [0.559, 0.742] | 100 / 100 | sym (0.641) | 0.641 | 0.010 [-0.118, 0.139] |
| R2>R4 | 0.822 [0.762, 0.877] | 100 / 200 | bytes (0.860) | 0.800 | -0.037 [-0.115, 0.045] |
| R2s>R4 (spread-matched one-person render) | 0.870 [0.806, 0.926] | 100 / 100 | thumb (0.920) | 0.709 | -0.051 [-0.127, 0.024] |
| R3m>R4 (mirror, own rung) | 0.685 [0.595, 0.772] | 100 / 100 | sym (0.921) | 0.921 | -0.236 [-0.336, -0.141] |
| R0>R4 | 1.000 [0.998, 1.000] | 100 / 200 | thumb (0.992) | 0.897 | 0.007 [-0.000, 0.025] |
| R3>RT (noise floor) | 0.534 [0.477, 0.599] | 25 / 25 | lapvar (0.530) | 0.515 | 0.005 [-0.080, 0.074] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.573 [0.522, 0.622]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.160 [0.112, 0.218]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.985 [0.957, 0.997]; R2i 0.985 [0.957, 0.997]; R2s 0.990 [0.946, 1.000]; R3 1.000 [0.964, 1.000]; R3m 0.990 [0.946, 1.000]; RT 1.000 [0.863, 1.000]
- latent distance medians: {'R2': 7.503108501434326, 'R2s': 5.579577922821045, 'R3': 6.427915334701538, 'R4': 6.460351228713989}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.488, coverage 0.860
- R3 vs R4 within 60 days: 0.649 [0.467, 0.808] n [35, 35]
- AG3 levels vs R2: 0.0: 0.495; 0.1: 0.517; 0.2: 0.593; 0.3: 0.739; 0.4: 0.821; 0.5: 0.842; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.528; 0.2: 0.515; 0.3: 0.561; 0.4: 0.642; 0.5: 0.716; ramp (twin dose: second photo only)

## mip1/frgc/selfmad_hrnet_w18__rel (secondary (printed beside))

Reading A: reads the benchmark; reading B: reads morphing; R3 vs R4: mixed; R2 vs R3: mixed; AG2: -; G-a: no published number given; benchmark EER 0.99%; p(R2 vs R4 <= 0.65) 0.0000

| Contrast | AUC [95%] | n | best baseline (AUC) | symmetry AUC | excess [95%] |
|---|---|---|---|---|---|
| R0>R2 | 0.929 [0.904, 0.952] | 200 / 200 | thumb (0.985) | 0.633 | -0.056 [-0.083, -0.029] |
| R2>R3m (mirror, own rung) | 0.694 [0.644, 0.746] | 100 / 200 | sym (0.979) | 0.979 | -0.285 [-0.339, -0.229] |
| R2>R3 | 0.739 [0.705, 0.777] | 100 / 200 | bytes (0.794) | 0.674 | -0.054 [-0.103, -0.005] |
| R3>R4 | 0.693 [0.607, 0.775] | 100 / 100 | sym (0.641) | 0.641 | 0.053 [-0.066, 0.172] |
| R2>R4 | 0.895 [0.844, 0.938] | 100 / 200 | bytes (0.860) | 0.800 | 0.035 [-0.038, 0.116] |
| R2s>R4 (spread-matched one-person render) | 0.931 [0.883, 0.969] | 100 / 100 | thumb (0.920) | 0.709 | 0.010 [-0.054, 0.076] |
| R3m>R4 (mirror, own rung) | 0.724 [0.642, 0.800] | 100 / 100 | sym (0.921) | 0.921 | -0.197 [-0.286, -0.113] |
| R0>R4 | 0.999 [0.996, 1.000] | 100 / 200 | thumb (0.992) | 0.897 | 0.006 [-0.001, 0.024] |
| R3>RT (noise floor) | 0.523 [0.476, 0.583] | 25 / 25 | lapvar (0.530) | 0.515 | -0.006 [-0.087, 0.060] |

Flag rates at the corrected-MAD22 EER threshold (rate [exact 95%]), both class policies, no verdict:
- genuine error, policy N (reconstruction = non-attack: R0 + R2): 0.512 [0.462, 0.562]
- genuine error, policy X (reconstruction inadmissible: R0 only): 0.175 [0.125, 0.235]
- attack detection (R4): 1.000 [0.964, 1.000]
- single-subject: R2 0.850 [0.793, 0.896]; R2i 0.885 [0.832, 0.926]; R2s 0.850 [0.765, 0.914]; R3 0.990 [0.946, 1.000]; R3m 0.970 [0.915, 0.994]; RT 0.960 [0.796, 0.999]
- latent distance medians: {'R2': 7.503108501434326, 'R2s': 5.579577922821045, 'R3': 6.427915334701538, 'R4': 6.460351228713989}
- R3 vs R4 matched bins (also reported): mixed, pooled 0.572, coverage 0.860
- R3 vs R4 within 60 days: 0.675 [0.514, 0.822] n [35, 35]
- AG3 levels vs R2: 0.0: 0.487; 0.1: 0.534; 0.2: 0.618; 0.3: 0.741; 0.4: 0.852; 0.5: 0.889; ramp (dose along two-person mixing; the second identity also moves the latent, perceptual and MS-SSIM targets)
- AG3T levels vs R2: 0.1: 0.501; 0.2: 0.542; 0.3: 0.603; 0.4: 0.680; 0.5: 0.731; ramp (twin dose: second photo only)

Not scored: ['mixfacenet_mad_smdd']
