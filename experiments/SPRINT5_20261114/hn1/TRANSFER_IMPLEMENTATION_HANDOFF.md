# HN qualified transfer implementation handoff

Independent root review is required because this agent authored the control and runner. No training or detector payload access has occurred in this implementation task.

The full 124-control construction passed under root release. Packaging verifies every source image hash and creates 372 PNG assets: 124 positives shared by both arms, 124 matched-target negatives and 124 self-target negatives. Each arm has 248 unique native images, 124 per class, with 44 FERET and 204 FRGC rows. No new resizing code is introduced. The original model's 224 loader is shared.

The metadata audit independently checks all H/B contributors, source image paths/bytes and landmark paths/bytes against the fixed 100-host S4/S3 development population. It finds 143 training people versus 200 development contributors, with no identity, path or byte-hash intersections. The checkpoint's historical exposure remains inherited; this audit covers the new continuation inputs.

The runner imports the unchanged FS1 training loss, loader and optimizer. Its source patch asserts the pinned original trainer, 248 unique rows, 124 positives, empty val10, full batch 248, prior shuffle, recipe v1 and 2/100 updates. It loads exactly the trainable-parameter key set from admitted AB1 Sb408 before fresh AdamW initialization. Paired seeds 531–535 use the same single initialization. Full batches give exactly 100 appearances per image over 100 updates, or 24,800 forward images per fit. This is conditional continuation variability, not five independent pretrained initializations.

`run.sh` and `worker.sh` independently require a root-authored release tied to the actual source manifest hash. The overlay verifier checks its archive hash and all 375 safe, unique file members. Original FS1 and AB1 inventories are rechecked after extraction. The pre-existing strict battery is unchanged, including the full 21,277-row own-score expectation and byte-identical platform reference gates. Failures archive logs and partial checkpoints. Existing successful outputs fail closed instead of being reused.

Validation performed: exact FS1 patch application and Python compile; shell syntax; full image-byte packaging; safe overlay member verification; independent identity/input audit. GPU memory, model execution and byte gates still require the prescribed two-arm two-step H100 smoke. No runtime is claimed from CPU packaging timings.

Deployment layout: `packs/SPRINT5_2_v1/source/`, `packs/SPRINT5_2_v1/hn_native_overlay.tar`, and root-completed `SMOKE_RELEASE.json`. Run `bash source/worker.sh smoke` inside the authorized H100 allocation. Production uses array indices 0–9, paired seeds 531–535, only after both smoke archives and their exact hashes are admitted in `PILOT_RELEASE.json`.

The claim is strictly geometry-matching transfer to existing S4/S3. HN's measured nuisance floor remains max AUC 0.7433476, conditional CI [0.7125105, 0.7959151]. There is no independent HN heldout-construction claim, identity-specificity claim, NEXT adoption or candidate read authorization. The reader requires separate independent pre-read review.
