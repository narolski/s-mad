# Method comparisons: source and technical-metadata handoff

Owner /root/sol_method_comparisons; bounded audit14November2026. Latest compute evidence: COMPUTE_HEARTBEAT_20261114T152955Z.md, observation about15:30UTC/16:30CET. No scheduler queries, job mutations, GPU work, rentals, checkpoint/NPZ/score reads or archive extraction by this owner. Existing Astra unblock plan reused, not replaced.

## Dispatch decision

**No new baseline GPU job is READY. Root should collect and independently admit the existing diagnostic technical packet now, zero GPU.** IDistill6319494 completed but no complete durable technical-admission packet was found in bounded cached inventory. MADation6319495_401 failed historically; no first synchronous traceback was found locally. A clipping repair is not yet supported. Preserve running production and every failed attempt. Do not repeat smokes whose receipts already exist.

## Authoritative status, separated from scientific eligibility

| Output | Latest recorded state | Eligibility / action |
|---|---|---|
| MADation B/L H100 | Original smoke6310087_401 and arrays6310124/6310126 failed. Synchronous diagnostic6319495_401 FAILED1:0 in1m30s | Ineligible retrains. Diagnostic failure known since about13:08CET, NOT new. First synchronous training traceback needed; original asynchronous clipping illegal instruction and cleanup SIGABRT are not a proven synchronous diagnosis. |
| MADation Athena | Historical3545814_[401–405],3545813_[402–405] pending | Current scheduler state unknown here. Preserve; exact seed-twin reconciliation required before any duplicate/cancellation. Requested association unavailable in cached watcher. |
| MixFaceNet H1006310125 | 401–402 COMPLETED,403–404 RUNNING,405 PENDING | Completion is not archive/scoring admission. Five-seed verdict incomplete. Preserve and opaque-collect once. |
| MixFaceNet A1003545870_401 | Historical completed, archive hash verified in AD5 record | Descriptive cu117 cross-platform check outside H100 method verdict; never substitute it for H100401. |
| SelfMAD H1006310127 | 401–402 RUNNING,403–405 PENDING | No completed H100 seed established by heartbeat. Preserve. Earlier Athena missing-save-parent failures/code_v5 recovery remain historical failures. |
| IDistill original smoke6312775 | TIMEOUT retained | Bare wait included infinite monitor; orchestration failure, not smoke pass. |
| IDistill waitfix6319494 | COMPLETED0:0,3m11s | Needs independent technical acceptance of existing outputs. DONE or scheduler success alone insufficient. |
| IDistill production6312778 | RUNNING | Unadmitted: production started before valid smoke. Needs explicit score-blind operational salvage exception or reviewed fixed-rerun disposition; later smoke cannot automatically admit it. |
| IDistill DGX AE/classifier401 | Historical completed and archives/smoke SHA verified | Separate one-seed ARM/GB10/torch2.12 variant under CB1 amendment3; not H100 three-seed set or faithful-stack proof. No new scientific verdict here. |

Sources: latest heartbeat; AD5 prereg amendments4–7 and RECOVERY_20261114.md; CB1 prereg and RECOVERY_20261114.md; PRERUN_CB1_WAIT_RECOVERY_20261114.md; NOTEBOOK. Older AD5 result.md saying no retrain exists and AGENT_STATUS queue snapshots are stale for current compute state.

## Method/source/checkpoint/recipe evidence

Release hashes below come from existing OCC1 INPUT_MODEL_PINS.json and AD5 registration, not checkpoint reads or fresh integrity verification.

