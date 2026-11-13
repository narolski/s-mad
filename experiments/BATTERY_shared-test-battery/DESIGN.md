# Shared test battery (BATTERY), version 1: design note

Owner: BATTERY role (Claude agent for the lead). Written 13 Nov 2026. Status: **release candidate 1.0.0-rc2, not released** (rc1: 761a3c7; rc2 applies the pre-run check
`experiments/reviews/PRERUN_BATTERY_RC1_20261113.md`, F1-F8).
Battery v1 counts as released only when the lead says so, after the pre-run check (experiment-reviewer) and this regression
test. Code: `src/battery/`. Large outputs: `/mnt/t7/smad_next/BATTERY/`. Arms registered before the release keep their own
readers; nothing in other owners' folders was changed.

## 1. What it does

One command per trained network (CLIP ViT-B/16 + LoRA first):

```
cd src && python -m battery.run --ckpt NETDIR --arm NAME --seed N --out OUTDIR --code PN1_TREE/code --ref REFERENCE_TAR \
    --hf-home DIR --data dev=ROOT tt1=ROOT meds=ROOT gd=ROOT [--train-manifest CSV] [--expect-eval FITJOB_scores_eval.npz] \
    [--stats auto|yes|no]
cd src && python -m battery.run --stats-only OUTDIR        # zero-GPU completion of the statistics on the DGX
cd src && python -m battery.read OUTDIR1 OUTDIR2 ... [--expect-seeds 408 409 410 411 412]   # rows per arm, no verdict
```

Steps of `battery.run`, in this order; a failure stops the run before anything later happens:

1. **Deny-list guard** (`guard.py`). Self-test, then a process-wide audit hook on every file open, directory listing and glob.
   Every manifest and every image path of every set is checked before scoring. Denied (path tokens, lower case): FRLL and
   FRLL-Morphs, MAD22, MorDIFF, DiM (DiM-A/C, Fast-DiM, Greedy-DiM), H1, FEI, CASIA-WebFace, any `valx` file except
   `valx_a.csv`, FST, A12SP / A12-SP, `gtest` (prep_gtest). Tokens, not substrings, for short names, so that development
   sources such as CASIA-FASD or colorFERET pass. Both the path string and its resolved real path (symlinks followed) are
   checked (rc2, F5); the self-test includes symlinks named `ok.png` and `valx_a.csv` pointing into denied places. The
   audit hook exempts only files under the Python installation roots (`sys.prefix`, `base_prefix`, `exec_prefix`). The battery never calls `pn1lib.catalog()`, which opens the benchmark lists (section 4).
   Exit code 3 on a hit.
2. **Platform record** (`gate.py`, `platform.json`): GPU model, UUID, compute capability, driver, torch build, CUDA runtime,
   cuDNN version, TF32 for matmul and cuDNN, cudnn.benchmark, deterministic flags, attention backends, Python and package
   versions, host, Slurm job (items 1-11 of `TT1/PLATFORM_PINS_FOR_FINAL_READ.md`). TF32 is set on for both, as the
   fit-job scorer `pn1_score.py` does; `cudnn.benchmark` is set False explicitly (item 10). Every output also records the
   sha256 of every battery `.py` file and one hash over them (`battery_code_sha256`; `stats_code_sha256` when the
   statistics are completed); the reader refuses to pool an arm whose records carry more than one hash (rc2, F1). Any
   change to battery code means a new VERSION and a rerun of the regression test.
