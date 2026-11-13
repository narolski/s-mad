# Second backbone for the protocol recipe (BB2): result (part 1, registered read of the fits; C2P part pending)

Read once with `src/BB2/bb2_read.py` (sha256 b8d3f650…) on 13 Nov 2026 15:36 CET, after the seed mode was frozen
("five": all 15 fits fetched and verified; `seed_mode.json`, commit 546d892). Output `bb2.json`. Development data only
(FS1 pack: FFHQ landmark_combined and HN2 list, our FRGC / colorFERET ladder); no benchmark row. Backbone DINOv3
ViT-L/16, recipe and learning rates of the CLIP arm unchanged, WCSS H100. Counting: FS1's own rules (5 seeds). All 15
fits read (finite, H100, training-row accuracy at the own rule A 1.000, B 1.000, Sb 0.979; no fit collapsed: evaluation
logit SD 2.4-2.9); Sb's misfit is concentrated in its splice rows (below). Reviewed: `experiments/reviews/REVIEW_BB2_PART1_20261113.md`
(conclusions need qualification; counts confirmed; wording below follows the review).

## Registered readings

| Contrast | BB2 (DINOv3, seeds 403-407) | CLIP (FS1, same seeds) | Registered sentence |
|---|---|---|---|
| 1, landmark_combined AUC: Sb − B ≥ +0.05 and Sb − A ≥ −0.02 | **not repeated** (0 of 5 seeds) | replicated (5 of 5) | Registered: "did not repeat on a second backbone ... not shown to be independent of the CLIP backbone." Qualified (review): on DINOv3 at the CLIP learning rates Sb did not fit its own splice training rows, so BB2 neither confirms nor refutes that the gain is independent of the backbone. Never "CLIP-specific". |
| 2, storage share ≤ 0.65 with A failing | uninformative (A passes on 5 of 5: shares 0.23-0.30) | uninformative | "storage mark uninformative (A's positive control not met on DINOv3)"; no CLIP effect to repeat |
| 3, face-only test ladder: Sb − B ≥ +0.05 | **repeated** (5 of 5) | replicated (5 of 5) | "The face-only ladder gain of Sb over B repeats on DINOv3 (+0.065 to +0.114, 5 of 5 seeds), at a low level (Sb 0.63-0.68, B 0.52-0.62; CLIP Sb 0.91-0.96). It appears only with the ladder's own splice engine, not on FFHQ landmark_combined." |

Caveats carried by every sentence (prereg section 7): the spliced arm was first chosen on a frozen DINOv3 head read on
MAD22; development data only; ViT-L against ViT-B; CLIP learning rates used unchanged; different platform.

## Numbers (per seed 403 / 404 / 405 / 406 / 407; `bb2.json`)

- landmark_combined AUC: A 0.744 / 0.730 / 0.739 / 0.755 / 0.752; B 0.723 / 0.709 / 0.727 / 0.736 / 0.728; Sb 0.709 /
  0.711 / 0.729 / 0.739 / 0.723 (95% intervals about ±0.02). Sb − B −0.014 to +0.003; Sb − A −0.035 to −0.010. Every
  DINOv3 arm is 0.13-0.18 below the best single statistic (noise_std_face 0.886). CLIP same seeds: Sb 0.814-0.885, B 0.649-0.710, A 0.688-0.764.
- Storage share (FFHQ persons whose logit rises under history matching): A 0.302 / 0.227 / 0.252 / 0.228 / 0.266; B
  0.217 / 0.229 / 0.231 / 0.199 / 0.248; Sb 0.282 / 0.290 / 0.280 / 0.260 / 0.277. CLIP A 0.53-0.63.
- Face-only test ladder AUC (contrast 3): A 0.536 / 0.523 / 0.592 / 0.650 / 0.527; B 0.545 / 0.527 / 0.573 / 0.616 /
  0.524; Sb 0.628 / 0.641 / 0.648 / 0.681 / 0.627 (Sb − B +0.065 to +0.114). CLIP: Sb 0.91-0.96, B 0.80-0.86.
- Face-blanked test ladder AUC (printed): 1.000 for every arm and seed (CLIP 0.99-1.00). The surround alone
  separates the test ladder perfectly for every network; this read does not discriminate.
- Own-rule genuine flags (printed): development R0 and its stored copies 0-1%; AF0 validation photos 0-1.6%; FFHQ
  genuine 1.5-4.6%.
- R1-R6 (printed): R1 Sb − B −0.018 to −0.001; R3 Sb's increment over the 27 statistics minus B's −0.003 to −0.002;
  R6 AUC loss from landmark_complete to landmark_combined 0.25-0.29 for every arm (CLIP Sb 0.11-0.18). The R1-R6
  sentence is not evaluated (contrast 1 not repeated).

## Post hoc, descriptive (review; training rows, development scores, weights; not registered)

