
from __future__ import print_function #Python 2.7 compatibility

#--------------------------------------------------------------
def undSpecKPP(_tilt_microrad, _taper_microm, _elev_microm):

    undLen = 1.220 #1.5 #[m] Distance between Undulator Motion "Axes"
    halfUndLen = 0.5*undLen
    tilt_halfUndLen_mm = _tilt_microrad*halfUndLen*1.e-03
    quart_taper_mm = 0.25*_taper_microm*1.e-03
    dyUU_mm = -tilt_halfUndLen_mm - quart_taper_mm #[mm] Upstream Upper displacement 
    dyUL_mm = -tilt_halfUndLen_mm + quart_taper_mm #[mm] Upstream Lower displacement
    dyDU_mm = tilt_halfUndLen_mm + quart_taper_mm #[mm] Downstream Upper displacement
    dyDL_mm = tilt_halfUndLen_mm - quart_taper_mm #[mm] Downstream Lower displacement
    elev_mm = _elev_microm*1.e-03

    print('dyUU=', round(dyUU_mm, 6), 'dyUL=', round(dyUL_mm, 6), 'dyDU=', round(dyDU_mm, 6), 'dyUL=', round(dyDL_mm, 6), 'elev=', elev_mm)
    
    

    resKPP = 0
    return resKPP

#*********************************Entry
if __name__ == "__main__":

    #test call
    undSpecKPP(-50, -50, 300)
