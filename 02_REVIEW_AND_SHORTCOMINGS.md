# Review of the experiment record and its shortcomings

Date: 11 Nov 2026. Sources: `mambamorph-code` (main at `1714b11`, ledger A1–A50, ABC60, A138/A139,
`experiments/research_loop_20261111/`), the OpenCode session "Eval image builder for MAD morph
experiments" (27 Oct – 10 Nov, 253 user messages), and the literature repository
`narolski/research` (branch `claude/biometric-sota-2026-litreview`). Nothing sealed was opened.

Terms: S-MAD = single-image morphing attack detection. EER = equal error rate. E7 = the control in
which the genuine photos get the same shrink-and-enlarge history as the morphs. Twin = a
one-identity image made by the same pipeline as a morph.

## 1. What the record establishes

| Area | Status | Evidence |
|---|---|---|
| Benchmark files differ by class before any face content is read | Shown | File attributes alone separate classes in 10 of 10 cells (A41). |
| Diffusion-morph scores of SelfMAD, MADation ViT-B/16 and the Inception recipe follow processing history | Shown (strongest part) | A32/A41, A43, A44 R-last, A46, A47 I-3. |
| Any detector separates GAN morphs from same-generator one-identity renders | Not found | 12 method rows, 51 networks, none at AUC ≥ 0.65 (A36/A37/A41). |
| Landmark-morph scores are a shortcut | Not shown | Four CLIP-based rows hold under E7 and beat the file-size floor. |
| A training change removes the shortcut | Partly, at a cost (corrected 11 Nov 18:15; was "Not found") | The same random resample, JPEG and blur chain on both classes removed the different treatment of shrunk genuine photos in A22 (+14.5 to -0.2 points, 5.1-point cost) and cut flagged shrunk FFHQ photos from 19 to 40% down to 4 to 8% in A30 amendment 6 (0.4 to 1.5 points). Not tested on the ladder. A49 (consistency loss) failed; ABC60 (more data) null; A47 I-1 costs accuracy; Astra E2 and ROI ideas negative. Source: `docs/PLANNING_RECORD.md` section 15 item 3. |
| MADMamba is competitive | No | W3/E10 scored 9.19%, 4th of six from scratch; absent from all work after 8 Nov. |

## 2. Shortcomings, ranked by how much they block a CVPR paper

1. **No positive result.** Every mitigation tried so far changed the loss or added unmatched data.
   None changed what the two classes differ in. As long as morphs and genuine photos come from
   different pipelines, any loss can still find the pipeline.
2. **No experiment has asked the direct question.** "Can a network tell a two-identity render from a
   one-identity render of the same pipeline when trained to do so?" was only ever tested zero-shot,
   on detectors trained elsewhere. The answer decides the paper and takes about one day.
3. **All decisive evidence rests on 204 FRLL photos of 102 people.** There is no second genuine-photo
   pool and no untouched test set; the fresh confirmation cohort failed at selection.
4. **The claim as worded by the author is wider than the evidence.** "Existing methods detect
   GAN/diffusion/regular morphs through benchmark cues" holds for diffusion, is an absence result for
   GAN, and has counter-evidence for regular morphs. `01_EVIDENCE_DOSSIER.md` gives the wording that
   survives review.
5. **Reproduction arm is weak.** Our Inception-MAD and MorphHRNet retrains miss the published numbers
   by 20–30 points (A45); the MixFaceNet crop branch is suspended for a crop defect (A46); fused FD-MAD
   never ran. These methods can only appear "as released" or be dropped.
6. **The label-permuted negative control (A47 I-4) was not at chance**, so the morph-free result
   (I-3: 0.00% EER on MorDIFF without ever seeing a morph) lacks its control. I-3 is the single most
   persuasive number in the record and is not yet registered in `PROTOCOL.md`.
7. **Process cost exceeded science output.** From 8 to 10 Nov the record shows about 90 commits, an
   orchestrator daemon, deadline enforcement and resource journals, and three finished studies. Jobs
   failed at 0 s several times; MAD22 is forecast to start on 13 Nov 23:20. The author's messages on
   10 Nov ask repeatedly why nothing is running.
8. **Compute sat idle or reserved.** 245 H100-hours reserved, 66 used. Vast balance is about 15 USD.
   The DGX runs one 4 GB job.
9. **The data that the fix needs is blocked on paperwork.** The DiffAE pool has zero images because the
   FERET/FRGC use-scope question was never answered.
10. **Ledger drift.** A44/A45/A47 entries still say "running"; A138/A139 live only under
    `/tmp/opencode`, which does not survive a reboot.
11. **Two loops write to one repository** and reuse seeds 201–205.

## 3. What this implies for the next four days

- Move the intervention from the loss to the data: both classes from one pipeline, one history.
- Use frozen features and small heads first. A full pass over a twin set is a few GPU-minutes, so ten
  ideas can be tested in a day on the DGX with no queue.
- Keep one page of pre-registration per experiment (hypothesis, falsifier, metric, stop rule) and one
  review. No orchestrator, no per-job resource journals.
- Design every experiment so that both outcomes can be written up (see `05_RESEARCH_PLAN.md`,
  section "What the paper says under each outcome").

## 4. Notes from the OpenCode session

- The session wrote `smadcvpr/prep_eval.py` (alignment with compression and resampling), ran the
  A10/A12 batches, and from 8 Nov ran the ABC60, MAD22, A138 and Astra work.
- Author rulings recorded there and still binding: no ensembles or seed picking; five real seeds;
  sealed files stay closed; experiments may run in parallel; the 11 Nov cutoff is superseded.
- The author's goal on 10 Nov 13:00: "Rozwiąż problem uczenia się pod skróty dla detektorów morfów."
  The session's own direction at its end matches this plan: matched same-person / two-person rendering
  controls plus a frozen-feature head. It was never executed (renderer pinned to the local ARM CPU,
  source-scope gate closed).
- User message list: `context/opencode_eval_image_builder_user_messages.txt`.

## 5. Notes from `narolski/research`

- The review's cross-area finding is the same thesis: "detectors learn the trace of one production
  step", and the working recipe elsewhere is a web-scale encoder, lightly adapted, "trained on data in
  which the target trace is the only class difference, checked by shortcut audits" (B-Free, DDA,
  AVH-Align).
- NIST FATE MORPH (Sept 2026): no system is strong on both Greedy-DiM and manual morphs. This is the
  external motivation.
- LoRA-adapted CLIP beats instruction-tuned multimodal models on morphs; full fine-tuning collapses
  feature rank. This supports a frozen or lightly adapted CLIP ViT-L/14 as the base.
- One correction for that repository: the "Alpha Blending Hypothesis" paper (arXiv:2605.10334) was
  withdrawn on 4 Nov 2026 for train/test overlap; its numbers should not be cited.
