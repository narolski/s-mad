# Planning record: what the planning, inventory, literature, review and ideation agents found

Written 11 Nov 2026 (evening) by a documentation agent, on the author's instruction of 11 Nov that the research
of every subagent is documented in detail so that nothing is lost. Scope: the 13 agents of the main session that
did not own an experiment, and the three saved workflow outputs (ideation round 1, vetting round 2,
class-definition literature check). Experiment owners document their own work in
`/home/narolski/smad-next/experiments/<folder>/README.md`.

**How this was made.** Each transcript
(`/home/narolski/.claude/projects/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/subagents/agent-<id>.jsonl`)
was read with `/home/narolski/smad-next/src/docs_tools/dump_transcript.py`
(`python3 -I dump_transcript.py <transcript> [--section task|middle|final|rawfinal] [--results-for REGEX]`): the task
and the final report in full, the middle through assistant text, one-line tool summaries and selected tool
results. Every finding was then searched for in `README.md`, `NOTEBOOK.md`, `EXPERIMENTS.md`, `01` to `14`,
`ideas/`, `literature/`, `prior/INDEX.md` and `experiments/` (including `experiments/reviews/`). A copy of the
plan files as of 14:02 CET (the prior-arrangement agent's clone,
`/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/smad_prior/s-mad/`)
was compared with the current files: the lead's later edits to `06`, `07`, `08` and `11` added lines and removed
only 3 (in `06` and `07`); `01`, `02`, `03`, `04`, `05`, `09` and `10` are unchanged since then.

**Marks.** "Recorded in" names the file and heading. "Not recorded elsewhere" lists in full what the repository
does not hold, or holds less precisely than the agent reported it. "Not verified" means the agent said so or I
could not check it. Numbers, links and paper references are as the agents gave them; nothing was re-run.

**Not copied.** The corrected-MAD22 acquisition receipt read by the inventory agent contains a share link with an
access token: [stored outside the repository]. No key, password or token appears in this file. No sealed file was
opened for it.

**Abbreviations used throughout.** S-MAD = single-image morphing attack detection. EER = equal error rate, in %.
AUC = area under the ROC curve (0.5 = chance). MAD22 = the SYN-MAD 2022 benchmark; "corrected MAD22" = the
author's re-upload of 9 Nov (204 genuine images, 4,483 morphs). FRLL = the Face Research Lab London set (102
persons, a neutral and a smiling frontal photo each). SMDD = Synthetic Morphing Attack Detection Development set
(StyleGAN2 renders and landmark morphs). E7 = the approved control that gives genuine photos the morphs'
shrink-and-enlarge history (also called "resmatch" or "RSX"). DGX = the local DGX Spark (ARM, GB10 GPU). WCSS =
the Wrocław supercomputer (Slurm, H100 GPUs). H100-h = one hour of one H100. Vast = a rented-GPU market. LoRA =
low-rank adaptation. FE / FS = MADation's frozen-encoder / from-scratch released variants. BPCER / APCER =
genuine-rejection / attack-acceptance rate. FMR = false-match rate. DiffAE = diffusion autoencoder. MIPGAN = the
identity-prior GAN morph generator. Rungs R0 to R4, R2w, R3m: as in `/home/narolski/smad-next/EXPERIMENTS.md`.
Path abbreviations in section 1: `E/` = `/home/narolski/mambamorph-code/experiments/`, `RL/` =
`E/research_loop_20261111/`, `ORCH/` = `/home/narolski/.local/state/smad-orchestrator-v1/`, `T/` =
`/tmp/opencode/`.

## Overview

| # | Agent (transcript id) | Model | Time (CET, transcript) | Output | Record state |
|---|---|---|---|---|---|
| 1 | Review of the repository state since 8 Nov (aaa120f8d2f9b3fe5) | Fable | to 13:14 | report only | condensed into `02`, `12`; most detail missing (section 1) |
| 2 | Evidence inventory for the shortcut claim (aa6c31710fa500a8c) | Fable | to 13:14 | `01_EVIDENCE_DOSSIER.md` | byte-identical copy; two sources it cites live only in a scratchpad |
| 3 | Literature research on shortcut-robust S-MAD (a30d1c6dd23d54541) | Fable | to 13:14 | `03_LITERATURE_AND_METHODS.md` | byte-identical copy; a few fetched details missing |
| 4 | Web search for detector releases (a390f2ea6518de9c1), helper of 8 | Sonnet | 13:41 to 13:42 | report only | table in `10` section A.1; links and terms missing |
| 5 | Pre-run review of the sprint plan (abddeb219d2e716de) | Fable | 13:43 to 13:48 | report only | fixes applied in `11`, `04`, `05`; report now saved |
| 6 | Cue matrix from the record (a6ca26fd0d48da3cf) | Opus | 13:40 to 13:50 | `08_CUE_MATRIX.md` | intact; lead added an update list |
| 7 | Dataset-extension coverage analysis (a4b2797a30db79a2e) | Opus | 13:40 to 13:52 | `09_DATASET_EXTENSION_ANALYSIS.md` | intact; full derived tables and scripts missing |
| 8 | Inventory of detectors, corrected MAD22 and generators (a8f961816f943fb23) | Opus | 13:40 to 13:52 | `10_ASSET_INVENTORY.md` | intact; small details missing |
| 9 | Arrangement of prior experiments in narolski/s-mad (a28c7df2c4d1e1147) | Sonnet | 14:02 to 14:12 | branch `prior-work` | not merged: the repository still shows the older index |
| 10 | Prior-art sweep of morph detection ideas (a20a8d98e619e6803), helper of 11 | Sonnet | 14:51 to 14:57 | report only | verdicts in `ideas/IDEAS_v1.md` appendix; numbers missing |
| 11 | Research strategist for S-MAD ideas (acf7970ed07505ca6) | Fable | 14:43 to 15:01 | `ideas/IDEAS_v1.md` | intact |
| 12 | Pre-run review of the MIPGAN one-person controls (AG1) (aa7ebfd5a55401578) | Opus | 15:03 to 15:20 | report only | fixes in AG1 amendment 1; report now saved |
| 13 | Pre-run review of the SMDD five-partner audit and rebuild (SM1) (a2cfd6de5170bc99a) | Opus | 15:42 to 15:53 | report only | fixes in SM1 amendment A1; report now saved |

The verbatim reports of agents 5, 12 and 13 are now at
`/home/narolski/smad-next/experiments/reviews/PRERUN_SPRINT_PLAN_20261111.md`,
`/home/narolski/smad-next/experiments/reviews/PRERUN_AG1_20261111.md` and
`/home/narolski/smad-next/experiments/reviews/PRERUN_SM1_20261111.md`.

---

## 1. Review of the repository state since 8 Nov (agent aaa120f8d2f9b3fe5)

**Task.** Reconstruct, read-only, what happened in `/home/narolski/mambamorph-code` between 8 Nov 00:00 and
11 Nov (about 90 commits, `CONCLUSIONS.md`, the research loop of 11 Nov, the mitigation plan, the ledger entries
A43 to A47 and every newer batch), so that a research plan could be written. Report status and verdicts per
experiment, what "Astra" is, the mitigation plan and its gaps, what is running, the binding rules, and the ten
main risks, with a file path for every claim.

**What it found, and where it is recorded.** The report covers 8 Nov 00:00 to 11 Nov 13:11 CET. Nothing was
edited; the agent ran local `ps` and an `nvidia-smi` process query. Recorded:

- The status table and the ranked shortcomings: `02_REVIEW_AND_SHORTCOMINGS.md`, sections 1 and 2 (no positive
  mitigation result; weak reproduction; label-permuted control not at chance; process cost; 245 H100-h reserved
  and 66 used; data blocked on use-scope paperwork; ledger drift; two loops reusing seeds 201 to 205; MAD22 start
  forecast 13 Nov 23:20; MADMamba W3/E10 at 9.19%, 4th of six).
- The DGX processes and WCSS jobs of the Codex loop: `12_STATE_AT_HANDOVER.md` (from the Codex hand-over, which
  agrees with this report): PID 1623204 then controller 1637166, controller 1729673, PID 1668495;
  `6299123_[0-7]`, `6300801`, `6294928_[4-14]`, AB4 `6299453`.
- Vast ceiling of 100 USD in total: `12`, `06` and `07` decision 4.
- A45, A46 and A47 headline numbers: `01_EVIDENCE_DOSSIER.md` section 2.4.

**Not recorded elsewhere (full content as reported).**

*Timeline by theme* (`git log --since=2026-11-08`):
- 8 Nov 13:20 to 16:20: closing A44 to A47 with copy-backs, registered reads and independent reviews; the
  diffusion reproduction register on raw files (A46) took about 20 commits because of a crop-defect saga
  (`E/INDEPENDENT_REVIEW_*.md`).
- 8 Nov 13:54 to 14:20: author rulings on the MAD22 working subset, WCSS concurrency and autonomous follow-up
  (`E/MAD22_WORKING_DECISION_20261108.md`, `E/WCSS_CONCURRENCY_AUTHORIZATION_20261108.md`,
  `E/AUTONOMOUS_CONTINUATION_20261108.md`).
- 8 Nov 14:13 to 21:38: DINOv3 adaptation with a consistency loss (A49, four arms × five seeds) and the missing
  A/B/C control (A50) registered, run and reviewed.
- 8 Nov 21:35 to 24:00: mitigation planning: mitigation plan, then a four-model data-expansion pilot, then
  primary80fit, then the six-arm primary120fit, with smokes and budget gates (`E/primary120fit/SCOPE_CHANGE.md`).
- 9 Nov: classifier budget of 180 / 345 H100-h activated; ABC60 arrays submitted; 38 original fits verified;
  MAD22 author re-upload acquired; MAD22 synthetic smoke failed.
- 10 Nov: ABC60 accepted-qualified; MAD22 CPU plans (exact86, strict149 / cost24, canonical164) registered;
  own-generation pipeline prepared but blocked; orchestrator daemon and deadline enforcement built (paper
  repository commits `16ec66c` to `14bee08`).
- 11 Nov: "research loop" snapshot committed at 13:01 (`1714b11`): Astra E2, DiffAE102 / region of interest, the
  region-of-interest falsification (called A37 in the loop), GAN32 on Vast, first Astra CLIP fit.

*Experiments, status and numbers:*
- MorDIFF two-by-two (A43): analysed 7 Nov, 0.108 H100-h. The official MADation ViT-B/16's MorDIFF separation
  follows the decoding step count (score-blind match m = 20). R0 and R0m supported, R1m and R3m falsified, the
  joint shortcut hypothesis H-new-241 supported, the identity evidence R2m open (`E/A43_mordiff-two-by-two/meta.json`).
- MADation mechanism (A44), `E/A44_madation-mechanism/README.md` l.213 to 276: the eight last-checkpoint
  retrains (A44R) accepted-qualified: native MorDIFF 4.44%; R1 refuted (A_rec 0.476); R2 present (E7 rise
  +11.39 points, release-magnitude criterion not met); R3: H3 AUC 0.530, below 0.65. Original reads of 8 Nov: F1
  supported, F2 neither, F3 neither, F4 LoRA-carried, F5 dose response. Not run: F6 / H-new-281 (release feature
  extraction died on `NameError: torch`) and the D3 A43-arm reader path. D5 (R-aug / R-shuffle) withdrawn. The
  independent review of the 8 Nov original reads is still pending; `meta.json` verdicts are stale ("open").
- SMDD-only reproduction retrains (A45): corrections required (`E/INDEPENDENT_REVIEW_A44R_A45_20261108.md`). All
  reproduction gates fail on MAD22-5: Inception 32.72 against 10.53 published; HRNet-W18 40.91 and W48 34.93
  against 9.42. FD-MAD global branch 56.02 (256 px) and 27.61 (512 px) against 16.62: "not comparable", a partial
  implementation. The fused FD-MAD branch (H-new-294) was not run; H-new-295 not reached. 85 `rise_p10` values
  were serialised against the "no p-value" rule and are excluded from inference. `meta.json` and README still say
  running / not run.
- Diffusion reproduction register on raw files (A46), `E/CONCLUSIONS.md` l.335 to 369: the MTCNN branch is
  suspended, because the released crop script passes BGR and leaves negative slices unbounded (900 of 948 MorDIFF
  crops are 32 px or smaller). The paired BGR/RGB corrective study is blocked before scoring (one flagged crop is a
  single eye). RGB-only secondary accepted-qualified, descriptive: MixFaceNet 15.34% MAD22-5, 9.90% FRLL-5, 8.91%
  MorDIFF; `published_reproduction_admitted=false`. Surviving verdicts: H-311 falsified (MIPGAN cells not
  reproduced), H-312 supported, H-313 falsified (the N3 refuter fires, A_rec 0.72 / 0.74), H-322 falsified. The
  from-scratch ViT-B/16 X3 read not run.
- Training interventions (A47): accepted-qualified (`E/INDEPENDENT_REVIEW_A47_20261108.md`). Morph-free network
  (I-3): M3 held (MorDIFF 0.00%, DiM 0.00 to 1.17%); M1 partial (MorDIFF 14.88%). Label-permuted control (I-4): not
  chance-level for both recipes (6 of 17 and 11 of 17 cells), so uninterpretable. Augmentation (I-1): M1 "costs
  accuracy generally" (native +52.45 points); M3 not applicable. X3: M3 AUC 0.951, M1 0.635. README and `meta.json`
  still say "Pending".
- A48: a historical ID reservation only; no ledger entry
  (`E/SHORTCUT_MITIGATION_COVERAGE_AUDIT_20261108T213558_CET.md`).
