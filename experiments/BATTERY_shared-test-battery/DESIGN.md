# Shared test battery (BATTERY), version 1: design note

Owner: BATTERY role (Claude agent for the lead). Written 13 Nov 2026. Status: **release candidate 1.0.0-rc1, not released**.
Battery v1 counts as released only when the lead says so, after the pre-run check (experiment-reviewer) and this regression
test. Code: `src/battery/`. Large outputs: `/mnt/t7/smad_next/BATTERY/`. Arms registered before the release keep their own
readers; nothing in other owners' folders was changed.

## 1. What it does

One command per trained network (CLIP ViT-B/16 + LoRA first):

```
cd src && python -m battery.run --ckpt NETDIR --arm NAME --seed N --out OUTDIR --code PN1_TREE/code --ref REFERENCE_TAR \
    --data dev=ROOT tt1=ROOT meds=ROOT gd=ROOT [--train-manifest CSV] [--hf-home DIR] [--stats auto|yes|no]
cd src && python -m battery.run --stats-only OUTDIR        # zero-GPU completion of the statistics on the DGX
cd src && python -m battery.read OUTDIR1 OUTDIR2 ...        # the audit rows per arm, seed ranges, no verdict
```

Steps of `battery.run`, in this order; a failure stops the run before anything later happens:

1. **Deny-list guard** (`guard.py`). Self-test, then a process-wide audit hook on every file open, directory listing and glob.
   Every manifest and every image path of every set is checked before scoring. Denied (path tokens, lower case): FRLL and
   FRLL-Morphs, MAD22, MorDIFF, DiM (DiM-A/C, Fast-DiM, Greedy-DiM), H1, FEI, CASIA-WebFace, any `valx` file except
   `valx_a.csv`, FST, A12SP / A12-SP. Tokens, not substrings, for short names, so that development sources such as
   CASIA-FASD or colorFERET pass. The battery never calls `pn1lib.catalog()`, which opens the benchmark lists (section 4).
   Exit code 3 on a hit.
2. **Platform record** (`gate.py`, `platform.json`): GPU model, UUID, compute capability, driver, torch build, CUDA runtime,
   cuDNN version, TF32 for matmul and cuDNN, cudnn.benchmark, deterministic flags, attention backends, Python and package
   versions, host, Slurm job (items 1-11 of `TT1/PLATFORM_PINS_FOR_FINAL_READ.md`). TF32 is set on for both, as the
   fit-job scorer `pn1_score.py` does.
3. **Platform gate** (`gate.json`). Platform key = GPU model + torch build + TF32 setting. A platform without a pinned
   reference is refused (exit 5; the DGX GB10 is refused, TT1 H-new-5). The pinned reference network of the platform is
   loaded by the battery's own loader and scored by the battery's own scorer on the gate rows; its stored fit-job logits
   must be reproduced **byte-identically** (all 2,496 float32 logits equal). Criterion fixed here, before any gate is run.
   On failure: `GATE FAILED: nothing scored`, exit 2, no row scored.
   - Gate rows: 39 whole batches of the stored run (batch k = rows 64k to 64k+63 of the FS1 evaluation order, k = 0, 8, ...,
     304), so batch composition equals the stored run's (TT1-D2: batching changes the last bits). The rows span the logit
     range: camera photos at the floor, FFHQ genuine and morphs, splices; on the two references the stored logits run from
     -3.6 to +3.5 with 369-498 of them between -2 and +2 (floor rows alone would hide platform differences).
   - Pinned references: **A100 PCIe 40 GB, torch 2.2.1, TF32 on**: FS1 `PN1_Sb_s403` (tar 8dec83b8...), stored by
     `pn1_score.py` in its fit job on a rented A100-PCIE-40GB (container smad_torch221_cu121_v1.sif). **WCSS H100, torch
     2.11.0+cu128 (~/dmenv), TF32 on**: AB1 `AB1_Sb_s408` (tar a84b551f...), stored by `pn1_score.py` in AB1 fit job
     6311579 on r18-8. Each reference is checked by tar, stored-logit and weight sha256 before use.
