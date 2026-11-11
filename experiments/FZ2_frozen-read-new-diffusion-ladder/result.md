# FZ2 Frozen read of the new diffusion ladder: result

Status 11 Nov 2026, 21:50 CET: **secondary read (DG1 production set B) done; primary read (DG1 add-on) pending** —
2 of 8 add-on shards generated and extracted; shards 2–7 are queued on Athena (start estimate 12 Nov 02:27). The
registered readings of H-new-1 to H-new-4 are made on the add-on only; nothing below is a registered verdict.
Registration `prereg.md` (20:32, before any DG1 feature), full record `README.md`.

## Production set B, secondary replication (`read_prod.json`; per image `/mnt/t7/smad_next/FZ2/read_prod_items.csv`)

536 hosts (FRGC 427, colorFERET 109), 20 steps; REC, MIR, SAME, X 536 each; two-person dose α 0.1–0.4, 100 hosts each.
Features on the DGX (deviation, `prereg.md`); probes out of fold with whole partner cycles held out; two-way person
bootstrap, B = 10,000. AUC: positive = first named.

**Frozen SMDD heads and the release head, no refit (H-new-3 contrasts; no FRESH rung in this run):**

| | head s401 | heads s402–s405 | released FE ViT-L/14 head |
|---|---|---|---|
| X20 vs SAME20 | 0.662 [0.622, 0.699] | 0.660–0.661 | 0.665 [0.625, 0.703] |
| best baseline for X20 vs SAME20 | thumb32 0.700 [0.656, 0.741] | | thumb32 0.700 |
| excess over the best baseline | −0.038 [−0.094, +0.019] | | −0.035 [−0.089, +0.023] |
| SAME20 vs REC20 | 0.378 [0.356, 0.401] | | 0.396 [0.374, 0.417] |
| X20 vs REC20 | 0.537 [0.496, 0.578] | | 0.561 [0.518, 0.604] |
| MIR20 vs REC20 | 0.702 [0.681, 0.723] | | 0.722 [0.702, 0.742] |

X20 vs SAME20 without flagged items 0.662 [0.619, 0.702]; FRGC 0.664, colorFERET 0.683. The five baselines for X20 vs
SAME20: PNG bytes 0.603 (X lower), Laplacian variance 0.695 (X lower), asymmetry 0.631 (X lower), thumb32 0.700,
surround-only thumbnail 0.669. (H-new-3's falsifier, applied here descriptively, would fire: the excess interval
includes 0.)

**Probes (clip_mad; dinov2 in brackets):**
- Shared direction D_SR (trained SAME20 vs REC20, 0.999 [0.998]): X20 vs REC20 0.987 [0.985], MIR20 vs REC20 0.994
  [0.980], and it ranks SAME20 above X20 (X20 vs SAME20 0.162 [0.183]).
- Probe X20 vs REC20 0.995 (excess over thumb32 +0.19); MIR20 vs REC20 1.000.
- **P_XS (trained X20 vs SAME20): 0.941 [0.923, 0.957] (0.953).** Stratified by input-pair disagreement d (pooled
  fifths): 0.933 [0.911, 0.952], Δ = +0.008 [+0.001, +0.017]; X against the top-fifth-d SAME images 0.912 [0.874, 0.945]
  (108 images). Within-stratum AUCs 0.97, 0.93, 0.94, 0.94, 0.88. Median d: X 29.1, SAME 22.5 grey levels. Spearman of
  the score with d: −0.03 inside X, +0.16 inside SAME. (H-new-4's falsifier, applied descriptively: Δ ≤ 0.05.)
- P_XS scores by rung (mean decision value): SAME −2.81, MIR −0.64, REC +2.21, X +2.17, two-person dose α 0.1 / 0.2 /
  0.3 / 0.4: +2.37 / +2.46 / +2.52 / +2.42 (dose vs SAME 0.96 at every α; dose vs REC 0.52–0.55). Dinov2 the same
  pattern. So in this run the P_XS direction separates the same-person mix from every other rung, including the
  reconstruction and the 10% two-person dose.

## Primary read (add-on): pending

H-new-1 (fresh-noise rung), H-new-2 (noise-only vs semantic-only), H-new-3 (with FRESH and excess), H-new-4 (with the
same-person dose series) — after all add-on shards are extracted.

## Compute

Athena: job 3545969 submitted 20:39, cancelled 21:31 before it started (0 GPU-hours). DGX GB10: production features
about 10 min (both backbones), add-on extraction running per shard.
