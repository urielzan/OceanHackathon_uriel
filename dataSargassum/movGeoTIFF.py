#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 12:04:36 2019

@author: urielm
"""

#from glob import glob
import os 

tif = 'data_GeoTIFF/asi.tif'

xmin,ymin = 499980.000, 2290200.000
xmax, ymax = 609780.000, 2400000.000

inc = 25000

for i in range(1,26,5):
    os.system('gdal_translate -a_ullr '+str(xmin+inc)+' '+str(ymax+inc)+' '+str(xmax+inc)+' '+str(ymin+inc)+' '+str(tif)+' data_GeoTIFF/asi_201907'+'{:02d}'.format(i)+'.tif')
    inc = inc - 5000

print (inc)