# Second backbone for the protocol recipe (BB2): full record

Owner: BB2 owner (Claude agent), DGX and WCSS. Started 12 Nov 2026, 23:30 CET. Follows
`/home/narolski/smad-next/DOCUMENTATION.md`. Registration: `prereg.md` (this folder). Short verdict: `result.md`.
Code: `/home/narolski/smad-next/src/BB2/`. Large outputs: `/mnt/t7/smad_next/BB2/`.

## 1. Question and current answer

Does the pattern that the protocol network (PN1) fresh seeds (FS1) show on CLIP ViT-B/16 repeat when the same three
arms (A plain recipe, B protocol negatives, Sb protocol + face-spliced morphs with matched negatives) are trained with
the same data, lists, seeds 403-405 and development reads on a second backbone? Backbone: DINOv3 ViT-L/16 (no ViT-B
DINO weights exist on disk; prereg section 2). Status 12 Nov 2026 23:52: code, CPU equivalence test, reader and draft
registration written; DGX smoke running; draft goes to the independent pre-run review. No fit submitted. No answer yet.

## 2. Timeline (CET, machine clock)

- 12 Nov 23:30 Read OWNER_BRIEF.md, DOCUMENTATION.md, NOTEBOOK.md (12 Nov), PN1 README / prereg (arms, amendment 4,
  FS1, D1-D3, R1-R6), prereg_fresh_seeds_v4_frozen.md, BENCHMARK_EXPOSURE.md (not re-read in full), src/PN1/run.sh, the
  pack code (train.py, archs_a12.py, common.py LoRA, pn1_score.py), FINAL prereg (robustness row), PRERUN_PN1_REMEDIES,
  A49 records, MS1 prereg part 2 and src/MS1/wcss/.
- 23:31-23:36 Weight search. DGX: DINOv3 ViT-L/16 (timm and HF), DINOv2 ViT-L/14, DINOv2 ViT-S/14; no ViT-B DINO.
  WCSS (one ssh, `find ~ /lustre/pd03/hpc-narolski-1790461090 -maxdepth 7 -name "models--*"`): no DINO cache found;
  `~/dmenv`: timm 1.0.30, torch 2.11.0+cu128, transformers 5.19.0. Decision DINOv3 ViT-L/16 sent to the lead 23:36.
- 23:37 Checked timm Eva (DINOv3): fused `attn.qkv` Linear(1024, 3072) without bias, so `LoRAQKV` applies; no absolute
  position embedding (RoPE); `global_pool="token"` = CLS after the final norm.
- 23:38 `src/BB2/archs_a12.py` (pinned `bedfeb86…` + new entry `a12_dinov3_vitl16_madation` and class
  `DINOv3MADation`). CPU build: weights from the overlay path, 318 of 318 tensors equal the file; LoRA 24 blocks,
  trainable 197,633.
- 23:39-23:47 CPU equivalence test of the CLIP path (`test_clip_identical.sh`): arm B 3 steps batch 8, arm Sb 5 steps
  batch 8. First comparison run flagged only the tree path in `meta.json["arch_extra"]["weights"]` and `train_hours`;
  comparator fixed to drop wall-clock keys and normalise the two tree paths (no change to what is trained); both PASS.
- 23:42 GPU memory measurement on the DGX (bs 16 and 32, train mode, LoRA): CLIP ViT-B/16 3.79 GB per 32 images,
  DINOv3 ViT-L/16 8.61 GB per 32 images -> about 70 GB at batch 256.
- 23:44 overlay built (`build_overlay.sh`), sha256 `7c0a0b41…`. 23:44:46 DGX smoke started (run.sh, arm Sb seed 403, 20
  steps, 64 scoring rows, batch 64 x 4 accumulation to keep DGX memory modest and to exercise the fallback path).
- 23:47 upload of the FS1 pack and the overlay to WCSS `.../smad-next/packs/BB2/` started (rsync under the lock).
  A WCSS check at 23:4x found the Slurm controller unreachable ("Unable to contact slurm controller").
- 23:50 `bb2_read.py` written; mock test (random logits in mock tars, a fake FS1 reading) runs end to end.
- 23:48-23:52 draft `prereg.md`, this README, `result.md`.

## 3. Data

- FS1 development pack `/mnt/t7/smad_next/PN1/pn1_pack_fs.tar` sha256 `96c31ae2…` (unchanged; arms' manifests and the
  evaluation manifest inside; see prereg section 3). Unpacked tree used by the tests: `/mnt/t7/smad_next/PN1/fs_tree/`.
