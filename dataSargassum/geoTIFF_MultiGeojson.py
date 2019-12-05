#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 12:47:06 2019

@author: urielm
"""

import geopandas as gpd
from osgeo import gdal#,osr
import pandas as pd
#from shapely.geometry import Point
from glob import glob
from datetime import datetime
import os

epoch = datetime.utcfromtimestamp(0)

files = glob('./data_GeoTIFF/asi_2019*')
files.sort()

index = 0

for file in files:
    
    timeS = file[file.find('2019'):file.find('.tif')]
    
    ds = gdal.Open(file)
    
    gdal.Translate('data_GeoTIFF/tmp.tif',ds,options = gdal.TranslateOptions(bandList=[1]))
    
    os.system('gdal_polygonize.py data_GeoTIFF/tmp.tif data_Shapefile/'+timeS+'_out.shp')
    
    df = gpd.read_file('data_Shapefile/'+timeS+'_out.shp')
    
    df = df[df.DN == 255]
    
    df["area"] = round(df['geometry'].area,2)
    
    dateT = datetime.strptime(timeS,'%Y%m%d')
    time = (dateT - epoch).total_seconds() * 1000.0
    
    df['time'] = time
    
    df['fecha'] = dateT.strftime('%Y-%m-%dT%H:%SZ')
    
    df['index'] = index
    
    df['IDpolygon'] = range(1, len(df) + 1)
        
    df.to_file("data_Geojson/asi_"+timeS+".json", driver="GeoJSON")

    index = index + 1
    
files_json = glob('./data_Geojson/asi_2019*')
files_json.sort()    

gdf_b = gpd.read_file(files_json[0]) 
    
for json in files_json[1:]:    
    
    gdf_i = gpd.read_file(json)
    
    gdf_b = pd.concat([gdf_b,gdf_i])

gdf_b = gdf_b.to_crs({'init': 'epsg:4326'})
gdf_b.to_file("asi_multi.json", driver="GeoJSON")

multi_json = open('asi_multi.json','r')    
data_json = multi_json.read()
data_js = 'var asi = '+ data_json
multi_js = open('asi_multi.js','w')

multi_js.write(data_js)
multi_js.close()
multi_json.close()
