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

- 19:12 lead's go for the D5 measurement. 19:13 test on 8 frames; 19:13:51-19:14:47 `d5_measure_border.py`:
  border fraction (exactly-black share of the 512 frame, TT1 definition) of 13,024 frames (MS1 FFHQ 900, CelebA-HQ
  kept 9,898, AR1 1,582 and AF0 644 after val-reserved persons are left out); none unreadable. Border none / under 5% /
  5% or more: FFHQ 19 / 384 / 497; CelebA-HQ 124 / 5,227 / 4,547; AR1 1,353 / 124 / 105; AF0 265 / 209 / 170.
  The source eye distance is in no existing record of these frames (`73_delin_align` logs no scale; the soften logs
  hold the frame-side distance, about 130 px), so it is left empty. Measuring it would need face detection on the
  source images (CPU, measurement only): not done, needs the lead's go.
- 19:15 D5 version 2 lists (two designs, each with and without MEDS); version 1 files kept, superseded.
- FaceMorpher tool limit (D1d): FFHQ keys 69321 (af0) and 08060 (hold-out) fail with IndexError in the unchanged tool.

- 19:19 lead's go for source eye distance; first run with 4 workers stopped by me at 19:38 on the lead's load
  request (it could not resume; no output kept); restarted 19:39 resumable, 2 workers, one thread per process
  (onnxruntime sessions re-created with intra/inter-op threads 1; cv2.setNumThreads(1)), nice 19; ended about 20:22.
  13,024 of 13,024 measured, all pass the aligner's frontal filter; the geometric border from the detected eyes agrees
  with the measured black-pixel border within 0.02 on AF0 644/644, AR1 1,582/1,582, CelebA-HQ 9,317/9,898, FFHQ
  855/900. Median source eye distance: FFHQ 259, CelebA-HQ 254, AR1 260, AF0 65 px.
- 20:17-20:20 partner-overlap audit (`PARTNER_OVERLAP_AUDIT.md`), urgent request of the lead.
- About 20:22 D5 version 3 lists; 20:22 battery person tables (D7) and GD overlap (D8): every battery set and every
  GD family has 0 persons in common with every arm's training persons (incl. SbM3 / SbM3S FFHQ persons and GX1's
  planned training persons).

## Commands (DGX; thread caps OMP/OPENBLAS/MKL/NUMEXPR = 2, nice 10)

```
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/DATA/d1d_fm_r2.py --workers 2 [--limit 8]
python3 -I src/DATA/d1a_coverage.py
python3 -I src/DATA/d2_meds_pairs.py
/home/narolski/mambamorph-code/.venv-spark/bin/python -I src/DATA/d5_measure_border.py --workers 2 [--limit 8]
nice -n 19 .venv-spark python -I src/DATA/d5_measure_ied.py --workers 2   (OMP/OPENBLAS/MKL = 1)
python3 -I src/DATA/d5_balanced_genuine.py
python3 -I src/DATA/partner_overlap_audit.py
python3 -I src/DATA/battery_persons.py
```

## Products

| Product | Path | Hash |
|---|---|---|
| R6 backup | `/mnt/t7/smad_next/volatile_backup_20261113/` (+ README.txt) | SHA256SUMS 9f1a8eb24646de14... |
| 11 Nov backup sums | `/mnt/t7/smad_next/volatile_backup_20261111/SHA256SUMS` | 77f37bf06f5fcf5e... |
| D1d renders | `/mnt/t7/smad_next/DATA/D1d/` | manifest.csv 1bfa13ecbbade173..., SHA256SUMS 02c40d154e24fb75... |
| D1a coverage | `DATA/D1a/coverage.csv` = `experiments/DATA_builds/D1a_coverage.csv` | 4bb5948f3717dd61... |
| D2 MEDS pairs | `DATA/D2/` (ids only, never in git); counts `D2_counts.json` | list 2ac6112ecbccfdaa... |
| D5 lists v2 | `DATA/D5/`; cells `D5_cells.json` | bied_all b45c6ed9e9884729, bied_nomeds e18dac9ac10c2d5d, border_all 46d237d03d60f1fc, border_nomeds 97b3f30c431e0b1c; frames_measured 6090a0ba6398f6a9 |

## Open items

- D5: border is measured; the source eye distance of the MS1 FFHQ, CelebA-HQ and AR1 / AF0 frames needs face
  detection on their source images (CPU, measurement only), awaiting the lead's go. The border-only lists differ in
  source mix between cells (border-free rows are mostly AR1 and MEDS, bordered rows mostly TT1): a user stratifies
  by source.
- Nothing is kept only in `/tmp` or `/dev/shm`.
