# Commands and missing prerequisites — SOURCE PREPARATION ONLY

Safe CPU/source checks on gx10:
```
cd /home/narolski/smad-next/src/recovery_20261114/ad5_full_math_v2
python3 -m unittest -v test_cpu.py test_retention.py test_release.py
bash -n body.sh allocation_entry.sh
sha256sum -c SHA256SUMS
```

Future ROOT ONLY, AFTER other independent review/adoption, clean commit, site/native/budget receipts and exact per-seed release (NOT authorized now): stage source unchanged to AD5/ad5_full_math_v2; create AD5/dispatch/ad5_full_math_v2_20261114/s401..s405 and parent AD5/logs/keep/ad5_full_math_v2_20261114; stage exact release dependencies. Do not stage any fabricated receipt/unknown hash.

For each seed401..405 in order, with fresh site check and all earlier native allocations closed:
```
python3 -I /lustre/pd03/hpc-narolski-1790461090/smad-next/AD5/ad5_full_math_v2/launch.py 401
```
Substitute ONLY exact next registered seed; launch.py performs sbatch once, never a loop/retry. Future native entry itself performs one own-job scontrol lookup for StartTime. Root uses shared WCSS flock and normal native reconciliation; no polling daemon. No submission was performed here.

After native terminal root writes ROOT_NATIVE_CLOSED.json in that seed dispatch, binding root_confirmed_terminal=true,seed,claim_sha256,native_state,native_receipt_file/native_receipt_sha256. It is closure evidence, not scientific success. Then root may invoke bundle.py SEED for opaque create-only archive. Transfer/verify archive on gx10 supplies actual arrival timestamp, not this bundle's timestamp.

Missing current budget/capacity/clean commit/source-independent review means HOLD. Converter/source equivalence and scientific score/read releases remain separately absent. Do not substitute legacy ad5w_train.sbatch, smoke v1r1 launch, interactive migration or any old job release.
