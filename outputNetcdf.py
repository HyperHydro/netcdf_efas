#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import datetime
import time
import re
import subprocess
import netCDF4 as nc
import numpy as np
import pcraster as pcr
import virtualOS as vos

# the following dictionary is needed to avoid open and closing files
filecache = dict()

class OutputNetcdf():
    
    def __init__(self, mapattr_dict,\
                       cloneMapFileName = None,\
                       netcdf_format = "NETCDF3_CLASSIC",\
                       netcdf_zlib = False,\
                       netcdf_attribute_dict = None,\
                       netcdf_attribute_description = None) 
        		
        # netcdf format and zlib setup
        self.format = netcdf_format
        self.zlib   = netcdf_zlib 

        # longitudes and latitudes
        if cloneMapFileName != None:\
           self.longitudes, self.latitudes, cellSizeInArcMin = self.set_latlon_based_on_cloneMapFileName(cloneMapFileName)
        if mapattr_dict != None:\
           self.longitudes, self.latitudes, cellSizeInArcMin = self.set_latlon_based_on_cloneMapFileName(cloneMapFileName)
        
        # default netCDF attributes
        important_information = "The dataset was resampled to "+str(cellSizeInArcMin)+" arc minute resolution. "
        self.attributeDictionary = {}
        self.attributeDictionary['institution']  = "European Commission - JRC and Department of Physical Geography, Utrecht University"
        self.attributeDictionary['title'      ]  = "EFAS-Meteo 5km for Rhine-Meuse - resampled to "+str(cellSizeInArcMin)+" arc minute resolution. "
        self.attributeDictionary['source'     ]  = "5km Gridded Meteo Database (C) European Commission - JRDC, 2014"
        self.attributeDictionary['history'    ]  = "The data were provided by Ad de Roo (ad.de-roo@jrc.ec.europa.eu) on 19 November 2014 and then converted by Edwin H. Sutanudjaja (E.H.Sutanudjaja@uu.nl) to netcdf. "
        self.attributeDictionary['history'    ] += important_information 
        self.attributeDictionary['references' ]  = "Ntegeka et al., 2013. EFAS-Meteo: A European daily high-resolution gridded meteorological data set. JRC Technical Reports. doi: 10.2788/51262 ; "
        self.attributeDictionary['references' ] += "Burek et al., 2013. Evaporation Pre-Processor for the LISFLOOD Water Balance and Flood Simulation Model. JRC Technical Reports. https://solismail.uu.nl/owa/redir.aspx?SURL=6Q5S2vveK4XowrqnrXKcfTo85LKqdv0QN1HiI5EFu5XAIipJaI7SCGgAdAB0AHAAcwA6AC8ALwBlAGMALgBlAHUAcgBvAHAAYQAuAGUAdQAvAGoAcgBjAC8AZQBuAC8AcAB1AGIAbABpAGMAYQB0AGkAbwBuAC8AZQB1AHIALQBzAGMAaQBlAG4AdABpAGYAaQBjAC0AYQBuAGQALQB0AGUAYwBoAG4AaQBjAGEAbAAtAHIAZQBzAGUAYQByAGMAaAAtAHIAZQBwAG8AcgB0AHMALwBsAGkAcwB2AGEAcAAtAGUAdgBhAHAAbwByAGEAdABpAG8AbgAtAHAAcgBlAC0AcAByAG8AYwBlAHMAcwBvAHIALQBsAGkAcwBmAGwAbwBvAGQALQB3AGEAdABlAHIALQBiAGEAbABhAG4AYwBlAC0AYQBuAGQALQBmAGwAbwBvAGQALQBzAGkAbQB1AGwAYQB0AGkAbwBuAC0AbQBvAGQAZQBsAA..&URL=https%3a%2f%2fec.europa.eu%2fjrc%2fen%2fpublication%2feur-scientific-and-technical-research-reports%2flisvap-evaporation-pre-processor-lisflood-water-balance-and-flood-simulation-model "
        self.attributeDictionary['comment'    ]  = "Please use this dataset only for Hyper-Hydro test bed experiments. " 
        self.attributeDictionary['comment'    ] += "For using it and publishing it, please acknowledge its source: 5km Gridded Meteo Database (C) European Commission - JRDC, 2014 and its reference: Ntegeka et al., 2013 (doi: 10.2788/51262). "
        self.attributeDictionary['comment'    ] += "The original data provided by JRC are in European ETRS projection, 5km grid; http://en.wikipedia.org/wiki/European_grid. "
        self.attributeDictionary['comment'    ] += important_information 

        # using a specific defined set of netCDF attributes
        if netcdf_attribute_dict != None:\        
            self.attributeDictionary = {}
            self.attributeDictionary['institution'] = output_netcdf['netcdf_attribute']['institution']
            self.attributeDictionary['title'      ] = output_netcdf['netcdf_attribute']['title'      ]
            self.attributeDictionary['source'     ] = output_netcdf['netcdf_attribute']['source'     ]
            self.attributeDictionary['history'    ] = output_netcdf['netcdf_attribute']['history'    ]
            self.attributeDictionary['references' ] = output_netcdf['netcdf_attribute']['references' ]
            self.attributeDictionary['comment'    ] = output_netcdf['netcdf_attribute']['comment'    ]
            self.attributeDictionary['description'] = output_netcdf['netcdf_attribute']['description']
        
        # extra netcdf attribute ('description')
        if netcdf_attribute_description != None: self.attributeDictionary['description']  = netcdf_attribute_description

        
    def set_latlon_based_on_cloneMapFileName(self, cloneMapFileName):

        # cloneMap
        cloneMap = pcr.boolean(pcr.readmap(cloneMapFileName))
        cloneMap = pcr.boolean(pcr.scalar(1.0))
        
        # properties of the clone maps
        # - numbers of rows and colums
        rows = pcr.clone().nrRows() 
        cols = pcr.clone().nrCols()
        # - cell size in arc minutes rounded to one value behind the decimal
        cellSizeInArcMin = round(pcr.clone().cellSize() * 60.0, 1) 
        # - cell sizes in ar degrees for longitude and langitude direction 
        deltaLon = cellSizeInArcMin / 60.
        deltaLat = deltaLon
        # - coordinates of the upper left corner - rounded to two values behind the decimal in order to avoid rounding errors during (future) resampling process
        x_min = round(pcr.clone().west(), 2)
        y_max = round(pcr.clone().north(), 2)
        # - coordinates of the lower right corner - rounded to two values behind the decimal in order to avoid rounding errors during (future) resampling process
        x_max = round(x_min + cols*deltaLon, 2) 
        y_min = round(y_max - rows*deltaLat, 2) 
        
        # cell centres coordinates
        longitudes = np.arange(x_min + deltaLon/2., x_max, deltaLon)
        latitudes  = np.arange(y_max - deltaLat/2., y_min,-deltaLat)

        #~ # cell centres coordinates
        #~ longitudes = np.linspace(x_min + deltaLon/2., x_max - deltaLon/2., cols)
        #~ latitudes  = np.linspace(y_max - deltaLat/2., y_min + deltaLat/2., rows)
        
        #~ # cell centres coordinates (latitudes and longitudes, directly from the clone maps)
        #~ longitudes = np.unique(pcr.pcr2numpy(pcr.xcoordinate(cloneMap), vos.MV))
        #~ latitudes  = np.unique(pcr.pcr2numpy(pcr.ycoordinate(cloneMap), vos.MV))[::-1]

        return longitudes, latitudes, cellSizeInArcMin  

    def set_latlon_based_on_mapattr_dict(self, mapattr_dict):

        # cell size/length/resolution 
        cellLength = mapattr_dict['cellsize']
        # - cell size in arc minutes rounded to one value behind the decimal
        cellSizeInArcMin = round(cellLength * 60.0, 1) 
        # - cell sizes in ar degrees for longitude and langitude direction 
        cellLength = cellSizeInArcMin / 60.
        deltaLat = cellLength
        deltaLon = cellLength

        # latitudes and longitudes
        latMax = mapattr_dict['yUL'] - deltaLat/2.
        latMin = mapattr_dict['yUL'] - deltaLat*mapattr_dict['rows'] + deltaLat/2.
        lonMin = mapattr_dict['xUL'] + deltaLon/2.
        lonMax = mapattr_dict['xUL'] + deltaLon*mapattr_dict['cols'] - deltaLon/2.
        
        # cell centre coordinates
        longitudes = np.arange(mapattr_dict['xUL'] + mapattr_dict['cellsize']*0.5, \
                               mapattr_dict['xUL'] + mapattr_dict['cellsize']*mapattr_dict['cols'], \
                               mapattr_dict['cellsize'])
        latitudes  = np.arange(mapattr_dict['yUL'] - mapattr_dict['cellsize']*0.5, \
                               mapattr_dict['yUL'] - mapattr_dict['cellsize']*mapattr_dict['rows'], \
                              -mapattr_dict['cellsize'])

        return longitudes, latitudes, cellSizeInArcMin  

    def createNetCDF(self, ncFileName, varName, varUnits, longName=None):

        rootgrp = nc.Dataset(ncFileName,'w',format= self.format)

        #-create dimensions - time is unlimited, others are fixed
        rootgrp.createDimension('time',None)
        rootgrp.createDimension('lat',len(self.latitudes))
        rootgrp.createDimension('lon',len(self.longitudes))

        date_time = rootgrp.createVariable('time','f4',('time',))
        date_time.standard_name = 'time'
        date_time.long_name = 'Days since 1901-01-01'

        date_time.units = 'Days since 1901-01-01' 
        date_time.calendar = 'standard'

        lat= rootgrp.createVariable('lat','f4',('lat',))
        lat.long_name = 'latitude'
        lat.units = 'degrees_north'
        lat.standard_name = 'latitude'

        lon= rootgrp.createVariable('lon','f4',('lon',))
        lon.standard_name = 'longitude'
        lon.long_name = 'longitude'
        lon.units = 'degrees_east'

        lat[:]= self.latitudes
        lon[:]= self.longitudes

        shortVarName = varName
        longVarName  = varName
        if longName != None: longVarName = longName

        var = rootgrp.createVariable(shortVarName,'f4',('time','lat','lon',),fill_value=vos.MV,zlib=self.zlib)
        var.standard_name = varName
        var.long_name = longVarName
        var.units = varUnits

        attributeDictionary = self.attributeDictionary
        for k, v in attributeDictionary.items(): setattr(rootgrp,k,v)

        rootgrp.sync()
        rootgrp.close()

    def changeAtrribute(self, ncFileName, attributeDictionary, closeFile = False):

        if ncFileName in filecache.keys():
            #~ print "Cached: ", ncFileName
            rootgrp = filecache[ncFileName]
        else:
            #~ print "New: ", ncFileName
            rootgrp = nc.Dataset(ncFileName,'a')
            filecache[ncFileName] = rootgrp

        for k, v in attributeDictionary.items(): setattr(rootgrp,k,v)

        rootgrp.sync()
        if closeFile == True: rootgrp.close()

    def addNewVariable(self, ncFileName, varName, varUnits, longName=None, closeFile = False):

        if ncFileName in filecache.keys():
            #~ print "Cached: ", ncFileName
            rootgrp = filecache[ncFileName]
        else:
            #~ print "New: ", ncFileName
            rootgrp = nc.Dataset(ncFileName,'a')
            filecache[ncFileName] = rootgrp

        shortVarName = varName

        var = rootgrp.createVariable(shortVarName,'f4',('time','lat','lon',) ,fill_value=vos.MV,zlib=self.zlib)
        var.standard_name = varName
        var.long_name = varName
        var.units = varUnits

        rootgrp.sync()
        if closeFile == True: rootgrp.close()

    def data2NetCDF(self, ncFileName, shortVarName, varField, timeStamp, posCnt = None, closeFile = False):

        if ncFileName in filecache.keys():
            #~ print "Cached: ", ncFileName
            rootgrp = filecache[ncFileName]
        else:
            #~ print "New: ", ncFileName
            rootgrp = nc.Dataset(ncFileName,'a')
            filecache[ncFileName] = rootgrp

        date_time = rootgrp.variables['time']
        if posCnt == None: posCnt = len(date_time)
        date_time[posCnt] = nc.date2num(timeStamp,date_time.units,date_time.calendar)

        rootgrp.variables[shortVarName][posCnt,:,:] = varField

        rootgrp.sync()
        if closeFile == True: rootgrp.close()

    def dataList2NetCDF(self, ncFileName, shortVarNameList, varFieldList, timeStamp, posCnt = None, closeFile = False):

        if ncFileName in filecache.keys():
            #~ print "Cached: ", ncFileName
            rootgrp = filecache[ncFileName]
        else:
            #~ print "New: ", ncFileName
            rootgrp = nc.Dataset(ncFileName,'a')
            filecache[ncFileName] = rootgrp

        date_time = rootgrp.variables['time']
        if posCnt == None: posCnt = len(date_time)

        for shortVarName in shortVarNameList:
            date_time[posCnt] = nc.date2num(timeStamp,date_time.units,date_time.calendar)
            rootgrp.variables[shortVarName][posCnt,:,:] = varFieldList[shortVarName]

        rootgrp.sync()
        if closeFile == True: rootgrp.close()

    def close(self, ncFileName):

        if ncFileName in filecache.keys():
            #~ print "Cached: ", ncFileName
            rootgrp = filecache[ncFileName]
        else:
            #~ print "New: ", ncFileName
            rootgrp = nc.Dataset(ncFileName,'a')
            filecache[ncFileName] = rootgrp

        # closing the file 
        rootgrp.close()

        # remove ncFilename from filecache
        if ncFileName in filecache.keys(): filecache.pop(ncFileName, None)
