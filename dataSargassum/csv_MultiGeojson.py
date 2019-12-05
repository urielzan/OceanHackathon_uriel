#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 12:40:30 2019

@author: urielm
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from glob import glob
from datetime import datetime

files = glob('./csv/*.csv')
files.sort()

epoch = datetime.utcfromtimestamp(0)

for i in range(121,151):
    df = pd.read_csv('csv/incendios_2019'+str(i)+'0000.csv')
    df.insert(6,"time",(datetime.strptime('20191210000','%Y%j%H%M') - epoch).total_seconds() * 1000.0)
    df.insert(7,"i",1)
    
    ID = 1
    times = []
    
    for file in files:
        
        jday = file[file.find('2019')+4:file.find('.csv')-4]
        timeF = file[file.find('2019'):file.find('.csv')]
        
        if jday == str(i):
            
            df1 = pd.read_csv(file) 
            dt = datetime.strptime(timeF,'%Y%j%H%M')
            #time = dt.second + dt.hour*60*36000 + 1430391600000
            #time = ID
            #time = (dt.minute + dt.hour*60)
            time = (dt - epoch).total_seconds() * 1000.0
            
            df1.insert(6,"time",0)
            df1['time'] = time
            df1.insert(7,"i",0)
            df1['i'] = ID
            
            df = pd.concat([df,df1])
            
            times.append(time)
            
            ID = ID + 1

       
    
    df["geometry"] = df.apply(lambda x: Point(x["lng"], x["lat"]) , axis = 1)
    
    #df.rename(columns = {'ide':'id'}, inplace = True) 
    
    gdf = gpd.GeoDataFrame(df, geometry='geometry',crs={'init': 'epsg:4326'})
    
    gdf.to_file("geojson/PC_"+str(i)+".json", driver="GeoJSON")