3. **Platform gate** (`gate.json`). Platform key = GPU model + torch build + TF32 setting. A platform without a pinned
   reference is refused (exit 5; the DGX GB10 is refused, TT1 H-new-5). The pinned reference network of the platform is
   loaded by the battery's own loader and scored by the battery's own scorer on the gate rows; its stored fit-job logits
   must be reproduced **byte-identically** (all 2,496 float32 logits equal). Criterion fixed here, before any gate is run.
   On failure: `GATE FAILED: nothing scored`, exit 2, no row scored.
   - Gate rows: 39 whole batches of the stored run (batch k = rows 64k to 64k+63 of the FS1 evaluation order, k = 0, 8, ...,
     304), so batch composition equals the stored run's (TT1-D2: batching changes the last bits). The rows span the logit
     range: camera photos at the floor, FFHQ genuine and morphs, splices; on the two references the stored logits run from
     -3.6 to +3.5 with 369-498 of them between -2 and +2 (floor rows alone would hide platform differences).
   - **Node rule (fixed 13 Nov 2026 20:03 CET, commit 8637f7e, before smoke 6316361 is fetched or read; lead's answer (2) in
     `experiments/reviews/PRERUN_BATTERY_RC1_20261113.md`).** A run is *byte-gated* if all 2,496 gate logits are equal.
     Otherwise it is *tolerance-gated* if max |dlogit| <= 1e-4 and 0 own-rule flips on the 2,496 gate rows; its records
     carry `gate_class = "tolerance-gated"` and are never pooled with byte-gated records (the reader prints them as a
     separate arm entry). Anything else fails (exit 2, nothing scored). The rule is not changed after any gate is seen.
     If smoke 6316361 ran on r18-8 (the node of the H100 reference), a second smoke with `--exclude=r18-8` is queued.
   - Pinned references: **A100 PCIe 40 GB, torch 2.2.1, TF32 on**: FS1 `PN1_Sb_s403` (tar 8dec83b8...), stored by
     `pn1_score.py` in its fit job on a rented A100-PCIE-40GB (container smad_torch221_cu121_v1.sif). **WCSS H100, torch
     2.11.0+cu128 (~/dmenv), TF32 on**: AB1 `AB1_Sb_s408` (tar a84b551f...), stored by `pn1_score.py` in AB1 fit job
     6311579 on r18-8. Each reference is checked by tar, stored-logit and weight sha256 before use.
   - **The gate covers the scored network only if its inference settings equal the reference's** (rc2, F3): `arch`, `res`,
     `ft`, `lora_r`, `lora_targets`, `lora_alpha`, `lora_rs`, `lora_train_norms` of the network's meta.json are compared
     with the reference's before the gate; a difference refuses the run (exit 5). `--seed` must equal the meta seed.
   - **Network check** (`--expect-eval`, rc2, F3): in a fit job the battery's dev logits must equal the same job's
     `pn1_score.py` `scores_eval.npz` byte for byte on every stored id (at least 19,797); otherwise `logits_dev.npz` is
     renamed `*.bak-netcheck`, the status says so, exit 6, and the output is never read. This is the per-network gate of
     PLATFORM_PINS item 13 at no GPU cost.
4. **Scoring** (`run.py score_rows`): the fit-job scorer's loop (`pn1_score.py`: `common.ImageItems` at the network's
   resolution, bilinear resize of the whole frame, batch 64 in manifest order, `common.forward_logit`, float32 logit, no flip,
   eval mode, no autocast). Every set keeps its manifest order, so a battery logit on a gated platform equals the fit-job
   logit of the same row on that platform. Writes `logits_<set>.npz` (id, logit, manifest sha256), `scores_eval.npz` (dev),
   `last_trainable.pt`, `meta.json`, and with `--train-manifest` the unique training rows (`logits_train.npz`, as
   pn1_score.py). Before scoring, every image of every set is checked against its pack's checksum file (`SHA256SUMS`,
   `AB1SUMS`; rc2, F8), on the DGX, on WCSS and on a rented machine alike. TEST runs name their files `TEST_*`. The network loader is pluggable (`backbones.py`): both registered backbones are built by the training
   code's own `common.build_run_model(meta)`; CLIP ViT-B/16 LoRA is live; the DINOv3 ViT-L/16 entry is registered but refuses
   to run until its code pin (BB2 overlay `archs_a12.py`) and a DINOv3 reference network per platform are pinned.
5. **Statistics** (`stats.py`, `battery.json`): every row statistic, from the reviewed readers' own functions, imported
   unchanged (section 3). `battery.json` holds the platform, the gate, every set's manifest and logit hashes, the network's
   provenance, the reader files' sha256, the battery code hashes, all block outputs and the 20 audit rows (`rows.py`).
   The training manifest's sha256 is recorded; if it is not one of the registered FS1/AB1 training manifests, the
   record carries the in-source note "training sources not checked against battery sets: rows 1, 4, 13, 14 may be
   in-source" and the reader prints it (rc2, F7; lead 13 Nov: arms trained on FFHQ or new sources use v1 only with this
   note until DATA's person/source table exists). `/mnt/t7/smad_heldout/ffhq_morphs` is development data (author ruling
   12 Nov) despite its folder name.

