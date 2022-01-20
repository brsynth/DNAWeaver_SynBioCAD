from argparse  import ArgumentParser
from ._version import __version__

def build_args_parser(
    prog: str,
    description: str = '',
    epilog: str = ''
) -> ArgumentParser:

    parser = ArgumentParser(
        prog = prog,
        description = description,
        epilog = epilog
    )

    # Build Parser
    parser = add_arguments(parser)

    return parser

def add_arguments(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        'input',
        type=str,
        help='Path to an .xml SBOL file containing constructs designs and sequences'
    )
    parser.add_argument(
        'output',
        type=str,
        help='Path to the output spreadsheet'
    )
    parser.add_argument(
        'assembly_method',
        type=str,
        choices=["gibson", "golden_gate", "any_method"],
        help='If "any_method" is selected, each construct can be built with any method. However, Golden Gate Assembly will have priority over Gibson Assembly'
    )
    parser.add_argument(
        '--nb_constructs',
        type=int,
        help='Maximum number of constructs to build (only used in tests)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )
    return parser
