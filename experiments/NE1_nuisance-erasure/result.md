# Nuisance directions in the frozen candidate's own features (NE1): result

Status: read once, 13 Nov 2026 (`date` Fri Nov 13 07:55:10 PM CET 2026 to 07:56:44 PM). Reviewed (post-result,
experiments/reviews/REVIEW_NE1_20261113.md: needs qualification); corrections applied. Figures marked *post hoc* come
from the reviewer's recomputation on the saved features (`posthoc/a1.py` `53db928b…`, `posthoc/a2.py` `3e22017f…`).
Registration 9ef5884 (pre-run check 653a766, fixes F1-F8). Post-freeze diagnostic on development rows only. The frozen
Sb networks (seeds 403-407) are not changed and the sealed read is not touched.

## Run

- **Extraction.** Athena job 3550470 (plgrid-now, node t0004, A100-SXM4-40GB), 19:47:17 to 19:53:52, exit 0.
  Container torch 2.2.1 / CUDA 12.1 / cuDNN 8902, matmul TF32 off, cuDNN TF32 on.
- **Result tar.** `NE1_feats.tar` sha256 `18d13b10128274c1…`. It checks against its .sha256 on Athena and in
  `/mnt/t7/smad_next/NE1/results/`, and its inner SHA256SUMS pass. 15 feature files (5 networks × 3 manifests).
- **Platform gate.** H0's logits on the 3,417 G rows are byte-identical to TT1-FS pn1fs on all 5 networks (max |Δ| 0).
  Logit = feature · w + b within 1e-4. All five networks are "certified". This also shows that A100 SXM4 and the pn1fs
  A100 PCIe give the same bytes.
- **Reader.** `ne1_heads.py` (`5c6fdcd2…`), run once. Output `ne1_read.json` (`f3f371ae2dbbeea4…`).

## Registered table (section 7)

| Row | Reading | Count |
|---|---|---|
| Border | **inconclusive (border)** | literal count: separable on 3 of 5 seeds (needs 4); ceiling-fail 0; not-removable 0. Every "separable" seed is an over-correction (removal > 1), see below |
| Splices (binding: fitted on L development hosts, read on L test hosts) | **inconclusive (splices)** | moves on 2 of 5 seeds; no change on 1; the H1dc control moves on 1 |
| Splices, training-list fit (printed only) | "does not move the trade-off" | no change on 4 of 5 seeds |
| Storage | **floor (not testable), by construction** | H0's amsl112 storage shift ≤ 0.02 on 5 of 5 seeds; the camera-pool unit saturates for FFHQ photos (see below) |

The erasure-works check passed on all five seeds: erasing T's morph direction drops H0's AUC by 0.39-0.72. So the AUC
guards are sensitive.

## Readings (descriptive; point values per seed 403/404/405/406/407)

### Border

- **H0's border shift.** H0's paired rank shift is +0.34 to +0.41 (bootstrap intervals all above 0.31). In camera-pool
  percentile units, a bordered copy sits about 37 points above its own unbordered photo.
- **Linear decodability.** A border-presence probe on half-B rows reaches AUC 0.991-0.996. After the eraser it falls
  to 0.53-0.59, pooled over masks; the pooled value hides the CFP-FF and MSU-MFSD residual.
- **The rank shift reverses.** After the half-A rank-1 eraser, the shift does not go to 0; it reverses, to −0.25 to
  −0.37.
- **In logits, the mean is cancelled** (*post hoc*). The eraser cancels the mean paired shift: removal is 0.88-1.06
  for H3 vs H1, and 0.90-1.04 for H0e vs H0.
- **The residual is skewed by mask** (*post hoc*).
  - CFP-FF and MSU-MFSD stay positive (+0.14 to +0.44 logit). The other five masks go negative.
  - 82-90% of copies now rank below their own photo, where 96-97% ranked above before.
- **What the removal fractions above 1 mean.** The rank-unit removals are H3 vs H1 1.91 / 1.77 / 2.15 / 1.58 / 1.99,
  H0e vs H0 1.90-2.41 and the ceiling H3c 1.70-2.09. They mean over-correction, not more than full removal. A border
  dependence of the same size, with the opposite sign, remains (|H3| 0.25-0.37 against |H1| 0.31-0.44). The literal
  ≥ 70% rule counts this as removal; a two-sided reading (|1 − removal| ≤ 0.3) would not, on 0 of 5 seeds (*post hoc*).
- **Flags** (*post hoc*). The lead's draft defined removal on flags. At the 99th-percentile camera cut, excess flags
  over photos fall from H1 to H3 by only 21-43%: 0.123→0.081, 0.075→0.055, 0.048→0.038, 0.048→0.033, 0.166→0.094.
- **Detection cost.**
  - AUC(H3) − AUC(H1) on FFHQ landmark_combined is −0.008 / +0.002 / +0.000 / −0.006 / +0.001, within the 0.01 guard on
    every seed. The set is FFHQ, so this is cross-domain.
  - Recall is not free (*post hoc*). At each head's own 99th-percentile camera cut, landmark_combined recall falls by
    0.03-0.09 on 4 of 5 seeds (H3 vs H1).
  - The border direction overlaps the head: cos(d3, w) is 0.29-0.52.
