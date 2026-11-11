# State at hand-over from the Codex loop

Read on 11 Nov 2026 from the Codex session "Eksperymenty z S-MAD" (10 Nov 22:41 to 11 Nov 14:02 CET)
and its hand-over note. The Codex loop is paused by the author since 11 Nov 13:59 CET. Its running
processes were left alive. No secrets are copied here; the transcript itself contains credentials and
stays out of git.

## Author instructions given there that still bind

- Prefer detector experiments and mechanism tests. The author twice objected to time spent on
  image generation.
- WCSS jobs: no node exclusion lists and no self-imposed restrictions (10 Nov). MAD22 scoring may be
  split into shards. Consider `lem-gpu-normal` when `lem-gpu-short` is the slower queue.
- Discovery experiments should not wait in the WCSS queue; WCSS is for the large, methodologically
  complete runs (five seeds). Rented GPUs for speed, used fully.
- Vast: 100 USD in total (not per top-up). Last balance read by Codex: 12.33 USD. All four rented
  instances were closed after verified copy-back.
- Blackwell 4-bit floating point (NVFP4) is optional and must not silently change the precision of
  compared experiments.
- All datasets are licensed research data; they may be processed and copied to the author's Mac.
  The Mac and the DGX CPU may run work when the GPU is busy.
- Results are committed to the repository as they arrive.
- Deadline: 16 Nov, with experiments done by 14 Nov if possible.

## Still running on the DGX (started by Codex)

| Process | What | Until |
|---|---|---|
| PID 1623204, then controller 1637166 | 20 fits of a frozen CLIP head: two read-outs × with and without resize/compression augmentation × seeds 201 to 205, one after another | up to 66 h in total (about 3 h per fit) |
| Controller 1729673 | Scores each finished fit for sensitivity to photo acquisition ("PAS") | follows the fits |
| PID 1668495 | DiffAE generation for a fresh confirmation cohort (64 planned pairs, 48 usable) | 3 h limit from 13:38 CET |

Not finished there: task scoring (error rates) of those 20 fits. The script
`/tmp/opencode/astra-core20-evaluation-v1-source/prepare.py` has a syntax error and never ran.

## WCSS (last read by Codex, 13:54 CET)

- `6299123_[0-7]`: corrected MAD22 scoring, 8 shards, pending. Do not duplicate.
- `6300801`: A138 profile D3-A, pending. D3-N and D3-P finished (20-step profiles only).
- `6294928_[4-14]`: held; do not release.
- AB4 `6299453` failed: two MambaVision training replays diverge in loss before gradient clipping.
  Bitwise-repeatable MambaVision training is therefore not available; five-seed statistics are.

Access convention used by the running controllers: `flock -w 15 /tmp/opencode/wcss-client.lock ssh …`;
Slurm binaries in `/opt/slurm/current/bin/`; protocol edits under `/home/narolski/.smad-protocol.lock`.

## Results obtained by Codex on 11 Nov (commits `fd72565` to `0386400` in `mambamorph-code`, local only)

All use small heads on frozen features and small panels; none shows a shortcut removed.

| Study | Size | Result |
|---|---|---|
| Heads trained on GAN morphs against GAN reconstructions and self-morphs | 135 heads, 16 training pairs | Separates GAN reconstructions at AUC 0.73 to 0.78, but DiffAE at 0.26 to 0.32: no transfer between generators |
| Joint GAN + DiffAE training, uniform vs group-robust weighting | 10 heads, 16 + 74 pairs | No stable gain. Camera photos 0.84 / 0.82; StyleGAN3 held-out set 0.63 / 0.62; spread-matched set 0.457 / 0.458 |
| Old DiffAE-trained heads scored on the new GAN set | 150 heads | 0.41 to 0.52: no transfer |
| Face-region idea | — | Falsified with spread-matched controls |
| Token-normalisation idea (Astra E2) | — | Gate failed; those arms must not run |

Reading for this plan: these are small-scale versions of our gate 0 (a twin-trained head on existing
generator sets), and they came out negative. That lowers the odds for generator morphs and supports
doing the landmark family first. They do not settle it: 16 to 90 training pairs is far below the
planned 2,000.

## Changes to this plan

- Gate 0 is already partly answered (negative, underpowered). It is rerun only at the larger size.
- First round uses images that already exist; new generation is limited to what the GAN causal test
  and the landmark self-morphs need.
- WCSS job rules follow the 10 Nov ruling (no exclusion lists). The administrators' requirement
  `--extra=FORCE_RM_TMPDIR` and job IO through `$TMPDIR` stay.
- WCSS access uses the same lock file as the running controllers.
