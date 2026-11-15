Reviewer: results-reviewer (Opus), 13 Nov 2026, read-only. Report as returned (saved by the MS1 owner; scratch
scripts copied to `experiments/MS1_multi-source-training-set/review_scripts/part3/`).

# MS1 part 3 post-result review

Scope: commit 6c232f4; reader `src/MS1/ms1_part3.py` sha256 matches the pin in prereg Part 3. Recomputed
independently from the 15 fit tars (scores_eval / scores_train) and the 15 CFD held-out npz files. No valx, FST, A12SP,
benchmark or C2P file opened; nothing edited.

## 1. Verdict
Both verdicts follow the registered rules; spot checks match `ms1_part3.json`.
- H-mem supported: M(SbM3) < M(Sb) on 5 of 5 seeds (Sb 0.153/0.134/0.130/0.143/0.112; SbM3 0.110/0.085/0.097/0.090/0.088).
- H-new-4 inconclusive: ρ(Sb) > 0.2 only in A; |ρ(SbM3)| < 0.1 only in A and W; ρ(Sb) < 0.1 in B and L (2 of 4, short
  of the 3 needed to falsify).
Qualifications: H-mem's 5/5 holds for mean logit (registered), mean probability and rank AUC; it drops to 3/5 with
medians; which kinds drive it flips with the scale; SbM3 does not fit its training rows less tightly, which plain
dilution predicts first. H-new-4's registered statistic mostly measures sex, not femininity; within sex there is a
post-hoc signal for women under Sb (pooled ρ 0.25) that SbM3 removes.

## 2. Findings
F1 (major): the H-mem gap is mostly a few tails on unsaturated kinds. In mean logit, S4 (Sb median 0.73), S3 (0.28) and
zero/halves (0.17) carry M; without S3 and S4 SbM3 is lower on 2/5 seeds; without zero, halves, S3, S4 on 1/5. On
saturated kinds training and held-out medians agree within about 0.01 logits (af0_zero −3.50 vs −3.49 for Sb). The
zero/halves gap sits in the FRGC stratum (Sb 0.28-0.31), about 0 for colorFERET. Median-based M: SbM3 lower on 3/5
(SbM3 0.064, 0.0005, 0.030, −0.015, 0.066 vs Sb about 0.035). Rank AUC (P[training row more confident than held-out
row]): 5/5 (Sb 0.541-0.557 vs SbM3 0.514-0.535); under rank AUC R0, R2w and S0 favour SbM3 on 5/5, zero, halves, u50
the other way. The per-kind sentence in result.md holds only on the logit scale. Memorisation small in both arms.

F2 (major): "consistent with dilution" is weaker than stated. SbM3 fits saturated training rows at least as tightly
(genuine-kind training medians 0.01-0.05 logits more negative; attack kinds 0.02-0.04 more positive); the gap closes
because held-out tails move toward the training level. Exception S3: SbM3 worse on both training (median −1.90 vs
−2.49) and held-out (−1.45 vs −2.27). Fits better generalisation / regularisation from FFHQ content as well as or better
than reduced exposure. Confounds clean: all 5,535 / 8,798 training rows match their manifest by path, 0 kind
mismatches; FRGC/colorFERET rows identical across arms; held-out source mix matches training. Exposure ratio 0.625 for
every FRGC/colorFERET kind incl. S4 (the splice-share drop is the same dilution). SbV = Sb on every statistic (expected
null).

F3 (major): H-new-4 confounded by sex: ρ(Feminine, self-reported sex) = 0.865 over 597 models (307 F / 290 M; model code
and GenderSelf agree). Simpson-type reversal in group B under Sb: overall −0.068, within BF 0.273 (n = 104). Post-hoc
within-sex ρ(Feminine) for Sb: AF 0.24, BF 0.27, WF 0.16, LF 0.00; men 0.06-0.14; pooled F 0.248 (n = 307), pooled M
0.097. SbM3: F 0.007, M −0.125. SbV = Sb. The female flag skew and the Feminine correlation are the same signal.
SbM3's B and L negatives come from its men (BM −0.19) and bulk ranking; SbM3 flags 1 image in total in the group×sex
tables.

F4 (moderate): per-cell flag counts tiny and dominated by seed 406 (Sb AF 5, 5, 3, 13, 3 of 57; WF 5, 9, 3, 15, 1 of 90).
Group A n = 109; per-seed ρ 0.28-0.53.

F5 (minor): mark result.md reviewed; add the FS1 print mean logit drop complete → combined morphs Sb 1.67-2.70, SbM3
3.06-4.06 (consistent with combined morphs pushed toward genuine).

## 3. Replacement text for result.md
(Applied by the owner; see result.md, Part 3.)

## 4. Next steps, ranked
1. Apply the text; add rank-AUC and within-sex reads through a registered printed-only amendment (0 GPU).
2. Register the rank-AUC gap as the primary memorisation statistic for any later arm (0 GPU).
3. CFD morph pool scored by the 15 kept networks (H-new-1), with a within-sex read: Sb's misses on female-parent morphs
   below its misses on male-parent morphs if the smooth/feminine = morph cue holds (about 0.5 H100-h; pool is an author
   item; registration).
4. Sb at 0.63x steps (H-new-2): dilution predicts rank-AUC gap ≤ about 0.53 and CFD flags ≤ 0.5x Sb; F2 weakly predicts
   the flags will not fall; falsified if ≥ 0.8x Sb (3-4 H100-h; author).
5. Splice-share-matched SbM3 (H-new-3): S4 gap back toward 0.7 and S4 vs S0/S3 AUC to Sb's; CFD flags about 0 (about 5
   H100-h, post-deadline).
6. CelebA-HQ fourth source (5-8 H100-h, post-deadline): miss guard on an unseen-pipeline attack pool; sex-stratified
   CFD flag read and within-sex ρ(Feminine) as printed guards. CelebA-HQ (super-resolved, heavy makeup) is the source
   most likely to teach "smooth = genuine".
Risk: any SbM3 claim stays "fewer genuine flags with a printed attack-side cost"; neither part-3 read is a mechanism
claim; H-mem cannot be cited as evidence that dilution causes the CFD gain.