- **Why the row is inconclusive.** The four separable conditions hold on every seed except the null comparison. H3
  beats the largest null removal on seeds 404, 406 and 407 but not on 403 (1.91 < 2.17) or 405 (2.15 < 2.28).
- **The null erases the detector** (*post hoc*).
  - T's first principal component is the detection axis: it carries 91% of the variance, its AUC on T is ≥ 0.998, and
    |cos(PC1, w)| is 0.98.
  - The registered N(0, Cov(T)) draws lie near it (median |cos| 0.93-0.95), so the null erases the detector. Their
    landmark AUC drops to 0.72-0.90.
  - A post hoc isotropic null removes ≤ 0.10.
  - The registered reading stands.
- **Secondary (99th-percentile cut of each head's own camera-pool scores).** H0 flags 5.4-19.9% of half-B bordered
  copies and 0-1% of their photos. H3 flags 3.8-9.9%. Under the old rule, H0 at logit 0 flags 24-75 of 1,435 half-B
  copies.

### Same-person splices (L test hosts, 191; matched S4 recall 0.69-0.80)

- **Binding read (H2d − H0, S3 share at matched recall).** +0.042 / −0.058 / −0.037 / +0.010 / −0.073. Two seeds pass
  the −0.05 bar. Every bootstrap interval for H2d − H0 includes 0.
- **H2d is a reweighted refit, not a group-robust solution.**
  - Its C choice is degenerate: worst-group accuracy on the L development hosts is 0.00-0.05 at every C on every seed.
    The worst groups are ladder R4 at 112 px and the S4_face splices. The chosen C were 10 / 10 / 1 / 0.01 / 10.
  - H2d − H1dc is within 0.021 on 5 of 5 seeds, so the group weights add nothing beyond refitting on L.
- **Threshold-free read.** The S4-vs-S3 AUC is 0.70-0.75 for every head, within 0.011 of H0 on 5 of 5 seeds. No
  last-layer change separates S3 from S4 better.
- **Training-list read (H2 − H0, printed).** +0.010 / +0.026 / −0.005 / −0.021 / −0.058. T's worst-group accuracy is
  0.71-0.81 (not ≥ 0.98), so this row is testable; it reads "no change" on 4 of 5 seeds.

### Storage

- **Floor by construction.** Under H0, the half-B FFHQ natives already sit at camera-pool rank 0.988-0.990 (*post
  hoc*), so the unit cannot show a shift above about 0.012, below the 0.02 floor. The registered H0 shifts are −0.002
  to −0.003 (amsl112) and −0.002 to −0.006 (fm61). The storage row is untestable in this unit. This is a design flaw of
  the registration: the camera reference pool was chosen for the border read.
- **Sb does react to storage** (*post hoc*). Mean logit changes by −0.05 to −0.22. Own-rule flags (logit 0) rise from
  0.7-4.0% on natives to 2.1-6.9% at fm61 and 1.4-7.0% at amsl112, as MS1 and FS1 found.
- **Probe.** A storage probe decodes stored against native at AUC 0.82-0.88. It falls to 0.56-0.59 after the H4 eraser.

## What this does and does not show

- **Shows.**
  - The border cue is almost perfectly linearly decodable from Sb's penultimate features (probe AUC ≥ 0.99).
  - One mean-difference direction learned on other persons cancels the mean border shift in logits. But it
    over-corrects five masks and under-corrects CFP-FF and MSU-MFSD.
  - Bordered-copy flags at the 99th-percentile cut fall by only 21-43%.
  - AUC is unchanged. Recall at the 1% camera cut falls by up to 0.09.
  - Last-layer refits, reweighted or not, leave the S3/S4 separation unchanged (threshold-free AUC within 0.011).
- **Does not show.**
  - That the border response is a single direction: the mask-specific residuals suggest it is not.
  - That it is separable from the detection axis (cos with w 0.29-0.52).
  - That last-layer reweighting moves the same-person-splice trade-off.
  - Anything about storage: the unit saturates, and Sb's storage reaction (MS1, FS1) stands.
- **Wording for the paper.** Not "the border cue is a removable linear direction". At most: "linearly decodable (probe
  AUC ≥ 0.99); a rank-1 eraser cancels its mean but over-corrects it per mask".

## Follow-ups proposed by the reviewer (CPU only on the saved features; would need a registration, NE1b, first)

- **H-new-1: rank greater than 1.** A rank-7 per-mask or LEACE border eraser, read with two-sided and flag-based
  removal.
- **H-new-2: shared axis.** An eraser orthogonalised to w or PC1, plus in-domain recall at a fixed false-alarm rate.
- **H-new-3: feature ceiling for splices.** An S4-vs-S3 linear probe fitted on L development hosts and read on test
  hosts. A ceiling of about 0.77 means a backbone limit; ≥ 0.85 means the head is the bottleneck.
- **H-new-4: storage re-read.** Use the FFHQ resmatch genuine set as the reference pool.
