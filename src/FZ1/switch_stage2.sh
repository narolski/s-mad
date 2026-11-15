#!/bin/bash
until [ -f /mnt/t7/smad_next/FZ1/feats/clip_mad/sg3.npz ]; do sleep 5; done
sleep 3
B=$(pgrep -f "^/bin/bash /home/narolski/smad-next/src/FZ1/run_feats.sh")
P=$(pgrep -f "fz1_feats.py --backbone clip_mad --set a43,sg3,eval,smdd,smdd_flip")
echo "killing bash $B python $P"
[ -n "$B" ] && kill $B
[ -n "$P" ] && kill $P
sleep 10
cd /mnt/t7/smad_next/FZ1 && setsid nohup /home/narolski/smad-next/src/FZ1/run_feats2.sh > /mnt/t7/smad_next/FZ1/run_feats2.out 2>&1 < /dev/null &
echo launched stage2
