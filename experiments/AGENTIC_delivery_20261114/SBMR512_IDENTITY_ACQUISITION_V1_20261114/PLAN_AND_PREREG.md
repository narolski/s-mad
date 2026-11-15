# SbMR512 first current-identity acquisition — source preparation, 2026-11-14

Author astra_sprint_plan_review. This package needs an OTHER independent source/prerun reviewer; author does not approve own code. SOURCE_PREPARED_ONLY; no actual WCSS/environment acquisition, interpreter execution, model/package import, weights/data/NPZ/archive or GPU access performed.

## Concrete path evidence and purpose

src/RZ1/wcss/rz1-512.sbatch line32 assigns PN1_PY=$HOME/dmenv/bin/python. Under the bound narolski account the requested prospective path is /home/narolski/dmenv/bin/python. src/RZ1/run_rz1.sh uses that PN1_PY and reconstructs code at $TASK_WORK/pn1/code from FS1 pack96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004. The old scratch path is ephemeral, not an extant source requirement. Common/archs source can reuse already admitted source-only extraction /mnt/t7/smad_next/coordination_20261114/next_training_source_only_20261114T192658Z/pn1/code/smadcvpr with existing b5d42a... / bedfeb... pins, subsequently staged unchanged for reconstruction. Do not search old scratch or reopen candidate packs to rediscover it.

SOURCE_PATH_EVIDENCE.json binds actual inspected dispatch/source scripts. Their $HOME/dmenv path is source evidence, not proof the current installation still exists or matches historical scorer. Existing typed torch2.11.0+cu128 fact remains separate from current installation observation.

This acquisition is deliberately the step BEFORE the hash-exact v1r1 environment probe. Root grants specific paths/file classes and bounded directory metadata enumeration WITHOUT requiring their as-yet-unknown content hashes. Acquisition computes those identities. Independent postreview/root adoption can then create the exact pinned environment-probe request, or adopt equivalent acquired fields without repeating identical reads when policy allows. No unknown identity is invented to satisfy a circular precondition.

## Exact acquisition scope

- Requested /home/narolski/dmenv/bin/python: read symlink target metadata up to8 leaf hops, never execute it. Resolved target must remain within the fixed venv or /usr/bin, /usr/local/bin, /opt. Canonical no-follow parent traversal applies; unexpected ancestor symlink/out-of-grant path means HOLD, no adaptive search. Hash regular resolved executable, at most128MiB.
- Exact /home/narolski/dmenv/pyvenv.cfg, at most64KiB. Emit only home/include-system-site-packages/version/version_info/executable values and full-file digest; command and arbitrary fields omitted.
- Nonrecursive directory-entry names only: /home/narolski/dmenv/lib (≤128 entries), at most4 python3.N directories and their exact site-packages (≤20000 processed entries each). Emit ONLY relevant package/dist-info names for fixed torch/torchvision/timm/numpy/Pillow/OpenCV/transformers/HF/safetensors/tokenizers allowlist. No unrelated entry names exported.
- Relevant uniquely named dist-info: only METADATA/RECORD,16MiB each, no RECORD-path traversal. METADATA fields parsed from same authenticated bounded snapshot via reviewed safeio; no fallback PKG-INFO/discovery/package import. Duplicate distributions fail instead of choosing one.
- Fixed21 explicit import-chain .py paths in acquire.py SOURCES,≤4MiB each, no recursive crawl/native-library enumeration. Missing fixed paths stay UNKNOWN. No .pth execution or file reads; no HF-cache/source-data/weights/images/logits/raw logs.
- Aggregate content read≤256MiB. Native libraries not covered by fixed source list remain UNKNOWN and may be bound in a separate narrow followup if actually required; do not infer all dependencies from this first identity receipt.

Actual target library/source identity remains UNKNOWN until separately authorized execution. lib64/Conda or unusual symlink layouts are intentionally not auto-discovered; a missing/unsupported layout is a bounded finding, not permission to broaden paths.

## Code, generated validation and authority separation

