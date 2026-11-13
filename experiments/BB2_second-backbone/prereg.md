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

## Amendment 1 (registered at the git commit that adds this version, with its pre-run fixes A1.7 and amendment 2; written from Fri Nov 13 08:36 CET 2026; before any BB2 fit exists, before any BB2 score is read and before any BB2 network is scored on the MS1 FFHQ hold-out)

**Why.** Registration 4393990 predates today's CLIP results: FS1 read 13 Nov 06:38 (`experiments/PN1_protocol-network-
first-tests/result.md`, review `experiments/reviews/REVIEW_PN1_FS1_20261113.md`): contrast 1 replicated 5 of 5, contrast
2 uninformative (A's positive control failed), contrast 3 replicated. The author then adopted the replacement storage
test C2P (PN1 prereg.md, 2715e48) and the amended freeze rule (FINAL prereg section 1, 6691adc). The lead (13 Nov
08:45) asked that BB2 carry the same development reads as the first backbone: the storage flag-rate rise (C2P), the
landmark_combined AUC (FS1 contrast 1) and the same-person splice flag rate (S3), development data only.

**Disclosure.** Written after the FS1 reading and its review were read by the BB2 owner (CLIP values above; Sb's S3 own-
rule flags 31-41%). No C2P score of any network was known to the BB2 owner at writing (`c2p_read.json` absent). No BB2
fit exists (the fit submission under 4393990, unchanged, was refused twice by the WCSS controller at 08:30 and 08:35);
this amendment changes no fit, no flag, no pack and no FS1-pack read of sections 5-7. The WCSS smoke values are
operational only (loss at step 100, memory).

**A1.1 Unchanged.** Arms A, B, Sb; seeds 403-405; recipe, packs and fit jobs; reads and counting of sections 5-7
(contrasts 1-3, R1-R6, adequacy control) and their sentences. Contrast 2 (v4) is still computed and printed; since it
was "uninformative" on CLIP, its BB2 sentence is "No CLIP effect to repeat" by section 7.

**A1.2 New read: contrast 2-prime and H-new-1 on BB2 (registration C2P, unchanged statistics).**
- Data: the MS1 FFHQ hold-out (fam `ms1ffhq`, 1,480 rows: 300 native photos, 291 fm61 / 290 amsl112 copies, 150 u50
  morphs and their copies) of the MS1 pack `pn1_pack_ms1.tar` `c11b16bc…` (evaluation manifest `d1fab6ad…`), FFHQ =
  development only. No BB2 network has scored it. No FRLL, MAD22, MorDIFF, DiM, H1, FEI, CASIA-WebFace or sealed row is
  scored (the job scores only fams af0, ffhq, ms1ffhq).
- Scoring: one WCSS H100 job (`src/BB2/wcss/bb2_c2p.sbatch`), submitted only after every fit of the read set has
  ended (its inputs exist at submission; never queued with a dependency on the fits); unchanged `src/PN1/rescore.py`
  (`6f6eede7…`, logit without flip) run through the unchanged wrapper `src/TT1/rescore_tf32.py` (`0d0b6b6f…`, TF32 on
  for matmul and cuDNN, the numerics of pn1_score.py in the fits; review fix F1), on the MS1 pack with the BB2 overlay
  unpacked over it (the job asserts the pack's archs_a12.py is the pinned bedfeb86… before the overlay). Families af0
  and ffhq for the platform gate (C2P.2's thresholds, against each fit's stored pn1_score.py logits, same GPU type),
  ms1ffhq for the read. Disclosure: CLIP's C2P was scored with TF32 off (rescore.py defaults); C2P's statistics compare
  scores within one network, so this matters little. Local plumbing check only: rescore.py runs on a BB2 network
  (the 100-step smoke network; its logits are tiny, so this says nothing about the gate on trained networks).
- Statistics: C2P.3 and C2P.4 exactly, through `src/PN1/c2p_read.py` (`45e72914…`, imported unchanged; same pairs,
  bootstrap draws rng 20261131, margins).
- Read seeds and adequacy (review fixes F2, F3): a seed enters C2P only if it is a read seed by section 6 (verified tars,
  finite logits, no non-finite training loss); X's pass on a seed counts only if X and A both reach the training-
  adequacy accuracy (≥ 0.75, section 6) on that seed (an under-trained network that reacts little must not pass);
  X's native-morph miss is printed beside every pass.
- Three-seed counting (new): per size z, A's control as C2P.3. X ∈ {B, Sb} **passes** if it passes on ≥ 2 of 3 seeds at
  fm61 AND at amsl112; **fails** if it passes on 0 seeds at a size where A's control is met on ≥ 2 seeds;
  **uninformative** if A's control is met on ≤ 1 seed at either size; otherwise "inconclusive, no claim". Gate-failed or
  lost seeds keep the denominator of 3. H-new-1: **supported** if Δm_att ≤ −0.20 on ≥ 2 of 3 seeds at either size;
  **falsified** if Δm_att ≥ −0.10 on ≥ 2 of 3 seeds at both sizes; otherwise inconclusive; fewer than 2 read seeds: not
  read. H-new-2 is not read for BB2.
- Sentences (reader `src/BB2/bb2_c2p_read.py`): if CLIP's contrast 2-prime "passes" for X and BB2 passes: "The reduction
  of the storage reaction (X ...) repeats on a second backbone (DINOv3 ViT-L/16, 2 of 3 seeds or more)"; if CLIP passes
  and BB2 does not: "... did not repeat on a second backbone (<verdict>): not shown to be independent of the CLIP
  backbone"; if BB2 is uninformative: "uninformative (the plain arm's control is not met on DINOv3)"; if CLIP does not
  pass: "No CLIP effect to repeat; printed only". H-new-1 printed beside CLIP's, both verdicts. The caveats of section 7
  apply (2 of 3 seeds; Sb chosen on a DINOv3 head; development only; CLIP learning rates; different platform). Review
  F5: with a per-seed pass probability of 0.3 / 0.5 / 0.9, "≥ 2 of 3" passes with probability 0.22 / 0.50 / 0.97
  against 0.03 / 0.19 / 0.92 for CLIP's "≥ 4 of 5"; a false pass on a partial reaction is 2-7 times more likely than on
  CLIP. This sentence accompanies every three-seed BB2 C2P sentence; amendment 2 replaces it by CLIP's own rule when
  five seeds are read.

**A1.3 New printed read: same-person splice flags (S3).** From each fit's stored scores (FS1 pack, splice rows): own-
rule flag share of S3 (development 100, test 191), of S0, S4 miss, AUC S3 vs S0 and S4 vs S3, per arm and seed. Printed
only, no verdict; it describes whether the blending-seam reaction seen on CLIP (Sb 31-41% of development S3) is a
property of the recipe on both backbones.

**A1.4 Room for a seam-shortcut arm.** A training arm against the blending-seam shortcut (drafted by another owner
today) can be added on BB2 later only by a registered amendment before its fits: its manifest enters as a further
overlay file (the FS1 pack stays unchanged), `run.sh`'s arm list and the fit script's task table are extended by that
amendment, seeds 403-405, the same recipe, scoring and reads (sections 5-7, A1.2, A1.3), compared with BB2 Sb of the
same seed. No BB2 rule above changes when it is added.

**A1.5 Freeze and sealed read.** BB2 never enters the freeze rule (FINAL section 1 as amended at 6691adc); its networks
of the arm FINAL freezes are scored once in the sealed read as a robustness row (section 10 unchanged).

**A1.7 Pre-run review and operations.** Review `experiments/reviews/PRERUN_BB2_A1_20261113.md` (Opus, on ddf8b0b;
GO WITH FIXES): F1 (TF32 wrapper), F2 (adequacy for C2P passes), F3 (job takes a registered task-list override
`BB2_TASKS`, results-folder and output-name overrides; default unchanged; reader applies section 6's read-seed rule and
verifies tar hashes; C2P deadline: the job is submitted after the last fit of the read set ends and read by 14 Nov
2026 23:59 CET; an infrastructure failure is rerun once unchanged after the failed output is moved to
`*.bak-<label>`; a gate failure is never rerun), F4 (a WCSS smoke of the job on the two smoke networks,
`BB2_TASKS="BB2smoke_Sb_s403_bs256x1 BB2smoke_Sb_s403_bs128x2"`, results `results/BB2_smoke`, output `BB2C2Psmoke`;
never read as a result), F5 (power sentence above), F6 (reader checks the output tar's members, TF32 on and the GPU
model against the fits'; records the sha256 of CLIP's c2p_read.json when it reads it; mock outputs renamed), F7
(operational deviation, lead 13 Nov 08:4x: the array throttle of the nine fits is raised from 5 to 9 after submission
because WCSS had about 20 idle H100 nodes; every fit still runs alone on one H100; no fit changes). Improvement 5:
the seam arm (A1.4) is registered only after BB2 Sb results are known, which it discloses; its manifest uses existing
images only (no new blur, blending or resize code) and its overlay is pinned by sha256.

**A1.6 Pins.** `src/BB2/bb2_c2p_read.py`, `src/BB2/wcss/bb2_c2p.sbatch`: sha256 at the commit that registers this
amendment (README). `rescore.py` 6f6eede7…; `c2p_read.py` 45e72914…; MS1 pack c11b16bc….

## Amendment 2 (registered, with amendment 1, at the git commit that adds the section "Registration of amendments 1 and 2" below; lead's go 13 Nov about 08:50: "go for amendment 2 (seeds 406 and 407, six more fits, counting rule fixed now ...)"; before any BB2 fit exists or any BB2 score is read)

- **Fits.** Seeds 406 and 407, arms A, B, Sb: six more fits, the same recipe, packs, batch rule (256 x 1, from the WCSS
  smoke 6308946) and time limit (`--time=0-03:03:00`) on WCSS H100s, the platform of the smoke and the first nine
  fits. Driver `src/BB2/run_s5.sh` = `run.sh` (0eaa4dce…) with 406 and 407 added to the seed list (a new file, so the
  queued array of the first nine fits, which checks run.sh's own hash, is untouched); `src/BB2/wcss/bb2_fit2.sbatch` =
  `bb2_fit.sbatch` with the six-task table and run_s5.sh (diff in the README). Command:
  `cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/BB2 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR --time=0-03:03:00 --export=ALL,BB2_BS=256,BB2_ACCUM=1 bb2_fit2.sbatch`.
  About 10.2 H100-hours.
- **Which counting applies (fixed now; decided by completion, never by a score).** If all six fits of 406 and 407 are
  fetched with verified sha256 by 14 Nov 2026 18:00 CET (later tars are never placed in the results folder), the read
  set is seeds 403-407 and every BB2 count uses CLIP's own rules: contrasts 1-3 FS1's table (n = 5: repeated on ≥ 4,
  not repeated on ≤ 1; n = 4: 4 of 4 / ≤ 1; n ≤ 3: not read), contrast 2's control "A fails on all but at most one
  read seed, n ≥ 4", the R1-R6 sentence's R3 condition "≥ 4 seeds"; C2P.3 and C2P.4 exactly (passes ≥ 4 of 5 at both
  sizes; fails ≤ 1 with the control on ≥ 4; uninformative with the control on ≤ 3; H-new-1 on ≥ 4 of 5); the adequacy
  gate keeps its threshold and needs ≥ 4 adequate seeds. Otherwise the registered three-seed rules on 403-405 apply
  and seeds 406/407 are not read. "Repeated" keeps its meaning (CLIP's "replicated" condition met on BB2).
- **C2P job.** With five seeds, `BB2_TASKS` lists the 15 fit tasks; otherwise the default 9.
- **Readers.** `bb2_read.py` and `bb2_c2p_read.py` choose the mode by the file rule above (`seed_mode`), print it, and
  apply the matching counts. Mock-tested in both modes.
- **Disclosure.** Added after amendment 1's review recommended it and with the CLIP FS1 values known; no BB2 score
  exists.

### Amendment 2 pre-run check and fixes (review `experiments/reviews/PRERUN_BB2_A2_20261113.md`, Opus, on c092af5; GO WITH FIXES)

- **Fix 1, the mode is frozen blind to scores.** `src/BB2/freeze_mode.py` writes `experiments/BB2_second-backbone/seed_mode.json`
  (mode, the read set's tars with sha256, the fetch log's sha256 and last lines, time, reason). It may run only when all
  15 fit tars are present and verified, or every missing fit is a remote-confirmed failure (no tar after its one
  rerun), or at 14 Nov 2026 18:00 CET or later; mode = five if all six 406/407 tars are present and verified, else
  three. The file is committed before any reader runs on real tars; both readers refuse real mode without it, take its
  mode, and check every listed tar against its sha256. Rules: no reader runs on real tars before the freeze; every
  fit is fetched as soon as it ends (`src/BB2/fetch_bb2.sh`, one line per verified tar in `results/fetch.log`).
- **Fix 2:** five-seed contrast 2 control is exactly fs_read.py:242 (`n ≥ 4 and A fails on ≥ n − 1`); the three-seed
  rule is unchanged.
- **Fix 3:** the C2P reader refuses a C2P tar whose `tasks.txt` is not exactly the frozen read set.
- **Fix 4:** pins below; diffs of run_s5.sh and bb2_fit2.sbatch in the README.
- **Fix 5:** the C2P job writes the sha256 of the wrapper and rescore.py it ran into env.txt; the reader checks the
  pins (field "wrapper_pinned"). TF32 is on by construction of the pinned wrapper.
- **Fix 6, GPUs:** bb2_fit2.sbatch runs at most 6 at once; with the first array at throttle 9 BB2 may hold up to 15
  H100s at once (operational deviation from section 9's "at most 5", on the lead's instruction to use the idle WCSS
  nodes; every fit still runs alone on one GPU; no fit changes). If the lead sets a lower cap, the dispatcher applies it.
- Disclosed difference from CLIP's counting: with fewer than 4 read seeds BB2 prints "not read (too few seeds)" where
  fs_read prints "inconclusive"; the outcome (no claim) is the same.

## Registration of amendments 1 and 2 (`date` at writing: Fri Nov 13 08:52:52 AM CET 2026; no BB2 fit exists; no BB2 score of any kind has been read)

Pins (sha256): `src/BB2/bb2_read.py` 78aa516bd1d4b909d40303fcded24d3aa732c5dd6c99c170ce701d1d49777bcb (replaces e85783c5 of
section 11); `src/BB2/bb2_c2p_read.py` 906c5b122b3f424ef0f459f6b62204f22f2411bf2dc1e821c642541fe354b9ee; `src/BB2/freeze_mode.py`
b166852c11e00ea70ab101e8519c4e2bc93649a55f77400620ff37b6ed4e78ae; `src/BB2/fetch_bb2.sh` 062b713e28bc754ab53257c49cca700d725c6bc92d296f9e2f248dc1e8161cff;
`src/BB2/run_s5.sh` 6e53a70dbe445f9d48c49a78950c59559a2a39b4fd7f8455bdedc7ef898b810a; `src/BB2/wcss/bb2_fit2.sbatch`
385faad652b220e5a58cb6087745def30385b5b4ce6267c521770d0f6493f662; `src/BB2/wcss/bb2_c2p.sbatch`
3c4de47c374f61c89b8c712575305e7646ef7375fa327bf118e819db9be526c5; unchanged: run.sh 0eaa4dce…, bb2_fit.sbatch 84b21718…,
rescore.py 6f6eede7…, rescore_tf32.py 0d0b6b6f…, c2p_read.py 45e72914…, fs_read.py c0d8dc19…, MS1 pack c11b16bc….

## Amendment 3 (lead, 13 Nov about 09:40; registered at the git commit that adds its "Pre-run check" paragraph below; written before any BB2 fit has started; no BB2 score exists)

Why: CLIP's first C2P read was "uninformative" because its networks were rescored on another GPU model with another
TF32 setting (`experiments/reviews/REVIEW_PN1_C2P_20261113.md`, Q5). BB2's design (same GPU type, TF32 wrapper) is
kept; three additions:

1. **GPU name asserted.**
   - C2P job: `src/BB2/precision_probe.py --expect-gpu "NVIDIA H100"` runs before any scoring; on another GPU name the
     job stops (`BB2_C2P_FAIL`). The reader requires the probe's `gpu_ok` and GPU name "NVIDIA H100" in each C2P tar.
   - Fits: the nine and six fits were already queued with the registered scripts (6310084, 6310092; run.sh is
     hash-checked at run time, so it is not edited while they are queued). Their assertion is applied at read time:
     run.sh writes the GPU name into every result tar (`gpu.txt`); a seed is read only if all three of its fits ran on
     "NVIDIA H100" (both readers). The smoke ran on "NVIDIA H100" (95,830 MiB).
2. **Effective precision logged.** The probe sets TF32 the way pn1_score.py and rescore_tf32.py do (legacy flags
   `torch.backends.cuda.matmul.allow_tf32` and `torch.backends.cudnn.allow_tf32`), then prints the legacy flags,
   `torch.get_float32_matmul_precision()`, the newer `fp32_precision` attributes where the build has them (matmul,
   cuDNN conv), and the relative error of a 4096 x 4096 fp32 matmul and of a 3 x 3 convolution against fp64 (about
   1e-7 for IEEE fp32, about 1e-4 to 1e-3 for TF32), in case the legacy flags are remapped in this build. The C2P job
   runs it in the same interpreter and build as the fits (`~/dmenv`, torch 2.11.0+cu128), so it documents what the
   fits' pn1_score.py flags meant there too. Printed only (beyond the GPU assertion). DGX check (torch 2.12.1, GB10):
   matmul and conv fp32_precision "tf32", relative errors 2.9e-4 / 3.0e-4.
3. **CLIP comparison branch for C2P.** BB2's "repeat of the CLIP effect" sentence for contrast 2-prime now reads "No
   CLIP effect to repeat; printed only", because the first CLIP C2P read is "uninformative" (0cb89c5,
   `c2p_read.json` 62ee0bf4…), unless the registered re-scoring of the CLIP networks (amendment C2P-R, awaiting the
   author) is registered and read before the BB2 C2P read and "passes"; then its reading file is given to the reader
   (`bb2_c2p_read.py --clip-json <C2P-R reading>`) and the registered sentences of A1.2 apply against it. Which file is
   used is fixed by that order (C2P-R read before the BB2 C2P read, or not), never by a BB2 score. H-new-1 is printed
   beside whichever CLIP reading applies.

Smoke: the queued C2P smoke (6310085) uses the script as submitted (without the probe); the dispatcher is asked to
replace it with the amended script so that the production path is smoke-tested exactly.

**Amendment 3 pre-run check** (`experiments/reviews/PRERUN_BB2_A3_20261113.md`, Opus, on 69b970d; GO WITH FIXES) and
fixes, registered here (`date`: Fri Nov 13 09:4x CET 2026; lead's agreement 09:4x: fits stay queued, read-time GPU
assertion from gpu.txt suffices, replace the C2P smoke):
- Fix 1: a missing fit gpu.txt drops that seed instead of crashing the C2P reader.
- Fix 2: the C2P reader refuses any C2P tar whose probe did not assert "NVIDIA H100" or that holds unexpected members.
- Fix 3: the CLIP file is fixed before the read: `experiments/BB2_second-backbone/clip_choice.json` (file path and
  sha256 of the CLIP reading to use: the first C2P reading `c2p_read.json`, or C2P-R's reading if C2P-R was read
  first) is committed before the BB2 C2P read; the reader requires `--clip-json`, refuses unless it equals that
  committed, unchanged choice, refuses if its output exists (one read), and checks the CLIP file's schema. The branch
  uses CLIP's per-arm verdict: "passes" -> the repeat sentences of A1.2; any other verdict -> "No CLIP effect to repeat;
  printed only".
- Fix 4: the probe's sha256 is hard-coded in the C2P job; pins below.
- Fix 5: a missing gpu.txt is logged as its own not-read reason in bb2_read.py.
- Smoke: the replacement C2P smoke (output `BB2C2Psmoke2`) is the smoke of the production path; 6310085 (pre-amendment
  script) is cancelled and never cited. The probe's failure path was tested on the DGX (`--expect-gpu "NVIDIA H100"` on
  a GB10: exit 4; the job's `|| fail` stops before scoring).
- Pins (sha256): `src/BB2/precision_probe.py` b49c1e704bc8957db76398abfd5ab54218ee152ac32ed9e061c634378148605e; `src/BB2/wcss/bb2_c2p.sbatch` e2185edeb0fd06478c259970da4cf15d518dda1c8d80d26324391307fd1a7da4; `src/BB2/bb2_read.py` b8d3f650b6ce977ef2ce5732507a6e7b536d8f7b9e0ab638f20263c15b20bb5f; `src/BB2/bb2_c2p_read.py` cad995d8dfd53e2664331ad75eed4eda3db6bc9a3779dfd3d0f35035fd46c9c6.

## Predictions logged before the C2P and S3 reads (from the post-result review of part 1, `experiments/reviews/REVIEW_BB2_PART1_20261113.md`; `date` at writing: see the commit; no C2P score of any BB2 network exists, and the S3 printed read has not been computed)

Printed beside the registered reads; they change no registered rule.
- H-new-2 (DINOv3 Sb reads a face-surround mismatch): on the development ladder, DINOv3 Sb flags at least 50% of S3 at
  its own rule on at least 4 of 5 seeds and its S4-vs-S3 AUC is at most 0.65; falsified if S3 flags are at most 41% and
  the AUC is at least 0.75 (on at least 4 of 5 seeds); otherwise inconclusive.
- H-new-3 (the storage shortcut needs adaptation): in C2P, A's positive control fails on DINOv3 at both sizes on at
  least 4 of 5 seeds (contrast 2-prime "uninformative").

## Amendment 4: E3, one DINOv3 arm at a learning rate fixed by rule (registered with its pre-run fixes at the commit that adds the section "Pre-run check of amendments 4 and 5"; lead's go 13 Nov about 15:40 under the author's standing instruction; registered at the commit that adds its final version; no E3 fit exists)

**Why.** The post-result review of part 1 (`experiments/reviews/REVIEW_BB2_PART1_20261113.md`) found that at the CLIP
learning rates DINOv3 Sb did not fit its own splice training rows (training AUC lad_S4 vs lad_S3 0.58-0.59 against
CLIP's 0.85-0.88) and that the relative LoRA update was about 3.5 times smaller than on CLIP (1.5-1.9% against
5.2-6.3%). BB2's "contrast 1 not repeated" therefore cannot separate "the recipe did not transfer because it under-fitted"
from "the effect depends on the backbone". E3 asks that question once.

**The one value tried, and where it comes from.** LoRA learning rate 1.17e-5 = 3.5 x 3.33e-6 (rounded as stated by the
lead), so that the relative LoRA update can reach the size it had on CLIP; head learning rate unchanged (3.33e-5);
everything else as BB2 (recipe, flags, steps, batch 256 x 1, packs, overlay, lists, arch). The factor 3.5 was fixed from
the training-fit diagnosis of part 1 (weights and training rows only), not from any development read of E3 (none exists)
and not from any BB2 development score. Only this one value is tried; there is no search, no second value, no rerun with
other settings. Code: `src/BB2/run_lr.sh` = `run_s5.sh` with `BB2_LR=1.17e-05`, run folder and results folder BB2L
(diff in the README); `src/BB2/wcss/bb2l_fit.sbatch` = `bb2_fit2.sbatch` with 15 tasks (A, B, Sb x 403-407, seed by seed,
403-405 first), task names `BB2L_<arm>_s<seed>`, results `results/BB2L`. DGX smoke of run_lr.sh: 20 steps, optimiser
groups show LoRA lr 1.17e-05 and head lr 3.33e-05.

**Seeds and counting.** All 15 fits are submitted; the counting is frozen before any E3 tar is opened, exactly as
amendment 2 (`src/BB2/freeze_mode_L.py` -> `seed_mode_L.json`, committed; five-seed rules if all six 406/407 fits are
fetched and verified by 14 Nov 2026 18:00 CET, else three-seed rules on 403-405; late tars are reported as late, never
read). The fetch deadline for all E3 reads is 14 Nov 2026 18:00 CET.

**Splice-fit gate (new, fixed now).** A read seed counts for contrasts 1 and 3 only if (a) the training-adequacy rule of
section 6 holds and (b) Sb's training-row AUC of lad_S4 against lad_S3 (unique rows of `scores_train.npz`) is at least
0.80. If fewer than the counting minimum of seeds (4 in five-seed mode, 2 in three-seed mode) pass, contrasts 1 and 3
read "uninformative (splice rows under-fitted)".

**Reads.** BB2's reads unchanged (contrasts 1-3 with FS1's rules, R1-R6 printed, own-rule flags printed), through
`src/BB2/bb2l_read.py` = `bb2_read.py` with the E3 names, the gate and the outcome below. No C2P read for E3.

**What each outcome means (pre-stated, printed by the reader as `e3_outcome`).**
| E3 result | Meaning |
|---|---|
| contrast 1 "repeated" (gate met) | "did not transfer because under-fitted": with the splice rows fitted at the rule-fixed learning rate, the landmark_combined gain of Sb over B repeats on DINOv3 ViT-L/16; BB2's "not repeated" was under-fitting |
| contrast 1 not repeated and Sb − B < +0.02 by the seed count (≥ 4 of 5, or 2 of 3) | "backbone-dependent (for DINOv3 ViT-L/16 with a CLS read-out)": with the splice rows fitted, the gain does not appear |
| gate not met, or too few seeds | "under-fitted again or too few seeds": BB2 stays uninformative about backbone dependence |
| anything else | "inconclusive, no claim" |
Contrast 3 and contrast 2 are read and worded as in BB2 sections 6-7. Caveats as BB2 (development only; Sb chosen on a
frozen DINOv3 head; ViT-L against ViT-B; CLS read-out at 224 px, not the 512 px mean-patch read-out of tier 0; a
learning rate changed from the CLIP recipe by one rule).

**Operations.** WCSS H100s as BB2, time limit 3:03 (section 9's rule; review fix 2), `--export=ALL,BB2_BS=256,BB2_ACCUM=1`; queued right behind the BB2
C2P job and SE1's SE fits. About 15 x 1.6 h ≈ 24 H100-hours.

## Amendment 5: E2, zero-LoRA ablation and a frozen-feature linear probe (registered with amendment 4; descriptive, post hoc; development and training rows only)

- **Networks:** the 15 BB2 DINOv3 networks (results/BB2, frozen in seed_mode.json) and the 15 FS1 CLIP networks (A, B,
  Sb x 403-407, `/mnt/t7/smad_next/PN1/results_fs`, copied to WCSS with sha256).
- **Scoring (one WCSS H100 job, `src/BB2/wcss/bb2_e2.sbatch`, `src/BB2/e2_score.py`):** every network with all LoRA B
  matrices set to zero (head on the frozen tower) on its own training rows (unique) and on the whole FS1 evaluation
  pack; CLIP networks also with LoRA on the platform-gate rows (fams af0 + ffhq). TF32 on as in the fits; GPU asserted
  and precision logged (precision_probe.py). Plus the frozen DINOv3 CLS features of train_Sb's unique rows.
- **CLIP on a different GPU (lead's rule):** the CLIP networks were trained and scored on an A100 PCIe. Their H100
  head-only scores are used only for networks that pass C2P.2's gate on the H100 (LoRA on, against their stored A100
  logits: p99 |Δ| ≤ 0.05, max ≤ 0.10, decisions agree ≥ 99.5%). For a network that fails, E2 reports only what its
  stored A100 scores already give (as-trained values), and says so.
- **Reads (`src/BB2/e2_read.py`, once):** per network, as trained (stored scores) and with LoRA zeroed: own-rule
  training accuracy, Sb's training AUC lad_S4 vs lad_S3, FFHQ landmark_combined AUC, test-ladder face-only AUC
  (S4_bg vs S0_bg, unpaired); LoRA's contribution = as trained − zeroed. Linear probe: frozen DINOv3 CLS features of
  train_Sb (StandardScaler + LogisticRegression C = 1; 5-fold StratifiedGroupKFold by person, random_state 0); CV AUC
  of lad_S4 vs lad_S3 and of lad_S4 vs lad_S0.
- **Pre-stated readings (printed, decide nothing):** "LoRA did little for Sb's splice fit on DINOv3" if LoRA's
  contribution to Sb's training AUC S4 vs S3 is within ±0.03 on ≥ 4 of 5 seeds; otherwise "LoRA contributed". Probe:
  CV AUC S4 vs S3 ≥ 0.80 -> "linearly separable in frozen DINOv3 CLS features: the under-fit is an optimisation
  matter"; ≤ 0.65 -> "frozen DINOv3 CLS features barely separate S4 from S3"; otherwise "partly separable".
- **Smoke:** the job with one DINOv3 and one CLIP tar, 8 rows per set (`BB2_E2_TARS`, `BB2_E2_LIMIT=8`,
  `BB2_E2_OUT=BB2E2smoke`), before the production job is queued. Local CPU test of e2_score.py and e2_read.py passed.
- About 1-1.5 H100-hours.

### Pre-run check of amendments 4 and 5 (`experiments/reviews/PRERUN_BB2_A45_20261113.md`, Opus, on db25468; GO WITH FIXES), fixes applied and registered here (`date`: see the commit; no E3 fit and no E2 score exists)

1. The E3 reader's sentences treat every "uninformative ..." and "not read ..." label as not read (it could have printed
   "did not repeat ... not independent of the CLIP backbone" when the gate failed); mock-tested with a failing gate.
2. E3 time limit 3:03 (section 9's rule), not 2:15 (arm A took up to 1:49 in BB2).
3. `src/BB2/fetch_bb2l.sh` (remote results/BB2L, BB2L_* tars, local results_L, fetch.log there) fetches E3.
4. Wording: zeroing the LoRA B matrices removes LoRA from the trained network (the head was trained with LoRA-shifted
   features); "as trained minus zeroed" is an upper bound on LoRA's contribution, so "LoRA did little" is conservative
   and "LoRA contributed" may be inflated. The probe separates S4 from S3 alone, while the network's head must also fit
   every other training row, so a probe AUC ≥ 0.80 points at the loss mix or the optimisation, not only the features.
5. The gate selects on Sb's own fit: the reader also prints contrast 1 and the Sb − B < +0.02 count over all adequate
   seeds, ungated (`printed_ungated`), beside the gated counts; printed only.
6. The R1-R6 sentence's seed list includes the gate.
7. Outcome labels: "under-fitted again" only when the gate fails; "too few testable seeds" when the gate is met but
   B is at the ceiling or seeds are lost. Inherited counting with the gate: if only 2 seeds pass in three-seed mode,
   2 of 2 are needed; if only 4 pass in five-seed mode, 4 of 4.
8. e2_score.py asserts 48 (DINOv3) / 24 (CLIP) zeroed B matrices and that every trainable non-head tensor is a LoRA
   A_/B_ matrix; its pin in bb2_e2.sbatch updated.
9. e2_read.py verifies the E2 tar's sha256, the frozen BB2 tars (seed_mode.json) and the CLIP tars' .sha256 files.
10. No E2 result can change E3's learning rate, seeds, counting or submission.
11. E3 has no separate WCSS smoke: its path is the one 6310084/6310092 ran in production on WCSS, changed only in the
    learning-rate string and names; the DGX smoke of run_lr.sh confirmed the learning rates (1.17e-05 LoRA, 3.33e-05
    head) and the BB2L names. Lead's acceptance requested.
12. freeze_mode_L.py docstring corrected; its cut-off is local time on the DGX (CET).
- Pins (sha256): `src/BB2/run_lr.sh` 916bef3b0f62054c9d2281915d4a3146753c0438b6a4ee6b26435ce0b9bf50f5; `src/BB2/wcss/bb2l_fit.sbatch` 777b2fcd5e9be40b9d430ceff8eb80d5324902804e99d990f8fe61c1a829c4a9; `src/BB2/bb2l_read.py` 6ccf6f2f013c51e4958e47aebd0f0fc74ff9b1ba3643d76bee042a7c54ed44e0; `src/BB2/freeze_mode_L.py` be04a5e1843631989d4326ac2afe639127508d09a6afcdda1db0cbe55578a7ca; `src/BB2/fetch_bb2l.sh` 152b10360c3de11cea6ddac536f35fc586ca21d378328398fc47967df0fd6ffd; `src/BB2/e2_score.py` d183171829ea07abbd13d47fca3548498cafb6c170ebaa6ed3db1d32ea1f8a99; `src/BB2/wcss/bb2_e2.sbatch` 42130501f1a587f935925652c910be80bcda131cb8f55e79c20b1d1a33ad0a9f; `src/BB2/e2_read.py` f3efd051ca68984874d5f0a0753f29498228ab05af318dc7fb910f9edca175de.
- Commands: E3 `cd /lustre/pd03/hpc-narolski-1790461090/smad-next/packs/BB2 && /opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR --time=0-03:03:00 --export=ALL,BB2_BS=256,BB2_ACCUM=1 bb2l_fit.sbatch`;
  E2 smoke `... sbatch --extra=FORCE_RM_TMPDIR --job-name=bb2-e2smoke --time=0-00:40:00 --export=ALL,BB2_E2_TARS="<one DINOv3 and one CLIP tar>",BB2_E2_LIMIT=8,BB2_E2_OUT=BB2E2smoke bb2_e2.sbatch`;
  E2 production (after the smoke passes) `... sbatch --extra=FORCE_RM_TMPDIR bb2_e2.sbatch`.

- **Lead's additions (13 Nov about 16:05; before any E3 fit):** E3 skips a separate WCSS smoke (finding 11 accepted).
  bb2l_fit.sbatch gains a first-step guard: a static check that run_lr.sh holds `BB2_LR=1.17e-05`, then the fit runs
  in the background while the job watches its log; the optimiser-groups line that train.py prints before step 1 must
  read `('1.17e-05', 0.05, 96), ('3.33e-05', 0.05, 2)`, otherwise the run is killed at once and the task exits 3
  (tested locally with stand-in scripts: correct line -> rc 0; wrong LoRA lr -> killed, rc 3, after 7 s). E3 is queued
  unthrottled (array %15). The E2 production job is queued beside its smoke and is valid only if the smoke passes (the
  dispatcher cancels it otherwise). `src/BB2/wcss/bb2l_fit.sbatch` sha256 3fdec5a03b0bf3e6ad3a575be1b7014ed58200c062a112bec3fe1340b1f05a72 (replaces the pin above).

## Amendment 6: reading deadline of the C2P job, E2 and E3 (`date` at writing: Fri Nov 13 05:14:58 PM CET 2026; before any tar of 6313488, 6313858, 6313861 or 6313860 exists)

Author ruling, verbatim (NOTEBOOK, 13 Nov 17:15): "For now, assume that we can go over the cutoff date due to WCSS and
Athena waiting time." Lead's rule, relayed by the dispatcher 17:15: "read once when all fits of the batch have ended,
latest 15 Nov 18:00; rows arriving later are labelled late". This replaces, for these batches only:
- **C2P job (6313488; A1.7):** "read by 14 Nov 2026 23:59 CET" -> read once when the job has ended, latest 15 Nov 2026
  18:00 CET; nothing later is read, it is reported as late.
- **E2 (6313858 smoke, 6313861 production; amendment 5):** read once when the production job has ended, latest
  15 Nov 2026 18:00 CET; later output is labelled late and not read as registered.
- **E3 (6313860; amendment 4):** the fetch deadline "14 Nov 2026 18:00 CET" becomes 15 Nov 2026 18:00 CET everywhere
  (seed counting and reading). The seed mode is frozen (freeze_mode_L.py, unchanged rules) when all 15 E3 fits have
  ended (each fetched and verified, or a remote-confirmed failure) or at 15 Nov 2026 18:00 CET, whichever is first;
  five-seed rules if all six 406/407 fits are fetched and verified at the freeze, else three-seed rules; tars arriving
  after the freeze are labelled late and never read. `src/BB2/freeze_mode_L.py` cut-off changed accordingly (sha256 c993e12adad7e25f01afd0ff5e3995f491495d8e44acb808ee5c02044fb7965b).
Nothing else changes: the BB2 part-1 reading (frozen at 546d892, read 15:36) is untouched; the queue order stays as set.
