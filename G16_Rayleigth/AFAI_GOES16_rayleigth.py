# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


from glob import glob
from satpy.scene import Scene
from satpy.dataset import DatasetID
from satpy.utils import debug_on
debug_on()
import matplotlib.pyplot as plt

fl_ = glob("./data/OR_ABI-L1b-RadC*")

scn = Scene(reader='abi_l1b', filenames=fl_)

scn.load([DatasetID(name='C02', modifiers=('sunz_corrected', 'rayleigh_corrected')),DatasetID(name='C03', modifiers=('sunz_corrected', 'rayleigh_corrected')),DatasetID(name='C04', modifiers=('sunz_corrected', 'rayleigh_corrected'))])

new_scn = scn.resample(resampler='native')
dsids = new_scn.keys()
print(dsids)
#print(new_scn[dsids[0]][1000:1002, 1000:1002].values)

red = new_scn[dsids[0]][:].values
nir = new_scn[dsids[1]][:].values
swir = new_scn[dsids[2]][:].values

#fai = nir -(red + ((nir-red)/(swir-red))*(swir - red))

afai = nir -(red + ((swir-red)*(748 - 667)/(869-667)))

plt.figure(figsize=(20,10))
plt.imshow(afai)
plt.savefig('ifai.png')