# Protocol network, first tests (PN1): result (short page)

Status 11 Nov 2026, 20:05 CET: tier 0 being recomputed after amendment 4; tier 1 not run. Full record: `README.md`.
Registration: `prereg.md` (amendments 1 to 4).

## Provisional tier-0 version (kept, superseded)

The first tier-0 tables (CLIP heads A0 and B0, computed 19:35 to 19:53, read by the owner and reported to the lead at
about 19:53) were made with class balance over the whole manifest. The independent pre-run review (manifest counts
only, no score opened) showed that this balance made "stored at 61.2 px" a cue for "morph" in B0 and left a database
cue in A0. Those tables are kept under `tier0_v1_provisional/`, `tier0_v1_provisional_tables.md` and
`tier0_v1_provisional_key.csv` and are superseded by the recomputed tables (amendment 4: balance inside each stratum of
database by storage history, partner-safe folds, partner-cycle bootstrap, 224-px cues in the floor, camera-photo
threshold for the storage marks). They are not results of PN1.

## Compute

- DGX GB10 (shared), one process: about 37 minutes of GPU wall time for feature extraction, the JPEG-call check and the
  8-image test of the task script (allowance 30 minutes).
- Athena (account plgmultivision-gpu-a100, one A100-SXM4-40GB each, container image `fedeff10…`):

| Job | Purpose | State | Elapsed | GPU-hours |
|---|---|---|---|---|
| 3545947 | smoke 1 (arm Bn, 200 steps) + DINOv3 extraction (featx) | FAILED (path bug in the smoke job file; featx part done) | 0:04:14 | 0.07 |
| 3545968 | smoke 2 (arm Bn, 200 steps, 64 scored rows) | COMPLETED, SMOKE_RC 0, 1.24 it/s, peak 30,833 MiB | 0:05:21 | 0.09 |
| 3545976_[0-7] | eight fits A, B, Bn, C x seeds 401, 402 | submitted 20:45 | | |
| 3545977 | reference row: eight SMDD ViT-B/16 recipe retrains scored (amendment 5) | submitted 20:45 | | |
