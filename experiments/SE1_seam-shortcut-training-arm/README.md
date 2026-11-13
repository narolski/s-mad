# Same-person blends as negatives (SE1): full record

## 1. Question and current answer

13 Nov 2026. Can the protocol network be trained to depend on two-identity content rather than on a blend inside the face? Method: add same-person full-frame blends as negatives (ladder same-person morphs R3, mirror self-morphs R3m, and mirror self-morphs of every AF0 training person). Status: registration drafted and in pre-run review; images, manifests and overlay built; smoke queued on WCSS; no fit and no score yet.

## 2. Timeline

- 08:28 Read OWNER_BRIEF, NOTEBOOK (12–13 Nov) and the PN1 / FS1 / C2P / FINAL documents.
- 08:30 Counted what Sb already uses as negatives (`/mnt/t7/smad_next/PN1/manifests2/manifests2_summary.json`, `train_Sb.csv`). It includes S3 and S0 but no same-person full blend.
- 08:32 Read FS1 development flags for A, B and Sb per rung from the 15 FS1 tars (prereg section 1 table; disclosed). Every arm flags 83–100% of same-person morphs.
- 08:35 `src/SE1/build_selfm.py --check`: AR1 R3m rebuilt pixel for pixel on 8 hosts (`/mnt/t7/smad_next/SE1/check_r3m.json`). 8-image test, then the full build: 644 self-morphs (518 train, 126 dev) in 60 s (`selfm_build.csv/json`).
- 08:39 `src/SE1/mk_se.py`: train_SE.csv (`c4e5aa47…`), se_eval.csv (`6dcef964…`), overlay `se1_overlay.tar` (`de26d6ce…`, 972,605,440 bytes, 2,738 files).
- 08:42 Overlay, run.sh and sbatch files uploaded to WCSS `packs/SE1/` and verified there (sha256 OK). The FS1 pack is on WCSS at `packs/BB2/pn1_pack_fs.tar` (96c31ae2…).
- 08:4x Smoke command placed in the dispatcher queue (`/mnt/t7/smad_next/dispatch/submit_queue/wcss_se1_smoke.cmd`); the WCSS Slurm controller was not answering.
- 09:xx Lead input: reframe as "identity against same-person blend" (strategist §0 and item #5; the numbers were checked on the FS1 tars and hold), SE is an ablation row, five seeds, share AB1's platform. Seeds changed 501–505 → 408–412 (AB1's seeds). run.sh then re-pinned for the Athena container option (final pin b2a975f1…, prereg section 13).
- 09:xx prereg.md drafted; experiment-reviewer (opus): GO WITH FIXES (`experiments/reviews/PRERUN_SE1_20261113.md`); all six majors and the minor points fixed (prereg section 14); reader rewritten (seed-mean guards, stored R3 target, attribution, platform check); Athena twin and rented fallback scripts written; the FS1 pack and the overlay uploaded to Athena `packs/SE1/` and verified.

## 3. Data

- New images: `/mnt/t7/smad_next/SE1/img/selfm/<AF0 id>_selfm.png` (644). Mirrors and their .tem files: `/mnt/t7/smad_next/SE1/mirror/`. Per-image sha256 in `selfm_build.csv`.
- Manifests: `/mnt/t7/smad_next/SE1/manifests/{train_SE.csv, se_eval.csv, se1_summary.json}`.
- Overlay: `/mnt/t7/smad_next/SE1/se1_overlay.tar` (+ .sha256). WCSS copy: `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/SE1/`.
- Existing images used: AR1 ladder R3/R3m OpenCV (`/mnt/t7/smad_next/AR1/img/frgcferet/opencv/`), AR1 FaceMorpher splices (development hosts), the MS1 FFHQ hold-out (`/mnt/t7/smad_next/MS1/pack_tree/pn1/data/eval/ms1/`).

## 4. Code

- `src/SE1/build_selfm.py`: mirror self-morphs (lossless flip, mirrored .tem, unchanged `78_tool_morph.py` b8a389f1…). `--check` reproduces AR1 R3m.
- `src/SE1/mk_se.py`: manifests and overlay.
- `src/SE1/run.sh`: task script (copy of the BB2 run.sh; CLIP ViT-B/16 FS1 recipe; arms A|Sb|SE; seeds 408–412).
- `src/SE1/wcss/se1_smoke.sbatch`, `se1_fit.sbatch`: WCSS jobs (`--extra=FORCE_RM_TMPDIR`, all IO in $TMPDIR).
- `src/SE1/se1_read.py`: the registered reader (mock-tested: `/mnt/t7/smad_next/SE1/se1_read_mock.json`).
- `src/SE1/baseline27_se1.py`: the 27-statistic baseline (to run after the registration commit).
- DGX Python: `/home/narolski/mambamorph-code/.venv-spark/bin/python`. WCSS: `~/dmenv` (torch 2.11, cu128).

## 5. Results

None yet.

## 6. Checks

- AR1 R3m reproduced pixel for pixel by the SE1 build path (8 hosts).
- The overlay never replaces an FS1 file (asserted in mk_se.py; run.sh uses `--skip-old-files` and re-checks FS1's SHA256SUMS).
- The WCSS copies of the overlay and run.sh verified by sha256.
- Not verified yet: run.sh end to end (the WCSS smoke does this).

## 7. Dead ends and failures

- The first seed choice (501–505) was replaced by 408–412 before any job ran, so the same-seed fits can be compared with AB1's.

## 8. Observations and ideas

- Every FS1 arm flags 83–100% of development same-person full morphs (R3, R3m); the whole detector family reads "blend", not "two identities".

## 9. Open items

- Pre-run review; registration commit; baseline computation; smoke result; fit submission.

## 10. Handover state

- WCSS smoke: job 6310083 (submitted by the dispatcher 09:02, lem-gpu-short; expected end about 09:40; owner checks the log logs/se1-smoke-6310083.out). Athena smoke not submitted (dispatcher: WCSS took it; Athena A100 reserved to about 22 Dec), so the platform is WCSS H100. Fits (wcss_se1_fits.cmd, array of 15) are submitted by the dispatcher once the smoke log shows PN1_TASK_DONE and SE1_SMOKE_RC 0.
- Compute spent: 0 GPU-hours.

## 11. Reproduce

See prereg.md section 12.
