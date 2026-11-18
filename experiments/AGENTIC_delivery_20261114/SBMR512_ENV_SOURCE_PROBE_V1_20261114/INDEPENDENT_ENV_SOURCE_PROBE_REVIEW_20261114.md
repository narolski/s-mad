# Independent environment/source probe v1 review — 2026-11-14

OTHER reviewer astra_sprint_plan_review. Source and generated fixtures only. No actual environment probe, WCSS, GPU, model imports, installed target package collection, archive/member/weight/image/NPZ/score access.

HOLD_SBMR512_ENV_SOURCE_PROBE_V1_IMPLEMENTATION

13 provided CPU fixtures independently pass, but two additional generated fixtures reproduce violations of the intended exact-file read boundary. Preserve this frozen version; author a separately pinned revision and delta-review it before any root metadata execution release.

## Blocking findings

B1 — Distribution.at is not an exact pinned-METADATA-only parser. A generated torch.dist-info directory with empty, correctly pinned METADATA and RECORD plus an UNPINNED PKG-INFO containing Name: torch / Version: UNPINNED_FALLBACK_CANARY produced CONTENT_HASHED with that unpinned version. Standard-library metadata parsing falls back to PKG-INFO when METADATA is empty. Repeated dist.metadata/dist.version calls also reopen files after their hash checks. The receipt therefore can report content not authenticated by metadata_sha256 and can access a file absent from the allowlist.

Fix: read bounded METADATA once into authenticated bytes; verify hash/size and parse those SAME bytes directly using a standard-library email parser. Require exactly valid Name and Version fields and reject missing/duplicate/empty malformed values. No Distribution.at, package discovery or PKG-INFO fallback. RECORD should be hashed once without parsing referenced paths. Add fixtures with empty METADATA and forbidden fallback-file canary, metadata mutation after snapshot, duplicate/missing names/versions and version/hash consistency.

B2 — File confinement checks precede separate path opens and do not hold against a mutable environment. A generated fixture swapped allowed.py to a symlink immediately after regular() returned. collect then stat/sha opened generated not_allowlisted.py before eventually rejecting its hash. A post-read hash failure does not undo an out-of-scope read. The present byte cap also trusts the pre-read stat; a growing file can exceed its approved size because sha reads until EOF without a cap.

Fix: descriptor-bound reads. Open each allowed path through trusted directory descriptors with no-follow constraints on every component (Linux dir_fd/O_DIRECTORY/O_NOFOLLOW or equally reviewed confinement); fstat regular type and exact expected size, cap reads to approved bytes plus at most one byte to detect growth, hash the same descriptor, reject changes using fstat before/after. Never reopen the pathname to parse metadata or derive the recorded version. A file replacement must not change the object whose verified bytes are used. Add leaf/ancestor symlink swap, growth, type swap and metadata reopen fixtures. Record missing/dangling entries carefully: do not silently classify a detectable dangling symlink as a trustworthy absent regular file.

Also apply snapshot discipline to request/release parsing and hashing: current main reads JSON text and later hashes paths again. Parse/hash the same bounded control-document bytes so authorization cannot bind one version while collecting another. For installed metadata/source, before/after stat checks are necessary mutation detection, not a theorem against arbitrary malicious same-inode writes; exact byte hash and unchanged authenticated snapshot remain the admission basis.

## What passes

Manifest8b68d7f2cac7bc700d05c7362fb1750390529d642bb3e3087be1810454042813 and all its entries verify; probe f0051c1c4f817c1d9c103d2397f188f0cdf1a3e04ed2e60bacfeed8fd0bb16d4. Direct safe test command /usr/bin/python3 -I -S -B <packet>/test_probe.py passes13/13 in0.007s. Reviewer first tried -m unittest under -I, which failed module discovery before importing tests/probe; corrected direct-script invocation succeeded. No collection/main was executed.

Imports are standard-library only; -I -S startup validation avoids site .pth/sitecustomize hooks and optimized assertions are not relied on (require raises ValueError). Source/metadata-only roles, explicit filenames, limits, no directory crawl, fixed output, create-only claim before installed-file collection, fsynced receipts and typed failure are appropriate. Current-versus-historical identity and -S venv-prefix caveats are preserved. Hardkill can leave an incomplete claim; no retry is implied. Durable process status/timeout/memory wrapper remains a separately reviewed prerequisite.

## Minimal remaining actual input binding

After the corrected probe is independently reviewed, root needs only the following concrete metadata/source bindings, not an impossible hidden-cache equivalence proof:

- Exact selected interpreter binary path/resolved identity/hash and stdlib provenance, with isolated/no-site flags; explicit target installation roots rather than inferring historical venv identity from -S sys.prefix.
- Exact installed METADATA/RECORD paths, sizes/hashes for the packages actually needed by pinned common/archs/timm preprocessing/import chain (torch, torchvision, timm, numpy, Pillow, OpenCV and applicable HF dependencies); unavailable versions remain UNKNOWN.
- Exact installed source/native-library files and their content pins: common/archs/RZ wrapper source already pinned by Bii authority; timm factory/ViT positional resize/attention and preprocessing dependencies actually used; no HF cache/weight scan or broad installed-tree crawl.
- A separately bounded root permission for obtaining missing source/install metadata paths/pins, if existing admitted receipts do not supply them. An unsigned UNKNOWN-filled request is not executable authorization. Do not invent hashes merely to satisfy the schema.
- Fixed corrected probe/review/request/release hashes and reviewed sanitized CPU process wrapper (120s plus10s TERM proposal, enforced memory limit, create-only durable terminal receipt).

Existing Bii source/typed checkpoint descriptors establish source and opaque overlay identity only. This metadata probe can freeze the prospective current reconstruction environment; it cannot attest historical executed package bits, backend defaults, image/pretrained bytes or decoded checkpoint schema. Those retain UNKNOWN and need their distinct bounded admissions. A future empirical first-eval-batch native-bytegate can be justified without all-state/cache equivalence; PASS cannot admit TT1/full14panel. No NEXT statistical/once/scientific gate changes.

## Evidence

INDEPENDENT_REVIEW_CHECKS_20261114.json SHAfa641159f12a275f18175212f73394493c943f398c96048306660b6454563ab1 records pins, independent tests and exact generated-only outcomes. Parent/root and source author were promptly notified of both blockers. No author code changed; no live probe or release was issued.