acquire.py uses only stdlib plus safeio.py, an exact copy of independently reviewed environment probe v1r1 source34c5f9d691714835ea164e5ae87eaf11ceaf5b166a7ce7e37cf1bd7d2402f4de. The helper is loaded from its exact sibling path under -I -S -B; wrapper/OTHER review must bind both source bytes before startup. Descriptor-relative O_NOFOLLOW snapshot/hash/read caps and same-byte email parsing preserve the resolved v1r1 boundaries. Source identity acquisition computes actual content hashes rather than pretending they were preknown.

11 generated CPU tests PASS0.006s: nonexecutable synthetic interpreter bytes/symlink chain, irrelevant directory/data canary omitted, source never imported, fallback rejection, source symlink refusal, ungranted/cyclic interpreter links, duplicate distribution, directory caps, missing-site UNKNOWN and package-name filters. Bash syntax of run_cpu.sh PASS. Tests never call actual main or touch dmenv. This is author validation; independent review still required.

Future source-only test:
python3 -I -S -B /home/narolski/smad-next/experiments/AGENTIC_delivery_20261114/SBMR512_IDENTITY_ACQUISITION_V1_20261114/test_generated.py

## Root grant and bounded CPU wrapper — NOT AUTHORIZED

ROOT_GRANT_TEMPLATE_NOT_AUTHORITY.json is intentionally invalid. OTHER reviewer must bind exact source/package; root separately authorizes the above fixed identity-acquisition scope, canonical bootstrap interpreter/hash and review hash. Bootstrap is an ALREADY trusted system interpreter used by the coordinator, not the unknown dmenv interpreter. Existing coordinator/system interpreter provenance or a separately allowed exact system-executable identity check supplies this one bootstrap pin; no need to execute the target to learn its identity.

run_cpu.sh is a runnable proposed wrapper, not an executed command: sanitized env, CUDA_VISIBLE_DEVICES empty, -I -S -B, one CPU process/thread settings, ulimit virtual memory512MiB, timeout120s/TERM grace10s, fixed create-only durable dispatch stdout/stderr/EXECUTION receipt. Root must verify canonical timeout/bash/bootstrap tool provenance, fixed parent directories and safe placement; no scheduler allocation/GPU is requested. Staging paths are source-only, no need to stage model/data. Hard kill/host loss may leave claim without terminal receipt; reconcile as incomplete, no automatic retry.

After independent review/root staging and exact grant only, argv shape is:
bash <STAGED_EXACT_PACKAGE>/run_cpu.sh <ROOT_PINNED_CANONICAL_BOOTSTRAP> <EXACT_ROOT_GRANT_JSON>

Fixed receipt directory:
/lustre/pd03/hpc-narolski-1790461090/smad-next/coordination_20261114/sbmr512_identity_acquisition_v1
Fixed dispatch:
/lustre/pd03/hpc-narolski-1790461090/smad-next/coordination_20261114/sbmr512_identity_acquisition_dispatch_v1

Exclusive CLAIM precedes identity/install reads, then RECEIPT and COMPLETE or typed FAILED. No actual directory was created here. Root external source manifest check must precede executing wrapper/helper. Scope/decision/review/source/bootstrap/fixedoutput/no-retry checks occur before claim and target reads.

## What the receipt can and cannot close

Receipt records requested/resolved interpreter and symlink chain, current file identity, relevant metadata directory locations/version/RECORD/METADATA/source hashes, selected pyvenv fields, byte count and explicit UNKNOWNs. It freezes a prospective reconstruction environment. It does not establish historical executed identity, CUDA/driver/backend defaults, checkpoint schema, pretrained bytes or image provenance. No hidden-cache theorem is needed; later first-batch empirical native-bytegate remains a separately released test and cannot license full TT1/panel. NEXT scientific once/kernel output gates unchanged.

Next concrete sequence: OTHER source review → root fixed acquisition scope/bootstrap/CPU release → one acquisition → independent generated-receipt postreview → exact current-input binding. No new planning role/daemon/worker/paper update, no model construction, no science read implied.
