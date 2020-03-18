#!/usr/bin/env python3

from docopt import docopt
from methods import (
    get_assembly_plan_from_sbol,
    compute_all_construct_quotes,
    write_output_spreadsheet,
)
import logging
import tempfile
import shutil
import tarfile
import glob
import os

## run using HDD 3X less than the above function
#
#
def runDNAWeaver_hdd(inputTar, outputTar, assembly_method='any_method', max_constructs=None):
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        with tempfile.TemporaryDirectory() as tmpInputFolder:
            tar = tarfile.open(inputTar, mode='r')
            tar.extractall(path=tmpInputFolder)
            tar.close()
            for sbol_path in glob.glob(tmpInputFolder+'/*'):
                if sbol_path.split('/')[-1].split('.')[-1]=='xml':
                    fileName = sbol_path.split('/')[-1].replace('.sbol', '').replace('.xml', '').replace('.rpsbml', '')
                    runDNAWeaver(sbol_path, tmpOutputFolder+'/'+fileName+'.xlsx', assembly_method, max_constructs)
            with tarfile.open(outputTar, mode='w:xz') as ot:
                for excel_path in glob.glob(tmpOutputFolder+'/*'):
                    fileName = str(excel_path.split('/')[-1])
                    info = tarfile.TarInfo(fileName)
                    info.size = os.path.getsize(excel_path)
                    ot.addfile(tarinfo=info, fileobj=open(excel_path, 'rb'))

#########################################################################################
################################### DNA Weaver ##########################################
#########################################################################################

def runDNAWeaver(inputSBOL_path, outpoutXLSX_path, assembly_method='any_method', max_constructs=None):
    if not assembly_method in ['gibson', 'golden_gate', 'any_method']:
        logging.warning('Did not resognise assembly method input: '+str(assembly_method)+'. Reverting to any_method')
        assembly_method = 'any_method'
    # PARSE THE SBOL FILE
    part_sequences, construct_parts, construct_sequences = get_assembly_plan_from_sbol(path=inputSBOL_path)
    # COMPUTE ALL QUOTES
    quotes, primer_sequences, fragment_quotes, errors = compute_all_construct_quotes(
                                                    construct_sequences=construct_sequences,
                                                    part_sequences=part_sequences,
                                                    assembly_method=assembly_method,
                                                    max_constructs=int(max_constructs) if max_constructs else None)
    # WRITE THE RESULT
    write_output_spreadsheet(quotes=quotes,
                            primer_sequences=primer_sequences,
                            part_sequences=part_sequences,
                            fragment_quotes=fragment_quotes,
                            construct_parts=construct_parts,
                            construct_sequences=construct_sequences,
                            errors=errors,
                            target=outpoutXLSX_path)
    return True
