# MONITOR 2026-11-16T1955Z (20:55 CET) — AD6 HOLD arms onto Athena (user instruction 19:30 CET)

- **Athena UP**: login01, 48-node plgrid-gpu-a100; but ~25 nodes `fail*` and partition effectively GPU-full:
  of 14 sampled mix nodes, all have 8/8 GPUs allocated except t0007 and t0048 (1 free each). Node RAM
  (memfs reservations) also heavily allocated. Our old pending job 3555043 untouched.
- **Pack upload DONE + VERIFIED**: 4 packs + sha sidecars (9,160,458,598 bytes total, 4m22s, ~33 MB/s,
  one rsync under the transfer flock) → `smad-next/AD6/packs/`:
  - ad6w_code.tar sha OK (968001b0...), ad5w_wheels39.tar sha OK (3bd18ded...), ad6_sb_pack.tar sha OK
    (2b5b2880...), ad6w_wheels39_v3.tar sha OK far-side (189968dfed80828feed091cbc4c78e754e2e77ffe8f2bcabb6c2049d246cc07d
    == local/PyPI anchor). Sidecar for v3 was absolute-path (from earlier staging) — fixed to relative on far side.
- **Athena adaptation of registered recipe** (code/recipe UNCHANGED, env v3 unchanged):
  `src/AD6/athena/ad6w_athena_v1.sbatch` (bash -n OK; scp'd to `smad-next/AD6/`). Site diffs vs
  src/AD6/wcss/ad6w_v3.sbatch (v3.1, md5 2d91c815...): L=/net/pr2/projects/plgrid/plggrestoration/smad-next/AD6
  (packs read from lustre project folder, work area in $MEMFS, result tar + live keep log to lustre),
  PYBIN=/usr/bin/python3.9 (Athena modules have NO 3.9; /usr/bin/python3.9 = 3.9.25, ensurepip OK; v3 wheels cp39),
  account plgmultivision-gpu-a100, partition plgrid-gpu-a100.
- **SMOKE attempt 1 (interactive)**: `srun --pty` 4-GPU alloc 3556444 queued 11 min, never scheduled
  (0 free GPUs on single nodes; free GPUs have no RAM room), revoked by us. User wanted interactive smoke,
  but the partition cannot give 4 GPUs today. No login was repeated; no lock misuse.
- **SMOKE attempt 2 (batch)**: job 3556457 `ad6athS`: 1 GPU, 8 CPUs, --mem=64G, -C memfs, 30-min TL,
  exclude t0010/t0014/t0020, ARM=B, seed 401, **AD6_BPG=64** (per-GPU batch of the registered WCSS H100
  layout; smoke-only override, script prints an explicit BPG-override line; production keeps gpu:4 =
  global batch 256). Pending (Priority) at submission; verdict from the live lustre keep log when running.
- **Plan on PASS**: array 401-405 ARM=B at `--gres=gpu:4 -c 32 --mem=96G` (H1); WCSS-owned HOLDS H1-H3
  get an Athena data-source twin note. sshare/sprio re-check after first runs (plgmultivision fair-share).
- **Risks**: (a) GPU scarcity — H1 production may queue hours; (b) memfs RAM near-full cluster-wide
  (t0001 963G/t0008 996G/t0037 996G allocated of 1024G) may keep --mem=96G jobs waiting longer than the
  GPUs themselves; (c) sdists easydict/openai-clip need setuptools build (no compiler required);
  (d) python3.9 is a system python, venv from ensurepip/venv OK.