4. **Scoring** (`run.py score_rows`): the fit-job scorer's loop (`pn1_score.py`: `common.ImageItems` at the network's
   resolution, bilinear resize of the whole frame, batch 64 in manifest order, `common.forward_logit`, float32 logit, no flip,
   eval mode, no autocast). Every set keeps its manifest order, so a battery logit on a gated platform equals the fit-job
   logit of the same row on that platform. Writes `logits_<set>.npz` (id, logit, manifest sha256), `scores_eval.npz` (dev),
   `last_trainable.pt`, `meta.json`, and with `--train-manifest` the unique training rows (`logits_train.npz`, as
   pn1_score.py). The network loader is pluggable (`backbones.py`): both registered backbones are built by the training
   code's own `common.build_run_model(meta)`; CLIP ViT-B/16 LoRA is live; the DINOv3 ViT-L/16 entry is registered but refuses
   to run until its code pin (BB2 overlay `archs_a12.py`) and a DINOv3 reference network per platform are pinned.
5. **Statistics** (`stats.py`, `battery.json`): every row statistic, from the reviewed readers' own functions, imported
   unchanged (section 3). `battery.json` holds the platform, the gate, every set's manifest and logit hashes, the network's
   provenance, the reader files' sha256, all block outputs and the 20 audit rows (`rows.py`).

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
  (queued for the dispatcher, section 7). A new arm's fit job adds the same `python -m battery.run` lines after
  `pn1_score.py`, with `--ckpt $RUN` (train.py's last.pt + meta.json), `--ref` the H100 reference tar and
  `--train-manifest`.
- **Rented A100 PCIe** (container smad_torch221_cu121_v1.sif, torch 2.2.1): the same command; the driver uploads the four
  packs and `PN1_Sb_s403.tar`. Not yet smoke-tested on an A100 (no rented machine was used for v1).
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
  every set of every network is scored on one setting.
- **Statistics only.** `battery.read` prints numbers, seed ranges and the number of seeds; it prints no verdict, since
  the battery registers no rule. Booleans that are a registered rule of another experiment (for example PR1's Z2a
  `usable`) stay in the JSON but are not printed. Outputs that are TEST runs, that did not pass the gate, or whose logits
  changed since scoring are left out and listed. Records built from stored logits (`battery.stored`, for the regression)
  are shown only with `--include-stored` and are labelled.
- **Same platform within an arm.** The reader prints the platform of every arm and says when one arm mixes platforms.

## 5. Regression test (CPU, stored logits)

`python -m battery.regress` runs every block on the stored logits of every reviewed network that has them, and compares
every leaf of the reviewed per-network JSON record with the battery's value at the same path by exact equality.
Results: `regression_v1.json` (this folder), stdout `/mnt/t7/smad_next/BATTERY/regression_v1_stdout.txt`. See
`README.md` for the numbers and for every row that cannot be reproduced and why.

## 6. Audit rows without data (for the DATA role, through the lead)

See `MISSING_DATA.md`.

## 7. Open items before release

- H100 smoke (`/mnt/t7/smad_next/dispatch/submit_queue/wcss_battery_smoke.cmd`): gate on the H100 reference, then all four
  sets for AB1_Sb_s408 and AB1_A_s408; their dev logits must equal their stored fit-job logits on all 21,277 rows. Whether
  two different H100 nodes are byte-identical is not yet measured; if they are not, the gate fails everywhere but r18-8
  and the lead decides on a tolerance before any read (never after seeing a gate).
- A100 PCIe smoke: not run (no rented machine in v1).
- DINOv3 loader: needs the BB2 overlay pin and a DINOv3 reference network per platform.
- Pre-run check by the experiment-reviewer (lead launches).
