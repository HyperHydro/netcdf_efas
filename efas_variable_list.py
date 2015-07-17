#!/usr/bin/python
# -*- coding: utf-8 -*-

# dictionary for netcdf file names, variable names and units: 
netcdf_short_name = {}
netcdf_unit       = {}
netcdf_long_name  = {}
description       = {}

# pd Mean daily vapour pressure (hPa) 
efas_variable_name = "pd"
netcdf_short_name[efas_variable_name] = 'vapour_pressure'
netcdf_unit[efas_variable_name]       = 'hPa'
netcdf_long_name[efas_variable_name]  = 'daily_mean_vapour_pressure'
description[efas_variable_name]       = 'Mean daily vapour pressure (hPa).'

# pr Daily precipitation (m) between 6 UTC on the day specified and 6 UTC on the next day 
efas_variable_name = "pr"
netcdf_short_name[efas_variable_name] = 'precipitation'
netcdf_unit[efas_variable_name]       = 'm.day-1'
netcdf_long_name[efas_variable_name]  = 'daily_precipitation'
description[efas_variable_name]       = 'Daily precipitation between 6 UTC on the day specified and 6 UTC on the next day.'

# rg Downward_surface_solar_radiation) 
efas_variable_name = "rg"
netcdf_short_name[efas_variable_name] = 'downward_surface_solar_radiation'
netcdf_unit[efas_variable_name]       = 'J.m-2.day-1'
netcdf_long_name[efas_variable_name]  = 'calculated_downward_surface_solar_radiation'
description[efas_variable_name]       = 'Downward surface solar radiation (J.m-2.day-1), see the references for the methodology. '
description[efas_variable_name]      += 'Note that the unit is J/m2/day as given in the Lisvap manual p.18 (althoughh there is a tiny error it should be J m-2 d-1 instead of Jm-2 d): '
description[efas_variable_name]      += 'https://ec.europa.eu/jrc/en/publication/eur-scientific-and-technical-research-reports/lisvap-evaporation-pre-processor-lisflood-water-balance-and-flood-simulation-model '

# tn Daily minimum temperature (°C) between 18 UTC and 6 UTC (i.e. during the preceding night) at 2m 
efas_variable_name = "tn"
netcdf_short_name[efas_variable_name] = 'minimum_temperature'
netcdf_unit[efas_variable_name]       = 'degrees Celcius'
netcdf_long_name[efas_variable_name]  = 'daily_minimum_temperature'
description[efas_variable_name]       = 'Daily minimum temperature between 18 UTC and 6 UTC (i.e. during the preceding night) at 2m.'

# tx Daily maximum temperature (°C) between 6 UTC and 18 UTC (i.e. during daytime) at 2m 
efas_variable_name = "tx"
netcdf_short_name[efas_variable_name] = 'maximum_temperature'
netcdf_unit[efas_variable_name]       = 'degrees Celcius'
netcdf_long_name[efas_variable_name]  = 'daily_maximum_remperature'
description[efas_variable_name]       = 'Daily maximum temperature between 6 UTC and 18 UTC (i.e. during daytime) at 2m.'

# ta Daily mean temperature (°C) is calculated using ta=(tx+tn)/2 
efas_variable_name = "ta"
netcdf_short_name[efas_variable_name] = 'temperature'
netcdf_unit[efas_variable_name]       = 'degrees Celcius'
netcdf_long_name[efas_variable_name]  = 'daily_mean_precipitation'
description[efas_variable_name]       = 'Daily mean temperature (ta) ; calculated using ta = (tx+tn)/2 ; with tx and ta are the maximum and minimum temperature values.'

# ws Mean daily wind speed at 10 metres (m/s) calculated from 3-hourly observations (0-24 UTC) 
efas_variable_name = "ws"
netcdf_short_name[efas_variable_name] = 'wind_speed'
netcdf_unit[efas_variable_name]       = 'm.s-1'
netcdf_long_name[efas_variable_name]  = 'daily_mean_wind_speed'
description[efas_variable_name]       = 'Mean daily wind speed at 10 m height (m/s) calculated from 3-hourly observations (0-24 UTC).'

