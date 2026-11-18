# AD5 resource accounting audit — 2026-11-14

## Decision support

**I cannot attest at least 6 available H100 GPU-hours for MADation ViT-B/16 seed 401 from the evidence available.** No seed launch or budget reservation was made. The current verifier requires an explicit cumulative ledger, a convention, `available_h100_hours >= 6`, and `reserved_this_seed_hours = 6`; no populated ledger with those fields was found.

The registration initially set **250 GPU-hours** (`prereg.md:222`, 11 Nov 19:20). The later Amendment 2 allowance of **300 A100-hours** (`prereg.md:255`, 11 Nov 20:17) supersedes that earlier source entry. Amendment 4 subsequently moves the retrains to WCSS H100 without specifying an A100-to-H100 conversion or a new accounting convention. The latest written cap is therefore 300 A100-hours; it does not itself establish any available H100 balance.

## Native WCSS accounting

One successful, read-only `sacct` batch ran from GX10 to `ui.wcss.pl` under `/tmp/opencode/wcss-client.lock` using nested `ssh -n`. Authentication succeeded. The query was `-X -n -P -u narolski -S 2026-11-11T00:00:00` with JobID, JobName, State, ElapsedRaw, AllocTRES, ReqTRES, TimelimitRaw, Submit, Start, End and Account. Capture file mtime was 2026-11-14T20:50:43Z. `-X` excluded step rows; array tasks were counted once each.

The 500-row raw response contains 33 rows matching original AD5 MADation L/B, MixFaceNet, SelfMAD, IDistill/CB1ID, smoke and technical-recovery job names. The output gave no total-match count; because it returned exactly 500 lines, completeness beyond the returned rows is not established. Treat the filtered total below as a **known lower bound**, not a complete ledger.

For these 33 WCSS job/task rows, allocated GPU time to the snapshot is **66.8158 H100 GPU-hours**: 19.8839 hours from terminal jobs and **46.9319 hours already elapsed on jobs still running**. Running usage continues after the snapshot; pending and future use is unknown and is not counted as spent. Method breakdown: IDistill 16.2306; MADation including smoke/first-backward 0.3978; MixFaceNet 22.6328; SelfMAD 27.4556; synthetic/real technical-math jobs 0.0742; other AD5 diagnostic 0.0250 GPU-hours.

The allocation convention used the generic `AllocTRES gres/gpu` count where present, falling back to typed `gres/gpu:*` only if generic were absent. The selected rows carry both `gres/gpu` and `gres/gpu:hopper`; only the generic count was used, never both. `billing=8` was not counted as eight GPUs. All selected rows report account `hpc-narolski-1790461090`. Per-job time limits and the account string do not prove an account-level cap. No documented `sacctmgr`/association-limit command was found in AGENTS, CONTINUE or the compute policy, so native finite-versus-unlimited cap enforcement remains **unknown**.

## Other recorded resource use and unknowns

- Earlier Athena records list 2.445 A100 GPU-hours of smoke/scoring work (the README rounds this to 2.4 and its enumerated subtotal omits the 0.04-hour third scoring smoke) plus 6.77 A100 GPU-hours for descriptive MixFaceNet seed 401. These are kept separate from H100 usage; no A100-to-H100 conversion is applied. The Athena watcher currently reports `plgmorphgeneral` unavailable and no association visible; current Athena jobs/spend are unknown. No login was retried.
- The AD5 README records the DGX SelfMAD release scoring restarted at 20:02 and complete by 20:55 on 11 Nov. At most one GB10 over that 53-minute wall window is a coarse upper bound of 0.883 GB10 GPU-hours, not measured utilization. Other local DGX AD5 checks have no recorded duration in the located records; the RECORDS ledger explicitly marks IDistill DGX timing NOT CHECKABLE without its log. I did not read logs. Total GX-local exposure is therefore unbounded from this evidence.
- No actual cumulative budget ledger was found. `src/recovery_20261114/ad5_full_math_v2/verify.py` requires `budget_ledger_file`, explicit convention, finite available H100 hours and a 6-hour seed reservation; the current release skeleton contains only a ledger placeholder.

**Conclusion:** a 6-hour H100 headroom cannot be safely attested. The known WCSS elapsed total alone is not an available-balance ledger; remaining Athena/DGX debits and current/pending future usage are not fully bounded, and the A100 allowance has no stated H100 conversion. Native account-level enforcement is also unknown. Root should require the missing cumulative debits and explicit convention before deciding; this report does not authorize or reject a method on scientific grounds.

## Audit artifacts

- Raw native response: `WCSS_SACCT_RAW_20261114T200359Z.psv` (500 rows, 128,077 bytes, SHA256 `be06ef8f6964a95ffd6b89aaa734fdb77d7029449477ab3f2507cf307b672aab`).
- Machine-readable filtered accounting and calculation receipt: `AD5_RESOURCE_ACCOUNTING_20261114T200359Z.json`.
- Bounded note on an incidental broad-search text hit and its provenance limits: `AD5_RESOURCE_EXPOSURE_NOTE_20261114T200359Z.md`.
- WCSS stderr receipt is empty. No Slurm mutation, cancellation, GPU rental, timer, benchmark read or output-payload access occurred.
