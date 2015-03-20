#!/bin/sh
tmux new-session -n 'SRX Monitoring Session' -d '/nfs/xf05id1/src/nsls2-xf-utils/05id-mon.py'
tmux split-window -h -l 64 '/nfs/xf05id1/src/nsls2-xf-utils/05id2fe-mon.py'
tmux split-window -v -l 10
tmux -2 attach-session -d 
