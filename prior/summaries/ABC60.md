# ABC60: A, B and C arms on four backbones, five paired seeds

Terms: A = SMDD alone; B = A plus genuine photos; C = B plus our classical morphs. CN = ConvNeXt-T (IN-22k, from A30); VM = a Mamba vision backbone (exact variant not verified here); DeiT = data-efficient image transformer; D3 = DINOv3. Q = mean EER of H2 and H3 original. Native17 = mean EER over 17 native families. EER = equal error rate.

- **Question.** Does the full recipe (arm C) beat SMDD alone (arm A) on processing sensitivity and native accuracy, and does a Mamba backbone have an advantage?
- **What was done.** 60 fits (4 backbones x 3 arms x seeds 201 to 205), scored and analysed by the unchanged registered reader; closed 10 Nov 2026 with an independent review. Scoring cost 5,672 single-GPU seconds (1.5755 H100h); reservations total 245.17 H100h.
- **Result.** C minus A in EER points, all-five-seed 95% intervals. Q change: CN +1.490 [-0.511, +3.491], VM +2.450 [-1.299, +6.198], DeiT -0.866 [-2.720, +0.988], D3 +0.455 [-0.546, +1.456]. Native17 change: CN -6.727 [-13.688, +0.234], VM -12.446 [-24.955, +0.062], DeiT +1.040 [-9.328, +11.408], D3 -6.234 [-13.252, +0.784]. 412 inverted and 152 near-constant family fits among 2,400 evaluations.
- **Verdict.** ACCEPTED_QUALIFIED. Every interval includes zero: no Mamba advantage, no full120 success, no full-MAD22 claim. B minus A worsens Q in all four backbones.
- **Caveats.** Intervals are across five seeds on fixed seen images, not person-level; the registered CGD against C primary could not be evaluated (CGD outside this release); the earlier 64.56 H100h spend is an inherited, unreconstructed subtotal; MAD22 here is 185 and 4,069.
- **Sources.** `experiments/CONCLUSIONS.md` section "ABC60: independently accepted qualified fixed-population analysis"; `mambamorph-code/smadcvpr/PROTOCOL.md` line 20476; `experiments/primary120fit/`; artifact branch `recovery/final-gpu-boundary-v1`, analysis `d927af3`.
