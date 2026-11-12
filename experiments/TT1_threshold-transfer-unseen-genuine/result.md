# Threshold transfer on unseen genuine sources (TT1): result

Status at the commit that adds this file (after `date` Thu Nov 12 11:09:10 PM CET 2026): pools built and aligned; no
network has been scored. Scoring registration: draft `prereg_scoring_draft.md`, waiting for independent pre-run review. No result yet: the platform gate failed on the DGX (max |Δlogit| up to 0.116 on FFHQ genuine rows; cause in the
network computation on the GB10 stack, decode and resize bit-identical) and, narrowly, on the rented A100 (FFHQ rows
differ at float32 last-bit level, 1e-6 to 2.2e-5, against a registered byte-identity rule). No TT1 row has been scored on
any platform. Gate files: `gate_dgx_run2.json`, `gate_a100.json`; diagnostic `diag_stack_compare.json`.

Pool counts: `pools_summary.md` (per source and per family).