Sets (all development data; `sets.py`; each manifest pinned by sha256):

| Set | Manifest (rows) | WCSS pack | Audit rows |
|---|---|---|---|
| dev | `ab1_eval.csv` (21,277: the 19,797 FS1 evaluation rows in their order + 1,480 MS1 FFHQ hold-out rows) | `BB2/pn1_pack_fs.tar` 96c31ae2 + `AB1/ab1_overlay_v2.tar` 171fdb21 | 1, 2, 6-9, 12, 17-20 |
| tt1 | `tt1_score.csv` (34,411: 3,417 reference rows + 30,994 unseen-genuine, border and geometry rows) | `TT1/tt1_pack.tar` 2109f742 | 4, 5, 10, 17, 19 |
| meds | `meds_score.csv` (1,018 NIST MEDS frames; statistics also use the tt1 reference rows) | `BB2/tt1m_meds.tar` 3fb917b2 | 4 |
| gd | `pr1_gd.csv` (11,042 DiffAE and MIPGAN control rows) | `BB2/pr1_gd.tar` 40aa95d2 | 13, 14 |

## 2. Where it runs

- **WCSS H100, last step of a fit job** (frozen `~/dmenv`, torch 2.11.0+cu128): all IO in `$TMPDIR`; packs copied and
  verified one at a time; `--stats no` (the readers' side files live on the DGX); one result tar back to
  `results/<ID>/`; `--extra=FORCE_RM_TMPDIR` on every sbatch. Smoke job: `src/battery/wcss/battery_smoke.sbatch`
  (queued for the dispatcher, section 7). A new arm's fit job adds the fail-soft lines of
  `src/battery/wcss/fitjob_snippet.sh` after `pn1_score.py`: `--ckpt $RUN` (train.py's last.pt + meta.json), `--ref` the
  H100 reference tar, `--train-manifest`, `--expect-eval` the job's own `scores_eval.npz`, a fresh `--out`; a battery
  failure never stops the fit's own result tar.
- **Rented A100 PCIe** (container smad_torch221_cu121_v1.sif, torch 2.2.1): the same command; the driver uploads the four
  packs and `PN1_Sb_s403.tar`. Not yet smoke-tested on an A100; the A100 key stays unreleased. Proposal: an A100 smoke on
  Athena `plgrid-now` (1 GPU, 1 hour, free): Athena's A100-SXM4 in the torch 2.2.1 container reproduced the rented A100 PCIe
  gate scores of Sb 403-407 byte for byte tonight (NE1, Athena job 3550470), so its key would be pinned as a separate
  platform only after its own gate run on PN1_Sb_s403 is byte-identical.
- **DGX**: CPU only: the statistics (`--stats-only`), the reader, the regression test. The DGX GPU is not a scoring
  platform (refused by the gate).

## 3. Reuse instead of re-implementation

`legacy.py` imports each reviewed reader by file path after checking its sha256 against the version that produced the
reviewed numbers of the audit table (a file off its pin stops the battery):
`PN1/pn1lib.py`, `PN1/reads.py`, `PN1/fs_read.py`, `PN1/c2p_read.py`, `PR1/pr1_read.py`, `PR1/gd_read.py`,
`TT1/tt1common.py`, `TT1/tt1_read.py`, `TT1/tt1_read_fs.py`, `TT1/meds/tt1_read_meds.py`, `AB1/ab1_read.py`,
`BD1/bd1_read.py`. `smadcvpr/prep_eval.py` and `prep_gtest.py` are neither edited nor imported.

Blocks (`stats.py`): FS1 (fs_read per-arm record and rreads R1-R6), PR1 (pr1_read per-network record: pools, tau5, AUCs and
intervals, Z1, Z2a, Z2c, Z3, Z6), AB1 (ab1_read per-network record with c2p_read.net_stats), C2P (c2p_read.net_stats and
its H-new-2 counts), TT1 (tt1_read.read_net, family_ci, tt1_read_fs.extra_reads), MEDS (tt1_read_meds per-network
record), GD (gd_read GD0/GD1/GD2), BD1 (bd1_read per-network record). Most of these readers compute the per-network
record inline in `main()`, not in a function; the battery copies those per-network lines verbatim (same order, same random
seeds) and calls the readers' functions for every number. The regression test (section 5) is the proof that the copy is
exact.

## 4. Choices and their consequences

- **No catalogue call.** fs_read takes `persons` and `pool` from `pn1lib.catalog()`, which opens the FRLL/MAD22 and H1
  lists. Neither field is used by the pools, AUCs or bootstrap units it computes; the battery sets the reader's own
  fallbacks instead. The regression test shows the outputs are identical.
- **fs_read's storage-share interval.** fs_read draws the bootstrap interval of `share_rising` for its 15 networks from one
  random stream in a fixed order, so the interval of a network depends on its position. The battery gives a single new
  network the stream's first position (the position of A_s403); the regression test replays the order to reproduce all 15.
  Every other statistic is independent of position.
- **TF32 on for every set.** The fit-job scorer runs TF32 on; the TT1 and MEDS reads in the table were made by
  `rescore.py` with TF32 off. Battery numbers on the tt1 and meds sets are therefore not interchangeable with the
  TF32-off numbers of the table for the same network (TT1 measured up to 0.035 logit on camera rows). Within the battery,
  every set of every network is scored on one setting. A new arm's TT1/MEDS numbers are compared only with controls the
  battery scored on the same platform (registered step `prereg_ab1_comparators.md`). The battery rewrites the reader's
  TF32 label of the TT1 block (`tau_cam_label`, `tf32_split_R_cam.battery_note`) and adds `blocks.scoring`; the reader
  puts a NOTE above rows 4, 5, 10, 17 and 19 whenever stored (TF32 off) and battery (TF32 on) records are in one print.
- **Statistics only.** `battery.read` prints numbers, seed ranges and the number of seeds; it prints no verdict, since
  the battery registers no rule. Booleans that are a registered rule of another experiment (for example PR1's Z2a
  `usable`) stay in the JSON but are not printed. Outputs that are TEST runs, that did not pass the gate, or whose logits
  changed since scoring are left out and listed. Records built from stored logits (`battery.stored`, for the regression)
  are shown only with `--include-stored` and are labelled.
- **Same platform.** The reader prints the platform and gate class of every arm, says when one arm mixes platforms,
  and prints a NOTE when the arms of one print come from different platforms. `--expect-seeds` refuses a print with a
  missing seed or a duplicate (arm, seed) pair (guards against seed picking).

## 5. Regression test (CPU, stored logits)

`python -m battery.regress` runs every block on the stored logits of every reviewed network that has them, and compares
every leaf of the reviewed per-network JSON record with the battery's value at the same path by exact equality.
Results: rc1 `regression_v1.json`, rc2 `regression_v1rc2.json` (this folder). End-to-end check of the statistics path on
battery-format folders (rc2, F6): `e2e_v1rc2.json` (`python -m battery.e2e`). See `README.md` for the numbers and for
every row that cannot be reproduced and why.

## 6. Audit rows without data (for the DATA role, through the lead)

See `MISSING_DATA.md`.

## 7. Open items before release

- H100 smoke 6316361 (rc1 code; dispatcher). If it ran on r18-8, the rc2 smoke on another node
  (`battery_nets.sbatch --array=0-1 --exclude=r18-8`, queue file `wcss_battery_smoke2.cmd`, gated on that).
- The registered comparator step on the 15 AB1 networks (`prereg_ab1_comparators.md`, queue file
  `wcss_battery_ab1cmp.cmd`, behind every experiment fit): node identity across H100 nodes and same-platform comparators.
- A100: unreleased; Athena plgrid-now smoke proposed (section 2).
- DINOv3 loader: needs the BB2 overlay pin and a DINOv3 reference network per platform.
- The lead's release decision.
