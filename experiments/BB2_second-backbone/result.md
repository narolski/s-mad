# Second backbone for the protocol recipe (BB2): result (part 1, registered read of the fits; C2P part pending)

Read once with `src/BB2/bb2_read.py` (sha256 b8d3f650…) on 13 Nov 2026 15:36 CET, after the seed mode was frozen
("five": all 15 fits fetched and verified; `seed_mode.json`, commit 546d892). Output `bb2.json`. Development data only
(FS1 pack: FFHQ landmark_combined and HN2 list, our FRGC / colorFERET ladder); no benchmark row. Backbone DINOv3
ViT-L/16, recipe and learning rates of the CLIP arm unchanged, WCSS H100. Counting: FS1's own rules (5 seeds). All 15
fits read (finite, H100, training-row accuracy at the own rule A 1.000, B 1.000, Sb 0.979; no fit collapsed: evaluation
logit SD 2.4-2.9). Not yet reviewed.

## Registered readings

| Contrast | BB2 (DINOv3, seeds 403-407) | CLIP (FS1, same seeds) | Registered sentence |
|---|---|---|---|
| 1, landmark_combined AUC: Sb − B ≥ +0.05 and Sb − A ≥ −0.02 | **not repeated** (0 of 5 seeds) | replicated (5 of 5) | "The gain of spliced positives on FFHQ landmark_combined did not repeat on a second backbone (DINOv3 ViT-L/16): it is not shown to be independent of the CLIP backbone." |
| 2, storage share ≤ 0.65 with A failing | uninformative (A passes on 5 of 5: shares 0.23-0.30) | uninformative | "storage mark uninformative (A's positive control not met on DINOv3)"; no CLIP effect to repeat |
| 3, face-only test ladder: Sb − B ≥ +0.05 | **repeated** (5 of 5) | replicated (5 of 5) | "The face-only ladder gain of Sb over B repeats on a second backbone (DINOv3 ViT-L/16)." |

Caveats carried by every sentence (prereg section 7): the spliced arm was first chosen on a frozen DINOv3 head read on
MAD22; development data only; ViT-L against ViT-B; CLIP learning rates used unchanged; different platform.

## Numbers (per seed 403 / 404 / 405 / 406 / 407; `bb2.json`)

- landmark_combined AUC: A 0.744 / 0.730 / 0.739 / 0.755 / 0.752; B 0.723 / 0.709 / 0.727 / 0.736 / 0.728; Sb 0.709 /
  0.711 / 0.729 / 0.739 / 0.723 (95% intervals about ±0.02). Sb − B −0.014 to +0.003; Sb − A −0.035 to −0.016. Best
  single statistic 0.886 (floor not exceeded by any arm). CLIP same seeds: Sb 0.814-0.885, B 0.649-0.710, A 0.688-0.764.
- Storage share (FFHQ persons whose logit rises under history matching): A 0.302 / 0.227 / 0.252 / 0.228 / 0.266; B
  0.217 / 0.229 / 0.231 / 0.199 / 0.248; Sb 0.282 / 0.290 / 0.280 / 0.260 / 0.277. CLIP A 0.53-0.63.
- Face-only test ladder AUC (contrast 3): A 0.536 / 0.523 / 0.592 / 0.650 / 0.527; B 0.545 / 0.527 / 0.573 / 0.616 /
  0.524; Sb 0.628 / 0.641 / 0.648 / 0.681 / 0.627 (Sb − B +0.065 to +0.114). CLIP: Sb 0.91-0.96, B 0.80-0.86.
- Face-blanked test ladder AUC (printed): 1.000 for every arm and seed (CLIP 0.99-1.00).
- Own-rule genuine flags (printed): development R0 and its stored copies 0-1%; AF0 validation photos 0-1.6%; FFHQ
  genuine 1.5-4.6%.
- R1-R6 (printed): R1 Sb − B −0.018 to −0.001; R3 Sb's increment over the 27 statistics minus B's −0.003 to −0.002;
  R6 AUC loss from landmark_complete to landmark_combined 0.25-0.29 for every arm (CLIP Sb 0.11-0.18). The R1-R6
  sentence is not evaluated (contrast 1 not repeated).

## Pending

C2P (contrast 2-prime and H-new-1 on the MS1 FFHQ hold-out) and the printed S3 reads: rescoring job queued with the
dispatcher (WCSS controller down since about 15:20); CLIP's comparison file follows `clip_choice.json` (amendment 3).
Independent post-result review (results-reviewer) after this part is written.
