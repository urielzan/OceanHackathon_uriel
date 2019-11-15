# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 23:51:31 2019

@author: on_de
"""

import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset
from osgeo import gdal,osr

def rebin(a, shape):
    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)


def regionGOES(data,region,nvl):
    if region == 'CONUS' and nvl == 'L1b':
        # CONUS
        data = rebin(data , [3000,5000])       
       
    elif region == 'CONUS' and nvl == 'L2':
        # CONUS
        data = rebin(data , [1500,2500]) 
        
    elif region == 'FULLDISK':
        # Full Disk
        data = rebin(data , [10848,10848])   
        
    return data

def extraeNetCDFL2(path,res):
    print ('Extrayendo datos NetCDF L2"...')

    # Abre el archivo nc con em modulo NetCDF4
    nc = Dataset(path)
    
    # Extrae los valores de la variable, desenmascarando los valores, geenera un numpy.array
    data = nc.variables['CMI'][:].data
    
    
    #data = np.ma.getdata(data)
    banda = path[path.find('M3C')+3:path.find('_G16')]  
    print (banda)
    # Busca y designa el valor nulo, este valor puede variar de acuerdo al archivo
    if banda == '01':        
        data[data == 1023.] = np.nan
    elif banda == '02':
        data[data == 4095.] = np.nan
    elif banda == '03':
        data[data == 1023.] = np.nan
    elif banda == '05':
        data[data == 1023.] = np.nan
    elif banda == '06':
        data[data == 1023.] = np.nan
    elif banda == '07':
        data[data == 16383.0] = np.nan
    
    # Obtiene la constante del punto de prespectiva y las multiplica por las coordenadas extremas
   
    data = data*nc.variables['CMI'].scale_factor + nc.variables['CMI'].add_offset
    
    H = nc.variables['goes_imager_projection'].perspective_point_height
    xmin = nc.variables['x_image_bounds'][0] * H
    xmax = nc.variables['x_image_bounds'][1] * H
    ymin = nc.variables['y_image_bounds'][1] * H
    ymax = nc.variables['y_image_bounds'][0] * H
   
    if res == 1:
        data = rebin(data , [3000,5000])
    elif res == 2:
        data = rebin(data , [1500,2500])
        
    nx = data.shape[0]
    ny = data.shape[1]
   
    # Cierra el dataset
    nc.close()
    
    return data, xmin, ymin, xmax, ymax, nx, ny

def creaTiff(data, xmin, ymin, xmax, ymax, nx, ny):
    print ('Creando tif...')
    
    # Parametros para la creacion del TIFF por medio de GDAL
    xres = (xmax - xmin) / float(ny)
    yres = (ymax - ymin) / float(nx)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    dst_ds = gdal.GetDriverByName('GTiff').Create('tmp.tif', ny, nx, 1, gdal.GDT_Float32)
    
    # Aplica la geotransformacion y la proyección
    dst_ds.SetGeoTransform(geotransform)    # Coordenadas especificas
    srs = osr.SpatialReference()            # Establece el ensamble
    srs.ImportFromProj4("+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs") # Proeyeccion Goes16
    dst_ds.SetProjection(srs.ExportToWkt()) # Exporta el sistema de coordenadas
    dst_ds.GetRasterBand(1).WriteArray(data)   # Escribe la banda al raster
    dst_ds.FlushCache()                     # Escribe en el disco
    
    dst_ds = None

pathC02 = 'CG_ABI-L2-CMIPC-M6C02_G16_s20191111831190_e20191111833560_c20191111838275.nc'    
pathC03 = 'CG_ABI-L2-CMIPC-M6C03_G16_s20191111831190_e20191111833560_c20191111838326.nc'
pathC04 = 'CG_ABI-L2-CMIPC-M6C04_G16_s20191111831190_e20191111833560_c20191111838338.nc'
  
data, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(pathC02,2)
np.save('c02.npy',data)
creaTiff(data, xmin, ymin, xmax, ymax, nx, ny)
ds = gdal.Open('tmp.tif')
red = ds.ReadAsArray()

data, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(pathC03,2)
np.save('c03.npy',data)
creaTiff(data, xmin, ymin, xmax, ymax, nx, ny)
ds = gdal.Open('tmp.tif')
nir = ds.ReadAsArray()

data, xmin, ymin, xmax, ymax, nx, ny = extraeNetCDFL2(pathC04,2)
np.save('c04.npy',data)
creaTiff(data, xmin, ymin, xmax, ymax, nx, ny)
ds = gdal.Open('tmp.tif')
swir = ds.ReadAsArray()

afai = nir -(red + ((nir-red)/(swir-red))*(swir - red))
#np.where(afai == 0.0,np.nan,afai)
#afai[afai == 0.] = np.nan

plt.figure(figsize=(20,10))
plt.imshow(afai)
plt.savefig('ifai.png')
creaTiff(afai, xmin, ymin, xmax, ymax, nx, ny)


