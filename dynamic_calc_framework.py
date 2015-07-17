#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime

import pcraster as pcr
from pcraster.framework import DynamicModel

from outputNetcdf import OutputNetcdf
import virtualOS as vos

import logging
logger = logging.getLogger(__name__)

class CalcFramework(DynamicModel):

    def __init__(self, cloneMapFileName,\
                       pcraster_files, \
                       modelTime, \
                       output, inputEPSG = None, outputEPSG = None, resample_method = None):
        DynamicModel.__init__(self)
        
        # set the clone map
        self.cloneMapFileName = cloneMapFileName
        pcr.setclone(self.cloneMapFileName)
        
        # time variable/object
        self.modelTime = modelTime
        
        # output file name, folder name, etc. 
        self.output = output
        self.output['file_name'] = vos.getFullPath(self.output['file_name'], self.output['folder'])
        
        # input and output projection/coordinate systems 
        self.inputEPSG  =  inputEPSG
        self.outputEPSG = outputEPSG
        self.resample_method = resample_method

        # prepare temporary directory
        self.tmpDir = output['folder']+"/tmp/"
        try:
            os.makedirs(self.tmpDir)
            os.system('rm -r '+tmpDir+"/*")
        except:
            pass
        
        # pcraster input files
        self.pcraster_files = pcraster_files
        # - the begining part of pcraster file names (e.g. "pr" for "pr000000.001")
        self.pcraster_file_name = self.pcraster_files['directory']+"/"+\
                                  self.pcraster_files['file_name']

        # object for reporting
        self.netcdf_report = OutputNetcdf(cloneMapFileName, self.output['description'])       

        # make a netcdf file
        self.netcdf_report.createNetCDF(self.output['file_name'],\
                                        self.output['variable_name'],\
                                        self.output['unit'],\
                                        self.output['long_name'])
        
    def initial(self): 
        pass

    def dynamic(self):
        
        # re-calculate current model time using current pcraster timestep value
        self.modelTime.update(self.currentTimeStep())

        # for variables other than temperature and maximum temperature, just read them directly
        if self.output['variable_name'] != "temperature" or self.output['variable_name'] != "maximum_temperature":
            pcraster_map_file_name = pcr.framework.frameworkBase.generateNameT(self.pcraster_file_name,\
                                                                               self.modelTime.timeStepPCR) 
            pcr_map_values = vos.readPCRmapClone(v = pcraster_map_file_name,\
                                                 cloneMapFileName = self.cloneMapFileName,\
                                                 tmpDir = self.tmpDir,\
                                                 absolutePath = None, isLddMap = False,\
                                                 cover = None,\
                                                 isNomMap = False,\
                                                 inputEPSG = self.inputEPSG,\
                                                 outputEPSG = self.outputEPSG,\
                                                 method = self.resample_method)

        # for temperature and maximum temperature, we have to make sure that maximum temperature is higher than minimum temperature
        if self.output['variable_name'] == "temperature" or self.output['variable_name'] == "maximum_temperature":
            min_map_file_name = pcr.framework.frameworkBase.generateNameT(self.pcraster_files['directory']+"/tn", self.modelTime.timeStepPCR)
            max_map_file_name = pcr.framework.frameworkBase.generateNameT(self.pcraster_files['directory']+"/tx", self.modelTime.timeStepPCR)
            min_map_values = vos.readPCRmapClone(v = min_map_file_name,\
                                                 cloneMapFileName = self.cloneMapFileName,\
                                                 tmpDir = self.tmpDir,\
                                                 absolutePath = None, isLddMap = False,\
                                                 cover = None,\
                                                 isNomMap = False,\
                                                 inputEPSG = self.inputEPSG,\
                                                 outputEPSG = self.outputEPSG,\
                                                 method = self.resample_method)
            max_map_values = vos.readPCRmapClone(v = max_map_file_name,\
                                                 cloneMapFileName = self.cloneMapFileName,\
                                                 tmpDir = self.tmpDir,\
                                                 absolutePath = None, isLddMap = False,\
                                                 cover = None,\
                                                 isNomMap = False,\
                                                 inputEPSG = self.inputEPSG,\
                                                 outputEPSG = self.outputEPSG,\
                                                 method = self.resample_method)
            # make sure that maximum values are higher than minimum values
            max_map_values = pcr.max(min_map_values, max_map_values)
            if self.output['variable_name'] == "temperature": pcr_map_values = 0.50*(min_map_values + \
                                                                                     max_map_values)
            if self.output['variable_name'] == "maximum_temperature": pcr_map_values = pcr.max(min_map_values, max_map_values)
        
        # for precipitation, converting the unit from mm.day-1 to m.day-1
        if self.output['variable_name'] == "precipitation": pcr_map_values *= 0.001
        
        # reporting
        timeStamp = datetime.datetime(self.modelTime.year,\
                                      self.modelTime.month,\
                                      self.modelTime.day,0)
        self.netcdf_report.data2NetCDF(self.output['file_name'],\
                                       self.output['variable_name'],\
                                       pcr.pcr2numpy(pcr_map_values,vos.MV),\
                                       timeStamp)
