# Short pre-run check: PN1 fresh seeds FS1 (development-only) and amendment 14 as a development read

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

**Verdict: GO WITH FIXES.** The data isolation holds; I checked it myself. Three things must be fixed before any lease starts: the drivers have changed since they were pinned, two driver paths can release or idle a lease wrongly, and the FS1 reader is not committed. All checks were read-only. I opened no score file, no valx/FST/A12SP and no npz contents.

## Enforcement (item 2): verified, clean

- **FS1 pack** `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar`
  - Pack sha256 matches `96c31ae2…`.
  - The `pn1_eval.csv` extracted from the tar matches `f0f29f22…`. It has 19,797 rows, with unique ids and paths.
  - af0 1,339 (genuine 1,159, morph 180), all from FRGC/FERET hosts.
  - ladder 6,093 (opencv 3,383, facemorpher 1,837, none 873), FRGC/FERET.
  - splice 4,365 (genuine 2,910, morph 1,455), FRGC/FERET.
  - ffhq 5,000 (ffhq_bona 2,000, landmark_complete genuine 2,000 and morph 1,000).
  - ffhq_lcomb 3,000 (genuine 2,000, morph 1,000).
- **Symlink sources** (`fs_tree`)
  - eval/pn1 images come only from `/mnt/t7/smad_next/{AF0,AR1}`.
  - eval/hn2 and eval/a14 images come only from `/mnt/t7/smad_heldout/ffhq_morphs/eval/ffhqm/{ffhq_bona,landmark_complete,landmark_combined}`.
  - train images come only from `smad_next/{AF0,AR1,SM1}`.
- **Token scan of the tar paths:** the only matches are code files (`frll_dmad.py`, `prep_gtest.py`). The single manifest match, `..._amsl112`, is an FRGC photo with a size label, not AMSL data.
- **Training manifests:** train_A has 1,992 rows (`af070a60…`), train_B 7,762 (`bd53dc32…`), train_Sb 8,386 (`2cf3fda3…`). Every row's db is frgc or feret, with 0 FFHQ or benchmark rows.
- **Amendment-14 pack** `pn1_a14.tar` (`bda5fd3d…`): its list (`9f199c3a…`) has 12,365 rows: splice 4,365 (FRGC 3,525, FERET 840), ffhq 5,000 and ffhq_lcomb 3,000. There are no benchmark paths.
- **Scorers:** `pn1_score.py` and `rescore.py` read only the manifest they are given. No code path can score a benchmark row.

## Registered texts (item 1)

- The frozen v4 contrasts use development data only.
- My earlier fixes are all in:
  - F1: genuine pool is the HN2 persons, re-shrunk.
  - F2: ceiling clause and the paired complete-minus-combined read.
  - F3: mandatory floor with sha check (`a14_read.py:198-199`), lower-bound rule and the aligned==1 subset.
  - F4: continue on error, always tar, guard values.
  - F5: "associational" label, arm-level ρ and ρ without Sb.
  - F6: gate binds only the cross-platform reads, and a failed gate is not re-run.
  - B2-F1 to B2-F5: disclosures, seed table, ties, deadline, outcome table, "platform plus nondeterminism", per-machine print.
- `BENCHMARK_EXPOSURE.md` is honest about H1, MAD22 and FRLL.

## Blockers and majors

