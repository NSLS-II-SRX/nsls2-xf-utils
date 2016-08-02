echo "los gehts";
# 1um stepsize - unterste reihe (Reihe 0)
#./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-100 --xnumstep=50 --xstepsize=1 --xstart=-100 --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # langweilig
#./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-100 --xnumstep=50 --xstepsize=1 --xstart=-50  --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # langweilig
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-100 --xnumstep=50 --xstepsize=1 --xstart=0    --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 1
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-100 --xnumstep=50 --xstepsize=1 --xstart=50   --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 2

# 1um stepsize -  (Reihe 1)
#./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=1 --xstart=-100 --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # spaeter
#./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=1 --xstart=-50  --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # spaeter
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=1 --xstart=0    --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 3
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=1 --xstart=50   --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 4

# 1um stepsize -  (Reihe 2)
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=0 --xnumstep=50 --xstepsize=1 --xstart=-100 --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 5
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=0 --xnumstep=50 --xstepsize=1 --xstart=-50  --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 6
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=0 --xnumstep=50 --xstepsize=1 --xstart=0    --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 7
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=0 --xnumstep=50 --xstepsize=1 --xstart=50   --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 8

# 1um stepsize -  (Reihe 3) oberste Reihe
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=50 --xnumstep=50 --xstepsize=1 --xstart=-100 --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 9
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=50 --xnumstep=50 --xstepsize=1 --xstart=-50  --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 10
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=50 --xnumstep=50 --xstepsize=1 --xstart=0    --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 11
#./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=50 --xnumstep=50 --xstepsize=1 --xstart=50   --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # langweilig

# 0.5mu stepsize - in Reihe 1
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=0.5 --xstart=-100 --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 12
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=0.5 --xstart=-75  --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 13
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=0.5 --xstart=-50  --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 14
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=0.5 --xstart=-25  --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 15

# 0.5mu stepsize - in Reihe 1
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-25 --xnumstep=50 --xstepsize=0.5 --xstart=-100 --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 16
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-25 --xnumstep=50 --xstepsize=0.5 --xstart=-75  --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 17
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-25 --xnumstep=50 --xstepsize=0.5 --xstart=-50  --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 18
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-25 --xnumstep=50 --xstepsize=0.5 --xstart=-25  --ynumstep=50 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam; # 19

# 1um stepsize 2.5s -  (Reihe 1)
./srx-2dscan-sdd.py --detname=XF:05IDA{IM:1} --ystart=-50 --xnumstep=50 --xstepsize=1 --xstart=-50  --ynumstep=50 --ystepsize=1 --wait=0.1 --acqtime=2.5 --acqnum=1 --checkbeam; # 20

echo "done";