| Method | Authors' source / release | Our registered retrain |
|---|---|---|
| MADation B/L | gurayozgur/MADation0542cf86; B ddb1455bae4b72331aff4806590bd88ba2447563d803e207099c6b712d6bbe2f; L bb452ded624ffce2dc85168f8dde9293fc3709ec8cce755d8ecf1d5f5370e980 | Cropped SMDD39723rows;401–405; LoRA r2,B alpha4/dropout.4,L alpha8/dropout.2; backbone/header lr1e-5/1e-4; globalbatch256,40epochs,epoch40 backbone+header only. H100B1x256/L2x128, registered fit fallbackB2x128/L4x64; Python3.9,torch2.0.1/vision.15.2cu118; AD5_NO_TEST=1. |
| MixFaceNet | naserdamer/SMDD9683229c; release3d507c8bbd5dbd06bd735ae809fa0095e589c17c0c94cd2ed530cf34a014ab1c | Same cropped SMDD;401–405,batch16,100epochs,AD5_LAST=1,no test-selected early stopping,epoch100 primary. Retained other epochs do not authorize selection. H100/cu118 five-seed set. |
| SelfMAD | LeonTodorov/SelfMAD09ed0819(code673d0640); release0ad8db6f8f156cb21606e03ab32c88d122640cb835f7a93c77cca30c01386a26 | HRNetW18,25000SMDD genuine renders with own landmarks/labels;401–405,batch32,lr5e-4,100epochs,epoch100 primary. Optional registered oracle-epoch diagnostic separately labelled; no substitution for primary. |
| IDistill | NetoPedro/IDistill0473bb43007bb0088e90d226b59a2208d7e45856; no released checkpoint asserted | UNetAE latent128,seed420,300epochs,batch32,Adam1e-4,MSE; classifierResNet18 product fusion,prefusion BCE+KDweight1,Adam1e-4,batch16,<=250epochs,401–403; split420/authorsCUDAseed0. Keep test-selected/validation-selected/last distinct. Last stopping epoch still test-dependent through early stopping. |

Released-weights/our-scoring rows differ from our retrains of authors' code. AD5 all-five headline remains incomplete(k seeds) before five finish; reproduction/matches-release windows are labels/secondary strata, not a filter hiding failures. Keep RS1 unchanged/corrected crop variants labelled, MADation conversion CPU-equivalence gate, SelfMAD own landmark+6.25%/384/softmax path and MADation/MixFaceNet224/BGR/noTTA adapters. Earlier withdrawn original-crop MorDIFF rows remain withdrawn. No benchmark access expansion.

OCC1 official B numerical-parity and official L placement failures involve released networks, not AD5 fits. OCC1 remains with figures owner/existing Astra plan: five completed models require review; instrumentation retries require registration/review; FERET export forbidden. No duplicated OCC1 work.

## Immutable source and pack metadata

Source hashes verified in this audit:
- AD5 prereg6316790fe09ad6b6da1c1781f2b9630f5d7fe2ae197b3993e1f6123adcc2ad47
- CB1 prereg389bf2782db1c4feb167896ba75fce53d52067ad1f241d4eb380c200f8291ef7
- existing Astra unblock plan3ac8f06b9116863a421aa8219d826bcb9a658580c09898c17b28517b1aa18615
- synthetic clip_grad_probe.py7a8201f67ee73f3c757b7c033dea7cb52b2c09e249cf8285641a78d38cd77279
Reviewed scripts per submission/review dc07fd7: waitfix24304001f933259ffdb82f50695719f1ad82233b65def8e50c876ba871c4b541; launchblocking a1faf156564b3e98ce3e3c61bc3012d2a6bae48dee07a49215f1cb47dd28d37e.

Existing AD5 WCSS sidecars (not fresh content verification):
- code94964c3689aa866ad7700f4b86496590c1b353e8e8be59173158e7b46c35d6ee
- wheels393bd18def4da9cbec2766896fa160c34c0364de464ca3abd02d675c72620cf13c
- croppedSMDD3189e52af12e2853b06c86993b1b8b5cfef891fda749395778492e3445924900
- SelfMADcode b661f73e811735a5e16ad48af4061717c86bc195e5f32bc798cdb21532a77467
- SelfMADdata fc386dac8bd3a9a8dfd8960197559fb912c960a37b4a66326b5aaa7658880cb1
- SelfMADwheels8565c2916a9cca857c9dc7ac0401197a18ef344018f08746f19589eb7d32f554

CB1 sidecars: idistill_code.tar07794689c13d204909bee58f4f1378ac09a2c6f5b19f64c867f1e521a44a44a0; separately named v4code3669936cb95f819d7c499b6b8b071ef166bd437176325e1d3086d9d74de40c19; data aa1614369b43177bc53d7b21c7c4d2d2a48d8460611b9801eea59b7934140d15; cu118wheels4cfdd6aeb47948b6eeda396b18c40d1231ea0b4c96ab77c9fb2bf85f29874002; same croppedSMDD. Script actually references idistill_code.tar; do not assume separate v4 filename was executed. Bind actual remote pack sidecars in collection.

