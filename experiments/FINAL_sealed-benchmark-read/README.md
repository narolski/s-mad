# The sealed MAD22 read of the frozen candidate (FINAL): record

Owner: FINAL owner (agent), for the lead. Registration: `prereg.md` (v3). Code: `src/FINAL/`. Large files:
`/mnt/t7/smad_next/FINAL/`. Times are by the machine clock (`date`).

## State

- **13 Nov, 18:30-20:05.** The package was built, mock-tested and pre-run checked (GO after fixes); the registration
  was committed (see git log). No benchmark score of any frozen network exists.
  - The pre-run check (experiment-reviewer) and the registration commit follow.
  - Then the SelfMAD and reference-statistic runs (sealed), the pin commit, and the lead's start word.
- **Nothing was rented. Nothing was started on a rented machine.**

## What was done (exact commands; DGX, `P=/home/narolski/mambamorph-code/.venv-spark/bin/python`, nice 10, 2 threads)

1. **Development source extracted from the fresh-seed pack** (sha256 96c31ae2…, checked):
   `tar -xf /mnt/t7/smad_next/PN1/pn1_pack_fs.tar pn1/data/eval pn1/data/manifests pn1/code pn1/hf pn1/SHA256SUMS pn1/src`
   into `/mnt/t7/smad_next/FINAL/src_fs/`. It holds development rows only (that pack asserts no benchmark row).
2. **The five Sb tars checked** against the C2P pins (`src/PR1/nets_pins.txt`): 5 of 5 equal.
3. **The existing release rows copied:** `$P -I src/FINAL/extract_release_scores.py`, giving
   `/mnt/t7/smad_next/FINAL/release_scores_existing.npz` (dba3acda…; counts in the `.json` beside it). The values were
   not printed.
4. **Development thresholds:** `$P -I src/FINAL/thresholds.py`, giving `final_thresholds.json` (FFHQ genuine
   development rows only).
5. **The border mask explored on pixels only** (scratch script `mask_explore.py`; the same definition is in
   `build_pack.py`). OpenCV and Webmorph frames carry no edge-black region. FaceMorpher and MIPGAN morphs do. The
   genuine frames do not.
6. **Pack:** `$P -I src/FINAL/build_pack.py` built `/mnt/t7/smad_next/FINAL/FINAL_mad22_pack.tar`: 5,756,416,000
   bytes, sha256 5ec63472d9c489aea93bfdcdd0929b4651ef9c5a27e9c90801d7c54c3eee43c1.
   - Gate rows: 6,613. Benchmark rows: 9,930.
   - Border-equalised copies: FaceMorpher 1,408, MIPGAN-I 1,408, MIPGAN-II 1,407.
   - The tree it was built from is `tree_FINAL_mad22/` (symlinks plus the blanked PNGs).
   - Test pack: `--limit-bench 8` gave `FINAL_mad22_test8_pack.tar`, used for reader tests only and never uploaded.
7. **Batch-subset check (GB10, development rows only)**, in `/mnt/t7/smad_next/FINAL/test_subset/`: Sb s403 scored a
   30-batch FFHQ stretch and every 3rd batch of it. The 640 rows were byte-identical.
8. **Metrics self-test:** `$P -I src/FINAL/final_metrics.py` passed. It checks known EER, AUC and BPCER@APCER values,
   weights against duplication, and rates.
9. **Reader mock tests on synthetic scores and a synthetic release file:**
   `$P -I src/FINAL/mock_test.py --pack <pack> --work <dir> --thresholds <thresholds>`.
   - Full pack, in `mock_full/` and `mock_full_c/`. Every branch gave its registered outcome:
     - exceeded;
     - matched;
     - lost;
     - comparable (after the mock was retuned: the first comparable mock really was "lost");
     - gate failed ("no read");
     - the border caveat (3 families flagged).
   - A second reader run was refused in every branch.
   - The test pack gives wide intervals: its "lost" branch read "comparable", as it should with 8 rows.
   - Fixed after the mocks: the sign of the interval in the "exceeded" sentence.
