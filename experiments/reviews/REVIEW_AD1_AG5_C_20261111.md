# Independent review of AD1, AG5 and the cue checks (11 Nov 2026)

Reviewer: results-reviewer agent, read-only. Every number it recomputed from the per-image score files
matched the result files. Its own preview scripts are in `rev_scripts_20261111/`. Verdicts:

| Study | Verdict |
|---|---|
| AD1 (MorDIFF ladder) | accept-qualified |
| AG5 (StyleGAN3 ladder) | corrections required (wording only; numbers accepted) |
| C1 to C4 (cue checks) | accept-qualified |

Evidence level of all three: post hoc, one genuine pool (204 photos of 102 FRLL persons), released
weights scored once.

## Corrected wording (use these, not the earlier summaries)

- **MorDIFF, three adapted releases.** As scored in our pipeline, same-pair DiffAE morphs are not ranked
  above one-photo reconstructions rendered and stored identically: 0.480 (MADation ViT-B/16), 0.486
  (ViT-L/14), 0.403 (SelfMAD); upper bounds at most 0.59; same at 100 steps. Our morphs are
  indistinguishable from the published ones (0.48 to 0.51). Descriptive: the published MorDIFF error is
  not reproduced on our frames (4.9 against 1.10; 28.9 against 19.3).
- **One release does read the mixing step.** The released MADation FE ViT-L/14 (frozen encoder, trained
  head) separates morphs from reconstructions at 0.655 [0.581, 0.731] (20 steps) and 0.852 [0.799,
  0.903] (100 steps), without separating reconstructions from camera photos (0.459; 0.561 at 20
  steps); it also separates same-person mixes from reconstructions (0.721). No transfer to StyleGAN3
  (0.505). So "no released detector reads the morph step" is false.
- **Flag rates.** At each detector's EER threshold on our re-scoring of MorDIFF, giving the same 204
  genuine photos the morphs' resolution history raises the share flagged from 5% to 54% (ViT-B/16),
  from 26% to 51% (ViT-L/14) and from 2% to 98% (SelfMAD). At a threshold flagging 1% of untouched
  photos: 13%, 12% and 88%. The earlier sentence "51 to 98 percent are flagged" is withdrawn.
- **Storage alone.** For SelfMAD, a genuine photo merely stored at the published size outranks an
  actual MorDIFF morph in 89% of comparisons, and 203 of 204 such photos are flagged. This needs no
  ruling on what a reconstruction is.
- **StyleGAN3.** No network of 55 separates two-identity morphs from one-identity renders (maximum
  0.61; 0.42 to 0.53 against spread-matched renders). In 33 of the 42 recipe networks that separate
  the morphs from FRLL photos, and in the three releases, one-identity renders are separated from
  those photos at least half as strongly; that step mixes generator, source pool and resolution.
  Absence result; power not demonstrated (48% of these morphs verify against both contributors). The
  sentence "41 of 42 read the benchmark" is withdrawn.
- **Expression (reviewer preview, to be registered and rerun as C1b).** CLIP-based MADation networks
  score neutral genuine photos as more morph-like than smiling ones (ViT-L/14 release: 101 of 102
  persons, AUC 0.855). With neutral-only genuine photos its error rises, for example AMSL 17.7 to 24.5
  and Greedy-DiM 9.8 to 13.8. CNN recipes and SelfMAD do not show it. The imbalance flatters
  CLIP-based rows by 2 to 7 points in the 11 imbalanced cells, including our own retrains.
- **SelfMAD checkpoint selection.** The public code's default selects the checkpoint on test data that
  includes the 204 FRLL genuine photos used by every cell here; we could not determine whether the
  release was made this way. The MADation release epoch is undocumented too.
- Drop the d-prime shares from prose (they exceed 1 and do not add up); print AUCs against the camera
  photo and flag rates at a fixed threshold instead.
- Rename the "twin artefact" label on ViT-B/16 R2 vs R3 to "non-monotone rung; same-person mix
  confounded by expression".

## Follow-ups assigned

| Item | Owner experiment |
|---|---|
| Register and rerun the expression reading; neutral-only genuine column | C1b (running) |
| Frozen-feature readability probe; do fresh heads on frozen CLIP ViT-L/14 read the mixing step | FZ1 (running) |
| Re-score the MorDIFF ladder with the own-crop scorer so the benchmark number reproduces | WCSS slot task, not yet staged |
| Second photo pool | AD3, planned |
| Read the epoch field from the original SelfMAD archive | open |
