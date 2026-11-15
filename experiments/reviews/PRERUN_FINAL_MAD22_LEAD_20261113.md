<!-- Final, lead-ordered pre-run check of the sealed MAD22 read (registration a7d7454) by the experiment-reviewer (Opus); hand-back saved verbatim by the lead, 13 Nov 2026. Lead's answers: (1) the lead destroys the instance and records the lease ID and time in the README and NOTEBOOK; (2) the reader prints n per cell and the table states where a release cell's n differs. The guard fixes F1-F3 are signed by the lead as a guards-only amendment; no measure, cell, threshold, label or test changes. -->

**Verdict: GO WITH FIXES.** Everything the first review asked for is in the committed code and text. The pins match. The pack's scope is exactly what was registered. But three one-shot guards can be bypassed by an argument or an environment variable. Fix them before the start. All three are guard-only edits: no GPU, and no change to any measure, cell, threshold, label or test. Because they touch pinned files, they need a short dated amendment, a re-pin and a mock re-run. Fold that into the pin commit that is already planned for the SelfMAD and reference-statistic outputs.

What I checked, without opening anything I was not allowed to:
- All 30 pins are equal to the files now. Every `src/FINAL` file, the thresholds and the release npz match `final_pins.json`.
- The five network tars equal `src/PR1/nets_pins.txt` lines 3-15.
- Inside the pack, `final_bench.csv` is 48335f86, `final_gate.csv` is 2799d2f9, SHA256SUMS is bf48c489 and `common.py` is b5d42a99 (platform pin 12).
- I was refused access to `release_scores_existing.json`, so I did not see the per-pool release counts (see question 2).

## 1. Status of every finding in the first review (PRERUN_FINAL_MAD22_20261113.md)
All are present.
- **B1:** the raw-genuine candidates are in `final_read.py:302-303,311-312,355`, the aligned-native rows printed at 304-305, the disclosure in prereg §3.2:75-85 and in the reader at 449.
- **M1:** load and validate run before `marker.mkdir()` (505-510).
- **M2:** `STARTED` is created only after every non-scoring check (`remote_final.sh:77-81`). The GPU check is the exact string `A100-PCIE-40GB` (:49). The dry run with `DRYRUN_PASSED` is required before a start (`drive_final.sh:94`).
- **M3:** aligned-native rows, the AD4 morph-free values (:45-48), the F3 verdict (:409-411) and `LAB_SAT` (:40) are all in.
- **M4:** `mean2` has its own verdict and the sentence rule (:42, 450-455).
- **m1** is disclosed (§4:143-146). **m2** (:264, 335-338), **m3** (:140, 154, 159, 163, 274) and **m4** (`gate_check_final.py:34-36`) are in. That check only runs if the stored file has the `manifest_sha256` key; the earlier review confirmed offline that it does.
- **m5** (§4:159-162), **m6** (§3.2:73), **m7** (`make_pins.py:70-79`), **m8** (README:101-103) and **m9** (§3.4:117) are in.

## 2. Findings, most severe first

**F1 (major): the driver never checks against the registered pins, so a partial read is possible.**
- **Evidence:**
  - `drive_final.sh:17` takes `CFG=${FINAL_CONFIG:-...}`, and `:23-24` take PSHA and CSHA from local files.
  - The remote only checks itself against those same values (`remote_final.sh:43-46`). `bin/SHA256SUMS` is rebuilt from whatever files are present (`:68`).
- **Effect:** a config that keeps `read_id` FINAL_mad22 but lists only 3 of the 5 networks, or an edited `remote_final.sh`, would pass the checks, score MAD22 and use up the lock.
  - The reader would then refuse it (`:132`), but scores of the frozen networks would already exist.
  - The stand-in tests already used this override (`e2e/standin_config_*.json`).
- **Fix:** insert after `drive_final.sh:24`:
```bash
if [ "${FINAL_TEST:-0}" != 1 ]; then
  PINS=$SRC/final_pins.json
  pin() { python3 -c "import json,sys; print(json.load(open('$PINS'))['files'][sys.argv[1]])" "$1"; }
  [ "$CSHA" = "$(pin src/FINAL/final_config.json)" ] || { echo "config not at its registered pin"; exit 1; }
  [ "$PSHA" = "$(python3 -c "import json; print(json.load(open('$PINS'))['pack'])")" ] || { echo "pack not at its registered pin"; exit 1; }
  for f in remote_final.sh gate_check_final.py drive_final.sh; do
    [ "$(sha256sum < "$SRC/$f" | cut -c1-64)" = "$(pin src/FINAL/$f)" ] || { echo "$f not at its registered pin"; exit 1; }
  done
fi
```

**F2 (major): the comparison set can still be chosen at read time.**
- **Evidence:** `final_read.py:105-111` and `:315-317` treat SelfMAD and the reference statistic as "pending" whenever `--selfmad` or `--beststat` is left out, even if they are pinned. The SelfMAD and statistic runs started at 20:03 (`selfmad/scores/`, `beststat/run.log`).
- **Fix:** at the top of `load()`:
```python
for k in ("selfmad", "beststat"):
    if k in P and not getattr(a, k):
        sys.exit(f"{k} is pinned in final_pins.json: pass --{k}; it cannot be dropped at read time")
```