- DINOv3 weights: `~/.cache/huggingface/hub/models--timm--vit_large_patch16_dinov3.lvd1689m/snapshots/30c1109559f65dea34316b0d4842d35c5771fe11/model.safetensors`
  sha256 `45172f20…`, copied into the overlay as `pn1/hf/a12/vit_large_patch16_dinov3.lvd1689m.safetensors`.
- Overlay `/mnt/t7/smad_next/BB2/bb2_overlay.tar` sha256 `7c0a0b41f2e7bf656dc49db33c34a33ef62b10e8f0aaec24e247e684098d0bad`
  (BB2SUMS, archs_a12.py, weights).
- Local test trees: `/mnt/t7/smad_next/BB2/pinned/pn1` (real-file copy of the FS1 code, checked against the pack's
  SHA256SUMS), `/mnt/t7/smad_next/BB2/tree/pn1` (same + BB2 archs_a12.py + weights). Data and hf are symlinks into the
  FS1 tree.
- WCSS: `/lustre/pd03/hpc-narolski-1790461090/smad-next/packs/BB2/` (upload in progress).

## 4. Code (`/home/narolski/smad-next/src/BB2/`; DGX Python `/home/narolski/mambamorph-code/.venv-spark/bin/python -I`, torch 2.12.1+cu130, timm 1.0.27)

| File | Job |
|---|---|
| `archs_a12.py` | pinned archs_a12.py + DINOv3 entry (only reached through the new arch name) |
| `build_overlay.sh` | builds `bb2_overlay.tar` (deterministic) |
| `run.sh` | one fit = one task: FS1 pack + overlay (both hash-checked), unchanged train.py with the FS1 flags and `--arch a12_dinov3_vitl16_madation`, unchanged pn1_score.py, one result tar |
| `test_clip_identical.sh` | CPU proof that the CLIP path is unchanged (pinned tree against BB2 tree) |
| `bb2_read.py` | registered reader (imports fs_read.py unchanged); `--mock DIR` test |
| `wcss/bb2_smoke.sbatch` | WCSS smoke, decides the batch rule |
| `wcss/bb2_fit.sbatch` | nine fits, array `0-8%5` (`__BS__`/`__ACCUM__` filled from the smoke's rule before upload) |

## 5. Results

None yet.

## 6. Checks

- CLIP path unchanged: `clip_identical_B.json`, `clip_identical_Sb.json` (PASS; 203 tensors equal; logits bit-equal).
- DINOv3 weights load exactly (318 / 318 tensors equal).
- Reader mock test: `bb2_mock.json` (random logits; no real score).
- Not verified: timm 1.0.30 (WCSS) against 1.0.27 (DGX) DINOv3 outputs; the WCSS smoke runs the WCSS version.

## 7. Dead ends and failures

- First CPU comparison reported PASS false only because of the tree path and wall-clock; comparator fixed (section 2).
- Local test tree built first with symlinked code files: `common.py` resolved its own folder to the AD4 tree and would
  have imported the pinned archs_a12.py; rebuilt with real-file copies before any test.

## 8. Observations and ideas

- DINOv3 timm default input is 256; BB2 keeps 224 (the CLIP arm's pixels).

## 9. Open items and next steps

DGX smoke result; pre-run review; registration commit; WCSS smoke; fit submission; fetch; read; post-result review.

## 10. Handover state

- DGX: smoke `run.sh` (log `/mnt/t7/smad_next/BB2/dgxsmoke/smoke.log`, work folder `/mnt/t7/smad_next/BB2/dgxsmoke/work`
  (about 18 GB while it runs, delete after)).
- Upload to WCSS: log `/mnt/t7/smad_next/BB2/upload.log`.
- Nothing submitted on WCSS. Compute: DGX only.

## 11. Reproduce from scratch

```
src/BB2/build_overlay.sh /mnt/t7/smad_next/BB2
src/BB2/test_clip_identical.sh /mnt/t7/smad_next/BB2/test_clip B 3 8
src/BB2/test_clip_identical.sh /mnt/t7/smad_next/BB2/test_clip_Sb Sb 5 8
python3 -I src/BB2/bb2_read.py --mock /mnt/t7/smad_next/BB2/mock
# WCSS: upload packs/BB2 (FS1 pack, overlay, run.sh + run.sh.sha256, sbatch files), then
/opt/slurm/current/bin/sbatch --extra=FORCE_RM_TMPDIR bb2_smoke.sbatch ; ... bb2_fit.sbatch
python3 -I src/BB2/bb2_read.py
```
