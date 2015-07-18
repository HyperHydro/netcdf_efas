import pcraster as pcr
import netCDF4 as nc
import glob

# list of netcdf files 
netcdf_files = glob.glob("/scratch/edwin/input/forcing/hyperhydro_wg1/EFAS/netcdf_latlon/03min/*/*.nc")

# correct attribute information (references)
references = "Ntegeka et al., 2013. EFAS-Meteo: A European daily high-resolution gridded meteorological data set. JRC Technical Reports. doi: 10.2788/51262 ; Burek et al., 2013. Evaporation Pre-Processor for the LISFLOOD Water Balance and Flood Simulation Model. JRC Technical Reports. doi: 10.2788/26000 "

for ncFileName in netcdf_files:

    print ncFileName
    
    # open netcdf file
    rootgrp = nc.Dataset(ncFileName,'a')
    
    # correcting the reference information
    rootgrp.references = references

    print rootgrp.references
    
    rootgrp.sync()
    rootgrp.close()
