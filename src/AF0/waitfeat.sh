#!/usr/bin/env bash
# waitfeat.sh <backbone> <list> : block until feat/<backbone>/<list>.done equals the list length
n=$(( $(wc -l < /mnt/t7/smad_next/AF0/lists/$2.csv) - 1 ))
until [ "$(cat /mnt/t7/smad_next/AF0/feat/$1/$2.done 2>/dev/null)" = "$n" ]; do sleep 30; done
