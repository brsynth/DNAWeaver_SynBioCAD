#!/usr/bin/env python3

"""
Created on September 21 2019

@author: Melchior du Lac
@description: Galaxy script to query rpOptBioDes REST service

#script.py test_input.xml test_output.xlsx any_method

"""

import argparse
import sys
sys.path.insert(0, '/home/')
import rpTool
import tempfile
import tarfile
import glob
import logging
import os
import shutil

##
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Python wrapper to call OptBioDes using rpSBML')
    parser.add_argument('-input', type=str)
    parser.add_argument('-input_format', type=str)
    parser.add_argument('-output', type=str)
    parser.add_argument('-max_constructs', type=int)
    parser.add_argument('-method', type=str)
    params = parser.parse_args()
    if params.max_constructs==-1:
        max_cons = None
    else:
        max_cons = params.max_constructs
    if params.input_format=='tar':
        rpTool.runDNAWeaver_hdd(params.input,
                                params.output,
                                params.method,
                                max_cons)
    elif params.input_format=='sbol':
        #make the tar.xz 
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            input_tar = tmpOutputFolder+'/tmp_input.tar.xz'
            output_tar = tmpOutputFolder+'/tmp_output.tar.xz'
            with tarfile.open(input_tar, mode='w:xz') as tf:
                #tf.add(params.input)
                info = tarfile.TarInfo('single.rpsbml.xml') #need to change the name since galaxy creates .dat files
                info.size = os.path.getsize(params.input)
                tf.addfile(tarinfo=info, fileobj=open(params.input, 'rb'))
            rpTool.runDNAWeaver_hdd(input_tar,
                                    output_tar,
                                    params.method,
                                    max_cons)
            with tarfile.open(output_tar) as outTar:
                outTar.extractall(tmpOutputFolder)
            out_file = glob.glob(tmpOutputFolder+'/*.xlsx')
            if len(out_file)>1:
                logging.warning('There are more than one output file...')
            shutil.copy(out_file[0], params.output)
    else:
        logging.error('Cannot interpret input_format: '+str(params.input_format))
        exit(1)




