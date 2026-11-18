# OTHER B(ii) timing control-plane v1r1 delta review — 2026-11-15

Reviewer Sol/sol_sbm512_bii_probe, OTHER than sol_bii_timing_launchprep. **HOLD_LAUNCHER_V1R1_CONFIG_SNAPSHOT_BINDING.** The four prior control defects are addressed structurally and operational worker/method bytes remain unchanged, but one new generated reproduction breaks exact preallocation config binding. Preserve this immutable version; source-only narrow revision/re-review required. No actual allocation/scheduler/WCSS, runtime/library import, GPU/model/image/NPZ/weight access or scientific journal/read occurred. All subprocesses in the independent reproduction are mocked. No author package changed.

## Exact packet and inherited scope

Package manifest d3f9e7f737d7878db1a0b7c546fd97b7b3f408347df217368a024819f3abe5b8 and all members verify. Old launch-prep packagecf47424b...f2a2225 remains intact. Operational worker manifest6dc4375db303042904ca0725c631515ffaf00d7afc4266bf8334d067c0b698c7 and every member match the prior copied worker exactly. Parent review61322ecf43d078d9c333558d380f48c8ef1b269dac11c3f81ccd5d29c1022a5d and its four corrections were read. No math/backend/cache/spec/order/gate change or full-mode release is introduced.

Exact timing scope stays seed408/original eval rows0–63:64native then64flip image forwards,2calls,13 selected cross native references at indices40–52, exact float32 bytes, no tolerance/fallback/reset. No TT1 image/reference opening or perturbation panel. Full compressed eval arrays24859rows still require explicit future decode permission;13 selected comparisons are not13-row physical decoding. Timing cannot certify13771 full native targets or TT1/history/14panel performance.

Seven supplied stdlib generated/preservation/control-order methods independently PASS7/7 in0.003s;33 negative contract subcases plus valid fixture and source-tamper fixture. Bash syntax of launch.sh/allocation_entry.sh PASS. These fixtures do not establish actual17-role truth or native/profile/input admission.

## Blocking reproduced issue: config hash then reopen

`launch.py:19–21` hashes `path` against the external expected digest, then separately reopens that path to parse JSON. Later checks and preallocation argv use the second document while CLAIM records the first digest. `launch.py:37` passes its parsed `node_bootstrap` to allocation_entry, which executes `$3` before node_driver's later config validation.

Independent generated reproduction starts with schema-valid synthetic config A containing `/synthetic/bootstrap`. The mocked sha routine hashes A, then replaces the generated config file with schema-valid B containing `/synthetic/UNBOUND_BOOTSTRAP` plus a syntactically valid content pin. Admission hashes are fixture values; every tmux/srun/subprocess operation is mocked, and outputs are in a temporary generated directory. launch.main returns0, CLAIM records expected hash(A), but INTENT/srun argv names B's UNBOUND_BOOTSTRAP. Current disk hash differs from CLAIM. This is a confirmed unbound control choice, not an actual unauthorized execution.

Node_driver correctly hashes/parses its own same raw snapshot later, but that cannot protect allocation_entry's earlier bootstrap exec from the unbound launch config. Root external source/tool staging checks are required, yet the launcher's promised exact-config guard must not authenticate one document and use another. This can arise from an ordinary concurrent final-config update; no model/payload or hypothetical hidden-state issue is needed.

Minimal correction in a NEW immutable version: obtain one bounded immutable config byte snapshot, compare its SHA to expected, parse and use those SAME authenticated bytes for validate/admission checks/CLAIM/INTENT/srun bootstrap argument. Never reopen config to derive launch-control values. It is acceptable to reject detected mutation before allocation; if path contents change after an authenticated snapshot, only snapshot A's bound choices may be used and node may later fail closed on mismatch. Add generated replacement/mutation regression proving no allocation argv can contain B's bootstrap/config choices under digest(A), plus oversize/parse-binding checks appropriate to the chosen bounded reader. Preserve worker source/semantics, fixed output, root permissions, no-retry and all original safeguards. No actual allocation or new source/runtime acquisition is needed to fix/test this.

Reviewer `test_config_snapshot.py` intentionally reproduces the current unsafe behavior; its PASS is successful bug reproduction, not a safety PASS. It ran1test in0.005s, with no native command executed.

## Four earlier fixes verified structurally

1. Permanent fixed dispatch CLAIM and fsynced INTENT precede srun; real detached tmux PTY/pipe transcript/remain-on-exit and terminal reconciliation record are concrete. allocation_entry emits/fsyncs native job ID before Python. Missing ID/terminal remains UNKNOWN/incomplete requiring root reconciliation, never presumed unallocated or auto-retried.
2. Fixed dispatch/worker directories and whole staged worker manifest/member verification precede child imports. Generated source tampering refuses. External bootstrap/launcher/driver/contract/tools/staging pins still must be verified before startup. Worker/math bytes are unchanged.
3. Explicit `gpu:hopper:1,storage:local:8G`, interactive partition,8CPUs/32G/15min and immediate60s bound replace generic GPU selection. Node checks native partition/job/CPU/task/memory; actual Hopper/GRES/account/capacity and full profile require separately pinned native policy. Outer1200s/child840s are failure bounds, not completion estimates or a capacity guarantee.
4. Control bootstrap uses -I -S -B; child uses -E -s -B, explicitly preventing pyc despite -E ignoring environment variables. Child still has normal site startup, whose .pth/module/venv resolution must be actually reviewed. Isolated phase1 evidence does not alone admit that context. Runtime phase1's separate b7a82… review/fix is not duplicated here.

The binding provenance correction is right:43 current metadata identities were acquired ON WCSS and mirrored to GX, not a GX environment portability observation. All are current source/metadata anchors, zero native-library bodies; no redundant identity probe is required. A schema's ROOT_ADOPTED strings/content-pin slots are not actual semantic admission evidence.

## Remaining actual launch holds remain independent

All17 proposed role objects remain PENDING; no root execution release exists. Source fixes must not fill runtime/input/schema/positional/history booleans from status strings or metadata alone. Actual original64image bodies, base/config/frozen-weight provenance, overlay/meta schema, eval-container association/decode permission, native/import/default/worker/startup evidence, source-bound reconstruction policy, output mount/capacity and exposure/root permissions stay separately required. No universal hidden-cache theorem is demanded; firstbatch empirical equality has its already adopted limited interpretation.

8Gscratch/32Ghost/15min is still a resource proposal. No stage byte census/free-capacity observation establishes sufficiency or insufficiency here. The explicit localTMPDIR mapping or separately bounded Lustre firstbatch exception must be actually reviewed/adopted; no automatic staging/mount or bulk-I/O exception is created. Local mapping must bind actual final admission/release paths before child, preserving content/order and durable claims. This control extension does not implement or invent that staging workflow.

Time accounting remains PRE_WORKER content verification, whole child process/Backend cold setup, post-Backend worker interval and process GPU peak; subtraction is only approximate setup overhead. Staging/collection/native elapsed remain distinct. Exit0 alone would not admit technical PASS, full-kernel or NEXT science.

Stop after this concrete source-control HOLD. Root can request the narrow snapshot correction and independent delta re-review; no actual17-role/runtime/input/native/profile or GPU release follows from this report.
