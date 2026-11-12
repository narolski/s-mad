# DRAFT amendment 14 (not registered, nothing run): face-interior reads on one rented lease

v2 of this draft applies F1 to F6 of the pre-run review `experiments/reviews/PRERUN_PN1_A14_AND_SEEDS_V3_20261112.md`
(commit 3f2bd14).

**Status: HOLD.** Nothing is scored on FFHQ landmark_combined, and no floor statistic is computed on it, until the
author answers whether any ffhqm family is reserved as an endpoint
(`/mnt/t7/smad_heldout/ffhq_morphs/REGISTRATION_DRAFT.md` lines 46–47).

After his answer, the registration commits one of the two texts below into prereg.md:
- Text 14 (full) if he says yes;
- Text 14R (reduced, without landmark_combined) if he says no.

The fresh-seed contrasts are frozen before any amendment-14 tar is pulled (`prereg_fresh_seeds_v3_frozen.md`).

## Procedure after the author's answer

1. Paste the chosen text into prereg.md. Update the README ledger. Commit and push. That commit is the registration time.
2. Full only, before the lease is started:
   - run `python3 -I src/PN1/cues27.py a14_lcomb=/mnt/t7/smad_next/PN1/lists/a14_lcomb.csv` on the DGX CPU;
   - write `sha256sum` of `/mnt/t7/smad_next/PN1/cues/a14_lcomb.npz` to `experiments/PN1_protocol-network-first-tests/tier1_a14/a14_lcomb_floor.sha256`;
   - commit it.
3. The lead rents one A100-SXM4 40 GB and sends READY HOST PORT LEASE. Then run:
   - full: `bash /home/narolski/smad-next/src/PN1/rented/drive14.sh HOST PORT LEASE start full`
   - reduced: `bash /home/narolski/smad-next/src/PN1/rented/drive14.sh HOST PORT LEASE start reduced`
   - then, for either: `nohup setsid bash /home/narolski/smad-next/src/PN1/rented/drive14.sh HOST PORT LEASE loop > /dev/null 2>&1 &`
4. When `PN1_A14.tar` is verified, the loop writes RELEASE, plus FAILED if rc is not 0. Then `python3 -I src/PN1/a14_read.py` reads it.

---

## Text 14 (full): to be pasted into prereg.md

### Amendment 14 (registered at the git commit that adds this section; no amendment-14 score and no landmark_combined statistic exists at that commit; author's answer on ffhqm endpoints: [to fill]): face-interior reads on one lease (HN7, HN8, HN2b)

Basis: review `REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md` (commit 88f6016) and pre-run review
`PRERUN_PN1_A14_AND_SEEDS_V3_20261112.md` (commit 3f2bd14).

**Networks.** The 12 finished networks, A, B, Bn, C, Sb and Bv at seeds 401 and 402. They are unchanged: `meta.json` and `last_trainable.pt` come from their verified result tars.

