#!/usr/env/bin python

"""
check if all required python modules to install wradlib are installed on the machine
py_dwd_radar is built upon wradlib
"""

imports = ['numpy','matplotlib','scipy','h5py','netCDF4','xarray','xmltodict','gdal']
modules = {}

for x in imports:
    try:
        modules[x] = __import__(x)
        print("Successfully imported "+x+'.')
        print(modules[x].__version__)
    except ImportError:
        print("Error importing "+x+'.')