# Independent conditional full MADation B recovery proposal review — 2026-11-14

Reviewer: astra_sprint_plan_review; proposal author: astra_compute_unblock_plan. Source/preregistration and already admitted technical reports only. No model imports, images, weights, archive members, raw training logs, scientific outputs, GPU, scheduler or execution.

## Verdict

GO_SOURCE_PREPARATION_FOR_NEW_FULL_B_MATH_PRODUCER.
HOLD_UNQUALIFIED_AMENDMENT_ADOPTION_AND_FULL_FIT_RELEASE pending the two corrections below and concrete release pins. This is permission for source preparation and generated CPU fixtures only, not a full-fit release, scoring admission or scientific result.

The math-only patch is mechanically faithful: independently reconstructed exact unified diff, prospective trainer hash and inverse AST equality all PASS. All 19 package/source pins match. Existing failure history, reduced-list smoke and original trainer remain untouched.

## Required corrections

1. Original prereg Amendment 3 fixes the stage completion cutoff at 14 November 18:00 CET; Amendment 4 explicitly preserves Amendments 1–3. The proposal says late-addition rules remain unchanged but does not resolve this elapsed cutoff. Prospectively identify the new work as a late backend-recovery cohort with an explicit completion window/resource termination rule and reporting status. Preserve the original deadline ledger as incomplete; do not retrospectively turn late fits into on-time original results. Do not present five late fits as completion under the unchanged original cutoff. Root may bind this correction in a separate prospective adoption before execution; frozen proposal history must remain.
2. Replace “BGR-to-RGB source path” with the exact actual FaceDataset behavior: cv2.imread returns the BGR array, which is passed directly to ToPILImage and the original transforms without an explicit channel conversion. Preserve this behavior in code; this is a prose correction, not authorization to repair preprocessing.

## Source and recipe checks

Original trainer e905cc241327d0a6f809ef3188ac395353ee4e502e3d91409892f89890b5f55d; prospective trainer 355a3223152882669ad2e5f39fede88578d43ddd720b5aadec1c379ec219f976. Exactly one explicit math SDPA context encloses encode_image, normalized-feature header/loss and backward. Clipping, both original AdamW steps, zero_grad positions, schedulers, logging and callbacks remain outside this change and AST-identical.

Configuration defaults num_epoch=40, save_every=40, log_every=50 agree with proposed explicit flags. Original CLI overrides LoRA alpha4/dropout0.4 and model/header LR 1e-5/1e-4. Preserve two-logit one-hot BCEWithLogitsLoss, FP32, r2 q/v LoRA, norm clipping5, AdamW weight decay0.05 and original betas/eps. Trainer passes starting optimizer LR as scheduler eta_min: preserve the resulting constant-LR behavior, not merely the config default eta_min. Preserve epoch39 empty-test eval/train transitions and merge/unmerge effects, followed by original final save callback.

39723 rows, batch256, drop_last imply155 batches,43 omitted rows per shuffled epoch,6200 updates per optimizer and1,587,200 exposures per seed; five fixed seeds401–405 imply7,936,000 exposures. These are source-contract counts, not observed completed full training. No smoke warmstart, reduced3311 list, best checkpoint, resume or outcome-based stopping. Last40_backbone/40_header only; released reference weights remain comparator-only and all recovered fits must be labelled our retrains.

## Actual technical evidence and limits

The separately authored/admitted 36-update postreview SHA5e5ad6395a531f427c5d046388f6f1cf2b54578ec8b519bdfa2395422f2f1267 supports 36 real updates, original callbacks and checkpoint reload/byte gate on the reduced training smoke. It reports35.379740632 seconds for its instrumented interval,34.693GiB peak and104 seconds native allocation duration. It does not establish full39723-row IO cost, steady-state throughput,6200-update stability, full-training completion or backend equivalence. Root adoption of that exact technical result is still a release prerequisite. Proposal UNKNOWN/RUNNING wording is a historical author snapshot, not the current evidence verdict.

## Concrete producer contract and remaining release requirements

Proceed with a NEW producer namespace, immutable source package and OTHER independent source/launcher review. Generated fixtures must exercise40×155 updates:12400 optimizer steps,12400 zero_grad calls,80 scheduler steps and40 save-callback invocations with only the last pair emitted. Cover empty-test mode transitions, exact seeds401–405, no model forwards added by observers, finite gradients with legitimate individual zero LoRA-A allowed, progress/end-count checks, malformed source/input hashes, no evaluation data, reentry and TERM/KILL/partial-collection retention. Full-run instrumentation must not retain unbounded per-step tensor copies or silently alter RNG.

Before an actual full-fit release: bind exact canonical full CSV bytes/order/hash and runtime prefix-only rewrite; initialization/crop/code/wheel provenance; actual runtime and clean owned source commit; five-seed roster and create-only once/output namespaces; explicit late-recovery ruling; remaining budget ledger and H100 accounting convention; exact new resource/release/launcher review and measured timing estimate with uncertainty. Current full CSV hash and remaining allowance are UNKNOWN, not substitutes for reduced-list or nominal300 A100-hour values.

The6h actual PTY envelope is a new resource amendment from the old12h worker, not an inherited right. One H100/8CPU/120G/150Glocal per run, five at most30 allocation-hours, must fit current allowance and site limits. Child21000s plus10s TERM and300s collection leaves290s within21600s only if tied to reconciled native allocation start; setup time must not reset the clock. Preserve early nativeID, durable live logs/receipts, snapshots, complete failures, no automatic retry and no fallback platform. Missing completion remains incomplete; do not shorten epochs or chain resumed jobs to satisfy the envelope.

Exact source-only converter acquisition/pinning is required before conversion implementation/use; it need not block authoring the training-only producer, which must not invoke conversion/scoring. Original converter tolerance, own-final strict reload/byte gate, direct-vs-wrapper full noTTA byte scope and separate reference/scientific admission remain independent future gates. No historical print-differences/retry script can become an asserted byte PASS. L and F remain outside this B execution scope; L requires its own registered distributed gate and missing initialization/runtime pins.

## Pins

- PACKAGE_SHA256SUMS: debb0d12b58a657202b1ed9148abd8153751b70595e4604a9605f1a8c93afd25
- Amendment:186466f39d5803811840bf015bcf3350cf287a39c58cb99dced3a8e0f59e65bb
- Source matrix:31cabce835b87f23a8204ee4ab4a9ed4980013072fcef8891e47dd63369b109d
- Math-only patch:7980caa9105473fd96cccfac21c872c1e3970f3c93170575e0ac5cf7003a499b
- Independent checks JSON:5c46fd1f9ff6e5808bfb5d3c3f7398ddbe4e7e9d5138912dd7af30a4dcabfbb4

No author files or canonical registration changed. No full-fit/score/read release issued.
