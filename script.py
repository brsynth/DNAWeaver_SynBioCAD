#!/usr/bin/env python3

"""Create an optimized assembly plan for combinatorial designs.

Usage:
  script.py <input> <output> <assembly_method> [--constructs=<x>]

Where:
- <input> is a path to an .xml SBOL file containing constructs designs
  and sequences, e.g. "example.xml" 
- <output> is a path to the output spreadsheet e.g. "output.xlsx"
- <assembly_method> is either "gibson", "golden_gate", or "any_method".
  If "any_method" is selected, each construct can be built with any method.
  However, Golden Gate Assembly will have priority over Gibson Assembly.
- <constructs> is the max number of constructs to build (only used in tests)

Example
  script.py test_input.xml test_output.xlsx any_method

"""

from docopt import docopt
from methods import (
    get_assembly_plan_from_sbol,
    compute_all_construct_quotes,
    write_output_spreadsheet,
)

# PARSE THE SBOL FILE

if __name__ == "__main__":

    # PARSE THE COMMAN LINE PARAMETERS

    params = docopt(__doc__)

    # PARSE THE SBOL FILE
    
    design_data = get_assembly_plan_from_sbol(path=params["<input>"])
    print(params["<input>"])
    part_sequences, construct_parts, construct_sequences = design_data

    # COMPUTE ALL QUOTES
    constructs = params["--constructs"]
    assembly_strategy_data = compute_all_construct_quotes(
        construct_sequences=construct_sequences,
        part_sequences=part_sequences,
        assembly_method=params["<assembly_method>"],
        max_constructs=int(constructs) if constructs else None
    )
    quotes, primer_sequences, fragment_quotes, errors = assembly_strategy_data

    # WRITE THE RESULT

    write_output_spreadsheet(
        quotes=quotes,
        primer_sequences=primer_sequences,
        part_sequences=part_sequences,
        fragment_quotes=fragment_quotes,
        construct_parts=construct_parts,
        construct_sequences=construct_sequences,
        errors=errors,
        target=params["<output>"],
    )
    print ("Valid plans:", len([q for q in quotes if q is not None]))