10. **End-to-end test on the DGX with stand-in data** (`src/FINAL/make_standin.py`). A stand-in "MAD22" folder made
    of FFHQ development frames was used, so no benchmark image was involved.
    - **Config A** (the real networks): the driver staged, started and pulled. The remote job asserted pins, extracted
      and scored the gate. The gate FAILED on the GB10 (0 of 5; max |Δ| 0.114, as TT1 predicts for GB10). No row
      after the gate was scored. rc "FATAL GATE FAILED", two copies, FINAL_DONE + FAILED.
    - Second-start refusals tested:
      - the host `STARTED` refused the driver;
      - the local lock refused the driver;
      - the remote script started by hand with `STARTED` present exited 9;
      - `stage` after the lock refused (after a fix: the lock is a directory).
     - **Config B** (stand-in network tars whose stored gate rows carry GB10 scores from config A's run, so the gate
      must pass): gate 5 of 5 byte-identical (max |Δ| 0). This also shows run-to-run determinism of the subset gate
      on one stack. The 940 stand-in benchmark rows were scored for all five. rc 0, two copies verified, FINAL_DONE.
      - `src/FINAL/e2e_read_standin.py` then ran `final_read.py` on that real-format result tar, with a synthetic
        release file. It read all 4 forms × 7 cells. The outcome is meaningless (stand-in data) and only checks the
        format.
    - Run times on the shared GB10: about 70 s per network for 6,613 gate rows, and about 20 s per network for 940
      rows. An A100 PCIe was about 30 s per network for 19,797 rows (TT1-FS).
11. **SelfMAD:** `$P -I src/FINAL/selfmad_mad22.py list` wrote the 5,911-row list (5fdc9921…).
    - A smoke run of RS1 `score.py --mode own` on 8 FRLL photos (rows RS1 already scored) went to
      `/mnt/t7/smad_next/FINAL/selfmad/smoke/`.
    - No MAD22 row has been scored by SelfMAD.

12. **Pre-run check** (experiment-reviewer, opus, 13 Nov about 19:10-19:20): GO WITH FIXES. The record is
    `experiments/reviews/PRERUN_FINAL_MAD22_20261113.md`. Applied:
    - B1: each release also enters the comparison with raw genuine photos; the lower EER is taken (conservative).
      Aligned-native rows are printed; disclosure added.
    - M1: the reader verifies and parses every input before taking its one-read marker.
    - M2: the host marker is created only after every non-scoring check; the GPU must be A100-PCIE-40GB; a gate dry
      run on the lease (development rows only, once) must pass before the read can start.
    - M3: the code and text now agree (aligned-native rows printed, AD4 morph-free values printed, F3 verdict,
      saturation label).
    - M4: a landmark-only mean (OpenCV + Webmorph) with its own verdict and a sentence rule.
    - m2 absolute intervals; m3 non-finite scores mean "no read"; m4 the gate checks the stored manifest sha256;
      m5 the expected precision is stated; m6 the border wording; m7 later pins are a dated addendum; m9 the crop
      failures are disclosed.
    - Also added: a host run lock (flock) and a per-lease dry-run lock against concurrent starts.
    - Re-tests after the fixes:
      - Mocks on the full pack, `/mnt/t7/smad_next/FINAL/mock_full4/mock_results.json`: 7 of 7 branches give their
        registered outcome. The branches are exceeded (with SelfMAD and reference-statistic inputs), matched, lost,
        comparable, gate failed, border caveat with F3 falsified, and non-finite scores giving "no read".
      - A second reader run is refused in every branch.
      - The mock latents were changed so that a genuine photo has one latent across pools. The "matched" mock had
        become "comparable" once the raw-genuine comparator was added; this was the mock's design, not the reader.
      - End-to-end stand-in C (`e2e/leaseC`):
        - `start` before the dry run was refused;
        - the dry run passed 5 of 5, byte-identical;
        - a second `dryrun` was refused by the per-lease lock;
        - `start` ran the read, and a second `start` was refused by the start lock;
        - rc 0, two copies verified;
        - `e2e_read_standin.py --tag C` read all 4 forms × 8 cells.
    - m8, correction of the reviewer's reading: `/mnt/t7/smad_next/FINAL/beststat/beststat_limit8.npz` was computed
      on the STAND-IN tree (`e2e/tree_FINAL_standinB`, FFHQ development frames under MAD22-like names), not on MAD22.
      No MAD22 image has a statistic value yet.
    - m4, checked by the reviewer offline: all five stored `scores_eval.npz` are in pn1_eval order (19,797 unique
      rows), manifest sha f0f29f22…, A100-PCIE-40GB, host e8bf0b3abe77.
    - Not adopted (author decision): a tolerance fallback for the gate.