- DINOv3 layer-norm-affine adaptation with a consistency loss (A49): primary failed. P3 − P1 instability +0.00287
  [−0.0049, +0.0106]; native +0.246 points, passing the +2 point non-inferiority margin. Head-only P0 at 7.70%
  beats the adapted P1 at 10.71%. Cost 20.50 H100-h (`E/CONCLUSIONS.md` l.371).
- C − B replacement on four A12 carriers (A50): accepted-qualified. Capped gains only for M2 (−2.11 points) and
  M6 (−2.20 points), Holm p = 0.028. Uncapped EER worsens for three of four carriers; M2 Greedy-DiM +17.93 points.
  Cost 13.65 H100-h (l.377).
- The 60-fit data-arm study (ABC60): ConvNeXt-T, VMamba-T, DeiT-S and DINOv3 × arms A / B / C × seeds 201 to 205
  (A = SMDD, B = plus genuine photos, C = plus classical morphs). Accepted-qualified 10 Nov. All eight C − A
  intervals include zero (VMamba Q +2.45; native17 −12.45 [−24.96, +0.06]). Absolute Q is 45 to 53% EER; 412
  inverted and 152 near-constant flags; no Mamba advantage. The generated arms CG / CD / CGD ("generated60",
  completing "full120") were not run, so the four primary and two moderation tests are unevaluable. 66.14 H100-h
  used, 245.17 reserved (`E/CONCLUSIONS.md` l.385 to 446).
- MambaVision data arms (mv30 / ABC15): MambaVision-B-21K × A / B / C × five seeds; "mv30" adds the generated 15.
  Array 6294928: tasks 0 to 3 failed after 11,402 s each; tasks 4 to 14 held. An A/A replay (6297832) was
  tolerance-close but not bitwise; the AB4 trajectory diagnostic (6299032) hit DEADLINE at 0 s
  (`/home/narolski/mambamorph/research_notes/MAMBAVISION_AA6297832_QUALIFIED_PROTOCOL_ADDENDUM_20261110.md`).
- Algorithmic mitigation (A138): DINOv3 and ConvNeXt on fixed C with four arms: F head-only, N LN-affine, P
  two-view processing, A feature anchoring to the pretrained teacher (λ ∈ {0.1, 1}); GroupDRO (G) rejected.
  D3-F / N / P / A are the DINOv3 timing profiles. D3-F completed in 157 s. The uncommitted `CONCLUSIONS.md` says
  D3-N failed; the later `RL/README.md` says D3-N and D3-P completed and verified, with D3-A (6300801) pending.
  The 16 development and 30 conditional final fits were not run
  (`T/mambamorph-a138-algorithmic/experiments/A138_algorithmic/README.md`).
- Matched generation controls and x86 DiffAE runtime (A139): eight-dyad matched generation controls plus an x86
  DiffAE runtime build. Inventory job 6297756 failed in 3 s; runtime not built (`ORCH/receipts/A139_*.json`).
- Corrected MAD22 scoring (canonical164): the full corrected MAD22 (4,687 native images plus E7 panels, 164 tasks)
  for 15 models. The context15 smoke passed. Production job 6298965 was cancelled at 0 s; it now sits as the
  8-shard array 6299123_[0-7], pending, forecast 13 Nov 23:20 (`smadcvpr/PROTOCOL.md` l.20539 to 20545;
  `T/wcss-partition-amendment-state.md`).
- Own generation pool (own_generation_v1): a 1,500-pair DiffAE pool (D) plus 3,000 audited historical GAN images
  (G). Zero D images generated; blocked on dataset-use scope facts, review and runtime
  (`E/own_generation_v1/REVIEW_PUBLICATION.json`).
- Narrow / diverse20 pilot: prepared, explicitly last (`E/NARROW_DIVERSE_PILOT_20261108T215424_CET/`).

*Astra.* An external 13-point audit (ARER-RR, 2 Nov) of a CLIP-token normalisation idea, not a model
(`RL/reports/ASTRA_13_EXECUTION_PLAN_PL.md`).
- Idea: per-image channel normalisation of frozen CLIP ViT-B/16 patch tokens (arm RR) should remove the
  resolution / processing shortcut. Controls: RB (fixed training normalisation), RC (non-affine LayerNorm token
  read), C0-hi (probe baseline), RRo (no probe branch), and "−aug" variants (resize 96 to 512 with p = 0.5, JPEG
  quality 30 to 95).
- E2 gate, negative: on 204 FRLL genuine photos × 8 variants (1,632 views, 112 decoders) the resmatch signal is
  decodable at AUC 1.0. Kappa 1.195 / 1.122 / 1.116 / 1.174, so 0 of 4 taps pass the ≤ 0.5 threshold; RR, RB and
  RRo not admitted. The null controls resample50 and blur1 also failed validity (`RL/results/astra_e2/DECISION.json`).
- Remaining core: 20 fits (C0-hi, RC, C0-hi-aug, RC-aug × seeds 201 to 205), PAS_total primary, +1 point native
  non-inferiority margin (`RL/protocols/astra_core20.md`). One fit running at report time; the augmented loader
  not yet admitted.
- DiffAE102 / region of interest: 150 frozen heads; an apparent inner-region gain on H3 (0.557 against 0.432 for
  the full image).
- Region-of-interest falsification (A37 in the loop), negative: with latent-spread-matched negatives the inner
  region falls to 0.461 / 0.467 against 0.487 / 0.489 for the full image; region minus full −0.026
  [−0.062, +0.009]. No mitigation established (`RL/reports/A37_ROI_FALSIFICATION_PL.md`).
- GAN32: 128 inversions, 256 images. Frozen-head scoring done but unverified and unreported. Fresh
  confirmation-64 selection stopped on an undersized metadata cell (`RL/README.md`).

*Mitigation plan and the gaps of its coverage audit.* The plan
(`E/SHORTCUT_MITIGATION_PROSPECTIVE_PLAN_20261108T213558_CET.md`) was proposed, never registered: paired
processing consistency (JS divergence, λ 0 against 1, both arms two-view) on 12 core carriers × 2 arms × 5 seeds
= 120 fits, or 150 with CLIP-L, DINOv2-S and Swin22; seven Mamba-against-other interaction contrasts; Holm over 12
and over 7; fixed final checkpoint; budget request 400 / 480 H100-h. Pre-review: go with fixes for preparation,
no-go for production (`E/INDEPENDENT_PREREVIEW_SHORTCUT_MITIGATION_20261108T214152_CET.md`). Gaps: zero reusable
historical baselines; CLIP tensor conversion and the Swin22 snapshot unpinned; main branch lacks the A12 loader;
the MADMamba arm is an image-only objective, not the W3 recipe; the 18-cell evaluation grid equals the training
support, so it shows no transfer; no unseen-source test; the intervention had already failed in A49; the CLIP
dropout stochasticity confound is unaddressed; the budget was never authorised. Superseded in practice by the
data-arm primary120fit and by A138.

*Live processes at 13:11 CET beyond those in `12`* (DGX):
- PID 1623204 (driver 1623203): Astra C0-hi seed 201 at step 1,300 of 6,250, 1.51 it/s, about 14:05 finish,
  4.4 GB GPU, writes `/mnt/t7/smad_research/astra-core20-v1/seed201-C0hi`.
- PID 1634262: RC-aug seed 201 `--probe` (`T/astra-core20-aug-v2-source`), on GPU.
- PIDs 1568493 and 1631944: Vast watchdogs for leases 60202380 and 60203980 (GAN TRAINplus shards).
- PID 376521: orchestrator daemon. PID 4010194: ssh multiplexer `T/wcss.ctl`. PID 3905934: `opencode serve`.
  Several `claude --resume` and Codex sessions.
- PID 4141380: `http.server` on 0.0.0.0:8000 serving `T/kamil-share` (reachable from the network).
- WCSS, from state files (not re-polled): 6300531 D3-P, in addition to the jobs listed in `12`.

*Rules recorded since 8 Nov:*
- Vast: 100 USD total (older documents say 20); balance about 14.8 USD; lease upper estimates about 12.7 USD
  (`RL/README.md`, `T/vast-lease-*/LIVE_BUDGET.json`).
- WCSS: concurrency follows scheduler limits only; budgets, FORCE_RM_TMPDIR, Nice0 and sequential ssh remain.
- Classifier budget: 180 ABC / 345 full H100-h (commit `8e89b54`); caps 257.5 / 422.5, of which 245.17 reserved
  and 165 for generated arms. Generation is budgeted separately.
- Retries: no automatic retry, refund or requeue; consumed attempts (MAD22, AB4) need a new prospective
  registration.
- MAD22 (rule of 8 Nov, before the corrected copy existed): report the 185 / 4,069 subset as best confirmed,
  always beside the published 204 / 4,483.
- Autonomous follow-up allowed if prospectively registered and independently reviewed. No ensembles or seed
  picking; selection on VALX-A* only; no edits to `prep_eval.py` / `prep_gtest.py`.
- Seals: `fst*`, A12SP and `manifests/valx.csv` stay closed. W3/E10 was scored once (9.19%, 4th of six from
  scratch); the FST is not built with its diffusion family; MADMamba was not evaluated in A47 or the mitigation work.
- Deadline: the user's extension supersedes the old 11 Nov cutoff but not the per-job caps; publication 16 Nov.

*Risks not in `02`:*
- No PROTOCOL registration was found for the 8-shard MAD22 array 6299123; the registered canonical164 is a single
  50,400 s allocation. Needs checking (not verified since).
- Beyond `02` item 10 (A138 / A139 only under `/tmp/opencode`): they are also absent from `PROTOCOL.md`, part of
  their state is under `ORCH/`, and `/tmp/opencode` holds other primary evidence too (for example the corrected-MAD22
  raw manifest, since copied to `/mnt/t7/smad_next/volatile_backup_20261111/`).
- The Astra stream runs in a parallel Codex / opencode process with compressed pre-registrations, on the DGX and
  Vast; collision risk with the orchestrator's owners.
- All evaluation sets are already seen and design-informed; the fresh confirmation cohort failed selection; there
  is no untouched test or FST.
- MADMamba is mid-pack, fails the GAN test and is absent from every post-8-Nov study; the retitle decision
  (`E/CONCLUSIONS.md` l.301 on) is open.
- Operational fragility: unresolved MambaVision non-determinism, repeated 0-second failures, large unrefunded
  reservations, and the network-exposed http server above.
- Uncommitted changes in `/home/narolski/mambamorph-code`: `experiments/CONCLUSIONS.md` and
  `experiments/site/index.html`; the uncommitted `CONCLUSIONS.md` already contradicts the later D3-N / D3-P state.

*Two user messages that arrived after the report* (not acted on, read-only task):
"git@github.com:narolski/research.git is the repo" and "If you do more research, consider updating it, please".
`07_DECISIONS_NEEDED.md` records only "push the morph literature note to narolski/research".

---

## 2. Evidence inventory for the shortcut claim (agent aa6c31710fa500a8c)

**Task.** Build an evidence dossier, from logged and registered results only, for the claim that existing S-MAD
methods score well on landmark, GAN and diffusion morphs because of benchmark cues rather than the morphing
signal. Give a one-page summary, per-family tables with sources, construction evidence, what the evidence does not
show, ranked gaps, and the status of the A45 / A46 / A47 reads.

**Recorded in.** `/home/narolski/smad-next/01_EVIDENCE_DOSSIER.md` is byte-identical to the agent's output
(`.../scratchpad/smad_next/EVIDENCE.md`). Its final summary (diffusion strongest; GAN absence only; landmark
descriptive with counter-evidence; claim B file attributes O = 1.000 in 10 cells; A45 / A46 / A47 all read on
8 Nov; seven ranked gaps) is in sections 1, 2.4 and 5. Its caveat that the A32 to A42 numbers were not re-read
in PROTOCOL is in section 6.

**Not recorded elsewhere.**
- The dossier rests partly on two secondary sources that exist only in the session scratchpad, which is not
  backed up: S1 = `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/methods_table/methods_table_final.md`
  (59,793 bytes, 7 Nov 18:19) and S2 = `.../scratchpad/methods_table/shortcut_per_method_final.md` (45,228 bytes,
  7 Nov 18:53). `01` cites S1 or S2 27 times; the vetting round's record check (section 14.2) also took the
  adapted-release landmark numbers (1.0 / 1.0 / 14.7 / 4.4) from S1. The same folder holds the inputs they were
  built from (`gather_diffusion.md`, `gather_gan.md`, `gather_regular.md`, `claims.txt`, `conc_now.txt`,
  `a41reg_tmp.txt`, `build_methods_page.py`, `methods_page.html`). None of these is in any repository.
- A scratch extract `.../scratchpad/smad_next/_p1.txt` (PROTOCOL l.19973 to 19996, 20234 to 20353, 20369 to 20413)
  was left behind; it holds no finding of its own.

---

## 3. Literature research on shortcut-robust S-MAD (agent a30d1c6dd23d54541)

**Task.** Survey 2022 to 2026 work on shortcut mitigation, deepfake-detection analogues, identity-blending signals
and benchmark-bias papers, each with idea, our-setting version, needs and risk. Then propose five to seven
shortcut-free S-MAD designs feasible in four days, ranked.

**Recorded in.** `/home/narolski/smad-next/03_LITERATURE_AND_METHODS.md` is byte-identical to the agent's output.
The final report's points (no published MAD shortcut audit; "Fake or JPEG?", B-Free, Aligned Datasets, Dual Data
Alignment; SelfMAD labels one-identity blends as attacks; zero-shot results; "When Morphs Look Better"; the
withdrawn Alpha Blending paper; the norm-shrink factor sqrt((1+c)/2), 0.71 and 0.87; seven ranked designs; risks)
are all in that file and in `04_HYPOTHESES.md` M3.