**Platform.**
- One rented A100-SXM4 40 GB lease, with image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` and the pip pins of `remote_setup.sh`.
- Guard values (the lead's guard): cap 1.5 USD, deadline at lease start + 2.5 h.
- Disclosed platform change: pn1a (A100-SXM4-40GB, seed 401) and pn1b (A100-SXM4-80GB, seed 402) are released. The GPU UUID and versions of the new lease are written into the result tar.
- An infrastructure failure is re-run unchanged, once, on the same lease type.

**Equivalence gate.**
- A_s401 and B_s402 are rescored on the full amendment-13 HN2 list (5,000 rows).
- Equivalent if, for both networks: max |Δ logit| ≤ 0.05, mean ≤ 0.01, and |Δ AUC (landmark_complete morphs vs FFHQ genuine)| ≤ 0.002.
- The gate binds only the reads that cross platforms, HN7 and HN2b. If it fails, those reads are printed "platform not equivalent; no verdict".
- HN8 is scored entirely on the one lease and is not voided by a gate failure.
- A failed gate is not re-run on another platform.
- Measured basis for the tolerance: rescoring 5 splice rows of Sb_s401 on the DGX GB10 differed from pn1a by at most 0.011 logits. That was a pipeline smoke test, not a read.

**Pack, lists, code (existing files only).**
- Pack `/mnt/t7/smad_next/PN1/pn1_a14.tar`, sha256 `bda5fd3d5043ad72e08e9c7aeee88ba42181dd2daf68af5a9674406a8a73ef72` (4,435,681,280 bytes). Its manifest `pn1_a14.csv`, sha256 `9f199c3a8a981fd2e3e46f0d7c66ddfe8f8cf0e2a48e68d7f8c3e374f0ba2fc2`, has 12,365 rows:
  - splice: 4,365 rows of pack 2;
  - ffhq: the amendment-13 HN2 list, 5,000 rows;
  - ffhq_lcomb: landmark_combined orig 1,000 and resmatch 2,000.
- Floor list `/mnt/t7/smad_next/PN1/lists/a14_lcomb.csv`, sha256 `e1df77a5956deef613280999eb2e492dc97ff0a3cc555a682750f62623f59f04`.
- Code:
  - builder `src/PN1/build_pack14.py`, `1f08b98defbfd276e906a0de1bc57fe6b0771ee169cf93047f5432776de6e482`;
  - scorer `src/PN1/rescore.py`, `6f6eede71c6d9a895199dabc8bc90b882adb25f5f91cd2fcc676ebe7a380b51e` (logit without flip);
  - `src/PN1/rented/remote_a14.sh`, `adc0b84d0a51912fcf8d4fdb490db19bb2ab3224a53b5b2926eacd4411157db6`;
  - `src/PN1/rented/drive14.sh`, `e079e4b5d60b73ec97ee108c38316347783f827c4a7ba61244f59bb6da17f44e`;
  - reader `src/PN1/a14_read.py`, `970a0e038d3eb03bd7712eb4c42edef209c4968b68c39a68c7bb7bba7ee506ae`;
  - floor cues `src/PN1/cues27.py`, `2338780c3fbb536b2d0aec938fb0f38b81df0b32af9b2a5fe59aa8c06ef0fd15`.
- Script behaviour:
  - Each scoring call continues on error and is logged.
  - On exit, whatever exists is tarred with an rc file and pulled.
  - The script stops early if /workspace has under 15 GB free.
  - The driver checks the A14_STARTED echo.
  - If rc is not 0 and the partial tar is verified, the driver writes RELEASE plus a FAILED marker.

**What the images are (F1).**
- landmark_combined: new morph images built from the HN2 pairs with a real surround.
- The genuine pool is the HN2 persons, re-shrunk.
- Independent of the training splice engine and of H1, not of HN2.
- All 1,000 landmark_combined morphs use the pair keys of the 1,000 landmark_complete morphs of HN2.
- Their history-matched genuine pool is the same 2,000 FFHQ persons and source photos as HN2's resmatch pool. Only the shrink target differs (64.65 against 64.61 px).
- Files: 256×256 PNG, native eye distance median 64.7 px.

**HN7 (associational, between arms).**
- Reads, per network (12):
  - face-only R4 vs R2w AUC on the test hosts (T_S4_bg vs T_S0_bg);
  - H1 AUC;
  - Spearman correlation of the two across the 12.
- Supported if ρ ≥ 0.6 and A's face-only AUC > B's on both seeds. Falsified if ρ ≤ 0.2. Otherwise "inconclusive, no claim".
- Printed:
  - arm-level ρ (seed means, n = 6);
  - ρ without Sb (n = 10, and arm level n = 5);
  - an interval from 2,000 joint bootstraps (rng 20261117) of test partner cycles and H1 hosts. These resample hosts, not training, so the interval is too narrow.
- Disclosure:
  - The 12 points are about 4 independent training regimes, because Bv is B with repeated rows and Bn is a subsample of B.
  - Sb is the only arm trained on splices.
  - All 12 H1 values and the 6 face-only values of B, Sb and Bv were known when HN7 was written.
  - The only prediction made blind is "A's face-only AUC > B's on both seeds".
  - HN7 cannot support "face-interior sensitivity sets the transfer". Its label is "associational, between arms".

**HN8 (landmark_combined).**
- Per network: AUC of landmark_combined orig morphs against landmark_combined resmatch genuine, with intervals from 2,000 bootstraps of images within class (rng 20261117).
- Ceiling: a seed with B ≥ 0.95 is untestable.
- Over testable seeds:
  - falsified if Sb ≤ B on any;
  - supported if both seeds are testable, and Sb − B ≥ 0.05 and Sb − A ≥ 0 on both;
  - "untestable (ceiling)" if no seed is testable;
  - otherwise "inconclusive, no claim".
- Floor:
  - Mandatory: the reader asserts the floor file exists and matches the committed sha256.
  - The floor is the best of the 27 simple statistics by direction-free AUC.
  - "Reads the face splice" is stated only if, on both seeds, the 2.5% bound of (Sb AUC − floor maximum, re-taken in the same draw) is above 0.
- Printed:
  - the aligned==1 subset (excludes 1 morph and 11 genuine);
  - the paired landmark_complete-minus-landmark_combined logit per pair key (1,000 pairs), with mean, median, share higher and a 2,000-draw interval. For A, B, Bn and C the landmark_complete scores come from pn1a / pn1b, so this read is cross-platform and printed only.
- Disclosure: A's reading of the history-matched pool is history-driven: 72–78% of FFHQ persons rise when history-matched (`tier1/posthoc_b2.json`). That moves "Sb ≥ A" for reasons other than face reading.

**HN2b.** Sb and Bv at both seeds on the HN2 list, under the amendment-13 rule and reader functions, labelled "added under amendment 14".

**Cost.** About 0.5 A100-hours, about 0.3 USD:
- setup and pip about 5 min;
- upload of 4.4 GB about 7 min;
- scoring about 92,000 images, about 10 min.

---

## Text 14R (reduced, if the author reserves landmark_combined): to be pasted into prereg.md instead

### Amendment 14R (registered at the git commit that adds this section; no amendment-14 score exists at that commit; landmark_combined not read on the author's answer [to fill]): HN7 and HN2b on one lease

Identical to Text 14, with these changes:
- **No HN8.** No landmark_combined row is scored, and no floor statistic is computed on landmark_combined.
- **Pack.** `/mnt/t7/smad_next/PN1/pn1_a14r.tar`, sha256 `efa700a9dc2e85d6a605722990511adcf6920ec3f1e9ef86519cf7edf3aac216` (3,429,068,800 bytes). Its manifest `pn1_a14.csv`, sha256 `2603c4a62cf8f0861d0b650bb7f6a889ad787e0afe48209d5f99c6c74dbde30d`, has 9,365 rows: splice 4,365 and the HN2 list 5,000.
- **Code.** Same files and sha256s as Text 14. remote_a14.sh is run with the variant argument `reduced`, which skips the ffhq_lcomb calls. The reader takes the variant from the tar.
- **Reads, gate, guard values and failure rules.** The equivalence gate, HN7 and HN2b are exactly as in Text 14. Guard values are the same: cap 1.5 USD, deadline at lease start + 2.5 h.
- **Cost.** About 0.4 A100-hours, about 0.25 USD (3.4 GB upload, about 62,000 images).
- **Command after READY.** `bash /home/narolski/smad-next/src/PN1/rented/drive14.sh HOST PORT LEASE start reduced`, then the loop command above.
