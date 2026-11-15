# Independent new synthetic SDPA launcher prereview — 2026-11-14

Reviewer: Astra (astra_sprint_plan_review), independent of launcher author astra_compute_unblock_plan.
Decision: **CONDITIONAL_GO_ONE_NEW_SYNTHETIC_SDPA_INTERACTIVE_V1** for the exact source/resources below after root completes the concrete native prelaunch gates. No blocking source correction found. This is not an execution release, original-training retry, migration, model smoke, scientific read or production approval.

## Exact pins and independent checks

- Launcher SHA256SUMS:644ea85a9d6308c6362e7c138fa7aec85f452217e338742abbe24ae15a3e47ce.
- launch.py:df9d6544e9169c049a317c0b50aefe33add924c95a945d9e4eab3c20596aba04.
- allocation_entry.sh:b6077a9ae271e5e99f3195498fae87b646aec30b383c05cbe24f1dd8c09db29c.
- node.py:e316761f11995870c85b4cf993be150b444433c03987934ee31eb537f9b4ecee.
- test_mock.py:4a8c2d6577b38ef1d3f9255975cec4e2757d843f40a1bfccae12a0ce9450a693.
- Handoff:d1fcf49ea70ee9a01b0877945ecd65ebdec1ba1ca80950b95a38ee284349de6e.
- Unchanged synthetic probe manifest:8138eb69a50c9724ca20417148e1b5373fd12d2e1c8d139710e8eb9b9bb54b5b.
- Unchanged worker:7c3b602bdf091bf4d593ed5d5c0c5874ecea10723538b4feb32f4d2df6b3a76d.
- Existing source-design review:7d2b92f9f814a35608abc26870609f8bee421788067225fd9e008aaa2df3a45e.
- Bound prereg:d1d028032773f68541515cbd982c741ee031ef60cb5dc7ffb36be95416f6092a.
- Independent generated-only evidence SDPA_LAUNCHER_INDEPENDENT_MOCK_CHECKS_20261114.json:0e41d8ecd24a0e7e3d183010653162914a61f08fcaabf576c506dbec04a82201.

Rehashed both manifests and every listed member. Read actual launcher, shell wrapper, node controller, unchanged worker/probe and handoff. AST parsing/in-memory compilation of launcher Python and bash-n passed. Independently ran all4 test methods: PASS,0.031s. Five launcher scenarios cover success, capacity failure/no ID, allocated timeout/nonzero, allocated failure and launch exception. Four node-status fixtures preserve (0,0),(1,0),(1,2),(missing,missing), including failures despite worker0. Non-TTY refuses before release/claim; repeated invocation refuses before a second allocation. Real generated shell fixture retains native ID before fake Python exits73 and noclobber prevents a second entry. No real tmux, Slurm, CUDA or WCSS call executed by tests; verify_release is mocked in branch tests, so release checks were reviewed statically, not claimed as live site validation.

## Launch/control boundary: PASS

Actual direct srun argv includes --pty, --immediate=60, lem-gpu-interactive, one node/task,8CPUs,120G memory, one hopper GPU,150G local storage,15minutes and FORCE_RM_TMPDIR. No stdout pipe replaces PTY. tmux supplies controlling terminal; launcher requires stdin/stdoutTTY and TMUX_PANE. It enables remain-on-exit and durable pipe-pane transcript before srun.

Release/source/pack verification precedes permanent exclusive/fsynced CLAIM; allocation follows claim and durable INTENT. A failed setup after claim is terminal rather than a retry. The wrapper exclusively writes and syncs NATIVE_JOB_ID before invoking Python, including Python startup failure. It cannot guarantee an ID if scheduler/node failure prevents the wrapper from starting: missing ID is explicitly UNKNOWN_REQUIRES_ROOT_RECONCILIATION. srun/worker0 is explicitly not operator PASS. Separate default/math statuses and missing-status incompleteness remain recorded.

Launcher allocation environment is an explicit clean base; inherited TMPDIR/PYTHONPATH/PYTHONHOME/AD5 overrides are not passed. Node forwards native SLURM values, CUDA_VISIBLE_DEVICES/TMPDIR/TERM and clean base only; validates partition,8CPU,one visible GPU,PTY and unchanged worker. Actual H100/Python3.9/torch2.0.1+cu118/CUDA11.8 assertions remain in unchanged probe. Worker validates offline wheelpack3bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c, uses local TMPDIR and preserves each backend result before next fresh process.

Original FAILED6321768_401 is only a release provenance field with old_job_action NONE. No cancel, migration, old-job replay, automatic retry, batch fallback or resource-relaxation branch exists.

## Scientific workload and interpretation remain bounded

Exactly two fresh synthetic processes: default SDPA and math-only, fixed seed20261114, float32 source-inferred256×12×197×64 layout/strides and synthetic upstream gradient. No model, training images, checkpoint or weights. Inputs/hashes, runtime/device, actual grad_fn, synchronized forward/backward and finite output/gradient checks are logged.

A differing result can localize this synthetic path to backend/runtime behavior; it does not establish the original failure's unique root cause, backend numerical equivalence, actual model-gradient correctness or production recovery. Compare both input/gradient hashes and actual backend observations post-run. Source-inferred shape is not captured activation evidence. Native scheduler timeout bounds the whole15minute allocation, including setup; a partial attempt is incomplete and retained.

## Concrete root prelaunch gates — required, no additional design cycle

1. Commit and verify only owned exact sources/evidence; stage identical launcher/probe manifests and exact wheelpack. Hash all staged bytes and attach clean-commit evidence.
2. Obtain fresh native site evidence for actual interactive partition/QoS capacity and requested1H100/8CPU/120G/150Glocal/15min resources, no conflicting job/session for this new scope, fresh dedicated tmux name, absent worker keep namespace and sufficient durable space≥50GiB. This review performs no site query and makes no site-capacity claim.
3. Issue separate ROOT_RELEASE.json with GO_ONE_NEW_SYNTHETIC_SDPA_INTERACTIVE_V1, exact source/prereg/design review/this launcher-review hashes, root_authorized true, distinct author/reviewer, automatic_retry false, scientific_read HOLD, truthful site/owned-commit evidence and old_job_action NONE. Launcher validates hashes and attestation fields; it does not independently prove site capacity or Git cleanliness.
4. Execute once using the handoff's dedicated real-tmux command under the existing shared WCSS SSH lock. --immediate60 failure is a permanent attempted dispatch, not permission to retry. Root must reconcile transcript/native jobname/user/time/accounting if ID is missing, and native terminal state even if ID exists.
5. Collect entire journal, transcript, worker keep files and native accounting status/start/end/exit to fresh durable storage with hash/size verification. Host loss/SIGKILL may prevent terminal/NODE_EXIT or final copying; preserve partial evidence and reconcile, never manufacture NOT_ALLOCATED or repeat automatically.

Conditional GO applies only when those exact root gates pass. No actual login to WCSS, scheduler query, submission/cancellation, GPU/inference or scientific payload access occurred in this review. Author sources remain untouched.
