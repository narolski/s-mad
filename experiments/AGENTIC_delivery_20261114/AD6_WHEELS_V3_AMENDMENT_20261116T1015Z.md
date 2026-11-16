# AD6 WHEELS V3 amendment (env-only) — 2026-11-16, ~10:15Z

## Decision base
- Operator (author) decision 16 Nov 2026 ~09:45Z: option (A) — wheels v3, torch 2.1.2+cu121 for MADation B/L.
  Conditions attached: (1) authors' code and recipe unchanged; (2) environment qualifier recorded BEFORE scoring
  (this file, prereg-AD6 note); (3) smoke test first, 1 seed B on 1 node; PASS -> dispatch full B/L;
  (4) option (B) Athena remains fallback; (5) option (C) GB10 redundancy only after twin X_s401.
- Failure evidence (SMAD-next repo MONITOR_20261116T0910Z.md, logs keep/): 6336013 (B) + 6336015 (L) all 5 seeds
  FAILED (~82–84 s) with ncclInternalError (NCCL 2.14.3 / torch 2.0.1+cu118) on 4xH100 multi-GPU across 4 distinct
  nodes (r18-9 today; r14-9 / r18-4 historically — AD5 B/L never ran on WCSS, originals came from Athena).
  NCCL_P2P_DISABLE=1 probe 6336280: no help. 1xH100 probe 6336303: config+data+forward OK, but
  loss_image.backward() -> "CUDA error: an illegal instruction was encountered" (probe 6336330, CUDA_LAUNCH_BLOCKING=1).
  Cause: torch 2.0.1+cu118 (sm_80 build) vs H100 sm_90 in backward of CLIP/LoRA path.

## What changes (ENV ONLY)
| package | v2 (was) | v3 (now) |
|---|---|---|
| torch | 2.0.1+cu118 | 2.1.2+cu121 |
| torchvision | 0.15.2+cu118 | 0.16.2+cu121 |
| triton | 2.0.0 | 2.1.0 |
| fsspec | (absent) | 2023.4.0 (new dep of torch 2.1) |
| nvidia-*cu12 libs | (bundled in torch cu118 wheel) | explicit wheels (torch 2.1 cu121 deps) |

All other pins from `src/AD5/env/madation_requirements.txt` unchanged; Python 3.9 unchanged (cp39 wheels);
authors' code tar (`ad6w_code.tar`) and data pack (`ad6_sb_pack.tar`) UNCHANGED — reuse existing packs by SHA.
Machine qualifier: WCSS H100 nodes, driver 595.112.07 (exceeds CUDA 12.1 minimum 530).

## Receipts (independent verification)
- Local pack: `/home/narolski/ad6_stage/ad6w_wheels39_v3.tar` (4,185,989,120 bytes)
  sha256 `6ad91b394edb8f4abd9c874f17f214483c4a59a595c00b14c44bf11949c660b1`
- Remote WCSS copy: `/lustre/pd03/hpc-narolski-1790461090/smad-next/AD6/packs/ad6w_wheels39_v3.tar`
  sha256 verified server-side AFTER upload: `6ad91b394edb8f4abd9c874f17f214483c4a59a595c00b14c44bf11949c660b1` OK
- Wheel-level verification (all 15 wheels, independent source cross-check):
  - torch-2.1.2+cu121-cp39 sha256 `eaaf6907e3723c0ca6a91df5e01a7eef8cabec93120e9a50739f5a5f14a2aa46`
    == download.pytorch.org/whl/cu121 anchor
  - torchvision-0.16.2+cu121-cp39 sha256 `aa1325a6e041603deecefc569e64b8c75a6c9a1b876e29a2def298ba8456474d`
    == download.pytorch.org/whl/cu121 anchor
  - triton-2.1.0-cp39 sha256 `21544e522c02005a626c8ad63d39bdff2f31d41069592919ef281e964ed26446`
    == download.pytorch.org/whl/cu121/triton anchor
  - 12 nvidia-*-cu12 wheels + fsspec: sha256 == PyPI JSON API release digests (12/12 OK)
- Env spec diff (audit): `diff` of pin lines v2 vs v3 shows ONLY torch/torchvision/triton changes + new
  fsspec/nvidia deps. Repo copy: `src/AD6/wcss/madation_requirements_v3.txt`.
- v3 sbatch: `src/AD6/wcss/ad6w_v3.sbatch` (md5 e2aa10fc389523329dc347d6050b1e7a local ==
  `/lustre/.../AD6/ad6w_v3.sbatch` on WCSS). Task names `madation_{B,L}_v3sbr_s<seed>` (distinct from v2 names).
  `pip freeze` still captured into each result tar (`pip_freeze.txt`) — per-run environment receipt.

## Qualifier for the paper (carried into every downstream receipt row)
"AD6 MADation B/L runs on WCSS used env v3: torch 2.1.2+cu121 (was 2.0.1+cu118), torchvision 0.16.2+cu121,
triton 2.1.0, NCCL shipped with torch 2.1.2 (2.18.1). Reason: NCCL 2.14.3 ncclInternalError (4xH100) and
illegal-instruction in backward with torch 2.0.1+cu118 on H100 sm_90; authors' code and training recipe unchanged."

## Gate
Scoring of any v3-trained artifact is allowed ONLY after (a) smoke PASS and (b) full B/L results with jobs.json
+ pip_freeze receipts. If smoke FAILs -> stop, report, option (B) Athena fallback.

## v3.1 REVISION (16 Nov 2026 ~19:05Z) — pack + logging plumbing only, recipe/code UNCHANGED
- nvjitlink: v3 pack was missing nvidia-nvjitlink-cu12 (declared dep of nvidia-cusolver-cu12 11.4.5.107).
  Smoke 6339975 FAILED at pip ("Could not find a version ... nvidia-nvjitlink-cu12"). Wheel added:
  nvidia_nvjitlink_cu12-12.1.105-py3-none-manylinux1_x86_64.whl sha256 015fed699b390ce3b8a8578d822d501a
  4194d0a341d3859554067c1ab291cb85 == PyPI anchor. Pack rebuilt (17 entries, 4.0G):
  sha256 189968dfed80828feed091cbc4c78e754e2e77ffe8f2bcabb6c2049d246cc07d, verified server-side 18:38Z.
- Submission bug: header said L=; line 22 reads ${AD6_L}; smokes 6336514 + 6339945 died in ~2 s. Fixed header.
- Observability: v3.1 writes train_stdout.log DIRECTLY to $L/logs/keep/$T/ (local-scratch copies died with the
  job on SIGKILL; smoke 6340130's log was lost that way). Recipe and authors' code unchanged.
- New sbatch md5 (local == WCSS): 2d91c81592b446f4214bc20a8debfb54 (was e2aa10fc...).
