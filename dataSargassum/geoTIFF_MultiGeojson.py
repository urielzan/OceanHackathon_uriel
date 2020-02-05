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

def geotiffTogeojson(dia):
	epoch = datetime.utcfromtimestamp(0)

	files = glob('./data_GeoTIFF/*201907'+dia+'*.tif')
	files.sort()

	index = 0

	for file in files:

		tile = file[file.find('TIFF/')+5:file.find('_2019')]
		timeS = file[file.find('2019'):file.find('_AFAI')]    
		dateT = datetime.strptime(timeS,'%Y%m%dT%H%M%S')
		time = (dateT - epoch).total_seconds() * 1000.0

		print(tile)
		print(dateT.strftime('%Y-%m-%dT%H:%M:%SZ'))
		#print(time)

		#ds = gdal.Open(file)

		#gdal.Translate('data_GeoTIFF/tmp.tif',ds,options = gdal.TranslateOptions(bandList=[1]))

		os.system('gdal_polygonize.py '+file+' data_Shapefile/'+tile+'_'+timeS+'_out.shp')

		df = gpd.read_file('data_Shapefile/'+tile+'_'+timeS+'_out.shp')

		df = df[df.DN == 1]

		if len(df)>= 1:

			df["area"] = round(df['geometry'].area,2)
			#dateT = datetime.strptime(timeS,'%Y%m%d')
			#time = (dateT - epoch).total_seconds() * 1000.0
			df['time'] = time
			#df['time'] = df['time'].astype('datetime64[ns]')

			df['fecha'] = dateT.strftime('%Y-%m-%dT%H:%M:%S.0Z')
			#df['fecha'] = df['fecha'].astype('datetime64[ns]')
			#df['fecha'] = pd.to_datetime(df['fecha'])

			df['tile'] = tile    

			df['index'] = index

			df['IDpolygon'] = range(1, len(df) + 1)

			df.to_file("data_Geojson/afai_"+tile+'_'+timeS+".json", driver="GeoJSON")

			index = index + 1

def multiGeojson(dia):
	files_json = glob('./data_Geojson/*T16QEJ*201907*.json')
	files_json.sort()    

	gdf_b = gpd.read_file(files_json[0]) 
	gdf_b = gdf_b.to_crs({'init': 'epsg:4326'})

	print ('Creando multijson '+dia+'...')
	for json in files_json[1:]:    

		gdf_i = gpd.read_file(json)

		gdf_i = gdf_i.to_crs({'init': 'epsg:4326'})

		gdf_b = pd.concat([gdf_b,gdf_i])

	#gdf_b = gdf_b.to_crs({'init': 'epsg:4326'})
	gdf_b.to_file("afai_T16QEJ_201907_multi.json", driver="GeoJSON")

def jsVariable():
	multi_json = open('afai_T16QEJ_201907_multi.json','r')    
	data_json = multi_json.read()
	data_js = 'var asi = '+ data_json
	multi_js = open('afai_T16QEJ_201907_multi.js','w')

	multi_js.write(data_js)
	multi_js.close()
	multi_json.close()

def geojsonShapefile(dia):
	#file_multi = glob('./data_multiGeojson/*.json')

	df = gpd.read_file('afai_201907_multi.json')
	df.to_file("data_multiShapefile/afai_201907_multi.shp", driver="ESRI Shapefile")


for file in glob('./data_TarGZ/*'):

	dia = file[file.find('201907')+6:file.find('201907')+8]
	print(dia)
	#geotiffTogeojson(dia)
#multiGeojson('julio')
jsVariable()
#geojsonShapefile('julio')
