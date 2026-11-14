# Root-only future staging/release; nothing executed by author

Source /home/narolski/smad-next/src/recovery_20261114/ad5_real_math_multi_v1r1 must stage byteidentically to AD5/ad5_real_math_multi_v1r1 on WCSS; new dispatch/ad5_real_math_multi_v1r1_20261114 and logs/keep/ad5_real_math_multi_v1r1_20261114. Do not reuse v1 namespace.

CPU verification:
 cd /home/narolski/smad-next/src/recovery_20261114/ad5_real_math_multi_v1r1
 /usr/bin/python3 -m unittest -v test_cpu.py test_retention.py
 bash -n worker.sh body.sh allocation_entry.sh
 sha256sum -c SHA256SUMS

Only after other-agent R1 delta-review,clean committed scope/current site evidence and root exact ROOT_RELEASE:
 decision=GO_ONE_NEW_AD5_REAL_MATH_MULTI_V1R1
 durability_revision=R1_DIRECT_FSYNC_AND_SUPERVISED_720S
 supervisor_deadline_seconds=720
 all original36update/checkpoint/pin requirements remain; all review/source/site files must actually hash correctly; proposal root_authorized=false does not authorize.

Root future command on WCSS:
 tmux new-session -d -s ad5-real-math-multi-v1r1 'python3 -I /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_real_math_multi_v1r1/launch.py'

Pinned actual srun --pty resources remain1H100/8CPU/120G/150Glocal/15min,no exclusions/retry/jobactions. Early allocation epoch starts720s budget; TERM10s→KILL then shared60scollection+hashbudget. Timeout always INCOMPLETE. Root reconcile native terminal and exact technical artifacts; exit0 not production/scientific acceptance.
