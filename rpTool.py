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
    with tempfile.TemporaryDirectory() as tmpOutputFolder:
        write_output_spreadsheet(quotes=quotes,
                                primer_sequences=primer_sequences,
                                part_sequences=part_sequences,
                                fragment_quotes=fragment_quotes,
                                construct_parts=construct_parts,
                                construct_sequences=construct_sequences,
                                errors=errors,
                                target=tmpOutputFolder+'/tmp.xlsx')
        shutil.copy(tmpOutputFolder+'/tmp.xlsx', outpoutXLSX_path)
    return True
