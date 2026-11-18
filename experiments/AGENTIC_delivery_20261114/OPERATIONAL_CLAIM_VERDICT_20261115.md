# Operational training claim (contribution 3) — verdict from existing admitted data
# + SelfMAD seed state and forecasted ETAs — 2026-11-15T19:1xZ (continuation session)

Author: continuation session MAIN. No new training, no cluster job changes, no new scores read. Clone-safe: all verdicts trace to admitted reports (SHAs below).

## Verdict decision (one line)

**UNSUPPORTED — the joint operational claim ("matched-control (Sb) training improves two-person face-splice morph detection at comparable genuine false alarms while reducing artifact-induced responses") is NOT established by existing admitted evidence. Narrower supported wording is mandatory until the registered SPRINT5 paired-ranking read closes (or the author narrows contribution 3 accordingly).**

## Evidence actually held (report-level, independently reviewed)

| Contrast | Admitted result (source report) | What it supports | Does NOT support |
|---|---|---|---|
| AB1 S3-vs-S4 development AUC (H100 408–412, 8 arms) | Sb .755–.804 vs Sp .691–.722; Sb flags 36–41% vs Sp 70–74%; H-sp3/H-sp3b supported 5/5 (`AB1 result.md` 68d4878e; REVIEW_AB1_20261113) | Matched same-person-splice negatives reduce same-person-splice response and improve this construction's development ranking | Matched-BPCER utility; general contributor recognition; any fixed-operating-point face-splice sensitivity |
| AB1 storage | Genuine flag rise on storage: others .055–.385 vs Sb .000–.045 (own rule) | Descriptive attenuation of storage-induced own-rule false alarms for Sb | "Artifact removal"; registered composite storage verdict for Sb remains INCONCLUSIVE (5/5 then 3/5); R1 not passed |
| Batch C (166 checks independently reproduced 2026-11-14; review `eadbd510…`) | R4/R3 Sb−SpV +.0481 [.0269,.0722]; BN−BV −.0030 [−.0089,.0045]; Clean80 +.0818 [.0535,.1083] and −.0247 [−.0455,−.0050] | Ranking improvements on registered whole-frame contrasts; all 5 outcomes retained | Fixed-operating-point attack/genuine-false-alarm claim; 312-image diversity confound remains; "point_difference" = seed-mean difference, not absolute rates |
| XF1 (frozen 403–407) | Sb−B +.011 [−.010,.031] INCONCLUSIVE; Sb−A +.025 [.003,.048] marginal; grey-blanking warp FA 47–99% | Nothing positive; diagnostic only | Improved blending detection |
| TT1 | Sb fresh-source genuine transfer 4/5 | Unseen-genuine handling (genuine-only) | No attack side → no joint utility |
| FINAL (MAD22 corrected) | History-matched 4-family EER 3.37% vs SelfMAD 4.72% — threshold-fragile parity verdict; landmark-only 6.32% vs 7.37% not separated | "Where we stand" ranking | Superiority; shortcut-free; not a fixed-BPCER face-splice sensitivity |

Cross-report combination is prohibited by the registered wording rules (different networks/platforms/populations/uncertainty units). Additionally, the frozen SPRINT5 `ranking_statistics.py` analyze() does NOT yet emit the registered absolute per-seed S3/S4 false alarms, absolute S4 detection or achieved-BPCER tables (implementation gap documented and repaired as `reader_v2` source, SHA `93b2ff22…`, awaiting independent review), so no admitted report can currently adjudicate the joint operating-point claim even after all 15 SPRINT5 fits arrive.

## Permitted sentence for the manuscript until that read closes

"Matched-control training improves selected development rankings and attenuates some own-rule artifact false alarms; preserved face-splice attack sensitivity at comparable genuine false alarms has not yet been established."

This matches the narrower contribution-3 wording required by the Codex stop rule ("ranking improvement alone does not close the claim; retain Sb and narrow contribution 3"). The manuscript must NOT claim artifact suppression, superiority, or comparable-false-alarm preservation.

## SelfMAD (own-morph family) seed state — live poll 2026-11-15T18:51:52Z (sacct via WCSS)

| Task | State | Elapsed | Start | End (cluster tz) |
|---|---|---|---|---|
| 6310127_401 | COMPLETED 0:0 | 63827 s (17.73 h) | 11-14 08:07:23 | 11-15 01:51:10 |
| 6310127_402 | COMPLETED 0:0 | 63293 s (17.58 h) | 11-14 08:09:24 | 11-15 01:44:17 |
| 6310127_403 | **COMPLETED 0:0** (new) | 63284 s (17.58 h) | 11-15 01:44:20 | 11-15 19:19:04 |
| 6310127_404 | **COMPLETED 0:0** (new) | 63758 s (17.71 h) | 11-15 01:51:14 | 11-15 19:33:52 |
| 6310127_405 | RUNNING | 1965 s at poll | 11-15 19:19:07 | ETA below |

**Forecasted ETAs (based on the four completed seeds: mean 63 540 s = 17.65 h, max 63 827 s = 17.73 h):**
- Seed 405: ETA ≈ 2026-11-16 **12:55 CET** (mean basis) to **13:10 CET** (worst case 17.73 h).
- Therefore the five-seed SelfMAD family cannot be scientifically read tonight; 405 lands midday tomorrow, then still requires collection receipt, eligibility admission and the already-registered post-eval checks before any number enters the manuscript.

## Disposition for tonight

1. Verdict above is defensible and final FOR TONIGHT: no new training, no new scoring.
2. Manuscript keeps: narrow sentence (pre-registered wording), pending FRLL cells, SelfMAD-MAD22 rows marked as pending/missing with 2 completed + 2 collected + 1 running seeds disclosed.
3. When 405 completes and its archive/duration receipt is collected (~13:10 CET 16 Nov), the seed ledger row is updated; the claim verdict changes only through the separately registered SPRINT5 reader read (reader_v2) and admission, not through this continuation.
