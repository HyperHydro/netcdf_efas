import pcraster as pcr
import netCDF4 as nc
import glob

# list of netcdf files 
netcdf_files = glob.glob("/scratch/edwin/input/forcing/hyperhydro_wg1/EFAS/netcdf_latlon/*/temperature/*.nc")

# correct attribute information (references)
references = "Ntegeka et al., 2013. EFAS-Meteo: A European daily high-resolution gridded meteorological data set. JRC Technical Reports. doi: 10.2788/51262 ; Burek et al., 2013. Evaporation Pre-Processor for the LISFLOOD Water Balance and Flood Simulation Model. JRC Technical Reports. doi: 10.2788/26000 "

# correct attribute information (for average temperature)
description = 'Daily mean temperature (ta) ; calculated using ta = (tx+tn)/2 ; with tx and tn are the maximum and minimum temperature values.'

for ncFileName in netcdf_files:

    print ncFileName
    
    # open netcdf file
    rootgrp = nc.Dataset(ncFileName,'a')
    
    # correcting the attribute information
    rootgrp.description = description

    print rootgrp.references
    print rootgrp.description
    
    rootgrp.sync()
    rootgrp.close()