**F3 (major): the reader can read the real result twice.**
- **Evidence:** `--marker` and `--pins` (`:494-499`) let a second run use a fresh marker and a different output file.
- **Fix:** in `main()`, before `Read(a)`:
```python
real = str(pathlib.Path(a.result).resolve())
if real.startswith(("/mnt/t7/smad_next/FINAL/results/", "/mnt/t7/smad_next/vast/")) and \
   (a.marker is not None or pathlib.Path(a.pins).resolve() != (HERE / "final_pins.json").resolve()):
    sys.exit("the real result is read only with the default pins and marker")
```
  Also refuse when `--tables` already exists.

**F4 (minor): cleaning up the rented machine is not written down.**
- **Evidence:** the driver "never releases" (`drive_final.sh:3-4`). The pack, with 204 FRLL photos and the MAD22 frames, and the scores stay on the host. Platform pin 14 requires verified copies before release.
- **Add to prereg §9 after "After the job":** "The lead destroys (not stops) the instance only after `pull` has logged FINAL_DONE with both copies verified (or FINAL_FAILED, verified). The lease ID and the time it was destroyed are recorded in the README. No key or token other than the lease SSH key is on the host (HF_HUB_OFFLINE=1, base weights in the pack)."

**F5 (minor): partial scores after a crash are quarantined only by rule.**
- **Evidence:** `abort` after the gate tars whatever bench npz files exist (`remote_final.sh:37,99`), and the driver copies them twice. The reader does not open them when rc≠0 (`:134`).
- **Add:** "On FINAL_FAILED the result tar and its copy are renamed `*.QUARANTINE-<lease>` and never extracted."

**F6 (minor): the order "independent results review before interpretation" is implicit.**
- **Evidence:** §9:319 says only that the review "follows".
- **Replace with:** "`final_read.json` and the tables go to the results-reviewer before any sentence reaches the paper, NOTEBOOK or the author. The labels 'seen during development' and 'shortcut-saturated' (FaceMorpher, mean5) are attached by the reader (:345, 446-449) and may not be dropped."

**F7 (minor): the per-cell sizes of the release rows are not disclosed.**
- **Evidence:** variant-1 crop failures dropped 66 FFHQ photos. The same could have happened on MAD22 cells; I could not check this.
- **Fix:** the reader already prints `n_morph` and `n_genuine` per cell. Add a rule: "Where a release cell's n differs from ours, the table says so."

## 3. Your eight points
- **One-shot safety:** sound apart from F1-F3. A second start is refused by the host `STARTED` file, the local lock and the flock. A crash before the marker uses up nothing. A crash after the gate leaves an rc that only the lead acts on.
- **No number before the gate:** there is no such path. `rescore.py:43` prints counts only, the gate prints development maxima only, and the dry run never reads `final_bench.csv`.
- **Platform gate:** the GPU must be exactly A100-PCIE-40GB, with one idle card. torch 2.2.1, CUDA 12.1, cuDNN 8902 and the package pins are asserted. TF32 is on through the pinned `rescore_tf32.py`. Batch 64, unshuffled, manifest order.
  - The gate is 6,613 rows (104 whole batches, every third), compared byte for byte with each network's stored `scores_eval.npz`.
  - Any failure aborts before the first benchmark row (`:94`).
  - The cuDNN benchmark and deterministic flags and the attention backend are recorded, not asserted. The byte gate covers this; acceptable.
- **Scope:** exactly as registered.
  - Morphs: FaceMorpher 1,000, MIPGAN-I 1,000, MIPGAN-II 999, OpenCV 984, Webmorph 500. Native genuine 204 (102 neutral and 102 smiling), E7 5×204, border-equalised copies 1,408/1,408/1,407. 9,930 unique rows, 102 persons.
  - Every bench path is under `eval/mad22c` or `eval/be`, and `build_pack.py:42,218` blocks forbidden names.
  - The gate rows are development only (pn1, hn2, a14).
- **Measures:** fixed in code as registered: EER per history-matched cell with AUC, the own rule, the FFHQ development threshold already in the committed `final_thresholds.json`, the border-equalised forms, the reference statistic and forecasts F1-F3. The rows for released detectors are pinned (dba3acda).
- **Networks:** pinned, the last checkpoint only (`remote_final.sh:74`). The networks cannot be swapped once F1 is fixed.
- **Hygiene:** results are fetched, the sha256 is verified and a second copy is made (`drive_final.sh:50-61`). Only F4 is missing.
- **Reporting:** the labels are in the reader; F6 makes the review order explicit.

## 4. Improvements
1. F1-F3: about 30 minutes, 0 GPU. Then re-pin, re-run `mock_full`, the stand-in end-to-end test (`e2e`) and a refusal test for each new guard. Needs a dated amendment, which the lead can sign because it is guards only.
2. F4-F7: text only, in the same pin commit.

## 5. Questions for the authors
1. Who on the team records the instance destruction, and when?
2. Do the release rows of the MAD22 cells have the full n (crop failures)? I was denied access to `release_scores_existing.json`.

Key files:
- /home/narolski/smad-next/src/FINAL/drive_final.sh
- /home/narolski/smad-next/src/FINAL/final_read.py
- /home/narolski/smad-next/src/FINAL/remote_final.sh
- /home/narolski/smad-next/experiments/FINAL_sealed-benchmark-read/prereg.md
