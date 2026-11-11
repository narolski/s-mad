# SM1 rented-A100 runbook (ViT-B/16 LoRA fits; amendment A13)

Machine: plain Docker host, image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, root, one A100 40 GB, 16 cores,
about 80 GB disk under `/workspace`, no Slurm, no Apptainer. The lead rents and destroys it from the main session;
this owner never calls the rental API. SSH key by path only (`SM1_SSH_KEY`, default the lead's key path), never
printed or copied; `known_hosts` in the lease folder; `BatchMode=yes`.

## One command (the lead, after renting)

```
nohup setsid bash /home/narolski/smad-next/src/SM1/rented/drive.sh HOST PORT LEASE all > LEASE/sm1_all.log 2>&1 &
```

`all` runs, stopping at the first failure:
1. `setup`: GPU / cores / disk / `/dev/shm` printed; pinned packages as `src/athena/containers/smad_torch221_cu121_v1.def`
   (torch held at the image's 2.2.1); then for each of the 12 packs: local `.sha256` against the pin in `drive.sh`,
   free-disk check, upload, `sha256sum -c` on the machine, unpack, delete the tar (`unpack_one.sh`).
2. `smoke`: arm a, seed 401, 200 steps, 64 scored rows per manifest, the full audit set (`remote_smoke.sh`):
   speed, `PEAK_MIB`, `SMOKE_RC` → `LEASE/sm1_smoke.txt`.
3. `cancel`: only after `SMOKE_RC=0`: `scancel 3545957 3546034` on Athena (command lock), states logged.
4. `queue`: 12 fits one after another, detached on the machine: SM1B_{a,c,e,f}_s401, SM1B_{a,c,e,f}_s402, then
   SM1B_b_s401, SM1B_bp_s401, SM1B_b_s402, SM1B_bp_s402. A failed fit is rerun once unchanged; non-finite loss is not rerun.
5. pull every 10 minutes into `/mnt/t7/smad_next/SM1/results_rented/` (tars, `.sha256`, `logs/`), verify; when 12
   of 12 are verified, the empty file `LEASE/RELEASE` is written (the lead's guard destroys the machine). If the
   queue ends with fewer, no RELEASE; the log says which.

Single steps: `bash drive.sh HOST PORT LEASE setup|smoke|cancel|queue|pull|status`.

## Packs (12; 45.8 GB in total; pins = the files Athena's fits use)

`ad4_pack.tar` 11.19 GB (code, CLIP weights, AD4 evaluation frames); `sm1gpu_img_test` 10.70, `armsc` 6.63, `armsb`
6.46, `base` 5.52, `armf` 2.85, `audit` 1.52, `arme` 0.62, `jpegeval` 0.20; `sm1lora_manifests_v2` 0.09, `_b` 0.02,
`_audit` 0.001. Unpacked about 43 GB; peak disk about 55 GB.

## Per fit (`fit_local.sh`)

The training and scoring command lines of `src/SM1/lora_run.sh` with RECIPE m3, unchanged (6 loader workers, as the
Athena ViT-B/16 jobs); data from the once-unpacked packs. Then the audit set (A12 item 10, `sm1_lora_audit.py`).
Result `SM1B_<arm>_s<seed>.tar` (+ `.sha256`): `ad4eval/`, `ar1eval/`, `jpegeval/` (scores, metrics,
`last_trainable.pt`), `audit/` (scores_audit.npz, check.json), `meta.json`, `train.log`, `task_info.txt`.

## Expected time

AD4 measured 1.99 it/s on an A100 40 GB for this batch-256 step (52 min per 6,250 steps). Scoring about 10 to 15
min per fit (not measured on a rented card). Setup about 50 min at the AD4 rental's upload rate (23 MB/s). Total
about 14 h (first 8 fits after about 10 h).

Reading: `lora_read.py` on the extracted tars into a separate folder, `read_p3.py --dir ... --seeds 401,402`.