## Exact next root action: collect existing diagnostics, zero GPU

Reuse newer cached collection if one exists. Root uses existing WCSS endpoint ui.wcss.pl under gx10 flock /tmp/opencode/wcss-client.lock, single connection. No failed-login retries. Base /lustre/pd03/hpc-narolski-1790461090/smad-next. Duplicate check is existing BASELINE_DIAGNOSTIC_SUBMISSION_RECEIPT.json: dc07fd7 already submitted6319494/6319495; never replay those sbatch commands.

Collect these exact existing technical sources:
1. logs/CB1/cb1ids-cb1ids_smoke_waitfix-6319494.out, retained opaquely because raw stdout can contain Lowest EER.
2. results/CB1/idistill_all_smoke_waitfix_20261114.tar plus sidecar, opaquely; remote and durable-local SHA, size,mtime and member names/sizes only.
3. AD5/logs/keep/madation_B_s401_smoke_diag_launchblocking_20261114/train_stdout.log plus training.log/gpumem.csv if present. AD5_NO_TEST=1 permits training-only traceback. Resolve actual stdout path from receipt: initial native path contains array placeholder4294967294; do not fabricate401 suffix.
4. Executed scripts/pack sidecars, package/runtime identities and original paths/timestamps.

Create durable /mnt/t7/smad_next/coordination_20261114/baseline_technical_collection_<UTC>, create-only manifest+SHA receipt+allowlisted summary. Check actual space/size before copying. Print only IDistill architecture/matmul,worker-exit,DONE,error markers, no metric lines. No score-file extraction or values. Existing CB1 recovery permits technical member-existence checks; independent reviewer requires COMPLETED0, fresh DONE,workers401/402/403exit0,expected nonempty best/valbest/last+score members,no subprocess error,H100 architecture/runtime/exactpack checks. DONE is printed before final failure exit4, so alone insufficient. Preserve deviation: implemented smoke2AEepochs/256BF+6classifierepochs/128morphs versus original1epoch/64 prose.

Required durable outputs: technical collection manifest and hashes; independent smoke verdict; explicit score-blind production6312778 disposition; first synchronous MADation exception/source frame. CPU/IO only; transfer duration unmeasured. Corrected smoke acceptance does not itself authorize production salvage. Never stop production monitor before all training/scoring workers exit and every weight/latent/crop/opaque-score output is durably verified.

## ASTRA_PLAN_REQUEST: conditional packaging, not duplicate planning

Existing ASTRA_COMPUTE_UNBLOCK_PLAN_20261114.md already supplies decision tree. After traceback collection, resume existing Astra owner only for actual unresolved branch. No new generic planner or speculative clipping repair.

If clipping still implicated/inconclusive: package existing probe as THREE fresh processes, python clip_grad_probe.py --foreach default / true / false, separate exit/stderr, continue after failed mode. No models/data/checkpoints. Missing today: wrapper source/hash, exact environment/wheel/driver pins, immutable namespace/command, independent prerun GO and root duplicate check. Thus NOT dispatch-ready.

Proposed existing envelope1H100,8CPU,120G,150Glocal,15min,FORCE_RM_TMPDIR; WCSS only. Interactive is srun --pty ONLY (not sbatch); root verifies current QoS/limits, real PTY and durable launcher/status logs, otherwise normal eligible partition. If false alone passes, register/review mathematical equivalence checks and real B gating smoke before any production. If all synthetic modes pass, prospectively instrument original first update. L requires own real memory/fit smoke. IDistill rerun is conditional on denied salvage and measured full-phase timing:3m11smoke does not prove<=6h production. No epoch truncation/resume/hardware substitution.

## Limits and handoff

Read mambamorph AGENTS/pointed CONTINUE/CLAUDE, live NOTEBOOK/AGENT_STATUS, delivery README/workstreams/policy/latestheartbeat/Astra plan and native registrations/review. smad-next/CLAUDE.md and manuscript_cvpr2027/CLAUDE.md absent. Bounded depth4 filename search and coordination metadata did not find local631949* collection; not proof none exists elsewhere. No manuscript edits, no new scientific conclusions. Release bounded owner slot after root handoff.