13. **Re-check by the same reviewer** (about 19:55): **GO for the registration commit.** No blocker or major remains.
    Its three text points were applied:
    - the winner's-curse clause in §4;
    - `mean2` added to §3.1;
    - the release-path sentence added to the always-attached labels, in the text and in the reader.
    Mocks re-run after this last reader change: `mock_full5`, 7 of 7 branches pass.
14. **Platform note** (lead, received about 20:02). Athena's A100-SXM4 reproduced the five networks' TT1-FS gate byte
    for byte. This read keeps the built and tested rented A100-PCIE-40GB path. Athena is possible only by a dated
    amendment with its own runner and test (prereg §9).

15. **Sealed runs after the registration commit** (DGX, 20:03-20:24). Neither output was opened.
    - SelfMAD's MAD22 rows: RS1 score.py --mode own, 5,911 images, 1,232 s, beside IDistill (6 GB). The output is
      `/mnt/t7/smad_next/FINAL/selfmad/selfmad_mad22_scores.npz`, ec5e7609….
      - score.py writes a per-row `cropped` flag. The reader uses every row, as the other releases' rows are used.
    - The reference statistic on the 9,930 frames: `/mnt/t7/smad_next/FINAL/beststat/beststat_mad22.npz`,
      9c34cccf….
16. **Lead's pre-run check of a7d7454** (`experiments/reviews/PRERUN_FINAL_MAD22_LEAD_20261113.md`, c7b2daa): GO WITH
    FIXES. Applied as amendment G1, guards only, signed by the lead (prereg §12): F1-F7.
    - Refusal tests, each refused before any action:
      - F1, the real driver: a FINAL_CONFIG override is refused ("override refused outside test mode"); an edited
        remote_final.sh in a copy is refused ("not at its registered pin"); a config with 3 networks in a copy is
        refused ("config not at its registered pin"). The unmodified driver passes the pins and stops at the
        missing lease.json, with no ssh.
      - F2: the reader without --selfmad is refused when it is pinned.
      - F3: a result path under /mnt/t7/smad_next/vast/ with a non-default marker is refused; so are non-default
        pins, and an existing tables file. No marker was created by any refusal.
    - `mock_full6`: 7 of 7 branches pass.
    - End-to-end stand-in D: `start` without a dry run refused; dry run 5 of 5 byte-identical; read rc 0; second
      start refused; reader read 4 forms × 8 cells.
    - Pin addendum, prereg §13: the sealed outputs and the changed pinned files (drive_final.sh, final_read.py,
      make_pins.py). final_pins.json was regenerated.

## Ready: what the lead does (F4) and the commands

