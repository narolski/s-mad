# Second backbone for the protocol recipe (BB2): registration

Status: REGISTERED at the git commit that adds this version (`date` at registration: Fri Nov 13 12:05:19 AM CET 2026),
after the independent pre-run review (section 12) and before any BB2 fit is submitted. Draft written from Thu Nov 12
11:36:25 PM CET 2026 by the BB2 owner (Claude agent); draft commit 05a8e25. No BB2 fit exists; only the 20-step DGX smoke
(never read as a result). The BB2 owner has opened no FS1 fresh-seed tar or score (the FS1 tars on
`/mnt/t7/smad_next/PN1/results_fs/` were not listed beyond their names).

Author's approval, 12 Nov 2026 about 23:50 CET, his words: "do the second backbone", in answer to "A second backbone
... needs new training code for a DINOv3 arm ... On WCSS it would cost nothing ... it could run tomorrow."

## 1. Question (plain words)

A CVPR reviewer will ask whether the training protocol, and not the CLIP backbone, removes the shortcuts. The candidate
method is a training-data protocol on the MADation recipe (CLIP ViT-B/16 + LoRA, linear head on normalised features):
arm A = the plain recipe (camera photos against two-person morphs); arm B = protocol negatives (warp-only images, the
morph's own warped halves and stored-small copies, labelled genuine-class negatives); arm Sb = B plus face-spliced morphs
with matched negatives. The fresh-seed registration on CLIP (FS1, frozen contrasts v4 at git ac585b7; printed reads
R1-R6 at git e95656a) is running now on seeds 403-407.

BB2 repeats the three arms on a second backbone, with the same data, the same lists, the same seeds 403-405 and the same
development reads, and asks one question per FS1 contrast: **does the pattern seen on CLIP repeat on the second
backbone?** BB2 is confirmatory only. It never replaces the CLIP arm, never chooses between backbones, and its networks
are never combined with the CLIP networks.

## 2. Backbone (task 1)

Rule given by the lead: DINOv3 ViT-B/16 if its weights are on disk and load offline, otherwise DINOv2 ViT-B/14,
otherwise state what is available. No downloads.

Found (DGX `~/.cache/huggingface/hub`, all of `/mnt/t7` and `/home/narolski`; WCSS home and project storage, 12 Nov
23:3x): no DINOv3 ViT-B/16 and no DINOv2 ViT-B/14 anywhere. Available: DINOv3 ViT-L/16 (timm
`vit_large_patch16_dinov3.lvd1689m`, snapshot `30c11095…`, `model.safetensors` sha256
`45172f209c9583c40538afc26b60a07033e6fcc2e8c30228338e6b2e932e7941`, 1,212,347,640 bytes; and the official HF
`facebook/dinov3-vitl16-pretrain-lvd1689m` used by A49), DINOv2 ViT-L/14 (timm `.lvd142m`) and DINOv2 ViT-S/14.

**Choice: DINOv3 ViT-L/16, timm weights** (reported to the lead 23:36). Reasons: same patch size (16) and therefore
the same 14 x 14 token grid at 224 px as CLIP ViT-B/16; rotary position encoding, so 224 px needs no position-embedding
resampling; fused `attn.qkv` Linear without bias, so the unchanged LoRA code (`common.LoRAQKV`, q and v slices) applies
as it does to CLIP; same model family as the earlier A49 study; loads offline through the same timm path as the CLIP
weights (checked: all 318 tensors of the file equal the built tower's state). The DINOv2 models have patch 14 (a
different grid at 224) and ViT-S is much smaller than ViT-B. Cost: ViT-L is about 3.5x the compute of ViT-B/16.

What A49 tells us (`/home/narolski/mambamorph-code/experiments/A49_dinov3/`): it used the official HF DINOv3 ViT-L/16
through transformers 5.19, final CLS after the last norm, L2-normalised, linear logit; no LoRA (head only or LayerNorm
affine + head). Its paired processing-consistency term (lambda 1) failed its registered primary (P3 − P1 processing
change +0.0029 [−0.005, +0.011]); LayerNorm adaptation drove the self-morph control AUC to 0.11-0.14. BB2 uses no
consistency term and keeps every norm frozen (`--lora-train-norms=0`, as the CLIP recipe).

## 3. Arms, data, seeds

- Arms A, B, Sb, defined by FS1's manifests, byte-equal: train_A `af070a60…`, train_B `bd53dc32…`, train_Sb `2cf3fda3…`
  (inside the FS1 pack). Training images are our own AF0 and ladder images from FRGC / colorFERET only.
- Seeds 403, 404, 405: nine fits. One network per fit, last checkpoint, no selection, no ensembles, no fusion with the
  CLIP arm, no seed picking.
- Pack: the unchanged FS1 development pack `pn1_pack_fs.tar`, sha256
  `96c31ae29c4118947e3fd0a7a97600805cbfa5a82369c8ecbc6ee3d6349f2004`, with evaluation manifest `pn1_eval.csv`
  `f0f29f2201bd3a1dc67f24772347960ba7a383a9e5c1fa8920d0cc1b854a5045` (19,797 development rows: af0 1,339, ladder 6,093,
  splice 4,365, FFHQ HN2 list 5,000, FFHQ landmark_combined 3,000). It holds no FRLL, MAD22, MorDIFF, DiM, H1, FEI,
  CASIA-WebFace or sealed row; the reader keeps FS1's assertion (only families af0, ladder, splice, ffhq, ffhq_lcomb).
  Nothing else is scored by any BB2 job. valx, FST and A12SP files are never opened.
- Plus the BB2 overlay `bb2_overlay.tar` (sha256 in section 10): the BB2 `archs_a12.py` and the DINOv3 weights,
  unpacked over the FS1 pack after both tars are hash-checked (run.sh refuses otherwise).

## 4. Recipe, code change, unavoidable differences (each fixed by a rule written here, before any fit)

Unchanged: `train.py` (`cbb2cbd1…`), `common.py` (`b5d42a99…`), `pn1_score.py` (`737d6e35…`), every training flag of
FS1's run.sh: `--regime d0 --split train90 --lofo none --lr 3.33e-06 --res 224 --workers 7 --recipe=v1
--label-smoothing=0 --drop-path=0 --sampler=prior --final=last --steps=6250 --ft=lora --lora-targets=qv --lora-r=2
--lora-alpha=4 --lora-rs --lora-dropout=0.4 --lora-train-norms=0 --opt=adamw --wd=0.05 --head-lr=3.33e-05 --bs=256
--aug=flip --sched=const --clip-grad=5 --pos-weight=1`. Only `--arch` changes, to `a12_dinov3_vitl16_madation`.
Scores: logit without flip averaging, as FS1.

The code change is one new registry entry and one new class in `archs_a12.py` (`src/BB2/archs_a12.py`, diff against
the pinned `bedfeb86…`: 45 added lines, 2 changed dictionary lines that only append the new name; nothing else). Every
new line is reached only through the new arch name. `train.py`, `common.py` and `pn1_score.py` are not changed.

CLIP path unchanged, shown on CPU (`src/BB2/test_clip_identical.sh`): the pinned `train.py` with the FS1 CLIP flags run
from the pinned FS1 code tree and from the BB2 tree (identical except `archs_a12.py`), on the pack data and the pinned
CLIP weights, then the unchanged `pn1_score.py` on 16 evaluation and 16 training rows: every one of the 203 tensors of
`last.pt` equal (`torch.equal`), `meta.json` equal apart from wall-clock and the tree path, train.py output equal apart
from timing, evaluation and training logits bit-equal. Passed for arm B (3 steps, batch 8) and arm Sb (5 steps, batch
8): `/mnt/t7/smad_next/BB2/test_clip{,_Sb}/clip_identical.json` (copied to this folder as `clip_identical_B.json`,
`clip_identical_Sb.json`). The pinned registry does not contain the new name.

Differences that cannot be avoided, with the rule for each:

| Difference | CLIP arm (FS1) | BB2 | Rule |
|---|---|---|---|
| Model size | ViT-B/16, 12 blocks, width 768, 86 M | ViT-L/16, 24 blocks, width 1024, 303 M | no ViT-B DINO on disk, no download (section 2) |
| Patch, grid | 16, 14 x 14 at 224 | 16, 14 x 14 at 224 | same |
| Input | 224 px, loader resize unchanged | 224 px, same loader, same pixels | keep the CLIP input size; DINOv3 has no learned position embedding, so nothing is resampled (its timm default 256 is not used) |
| Normalisation | CLIP mean/std | ImageNet mean/std (0.485, 0.456, 0.406 / 0.229, 0.224, 0.225) | each backbone's own pretraining constants (the DINOv3 processor's) |
| Pooled feature | CLS after ln_post, CLIP projection, 512-d | CLS after the final LayerNorm, 1024-d; no projection exists; 4 register tokens not used | the backbone's own image token, as A49 and the DINOv3 linear probes |
| Head | L2-normalise, Linear(512, 1), 513 parameters | L2-normalise, Linear(1024, 1), 1,025 | same head form |
| LoRA | q, v slices of every attn.qkv, r 2, alpha 4, rsLoRA, dropout 0.4: 73,728 | same policy on 24 blocks: 196,608 | same placement policy; total trainable 197,633 against 74,241 |
| Frozen parts | everything else incl. norms | everything else incl. norms and layer-scale | same |
| qkv bias | present (frozen) | none in DINOv3 | no effect on trainable parameters |
| Learning rates | 3.33e-6 (LoRA), 3.33e-5 (head), tuned by MADation for CLIP | unchanged values | see below |
| Precision | fp32 with TF32 matmul (train.py) | same | unchanged |
| Batch | 256, one pass | 256 one pass, or 128 x 2 accumulation by the memory rule below | see below |
| Data order | loader generator seeded by the seed | same seeds, same generator | the sampler order is seeded the same way; model-initialisation draws and dropout masks differ because the network differs |
| Platform | rented A100 PCIe 40 GB, torch 2.2.1, timm 1.0.27 | WCSS H100, `~/dmenv` torch 2.11.0+cu128, timm 1.0.30 | stated; BB2 arms are compared only with each other; across backbones only the pattern is compared |

**Learning rate (fixed rule).** The recipe's learning rates were tuned by MADation for CLIP. BB2 uses them unchanged.
No learning rate, step count or other setting is tuned on development data or on anything else. A fit with non-finite
loss or weights is reported and never rerun; a fit that trains to a near-constant score (standard deviation of its
19,797 evaluation logits below 0.001, printed with the training-row accuracy at the own rule) is marked "collapsed",
read as it is and reported; it is never rerun with other settings. An unchanged learning rate may simply be too low or
too high for this backbone; that risk is accepted and stated with every BB2 sentence.

**Memory rule (batch; review fix 3).** Measured on the DGX (GB10, fp32/TF32, LoRA, train mode): 8.6 GB of activations
per 32 images for ViT-L/16 against 3.8 GB for CLIP ViT-B/16, so batch 256 needs about 70 GB. The WCSS smoke (section 9)
runs 100 steps at batch 256 in one pass and then 100 steps at batch 128 x 2, logging the GPU's memory.used every 2 s.
All nine fits use batch 256 in one pass only if the 256 x 1 smoke completed and its peak memory.used is at most 72 GiB
(73,728 MiB); otherwise all nine use `--bs=128 --accum=2` (train.py's existing option, train.py:868-874: the loss of
each half divided by 2, gradients summed, clipping and one optimiser step after the second half: the same objective
over 256 images per step and the same 6,250 steps; only the order in which random draws are consumed differs),
provided the 128 x 2 smoke completed; otherwise BB2 stops and is reported. A fit that runs out of memory or reaches its
time limit (an infrastructure failure) is rerun once at 128 x 2 with twice the time limit, and labelled so in the
result. The choice is recorded in the README before the fits are submitted.

**Platform check (review fix 5).** In the WCSS smoke, `src/BB2/featcheck.py` computes the initial (no LoRA, eval, fp32,
TF32 off) L2-normalised DINOv3 feature of 8 fixed training images (the first 8 unique paths of train_A.csv) under WCSS's
torch 2.11 / timm 1.0.30 and compares it with the DGX CPU reference (torch 2.12.1, timm 1.0.27;
`featref_cpu.npz`, sha256 `89f3defe6a6f74ef1852f19ef6e9a2cc8b3867c8e55be895e9ae299425627b75`). If the largest absolute
difference exceeds 1e-3, no fit is submitted and the lead is told.

## 5. Reads (unchanged from FS1)

Contrasts 1-3 exactly as in `prereg_fresh_seeds_v4_frozen.md` (ac585b7) and printed reads R1-R6 exactly as in PN1
prereg.md "FS1 printed reads R1-R6" (e95656a; implementation `fs_read.py` `c0d8dc19…`), on the same images, with the
same floor file (`a14_lcomb.npz`, `714cb73d…`), the same bootstraps and rng seeds. `src/BB2/bb2_read.py` imports
`fs_read.py` unchanged (its hash is asserted) and repeats its per-seed block line for line with BB2 tar names:

- Contrast 1 (primary on CLIP): FFHQ landmark_combined orig morphs (1,000) against resmatch genuine (2,000). A seed
  meets it if Sb − B ≥ +0.05 AUC and Sb − A ≥ −0.02 AUC; a seed with B ≥ 0.95 is untestable; floor = best of the 27
  simple statistics; "beyond the floor" only if on every read seed the 2.5% bound of (Sb AUC − floor maximum) > 0.
- Contrast 2: share of the 2,000 FFHQ persons whose logit rises from ffhq_bona orig to landmark_complete resmatch; an
  arm passes on a seed if the share ≤ 0.65; A is the positive control (must fail).
- Contrast 3: test-ladder face-only R4 against R2w (T_S4_bg vs T_S0_bg); a seed meets it if Sb − B ≥ +0.05.
- Printed only: own-rule flags on development genuine pools, face-blanked reads, development-ladder versions, R1-R6.

## 6. What counts as "repeated" (new: three seeds; written before any BB2 fit)

- **Read seed:** A, B and Sb of that seed all finished with a verified tar and finite evaluation logits (FS1's `load`
  rule), and no non-finite training loss in train.log (implemented in `bb2_read.py`, review fix 4). A seed with a lost or non-finite arm is dropped and not
  replaced. An infrastructure failure is rerun once, unchanged, on the same partition. A collapsed fit (section 4)
  is read as it is.
- **Training-adequacy control (review improvement 1; fixed before any BB2 fit; no CLIP or BB2 training accuracy was
  looked up to set it):** the CLIP learning rates are used unchanged, so a "not repeated" could mean under-training.
  A read seed counts for contrasts 1 and 3 only if each of its three arms reaches a training-row accuracy at the own
  rule (logit > 0, `info.json` `train_acc_rule0`, over the arm's unique training rows) of at least 0.75. If fewer than
  two read seeds pass, contrasts 1 and 3 read "uninformative (under-trained)". Contrast 2 keeps A as its own positive
  control and is not gated.
- **Contrast 1 repeated:** the FS1 seed condition (both margins, same direction, inclusive at full precision) holds on
  at least 2 of 3 testable, adequately trained read seeds (2 of 2 if only two qualify). Not repeated: otherwise. Fewer
  than two such seeds: "not read (too few seeds)" (or "uninformative (under-trained)", above). The floor is read as on
  CLIP: exceeded only if the 2.5% bound is above 0 on every testable read seed (FS1's code; review fix 8).
- **Contrast 2:** fewer than two read seeds: "not read (too few seeds)" (review fix 7). A's positive control holds if A fails (share > 0.65) on at least 2 read seeds and on all but at most
  one; otherwise the mark is "uninformative on these seeds" for BB2. With the control, B and Sb are each "repeated" if
  they pass on at least 2 of 3 read seeds (2 of 2 with two), else "not repeated".
- **Contrast 3 repeated:** Sb − B ≥ +0.05 on at least 2 of 3 adequately trained read seeds (2 of 2 with two).
- **R1-R6:** printed per seed. The pre-stated R1-R6 sentence is evaluated as on CLIP, except that its R3 condition "on
  at least 4 of 5 seeds" is read as "on every read seed" (the count cannot reach 4 with 3 seeds).
- With 3 seeds and a per-seed SD of a difference of about 0.025 (FS1's figure), the chance that a true zero difference
  meets Sb − B ≥ +0.05 on 2 or more of 3 seeds is about 0.002; a true CLIP-size gain that is half as large on DINOv3
  would often read "not repeated" (a true +0.05 repeats about half the time). The 0.025 SD is CLIP's figure; for
  ViT-L it is unknown. "Repeated" needs 2 of 3 seeds, a lower bar than FS1's 4 of 5; this is stated beside every BB2
  sentence. BB2 can show that a pattern repeats; a "not repeated" is weak evidence of absence.

## 7. What the paper says (pre-stated; the reader prints these sentences)

"Replicated" below is FS1's own registered reading on CLIP. Anything else from FS1 (not replicated, inconclusive, not
read, uninformative) means there is no CLIP pattern to repeat.

| FS1 on CLIP | BB2 | Sentence |
|---|---|---|
| contrast 1 replicated | repeated, floor exceeded | "The gain of spliced positives over protocol-only training on FFHQ landmark_combined repeats on a second backbone (DINOv3 ViT-L/16, n seeds)." |
| contrast 1 replicated | repeated, floor not exceeded | same, "... but is not shown beyond simple statistics there." |
| contrast 1 replicated | not repeated | "The gain ... did not repeat on a second backbone (DINOv3 ViT-L/16): it is not shown to be independent of the CLIP backbone." |
| contrast 1 not replicated | any | "No CLIP effect to repeat; second backbone printed only" (if BB2 meets the margins on ≥ 2 of 3 seeds: "not claimed") |
| contrast 2 replicated for arm X (B or Sb) | X repeated | "The protocol's removal of the storage reaction (X) repeats on a second backbone (DINOv3 ViT-L/16, n seeds), so it is not a CLIP property." |
| contrast 2 replicated for X | X not repeated | "The removal of the storage reaction (X) did not repeat on a second backbone: it is not shown to be independent of the CLIP backbone." |
| any | BB2 control not met | "storage mark uninformative on DINOv3" |
| contrast 3 replicated | repeated / not repeated | "The face-only ladder gain of Sb over B repeats / did not repeat on a second backbone." |

Every sentence carries: "2 of 3 seeds (a lower bar than FS1's 4 of 5)"; "the spliced arm was first suggested by a
frozen DINOv3 ViT-L/16 head read on MAD22 (BENCHMARK_EXPOSURE item 8), so a repeat on DINOv3 is not independent of how
the arm was chosen"; development data only (FFHQ development set and our FRGC / colorFERET ladder), 3 seeds, ViT-L
against ViT-B, the CLIP learning rates used unchanged, a different platform. Never a benchmark claim, never "the
protocol is backbone-independent" in general, never a comparison of CLIP and DINOv3 accuracy as a result.

## 8. Disclosures

- The contrasts, margins and their direction were frozen with CLIP results in mind (FS1 v4 disclosures: the 401/402
  H1 gains of Sb, the 401/402 face-only ladder reads and paired shares were known). BB2 adopts them unchanged; it is a
  confirmatory repeat only, never a separate discovery.
- The FS1 fresh-seed readings will probably be known (to the lead, perhaps to the BB2 owner) before the BB2 fits end.
  Every BB2 rule is fixed here first; no BB2 rule changes after any FS1 or BB2 score is seen.
- FFHQ landmark_combined and the HN2 list were read on CLIP seeds 401/402; the 191-host test ladder has been read many
  times (BENCHMARK_EXPOSURE.md, FS1 v4). (Corrected after the review, fix 1.) DINOv3 has a history here: frozen
  DINOv3 ViT-L/16 heads (tier 0, 512 px mean patch tokens, seeds 401-405; PN1 prereg section 3) were read on H1, MAD22
  and the 191-host test ladder (BENCHMARK_EXPOSURE.md section 1), and the tier-0 lead "protocol plus spliced on DINOv3,
  MAD22 2.0 / 3.0%" was chosen on MAD22 and motivated the Sb arm (BENCHMARK_EXPOSURE item 8). So the Sb idea came from
  this backbone family, and a DINOv3 repeat is not independent of how the arm was selected. No DINOv3 LoRA network has
  been scored on FFHQ landmark_combined, the HN2 list or the FS1 pack. For the sealed read, MAD22, H1 and FRLL are
  compromised for DINOv3 as for the PN1 family.
- DINOv3 pretraining data (LVD-1689M, web images) may contain faces; nothing is known about overlap with FFHQ. CLIP's
  pretraining data has the same issue.
- Platform and software differ from the CLIP arm (section 4).

## 9. Operations

- WCSS (narolski@ui.wcss.pl), partition lem-gpu-short, one H100 per fit, at most 5 GPUs at once (array `%5`), 8 CPUs,
  64 GB RAM, 80 GB local scratch; all IO in `$TMPDIR`; `--extra=FORCE_RM_TMPDIR` in every script and command; Slurm by
  full path; every ssh under the shared lock, one attempt.
- Smoke first (`src/BB2/wcss/bb2_smoke.sbatch`): arm Sb seed 403, 100 steps, 64 scoring rows, batch 256 then (only on
  failure) 128 x 2; GPU memory logged; results to `results/BB2_smoke`, never read as results. It decides the batch
  rule (section 4) and the time limit of the fits (1.5 x the projected time from its step rate + 30 minutes, at least
  3 h).
- Fits (`src/BB2/wcss/bb2_fit.sbatch`): array of nine tasks, seed by seed (403 A, B, Sb; 404; 405), submitted only after
  the smoke and after this registration is committed, with the complete workload (packs, run.sh, sbatch) already on
  WCSS and hash-checked. Owner, job ID and expected end go into the README at submission.
- Deadline: seeds whose three fits are finished and fetched by 14 Nov 2026 18:00 CET are read; later seeds are never
  read for BB2 (no addendum; review fix 9). Partition limit: lem-gpu-short allows 3 days per job (WCSS documentation as
  recorded in the wcss-gpu notes; review item 6), far above the fits' limit.
- Registered submission commands (review fix 2; the sbatch file is pinned and not edited; `<T>` = the time limit from
  the smoke's step rate by the rule above):
  `/opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR --time=<T> --export=ALL,BB2_BS=256,BB2_ACCUM=1 bb2_fit.sbatch`
  or, by the memory rule, `... --export=ALL,BB2_BS=128,BB2_ACCUM=2 bb2_fit.sbatch`. The script refuses any other batch
  setting before copying anything. A registered rerun (section 4) uses `--array=0-<k-1>`, `BB2_TASKS="<indices>"`,
  `BB2_BS=128,BB2_ACCUM=2` and twice the time limit; it must first move the failed task's partial outputs aside (run.sh
  never overwrites a tar).
- Fetch: each tar and its .sha256 to `/mnt/t7/smad_next/BB2/results/`, sha256 verified; logs fetched and hashed. The
  WCSS copies stay until the local copies are verified; nothing is deleted while it holds the only copy.

## 10. Kept for the sealed final read

Every fit tar holds `last_trainable.pt` (all trainable tensors: LoRA and head) and `meta.json`; with the base weights in
the overlay (sha256 `45172f20…`) and the BB2 `archs_a12.py` they rebuild the network exactly (`rescore.py` /
`common.build_run_model`). Kept: all nine tars on `/mnt/t7/smad_next/BB2/results/` with sha256 lists, the overlay tar,
the run logs. Not kept: full `last.pt` (its sha256 is inside each tar), optimiser state.

Role in the sealed read (FINAL prereg): the BB2 networks of the frozen arm are scored once in the sealed read as a
robustness row, never as an alternative to pick from. If Sb is frozen, BB2 Sb (seeds 403-405); if B, BB2 B. If the
three-source arm of MS1 is frozen (SbM3), BB2 has no matching arm; the sealed read then prints BB2 Sb labelled
"single-source counterpart on the second backbone". If no method is frozen, BB2 is not scored there. The row's label
always carries: "the spliced arm was first chosen on a frozen DINOv3 head read on MAD22; MAD22, H1 and FRLL are
compromised for this backbone family".

## 11. Pins (at the registration commit)

- `src/BB2/archs_a12.py` `a2a68634edfe7f4315f14be1808a2a52ba13ec68fac6c6dba9655820aa18e185` (pinned original `bedfeb86…`)
- overlay `/mnt/t7/smad_next/BB2/bb2_overlay.tar` `7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad`
  (builder `src/BB2/build_overlay.sh`)
- `src/BB2/run.sh` `0eaa4dce1df14537990d490bebbe01ad72d0719686cadfce832f3ce2b82f07c3` (= `src/PN1/run.sh` `6a23a7a4…` with the
  BB2 lines marked)
- `src/BB2/bb2_read.py`, `src/BB2/featcheck.py`, `src/BB2/test_clip_identical.sh`, `src/BB2/wcss/bb2_smoke.sbatch`,
  `src/BB2/wcss/bb2_fit.sbatch`: sha256 in section 12 at the registration commit.
- FS1 pack `96c31ae2…`, evaluation manifest `f0f29f22…`, fs_read.py `c0d8dc19…`, train.py `cbb2cbd1…`, pn1_score.py `737d6e35…`.

Budget: nine fits of about 2-3 H100-hours each (estimate before the smoke), smoke about 0.5 h; free on WCSS.

## 12. Pre-run review and registration

Review: experiment-reviewer, 13 Nov 2026 about 00:00, on commit 05a8e25, verdict GO WITH FIXES; report saved as
`experiments/reviews/PRERUN_BB2_20261113.md`. Applied: fix 1 (DINOv3 history disclosed in sections 7, 8, 10), fix 2
(fit script takes batch and time from the registered command line and refuses others), fix 3 (memory rule with a
72 GiB peak bound; out-of-memory / timeout rerun rule), fix 4 (read-seed rule implemented), fix 5 (feature check on
WCSS), item 6 (partition limit), fix 7 (contrast 2 with one seed), fix 8 (floor wording), fix 9 (late seeds), power
wording, improvement 1 (training-adequacy control). Not applied: improvement 3 (seeds 406, 407): a decision for the
lead and the author; if added, it needs its own registration before any BB2 score exists.

Pins at registration (sha256): `src/BB2/archs_a12.py` a2a68634edfe7f4315f14be1808a2a52ba13ec68fac6c6dba9655820aa18e185;
`src/BB2/run.sh` 0eaa4dce1df14537990d490bebbe01ad72d0719686cadfce832f3ce2b82f07c3;
`src/BB2/bb2_read.py` e85783c5341844c45caca6dc9e8430aa2ac96c31c5211d316552a3a0c6b94031;
`src/BB2/featcheck.py` 430efddcd01b9c4713c42f6b59bc8fb74c3e529912d34063731960b4a43e837f;
`src/BB2/test_clip_identical.sh` a2d13f3fb5ebc12fafd6405f0b4620a52a92fa292065714e10606c8a77dd1266;
`src/BB2/build_overlay.sh` 13805e62495894ac3eb0e3805fc0e1c8ad6c3373ecf37bfafab358e30fae23fc;
`src/BB2/wcss/bb2_fit.sbatch` 84b21718bb960909003e4ee3354ea90e7da7e63b651f46bba2feaf3e5bbd4e79;
`src/BB2/wcss/bb2_smoke.sbatch` 2bf724869b8b52ad44be2ac0607fb7dc96b3a8d76f469ad216560efa201fc653;
overlay 7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad; featref_cpu.npz
89f3defe6a6f74ef1852f19ef6e9a2cc8b3867c8e55be895e9ae299425627b75; FS1 pack 96c31ae2….
