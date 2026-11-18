# Common AB1 fresh entry V3 — conditional source handoff

SOURCE ONLY. No actual winner, selection/admission payload, runtime, model, input pack, GPU, scheduler or scientific preflight was accessed. No training/native scorer was executed. V1 and permanently disabled V2 are preserved. This is a reviewable conditional executable, not actual fit authority.

## Concrete entry and trust boundary

The sole supported entry is source/run_guarded.py, launched by the leader from the exact committed/reviewed package with a clean bootstrap environment and an externally verified root-release SHA256. The root-release SHA is the external trust anchor; a caller inventing both a release and its hash has not obtained root authorization. No current grant exists. ROOT_RELEASE_TEMPLATE_HOLD.json deliberately denies entry.

Prospective invocation shape (placeholders are NOT commands or permission):

    env -i PATH=/usr/bin:/bin LANG=C.UTF-8 /usr/bin/python3 -E -s <exact-staged-source>/run_guarded.py --root-release <root-committed-release.json> --root-release-sha256 <externally-verified-root-grant-SHA> --task-env <literal-task-file> --work-dir <reviewed-empty-local-TMPDIR>

Bootstrap /usr/bin/python3 and its root-managed startup/stdlib provenance must be pinned outside startup by the leader, consistent with the separate runtime admission. The code cannot authenticate its own first instruction. Root must review/adopt this concrete bootstrap/source policy before use; there is no actual runtime/import probe in this package.

Order is explicit: bounded same-bytes-hashed root/control records -> exact selected winner and independent selection admission -> exact adopted selected full cohort/common-AB1 subset -> source/method review, runtime/input, resource/budget/durability and no-duplicate metadata -> staged opaque source/runtime/input hashes -> literal task parsing and exact role/seed check -> empty local work and fixed fresh durable namespace checks -> create-only claim/logs -> worker authority recheck -> parent training/native scoring. No task.env is ever interpreted as untrusted shell code. The wrapper parses only TASK/ARM/SEED literal assignments, writes a private0400 generated task.env; the native shell rechecks authority and canonical claim/task path before its original source statement.

source/run_ab1_fresh.sh is a new version, not removal of V2's HOLD in place. Its first executable operation invokes worker_gate.py before task.env. A direct shell invocation without valid authority/claimed exact task refuses. No alternate historical seed guards/selector/journals are broadened. Authority gate and worker source contain no test bypass, fixture CLI, model import or scoring reader.

## Exact source/role/permission binding

POLICY.json binds the approved original rule, adopted scope, V2 review/manifest/parent, exact190 alternative conditional role identities and70 commonAB1 roles. Only eventual selected branch can match. GX is refused; Sbc additionally requires admitted crop ruling. It does not choose an arm or recompute scientific qualifications. Selection/admission schemas are prospective control contracts; root must derive them from the actual independently admitted original once-selection, never fabricate a winner or turn descriptive support into new bars.

Parent AB1 pack/overlay/architecture/train_A|B|Sb/eval ab1_eval.csv/6250steps/batch256/last/learning rates/scorer command remain original. Generated tests verify training and native scorer command text byte for byte against the pinned original parent. Task identities/seeds413–417/new output root/production guards are restricted independently. POLICY records known immutable pack/overlay path/digests rather than generic nulls; actual staged-byte admission remains missing. This source does not implement SbFM/RZ1/E3 training, fresh native scientific adapters, TT1/MEDS/border/kernel/refit support or final confirmation statistics.

The root decision must be GO_FRESH_COMMON_AB1_FIT_AND_REGISTERED_DEV_NATIVE_SCORE with permissions exactly COMMON_AB1_FIT and AB1_REGISTERED_DEV_EVAL_AND_TRAIN_NATIVE_SCORE, sealed_access=false and scientific_confirmation_read=false. A blanket FIT_ONLY release is refused because the original parent calls pn1_score.py on its registered ab1_eval and training rows. No still-sealed benchmark path is supplied. Unseen benchmark/final confirmation access needs a separate exact release and adapter. Output storage does not authorize scientific result inspection.

## Durability and failure behavior

Prospective source stage is the fixed WCSS packs/NEXTCONF_V3/source; durable results/claims are fixed results/NEXTCONF_V3 under the original WCSS root. These new paths are proposals requiring root adoption and clean absent namespace/actual byte-capacity evidence; no directory there was created. Each exact task gets a create-only directory/CLAIM, generated task, STARTING/RUNNING, stdout.log/stderr.log and terminal record. Existing claims or tar/part/sidecar refuse; no deletion, overwrite, auto retry or seed replacement. Clean child environment removes inherited BASH_ENV, LD/PYTHON/test/warmstart settings.

After original training completes and verifies last.pt/meta, the new producer copies full original last.pt to its private durable last.pt.part, syncs and renames before original native scoring. This retains the actual last checkpoint even if native scoring subsequently fails. Existing trainable/frozen-base reconstruction provenance is not replaced or declared invalid. Future collection must include claim directory/checkpoint AND result tar/sidecar with fresh remote/local hashes and receipts, then mirror durably on GX10/T7. Full-checkpoint output space is an explicit resource-admission responsibility.

TERM/INT handlers record signal and forward to only the fixture/worker process group; stdout/stderr are already open directly on durable files. SIGKILL cannot run a handler: its retained claim/RUNNING/log/checkpoint with absent terminal is UNKNOWN/unfinished, never PASS; the fixed claim prohibits retry. A kill before checkpoint creation cannot retain a checkpoint that does not exist; partial last.pt.part remains evidence if copying was interrupted. All missing/failed seeds remain visible and denominator policy unchanged.

## Generated evidence and next action

GENERATED_TEST_RESULTS.json records13 passing methods: denial before task/staged data, explicit scoring permission, pinned metadata/provenance/selection/role/cohort mismatches, malformed/untrusted task code never executed, old/bad seeds refused, no overwrite, TERM/KILL log/checkpoint durability with fake subprocesses only, exact190/70 counts, original scientific command preservation, shell syntax and self source pins. No test invokes the scientific shell or a model.

Next is OTHER independent review of this immutable source/method/entry/worker/claim implementation and control schemas. Runtime build, source bootstrap, input/resource/admission/budget/duplicate receipts, actual admitted winner/full registration, exact root fit+registered-dev-score release and independently reviewed remaining fresh adapters are all HOLD. No stage is opened by these tests. Root alone may prospectively adopt reviewed code and later issue exact authority from a clean owned-source checkout.
