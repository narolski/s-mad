# Independent runtime-only phase1 source review — 2026-11-15

Verdict: HOLD_SOURCE_FIX for this exact package. The narrow runtime-only design and separation from the 17 model/input gates are suitable; execution is not authorized by this review.

Reviewed source manifest: 910f05bf4e8a5c341aaec1f270b0a6a82164a630a164ceca7242ab5fbdb6525e.
Reviewed package manifest: 2331bd103e55c3234449058c8a31ff67705d42d581ec0fc3e2a72a9580d33b35.
Probe: 6304d4705937d05e3aad9ee53306f6474490f749b6bc2a49ce37d7193299e26f.
All 6 source and 14 package members match. Independently reran all four supplied generated methods (PASS), Bash syntax and Python AST checks. Two additional generated-file reproductions succeeded in demonstrating the confinement defect. No actual target import, library, interpreter, driver, environment, archive, model, input, weight, reference, GPU, WCSS or scheduler was accessed. Author files unchanged.

## Blocking source findings

1. probe.py inside()/file_identity(): lexical parent membership plus leaf-only O_NOFOLLOW does not confine reads. A generated allowed/jump ancestor symlink to an outside directory and an allowed/../outside path both returned the SHA of an outside-grant synthetic 18-byte ELF. The current body grant therefore does not enforce its file class. Reject parent traversal and use descriptor-relative ancestor confinement, with any necessary system-library aliases explicitly registered and validated rather than an unrestricted resolve/follow operation. Retain regular-file checks, bounded same-descriptor reads and before/after identity. Add both reproductions as rejection fixtures, plus ancestor replacement.

2. parse_maps() discards device/inode and file_identity() has no mapped identity argument. Hashing a pathname after maps capture can identify a replacement file rather than the mapped file. Carry device/inode from the captured map records, reject inconsistent entries for one path, and compare the opened descriptor's device/inode before reading the body. This is a specific current observation binding, not a universal dependency-closure or historical-cache theorem. Add a synthetic mapped-inode mismatch fixture. For streaming cap correctness, bound reads by the remaining approved snapshot size plus a one-byte growth check, rather than reading an unrestricted 4MiB chunk past the approved size.

## Driver identity and remaining execution gates

The proposed nvidia_smi_sha256 is null and the current probe correctly refuses it. A login-node copy is not evidence for the compute-node tool. Root can either provide a separately justified exact compute-node pin, or authorize a narrowly revised source mode that acquires the identity of fixed /usr/bin/nvidia-smi as trusted root-managed OS software before the fixed driver-only query. Such a mode needs explicit grant fields, confined canonical/registered-alias handling, regular-file and size/stability checks, owner/non-writable trust checks, a recorded SHA, and no PATH search or alternative command. Keep the exact driver query, bounded output/time and numeric driver-version grammar. Do not fabricate a preknown node hash or run this version with null. This is a small explicit technical acquisition permission, not a demand to know all native libraries before importing.

Root must externally verify staged launcher, contract, shell, node bootstrap, manifest and tools before starting them: launch.py verifies admission hashes before CLAIM, but content/member verification is performed by node_driver after allocation; its comment claiming all source is checked before preallocation is broader than the implementation. Correct the comment or add those checks. A trusted staging preflight can supply the required prelaunch verification without model gates.

The five admissions must be real root records with exact source/independent-review binding, current identity reuse, runtime-import scope including CUDA initialization, native file-class/body permission and site profile. The proposed 2CPU/8G/1G/5min resources are unmeasured and require native placement/tool checks and staged-byte/free-space census; they are not runtime sufficiency evidence. No source-only review signs these records.

## Controls and accepted limits

The fixed five imports, -I -S -B, explicit site-packages addition, private empty cache/home paths and offline settings establish a prospective isolated import context. No explicit model constructor, checkpoint/image/NPZ reader, model forward or optimizer is called. Package import and CUDA metadata calls nevertheless execute native software, so their future explicit technical permission remains necessary. This context is not an assertion that the future -E -s model worker or historical startup had equivalent state.

The launcher has a permanent preallocation CLAIM and durable INTENT before srun; actual detached tmux PTY, pipe transcript/remain-on-exit, immediate=60, hopper resource, early fsynced native ID before Python, 480s outer/240s child bounds and no retry are present. Missing native ID remains reconciliation-required, never proof of nonallocation. Root must reconcile native terminal state after any result/failure. Claim and partial logs must be retained.

Existing 43 identity fields describe current WCSS files mirrored to GX, not an executed GX environment or historical identity. Reuse their adopted receipt 7847e2007570f75012f36fccd9257f73231c9a28cafbfb38ba86c2286d76e61b; no redundant standalone probe is required. Loaded-library observations cover only this process/time; later kernels and unobserved package bodies remain unknown.

## Minimal next step

Author freezes a new immutable source revision correcting the two read-boundary defects and resolving the explicit driver identity mode (or retaining exact-pin mode with a genuinely available root pin). OTHER reviewer performs a narrow generated delta review. Root then supplies the five real technical admissions, exact stage/tool/native profile checks and a new explicit runtime-only release. Only that permits the first necessary import/CUDA metadata probe; postcollection review precedes adoption. No model construction, first-batch timing, full TT1/panels, scientific reader or NEXT claim follows automatically.
