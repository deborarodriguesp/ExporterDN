##################################################################
#
#     Developed by: Ana Isabel Oliveira
#     Project: Water4Ever
#     Date: MARETEC IST, 14/05/2019
#
##################################################################


#!/usr/bin/python
# -*- coding: utf-8 -*-

# Imports
import os
import sys

HDF_blocks = 0
NODES_blocks = 0
hdf_filepaths = []
timeseries_names = []
nodes_id = []
hdf_group = ''
property = ''

def read_line(line_to_read, type):

    if type == 'hdf':
        if "NAME" in line_to_read:
            value = line_to_read.split(':')[1]
            value = value.replace('\n','')
            value = value.strip()
            value_type = 'filepath'
        else:
            print "Error reading HDF filename."
            sys.exit()
    
    elif type == 'timeserie':
        if "NAME" in line_to_read:
            value = line_to_read.split(':')[1]
            value = value.replace('\n','')
            value = value.strip()
            value_type = 'timeserie_name'
        elif "DN_NODE_ID" in line_to_read:
            value = line_to_read.split(':')[1]
            value = value.replace('\n','')
            value = value.strip()
            value_type = 'node_id'
            
    elif type == 'parameter':
        if "HDF_GROUP" in line_to_read:
            value = line_to_read.split(':')[1]
            value = value.replace('\n','')
            value = value.strip()
            value_type = 'hdf_group'
        elif "PROPERTY" in line_to_read:
            value = line_to_read.split(':')[1]
            value = value.replace('\n','')
            value = value.strip()
            value_type = 'property'
        else:
            print "Error reading HDF property."
            sys.exit()
            
    else:
        pass
    return value, value_type

def read_file(input_file):

    fin = open(input_file)
    fin_lines = fin.readlines()

    for nlin in range(len(fin_lines)):
        if "!" in  fin_lines[nlin]:
            pass
            
        # Count HDF blocks
        elif "<BeginHDF5File>" in fin_lines[nlin]:
            global HDF_blocks
            global hdf_filepaths
            
            HDF_blocks = HDF_blocks + 1
            i = 1
            while not "<EndTimeSerie>" in fin_lines[nlin+i]:
                try:
                    v, v_type = read_line(fin_lines[nlin+1], 'hdf')
                    hdf_filepaths.append(v)
                    break
                except:
                    i = i + 1
        
        # Count NODEs blocks
        elif "<BeginTimeSerie>" in fin_lines[nlin]:
            global NODES_blocks
            global timeseries_names
            global nodes_id
            
            NODES_blocks = NODES_blocks + 1
            i = 1
            while not "<EndTimeSerie>" in fin_lines[nlin+i]:
                try:
                    v, v_type = read_line(fin_lines[nlin+i], 'timeserie')
                    if v_type == 'timeserie_name':
                        timeseries_names.append(v)
                    elif v_type == 'node_id':
                        nodes_id.append(v)
                    else:
                        pass
                    i = i + 1
                except:
                    i = i + 1
        
        # Get property to extract
        elif "<BeginParameter>" in fin_lines[nlin]:
            global hdf_group
            global property
            
            i = 1
            while not "<EndParameter>" in fin_lines[nlin+i]:
                try:
                    v, v_type = read_line(fin_lines[nlin+i], 'parameter')
                    if v_type == 'hdf_group':
                        hdf_group = v
                    elif v_type == 'property':
                        property = v
                    else:
                        pass
                    i = i + 1
                except:
                    i = i + 1
        
        else:
            pass

    fin.close()
    
    return

def check_variables():

    if HDF_blocks==0:
        print ('\n   ERROR:      No HDF blok is defined. \n')
        sys.exit()
    
    if NODES_blocks==0:
        print ('\n   ERROR:      No TIMESERIE blok is defined. \n')
        sys.exit()
        
    if len(timeseries_names) != len(nodes_id):
        print ('\n   ERROR:      Check TIMESERIE bloks. The number of TIMESERIES names is different from DN_NODES_ID. \n')
        sys.exit()
    
    if hdf_group == '' and property == '':
        print ('\n   ERROR:      No <BeginParameter>/<EndParameter> block is defined. \n')
        sys.exit()
        
    if hdf_group == '' and property != '':
        print ('\n   ERROR:      No HDF_GROUP is defined in <BeginParameter>/<EndParameter> block. \n')
        sys.exit()
        
    if hdf_group != '' and property == '':
        print ('\n   ERROR:      No PROPERTY is defined in <BeginParameter>/<EndParameter> block. \n')
        sys.exit()
    

    return
    
def init():

    print ('\n   WARNING: Be careful!!! Do not use spaces and special characters in the names and directories!!!\n')
    
    input_file = 'input.dat'
    
    # Define_global_variables()
    read_file(input_file)
    check_variables()