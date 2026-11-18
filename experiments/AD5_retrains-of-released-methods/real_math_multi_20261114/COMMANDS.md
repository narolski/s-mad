# Exact commands for root AFTER independent prereview and source commit only

No staging/allocation done by author. Source namespace must be copied unchanged to:
  /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_real_math_multi_v1
The exact original code/wheels/crops inputs remain existing AD5/packs descriptors.
Create fresh dispatch/ad5_real_math_multi_v1_20261114 directory and copy exact reviewed PREREG.md, other-agent source+launcher review, owned-source Git commit/clean check and current site-preflight receipts there.
Root must replace PROPOSED release with exact decision GO_ONE_NEW_AD5_REAL_MATH_MULTI_V1 and all required hashes, author != reviewer, clean committed owned source, durable_free_gib>=50. Do not populate guessed review/site hashes. verify.release() must pass before launch; no previous claim/KEEP namespace may exist.

Source-only CPU verification:
  cd /home/narolski/smad-next/src/recovery_20261114/ad5_real_math_multi_v1
  /usr/bin/python3 -m unittest -v test_cpu.py
  bash -n worker.sh
  bash -n allocation_entry.sh
  sha256sum -c SHA256SUMS

Root-only launch on actual WCSS front end after release:
  tmux new-session -d -s ad5-real-math-multi-v1 'python3 -I /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_real_math_multi_v1/launch.py'
Actual srun argv is pinned in launch.py: --verbose --immediate=60 --job-name=ad5-real-math-multi-v1 --partition=lem-gpu-interactive --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=120G --gres=gpu:hopper:1,storage:local:150G --time=00:15:00 --extra=FORCE_RM_TMPDIR --pty /bin/bash .../allocation_entry.sh
No job/resource query, exclusions, migration, cancel, autoretry or old job action. Root must independently reconcile native terminal state after durable worker/node records. Full model/checkpoint/data access remains forbidden before this exact release.
