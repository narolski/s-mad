#!/bin/bash
# SM1: contributor landmark stage (4 workers), log in OUT.
cd /tmp && exec nice -n 10 /home/narolski/mambamorph-code/.venv-spark/bin/python -I /home/narolski/smad-next/src/SM1/landmarks.py --stage contrib --workers 4 > /mnt/t7/smad_next/SM1/landmarks_contrib.log 2>&1