- **Under-fitting of the splice rows (Sb):** S3 negatives flagged 57-58% (CLIP 26-37%); S4 morphs missed 17-20% (CLIP
  3-6%); training AUC S4 vs S3 0.578-0.593 (CLIP 0.854-0.881); S4 vs S0 about 0.90. Sb's loss levels off at 0.06-0.13
  (A, B about 0.024).
- **Adaptation size:** relative LoRA update ‖scale·BA‖ / ‖W‖ (q, v; mean over layers) 1.5-1.9% on DINOv3 against
  5.2-6.3% on CLIP (about 3.5x smaller); LoRA not inert (B norms 0.36-0.44); head weight norm 4.6-4.8 (CLIP 3.8).
- **Storage on DINOv3:** the plain arm's mean logit moves −0.03 to −0.06 genuine SD from native to history-matched
  FFHQ photos; own-rule flags 2.8-4.6% -> 2.9-5.1%; AUC matched vs native 0.48-0.49 (CLIP A: flags 6-11% -> 21-31%). On
  DINOv3 the plain recipe shows no storage reaction on these FFHQ development photos, so there is nothing for the
  protocol to remove there; the share falls below 0.5 because of a tiny uniform drop.
- **Read-out caveat:** BB2 reads the CLS token at 224 px; the tier-0 DINOv3 heads that motivated Sb read mean patch
  tokens at 512 px.
- Reading: BB2 is an attempted transfer of the recipe that did not adapt to the splice task at the CLIP learning
  rates. The storage claim cannot rest on DINOv3.

## Pending

C2P (contrast 2-prime and H-new-1 on the MS1 FFHQ hold-out) and the printed S3 reads: rescoring job queued with the
dispatcher (WCSS controller down since about 15:20); CLIP's comparison file follows `clip_choice.json` (amendment 3).
Predictions H-new-2 (S3) and H-new-3 (C2P control) logged in prereg.md before those reads (6f36c0c).

# Part 2: C2P (contrast 2-prime, H-new-1) and the printed same-person splice reads (S3) of the 15 CLIP-rate DINOv3 fits

Read once with `src/BB2/bb2_c2p_read.py` (sha256 cad995d8…) on 13 Nov 2026 19:14 CET (machine clock) from
`/mnt/t7/smad_next/BB2/results/BB2C2P.tar` (sha256 1ab51f3e…, local = .sha256 = WCSS; job 6313488, NVIDIA H100,
19:05-19:13, 0 failures); CLIP file fixed beforehand in `clip_choice.json` (e0325b5; CLIP's first C2P reading, C2P-R
not registered). Output `bb2_c2p.json` (sha256 c80249ba…). Five-seed rules (frozen mode). Development data only. Unreviewed.

- **Platform gate:** all 15 networks pass (max |Δlogit| 0.0003-0.0006 against their in-fit logits; probe: NVIDIA H100,
  TF32 in effect, matmul error vs fp64 2.9e-4; wrapper and rescore.py at their pins).
- **Contrast 2-prime: "uninformative" for B and for Sb.** The plain arm's positive control fails on 5 of 5 seeds at both
  sizes: A's own-rule flag rise on the 300 FFHQ hold-out persons is −0.003 to +0.003 (61.2 px) and −0.007 to +0.003
  (112.7 px), mean shift −0.15 to −0.11 genuine SD (stored photos score slightly lower). CLIP's contrast 2-prime was
  also uninformative, so the registered sentence is "No CLIP effect to repeat; printed only".
- **H-new-1 (storage evasion): "falsified" for B and for Sb** (morph shift −0.01 to +0.01 genuine SD at both sizes on
  5 of 5 seeds). CLIP: Sb falsified, B inconclusive (first C2P reading). Printed beside CLIP's.
- **Logged predictions (6f36c0c):** H-new-3 (A's control fails at both sizes on ≥ 4 of 5 seeds): **met** (5 of 5).
  H-new-2 (development S3 flags ≥ 50% on ≥ 4 of 5 seeds and S4-vs-S3 AUC ≤ 0.65): **met** (Sb S3 0.55-0.60, S4 vs S3
  0.567-0.574 on 5 of 5).
- **Printed S3 reads (development ladder, own rule):** Sb flags 55-60% of same-person splices (test ladder 62-66%),
  7-8% of seam-only composites (S0), misses 23-26% of face-spliced morphs (S4); S3 vs S0 AUC 0.78-0.79; S4 vs S3 AUC
  0.57. The plain and protocol arms also flag 43-49% of S3 (S0 9-13%), and miss 42-51% of S4; S4 vs S3 0.53-0.55.
  (CLIP at the same seeds: Sb 31-41% of development S3, A and B 2-7%.) On DINOv3 at CLIP's learning rates every arm
  reacts to a same-person blend inside the face about as often as to a two-person one.
- Storage reading for DINOv3 at these learning rates: none of the arms reacts to storage on the unseen hold-out
  persons (flag rise within ±0.007 at both sizes), so there is nothing for the protocol to remove there (descriptive).
