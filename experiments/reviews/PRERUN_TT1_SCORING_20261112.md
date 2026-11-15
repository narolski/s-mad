# Pre-run review: TT1 scoring plan (unseen genuine sources)

Reviewer: experiment-reviewer (Opus), 12 Nov 2026, read-only. Report as returned, unedited.

**Verdict: GO WITH FIXES.** I found no blocker for the decisions as written. Seven majors need text or code changes before registration. The WCSS H100 platform section has not been written yet: `git status` shows the draft unchanged at f4fe159, and §4 still covers only the DGX and the rented A100.

**Checked and correct.** The sha256s of both manifests, strata_edges.json and src/TT1/*.py match what the draft and README say. U_p recomputed from aligned_manifest.csv gives 21,035 rows, with the same per-source counts and the same 54 band exclusions. All 25,241 raw/aligned paths lie under /mnt/t7/smad_next/TT1. aligned=0 rows are not in the primary pool.

## Majors

**M1. The TT-H1 decision uses the wrong unit.** "Lower Clopper-Pearson bound > 5%" counts images. OULU-NPU has 989 frames from 55 people, so that bound is far too narrow and pushes towards "fails".
- Fix (§6 TT-H1): "The decision uses the person- or pseudo-identity-bootstrap bound. The Clopper-Pearson bound is printed only."
- Add the anchor: "R_cam own-rule share is printed. TT-H1 is uninformative for a network whose R_cam share exceeds 5%."

**M2. The pseudo-identity bootstrap is too narrow, and the draft only labels it.** Components outnumber true people: CFP 1,586 vs 500, AgeDB 2,338 vs 568, and LFW/CALFW share people across separate components.
- Fix (§2 Persons): "Pack half-widths are multiplied by sqrt(components / true people): CFP 1.78, AgeDB 2.03, lfw_calfw sqrt(7,957/5,749) = 1.18. This applies to every pack interval that enters a rule (TT-H1, TT-H4, TT-H5, TT-H6)."
- Optional extra: merge components by buffalo_l embedding (no image operation) at a cosine cut fixed now.

**M3. The border control misses a read and is described too strongly.**
- R3(d) tests the border only on FFHQ. Add "(e) R_cam^border(f) against R_cam, per family". It costs nothing.
- Edge mismatch: in the U frames the edge where the black border meets the photo is softened by prep_eval's warp, while blanking makes a hard step. The mask rule (max channel = 0) also catches dark pixels inside the face. Add: "The mask is the largest exactly-zero region connected to the frame edge."
- Add to §0: "The border reference matches border geometry only. It does not match enlargement, resolution, compression or source."

**M4. Say which contrasts identify what.** Add to §0 or §5:
- U vs R_cam: everything together (source, enlargement, JPEG, sharpness, border).
- R_cam^border vs R_cam, and R_ffhq^border vs R_ffhq: border alone.
- U vs R_cam^border: source plus enlargement plus JPEG plus sharpness. The border is roughly removed; enlargement is not.
- Within-pack ρ and quintiles: sharpness at fixed size, as correlation only.
- No current contrast identifies "source beyond storage and border". The control that would: crop R_cam photos to the 112/224 crop geometry with integer slicing, shrink them with an already-approved storage-history path, then run prep_eval.align unchanged. That separates border, enlargement and source within each geometry group.
  - This needs an amendment and the lead's or author's confirmation that an approved shrink path exists (OWNER_BRIEF lists only h1_build, the morphers, blanking and E7 outputs).
  - If it is not built, state: "TT-H5 'source matters' can mean enlargement/storage; identified only within each geometry group."

**M5. TT-H5 cannot separate enlargement from family.**
- Enlargement takes two values: all anti-spoofing families sit at about 1.7x, all packs at about 3.5x.
- Greyscale is essentially packs only; AgeDB's 27.5% is extrapolated when AgeDB is held out.
- In R4(d), with family indicators, enlargement is identified only by the within-family p10-p90 spread (1.65-1.81), which is mostly IED detection noise.
- Fix: "The enlargement coefficient in R4(d) is printed, labelled 'identified by within-family detection noise', and is not interpreted."

**M6. Saturated scale.** The bounded head puts R_cam on the floor at about -3.87. The DGX tolerance of 0.02 logits is comparable to the 0.03-0.10 band that holds τ_cam.
- Meaningful reads: the own-rule flag share; AUC and the share above R_cam's median, computed with mid-ranks.
- Not meaningful: anything at τ_cam (already labelled); u-units when u < 1; ρ for arms whose genuine scores sit mostly on the floor.
- Fix: "Print each pool's share within 0.05 of the network's floor. An AUC read whose two pools both exceed 50% at the floor is labelled 'floor-tied'. AUC uses mid-rank ties."

**M7. TT-H6 must not become selection.**
- Seed equals machine (pn1a = 401, pn1b = 402). Sb and Bv used pack 2, A and B pack 1.
- The paired bootstrap captures image sampling only, not training variance.
- Fix:
  - Replace "Lowest and most uniform arm is named" with "Descriptive on seeds 401/402 (two machines). No arm, seed or threshold is chosen from TT1. FS1's frozen contrasts and the MS1 arm choice are not revisited."
  - Disclose the pack difference in §1.

## Platform and operations (needed before the H100 run)

- **H100 gate.** Bit-identity with the A100 scores is unlikely on H100 with torch 2.11. Use G-DGX tolerances for all 12 networks: gate rows scored first in the same job, `gate.json` written, exit non-zero on failure, and add Kendall ≥ 0.99 on R_cam (AD4 had a gate that failed on rank agreement).
- **Pack.** One tar, unpacked into $TMPDIR, `--extra=FORCE_RM_TMPDIR`, one result tar back. Do not put 33,577 PNGs on Lustre.
- **Reusable pack for FS1.** Split it into an image+list+code tar (sha pinned now) and one network tar per block.
- **No placeholders.** Submit only after the pack and reader sha256s are committed and an 8-row test has run on WCSS. No generic slot jobs.
- **Exact numbers.** The registration must state the exact row count, not "about 33,577".
- **Keep rule.** Hold a second local copy before release.

## Minors

- 23,832 frames come from `/mnt/t7/Datasety/downloads/CASIA-Webface/*.bin`. They are LFW, CALFW, CFP and AgeDB, not CASIA-WebFace images.
  - Still, celebrity identities may overlap CASIA-WebFace, which supplies the H1 source identities (10_ASSET_INVENTORY.md:116).
  - Add the path and the overlap statement to §0, and have the build_list assert that the train.rec/cfp_fp/cplfw files are never read.
- R_ffhq (HN2) must be disjoint from MS1's FFHQ training images before TT1 scores any MS1 network.
- MSU-MFSD (65 images, 35 people) gets the same weight as lfw_calfw in F̄. Print F̄ without MSU as a sensitivity read.

## What the paper can say

Own-rule false-alarm rates on unseen low-resolution genuine frames (1.7x and 3.5x enlargement, with a black border), on development sources only. It cannot claim a miss rate, a high-resolution result, a benchmark or generalisation statement, or a cause of any source effect.

## Questions for the author

1. Is there an approved shrink path that M4's control could use tonight?
2. Do LFW, CALFW, CFP and AgeDB fall outside the "CASIA-WebFace" closure?

Main file: /home/narolski/smad-next/experiments/TT1_threshold-transfer-unseen-genuine/prereg_scoring_draft.md
