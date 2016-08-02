import pyxrf_quant
import numpy
import matplotlib.pyplot as plt

cell01_cathode_scan = []
cell01_cathode_scan.append(2669)
for i in range(2681, 2718, 4):
    cell01_cathode_scan.append(i)
cell01_cathode_path = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_cathode/'

n=100

cell01_anode_scan = []
cell01_anode_scan.append(2679)
for i in range(2682, 2719, 8):
    cell01_anode_scan.append(i)

cell01_anode_path = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_anode/'

scanpath = cell01_anode_path

#scanlist = cell01_cathode_scan
#scanlist = [2669, 2705, 2717]
scanlist = cell01_anode_scan
#scanlist = [2679, 2718]

for scanid in scanlist:
    cusum, cumap = pyxrf_quant.sum_element( h5filepath = scanpath,
                                            h5filename = str(scanid)+'.h5')
    p,x = numpy.histogram(cumap.flatten(), bins=len(cumap.flatten())/n)
    x = x[:-1] + (x[1] - x[0])/2
    plt.plot(x, p, label = str(scanid))

plt.legend()
plt.show()



