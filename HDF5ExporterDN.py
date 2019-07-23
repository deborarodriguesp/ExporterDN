##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: HazRunoff
#     Date: MARETEC IST, 24/05/2019
#
##################################################################


#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import os
import sys
import h5py
import numpy
import read_input_file
import datetime as dt

def initialize_file(file, year0, month0, day0, hour0, minute0, second0, prop, node_id):

    fin_txt = open(file, 'w')
    
    prop = prop.replace(' ', '_')
    
    fin_txt.writelines('Time Serie Results File\n')
    fin_txt.writelines('NAME                    : ' + 'Node_' + node_id + '\n')
    fin_txt.writelines('SERIE_INITIAL_DATA      : ' + str(int(year0)) + '.' + (str(int(month0)) + '.').rjust(4) \
                                                    + (str(int(day0)) + '.').rjust(4) + (str(int(hour0)) + '.').rjust(4) \
                                                    + (str(int(minute0)) + '.').rjust(4) + str(round(second0, 1)).rjust(5) + '\n')
    fin_txt.writelines('TIME_UNITS              : SECONDS' + '\n')
    fin_txt.writelines('Seconds'.rjust(13) + 'YY'.rjust(5) +'MM'.rjust(4) + 'DD'.rjust(4) \
                       + 'hh'.rjust(4) + 'mm'.rjust(4) + 'ss'.rjust(9) \
                       + prop.rjust(46) + '\n')
    fin_txt.writelines('<BeginTimeSerie>\n')

    fin_txt.close()

    return

def write_timeseries(year, month, day, hour, minute, second, property_values, timeseries_names, property, nodes_id):

    f = 0
    for name in timeseries_names:
        file = 'Node_' + name + '.ets'
        file_exists = False
        if not os.path.isfile(file):
            initialize_file(file, year[0], month [0], day[0], hour[0], minute[0], second[0], property, nodes_id[f])
            file_exists = True
        else:
            file_exists = True

        if file_exists:
            # Get initial date of time serie to calculate the seconds from the beginning to each instant
            fin_txt = open(file, 'r')
            fin_txt_lines = fin_txt.readlines()
            initial_time_string = fin_txt_lines[2]
            initial_time_string = initial_time_string.split(':')[1]
            year0 = int(initial_time_string.split()[0].replace('.',''))
            month0 = int(initial_time_string.split()[1].replace('.',''))
            day0 = int(initial_time_string.split()[2].replace('.',''))
            hour0 = int(initial_time_string.split()[3].replace('.',''))
            minute0 = int(initial_time_string.split()[4].replace('.',''))
            second0 = int(initial_time_string.split()[5].replace('.',''))
            fin_txt.close()
            
            # Initial date in datetime format
            d0 = dt.datetime(year0, month0, day0, hour0, minute0, second0)

            # Calculate the seconds from the beginning to each instant and write ieach line
            fin_txt = open(file, 'a')
            for l in range(numpy.shape(property_values)[0]):
                di = dt.datetime(int(year[l]), int(month[l]), int(day[l]), int(hour[l]), \
                                 int(minute[l]), int(second[l]))
                seconds_from_beginning = (di-d0).total_seconds()
                
                line_to_write = str(round(seconds_from_beginning,2)).rjust(14) + str(int(year[l])).rjust(5) + \
                                str(int(month[l])).rjust(4) + str(int(day[l])).rjust(4) + str(int(hour[l])).rjust(4) + \
                                str(int(minute[l])).rjust(4) + str(round(second[l],3)).rjust(9) + str(property_values[l][f]).rjust(45) + '\n'
                                
                fin_txt.writelines(line_to_write)

            fin_txt.close()
        f = f + 1

    return
    
def end_time_series(timeseries_names):

    for name in timeseries_names:
        file = 'Node_' + name + '.ets'
        fin_txt = open(file, 'a')
        
        fin_txt.writelines('<EndTimeSerie>')
        fin_txt.close()

    return

if __name__ == '__main__':

    read_input_file.init()
    
    ####### Get keywords values #######
    # Manage dates
    hdf_filepaths = read_input_file.hdf_filepaths
    timeseries_names = read_input_file.timeseries_names
    nodes_id = read_input_file.nodes_id
    hdf_group = read_input_file.hdf_group
    property = read_input_file.property


    # Sort HDF files
    hdf_filepaths.sort()
    
    for hdf in hdf_filepaths:
        print ("Reading file " + hdf)
        # Open HDF file
        fin_hdf = h5py.File(hdf, 'r')
        
        # Dealing with time
        time_keys = fin_hdf['Time'].keys()
        
        year = list()
        month = list()
        day = list()
        hour = list()
        minute = list()
        second = list()
        for k in time_keys:
            year.append(fin_hdf['Time'][k].value[0])
            month.append(fin_hdf['Time'][k].value[1])
            day.append(fin_hdf['Time'][k].value[2])
            hour.append(fin_hdf['Time'][k].value[3])
            minute.append(fin_hdf['Time'][k].value[4])
            second.append(fin_hdf['Time'][k].value[5])

        # Get the reach for each node considering the up node of the reach
        reaches_down_nodes = list(fin_hdf['Reaches']['Up'].value)
        
        pos = list()
        for n in nodes_id:
            pos.append(reaches_down_nodes.index(int(n)))

        # Dealing with datasets
        dataset_keys = list(fin_hdf[hdf_group].keys())
        
        property_values = numpy.zeros((len(dataset_keys),len(nodes_id)))
        i = 0
        for d in dataset_keys:
            dataset = fin_hdf[hdf_group][d].value
            j = 0
            for p in pos:
                property_values[i][j] = dataset[p]
                j = j + 1
            i = i + 1
        fin_hdf.close()
        
        write_timeseries(year, month, day, hour, minute, second, property_values, timeseries_names, property, nodes_id)
    end_time_series(timeseries_names)