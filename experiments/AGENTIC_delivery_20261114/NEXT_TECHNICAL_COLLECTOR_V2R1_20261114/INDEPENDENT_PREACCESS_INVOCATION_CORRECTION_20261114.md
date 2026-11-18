# Independent pre-access invocation adjudication — 2026-11-14

GO_PREACCESS_INVOCATION_CORRECTION_SAME_OUTPUT

Reviewer Astra / astra_sprint_plan_review. Approval is limited to root issuing ONE corrected invocation of the already released exact technical collector, with the same release, packet, code and fixed output. This is not an automatic retry or alternative output/once journal. No scientific read is authorized.

## Evidence

Failure directory /mnt/t7/smad_next/coordination_20261114/next_technical_v2r1_execution_20261114T195258Z preserved. Independently hashed driver.py d8a44b0f1a558eeee9f28274ce8faf3f9b06645d9b8448a591deac46365208dd; STDERR.txt c3047c51c147c0b49dd9e1b1ad7eb20cb72b8a48383f47347fba60b9b1737c6e; empty STDOUT.txt e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855; EXECUTION.json7e760c4ec2815ffc59d471b12c0d6ed59d355349dca11b024643ae4b1876e17e.

Actual exit1 is ModuleNotFoundError for native_metadata_predicates_v2 at collector module line15. The driver added python3 -I, unlike reviewed README; isolated mode omits script-directory import resolution. Source AST confirms only standard-library imports execute before that failed local import. Definitions of collect_archive(line205) and main(line249), and main invocation(line285), have not been reached. Thus this attempt did not execute release checking, actual archive/header/member access, metadata collection, output creation or any claim. This conclusion is from the exact source control flow and traceback, not merely absence of stdout. Fixed output was independently observed ABSENT.

Exact collector39d2f3899f53665d88fcfb386be3716928d6c53fb7d47f5e73e45bbafcc39564 and predicates2c270fe119b8c558d4ef7b112088423e53716e68e9ce1f1cb8352a055fac5e5d independently matched both working bytes and committed Git objects at03da23bd4166247fa92f23c3d59a34d4bae8c376. Release hash independently verified f048a30ee3eedb2eef0e5c42ce0f296d4210366ee10307ece98293f29b3852d0; packet remains8bafbc49c9a6ed0c832bce17cd75358a055eb48738ec15faeebca6e0d8e9c0b9. Implementation reviewef2928b8f17f44eafd34965d10d7ab2bb4a88da0c69034dc1814bd4aa476f2f3 remains applicable. No source correction is needed.

## Exact authorized correction for root

Remove ONLY the erroneous -I argument from the child argv, restoring README invocation:

```sh
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 timeout 900s python3 /home/narolski/smad-next/src/NEXT/technical_metadata_v2r1/technical_collector_v2.py --packet /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/NEXT_TECHNICAL_COLLECTOR_V2R1_20261114/TYPED_SCOPE.json --release /mnt/t7/smad_next/NEXT/technical_metadata_v2r1_ROOT_RELEASE.json --output /mnt/t7/smad_next/NEXT/technical_metadata_v2r1_collection_20261114
```

Keep root driver environment identical to the failed invocation apart from no -I in argv; do not add module-path injection or alter source. Use a new create-only DRIVER-LOG namespace with reference to the preserved failure and this review. Keep the SAME exact release and SAME fixed technical output path. Recheck absence and source/release pins immediately before launch; if output appeared or pins changed, stop for review. Root must explicitly issue this bounded correction, since failed execution record correctly says retry forbidden. This report adjudicates the demonstrated pre-access invocation error, not a general exception to that prohibition. No source/model/resource/statistical changes or second failure retry is approved.

Corrected attempt still runs all released checks before archive access. Retain stdout/stderr/native exit and all failures, no overwrites. Any new failure, including an unknown point of access or partial output, requires independent adjudication; do not delete output or choose another path. Actual completed technical collection requires the previously mandated independent postreview and does not grant NEXT native/scientific eligibility.

Reviewer only read these execution/release records and source/Git metadata; did not run collector/main, import it, inspect real candidate archives/members, start a process for collection, or issue a release.
