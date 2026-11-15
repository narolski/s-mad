# Author approval of selection rule version 3

Recorded in Codex at 2026-11-14T10:16:24.259447+01:00.

The author wrote in the current conversation:

> I approve the /home/narolski/smad-next/experiments/NEXT_method-selection-rule/prereg_draft_v3.md. What else do we need to do now?

Approved file: `experiments/NEXT_method-selection-rule/prereg_draft_v3.md`.
Approved draft SHA256: `e1b7a4cede954ce347f00ec7f0f5420afbfbefe9a7692ff6002b0ce82f09493e`.
Repository HEAD before binding: `c1f1efa9a91c5a75e038d76cc56f789b0a6dce51`. The working draft was byte-identical to that committed file.

This commit changes only the heading and status paragraph of the rule. Every criterion, margin, challenger order, deadline, disclosure and safeguard stays byte-for-byte unchanged from **Fixed now** onward. The binding commit is the commit introducing this approval record and removing the draft designation from the rule's heading.

The approval satisfies the request for written approval of the rule (section 12 question 1). It does not assert that input pins, floors, fit gates or reviews have passed; it does not authorise opening challenger archives before those requirements are met. The section 12 questions about a supplementary rescoring job and the interior-crop ruling are not answered separately by this record. Availability of 512 px sealed frames must be established from manifests without opening scores.

Before selection: resolve provenance and pins from a clean tree, establish which arms remain eligible under section 7, verify all input/floor hashes, and apply the rule once on development data only. Selection must be followed by confirmation on fresh seeds 413–417 before the next freeze and sealed read. Existing collected archives remain closed during this administrative binding step.