- **Offer filters:** 1 × A100 PCIe 40 GB. The GPU name must be exactly "NVIDIA A100-PCIE-40GB" (the job aborts on
  anything else, before any score).
  - Image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`; disk ≥ 40 GB; internet up and down ≥ 100 Mbps (pip, and
    a 5.76 GB upload); reliability ≥ 0.98; CUDA driver ≥ 12.1.
  - Write `/mnt/t7/smad_next/vast/<LEASE>/lease.json` with `ssh_host`, `ssh_port` (and the usual lease fields).
- **Commands (owner):**
  - `cd /home/narolski/smad-next`
  - `bash src/FINAL/drive_final.sh stage <LEASE>`
  - `bash src/FINAL/drive_final.sh dryrun <LEASE>`
  - `bash src/FINAL/drive_final.sh loopdry <LEASE>`
  - Then report DRYRUN_PASSED to the lead. Only on the lead's explicit word:
    `bash src/FINAL/drive_final.sh start <LEASE>` and `bash src/FINAL/drive_final.sh loop <LEASE>`.
- **After FINAL_DONE (F4):** the lead destroys (not stops) the instance. The lease ID and time go in the README and
  NOTEBOOK.
- **On FINAL_FAILED (F5):** the two result tars are renamed `*.QUARANTINE-<lease>` and never extracted.
- **Then:** the reader once (command above, default pins and marker), the results-reviewer, then the report to the
  lead (F6).

## Dead ends and fixes

- Driver start: `cd $B && nohup … &` sent the whole list to the background and held the ssh/command pipe until the
  job ended. Changed to `cd $B || exit 1; nohup … &`.
- The stand-in morph names repeated. Fixed.
- `stage` tested the lock with `-f` on a directory. Changed to `-e`.

## Planned commands after the registration commit (in order)

1. SelfMAD MAD22 rows on the DGX (check `nvidia-smi` first; the IDistill job keeps the GPU):
   `cd /tmp && OMP_NUM_THREADS=2 nice -n 10 $P -I /home/narolski/smad-next/src/RS1/score.py --det selfmad_hrnet_w18 --mode own --manifest /mnt/t7/smad_next/FINAL/selfmad/selfmad_mad22_list.csv --out-dir /mnt/t7/smad_next/FINAL/selfmad/scores --tag own_selfmad_mad22__dgx --workers 2`
   then `$P -I src/FINAL/selfmad_mad22.py pack`. The output is sealed: nothing is printed but counts and the sha256.
2. Reference statistic:
   `$P -I src/FINAL/beststat_mad22.py --tree /mnt/t7/smad_next/FINAL/tree_FINAL_mad22/final`. Sealed.
3. Pins: `python3 -I src/FINAL/make_pins.py --selfmad <npz> --beststat <npz>`, then the pin commit.
4. The lead rents one A100-PCIE-40GB and writes `/mnt/t7/smad_next/vast/<LEASE>/lease.json`. Then:
   `bash src/FINAL/drive_final.sh stage <LEASE>`, `bash src/FINAL/drive_final.sh dryrun <LEASE>`,
   `bash src/FINAL/drive_final.sh loopdry <LEASE>` (needs DRYRUN_PASSED). Then, on the lead's word,
   `bash src/FINAL/drive_final.sh start <LEASE>` and `bash src/FINAL/drive_final.sh loop <LEASE>`.
5. Reader, once:
   `$P -I src/FINAL/final_read.py --result /mnt/t7/smad_next/FINAL/results/FINAL_mad22_<LEASE>.tar --pack /mnt/t7/smad_next/FINAL/FINAL_mad22_pack.tar --release-existing /mnt/t7/smad_next/FINAL/release_scores_existing.npz --selfmad /mnt/t7/smad_next/FINAL/selfmad/selfmad_mad22_scores.npz --beststat /mnt/t7/smad_next/FINAL/beststat/beststat_mad22.npz --thresholds experiments/FINAL_sealed-benchmark-read/final_thresholds.json --out experiments/FINAL_sealed-benchmark-read/final_read.json --tables experiments/FINAL_sealed-benchmark-read/final_tables.md`

## Kept, and where

- The pack and its tree: `/mnt/t7/smad_next/FINAL/`.
- The stand-in tests: `/mnt/t7/smad_next/FINAL/e2e/` (FFHQ development frames only).
- Mocks: `mock_*`.
- Development extraction: `src_fs/` (6.5 GB, a copy of a pack that exists). It can be removed after the read; I will
  list it to the lead.
