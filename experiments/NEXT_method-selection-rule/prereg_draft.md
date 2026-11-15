# Selection rule for the next method version (DRAFT, not yet registered)

Drafted by the lead on 13 Nov 2026 (machine clock in the commit), merging the proposals of the DINOv3 owner (BB2 plan, section 7) and the resolution-study owner (RZ1 plan). The author answered "1. Go with your proposal." to the lead's statement that one rule across all new arms would be merged and brought to him. This file is that rule. It becomes binding at the commit that removes "DRAFT", after a pre-run check, and before any challenger arm below has been read.

## Scope

The current method stays as frozen by the author on 13 Nov: arm Sb (CLIP ViT-B/16 + LoRA), seeds 403-407, read once on MAD22. This rule chooses the method of the NEXT version, which is read once on the sets that are still sealed (FRLL-Morphs, FEI, MorDIFF, the DiM families). MAD22 is a seen benchmark for the next version and is never an input to this rule. Every input is a registered read on development data.

## Default and challengers

Default: Sb, as trained on the challenger's own platform at the challenger's own seeds (the comparator).

Challengers (closed list; a combination of two is a new arm that needs its own registration and its own five seeds before it can be a challenger):
1. Second morphing engine (SbFM; AB1 owner).
2. GAN morphs with render-matched genuine examples (GX; GX1).
3. Resize mixing at 224 (SbM, SbMR; RZ1 wave 1).
4. Native centre crop (Sbc) and 512 input (Sb512, SbMR512; RZ1 wave 2).
5. Border-crossed (Sbx; AB1 owner).
6. Same-person blends as genuine (SE; SE1, H100 block).
7. DINOv3 with the rule-fixed learning rate (BB2 E3 Sb), compared unpaired with the CLIP Sb trained on WCSS H100 (AB1).

## A challenger qualifies only if all of these hold on its five seeds (four read seeds are the minimum; fewer is "not read")

a. Detection: FFHQ landmark_combined AUC at least the comparator's + 0.03 on at least 4 of 5 seeds, paired within seed. For the unpaired DINOv3 comparison: seed median at least 0.904 and Mann-Whitney p at most 0.05 against the comparator's five seeds.
b. Storage: the rise in own-rule flags on stored genuine photos is at most the comparator's + 0.02 at both storage sizes on at least 4 of 5 seeds, with a plain-training control of the same platform meeting its control bar; storage evasion of morphs is falsified.
c. Unseen genuine sources: mean flag rate over the low-resolution families at most the comparator's + 0.01 (+ 0.02 for the unpaired DINOv3 comparison), and the own rule transfers on the NIST mugshots on at least 4 of 5 seeds.
d. Same-person blends and borders: same-person splice flags at most the comparator's + 0.05; flags on border-blanked camera photos at most the comparator's.
e. Stability to the viewer's resize: no change above 0.05 in the own-rule flag rate on native genuine photos under any of the nine test kernels (read for every challenger whose pack carries the kernel cross table; otherwise stated as not read and the challenger cannot qualify on a resolution claim).
f. Every guard of the challenger's own registration is met, and its platform and training-fit gates passed.

## Choice among qualifiers

If none qualifies, Sb stays. If one qualifies, it replaces Sb. If several qualify, the one with the largest seed-mean gain in (a) is chosen; a tie within 0.005 is broken by the order of the list above. At most one arm is chosen; the others are reported as ablation rows with all their reads. The choice among several qualifiers by largest gain favours lucky seeds; the paper states this and reports every qualifier.

## The read of the next version

Once, on the still-sealed sets, on the GPU model and software build that trained the chosen arm, with a byte-identity gate on development rows first; the deciding measure and forms as in the final protocol of the MAD22 read. MAD22 numbers of the next version are printed as "seen during development".

## Disclosures

This rule was written after the reads of 13 Nov on the CLIP arms (which fix the comparator's known levels) and before any read of a challenger. The margins come from the two owners' proposals and from the seed-to-seed spread seen on 13 Nov (about 0.02-0.04 AUC on landmark_combined).
