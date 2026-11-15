# Recovery of the AB1 refit yardstick rescoring

WCSS job 6316319 failed at 10:14:33 CET on 14 November 2026 after 5 minutes 16 seconds. Its first network, AB1 A seed 408, passed the 21,277-row byte-identity gate and produced a durable archive. The next iteration stopped at `ln -sfn` with `Invalid cross-device link` while replacing the scratch training-manifest symlink. This is an orchestration failure before the next network's scoring, not a scientific outcome or a failed network fit.

Evidence: `/mnt/t7/smad_next/coordination_20261114/YARDSTICK_AND_PRESERVATION.json`. No production archive was opened by the lead.

The retry uses new files `src/RZ1/run_rz1r_linkfix.sh` and `src/RZ1/wcss/rz1-rescore-linkfix.sbatch`. The only runner change replaces that forced symlink replacement with an explicit check: unlink an existing symlink owned by this scratch task; refuse to replace a real file; create the new symlink normally. Training data, networks, manifests, platform, scorer, byte-identity gate, cross table and all scientific rules are unchanged. The original source and failure remain intact.

The runner retains original idempotence: hash-verified completed outputs are skipped and never overwritten. Thus A seed 408 remains its original completed output; the retry continues the remaining nine networks. Failed gate outputs remain failures and are not rescored as passes. This is the single infrastructure retry permitted by the RZ1 registration. The reviewer must verify its eligibility for that retry and the absence of any earlier retry.

The array's comparator outputs are still required for the approved selection rule; this recovery does not release any challenger result for reading. Output stays in `results/RZ1R` with per-file SHA256 sidecars and source provenance. The new wrapper pins the new runner's SHA256; all data/scorer pins are inherited unchanged.

After independent pre-run review and registration commit, stage both new files under the existing `packs/RZ1` directory and verify their SHA256. Submit once, under the WCSS lock, after checking for duplicate jobs:

```bash
cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/RZ1 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR --nice=9 rz1-rescore-linkfix.sbatch
```

Owner: Codex lead. Limit 2 hours 30 minutes inherited from the registered rescoring workload. Expected runtime about 45 minutes after start, based on the first completed network plus input staging. Preserve intent, submission receipt and native scheduler identity durably. At completion collect and hash-verify outputs before any eligible analysis.

The original smoke 6316283 is still required to have passed. It is no longer usable as an `afterok` dependency: the 512 continuation submission at 10:25:53 was rejected with `Job dependency problem` because the completed smoke aged out of controller memory. Before this retry, check accounting in the same submission operation for 6316283 COMPLETED/0:0, verify the committed finite-score/pre-post-guard smoke evidence and runner pins, and fail closed if any check is absent. Omitting an unusable scheduler dependency does not waive the smoke gate. The independent review addendum must approve this explicit gate before submission.