**Not recorded elsewhere** (details of the four pages the agent fetched, not carried into `03`):
- arXiv 2611.00074, "When Morphs Look Better: Face Image Quality as a Training-Free Signal for Morphing Attack
  Detection": authors Hao Peng, Fu Bo, Mahmoud Elshirbeny, Guray Ozgur (TU Darmstadt and Fraunhofer IGD); page
  header "15 Oct 2026". 17 face-image-quality methods as training-free scores, direction fixed in advance,
  threshold at 20% genuine error (BSCER); metrics D-EER, MACER and a signed separation. FRLL: 204 genuine images
  from MAD22 plus 1,000 morphs per technique, eight attack sets (FaceMorpher, OpenCV, WebMorph, MIPGAN-I and II,
  DCMorph, MorDIFF, Arc2Morph). FEI: 200 genuine images and 12 techniques from FEI-Morph V3 (8,000 landmark or
  commercial morphs, about 4,000 generative). Best on FRLL: DifFIQA(R), mean D-EER 11.42%, mean MACER 10.75%;
  then CLIB-FIQA 16.99%, eDifFIQA(L) 24.34%. Best on FEI: 39.75% (ViT-FIQA(T)). Up to 11 of 17 methods rate
  diffusion morphs above genuine images; GraFIQs(L) detects DCMorph and Arc2Morph well on FRLL but not landmark
  morphs. (`03` C3 has only "11.4% FRLL, about 40% FEI".)
- arXiv 2602.15461 (Ivanovska and Štruc): submitted 17 Feb 2026, under review at Pattern Recognition Letters; best
  model LLaVA1.6-Mistral-7B; code promised on publication.
- arXiv 2605.10334 (Yermakov, Cech, Fritz, Matas, "The Alpha Blending Hypothesis"): v1 11 May 2026, v2 of 4 Nov
  2026 is the withdrawal; the BlenD detector was trained on real images plus self-blended images; best average
  cross-dataset generalisation on 15 compositional deepfake datasets (2019 to 2025); an ensemble with
  blending-resistant models reached AUROC 94.0%; training reals from ScaleDF overlapped test sets.
- arXiv 2504.05504 (SelfMAD), as read by the agent: trains **only on the 25,000 genuine images of the SMDD
  training split**; Dlib detection, random crop margin 4 to 20%, 384 × 384. Pseudo-morphs: RGB shift,
  hue / saturation, brightness / contrast, downscaling or sharpening (kept genuine); pixel artefacts by blending
  the geometrically altered copy with the original, mask full-face or SegFormer face parts, blending factor drawn
  from {0.5, 0.5, 0.5, 0.375, 0.25, 0.125}; frequency artefacts by mixing the FFT magnitude with a random pattern.
  Labels: original and augmented = genuine, pixel-blended and frequency-manipulated = attack. Test faces: Dlib,
  fixed 12.5% margin. Test sets: FRGC-, FERET- and FRLL-Morphs (AMSL, FaceMorpher, OpenCV, WebMorph, StyleGAN2),
  Morph-PIPE, Greedy-DiM, MorCode. No JPEG, resolution or matched-control discussion.
  **Conflict:** `11_AUDIT_PLAN.md` section (b) says "SelfMAD is not SMDD-trained". By this paper both of SelfMAD's
  training classes are StyleGAN renders from SMDD (genuine renders and their self-blends). What the released
  checkpoint was trained on is not stated in its README (section 4), so for the release it is not verified. Our
  own-crop scorer uses a landmark box plus 6.25% margin (`10` section A.2) against the paper's 12.5% test margin
  (possibly per side against total; not verified).

---

## 4. Web search for detector releases (agent a390f2ea6518de9c1, helper of agent 8)

**Task.** Web search only: for 15 S-MAD methods, find whether weights and code are public, where, under which
licence, trained on which data, with which preprocessing, each marked checked or not found. Report a compact
table under 900 words.

**Recorded in.** `10_ASSET_INVENTORY.md`, section A.1 ("Published releases"): repository URLs, weights yes / no,
code, licence, status, and the line "Released weights exist for MixFaceNet-MAD, SPL-MAD, MADation and SelfMAD".
`NOTEBOOK.md`, "Facts to work from", repeats the summary.

**Not recorded elsewhere** (the agent read README pages through the fetch tool; it did not open LICENSE files or the
Drive links):
- MixFaceNet-MAD weights: Google Drive file https://drive.google.com/file/d/1qw6YZ3cpaa9UK2-hRfzKWx5rPvRo0h63/view,
  behind a request form (name, affiliation, official email). Terms: CC BY-NC-SA 4.0, research only, no
  competitions or product development; derivatives of the data and morphs must be made public. Code: `main.py`,
  `image_preprocess.py` (face detection and crop; detector and size not stated), `backbones/`. Trained on the SMDD
  training split.
- SPL-MAD weights: Google Drive file https://drive.google.com/file/d/1kFLp1dWp_sBwC-l-RTVo-LRitKSYxbyv/view
  (`casia_smdd.pth`), no request form mentioned; preprocessing would be in `dataset.py`.
- MADation weights: Google Drive folder https://drive.google.com/drive/folders/1FAZKgy7Bu_MLJh7UIQFtoMUR0aARUP8v,
  with training logs, behind a request form; code `src/config.py`, `train.sh`. The README does not say whether the
  folder holds ViT-B/16 or ViT-L/14, or the training data (SYN-MAD 2022 protocol implies SMDD; unconfirmed on the
  web page; `10` A.2 later confirmed SMDD in the local `src/config.py`).
- SelfMAD: weights on a university SharePoint, not GitHub releases; checkpoints for HRNet-W18 (the paper's model),
  EfficientNet-B4, EfficientNet-B7, Swin-base and ResNet-152. The README documents data layouts for FF++, SMDD,
  FRLL, FRGC and FERET, training paths in `data_config.json`, landmarks via `preprocessing/dlib_lm.py`, and does not
  say which dataset the released weights were trained on.
- PW-MAD: arXiv 2108.10291, DenseNet-121; the LMA-DRD dataset is on request; no code or weights.
- Inception-MAD: the SYN-MAD 2022 participant methods are in the IJCB 2022 summary paper, arXiv 2208.07337 (not
  read in full).
- MorphHRNet: nothing found; SelfMAD's released HRNet-W18 is a different HRNet-based detector.
- OrthoMAD: the example command uses `morgan_lma_train.csv`; the code extends the SMDD repository.
- IDistill: EUSIPCO 2023 and arXiv 2306.03002 are the same work.
- MorDeephy: ICPRAM 2023 (Medvedev); SOTAVerified lists no code.
- MADPromptS: arXiv 2508.08939; repository includes `src/`, `test_clip.sh` and an explainability notebook;
  licence CC BY-NC 4.0 (Fraunhofer IGD, 2025); evaluates on MAD22 and MorDIFF.
- FD-MAD: Paulo, Proença, Neves, arXiv 2601.20656, January 2026; per the paper trained on SMDD only and tested on
  FRLL-Morph and MAD22. SRL-MAD: Paulo, Proença, Neves, arXiv 2603.15050, "Structured Residual Latents for
  One-Class MAD", March 2026, one-class. R-FLoRA: Ramachandra, arXiv 2604.17321, "Residual-Statistic-Gated LoRA",
  TIFS 2026, frozen CLIP ViT-L/14. For all three only the abstract pages were checked; suggested next step: PDF
  footnotes, authors' GitHub pages, or email.
- MorDIFF repository: a morph-generation script plus a data request form. Greedy-DiM dataset:
  https://huggingface.co/datasets/zblasingame/DiM-FRLL-Morphs (CC BY-SA 4.0); the Greedy-DiM repository itself was
  not opened.

---

## 5. Pre-run review of the sprint plan (agent abddeb219d2e716de)

**Task.** Review, before anything was launched, the four-day sprint in `/home/narolski/smad-next`
(`11_AUDIT_PLAN.md` with the three-number test, `04`, `05`, `06`, `WORKFLOW.md`), against the author's constraints
and goals (a) diffusion shortcut beyond SelfMAD, (b) causal GAN tests, (c) a definitive landmark answer. Return
GO / GO WITH FIXES / STOP with ranked findings and fixes worded for pasting.

**Verdict.** GO WITH FIXES (F1 to F6). Full report:
`/home/narolski/smad-next/experiments/reviews/PRERUN_SPRINT_PLAN_20261111.md` (new; verbatim).

**How the findings were applied** (checked against the current files):

| Review item | Applied | Where |
|---|---|---|
| F1 / B1: two-sided rules, reproduction gate G-a, twin-validity gate, folded AUC, share rule with person bootstrap, BPCER with exact interval, "twice the camera rate" deleted | yes | `11`: "Gates before any verdict", "Verdict rules, fixed here" |
| F2 / B2: composition rule (FRGC / colorFERET primary, FRLL secondary, bridge number, every B hosts a twin) | yes | `11`: "Composition rule for twins" |
| F3 / B3: five-rung ladder with named steps | yes, later amended (R2 degenerate for landmark tools; R2w and R3m added) | `11`: "One ladder for every family", "Amendment, 11 Nov 15:40 CET" |
| F4 / B4: empirical null for the morph-free networks (AD4): 5 permuted-label seeds and one untrained network, 10-point margin, falsifier 3 of 5 | yes | `11` (a) AD4 reading; `04` A1 |
| F5 / B5: author ruling on warp paths; registration | ruling 2 (approved warp script, unchanged OpenCV and FaceMorpher, constant-colour blanking); ruling 5 (one page per experiment here, no ledger folders) | `11`: "Author rulings of 11 Nov (afternoon)" |
| F6 / M5: selection data separate from the final test, test scored once | yes | `05`: "Gates", test split |
| M1: manipulation check P1 and readability probe P2, negative control | yes, as G-b and G-c | `11` gates |
| M2: wording and the six conditions for (c) | yes | `11` (c) |
| M3: GAN note corrected; AG2 two-sided; R2 from the same MIPGAN optimiser with A = B; fixed iterations, loss and latent distance logged; AG4 trained on StyleGAN2, tested on MIPGAN-I | yes | `11` (b) |
| M3: AG4 also needs the B4 null and its own twin test near 0.5 | no | not written |
| M4: ±0.08 intervals, post hoc labels, Holm over 12 primary cells, two-way person bootstrap, gate 0 advisory | yes | `11` verdict rules; `05` gates |
| M5: tiers (lower bound 0.55; AUC 0.80 with BPCER at 10% APCER), thumbnail as decomposition, G2 on the score, M5 descriptive, G1 pass rule, third landmark tool | yes | `04` M1, M5, G1, G2; `05` TwinSet table |
| M6: operations | partly (`06`: 357 GB free, x86 MIPGAN build needed) | `06` "Other needs" |
| Improvements: re-read A43 for AD1, zero-step networks, cut order | yes | `11` (a) AD1 and "Order and cuts" |
| Paste text "Open 4": one PROTOCOL block "A51 smad-next" with the commit and prereg hashes | no | `PROTOCOL.md` in mambamorph-code contains no "smad-next" or "A51" (grep, 11 Nov evening) |

**Not recorded elsewhere.**
- Why the label-permuted control of A47 (I-4) failed, and why "permute within source" would not repair it:
  I-4 already permuted labels uniformly over all 40,000 SMDD rows (PROTOCOL l.19251, l.19425). A network that
  memorises random labels is an arbitrary function and lands off 0.5 per seed on cells whose classes differ
  grossly; M3 was off in the same direction in both seeds (dim_a EER 35.25 to 37.77), pointing to the CLIP prior
  (A44 H-new-282: frozen CLIP separates renders from camera at 0.922); the deciding checkpoint was `es.pt`,
  selected on correctly labelled validation data; the gate used a person bootstrap with n = 2 seeds. The A47
  review says "Randomized labels do not guarantee a chance-level trained model".
- Examples that broke the first verdict rules: SelfMAD on two- against one-identity DiffAE mixes scored 0.290
  (own preprocessing 0.252), strong reversed separation; with 102 twins the EER standard error is about 3 to 5
  points, and "twice the camera rate" at a 1% threshold means at most 2 of 102 twins.
- For the MADation ViT-B/16 release against the reference pool E (`D20_vs_E`, `C20_vs_E`), reconstructions score
  0.930 and same-person mixes 0.731, so the twins are not on a monotone ladder.
- Earlier precedent for the positive-control problem: in A46 the identity oracle passed (H-new-317) while
  image-only probes failed (H-new-318); morphs verify against both contributors at FMR 1e-3 in 0.905 of cases on
  the H4 reference.
- File bytes alone gave 0.620 on H1 because averaging smooths texture; A27 point (5) calls these "attack
  properties, not pipeline asymmetries".
- The morph-free M3 recipe came out reversed on MIPGAN (EER 75.5); renders against camera 0.951 / 0.956 / 0.967.
- Thresholds set after the values were seen: 0.59 (StyleGAN3), 0.706 (A43), 0.724 / 0.745 (A46).
- Operations at 13:45: the DGX GPU was 96% busy; the root disk 97% full (33 GB free); `/mnt/t7/smad_next` did not
  exist yet; `/mnt/t7` had 356 GB free. No MIPGAN generation code was found under `smadcvpr/`. The only precedent
  for an author-approved warp build was A27 (`h1_build.py`, approved 3 Nov with "Tak, buduj.").
- The FRLL extracted folders: the reviewer counted 205 files in `neutral_front` and 103 in `smiling_front`.
  Counted again on 11 Nov evening: 102 images each; `neutral_front` also holds 102 `.tem` landmark files. The
  reviewer's counts included non-image files; there are 102 persons.
- At review time `11_AUDIT_PLAN.md`, `WORKFLOW.md` and `NOTEBOOK.md` were staged but not committed (one commit,
  `12848d2`), and `08`, `09`, `10` did not exist yet.
- Question 3 (does pre-registration here replace PROTOCOL and ledger registration) was answered only by ruling 5;
  question 6 (are the benchmark's own MIPGAN code and weights available on x86, or only the A33 re-implementation,
  StyleGAN v1, 326 pairs) was answered in practice by AG1 using the H4 re-implementation.

---

## 6. Cue matrix from the record (agent a6ca26fd0d48da3cf)

**Task.** Build a matrix of every candidate benchmark cue: in which benchmark cells it is present (with the
measured separability), whether detector use was tested by an intervention on that cue alone, a status, and the
experiment that would close it. List cue-related ledger experiments the dossier omits.

**Recorded in.** `/home/narolski/smad-next/08_CUE_MATRIX.md`, written by the agent (23 rows, 19 cues, notes, status
summary, omitted experiments, "not verified"). The lead later added a dated update list at the top (15 lines) and
removed nothing (checked against the 14:02 copy). The final report's status summary (6 used, 5 not used, 8
present with use untested, 1 absent, 4 unknown) and top open cues match the file's "Status summary".

