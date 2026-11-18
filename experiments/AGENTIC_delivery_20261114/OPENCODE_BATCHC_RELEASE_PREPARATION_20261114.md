# Count-balanced ablation (Batch C): metadata release preparation

14 November 2026. **Preparation only; no final admission GO and no production authorization.** B1/B2 are accepted by MAIN and reused without rerunning tests or reference calculations. This reviewer performed read-only git inspection, metadata/receipt reconciliation, sidecar checks and filesystem checks. No candidate archive bytes or contents, numerical candidate scores, cluster connection, git mutation or once claim was used.

Machine-readable proposed manifest: `OPENCODE_BATCHC_RELEASE_PREPARATION_20261114.json`, SHA256 **`7c473741d5abf3cbd9bb800f5f588a2f9fb27bd7fdfd4365235799c609585b06`**. It contains all 30 exact archive paths, byte sizes, opaque hashes, sidecar hashes, expected job mappings, evidence paths/hashes, 49 source/transitive-input entries, execution arguments and remaining blockers.

## Source binding now established

During preparation MAIN committed the reviewed implementation as `7d5e06b7440269de37b338fa7be81940dd9c55a8` (14 Nov 12:39:50 CET). Independently verified all eight reviewed source/test/transitive-code hashes against the accepted B2 receipt and HEAD bytes. The three repaired AB1 paths have no worktree changes. The committed `OPENCODE_BATCHC_SOURCE_BINDING_20261114.md` explicitly binds the repaired sources and the 49-path receipt. This closes the earlier uncommitted-source condition for these exact bytes; it does not certify an entirely clean shared repository or authorize a read.

External input paths remain those in the accepted receipt, including the absolute live `check.FDIR` and `pn1lib.SPLIT`; a detached checkout cannot silently substitute its own floor/split directory. Reuse the accepted B2 input verification, with exact-byte verification at invocation. The descriptive companion output is already validated and should accompany the eventual reader artifact without repeating its calculation.

Registration commits independently resolved:

- `61f7994cc40bcb26b1f7be0689d2361c802e0061`, 13 Nov 09:21:59 CET: AB1's own 40 H100 fits, including Sb/B/Sp at 408–412. SE1/rented comparators are excluded.
- `35c8a9fd54fd04c153b7b93cf97cf1a621b86909`, 13 Nov 21:37:25 CET: amendment 7b adds BV and makes H-c2 BN−BV; batch C contains 15 fits.

Current `run_c.sh` and `ab1c_fit.sbatch` are byte-identical to their amendment-7b committed versions and registered hashes (`219ae9b0…`, `1376e0d0…`). Current AB1 `run.sh` is byte-identical to `61f7994` and the registered v2 hash `cfa4ed26…` (remote name `run_v2.sh`). Pack/overlay expectations remain FS1 pack `96c31ae2…`, AB1 overlay `171fdb21…`, Batch-C overlay `bf276e54…`. These are registered expected values, not newly inspected archive contents. Amendment 8 explicitly states that batch C did not have the missing-image fault; the held v2 submission is not evidence of a replacement job. The completed job under review remains 6316845.

## Archive and completion reconciliation

### Batch C: all 15 reconcile

MAIN's fresh local opaque receipt `/mnt/t7/smad_next/coordination_20261114/opencode_takeover/BATCHC_OPAQUE_LOCAL_INTEGRITY.json` is timestamped 14 Nov 11:35:23 UTC. Every Batch-C name, SHA256 and byte size matches:

1. `/mnt/t7/smad_next/coordination_20261114/NEW_ARCHIVE_REMOTE_HASHES.json` (historical remote hash inventory);
2. `/mnt/t7/smad_next/coordination_20261114/NEW_COLLECTION_VERIFIED.json`, collected/verified by **10:32:47 CET, 14 Nov**;
3. its byte-identical repository copy `experiments/RECORDS_ledger/codex_20261114/NEW_COLLECTION_VERIFIED.json`.

The source location is `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/AB1C/`; local location is `/mnt/t7/smad_next/coordination_20261114/archives/AB1C/`. Counts and expected task mapping are 3 arms × 5 seeds, with array index `3*(seed−408)+{SpV:0, BN:1, BV:2}`. The registered launcher establishes that mapping, not the archive filename alone.

`POST_SUBMISSION_STATE.json` (10:32:07 CET, 14 Nov) contains individual scheduler accounting for **6316845_0–14, all COMPLETED, exit 0:0**. Latest end is task 14 at **10:26:14 CET**. The JSON manifest retains every task's start/end and provenance. Arrival is bounded by the dated collection receipt; an exact per-file copy timestamp is not claimed. These 15 are demonstrably present before the amendment-7 deadline of **15 November 18:00 CET** and need no late label on the available evidence.

### Original AB1 comparators: provenance partly established; remaining gap explicit

The 15 paths are `/mnt/t7/smad_next/AB1/results/AB1_{Sb,B,Sp}_s{408..412}.tar`, from expected remote directory `/lustre/pd03/hpc-narolski-1790461090/smad-next/results/AB1/`. The saved submission command names **6310270**, registration `61f7994`, H100, AB1's own A/Sb and v2 overlay. Expected task indices are `8*(seed−408)+{Sb:1, B:2, Sp:3}`. They are not SE1 or FS1 sources.

