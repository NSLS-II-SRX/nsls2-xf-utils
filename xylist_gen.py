# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 21:45:27 2016

@author: xf05id1
"""

start_pt = [[40.5712, 22.6325], [40.3595, 22.865], [40.1856, 22.6639], [40.1338, 22.5888], [40.1062, 22.4691], [40.3929, 22.9605],
            [40.2036, 22.4967], [40.4958, 22.5094], [40.7262, 22.3589]]

xstep = 0.005
ystep = 0.005

xylist = []

numx = 4
numy = 3

for pt in start_pt:
  for i in range(numx+1):
      for j in range(numy+1):
          xylist.append([pt[0]+xstep*i, pt[1]+ystep*j])
          
          