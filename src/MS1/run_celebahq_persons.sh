#!/bin/bash
# MS1 CelebA-HQ persons: casia + calib in parallel, then refs, then group (thread caps, nice 10)
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2
P=/home/narolski/mambamorph-code/.venv-spark/bin/python
cd /home/narolski/smad-next/src/MS1
nice -n 10 $P -I celebahq_persons.py casia > /mnt/t7/smad_next/MS1/logs/chq_casia.log 2>&1 &
nice -n 10 $P -I celebahq_persons.py calib > /mnt/t7/smad_next/MS1/logs/chq_calib.log 2>&1
wait
nice -n 10 $P -I celebahq_persons.py refs > /mnt/t7/smad_next/MS1/logs/chq_refs.log 2>&1
nice -n 10 $P -I celebahq_persons.py group > /mnt/t7/smad_next/MS1/logs/chq_group.log 2>&1
echo CHQ_DONE
