from docopt import docopt
from . import (
    get_assembly_plan_from_sbol,
    compute_all_construct_quotes,
    write_output_spreadsheet,
)
from .Args import build_args_parser

# PARSE THE SBOL FILE

if __name__ == "__main__":

    # PARSE THE COMMAN LINE PARAMETERS
    parser = build_args_parser(
        prog = 'dnaweaver_cli',
        description='Create an optimized assembly plan for combinatorial designs'
    )
    args = parser.parse_args()

    # PARSE THE SBOL FILE    
    design_data = get_assembly_plan_from_sbol(path=args.input)
    part_sequences, construct_parts, construct_sequences = design_data

    # COMPUTE ALL QUOTES
    assembly_strategy_data = compute_all_construct_quotes(
        construct_sequences=construct_sequences,
        part_sequences=part_sequences,
        assembly_method=args.assembly_method,
        max_constructs=int(args.constructs) if args.constructs else None
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
        target=args.output,
    )
    print ("Valid plans:", len([q for q in quotes if q is not None]))
