# TASK_A_SCORE_DISPATCH_20261116T0355Z — scoring retrainów ukończony (15/15 × v1+v2)

## Wynik serii 1 (GB10, LOC /mnt/t7/smad_next/AD5/scores_retrains/)
**30/30 npz — recepcja czysta, bad=0** (`RECEIPTS.json` + `SHA256SUMS.txt` w katalogu; SHA256 niezależnie policzone
i wpisane do receipts):
- madation_B_s401–s405 ×(v1 171s, v2 ~176s) — rows=28,253 (prod lista v1 − 9 braków), uniq, finite
- madation_L_s401–s405 ×(v1 ~603s, v2 ~619s) — rows=28,253, uniq, finite
- mixfacenet_X_s401–s405 ×(v1 ~258s, v2 ~264s) — rows=29,049 (prod lista v2, 0 braków), uniq, finite
Serie 1 + selfmad: **20/26 przebiegów z komplanu 26 zamknięte**:
- selfmad s401 d3a53c52…, s402 9099f674…, s403 03a812c1…, s404 1fe532a7… (23,145 rows; mode own)
- brakujące: selfmad s405 (trening WCSS do ~12:57 CET) + Sb s403–s407 (zrobione 15 XI w FRLL_READ_RESULTS.json ✓)

## Pipeline rejestracji (audyt)
- Crops: regen GB10 (`regen_crops_dgx_20261116.sh`) z packów rs1a_pack+amend+raw (SHA-verified po stronie pulla);
  byte-identity vs prod rented: v1 22,664/28,253 (80.2%), v2 21,619/29,049 (74.4%); identyfikatory plików OK.
- Score listy: PROD score_v1.csv (28,262 − 9 bez……→28,253) / score_v2.csv (29,049) — kopie na regen_run; oryginały w results_rented.
- Koder: score.py pin 56bb1244…, ar1_common 42806acb… (asserts w ad5_score_athena.py); a36 conversions z
  equivalence-check coefficients (convert.json per retrain; a36 weryfikuje zgodność z training.log).
- Kwalifikatory: (1) nasze wlasne retrains vs released weights (RW) — etykiety osobne (NAME != AS), (2) crop regen
  GB10 (środowiskowa różnica GPU GB10/torch 2.12 vs prod) GPU GB10/torch 2.12, ~20–25% cropów nie byte-identycznych z prod) — before/after per-id join
  spójny dzięki sanity release re-score na TYCH SAMYCH cropach (w toku, process release_sanity_dgx_20261116.sh),
  (3) 9 braków v1 (lista w MONITOR 0025Z).
- Next: determinism check (release re-score vs prod npz per-id), potem EER/AUC per-family (FRLL roster 7,265)
  „before S → after H" dla 5 seedów × 3 metod (B/L/X) (B/L/X) + MAD22 corrected cell per metodę — po zejściu release sanity.

## Klastry
- WCSS: 405 RUNNING (ETA treningu ~12:57 CET → scoring selfmad ~10 min).
- Athena: 3555043 PENDING (nodes fail*); pełny fallback GB10 działa — Athena backup tylko.
