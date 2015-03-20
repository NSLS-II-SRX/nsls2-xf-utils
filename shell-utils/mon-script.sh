#!/bin/sh
cd /nfs/xf05id1/src/nsls2-xf-utils
terminator -T 'DO NOT RESIZE ME' --geometry=1500x340+0+0 -x /nfs/xf05id1/.tmux/monitor.sh 2>/dev/null &
