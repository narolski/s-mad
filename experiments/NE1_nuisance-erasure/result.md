# Nuisance directions in the frozen candidate's own features (NE1): result

Status: read once, 13 Nov 2026 (`date` Fri Nov 13 07:55:10 PM CET 2026 to 07:56:44 PM). Not yet reviewed.
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
| Border | **inconclusive (border)** | separable on 3 of 5 seeds (needs 4); ceiling-fail 0; not-removable 0 |
| Splices (binding: fitted on L development hosts, read on L test hosts) | **inconclusive (splices)** | moves on 2 of 5 seeds; no change on 1; the H1dc control moves on 1 |
| Splices, training-list fit (printed only) | "does not move the trade-off" | no change on 4 of 5 seeds |
| Storage | **floor (not testable)** | H0's amsl112 storage shift ≤ 0.02 on 5 of 5 seeds |

The erasure-works check passed on all five seeds: erasing T's morph direction drops H0's AUC by 0.39-0.72. So the AUC
guards are sensitive.

## Readings (descriptive; point values per seed 403/404/405/406/407)

### Border

- **H0's border shift.** H0's paired rank shift is +0.34 to +0.41 (bootstrap intervals all above 0.31). In camera-pool
  percentile units, a bordered copy sits about 37 points above its own unbordered photo.
- **Linear decodability.** A border-presence probe on half-B rows reaches AUC 0.991-0.996.
- **After the half-A rank-1 eraser (H3).** The probe falls to 0.53-0.59. The shift does not go to 0; it reverses, to
  −0.25 to −0.37. Removal fractions are therefore above 1: H3 vs H1 1.91 / 1.77 / 2.15 / 1.58 / 1.99, and H0e vs H0
  1.90-2.41. The ceiling eraser fitted on half B gives nearly the same (H3c 1.70-2.09), so the half-A eraser generalises
  across persons.
- **Detection cost.** AUC(H3) − AUC(H1) on FFHQ landmark_combined is −0.008 / +0.002 / +0.000 / −0.005 / +0.001. That is
  within the 0.01 guard on every seed. The set is FFHQ, so this read is cross-domain.
- **Why the row is inconclusive.** The four separable conditions hold on every seed except the null comparison. H3
  beats the largest null removal on seeds 404, 406 and 407 (1.77 > 1.68, 1.58 > 1.27, 1.99 > 1.48) but not on 403
  (1.91 < 2.17) or 405 (2.15 < 2.28).
- **Caveat on the null (found after the read; post hoc).**
  - The first principal component of T's features carries 91% of their variance (seed 403).
  - So the 20 directions drawn from N(0, Cov(T)) are close to that component, not spread at random.
  - Their |cos| with the border direction is 0.14-0.63 (seed 403), and their AUCs range from 0.72 to 0.88.
  - The registered null is therefore a "top-component" null, not an isotropic one. It is harsh in a way the
    registration did not intend. The registered reading stands.
- **Secondary (99th-percentile cut of each head's own camera-pool scores).** H0 flags 5.4-19.9% of half-B bordered
  copies and 0-1% of their photos. H3 flags 3.8-9.9%. Under the old rule, H0 at logit 0 flags 24-75 of 1,435 half-B
  copies.

### Same-person splices (L test hosts, 191; matched S4 recall 0.69-0.80)

- **Binding read (H2d − H0, S3 share at matched recall).** +0.042 / −0.058 / −0.037 / +0.010 / −0.073. Two seeds pass
  the −0.05 bar. H2d − H1dc is −0.021 / −0.016 / +0.005 / 0.000 / −0.010.
- **Training-list read (H2 − H0, printed).** +0.010 / +0.026 / −0.005 / −0.021 / −0.058.
- **Caveat: C choice is uninformative.** Worst-group accuracy on the L development hosts is 0.00-0.05 for every C on
  every seed. The worst groups are ladder R4 at 112 px and the S4_face splices, which the group-balanced head
  misclassifies almost entirely at decision 0. So H2d's C choice rests on near-zero worst-group values. T's worst-group
  accuracy is 0.71-0.81 (not ≥ 0.98), so the training-list row is testable.

### Storage

- H0's paired rank shift of the stored copies against their own natives is −0.002 to −0.003 at amsl112 and −0.002 to
  −0.006 at fm61 (half-B MS1 FFHQ persons). The frozen Sb shows no storage reaction in this unit, so the storage row is
  at its floor.
- A storage probe still decodes stored against native at AUC 0.82-0.88. It falls to 0.56-0.59 after the H4 eraser.

## What this does and does not show

- **Shows.** The border cue is almost perfectly linearly decodable from Sb's penultimate features. One mean-difference
  direction learned on other persons removes most of that decodability and the frozen head's border shift, at no
  detection cost on FFHQ landmark morphs (within 0.01 on 5/5 seeds). The shift reverses instead of vanishing.
- **Does not show.** That the direction is specific beyond the dominant feature component: it fails the registered
  null on 2 of 5 seeds. It also does not show that last-layer reweighting moves the same-person-splice trade-off:
  2 of 5 seeds pass, 1 shows no change. No claim is made about storage: the frozen network has no paired storage shift
  to remove.