**Not recorded elsewhere.**
- The agent's open item "whether the zero alignment borders come from the morph tools or from our frame padding"
  (`08`, "Not verified in this session") has since been answered by the independent review of the
  fixed-threshold re-read (EV1): our own alignment leaves the border around smaller morph files (`NOTEBOOK.md`, EV1
  row and 17:15 log line). `08` row 7 and its update list do not say so yet.

---

## 7. Dataset-extension coverage analysis (agent a4b2797a30db79a2e)

**Task.** Answer the author's question whether the planned experiments cover the effect of dataset extension on
generalisation and on cue use: table every past data-extension experiment, say what is established, null or
untested, check the plan's coverage, and propose the minimum additions, preferring re-scoring of existing fits.

**Recorded in.** `/home/narolski/smad-next/09_DATASET_EXTENSION_ANALYSIS.md`, written by the agent, unchanged since.
The derived reading (photos cut the diffusion E7 rise by 13 to 29 points; classical morphs give 9 to 22 back; not
reproduced in Inception's recipe) is in section 2.2 with the diffusion-rise table; the proposals became X0 to X5 in
`NOTEBOOK.md`.

**Not recorded elsewhere.**
- The full derived tables behind section 2.2 (per-arm native and E7 errors, landmark and diffusion contrasts with
  intervals, Q, H2, H3 and X3 columns, and the A12 checkpoint triplets at both checkpoints): Appendix A below.
  Notable there and not in `09`: in all four architectures, adding genuine photos (arm B) lowers the X3:self AUC
  sharply (ConvNeXt-T 0.946 to 0.376, VMamba-T 0.746 to 0.598, DeiT-S 0.720 to 0.528, DINOv3 0.534 to 0.350);
  arm C returns it (0.905, 0.899, 0.796, 0.332). E7 and native errors on the three GAN cells are identical in every
  arm, because the E7 copies are byte-identical there (also stated in `experiments/AD4/result.md`).
- The scripts and the data copy exist only in the session scratchpad:
  `/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/abc_sum.py`,
  `.../scratchpad/abc_rise.py`, `.../scratchpad/a12_rise.py` (run as `a12_rise.py es` and `a12_rise.py last` from
  `/home/narolski/mambamorph-code` with `.venv-spark/bin/python -I`), and `.../scratchpad/abc60.json` (1,848,037
  bytes), extracted in `/home/narolski/mambamorph-code` with
  `git show recovery/final-gpu-boundary-v1:experiments/primary120fit/recovery_v1/final_gpu_v1/analysis_ABC60_20261110_v1/ABC60_FROZEN_ANALYSIS.json`.
  `09` names `abc_rise.py` and `a12_rise.py` and asks to rerun them before registering X0.
- Manifest facts from the agent's checks: `smadcvpr_data/manifests/train.csv` has 29,882 "faithful" and 40,000
  "smdd" rows and no Multi-PIE or CASIA row; `eval.csv` and `gtest.csv` have no Multi-PIE row (supports `09`'s
  statement that CASIA and Multi-PIE are untrained sources).

---

## 8. Inventory of detectors, corrected MAD22 and generators (agent a8f961816f943fb23)

**Task.** Produce `10_ASSET_INVENTORY.md`: published releases and local copies of every S-MAD detector with
reproduction status and input pipeline; where the corrected MAD22 is and what a new experiment must point at;
generators and matched sets usable for one-identity controls; genuine-photo pools with two or more photos per
person and their identity-overlap risk.

**Recorded in.** `/home/narolski/smad-next/10_ASSET_INVENTORY.md`, written by the agent, unchanged since. Its
final report (auditable releases; the corrected MAD22 pointer and counts; "do not use" paths; blockers: no score on
the corrected MAD22, R8 twins in `/dev/shm`, no held-out FERET / FRGC identities except sealed val10, DiffAE runs
on the GB10, StyleGAN3 inversion only on x86) is in sections A to D and "Blockers found"; `NOTEBOOK.md` "Facts to
work from" and `06` repeat it. The R8 set and the corrected-MAD22 manifest were later copied to
`/mnt/t7/smad_next/volatile_backup_20261111/` (`NOTEBOOK.md`).

**Not recorded elsewhere** (from the agent's tool results):
- FRGC 2.0 stills per session: Fall2002 3,952 JPG / 193 subjects; Fall2003 11,358 / 370; Spring2003 11,334 / 285;
  Spring2004 12,684 / 345 (total 568 subjects, 39,328 images, all with two or more). The BEE metadata file
  `/mnt/t7/Datasety/FRGC-2.0/BEE_DIST/FRGC2.0/metadata/FRGC_2.0_Metadata.xml` gives per recording the subject, a
  capture date and eye, nose and mouth coordinates (useful for session matching; AG1 later used capture dates).
- Corrected-MAD22 acquisition receipt
  (`/mnt/t7/smad_heldout/mad22_incoming/marco_owncloud_20261109T103840Z/RECEIPT.md`): 4,693 author files,
  2,888,156,134 bytes; download 10:38:40 to 10:48:41 UTC, verification done 10:49:43 UTC on 9 Nov. Provenance: the
  dataset author's statement, relayed by the user, that a Google update removed access for some users and that he
  re-uploaded the complete files; the cause was not independently validated. Share link: [stored outside the
  repository].
- The five duplicate-hash groups in the corrected Webmorph folder: 021_03-vs-029_03 = 021_03-vs-037_03;
  022_03-vs-123_03 = 022_03-vs-173_03; 062_03-vs-066_03 = 062_03-vs-099_03; 066_03-vs-129_03 = 081_03-vs-087_03;
  130_03-vs-131_03 = 130_03-vs-138_03 (`old_comparison.json`). `10` names only the first.
- Input admission of the canonical E7 inputs (`input_admission.json`): every family attempted = aligned =
  retained (204 / 1,000 / 1,000 / 999 / 984 / 500, and 204 per E7 family); no failures; 0 GPU allocations.
- The A41 X3 DiffAE generation ran with Python 3.12 on aarch64, CUDA 13.0, device NVIDIA GB10 (`x3_gen.log`). The
  H4 MIPGAN input preparation logged `elapsed_s` 271.

---

## 9. Arrangement of prior experiments in narolski/s-mad (agent a28c7df2c4d1e1147)

**Task.** In a clone of narolski/s-mad (branch `prior-work` from `origin/sprint-plan-v2`), rewrite `prior/INDEX.md`
as a themed table, write a summary page per experiment from A32 on (plus E07, A49, A50, ABC60), a verbatim snapshot
of the committed `CONCLUSIONS.md`, a list of loose documents and a list of data locations. Commit in small steps
and push the branch.

**What it produced.** Branch `prior-work`, four commits, no trailers, pushed: local and remote-tracking refs in the
clone both read `b7013d4beec5a65b96220d9ce4385fbdac2ed97c`, with "update by push" entries. Files under `prior/`:
- `INDEX.md`: 167 lines, seven themed tables, about 90 rows, glossary and status legend; stale entries corrected
  from the independent reviews and `CONCLUSIONS.md` (A45 and A47 finished; A44 and A46 partial).
- `summaries/`: 18 files of about 10 lines: E07, A32-RSX, A36 to A47, A49, A50, ABC60 and A138 (A138 beyond the
  request).
- `CONCLUSIONS_snapshot.md`: verbatim from `git show HEAD`, commit `0386400` (138,218 bytes); later uncommitted
  edits not included.
- `LOOSE_DOCUMENTS.md`: about 45 files plus folders. `DATA_LOCATIONS.md`: one-level listings of
  `/mnt/t7/smad_heldout`, `/mnt/t7/smad_research`, `/mnt/t7/wcss_backups`, `/mnt/t7/smad_next` (sizes not measured,
  `du` timed out).

**Recorded in.** Nowhere in the working tree. `/home/narolski/smad-next` has fetched the branch
(`.git/refs/remotes/origin/prior-work` = `b7013d4`) but not merged it: `prior/` on the working tree holds only the
older `INDEX.md` (132 lines, "generated from meta.json at commit 1714b11", with A44, A45, A46 and A47 still
"running" and no rows for A49, A50 or ABC60), and `README.md` points readers to that older file. A second copy of
the branch files is in the session scratchpad clone
(`/tmp/claude-1000/-home-narolski-mambamorph/c2840dc9-dd37-4619-9347-d8a76080b93f/scratchpad/smad_prior/s-mad/prior/`).

**Not recorded elsewhere.**
- The whole content above (to be merged; nothing needs rewriting).
- The agent's "not verified" list: A8-W0 and the A12-SP folder not opened (name filter; the old index headline is
  quoted for A8-W0); no A139 result found; A138 only timing pilots; ABC60 VMamba and DeiT expansions unconfirmed;
  A49 arm P2 undescribed; A44 LoRA-removal tests without recorded result; A45 numbers from the independent review,
  `a45_read.md` not opened; A46 N1 to N3 definitions not checked in PROTOCOL; contents of `r8_cv` and `r8_fm`
  unknown; checkpoint-to-folder mapping not checked; PROTOCOL grepped only for ABC60 and A138 headers.
- A correction for the branch's `INDEX.md`: it says "The ledger entry of A16 and A20 says 'registered'; no result
  exists for either". For the frozen-CLIP readout ladder (A20) a final read exists in PROTOCOL l.7313 to 7332 (35
  fits; registered verdict "not success"), as the vetting round's record check found (section 14.2); only its ledger
  README is stale. A16 was not re-checked.

---

## 10. Prior-art sweep of morph detection ideas (agent a20a8d98e619e6803, helper of agent 11)

**Task.** Web search only: for eight candidate ideas (facial asymmetry, mirror self-morph control, pipeline-matched
genuine images, averageness and limits, a 112-pixel face-recognition backbone, test-time equalisation, a reference
network that never saw the class, recent S-MAD comparators) find the closest published work and say whether the
idea exists in MAD, only in neighbouring fields, or appears new, marking every citation checked, snippet or memory.

**Recorded in.** `ideas/IDEAS_v1.md`: the verdicts are folded into the idea entries and summarised in "Appendix:
prior-art sweep of 11 Nov"; some numbers are in the entries (11.42 / 39.75 for arXiv 2611.00074; 92.70% for the
vegetables paper; 3.7% for arXiv 2608.29802).

**Not recorded elsewhere** (marks as the agent gave them; PDF fetches returned binary, so no full PDFs were read):
- Asymmetry: Ivanovska and Štruc, arXiv 2602.15461 (checked, HTML): LLM explanations cite "symmetric features"
  for genuine images and "distorted facial symmetry" for morphs; average EER 2.75% over FRLL-Morphs, MIPGAN-II,
  MorDIFF, Morph-PIPE and Greedy-DiM. Li, Cao, Zhao, "Exploiting Facial Symmetry to Expose Deepfakes", ICIP 2021
  (snippet), with a TIFS follow-up mentioned (title unconfirmed). Rhodes, Sumich and Byatt 1999, Psychological
  Science 10(1):52-58 (snippet): averaged composites are highly symmetric. Langlois and Roggman 1990; Grammer and
  Thornhill 1994, J. Comp. Psych. (snippets).
- Self-morph negatives: Kashiani et al., IJCB 2023, arXiv 2308.10392 (checked), "self-morphing" augmentation,
  label not stated in the abstract. Shiohara and Yamasaki, SBI, CVPR 2022, arXiv 2204.08376 (snippet): self-blends
  as fakes.
- Pipeline-matched genuine images: SMDD, arXiv 2203.06691 (checked, ar5iv): genuine images are never morphed; only
  morphs were filtered for artefacts; it reports much lower error on its own test set than on others. FD-MAD,
  arXiv 2601.20656 (checked): SMDD-trained models depend strongly on "texture statistics of the training dataset".
  Grommelt et al., "Fake or JPEG?", ECCV Workshops 2024. Chen et al., Dual Data Alignment, NeurIPS 2025 spotlight.
