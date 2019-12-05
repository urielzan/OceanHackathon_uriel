# -*- coding: utf-8 -*-
"""
Created on Sun Dec  1 15:08:30 2019

@author: on_de
"""

from glob import glob

files = glob('.\geojson\*.json')
files.sort()


for file in files:
    
    jday = file[file.find('PC_'):file.find('.json')]
    
    f = open(file,'r')
    
    s = f.read()
    
    j = 'var '+jday+' = '+ s
    
    e = open('data_js/'+jday+'.js','w')
    e.write(j)
    e.close()
    f.close()