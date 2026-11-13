# Pre-run check: contrast 2-prime (replacement storage test) and the amended freeze rule

Reviewer: experiment-reviewer (Opus), 13 Nov 2026, read-only. Report as returned, unedited.

**Verdict: GO WITH FIXES.** Fixes M1 to M3 must be in the registered text before any score exists. M4 is the author's decision.

**Non-exposure: I checked this myself from manifests and file lists. It holds.**
- **Hold-out manifest.** `/mnt/t7/smad_next/MS1/pack_tree/pn1/data/manifests/pn1_eval.csv` (sha256 d1fab6ad…) has 1,480 `ms1ffhq` rows. The counts per kind match the draft's table exactly.
- **Against the FS1 manifest** (`/mnt/t7/smad_next/PN1/fs_tree/pn1/data/manifests/pn1_eval.csv`, f0f29f22…, 19,797 rows):
  - 0 shared ids and 0 shared paths.
  - 0 shared persons, after splitting the morph host field on `|`.
  - 0 of the 1,480 hold-out image sha256 appear in the FS1 pack SHA256SUMS.
  - 0 person overlap with the TT1 rows.
- **Training sets.** `train_A`, `train_B` and `train_Sb` contain no "ffhq" string at all.
- **Platform-gate rows.** The `af0` (1,339) and `ffhq` (5,000) rows are identical in both manifests.
- **Hold-out scores.** They exist only inside the MS1 tars, and none is unpacked anywhere.
  - `tmp.6XNipEkzWN` holds staging files only (run.sh, task.env).
  - `ms1_read_mock.json` is a mock, and the MS1 `result.md` is 3 lines.
  - Limit: /mnt/t7 is mounted `noatime`, so file reads cannot be proven from the filesystem. "No reader opened them" rests on the logs and on these absences.
- **Design note.** 239 of the 300 genuine persons are also morph contributors, so the genuine and morph bootstraps are not independent. Disclose this.

**Blockers and majors**

**M1 (major): the test is close to certain to pass for Sb at fm61, so it has little evidential value there.**
- On FS1, Sb's flag rise divided by A's was 0.03 to 0.18, against a pass mark of 0.33. Its mean shift was −0.09 SD, against a mark of about 0.23.
- If FS1's stored copies were the trained size (the draft calls fm61 the trained size), fm61 just repeats a known result on new persons. I estimate P(pass) ≥ 0.95.
- For B (ratios about 0.12 to 0.37), I estimate P(pass) at about 0.6 to 0.8.
- The size no network was trained on (amsl112) is the only informative part.
- The relative mark alone lets a network whose flags double (5% to 10%) pass against a plain network rising 15 points.
- **Add** to section 2: "AND Δf(X_s, z) ≤ +0.05 (absolute) AND the upper 95% bootstrap bound of Δf(X_s, z) ≤ +0.08."
- **Add**: "Evidential weight is carried by amsl112; fm61 replicates FS1 on new persons."
- Keeping the mean-shift condition two-sided is right: it bounds Sb's reversed bulk shift.
- **Resolution.** With 290 pairs and about 15 to 60 discordant persons, the SE of Δf is about 1.3 points for Sb and about 2.7 points for A. The intervals are meaningful for A. For Sb they are about ±2.5 points, the same size as its whole effect.

**M2 (major): H-new-1 is underpowered, and the freeze rule rewards that.**
- With a native miss of about 30% and 20 to 40 changed morphs, the SE of the paired miss difference is about 3.7 points, larger than the 3-point margin.
- If the true effect is 0: P(falsified) is about 0.5, so "inconclusive" is likely.
- If the true effect is +3 points: P(supported) is about 0.3.
- The freeze needs only "not supported", so inconclusive lets the freeze through.
- **Replace** the decision by a paired logit read: "Δm_att(n, z) = mean over morphs of (stored − native logit) / SD(native genuine logits of n). **Supported** if Δm_att(Sb_s, z) ≤ −0.20 on ≥ 4 of 5 seeds at either size. **Falsified** if Δm_att(Sb_s, z) ≥ −0.10 on ≥ 4 of 5 seeds at both sizes. Misses and stored-vs-stored AUC are printed only."
- **Change** in the freeze rule (steps 1 and 2): "H-new-1 is not 'supported'" becomes "H-new-1 is 'falsified'".

**M3 (major): release safety and operations.**
- (a) `drive_c2p.sh pull` runs `rm -f "$L/HOLD"` even when n < 45. A failed scoring run caused by the machine would then be lost when the machine is released, which breaks the rule to re-run such failures unchanged.
  - **Replace** with: `[ "$n" -eq 45 ] || { log "partial: HOLD kept"; exit 0; }` before the `rm`.
- (b) The draft's "release logic change needed" is stale. It is already in place at `drive_ms1.sh:94,98` (commit bc5abe8), and 4 loop processes are running. Fix the text.
- (c) `remote_c2p.sh` does not pin rescore.py.
  - **Add**: `[ "$(sha256sum $B/held/pn1/src/rescore.py | cut -c1-64)" = 6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e ] || exit 1`
- (d) Cost and deadline.
  - Spend is about $5.56 of the $10 cap at $0.82/h, so the cap is reached around 12:20.
  - The lease deadline is about 13:10.
  - Queue end (about 09:50) plus 40 minutes of scoring fits, but HOLD must be touched before ALL_DONE_m1.

**M4 (major, author): the amended freeze rule is defensible only with full disclosure.**
- A hostile reviewer will say: "The gate failed, then a new gate was written with margins tuned to known effect sizes, and half of it repeats a known result."
- The answers:
  - The original test failed on its control, not on the method.
  - The new test is registered before any score on unseen persons and an unseen size.
  - Both results are reported.
  - H-new-1 falsification is required (M2).
- Paper wording: "Contrast 2 (registered) was uninformative because its positive control failed. A replacement test, registered after that failure with margins set knowing development effect sizes, was run on 300 unseen persons and an unseen storage size. At the decision rule, Sb's storage reaction was at most one third of the plain recipe's [and at most 5 points]." Never "removed" and never "shortcut-free".

**Minor: platform gate.**
- Using the L40S is acceptable: the gate is strict, and A100 replicates agreed within 0.044 logits.
- But `rescore.py` does not enable TF32, while `pn1_score.py:45-46` does. The gate therefore measures GPU model and precision together. Say so.
- Cutting the gate's max |Δlogit| from 0.15 to 0.10 costs nothing.

**Improvements**
1. M1 and M2 text: 0 GPU-hours, needs registration.
2. Print the stored-vs-stored AUC beside native-vs-native AUC: 0 GPU-hours.
3. Rehearse the partial-tar path (M3a) with a local mock run: 0 GPU-hours.

**Questions for the authors**
- Did FS1's stored copies (HN2 history-matched) use the fm61 size? If so, fm61 is a replication, not a test.
- Will you require H-new-1 to be "falsified" (M2) rather than "not supported"?

Files:
- `/home/narolski/smad-next/experiments/PN1_protocol-network-first-tests/prereg_contrast2prime_draft.md`
- `/home/narolski/smad-next/src/MS1/c2p/drive_c2p.sh`
- `/home/narolski/smad-next/src/MS1/c2p/remote_c2p.sh`
- `/home/narolski/smad-next/src/MS1/rented/drive_ms1.sh`
- `/mnt/t7/smad_next/vast/ms1m1b/lease.json`