1. **Blocker: the drivers no longer match their registered pins.** The working tree has uncommitted edits adding a one-host layout. As of 08:19:
   - `run.sh`: working tree `04998a7c…`, registered `74a49b0b…`.
   - `drive_fs.sh`: `29ce8a41…` vs `504476a8…`.
   - `remote_fs.sh`: `010f1f62…` vs `755261f0…`.
   - `drive14.sh`: `f0c99f17…`, registered as "unchanged `e079e4b5…`".
   - `remote_a14.sh`: `fadc2c79…`, registered as "unchanged `adc0b84d…`".
   - `drive_fs.sh:20` still pins `RUNSH=74a49b0b…`, so setup will abort.
   - One 2-GPU host also contradicts the registered "two leases, A100-SXM4 40 GB" and "results printed per machine".
   - **Fix:** finish the edits, then commit an FS1 and amendment-14 amendment with the new sha256s. Disclose the one-host layout (both queues share the host's CPU, disk and GPU type) and redefine "machine" as "GPU/queue" for the per-machine print. Do this before setup.

2. **Major: the release logic can release a lease with results still on it.**
   - In `drive_fs.sh` pull, when the remote reports `ENDED` but the rsync failed (the `|| true` at lines 60 and 74), DONE and then RELEASE are written with tars still on the remote. The lead then destroys the machine and the results are lost.
   - `$bad` is also not recomputed after the line-74 re-pull.
   - **Fix:** after the re-pull, re-verify every task. Count a task as failed only if the remote confirms it: `R "[ ! -f $B/root/results/PN1/$t.tar ] && cat $B/rc/$t"` must succeed and give a non-zero rc. Otherwise exit without DONE, so the next loop retries.

3. **Major: the lease can sit idle until the cap.**
   - `remote_fs.sh:29` waits for `A14_DONE` forever. That file is written only by the EXIT trap in `remote_a14.sh`.
   - If remote_a14 is hard-killed, or `drive14.sh start` fails after the queue started, the m2 queue never runs.
   - In the one-host layout this also blocks RELEASE for the whole host after m1 finishes.
   - **Fix:** wait at most 2.5 h, which is the registered amendment-14 guard. Then log "A14 timeout" and proceed. Or have `drive14.sh loop` touch `A14_DONE` remotely when it gives up.

4. **Major: the remote disk floor does not cover the one-host layout.**
   - Peak use is about 35 GB: fs pack 8.75 GB, a14 pack 4.4 GB, a14 extract about 4.4 GB, and two concurrent task extracts of about 8.6 GB each.
   - The only check is `remote_a14.sh:31` (15 GB, once), and the queue runs no check at all.
   - **Fix:** in `remote_fs.sh setup`, require at least 45 GB free (one-host) or at least 30 GB (two leases).

5. **Major (item 4, order of commits): the FS1 reader is not committed.**
   - `src/PN1/fs_read.py` is untracked (mtime 08:17:45). FS1 only requires it "before the first fresh-seed tar".
   - Amendment 14 runs first and produces landmark_combined scores on seeds 401/402. So the reader could be written after those numbers are seen.
   - Otherwise the order is clean: FS1 freeze at 08:15:37, amendment 14 at 08:16:09, floor npz written at 08:17:00, its sha committed at 08:17:07.
   - **Fix:** commit `fs_read.py` and pin its sha256 in the amendment from finding 1, before `PN1_A14.tar` is pulled.

6. **Major (wording): FFHQ is called unseen, but it has been read.**
   - Contrast 2's threshold of 0.65 and A's positive control were set knowing the 401/402 paired shares on these same images (A 0.72/0.78, others 0.30-0.44).
   - Neither v4's disclosures nor the choices list in `BENCHMARK_EXPOSURE.md` says so.
   - **Fix:** add this as choice 10 and to the v4 disclosures. In the contrast-2 claim, replace "an unseen development source" with "a development source not used in training (already read on seeds 401/402)".
   - This is a disclosure, not a change to the contrasts, so it does not break "nothing in this file changes".

**Minor:**
- T7 has 28 GB free against a 20 GB pull floor. Keep other jobs (AG1) from filling it, or pulls stop.
- `a14_read.py` `pools()` still loads the pack-2 manifest's FRLL rows into memory. It reports nothing from them, but it would be cleaner to filter them out.

## Questions for the authors

- Does the lead accept one 2-GPU host instead of the two registered leases? This is a platform change after the freeze and needs to be disclosed.
