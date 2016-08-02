# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 17:06:11 2016

@author: xf05id1
"""

import matplotlib.animation as animation
import numpy as np
from pylab import *

def ani_frame():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    im = ax.imshow(rand(300,300),cmap='gray',interpolation='nearest')
    im.set_clim([0,1])
    fig.set_size_inches([5,5])


    tight_layout()


    def update_img(n):
        tmp = rand(300,300)
        im.set_data(tmp)
        return im

    #legend(loc=0)
    ani = animation.FuncAnimation(fig,update_img,300,interval=30)
    writer = animation.writers['ffmpeg'](fps=30)

    ani.save('/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/demo.mp4',writer=writer,dpi=100)
    return ani

