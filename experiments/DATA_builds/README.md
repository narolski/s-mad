# Data builds (DATA): full record

Owner: data-building owner (DATA). Follows DOCUMENTATION.md. Queue: `REQUESTS.md`. Catalogue: `/DATA_CATALOG.md`.
Outputs: `/mnt/t7/smad_next/DATA/`. Code: `src/DATA/`. Clock times are from `date` on the DGX.

## Timeline (13 Nov 2026)

- 18:55-19:03 catalogue and request queue written (commits 4bc81cc, 50e1336).
- About 19:04 lead's go: R6 backup, D1a, D2, D5, D1d. D1b held; D1c, D3, D4, D6 and the home-disk copy wait for the author.
- 19:04 `cp -a` of `/dev/shm/smad_arms/{r6_frgc, r6_feret, r6_*.csv/json (+ .bak-partial145), r8_log.json, r8_pairs.csv}`
  to `/mnt/t7/smad_next/volatile_backup_20261113/`. sha256 computed on the source, `sha256sum -c` on the copy: all
  8,454 OK. `r6_feret` is an empty directory at the source. `/dev/shm` left untouched.
- 19:05-19:06 `SHA256SUMS` written for `volatile_backup_20261111` (17,506 files). Its r8_cv and r8_fm files (5,002)
  were checked against `/dev/shm/smad_arms` and match.
- 19:06 D1d test on 8 frames (`--limit 8`, outputs in `DATA/D1d/test8/`): 8 of 8 made, mean absolute difference from
  the input photo 0.09-0.12 grey levels on 3 checked.
- 19:07:04-19:08:35 D1d full run, 2 workers, nice 10, thread caps: 898 of 900. Two frames fail inside the unchanged
  tool (IndexError: landmark index 512 outside the 512-pixel frame). They are recorded as dropped; the tool is not
  changed. The diagnostic re-run wrote no image; its temporary list was removed.
- 19:09-19:10 D1a, D2, D5 lists.

## Commands (DGX; thread caps OMP/OPENBLAS/MKL/NUMEXPR = 2, nice 10)

```
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/DATA/d1d_fm_r2.py --workers 2 [--limit 8]
python3 -I src/DATA/d1a_coverage.py
python3 -I src/DATA/d2_meds_pairs.py
python3 -I src/DATA/d5_balanced_genuine.py
```

## Products

| Product | Path | Hash |
|---|---|---|
| R6 backup | `/mnt/t7/smad_next/volatile_backup_20261113/` (+ README.txt) | SHA256SUMS 9f1a8eb24646de14... |
| 11 Nov backup sums | `/mnt/t7/smad_next/volatile_backup_20261111/SHA256SUMS` | 77f37bf06f5fcf5e... |
| D1d renders | `/mnt/t7/smad_next/DATA/D1d/` | manifest.csv 1bfa13ecbbade173..., SHA256SUMS 02c40d154e24fb75... |
| D1a coverage | `DATA/D1a/coverage.csv` = `experiments/DATA_builds/D1a_coverage.csv` | 4bb5948f3717dd61... |
| D2 MEDS pairs | `DATA/D2/` (ids only, never in git); counts `D2_counts.json` | list 2ac6112ecbccfdaa... |
| D5 lists | `DATA/D5/`; cells `D5_cells.json` | all 8b27d67d9ee7699e..., no MEDS 02a05f1247c1bbd3... |

## Open items

- D5 needs border and eye-distance columns for the MS1 FFHQ, CelebA-HQ and AR1 / AF0 photos (a measurement from the
  existing .tem files and logs, with no image operation) before its border-free and high-resolution cells can be
  filled without MEDS.
- Nothing is kept only in `/tmp` or `/dev/shm`.
