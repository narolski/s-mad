# Root acceptance of reviewed reader code — 2026-11-14

Decision: ACCEPT_CODE_ONLY; WAIT_FOR_ALL15_COMPLETED_ARCHIVES. This is not a collector or scientific-read release.

Root inspected collect_metadata.py, admit.py, journal.py and README against the independent Astra review0df7d276011001cd43ab04386f77f6cd677fa67e4e9823c016df7d14766ee8be; all source checksums verified for manifest02c7401529a8ca8b2a7af220f7ef36f8cbd8a71ffc50052b0a52f6e2606d1b6c. Astra independently ran23 generated-fixture tests and source/input checks. Root earlier inspected read.py/statistical rules and requested fatal nonfinite-guard diagnostics, now implemented and reviewed.

The collector requires all15 distinct registered archives and opaque digests before metadata parsing. It admits only fixed JSON/TXT/LOG members, inspects score/checkpoint headers without deserializing them, and writes create-only receipts. Exact6250steps,224resolution,256batch,1.6M exposures, source/manifest/software pins, original15schedule plans and strict byte gates are checked. Scientific admission validates the committed pre-fit binding, exact collector receipts and source/roster hashes before the permanent create-only read claim. No archive roster or payload was accessed in this root review.

Current dependency: production array6321090 pending per latest coordinator report. No actual complete15archive roster exists in the evidence available to root. Therefore no GO_METADATA_COLLECTION_ONLY or GO_READER_READ is issued and no collector, reader, journal or output is invoked/created.

Next lead action after scheduler completion: establish all15 expected production archives and matching durable opaque digests; bind an immutable archive roster and root GO_METADATA_COLLECTION_ONLY to this exact reviewed source. Execute collector once in a fresh output directory, inspect all metadata failures without reading scores, then independently verify the15 eligibility receipts. Only then bind a separate GO_READER_READ to the exact final roster and review. Any missing/failed fit keeps the full reader closed; no partial-seed fallback or adoption claim. All52 sparse genuine guard cells stay INCONCLUSIVE under the bound policy.
