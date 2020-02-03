from collections import OrderedDict
import proglog
from dnaweaver import SequenceString
from .generate_supply_network import generate_supply_network


def compute_all_construct_quotes(
    construct_sequences,
    part_sequences,
    assembly_method,
    logger="bar",
    max_constructs=None,
):
    """Compute the quotes for all the constructs in the assembly plan.
    
    The constructs are considered one after the other and every primer and
    fragment used in a construct are considered as available for free in the
    next construct assembly.

    Parameters
    ----------
    construct_sequences
      A dict of the form ``{construct_id: "ATGCCC..."}`` of all constructs to
      be built.
    
    parts_sequences
      A dictionary {part_id: "ATGCGC..."} of the base genetic parts, which will
      be considered as available for free.
    
    assembly_method
      Either "gibson", "golden_gate", or "any_method" (each construct will
      then be assembled using any method, with a preference for Golden Gate
      Assembly)
    
    logger="bar"
      A proglog logger

    Returns
    -------
    (quotes_dict, ordered_primers, amplified_fragments_quotes, errors)
      Data on the optimized DNA manufacturing plan
      - quotes_dict is a dict of the form {quote_id: quote} (where "quote" is
        a DNA Weaver Quote)
      - ordered_primers is a dict {primer_id: "ATGTGC..."} of all primers
        ordered in the whole construction plan.
      - amplified_fragments_quotes is a dict {fragment_id: quote} of DNA Weaver
        quotes for each PCR-created fragment in the construction plan.
      - errored is a dict {construct_id: "Error message"} for all failed
        assemblies
    """
    logger = proglog.default_bar_logger(logger)
    ordered_primers = OrderedDict()
    amplified_fragments = OrderedDict()
    amplified_fragments_quotes = OrderedDict()
    quotes_dict = OrderedDict()
    errors = OrderedDict()
    iterator = list(enumerate(construct_sequences.items()))
    if max_constructs is not None:
        iterator = iterator[:max_constructs]
    for i, (construct, sequence) in logger.iter_bar(construct=iterator):

        # CREATE THE SUPPLY NETWORK

        main_station = generate_supply_network(
            parts_sequences=part_sequences,
            already_amplified_fragments=amplified_fragments,
            already_ordered_primers=ordered_primers,
            assembly_method=assembly_method,
        )

        # FIND AN ASSEMBLY PLAN, ABORT IF ERRORS OR REJECTION

        try:
            for shift in range(5):
                # In DNA weaver, the sequence's 0 position is always considered
                # a cut site. In the unlucky case where this cut site is
                # invalid (e.g. it has a palyndromic sequence preventing
                # Golden Gate assembly), we rotate the sequence a bit to find
                # a better position 0
                rotated_sequence = sequence[shift:] + sequence[:shift]
                rotated_sequence = SequenceString(
                    rotated_sequence, metadata={"topology": "circular"}
                )
                main_station.prepare_network_on_sequence(rotated_sequence)
                quote = main_station.get_quote(rotated_sequence)
                if quote.accepted:
                    break
        except Exception as err:
            logger(message="Construct %s errored." % construct)
            errors[construct] = str(err)
            continue
        if not quote.accepted:
            logger(message="Construct %s: no valid plan found." % construct)
            errors[construct] = "No assembly plan found: %s" % quote.message
            continue
        logger(message="Construct %s processed succesfully." % construct)
        # IF SUCCESS, LOG THE QUOTE AND ITS PRODUCTS

        id_prefix = "ID_%s" % (i + 1)
        quote.compute_full_assembly_plan(id_prefix=id_prefix, id_digits=3)
        for _quote in quote.tree_as_list():
            if _quote.source.operation_type == "PCR":
                amplified_fragments[_quote.id] = _quote.sequence
                amplified_fragments_quotes[_quote.id] = _quote
            if _quote.source.name == "oligo_supplier":
                ordered_primers[_quote.id] = _quote.sequence
        quotes_dict[construct] = quote

    # RETURN THE COMPILED DATA

    return (quotes_dict, ordered_primers, amplified_fragments_quotes, errors)
