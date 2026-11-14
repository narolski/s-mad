# Independent environment/source probe v1r1 delta review — 2026-11-14

OTHER reviewer astra_sprint_plan_review; author Sol. Source and generated fixtures only. No actual probe main, target environment collection, package/model import, weights, images, archive/NPZ, GPU, cluster or scientific read.

GO_SBMR512_ENV_SOURCE_PROBE_V1R1_SOURCE_IMPLEMENTATION

Exact probe34c5f9d691714835ea164e5ae87eaf11ceaf5b166a7ce7e37cf1bd7d2402f4de; manifest92ac9a56b7cc8e976e7e69bc961114c80b3163e4f68622dd105e9d812a370ad0. This permits root source adoption/preparation, not execution. Actual allowlist/interpreter/install/source identities, reviewed resource/durable wrapper and exact future metadata release remain missing. Scientific/reconstruction/timing/GPU access remains HOLD.

## Resolved blockers

B1 from independent v1 review346625311eb0489534f1970373540ed7b9dd5ef0577ba6e2b721d8f6ebfd41c8 is resolved: no importlib.metadata/Distribution.at or metadata fallback remains. METADATA is read once as bounded authenticated bytes and parsed with stdlib email; Name/Version must each be present once, nonempty and syntactically restricted. The generated old empty-METADATA/unpinned-PKG-INFO canary now rejects without opening PKG-INFO. Mutation of the path after snapshot does not change reported version/hash.

B2 is resolved for the reviewed exact-file scope: traversal starts at root directory fd, each ancestor opens with O_DIRECTORY/O_NOFOLLOW and each leaf with O_NOFOLLOW/O_NONBLOCK. Only fstat-regular descriptors proceed; exact expected size and cap precede reading; approved size plus at most one byte detects growth; before/after descriptor fingerprint and exact expected hash must match. Hash/parse use the same bytes, not a pathname reopened after validation. Generated ancestor/leaf swaps reject before target reads; replacement after opening cannot redirect descriptor reads; same-inode mutation/growth/oversize/FIFO/dangling-symlink cases reject. Request/release JSON parsing and their recorded hashes likewise share captured bounded snapshots. Output directory/files use descriptor-relative exclusive creation and fsync.

This is bounded descriptor/content authentication, not protection against an adversary controlling the interpreter or kernel. Interpreter/stdlib and immutable staged probe startup remain root provenance prerequisites. Normal installation symlinks are intentionally rejected: root must bind canonical real source/library/interpreter paths rather than weaken no-follow behavior. Missing ordinary entries are UNKNOWN, never an inferred match.

## Independent verification

All source/evidence entries of new and held old manifests match; old v1 manifest8b68d7f2cac7bc700d05c7362fb1750390529d642bb3e3087be1810454042813 preserved. All19 generated fixtures independently PASS in0.031s under /usr/bin/python3 -I -S -B <newpacket>/test_probe.py, including direct actual helper-method reproduction of both previous blockers, captured control-byte mutation and authorization scope guards. This imports only reviewed standard-library probe helpers and operates on generated temporary files; actual main is never invoked.

Checks file INDEPENDENT_DELTA_CHECKS_20261114.json SHA3c92f3f08793fb53ee34a9f91636bf4eb3505236ee96854f58fff2c174305980. No author source changed.

## Minimal next bindings, unchanged from prior review

Root must provide a new exact valid request (unsigned UNKNOWN placeholders are not authority):
1. Canonical selected interpreter identity/hash plus independently admitted stdlib/startup provenance; isolated/no-site/unoptimized flags. Explicit target install metadata roots account for -S venv/sysconfig limitations.
2. Exact required installed METADATA/RECORD paths, sizes and hashes for packages on the pinned common/archs/timm/preprocessing import chain; applicable torch/torchvision/timm/numpy/Pillow/OpenCV/HF dependencies only. Missing metadata remains UNKNOWN.
3. Exact required installed source/native-library filenames/sizes/hashes; existing common/archs/RZ source pins reused. No broad crawl/HF cache/weight discovery. If paths/pins are not in admitted receipts, separately authorize narrow technical source/install metadata acquisition before constructing the request.
4. Corrected probe+review+request+release hashes and a reviewed sanitized CPU wrapper with fixed create-only durable output, timeout/termination/terminal receipt and enforced memory ceiling. Parent of output must already exist as canonical directories. No actual scheduler job required.

The future command shape remains env -i ... <pinned canonical interpreter> -I -S -B <exact probe.py> --request <root frozen request> --release <root metadata release>, under the separately reviewed120s+10s bounded wrapper. There is no expanded ROOT-approved runnable command until the missing concrete identities/receipts exist. Do not fabricate those values or use this source verdict as live permission.

Current installed bytes do not prove historical executed identity. Preserve historical/runtime-default/schema/pretrained/image UNKNOWN fields. No hidden-cache equivalence theorem is demanded for the later prospective first-batch native-bytegate experiment. That future timing requires separate reconstruction/input/backend/worker/root gates; a pass does not admit full TT1/14panels or alter NEXT once/scientific policy.

No execution release issued; stop at this source handoff.
