# DRAFT amendment 14 (not registered, nothing run): face-interior reads on one rented lease (HN7, HN8, HN2 for Sb and Bv)

This draft follows the batch-2 review `experiments/reviews/REVIEW_PN1_BATCH2_FZ2A12_AR1A11_20261112.md` (commit
88f6016), section 4 (HN7, HN8) and section 5 item 3. It is for the lead's pre-run reviewer.

- No amendment-14 score exists.
- The pack below is built from existing files only; nothing was built as an image.
- Before submission, the registration copies this text into prereg.md and is committed. The registration commit is the time reference.

## 1. Networks and platform

- **Networks:** the 12 finished networks, A, B, Bn, C, Sb and Bv at seeds 401 and 402. They are unchanged: `meta.json` and `last_trainable.pt` come from their verified result tars.
- **Lease:** one rented lease of one A100-SXM4 40 GB (the pn1a type), with image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime` and the pip pins of `remote_setup.sh`. About 0.5 A100-hours, about 0.3 USD.
- **Platform change (disclosed):** pn1a and pn1b are released. Seed 401 was scored on pn1a (A100-SXM4-40GB) and seed 402 on pn1b (A100-SXM4-80GB). All amendment-14 scores come from the new lease, and its GPU UUID and versions are written into the result tar.
- **Equivalence gate:**
  - On the new lease, A_s401 and B_s402 are rescored on the full amendment-13 HN2 list (5,000 rows), which pn1a and pn1b already scored.
  - Equivalent if, for both networks: max |Δ logit| ≤ 0.05, mean |Δ logit| ≤ 0.01, and |Δ AUC (morphs vs FFHQ genuine)| ≤ 0.002.
  - If the gate fails, every amendment-14 read is printed with the label "platform not equivalent" and gets no verdict.
  - Tolerance reference: on the DGX GB10, rescoring 5 splice rows of Sb_s401 differed from pn1a by at most 0.011 logits. That was a pipeline smoke test, not a read.
- **Scorer:** `src/PN1/rescore.py` (sha256 `6f6eede7…`, as amendments 12 and 13), logit without flip.
- **Driver scripts:** `src/PN1/rented/remote_a14.sh` (`5ce2a5ce…`) and `src/PN1/rented/drive14.sh` (`34866f3a…`).

## 2. Pack and lists (existing files only)

- **Pack:** `/mnt/t7/smad_next/PN1/pn1_a14.tar`, sha256 `bda5fd3d5043ad72e08e9c7aeee88ba42181dd2daf68af5a9674406a8a73ef72` (4,435,681,280 bytes). Built by `src/PN1/build_pack14.py` (`aa21ada0…`), which checks every file against pack 2's SHA256SUMS or the FFHQ-Morphs SHA256SUMS. Contents:
  - code and the CLIP weights from pack 2;
  - the 12 networks' trained tensors and meta;
  - one manifest, `pn1_a14.csv`, sha256 `9f199c3a8a981fd2e3e46f0d7c66ddfe8f8cf0e2a48e68d7f8c3e374f0ba2fc2`, 12,365 rows:
    - fam splice: the 4,365 spliced and blanked ladder rows of pack 2 (1,455 attacks, 2,910 negatives).
    - fam ffhq: the amendment-13 HN2 list, 5,000 rows (sha256 `4c0caa89…`).
    - fam ffhq_lcomb: FFHQ-Morphs landmark_combined orig, 1,000 morphs. In this family the morph face sits inside a real surround (Neubert "combined"). These files already exist: 256×256 PNG, native eye distance median 64.7 px.
    - fam ffhq_lcomb: its history-matched genuine pool, landmark_combined resmatch, 2,000. The same FFHQ genuine persons as HN2, shrunk to the morphs' native eye distance by `prep_ffhqm.py`; the files already exist.
  - The genuine persons are disjoint from every morph contributor (dataset design, checked for the HN2 list).
- **Floor list:** `/mnt/t7/smad_next/PN1/lists/a14_lcomb.csv` (sha256 `e1df77a5956deef613280999eb2e492dc97ff0a3cc555a682750f62623f59f04`, 3,000 rows). Its 27 simple statistics are computed on the DGX CPU by `src/PN1/cues27.py` (unchanged), after the registration commit and before the lease result is opened.
- **What runs on the lease:**
  - gate: A_s401 and B_s402 on fam ffhq;
  - HN7: A, Bn and C at both seeds on fam splice. B's splice scores already exist (amendment 12), and Sb's and Bv's are in their own evaluation;
  - HN8: all 12 networks on fam ffhq_lcomb;
  - HN2 for the spliced arm and the volume control: Sb and Bv at both seeds on fam ffhq.

## 3. HN7: cue redundancy

- **Statement:** on full-frame morphs the surround is a sufficient and easier cue. A network's face-interior sensitivity, not its full-frame AUC, therefore sets its transfer to face-spliced attacks.
- **Reads, per network (12):**
  - face-only R4 vs R2w AUC on the test hosts (T_S4_bg vs T_S0_bg; face-only S4 is face-only R4);
  - H1 AUC (Poisson morphs vs genuine);
  - Spearman correlation of the two across the 12 networks.
- **Prediction:** Spearman ≥ 0.6, and A's face-only AUC above B's on both seeds.
- **Falsified** if Spearman ≤ 0.2. Otherwise "inconclusive, no claim".
- **Known:** B 402 is already a within-arm counterexample (face-only higher, H1 lower).
- **Interval:** 2,000 joint bootstraps (`default_rng(20261117)`) of test partner cycles and H1 hosts, with all 24 AUCs recomputed in each draw. The decision uses the point estimate; the interval is printed.
- **Label:** first-test data, re-read (test ladder, H1).

## 4. HN8: independent face-splice test

- **Reads, per network:** AUC of landmark_combined orig morphs against landmark_combined resmatch genuine, with 95% intervals from 2,000 bootstraps of images within class (same rng).
- **Prediction:** Sb − B ≥ 0.05 on both seeds, and Sb ≥ A on both seeds.
- **Falsified** if Sb ≤ B on either seed. Otherwise "inconclusive, no claim".
- **Floor, registered alongside and printed beside:** the best single statistic of the 27 simple statistics, by direction-free AUC on the same 3,000 images. It is not a mark. Unless the Sb AUC exceeds this floor, "reads the face splice" is not stated.
- **Label:** FFHQ landmark_combined has not been read by any PN1 network before; this is its first read.

## 5. HN2 for Sb and Bv

The amendment-13 rule and reader functions apply to Sb and Bv at both seeds. These results are labelled "added under amendment 14".

## 6. Reader

`src/PN1/a14_read.py` (sha256 `b653efba…`) writes `tier1_a14/a14.json`. It is written now, before any score, and is unchanged at registration.

## 7. Command (the lead, after a READY line HOST PORT LEASE)

```
bash /home/narolski/smad-next/src/PN1/rented/drive14.sh HOST PORT LEASE start
```

- Then the pull loop given in the header of `drive14.sh`. RELEASE is written when `PN1_A14.tar` is verified.
- Expected time: setup and pip about 5 min, upload of 4.4 GB about 7 min, scoring of about 92,000 images about 10 min.