- Averageness and quality: Fu and Damer, IET Biometrics, arXiv 2208.05864 (checked): MagFace and CNNNIQA give
  over 70% accuracy for unsupervised detection. Scherhag et al., "Detecting morphed face images using facial
  landmarks", ICISP 2018, pp. 444-452 (snippet): differential, not single-image; error rates not retrieved.
  Scherhag, Rathgeb, Busch, "Morph detection from single face images: multi-algorithm fusion", ICBEA 2018
  (snippet): D-EER 2.8% fused, 5.5% best single. Zhang et al. 2020, "Detecting Morphing Attacks through Face
  Geometry Features" (snippet). No 3D-morphable-model S-MAD and no impossibility argument found.
- Face-recognition features: Colbois and Marcel, IJCB 2024, arXiv 2410.16802 (checked): frozen DINOv2, DNADet,
  CLIP and AIM features with a linear SVM or GMM; DNADet reportedly under 1% D-EER in one-class digital settings
  (snippet, unverified). Scherhag et al., TIFS 2020, arXiv 2001.01202 (snippet): differential, D-EER below 3%.
  Kessler et al., arXiv 2305.18216 (checked): ArcFace and MagFace for pair selection and differential MAD.
  Shahreza et al., arXiv 2608.29802 (checked): 30 vision encoders; CLIP ViT-L/14 with LoRA 3.7% overall ACER,
  SelfMAD 11.3%.
- Test-time equalisation: Zhang et al. 2501.09817 applies the same print-scan and ≤ 15 KB compression to both
  classes at dataset level; NIST IFPC 2025 slides on compression effects (snippet); Stay-Positive (Rajan and Lee,
  ICML 2025, arXiv 2502.07778, checked); "A Sanity Check for AI-generated Image Detection" (Yan et al., ICLR 2025,
  arXiv 2406.19435, snippet).
- Never-saw-the-class references: Ozgur, Boutros, Damer, "Tomatoes, Potatoes, and Onions", arXiv 2608.21455, ACM
  MM 2026 workshops (checked). Smeu et al., CVPR 2025, arXiv 2412.00175 (checked): leading silence alone separates
  real from fake in two audio-visual deepfake datasets; AVH-Align trained on real data only. Poliak et al. 2018,
  Gururangan et al. 2018 (snippet).
- Comparator numbers: FD-MAD (checked): FRLL-Morph average EER 1.85%, MAD22 average 6.12% (MorDIFF excluded);
  per-attack MorDIFF EER 0.00% FD-MAD, 1.10% MADation ViT-B, 5.30% Inception-MAD; its tables give MADation ViT-B
  5.76% on FRLL and 14.05% on MAD22. SRL-MAD at IWBF 2026, one-class, tested on FERET-Morph, FRLL-Morph and MorDIFF.
  R-FLoRA claims to beat nine S-MAD methods on four datasets; the 4.00% D-EER figure is from a secondary summary
  only. SelfMAD: "EER 64-66% lower than the best competitors", no absolute numbers retrieved. Greedy-DiM, Blasingame
  and Liu, IJCB 2024, arXiv 2404.06025 (snippet).
- NIST FATE MORPH (snippet): last page update 2026-01-09 (secunet-004); NISTIR 8584 (August 2025); a
  press-reported figure that single-image detection falls below 40% on unseen generators.
- Audits and demorphing: IJCB 2026 tutorial slides by Ivanovska mention dataset, attack and quality bias (snippet);
  Shukla and Ross, arXiv 2605.25442 (checked) demorphs, does not detect; SDeMorph, arXiv 2308.11442 (snippet).
- Searched for and not found: any MAD paper using bilateral asymmetry or flip consistency as a score; mirror
  self-morph negatives; explicit criticism of SMDD, FRLL-Morphs, SYN-MAD or MorDIFF for genuine-against-morph
  resolution, JPEG or crop differences; test-time equalisation in MAD; a blind reference baseline in MAD; any
  theoretical limit for S-MAD; 3D-morphable-model S-MAD; the Scherhag 2018 error rates; SelfMAD and Greedy-DiM
  absolute numbers; the ICIP 2021 abstract; verified metadata of the psychology papers.

---

## 11. Research strategist for S-MAD ideas (agent acf7970ed07505ca6)

**Task.** Generate new ideas for a detector that is state of the art and does not rely on benchmark shortcuts:
define "state of the art and shortcut-free" operationally, attack the current plan, give at least 12 ideas with
cheapest decisive tests and falsifiers, a ranked top five with a 72-hour order and a first experiment, what to drop,
and questions for the author.

**Recorded in.** `/home/narolski/smad-next/ideas/IDEAS_v1.md`, written by the agent (sections A to F, 16 ideas,
theory table, prior-art appendix), unchanged since 15:01. The first experiment became the clean-negative test (CN0)
and the mirror self-morph became rung R3m (`11`, amendment of 15:40); the strongest objection (R2 is the re-stored
photo) was confirmed by the lead's measurement (`11`, same amendment).

**Not recorded elsewhere** (its two web searches):
- No paper combines morph detection with invariant risk minimisation, group DRO or counterfactual environments for
  processing or compression shortcuts (2025 to 2026). Closest in a neighbouring field: a group-wise scaling risk
  minimisation objective (GS-RM) for domain-generalisable face anti-spoofing, ICCV 2025, arXiv 2507.04006 (search
  result, not opened).
- No work regresses the mixing factor from one image or studies how contributor similarity affects detectability;
  in demorphing the unknown morphing factor is a nuisance that "significantly influences performance", and its
  estimation is called ill-posed for a suspect image and a live capture, with Ferrara et al. named as addressing it
  (search result text only).

---

## 12. Pre-run review of the MIPGAN one-person controls (AG1) (agent aa7ebfd5a55401578)

**Task.** Review, before any image was generated, the GAN causal test batch (AG1 with AG2 and AG3): whether R2 =
MIPGAN with A = B is a fair processed genuine image, whether the composition rule is implemented, whether the
reader implements the registered rules, the dose definition, the twin-validity gate G-b, rule compliance and
operational risks.

**Verdict.** GO WITH FIXES. Full report: `/home/narolski/smad-next/experiments/reviews/PRERUN_AG1_20261111.md`
(new; verbatim).

**Recorded in.** `experiments/AG1/prereg.md`, "Pre-run review" and "Amendment 1" (both readings A and B registered;
"two photographs" wording; matched bins on non-identity terms, also reported only, with coverage rule and
interval; session-gap sensitivity; AG2 bridge gate; G-b on unseen photos, R2 false-match rate, failure labels,
honest negative control; cuDNN determinism and finiteness checks; dmenv fallback removed; RT extended to 152
persons; AG3 α = 0 through `mipgan_alpha`; twin-dose arm AG3T; primary pool pooled; distinct bootstrap seeds; FERET
decode fix; input alignment flagged), "Amendment 2" (mirror rung R3m, the reviewer's improvement 5; Athena as the
platform). `experiments/AG1/README.md` keeps the reviewer's padding counts, contributor cosines and session gaps.
Not fixed at the time: the MixFaceNet scorer.

**Not recorded elsewhere.**
- The sha256 prefixes on disk at review time, which the reviewer asked to pin: `ag1_gen.py` 375f5998…,
  `run.sh` 4222b7fc…, `ag1_code.tar` 53d4fe98…, `ag1_inputs.tar` f8a7bdb4…, `gan_weights.tar` e06f19af…,
  `gan_sg1.tar` 1571c1a3…, `pairs.csv` 19145659…, `shards.csv` 56aa2783… (amendment 2 later pins `shards.csv`
  a870e61c…). All five vendor files matched gan1 commit `24cc974`; `ag1_score.py` differed from `a43_score.py`
  (339533c4…) only in the docstring. `AG1/result.md` notes that the first runs used the code before the fixes
  (`ag1_gen` 375f5998…).
- Re-pairing by session was costly: FERET at ±30 days lowers the mean contributor cosine from 0.161 to 0.111;
  FRGC at ±60 days within gender is infeasible. Only 37 of 100 FERET and 35 of 100 FRGC morphs have the second
  photo within 60 days of the twin's second photo (the README's "about 72 of 200").
- AG3 dose: `mipgan_alpha(0.5)` equals `generate.mipgan` term by term (ag1_gen.py:166-174 against
  generate.py:136-143); the optimum satisfies dA/dB = α/(1−α); the α = 0 point (R2, ID-Diff ≡ 0) is not the limit
  α → 0 (the limit gives 12·dA instead of 10·dA); α also scales B's latent, perceptual and MS-SSIM targets.
- Costs of the proposed additions: α = 0 point about 10 GPU-minutes; twin-dose arm about 37 GPU-minutes;
  run-to-run noise floor about 20 GPU-minutes; GAN mirror twin about 1.7 H100-h. Time check for shard o02:
  130 × 23.3 s + 334 × 7.0 s = 89.5 minutes, estimated 129 against a 360-minute slot. A slot killed mid-task leaves
  its task in `claimed/`, to be re-queued unchanged.
- Smaller items: FRLL has 48 of 50 cycles as 2-cycles (about 50 dyads); the FRLL pairing uses s1-s1 cosine
  (build_inputs.py:265); FERET and FRGC had identical bootstrap weight matrices (same seed, n = 100); `frame()`
  returns None for existing frames, so the aligned flag is wrong on re-runs; maximum cross-pool w600k cosine 0.331
  (pools identity-disjoint).
- Author questions not answered in the AG1 files: which SelfMAD row is primary (pipeline or own crop), and is
  ViT-B/16 the only deciding release; were the canonical v3 MAD22 frames made by `prep_eval.align` with the CPU
  detector, as AG1's will be.

---

## 13. Pre-run review of the SMDD five-partner audit and rebuild (SM1) (agent a2cfd6de5170bc99a)

**Task.** Review the SM1 pre-registration: whether the partner-memorisation test (500 unused-render keys × 5
trained against 5 matched unused partners, paired logit gap, key bootstrap) can detect memorisation, whether the
rebuild arms isolate what they claim, whether the verbatim falsifiers are applied correctly, and any rule violation.

**Verdict.** GO WITH FIXES (1 blocker, 4 majors, minors). Full report:
`/home/narolski/smad-next/experiments/reviews/PRERUN_SM1_20261111.md` (new; verbatim).

**Recorded in.** `experiments/SM1_smdd-partner-audit-and-rebuild/prereg.md`, "Pre-run review" and "Amendment A1"
(all ten items registered at 16:10 CET, before the smoke pass: placebo-partner permutation test with sign-flip and
two-way bootstrap, difference-in-differences with arm (b) as positive control; SMDD-T mapping; mandatory (c′), new
(b′) and the pool-cue check; responsiveness gate at 0.70; extra flag-rate readings; matching on inter-ocular
distance and yaw; training-pair bootstrap; a256 row; scorer diff; operations). Both author questions are at
prereg l.291.

**Not recorded elsewhere.**
- The reviewer's sizing of the original test: with 500 keys the key-bootstrap interval is about ±0.05 logit, far
  below the detectors' per-partner variation, so under no memorisation the five trained partners come out higher
  about half the time, with the error shared by all five detectors.
- It checked the verbatim falsifiers with a whitespace-normalised substring test against `ROUND1_raw.json` (both
  True), and asked that line 4 of the prereg not say SM1 "implements" SMDD-X. Line 4 still says "Implements ideas
  ... ("SMDD-T") and pragmatist/ideas[2] ("SMDD-X")"; line 6 adds "SMDD-X is implemented only in part".

---

## 14. Workflow agents: what the condensed files drop

Raw outputs are in the repository: `ideas/ROUND1_raw.json`, `ideas/ROUND2_vetting_raw.json`,
`literature/class_definition_check_raw.json`. Only findings that matter and are missing from the condensed files
are listed; ideas that were not consolidated remain readable in the raw files.

### 14.1 Ideation round 1 (`ROUND1_raw.json`, seven lenses, 48 ideas) against `ideas/CONSOLIDATED_v1.md`

Facts and objections dropped (lens in brackets):
- (pragmatist) Codex heads already show in-generator success, DiffAE morph against reconstruction 0.947 with 74
  pairs, next to the cross-generator reversal (0.26 to 0.32); a "known generator" tier should be declared, or the
  generator half yields nothing. `12` has only the reversal.
- (pragmatist, physics) Measured build speeds: OpenCV tool 2,008 images per minute; FaceMorpher paths 334 to 455
  per minute; one code path 432 per minute; R2b at 1,841 per minute; StyleGAN3 inversion 63 s, DiffAE encode 13 s,
  one MIPGAN pair 994 s on the shared GB10; the GB10 at 94% utilisation with six processes at 15:02; feature
  storage about 0.5 MB per image for fp16 patch tokens, 0.4 GB per 100,000 images for CLS plus mean patch; 304 GB
  free on `/mnt/t7`. Also: score the corrected MAD22 locally on the 5,707 canonical512 PNGs in minutes instead of
  waiting for job 6299123.
- (pragmatist, adjacent) Input scale is untested: CLIP at 224 shrinks the 512 frames 2.3 times and discards the top
  56% of the band (AMSL 14.7 to 17.7%); a 224 / 336 / native-crop comparison was proposed (adopt 336 only for a
  gain of 0.03 AUC or more).