Historical evidence:

- AB1 `README.md:69–80`: smoke 6310091 passed; all 40 fits completed exit 0 during 13:14–14:22 on 13 Nov; all 40 tars fetched and verified on T7 and Lustre.
- Dispatcher `MEMORY.md:127,137,148,153`: smoke independently checked; seven tars fetched at 13:17; 36 fetched/verified at 14:12; all 40 fits reported completed by 14:30. At 14:12, the four remaining tasks were 24/31/32/39, none among these 15 comparator task indices.
- `src/AB1/fetch_ab1.sh` identifies the exact remote/local directories and job-sidecar verification procedure. The script alone is not proof of an execution.
- All **five Sb hashes** in MAIN's local receipt also equal committed `AB1_SB_SOURCE_PINS` in HEAD's `src/NEXT/read_selection.py`. This is supplemental byte identity, not transfer of NEXT admission.

For **all 30 archives**, this reviewer independently checked current sidecar SHA256, advertised archive hash and filename against MAIN's receipt, and filesystem byte size. Archive hashing itself is reused from MAIN; no archive was opened or rehashed here.

**Gap:** no dated per-archive historical collection-hash receipt was located for the original AB1 comparators in the bounded metadata sources inspected. The recovery receipt for 128 archives contains none of these 15. In particular, B/Sp have no historical hash cross-check in this packet; aggregate historical completion/fetch statements do not prove current bytes are those fetched then. Individual comparator scheduler end times are unverified and remain null. Their historical arrival before the deadlines is reported by aggregate records, not independently established per file. Obtain raw accounting/copy evidence or an explicit evidence-backed independent disposition; do not invent timestamps or silently promote the aggregate record to per-file verification. MAIN's planned fresh remote hashes should resolve current two-copy byte identity but cannot alone prove historical arrival.

## Proposed execution, not executed

Use the committed reviewed reader from `/home/narolski/smad-next`, after separate final admission and explicit production authorization:

```bash
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 TMPDIR=/tmp/opencode nice -n 10 \
  /home/narolski/mambamorph-code/.venv-spark/bin/python -I \
  src/AB1/ab1_pm3_read.py --pair C \
  --c-results /mnt/t7/smad_next/coordination_20261114/archives/AB1C \
  --ab1-results /mnt/t7/smad_next/AB1/results \
  --out /mnt/t7/smad_next/AB1/c/read_20261114/ab1_pm3_read_C.json
```

Environment is the accepted B2 Python 3.12.3 / NumPy 1.26.4 environment; its complete build/BLAS record and hashes are linked in the JSON. Do not use `-O`. Preserve stdout as `read_20261114/stdout.log`, stderr as `stderr.log`, and timing/exit/admission/source/environment/output hashes as `execution.json`, all exclusive-create. The operator must capture failures as well as success and retain partial output.

At preparation time, `lexists` is false for the proposed output, three proposed logs/receipt, and canonical `/mnt/t7/smad_next/AB1/READ_ONCE_PM3/C.claim.json` and `C.complete.json`. **The proposed output directory does not yet exist.** MAIN must prepare it, verify ownership/writability and recheck all paths immediately before release. No directory or journal was created by this reviewer. The reader owns the atomic claim; never preclaim it.

## B3–B5 disposition and next step

1. **B3:** reviewed source binding is now committed and independently matched. All Batch-C historical opaque hashes/completions/arrival bounds reconcile. Still require MAIN's fresh remote opaque checks for all 30 and resolution of comparator historical per-file provenance/completion/arrival gaps. Bind the completed manifest and evidence hashes in final independent admission; this preparation JSON is not that admission.
2. **B4:** opaque hashes, sidecars, filenames and scheduler completion do not prove embedded TASK/ARM/SEED, unique ordered finite evaluation scores, embedded train/eval manifests, H100 provenance, steps/limit, pack/overlay, n_items or finite training losses. Those remain **native guards on the first separately authorized read**. Do not invoke `_validate_native_archive` during metadata preparation.
3. **B5:** prepare the output directory and exclusive logs, bind the final command/environment and fresh once checks, obtain explicit authorization, then preserve any refusal and permanent claim. No automatic deletion/retry. The registration's historical allowance of one unchanged H100 infrastructure retry is not authorization to rerun a read or retry a non-finite fit. Lost/missing/late outcomes stay visible; fewer than four readable paired seeds means “not read.” Loader refusals must receive independent disposition rather than silently becoming scientific failures. Independent results review precedes any conclusion.

No new test run, refit, candidate read, NEXT action, publication edit or scientific conclusion follows from this packet.

CLAIMS:
- commit 7d5e06b7440269de37b338fa7be81940dd9c55a8 reviewed AB1 source/reference binding; independently verified source bytes
- file OPENCODE_BATCHC_RELEASE_PREPARATION_20261114.json sha256 7c473741d5abf3cb
- number proposed archives = 30 @ OPENCODE_BATCHC_RELEASE_PREPARATION_20261114.json:archives
- number Batch-C historical hash matches and individual COMPLETED/0:0 records = 15 @ OPENCODE_BATCHC_RELEASE_PREPARATION_20261114.json:archives
- number committed Sb comparator pin matches = 5 @ OPENCODE_BATCHC_RELEASE_PREPARATION_20261114.json:archives
