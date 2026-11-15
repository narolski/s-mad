# PN1 rented-A100 runbook (fallback for the eight fits and the reference row; amendment 6)

Machine: plain Docker host, image `pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime`, root, one A100 40 GB, 16 cores, no
Apptainer, no Slurm. Disk: at least 40 GB free under `/workspace` (pack 10.2 GB + reference tar 2.8 GB + one task's
extracted pack 10.2 GB at a time; each work folder is deleted after its task). The lead rents and destroys the machine
from the main session; this owner never calls the rental API. Connection as `src/AD4/vast/launch_remote.sh`: key by
path only (`PN1_SSH_KEY`, default the lead's key path), never printed or copied; `known_hosts` in the lease folder;
`BatchMode=yes`.

Inputs on the DGX: `/mnt/t7/smad_next/PN1/pn1_pack.tar` (+ `.sha256`, pinned `5c642790…`),
`/mnt/t7/smad_next/PN1/refnets.tar` (+ `.sha256`, `101da1e5…`, rebuilt byte-identical at 21:08),
`/mnt/t7/smad_next/PN1/athena_tasks/PN1_*/{run.sh,task.env}` (run.sh `42b335b6…`, unchanged).

## Steps (after the lead's "READY host port lease-folder")

```
cd /home/narolski/smad-next/src/PN1/rented
bash drive.sh HOST PORT LEASE setup     # uploads (about 13 GB), pip pins as the container definition, versions -> LEASE/pn1_setup.log
bash drive.sh HOST PORT LEASE smoke     # arm Bn, 200 steps, 64 rows: speed (it/s), PEAK_MIB, SMOKE_RC -> LEASE/pn1_smoke.txt
# report the three lines (speed, peak memory, rc) to the lead
# if SMOKE_RC=0: cancel the Athena set (amendment 6), command lock, one connection:
flock -w 300 /tmp/smadnext-athena-cmd.lock ssh -o BatchMode=yes plgpnarolski@athena.cyfronet.pl 'scancel 3545976 3545977; sacct -j 3545976,3545977 -X -n -o JobID,State'
bash drive.sh HOST PORT LEASE queue     # eight fits one after another, then the reference row
nohup setsid bash pull_loop.sh HOST PORT LEASE > /dev/null 2>&1 &    # pull + verify every 10 min; RELEASE when 9 of 9 verified
bash drive.sh HOST PORT LEASE status    # any time
```

Order of the remote queue: PN1_A_s401, PN1_B_s401, PN1_Bn_s401, PN1_C_s401, PN1_A_s402, PN1_B_s402, PN1_Bn_s402,
PN1_C_s402, then `score_ref_local.sh` (the eight SMDD ViT-B/16 recipe retrains). Each task writes
`/workspace/pn1/root/results/PN1/<task>.tar` + `.sha256` (run.sh's copy-back check). A failed task is rerun once
unchanged; a run with non-finite loss is not rerun. Expected time: about 1.5 h per fit at Athena's smoke rate (1.24
it/s), about 12 h for the whole queue.

Pulled results: `/mnt/t7/smad_next/PN1/results_rented/` (tars, `.sha256`, `logs/`). `pull` refuses to copy when the T7
drive has under 2 GB free. When all nine tars are verified, `drive.sh pull` writes the empty file `LEASE/RELEASE`, on
which the lead's guard destroys the machine.

Reading: `python3 -I ../tier1.py --results /mnt/t7/smad_next/PN1/results_rented` (then `report.py tier1`).

If the rental does not happen: nothing here runs; Athena (array 3545976, job 3545977) stays the platform.