- (adjacent) Blend physics: the high-frequency energy of a blend is 1 − 2a(1−a)(1−ρ) of the source energy, so 84%
  of the full effect is reached at mixing 0.3; a flat dose curve between 0.3 and 0.5 is legitimate and must not be
  read as a pipeline cue. This bears on the dose readings of AR2, AG3 and hypothesis M6 ("a jump at the first
  step means a pipeline cue").
- (adjacent) A44: the same recipe is at 34.7% MorDIFF EER at the early checkpoint and 4.4% at the last, with the
  E7 rise appearing in between; training length should be fixed by a shortcut metric on non-FRLL data.
- (adjacent) Related work missing from the plan's comparison set: SelfMAD++ (Information Fusion 2026), the
  PADLLM / MADLLM study (August 2026; LoRA CLIP ViT-L/14 as a strong baseline over 30 encoders), R-FLoRA (TIFS
  2026), NIST FATE MORPH (September 2026).
- (physics) Spread-matched renders used as a verdict-bearing R2 in the StyleGAN3 re-read (AG5) are
  identity-diluted, in effect a morph with the mean face, so they remove the only signal an ideal latent morph
  leaves.
- (physics) File-size floors on same-generator, same-size, lossless comparisons (H4b 0.912, H1 0.62 to 0.68)
  measure the texture energy that morphing removes: a mediator of the morph effect, not a construction cue; the
  right control is a blur-matched one-capture negative.
- (physics) The most promising positive number in the record was filed as a negative: the A46 d2 CLIP ViT-L/14
  probe separates our diffusion morphs from reconstructions at 0.993 held out and published DiM families at 0.81 to
  0.95, with the E7 control at 0.48; it was filed "not readable" because one control's bound exceeded 0.60.
  (The frozen-features experiment FZ1 has since re-measured such probes, for example B vs D 0.995 in
  `experiments/FZ1/result.md`; the A46 d2 numbers themselves and the question "what does it read" are not in the
  consolidation.)
- (physics) A DiffAE reconstruction with its own inverted noise code is a near-exact copy, so R2 is degenerate for
  diffusion autoencoders too; a same-person latent mix is another valid render of the same person and cannot be
  detected in principle (a stated limit, not a hypothesis).
- (physics) The mirror self-morph (R3m) is, in identity and lighting terms, a different face (asymmetry and light
  direction flip) and should behave like a look-alike morph, not a one-person negative.
- (physics) Guard G1 matches only landmark distance; hair, collar and lighting mismatch drive ghost energy in the
  periphery, so a periphery-blanked read is needed.
- (invariance) The twin contrast R3 against R4 is confounded with warp size: in the Codex loop rendering geometry
  alone predicted the class at AUC 0.81 pooled and 0.92 on FERET, and its three post hoc fixes failed; a design
  that crosses or matches geometry costs CPU minutes.
- (invariance) For GAN morphs latent averageness alone separates H3 at AUC 1.000 and a linear probe reads it at
  0.91, while the cue matrix lists averageness as a cue (row 18): the plan must say whether averageness is the
  legitimate signal or a shortcut.
- (invariance) Gate G-c is biased toward "not readable": `gate_c.py` groups folds by host only, so the partner photo
  of a test morph can be a training twin with label 0; with 1,024 features and about 850 training images the probe
  can fit photo-specific directions. Folds must hold out both persons of every morph.
- (identity) The two-contributor head (T5) had already failed twice: the summer demorph head S8 (divergence-only
  EER 0.63 to 0.74 on FRLL) and the reference-free demorpher (0.00 to 0.27% strict recovery against 97 to 99% for
  the oracle). `CONSOLIDATED_v1` drops T5 without this reason.
- (identity) The 0.75 "reads morphing" bar is probably above the identity ceiling on generator cells at benchmark
  pair similarity (estimate 0.65 to 0.78 for the AR1 median pair, 0.59 to 0.67 for strong look-alikes); state bars
  as a fraction of the measured ceiling.
- (identity) In AR1 twins and morphs differ in source cosine (0.87 against 0.23) and everything that travels with
  it (ghost size, pose and shape gap).
- (identity) T3 pools three different things: face-recognition feature norm (a quality measure, so a history cue),
  the CLIP typicality direction (truncated renders separable by simple image properties at 0.96, A37) and the
  identity direction; only the last is identity. Threat model: an attacker who restores the code length keeps
  both matches and removes typicality, so any typicality result holds for naive morphs only.
- (identity) Report verdicts on potent morphs only (both contributors verified at FMR 1e-3 with photos not used in
  the build), since the StyleGAN3 set verifies at 48% and the public StyleGAN family reportedly below threshold.
- (evaluation) The reproduction gate failed for every MorDIFF ladder row: ViT-B/16 5.4% against 1.10 published,
  ViT-L/14 26.0 against 19.3, and SelfMAD has no published MorDIFF number. Dropped from both consolidations
  (`CONSOLIDATED_v2` keeps only the AMSL gap), but recorded in `experiments/AD1/result.md` (reproduction gate
  paragraph) and `experiments/AD1/README.md`.
- (data) 50,000 SMDD renders and 70,000 FFHQ persons are unused while the planned negatives have 536 hosts; the
  CASIA H1 set can be a second unseen-source twin test without any second photo.
- Ideas not taken into any theme (readable in the raw file): leaderboard rank predicted from genuine photos alone
  over about 295 networks (evaluation); null-space surgery of history directions (pragmatist); a mixing-direction
  test across families; shape-by-texture factorial; "cue spectrometer"; regeneration evidence with two reporting
  protocols (adjacent); history-null constrained adaptation with a shortcut-validated stopping rule; local
  evidence at native scale; spectral crossover map; virtual morphs in feature space; stationarity-cancelling
  features; disagreement-region test; code-crossed latent mixes (data); region-partial morphs; counterfactual-pair
  erasure; common-sign direction; distilling the reference oracle; identity coherence in a face-recognition trunk;
  mosaic test; token-averaged twins; potency against detectability frontier.

### 14.2 Vetting round 2 (`ROUND2_vetting_raw.json`, seven agents) against `ideas/CONSOLIDATED_v2.md`

Entry order in the raw file: 0 SMDD novelty check, 1 area chair, 2 dense-map novelty check, 3 evaluation novelty
check, 4 record check, 5 morph detection community reviewer, 6 image forensics reviewer.

From the record check (entry 4), dropped:
- `NOTEBOOK.md` still says "No training change has removed a shortcut so far" (and `02` section 1 "A training
  change removes the shortcut: Not found"). The record check calls this false as written: in A22 (frequency stream
  with the same random resample / JPEG / blur chain on both classes, 24 runs) the different treatment of shrunk
  genuine photos disappeared (+14.5 to −0.2 points) at a cost of 5.1 points on the selection set (9.02 to 14.16);
  in A30 amendment 6 the same chain cut the share of shrunk FFHQ photos flagged from 19 to 40% to 4 to 8% in four
  pretrained backbones at a cost of 0.4 to 1.5 points (read from `CONCLUSIONS.md` only). A49's consistency loss
  gave no gain (+0.0029 [−0.0049, +0.0106]); the frequency stream (A18, A19, A26) helps only AMSL from scratch
  (+10.5 AUC) and costs MIPGAN-I (−11).
- The same-person training arm R8 (part of A8-W1F) is mis-cited in `IDEAS_v1.md` l.164-165: its 5,000 same-person
  morphs (1,013 persons) were labelled as attacks, not negatives. Held-out splice-tool error fell for VMamba-T
  (40.95 to 22.60) and ConvNeXt-T (41.02 to 32.39), not for MADMamba (43.26 to 46.16); all three failed guard G2
  (gaps +7.45, +6.33, −8.67); A9-W2R found +R8 worth −1.06 [−1.44, −0.60] and dropped it ("R8 adds warp history to
  the morph class only").
- The largest landmark lever in the record was self-blends with a face-hull mask: with source-matched negatives
  alone every network scored 37.41 to 52.47% on a held-out splice tool; with SBI 40.95 to 2.76 (VMamba-T), 41.02
  to 4.95 (ConvNeXt-T), 43.26 to 19.84 (MADMamba).
- History fragility of "one source, blended or not" detectors: SelfMAD release Greedy-DiM 8.4 to 90.7% under E7,
  AMSL 2.9 to 33.3, WebMorph 5.9 to 51.9; our SelfMAD-style retrain M4 MAD22 FaceMorpher 99.8 to 0.8 under E7 and
  FRLL AMSL / WebMorph 100% (inverted); the A8 audit: one sharpness number separates our FERET / FRGC landmark
  morphs from their sources at 0.70 to 0.78 and SMDD at 0.99 or more, 26 low-level numbers together 0.984; E7
  photos are much softer (Laplacian variance 175 to 16 on the MAD22 FaceMorpher pool, 182 to 51-70 on FRLL).
- The frozen-CLIP readout ladder (A20; 35 fits, 7 arms × 5 seeds, frozen CLIP ViT-B/16 at 224): a patch-token
  reader against a pooled linear probe: held-out splice 25.93 to 11.20%, held-out diffusion 7.35 to 27.39%,
  Greedy-DiM ranking reversed, false alarms on shrunk genuine photos at the 1% threshold 10.78 to 30.77%, FRLL AMSL
  35.6 against 11.2 for the MADation recipe; registered "not success" (PROTOCOL l.7313-7332; ledger README stale).
  Proposed reference for any dense head: at most 10.8% of shrunk genuine photos flagged at the 1% threshold.
- PW-MAD retrains (M5, 8 seeds, constant 14 × 14 map): under E7 FRLL 14.4 / 15.8 / 8.9 / 4.2 to 24.5 / 28.8 /
  25.7 / 14.3; MAD22 FaceMorpher 1.2 to 20.7; diffusion mean 28.0 to 49.5 (uncapped 72.3; Greedy-DiM 33.6 to 83.3);
  H1 0.533 / 0.547 below the file-size floor 0.620 / 0.681; StyleGAN3 0.564; training without our morphs broke it
  (MAD22 mean 52.4, above 50 in 4 of 5 seeds).
- Frozen-encoder evidence for: A44 with the LoRA update scaled to zero changes the E7 rise by −5.84 (upper bound
  −2.76) and keeps morph against reconstruction at 0.736; five frozen-CLIP probes 0.862, LoRA fits at the authors'
  learning rate 0.671, eight retrains 0.476; A46 D2 head on frozen CLIP ViT-L/14 (200 + 204 images) ranks four
  published diffusion families above reconstructions at 0.807 / 0.947 / 0.854 / 0.847, E7 0.481 (verdict "no" only
  because a resampling control read 0.597 against 0.60); A49 head-only 0.659 / 0.622 against adapted 0.447 / 0.112;
  A12-4 frozen CLIP 15.2% against LoRA 25.4% on held-out diffusion. Reuse `a46_feat.npz` (5,146 items) for FZ1.
- Frozen-encoder evidence against, beyond `CONSOLIDATED_v2`: FE ViT-L/14 under E7 4.4 / 4.9 / 23.0 / 10.3 against
  the adapted release's 1.0 / 1.0 / 14.7 / 4.4; our ViT-L/14 recipe retrains 0.4 / 0.3 / 15.0 / 7.8 to 0.4 / 0.3 /
  14.5 / 7.6; FE ViT-L/14 does not rank two-person diffusion morphs above same-person mixes (0.312 / 0.489 /
  0.522), Greedy-DiM against reconstructions 0.636, StyleGAN3 0.505; frozen CLIP separates generator output from
  camera at 0.922; summer S14 frozen DINOv2-S probe FRLL 0.162 against 0.129 trained.
- The landmark bar sits on cue-loaded cells: on H1 (598 + 598, CASIA, same source, size and border) the released
  MADation ViT-L/14 reads 0.718 / 0.684, the file size 0.620 / 0.681, FE ViT-L/14 0.735 / 0.745, our ViT-L/14
  recipe retrain 0.833 / 0.810, SelfMAD 0.872 / 0.821; FRLL FaceMorpher and OpenCV at 1.0% are 2 of 204 photos.
  Proposal: make H1 and the FRGC / colorFERET ladder the primary S1 cells.
- SMDD partner structure missed by three earlier passes (data audit of 5 Nov, A41 header count of 7 Nov, the
  October demorpher project, which wrote "SMDD has exactly one image per identity"); that project's refiner gained
  +0.16 cosine on held-out SMDD and lost 0.21 to 0.27 on FRLL, consistent with memorising five partners (inference,
  not tested). SMDD's warp factor is drawn from [0, 1] per morph, so the published morphs cannot carry the
  ghost-energy target.
- SMDD high-frequency separability was measured twice before (A8 audit: noise SD, Haar HH energy and Laplacian
  variance each at AUC 0.99 or more; summer S59 spectral-residual SVM 0.37% on the SMDD evaluation split, about 0%
  on FRLL landmark, 46% on MAD22 with FaceMorpher inverted, AUC 0.02); H-new-235 is answered. 733 of 15,000
  training and 417 of 15,000 evaluation morphs are 257 to 264 px tall. Proposed acceptance test for any rebuilt
  SMDD arm: Laplacian-variance AUC 0.65 or less.
- Prediction for "rebuild SMDD, keep the MADation recipe": the record (A47 I-3, A44 R-last, A47 I-1, ABC60)
  expects the rebuilt set to lose most diffusion numbers and several FRLL landmark cells that history alone solves:
  a lower, cleaner baseline, not a gain; pre-state it in SM1.
- Same-generator heads (Codex loop): A38 probe 0.91 on StyleGAN3 (0.80 to 0.83 after fine-tuning, networks'
  outputs 0.42 to 0.50), A39 0.45 / 0.49 on spread-matched renders; 135 DINO heads 0.78 / 0.73 in-generator, 0.68 /
  0.57 against same-person morphs, 0.32 / 0.26 on DiffAE; 10 joint heads DiffAE / FRGC 0.947, camera 0.836,
  DiffAE / FERET against same-person 0.860, GAN against same-person 0.61 / 0.55, StyleGAN3 0.629 but 0.457 on
  spread-matched, Arc2Face 0.519.
- S8 multitask damage (FRLL 0.285 against 0.129 alone; self-blends DiM 0.074 to 0.525); the demorpher's
  Proposition 1: for a linear blend the residual half (A − B) cannot be observed from the morph.
- Own-engine training (summer S39): 4,000 Delaunay morphs from `scripts/68_hires_morph.py` (the engine AF0 uses)
  added to SMDD made every real MAD22 landmark family worse (WebMorph 0.189 to 0.33-0.36, OpenCV 0.005 to
  0.25-0.31, FaceMorpher 0.000 to 0.18); S16 synthetic artefacts 0.08 on SMDD, 0.66 / 0.42 on FRLL.
- Dating: the frozen ViT-L/14 reading of the diffusion mixing step was the registered positive control of A41
  amendment G on 7 Nov (0.636 [0.579, 0.693] Greedy-DiM, failing its 0.65 gate; 0.772 DiM-A; 0.742 MorDIFF); A43
  had 0.76 falling to 0.67 at 20 steps. The dissimilarity reading (K4) was read once on StyleGAN3 in A30 (84
  networks, no growth).

From the area chair (entry 1), dropped: the statistics in numbers (1.0% of 204 photos is 2 photos, exact interval
0.1 to 3.5%, a perfect 0 of 204 still 1.8%; AMSL 14.7% is 30 photos, 10.1 to 20.3%; "below 10%" is 20 photos, 6.1
to 14.7%); the eight-table minimum set (reproduction on own preprocessing; null rows per cell; genuine photos at
one fixed threshold on FRLL and a non-FRLL pool of 300 or more persons; and others); missing baselines (data-only
MADation on the method's images; dense head on SMDD only; SBI, Face X-ray-style and LAA-Net zero-shot; PW-MAD-style
constant map; UnivFD, B-Free, Dual Data Alignment and Aligned Datasets for the second output); AF0's scale (about
4,000 images of 530 persons, 490 colorFERET and 40 FRGC; the stress test on 10 persons); no print-and-scan or
passport-size JPEG condition; what survives (the AR1 twin gate passes: oracle 0.998, 99% of morphs verify).

From the evaluation novelty check (entry 3), dropped (these narrow the paper's novelty claims; the fixed-threshold
re-read (EV1) adopted a "NIST-style" per-pool block, `experiments/EV1_fixed-threshold-reread/prereg.md` A2, but
the precedent itself and its numbers are recorded nowhere):
- NIST FATE MORPH already reports, per algorithm, false-detection rates on three genuine pools at one threshold
  (source images, about 872,000 visa photos, about 1 million mugshots); since June 2020 it reports that at equal
  thresholds false detections fall and misses rise with resolution; it plots score against subject alpha (Section
  4.10). On Greedy-DiM the two single-image systems with the lowest miss rate at 1% mugshot false detections (0.000
  and 0.085) flag 28.9% and 93.4% of visa photos and 20.9% and 93.3% of source photos, against 1.3% and 7.9% of
  mugshots (visionbox-001, hhi-002; NISTIR 8292 draft supplement, PDF pages 47-48, checked).
- SYN-MAD 2022 ranks at 20% false alarms with one threshold for all attack types; Fu and Damer (2022) set the
  threshold on one genuine source; Peng et al. (2026) report 86 to 100% false alarms on FEI with an FRLL threshold.
- The S2 bar is too coarse on 204 photos (5% is 10 images, interval 2.7 to 8.8%; a detector with a true 12% passes
  one pool with probability 0.20).
- Null rows: Feng, Wallace and Boyd-Graber (ACL 2019, arXiv 1905.05778) show a failing partial-input baseline does
  not prove a dataset free of artefacts; use nulls one way only. Name AD4 "a network trained on photo history only".
- Dose in mixing weight is done (NIST 4.10; Ferrara et al., arXiv 1901.08811); dose in contributor dissimilarity
  looks new; "benchmark construction cannot fake this" is false (pairs are the top 18 to 21% most similar, 250 of
  1,176 or 1,378 per gender; split and subset effects).
- Webmorph neutral-only and DiM neutral / smiling construction are stated by the dataset authors; the imbalance as
  a usable cue is not in print.

From the morph community reviewer (entry 5), dropped:
- Published numbers against ours: MADation ViT-L/14 published 0.74 / 0.99 / 7.26 / 4.07 (FaceMorpher / OpenCV /
  AMSL / WebMorph); SelfMAD publishes 0.00 / 0.00 / 0.99 / 3.45 on the same families; ViT-B/16 AMSL 15.1 against
  3.85; ViT-L/14 MorDIFF 28.9 (all 1,000) or 26.0 (200-morph sample) against 19.26; FE ViT-L/14 35.9 against
  22.85; FE ViT-B/16 40.1 against 17.86; FS ViT-B/16 69.6.
- The SYN-MAD 2022 rule allowed only SMDD and no pretrained weights; FRGC-Morphs and FERET-Morphs are standard test
  sets (SelfMAD reports on them), so training on FRGC / colorFERET photos breaks comparability.
- Scherhag et al., BIOSIG 2017 (with Busch, Raghavendra, Marcel, Grother, Maltoni, Veldhuis, Spreeuwers) already
  require equal quality of genuine and morphed samples; the novelty is the measurement.
- The FE release's 20-step reading is 0.655 [0.581, 0.731], below the plan's own 0.75 bar.
- Use APCER and BPCER (SYN-MAD ranks APCER at BPCER 20%); "resolution history" is forbidden wording in our own
  conclusions (cue not identified).

From the image forensics reviewer (entry 6), dropped: the mean-absolute-difference target is 74% smooth tone
mismatch; the unnormalised patch target is predicted at rank 0.71 by the image's own local contrast; the
contrast-normalised target is 0.97 on flat skin against 0.73 on eyes and mouth; dismissed worries (about 1% of the
disagreement energy lies above a 224 input; a position template reaches only 0.10; warp size does not change
sharpness); Face X-ray lost a factor of seven in error from alpha to Poisson blending (Table 7); top-tenth pooling
raises the score by 1.75 patch SD for any spread increase, and at 224 the score is the mean of about 7 patches;
warp-only images have 0.40 (512) / 0.83 (224) of the photo's Laplacian variance, so false-alarm claims must use
untouched and history-matched photos, never warp-only images; benign in-image processing (burst merging,
portrait blur, retouching, sharpening halos, glasses reflections, flash shadows; Hasinoff et al., SIGGRAPH Asia
2016); the shrinkage ceiling predicted 0.94 to 0.99 against observed 0.82 to 0.85, removed by fresh within-person
variation (0.48 to 0.56) or a caricature factor 1.25 (0.55), rivalled by two genuine pools (0.69 to 0.74); the
data-processing bound does not cover DiffAE morphs; Face X-ray AUC 87.35% / 61.6% under light / heavy compression;
prior work Debiasi et al., PRNU-based morph detection (IWBF 2018).

From the SMDD novelty check (entry 0), dropped: pixel check, 379 of 379 sampled morphs fit the named partner best
(median residual 3.1 against 26.8 grey levels); keys carry 1 to 5 of the five partners (172 / 349 / 710 / 1,110 /
1,512 keys); the evaluation split has 3,919 keys and partners 3,536 / 3,331 / 3,232 / 2,988 / 1,913; under the
per-key reading about 10,500 different partners would be expected; IDistill's training loader reads both
contributor embeddings from file-name tokens (`code/data_utils.py` l.134-135), so its second-identity target takes
only five values (applies to any OrthoMAD-style recipe reading contributor identities); survival after SMDD's
artefact filter differs by partner (68.9 / 66.2 / 65.2 / 56.3 / 43.5%, assuming 5,000 pairs each); SMDD morphs use
blending 0.5 with a warp factor in [0, 1] and dlib tutorial code; each partner appears in 14.5 to 23.0% of training
attacks; later papers describe SMDD wrongly (MADation "created from the bonafide samples"; SynMorph pairs chosen by
a face-recognition system; SelfMAD "1024 × 1024"); precedents for a few fixed sources behind a class (Geva et al.,
EMNLP 2019; Dong et al., CVPR 2023, implicit identity leakage; Müller et al., ASVspoof 2021, silence up to 85%).

From the dense-map novelty check (entry 2), dropped: Dang et al., CVPR 2020, already supervise with a measured
source difference (threshold 0.1), and 4a(1−a)|W_A − W_B| = 4(1−a)|morph − W_A|; Forensics Adapter (CVPR 2025,
TPAMI 2026 extension, "Unleashing CLIP for Generalizable Face Forgery Detection"), LAA-Net, SLADD (regresses the
blending ratio), SelfMAD++ (segmentation branch; released code uses the face mask for genuine images and an
all-zero map for simulated morphs), Dong et al. CVPR 2023, Qin et al. TBIOM (partial morphs harder to detect);
reference corrections: single-image demorphing is Banerjee, Jaiswal and Ross (three authors); FOCAL's title
contains "Soft Contrastive Learning"; the arXiv abstract of 2501.09817 does not mention GAN-reconstructed genuine
images and shows no venue.

### 14.3 Class-definition literature check (`class_definition_check_raw.json`) against `14_CLASS_DEFINITIONS.md`

Five searchers and five checkers; 126 claims: 98 confirmed, 21 partly, 4 could not open, 2 wrong, 1 not confirmed.
`14` carries the main stances correctly. Dropped:
- Concas et al., arXiv 2509.14120 (17 Sep 2025; checker: venue stated on arXiv): a smoothing beauty filter on AMSL
  raises BPCER from 25.2% to 70-80% (AlexNet) and from 18.1% to 90-100% (VGG19), EER 27.6 / 19.0 to about 41 and
  37-43; the filtered genuine images stay bona fide. Direct precedent for "processed genuine photos flagged".
- NIST's 2026 report changed the print-and-scan wording: it is now differential detectors that classify "most
  scanned photos as morphs, even when they're not", while "some single-image morph detectors show very low false
  detection rates BUT very high morph miss rates" (the 2020 wording was about most algorithms).
- IDSwapMAD (Banas, Rathgeb, Merkle, Schaubert, EURASIP JIS 2026, article 4, 9 Feb 2026): face-swapped references
  used as the bona fide class for differential MAD training.
- Medvedev, Pimenta, Gonçalves, WACV Workshops 2024, pp. 1043-1050 (arXiv 2309.00665): about 250,000 landmark and
  250,000 StyleGAN selfmorphs counted as bona fide. Medvedev and Gonçalves, IWBF 2024 (arXiv 2402.14665): "self
  morphs didn't demonstrate significant impact to the performance". The group's public MorDeephy benchmark never
  tests selfmorphs.
- Colbois, Otroshi Shahreza, Marcel, arXiv 2402.00695 (IJCB 2023): template-inversion morphs scored with a
  GAN-image detector against FFHQ genuine scores. Benavente-Rios et al., arXiv 2510.09836 (NeurIPS 2025 workshop):
  keeps a separate word, "non-morphed", for synthetic single-identity faces. Ivanovska and Štruc, arXiv 2306.15733
  (IWBF 2023): one-class diffusion MAD. Yermakov et al.: adding self-blends to the real class lowers AUROC 89.3 to
  82.8 (withdrawn paper; its position is overstated by the searcher).
- Spreeuwers et al. (EUSIPCO 2018; handbook chapter 16): noise and down-up scaling applied to morphs only raise
  EER above 20% and above 12%. AEROBLADE suspects DIRE's results came from JPEG against PNG storage of real and fake
  representations. Deepfake-Eval-2024's rule: an item is fake if any portion is AI.
- Operational context: live enrolment in Norway and Sweden, signed studio photos in Finland, EU Regulation
  2019/1157 recital 32 (Busch keynote 2022, checked); Germany digital-only photos from 1 May 2025 and the
  Fraunhofer IGD "harmless image editing" claim (checked); ISO/IEC 30107-3 defines bona fide presentation by system
  policy; ISO/IEC FDIS 19792 wording quoted on Busch's MAD page.
- Venue facts: Zhang, Ramachandra, Raja, Busch is CVPR Workshops 2024, pp. 1510-1518 (one checker opened the CVF
  page; another got HTTP 403); MorDeephy is ICPRAM 2023, pp. 193-204; Aligned Datasets' authors are Rajan, Ojha,
  Schloesser, Lee.
- Not confirmed: "no generated-image detection paper puts pure VAE or diffusion reconstructions of real photos in
  the real class" (search budget ran out).

---

## 15. Most valuable items that were missing, ranked

1. **The rewritten prior-experiment record is unmerged.** The themed index (about 90 rows), 18 experiment
   summaries, the loose-document list and the data-location list are only on branch `origin/prior-work`
   (`b7013d4`) and in a scratchpad clone; the working tree still shows the older index with A44 to A47 "running"
   (section 9). Merge the branch, with the A20 correction.
2. **Volatile sources behind committed documents.** The dossier's S1 and S2 and their inputs, and the
   dataset-extension scripts with `abc60.json`, exist only in the session scratchpad (sections 2 and 7). Copy them
   into the repository.
3. **A standing sentence is contradicted by the record.** "No training change has removed a shortcut so far"
   (`NOTEBOOK.md`, also `02`) ignores A22 (+14.5 to −0.2 points at a 5.1-point cost) and A30 amendment 6 (19-40% to
   4-8% of shrunk photos flagged at 0.4-1.5 points), as the vetting record check found (section 14.2).
4. **SelfMAD's training data.** `11` (b) says SelfMAD is not SMDD-trained. By its paper both training classes are
   SMDD StyleGAN renders and self-blends of them; the release's data is not stated (sections 3 and 4).
5. **Prior art that narrows novelty claims.** NIST FATE MORPH already reports per-pool false detections at one
   threshold, resolution effects and alpha dose, with Greedy-DiM flag rates of 28.9% and 93.4% on visa photos;
   Scherhag et al. 2017 already required equal quality; Concas et al. 2025 measured beauty-filter false alarms
   (sections 14.2 and 14.3).
6. **Published reference numbers for the releases** (MADation ViT-L/14 0.74 / 0.99 / 7.26 / 4.07; SelfMAD 0.00 /
   0.00 / 0.99 / 3.45; FE and FS gaps) and the SYN-MAD rule of SMDD-only training without pretrained weights
   (section 14.2).
7. **Design confounds raised by the lenses and not carried forward**: warp size alone predicts twin against morph
   at 0.81 / 0.92 in the Codex loop; `gate_c.py` fold leakage; dose curves legitimately flat after α = 0.3; the
   identity ceiling below the 0.75 bar; the A46 d2 probe at 0.993 filed as a negative (section 14.1).
8. **Details of the repository-state review**: per-experiment numbers for A44 to A50, ABC60, MambaVision, A138,
   A139 and Astra; the budget figures; the unregistered 8-shard MAD22 array; the network-exposed http server on
   port 8000; the user's request to keep narolski/research updated (section 1).
9. **Release links and terms** for MixFaceNet-MAD, SPL-MAD and MADation weights, and SelfMAD's five released
   backbones (section 4).
10. **The full ABC60 derived tables**, including the X3:self drop when genuine photos are added (Appendix A).

---

## Appendix A. Derived ABC60 and A12 tables (dataset-extension agent, recomputed from the frozen analysis)

Source: `.../scratchpad/abc60.json` (frozen ABC60 analysis from branch `recovery/final-gpu-boundary-v1`,
`family_metrics`), seeds 201 to 205, mean over seeds. Exploratory, post hoc, not registered. Groups: LM = FRLL
AMSL, FaceMorpher, OpenCV, WebMorph and MAD22 FaceMorpher, OpenCV, Webmorph; GAN = FRLL StyleGAN, MAD22 MIPGAN-I,
MIPGAN-II; DIFF = DiM-A, DiM-C, Fast-DiM, Fast-DiM-ODE, Greedy-DiM, Greedy-DiM-S, MorDIFF. "17" = all 17 families.
Arms: A = SMDD, B = plus genuine photos, C = plus classical morphs. CN = ConvNeXt-T, VM = VMamba-T, DeiT = DeiT-S,
D3 = DINOv3.

**A1. Per-arm means** (output of `abc_sum.py`; its printed header was misaligned, the columns below are the order
the code writes them). EER in %, X3 columns are AUC:

| Arch | Arm | nat LM | E7 LM | nat GAN | E7 GAN | nat DIFF | E7 DIFF | nat 17 | E7 17 | H2 | H3 orig | H3 spread | X3:a256 | X3:rec | X3:self |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CN | A | 17.22 | 29.24 | 15.50 | 15.50 | 31.08 | 61.57 | 22.62 | 40.13 | 48.43 | 41.94 | 53.57 | 0.83 | 0.76 | 0.946 |
| CN | B | 14.79 | 16.78 | 20.46 | 20.46 | 23.68 | 29.73 | 19.45 | 22.76 | 50.99 | 46.76 | 51.21 | 0.82 | 0.59 | 0.376 |
| CN | C | 6.53 | 9.91 | 19.95 | 19.95 | 23.52 | 51.85 | 15.90 | 28.95 | 49.38 | 43.97 | 54.42 | 0.91 | 0.84 | 0.905 |
| VM | A | 19.66 | 31.27 | 40.09 | 40.09 | 37.68 | 66.63 | 30.68 | 47.39 | 47.98 | 42.22 | 52.62 | 0.51 | 0.54 | 0.746 |
| VM | B | 9.65 | 10.72 | 27.49 | 27.49 | 25.66 | 33.08 | 19.39 | 22.89 | 51.45 | 50.35 | 51.82 | 0.76 | 0.60 | 0.598 |
| VM | C | 5.71 | 8.67 | 24.69 | 24.69 | 28.00 | 53.81 | 18.24 | 30.09 | 48.91 | 46.19 | 53.66 | 0.85 | 0.78 | 0.899 |
| DeiT | A | 11.44 | 17.88 | 21.58 | 21.58 | 20.72 | 51.87 | 17.05 | 32.53 | 49.66 | 48.42 | 53.81 | 0.59 | 0.50 | 0.720 |
| DeiT | B | 15.24 | 19.28 | 23.98 | 23.98 | 28.27 | 46.23 | 22.15 | 31.21 | 51.21 | 54.61 | 53.33 | 0.56 | 0.48 | 0.528 |
| DeiT | C | 5.28 | 8.28 | 27.83 | 27.83 | 26.73 | 55.29 | 18.09 | 31.09 | 50.24 | 46.10 | 53.81 | 0.73 | 0.68 | 0.796 |
| D3 | A | 5.39 | 14.85 | 37.50 | 37.50 | 8.21 | 53.18 | 12.22 | 34.63 | 48.79 | 49.42 | 51.86 | 0.63 | 0.42 | 0.534 |
| D3 | B | 7.65 | 12.49 | 40.81 | 40.81 | 12.37 | 28.60 | 15.45 | 24.12 | 50.39 | 50.77 | 51.32 | 0.86 | 0.36 | 0.350 |
| D3 | C | 1.10 | 2.98 | 21.31 | 21.31 | 4.30 | 29.07 | 5.98 | 16.96 | 47.90 | 51.22 | 53.81 | 0.86 | 0.46 | 0.332 |

What X3:a256, X3:rec and X3:self compare exactly (presumably DiffAE cross morphs against the A41 X3
aligner-only, reconstruction and same-person sets) was not verified.

**A2. Paired contrasts** (output of `abc_rise.py`; five-seed paired t intervals, df 4, t = 2.776; "rise" = E7
minus native EER in points). `09` section 2.2 holds the DIFF rise table and the landmark C − A values only.

LM rise:

| Arch | A | B | C | B − A | C − B | C − A |
|---|---|---|---|---|---|---|
| CN | 12.02 | 1.99 | 3.38 | −10.03 [−15.02, −5.03] | +1.39 [−1.71, +4.50] | −8.64 [−12.95, −4.32] |
| VM | 11.61 | 1.07 | 2.96 | −10.54 [−17.30, −3.79] | +1.90 [−2.31, +6.11] | −8.65 [−15.66, −1.63] |
| DeiT | 6.43 | 4.04 | 3.00 | −2.39 [−4.18, −0.60] | −1.04 [−3.30, +1.22] | −3.43 [−5.06, −1.80] |
| D3 | 9.46 | 4.85 | 1.88 | −4.61 [−7.36, −1.86] | −2.97 [−5.24, −0.69] | −7.58 [−11.13, −4.03] |

E7 DIFF (absolute EER under E7):

| Arch | A | B | C | B − A | C − B | C − A |
|---|---|---|---|---|---|---|
| CN | 61.57 | 29.73 | 51.85 | −31.84 [−46.82, −16.86] | +22.12 [+7.72, +36.52] | −9.72 [−16.80, −2.65] |
| VM | 66.63 | 33.08 | 53.81 | −33.55 [−58.02, −9.08] | +20.73 [−5.69, +47.15] | −12.82 [−33.23, +7.59] |
| DeiT | 51.87 | 46.23 | 55.29 | −5.64 [−10.43, −0.86] | +9.06 [−1.38, +19.50] | +3.41 [−6.37, +13.19] |
| D3 | 53.18 | 28.60 | 29.07 | −24.59 [−36.44, −12.74] | +0.48 [−25.34, +26.29] | −24.11 [−42.21, −6.01] |

E7 LM (absolute EER under E7):

| Arch | A | B | C | B − A | C − B | C − A |
|---|---|---|---|---|---|---|
| CN | 29.24 | 16.78 | 9.91 | −12.45 [−17.79, −7.11] | −6.87 [−11.86, −1.88] | −19.33 [−23.99, −14.66] |
| VM | 31.27 | 10.72 | 8.67 | −20.55 [−43.25, +2.16] | −2.05 [−9.45, +5.35] | −22.60 [−40.44, −4.75] |
| DeiT | 17.88 | 19.28 | 8.28 | +1.40 [−4.37, +7.18] | −11.00 [−16.87, −5.13] | −9.60 [−14.14, −5.06] |
| D3 | 14.85 | 12.49 | 2.98 | −2.36 [−6.51, +1.79] | −9.51 [−13.77, −5.26] | −11.87 [−15.19, −8.56] |

H2 (EER):

| Arch | A | B | C | B − A | C − B | C − A |
|---|---|---|---|---|---|---|
| CN | 48.43 | 50.99 | 49.38 | +2.56 [+1.49, +3.63] | −1.61 [−3.03, −0.19] | +0.95 [−1.01, +2.91] |
| VM | 47.98 | 51.45 | 48.91 | +3.47 [+0.81, +6.13] | −2.54 [−3.92, −1.16] | +0.93 [−2.93, +4.78] |
| DeiT | 49.66 | 51.21 | 50.24 | +1.55 [−0.96, +4.06] | −0.97 [−3.97, +2.04] | +0.58 [−0.64, +1.81] |
| D3 | 48.79 | 50.39 | 47.90 | +1.60 [+0.40, +2.79] | −2.48 [−3.73, −1.24] | −0.89 [−1.92, +0.14] |

H3 orig (EER):

| Arch | A | B | C | B − A | C − B | C − A |
|---|---|---|---|---|---|---|
| CN | 41.94 | 46.76 | 43.97 | +4.82 [+0.90, +8.74] | −2.79 [−9.37, +3.79] | +2.03 [−2.11, +6.18] |
| VM | 42.22 | 50.35 | 46.19 | +8.13 [+5.65, +10.62] | −4.16 [−9.73, +1.41] | +3.97 [−0.95, +8.89] |
| DeiT | 48.42 | 54.61 | 46.10 | +6.19 [+0.71, +11.67] | −8.51 [−12.76, −4.26] | −2.32 [−5.35, +0.71] |
| D3 | 49.42 | 50.77 | 51.22 | +1.35 [−0.70, +3.41] | +0.45 [−2.21, +3.11] | +1.80 [+0.48, +3.12] |

Q = mean of H2 and H3 orig (EER; the C − A values reproduce the registered contrasts):

| Arch | A | B | C | B − A | C − B | C − A |
|---|---|---|---|---|---|---|
| CN | 45.18 | 48.87 | 46.67 | +3.69 [+1.24, +6.14] | −2.20 [−5.19, +0.79] | +1.49 [−0.51, +3.49] |
| VM | 45.10 | 50.90 | 47.55 | +5.80 [+3.95, +7.65] | −3.35 [−6.59, −0.11] | +2.45 [−1.30, +6.20] |
| DeiT | 49.04 | 52.91 | 48.17 | +3.87 [+2.04, +5.70] | −4.74 [−7.04, −2.44] | −0.87 [−2.72, +0.99] |
| D3 | 49.11 | 50.58 | 49.56 | +1.47 [+0.31, +2.64] | −1.02 [−2.37, +0.33] | +0.46 [−0.55, +1.46] |

**A3. A12 R-recipe triplets** (output of `a12_rise.py`, local score files
`/home/narolski/mambamorph-code/smadcvpr_runs/A12_scored/A12BR/`, uncapped EER on `eval.csv` orig / resmatch rows;
arms A = d0, B = photos only, C = d1; n = networks found; "D" = the seven diffusion families, riseLM = landmark
rise). Selected (es) checkpoint:

| Row | A (n, native D, E7 D, rise D, rise LM) | B (photos only) | C (d1) |
|---|---|---|---|
| frozen-CLIP probe | 5, 15.4, 15.2, −0.2, 0.3 | 5, 13.0, 9.8, −3.2, −0.6 | 5, 11.2, 10.7, −0.5, 0.2 |
| MADation R | 8, 12.6, 12.1, −0.5, 0.3 | 5, 14.0, 11.2, −2.8, −0.2 | 8, 7.7, 9.7, 2.0, 0.6 |
| Inception R | 5, 14.4, 63.0, 48.6, 15.3 | 5, 14.9, 57.6, 42.7, 19.7 | 8, 15.5, 55.9, 40.5, 8.9 |
| PW-MAD R | 8, 29.0, 72.3, 43.3, 10.0 | 5, 74.2, 52.6, −21.6, −6.1 | 8, 24.4, 68.5, 44.1, 7.3 |

Last checkpoint:

| Row | A | B | C |
|---|---|---|---|
| frozen-CLIP probe | 5, 16.0, 16.1, 0.1, 0.4 | 5, 13.1, 10.3, −2.9, −0.5 | 5, 10.3, 9.4, −0.9, −0.0 |
| MADation R | 8, 8.4, 30.4, 22.0, 4.3 | 5, 4.8, 22.2, 17.4, 1.4 | 8, 3.5, 16.3, 12.8, 1.3 |
| Inception R | 5, 18.7, 64.3, 45.5, 14.1 | 5, 16.1, 60.7, 44.6, 19.0 | 8, 19.9, 59.7, 39.8, 7.8 |
| PW-MAD R | 8, 42.9, 69.7, 26.8, 4.4 | 5, 70.9, 53.5, −17.3, −5.6 | 8, 28.6, 65.7, 37.1, 3.8 |

PW-MAD's photos-only arm has native diffusion EER above 70% at both checkpoints (`09`: "PW-MAD photos-only failed
training").
